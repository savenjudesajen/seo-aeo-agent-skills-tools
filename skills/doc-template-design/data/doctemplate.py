# -*- coding: utf-8 -*-
"""doctemplate.py (doc-template-design): build client-facing .docx files in a neutral, documented layout,
from nothing, in the default look or in a client's brand theme.

No template file is needed. Every part is written here: page setup, styles, bullets, first-page and running
headers, footers with a page number, embedded fonts and every body block (reference/components.md).

    from doctemplate import Doc
    d = Doc(short_title='Menu page refresh', client='Juniper Lane Bistro')          # default theme
    d.title('Publish the new menu pages before the spring launch')
    d.meta(['Action request', 'Juniper Lane Bistro', 'Prepared by <your team>', '9 April 2027'])
    d.lead('The new menu pages are ready ...')
    d.section('Context')                            # numbered automatically: 1, 2, 3 ...
    d.body('Short background paragraph.')
    d.table(['#', 'Task', 'Owner', 'Check'], rows, widths=[1, 9, 3, 4])
    d.save('Juniper_Lane_Menu_Page_Refresh.docx')

Text markup in any text argument: **bold**. In table and fact cells, "\\n" starts a new paragraph and a line that
starts with "~" becomes a small muted note.

Themes: Doc(..., theme='slug' | 'themes/x.json' | dict | Theme). A theme changes colours and fonts only; page
geometry, spacing and the block set stay the same (reference/brand-themes.md).

Requirements: Python 3.8+. fontTools to embed fonts (pip install fonttools), Pillow for figures and logos.
Fonts are Google Fonts statics fetched once from npm (@expo-google-fonts/<family>) and cached in
$DOCTEMPLATE_FONT_CACHE or ~/.cache/doctemplate-fonts. Doc(embed_fonts=False) builds without fonts or network:
the document names its fonts and the reader's machine substitutes.

CLI:
    python3 doctemplate.py --fonts [theme]            build and gate a theme's fonts (default theme without one)
    python3 doctemplate.py --sample out.docx [--theme x] [--no-embed]   build the fixture (sample_doc.py)
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from xml.sax.saxutils import escape

# ----------------------------------------------------------------------------------------------------------
# Layout tokens (twips unless noted; 1pt = 20 twips, 1in = 1440; sz in half-points)
# ----------------------------------------------------------------------------------------------------------
PAGES = {'letter': (12240, 15840), 'a4': (11906, 16838)}
MARGINS = {'top': 1440, 'bottom': 1296, 'left': 1440, 'right': 1440, 'header': 600, 'footer': 560}
CELL_MAR = {'top': 70, 'bottom': 70, 'left': 115, 'right': 115}
RULE_SZ = 4                  # hairline rules: 0.5pt (eighths of a point)
STRIPE_SZ = 24               # section stripe: 3pt
SZ = {'title': 48, 'meta': 18, 'lead': 24, 'body': 22, 'cell': 20, 'note': 17, 'section': 28, 'sub': 24,
      'minor': 22, 'caption': 20, 'furniture': 17, 'chip': 15, 'sub_caption': 17}
LINE_BODY, LINE_TIGHT = 276, 240     # 1.15 and single
META_SEP = ' / '
STATUSES = ['Keep', 'Rework', 'New', 'Remove', 'Optional', 'Later']
EMU_IN = 914400

DEFAULT_THEME = {
    'client': 'Neutral default', 'slug': 'default',
    'colors': {'ink': '1D2630', 'title': '1D2630', 'muted': '59636E', 'panel': 'EEF1F4', 'rule': 'BFC6CE',
               'accent': '2B5F8A', 'accent_text': 'FFFFFF', 'stripe': '2B5F8A', 'number': '2B5F8A',
               'alert': 'A4262C'},
    'status': {'Keep': ['EEF1F4', '1D2630'], 'Rework': ['F4E2B8', '1D2630'], 'New': ['2B5F8A', 'FFFFFF'],
               'Remove': ['A4262C', 'FFFFFF'], 'Optional': ['FFFFFF', '59636E'], 'Later': ['DDE2E7', '1D2630']},
    'fonts': {'body': {'family': 'Source Sans 3', 'weight': 400},
              'strong': {'family': 'Source Sans 3', 'weight': 700},
              'title': {'family': 'Source Serif 4', 'weight': 700}},
}

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
NSDECL = (' xmlns:w="%s" xmlns:r="%s"'
          ' xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"'
          ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
          ' xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"' % (W_NS, R_NS))
XML_HEAD = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n"


# ----------------------------------------------------------------------------------------------------------
# Colour helpers (WCAG relative luminance and contrast)
# ----------------------------------------------------------------------------------------------------------
def lum(h):
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


# ----------------------------------------------------------------------------------------------------------
# Fonts: Google Fonts statics from npm, renamed the way Google Docs and Word name embedded faces, gated
# ----------------------------------------------------------------------------------------------------------
WEIGHT_NAMES = {100: 'Thin', 200: 'ExtraLight', 300: 'Light', 400: 'Regular', 500: 'Medium', 600: 'SemiBold',
                700: 'Bold', 800: 'ExtraBold', 900: 'Black'}
REQUIRED_CHARS = ''.join(chr(c) for c in range(33, 127))        # a theme font must cover these
WANTED_CHARS = '’‘“”–—…•·|×→€£é'   # warn only
SIG_TEXT = REQUIRED_CHARS + WANTED_CHARS + ' fi fl ffi Th To Ta Va Wa Yo AV LT'
FONT_CT = 'application/vnd.openxmlformats-officedocument.obfuscatedFont'
PANOSE = {'sans': '020B0604020202020204', 'serif': '02020603050405020304', 'mono': '02070309020205020404'}
WORD_FAMILY = {'sans': 'swiss', 'serif': 'roman', 'mono': 'modern'}
GF_RAW = 'https://raw.githubusercontent.com/google/fonts/main/'
GF_MIRROR = 'https://cdn.jsdelivr.net/gh/google/fonts@main/'


def font_cache(path=None):
    p = path or os.environ.get('DOCTEMPLATE_FONT_CACHE') or os.path.expanduser('~/.cache/doctemplate-fonts')
    os.makedirs(p, exist_ok=True)
    return p


def font_category(family):
    """'sans', 'serif' or 'mono' for a family name (a theme can set it per role with "category")."""
    n = family.lower()
    if re.search(r'mono|code|courier|consol', n):
        return 'mono'
    if 'sans' not in n and re.search(r'serif|slab|garamond|caslon|baskerville|bodoni|times|georgia|newsreader|'
                                     r'merriweather|lora|playfair|fraunces|cormorant|crimson|literata|gelasio|'
                                     r'tinos|spectral|domine|bitter|zilla|arvo|rokkitt|cardo|prata', n):
        return 'serif'
    return 'sans'


def docx_font(role):
    """(font name in the docx, bold flag) for a {'family', 'weight'} role. Convention shared by Google Docs
    exports and Word: weight 400 and 700 are the family itself (700 as its bold); any other weight is a family
    of its own, e.g. 'Source Sans 3 SemiBold', whose bold face is the family's 700."""
    fam, w = role['family'], int(role.get('weight', 400))
    if w == 400:
        return fam, False
    if w == 700:
        return fam, True
    return '%s %s' % (fam, WEIGHT_NAMES[w]), False


def _download(url, timeout=120):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read()
    except Exception:
        # some sandboxes only trust their proxy certificate through curl's bundle
        return subprocess.run(['curl', '-sSfL', '-m', str(timeout), url], check=True, capture_output=True).stdout


def gf_slug(family):
    return re.sub(r'[^a-z0-9]+', '-', family.lower()).strip('-')


def gf_package(family, version=None):
    """(version, tarball URL) of a Google Fonts family's static TTFs on npm. Raises when it is not a Google Font."""
    slug = gf_slug(family)
    pkg = '@expo-google-fonts/' + slug
    if not version:
        version = json.loads(_download('https://registry.npmjs.org/' + pkg, timeout=60))['dist-tags']['latest']
    return version, 'https://registry.npmjs.org/%s/-/%s-%s.tgz' % (pkg, slug, version)


def font_signature(data):
    """Short hashes of a TTF: 'layout' (names, metrics, weight flags, advances of SIG_TEXT) and 'outline'
    (glyph coordinates). Equal signatures set and draw text identically. Pinned when a theme is confirmed."""
    from fontTools.ttLib import TTFont
    t = TTFont(io.BytesIO(data))
    cmap, hm, os2, hh = t.getBestCmap(), t['hmtx'], t['OS/2'], t['hhea']
    name = lambda i: str(t['name'].getName(i, 3, 1, 0x409) or '')
    lay = [t['head'].unitsPerEm, hh.ascent, hh.descent, hh.lineGap, os2.usWinAscent, os2.usWinDescent,
           os2.fsSelection, os2.usWeightClass, [name(i) for i in (1, 2, 4, 6, 16, 17)]]
    glyphs = []
    for ch in sorted(set(SIG_TEXT)):
        g = cmap.get(ord(ch))
        glyphs.append(g)
        lay.append((ch, g, hm[g][0] if g else None))
    out = []
    if 'glyf' in t:
        glyf = t['glyf']
        for g in sorted(set(x for x in glyphs if x)):
            gl = glyf[g]
            if gl.isComposite():
                out.append((g, [(c.glyphName, c.x, c.y) for c in gl.components]))
            elif gl.numberOfContours:
                c, e, _ = gl.getCoordinates(glyf)
                out.append((g, list(map(tuple, c)), list(e)))
    return {'layout': hashlib.md5(repr(lay).encode()).hexdigest()[:12],
            'outline': hashlib.md5(repr(out).encode()).hexdigest()[:12]}


def _name_spec(docx_name, family, weight, italic):
    """Name-table values for an embedded face. Renderers find a face by nameID 1, so it must equal the font name
    the document's runs use: the family for 400/700 faces, '<family> <Weight>' for other weights (with the
    typographic family and subfamily in nameIDs 16 and 17)."""
    if docx_name == family or weight == 700:
        style = {(False, False): 'Regular', (True, False): 'Bold', (False, True): 'Italic',
                 (True, True): 'Bold Italic'}[(weight == 700, italic)]
        return dict(n1=family, n2=style, n4='%s %s' % (family, style),
                    n6='%s-%s' % (family.replace(' ', ''), style.replace(' ', '')), n16=None, n17=None)
    wn = WEIGHT_NAMES[weight]
    return dict(n1=docx_name, n2='Italic' if italic else 'Regular', n4=docx_name + (' Italic' if italic else ''),
                n6='%s-%s%s' % (family.replace(' ', ''), wn, 'Italic' if italic else ''),
                n16=family, n17=wn + (' Italic' if italic else ''))


def _rename(font, spec, weight, italic):
    name = font['name']
    for nid in (1, 2, 3, 4, 6, 16, 17, 21, 22, 25):
        name.removeNames(nameID=nid)
    for nid, val in ((1, spec['n1']), (2, spec['n2']), (3, 'doctemplate;' + spec['n6']), (4, spec['n4']),
                     (6, spec['n6']), (16, spec['n16']), (17, spec['n17'])):
        if val:
            name.setName(val, nid, 3, 1, 0x409)
    os2 = font['OS/2']
    os2.usWeightClass = weight
    sel = os2.fsSelection & ~0b1100001          # clear ITALIC (bit 0), BOLD (5), REGULAR (6)
    if italic:
        sel |= 1
    if weight == 700:
        sel |= 1 << 5
    if not italic and weight != 700:
        sel |= 1 << 6
    os2.fsSelection = sel
    font['head'].macStyle = (1 if weight == 700 else 0) | (2 if italic else 0)


def _npm_member(tar, weight, italic):
    want = '_%d%s%s.ttf' % (weight, WEIGHT_NAMES[weight], '_Italic' if italic else '')
    return next((m for m in tar.getnames() if m.startswith('package/') and m.endswith(want)), None)


def _variable_face(cache, family, weight, italic):
    """Fallback when the npm package is missing: instance the google/fonts variable font at the weight."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    base = family.replace(' ', '')
    fname = '%s%s[wght].ttf' % (base, '-Italic' if italic else '')
    local = os.path.join(cache, fname)
    if not os.path.exists(local):
        data = None
        for licence in ('ofl', 'apache'):
            path = '%s/%s/%s' % (licence, base.lower(), fname.replace('[', '%5B').replace(']', '%5D'))
            for root in (GF_RAW, GF_MIRROR):
                try:
                    data = _download(root + path)
                    break
                except Exception:
                    continue
            if data:
                break
        if not data:
            return None
        open(local, 'wb').write(data)
    return instancer.instantiateVariableFont(TTFont(local), {'wght': weight}, updateFontNames=False)


def font_gate(fonts, plan, expected=None):
    """Check built fonts: nameID 1 equals the docx font name, weight and italic flags, character coverage, and
    (when the theme pins them) unchanged signatures. Returns (ok, report lines, signatures)."""
    from fontTools.ttLib import TTFont
    ok, lines, sigs = True, [], {}
    for name, embeds in plan:
        for kind, f, fam, w, ital in embeds:
            if f not in fonts:
                continue
            t = TTFont(io.BytesIO(fonts[f]))
            n1 = str(t['name'].getName(1, 3, 1, 0x409) or '')
            cmap = t.getBestCmap()
            missing = [c for c in REQUIRED_CHARS if ord(c) not in cmap]
            soft = [c for c in WANTED_CHARS if ord(c) not in cmap]
            good = (n1 == _name_spec(name, fam, w, ital)['n1'] and t['OS/2'].usWeightClass == w and
                    bool(t['OS/2'].fsSelection & 1) == ital and not missing)
            sig = font_signature(fonts[f])
            sigs[f] = sig
            drift = bool(expected and f in expected and (expected[f]['layout'] != sig['layout'] or
                                                         expected[f]['outline'] != sig['outline']))
            good = good and not drift
            ok &= good
            lines.append('%-36s %-26s %d%s  %s%s%s%s' % (
                f, n1, w, ' italic' if ital else '', 'ok' if good else 'FAIL',
                '  missing ' + ''.join(missing) if missing else '', '  (no %s)' % ''.join(soft) if soft else '',
                '  CHANGED since the theme was confirmed' if drift else ''))
    return ok, lines, sigs


# ----------------------------------------------------------------------------------------------------------
# Theme: colours, fonts and rules of a single client's documents
# ----------------------------------------------------------------------------------------------------------
THEME_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'themes')


class Theme:
    """Theme() or Theme('default') is the neutral default. Theme('slug') loads themes/<slug>.json next to this
    file; a path or a dict works too. Missing colours, statuses or fonts fall back to the default."""

    def __init__(self, spec=None):
        if spec in (None, 'default'):
            spec = DEFAULT_THEME
        elif isinstance(spec, str):
            path = spec if os.path.exists(spec) else os.path.join(THEME_DIR, spec.lower() + '.json')
            spec = json.load(open(path, encoding='utf-8'))
        self.spec = spec
        self.slug = spec.get('slug', 'theme')
        self.default = self.slug == 'default'
        self.client = spec.get('client', self.slug)
        self.prepared_by = spec.get('prepared_by')
        self.prepared_for = spec.get('prepared_for')
        self.never_mention = list(spec.get('never_mention') or [])
        c = dict(DEFAULT_THEME['colors'])
        c.update(spec.get('colors') or {})
        self.colors = {k: v.upper() for k, v in c.items()}
        for k, v in self.colors.items():
            setattr(self, k, v)
        st = dict(DEFAULT_THEME['status'])
        st.update(spec.get('status') or {})
        self.status = {k: (v[0].upper(), v[1].upper()) for k, v in st.items()}
        f = dict(DEFAULT_THEME['fonts'])
        f.update(spec.get('fonts') or {})
        self.fonts = f
        self.font_versions = dict(spec.get('font_versions') or {})
        self.body_font, self.body_bold = docx_font(f['body'])
        self.strong_font, self.strong_bold = docx_font(f['strong'])
        self.title_font, self.title_bold = docx_font(f['title'])
        if f.get('section'):            # optional label face for section headings (a brand's CTA or mono face)
            self.section_font, self.section_bold = docx_font(f['section'])
            self.section_caps = bool(f['section'].get('caps'))
        else:
            self.section_font, self.section_bold, self.section_caps = self.strong_font, self.strong_bold, False

    def meta_by(self):
        """'Prepared for <x>' or 'Prepared by <x>' for the meta line, or None (in-house work)."""
        if self.prepared_for:
            return 'Prepared for ' + self.prepared_for
        return ('Prepared by ' + self.prepared_by) if self.prepared_by else None

    def contrast_pairs(self):
        """(name, fill, text) pairs every theme must pass at 4.5:1."""
        pairs = [('table header', self.accent, self.accent_text), ('fact label', self.panel, self.ink),
                 ('section label', self.panel, self.ink), ('section number', self.panel, self.number),
                 ('text', 'FFFFFF', self.ink), ('title', 'FFFFFF', self.title), ('muted', 'FFFFFF', self.muted),
                 ('muted on panel', self.panel, self.muted)]
        return pairs + [('chip ' + k, f, c) for k, (f, c) in self.status.items()]

    def font_plan(self):
        """[(docx font name, [(embed kind, docx file, family, weight, italic)])]: the body font with italics,
        the title, strong and section fonts regular and bold."""
        plan, seen = [], set()
        for role in ('body', 'title', 'strong', 'section'):
            if role not in self.fonts or not self.fonts[role]:
                continue
            r = self.fonts[role]
            fam, w = r['family'], int(r.get('weight', 400))
            name, _ = docx_font(r)
            if name in seen:
                continue
            seen.add(name)
            base, reg = name.replace(' ', ''), (400 if name == fam else w)
            embeds = [('embedRegular', base + '-regular.ttf', fam, reg, False),
                      ('embedBold', base + '-bold.ttf', fam, 700, False)]
            if role == 'body':
                embeds += [('embedItalic', base + '-italic.ttf', fam, reg, True),
                           ('embedBoldItalic', base + '-boldItalic.ttf', fam, 700, True)]
            plan.append((name, embeds))
        return plan

    def category(self, name):
        for r in self.fonts.values():
            if r and docx_font(r)[0] == name:
                return r.get('category') or font_category(r['family'])
        return font_category(name)

    def font_files(self, cache=None, verbose=False):
        """{docx font file: bytes}, built once per theme and font versions, cached, gated."""
        cache = font_cache(cache)
        plan = self.font_plan()
        key = hashlib.md5(json.dumps([plan, sorted(self.font_versions.items())]).encode()).hexdigest()[:10]
        built = os.path.join(cache, 'built-%s-%s' % (self.slug, key))
        index = os.path.join(built, 'files.json')
        if os.path.exists(index):
            return {f: open(os.path.join(built, f), 'rb').read() for f in json.load(open(index))}
        from fontTools.ttLib import TTFont
        out, tars = {}, {}
        for name, embeds in plan:
            for kind, f, fam, w, ital in embeds:
                if fam not in tars:
                    try:
                        version, url = gf_package(fam, self.font_versions.get(fam))
                        p = os.path.join(cache, os.path.basename(url))
                        if not os.path.exists(p):
                            open(p, 'wb').write(_download(url))
                        tars[fam] = tarfile.open(p)
                        self.font_versions[fam] = version
                    except Exception:
                        tars[fam] = None                     # not on npm: try the variable font
                font = None
                if tars[fam] is not None:
                    m = _npm_member(tars[fam], w, ital)
                    if m is None and kind in ('embedBold', 'embedBoldItalic'):   # no 700: nearest heavier face
                        m = next((_npm_member(tars[fam], x, ital) for x in (800, 900, 600)
                                  if _npm_member(tars[fam], x, ital)), None)
                    if m is not None:
                        font = TTFont(io.BytesIO(tars[fam].extractfile(m).read()), recalcTimestamp=False)
                if font is None:
                    font = _variable_face(cache, fam, w, ital)
                if font is None:
                    if ital:
                        continue                               # no italic: renderers slant the upright
                    raise RuntimeError('%s has no %d weight on Google Fonts (npm or google/fonts)' % (fam, w))
                _rename(font, _name_spec(name, fam, w, ital), w, ital)
                b = io.BytesIO()
                font.save(b)
                out[f] = b.getvalue()
        ok, lines, _ = font_gate(out, plan, self.spec.get('font_sigs'))
        if verbose or not ok:
            print('font gate (%s):\n  %s' % (self.slug, '\n  '.join(lines)))
        if not ok:
            raise RuntimeError('font gate failed for theme %s' % self.slug)
        os.makedirs(built, exist_ok=True)
        for f, data in out.items():
            open(os.path.join(built, f), 'wb').write(data)
        json.dump(sorted(out), open(index, 'w'))
        return out


# ----------------------------------------------------------------------------------------------------------
# XML helpers (property order follows the OOXML schema so validators and Word accept every part)
# ----------------------------------------------------------------------------------------------------------
def rpr(font, bold=False, color='000000', sz=SZ['body'], italic=False, caps=False, bdr=None, shd=None):
    return ('<w:rPr><w:rFonts w:ascii="{f}" w:hAnsi="{f}" w:cs="{f}" w:eastAsia="{f}"/>{b}{i}{caps}'
            '<w:color w:val="{c}"/><w:sz w:val="{s}"/><w:szCs w:val="{s}"/>{bdr}{shd}</w:rPr>').format(
        f=escape(font, {'"': '&quot;'}), b='<w:b/><w:bCs/>' if bold else '<w:b w:val="0"/><w:bCs w:val="0"/>',
        i='<w:i/>' if italic else '', caps='<w:caps/>' if caps else '', c=color, s=sz,
        bdr='<w:bdr w:val="single" w:sz="4" w:space="0" w:color="%s"/>' % bdr if bdr else '',
        shd='<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % shd if shd else '')


def run(text, **kw):
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr(**kw), escape(text))


def rich(text, **kw):
    """Runs for text with **bold** segments."""
    out = []
    for i, seg in enumerate(str(text).split('**')):
        if seg:
            k = dict(kw)
            if i % 2:
                k['bold'] = True
            out.append(run(seg, **k))
    return ''.join(out)


def ppr(style=None, before=0, after=0, line=LINE_BODY, line_rule='auto', keep_next=False, keep_lines=False,
        page_break=False, num=None, pbdr='', shd=None, tabs='', ind='', jc=None):
    x = '<w:pPr>'
    x += '<w:pStyle w:val="%s"/>' % style if style else ''
    x += '<w:keepNext/>' if keep_next else ''
    x += '<w:keepLines/>' if keep_lines else ''
    x += '<w:pageBreakBefore/>' if page_break else ''
    x += '<w:numPr><w:ilvl w:val="%d"/><w:numId w:val="%d"/></w:numPr>' % num if num else ''
    x += '<w:pBdr>%s</w:pBdr>' % pbdr if pbdr else ''
    x += '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % shd if shd else ''
    x += '<w:tabs>%s</w:tabs>' % tabs if tabs else ''
    x += '<w:spacing w:before="%d" w:after="%d" w:line="%d" w:lineRule="%s"/>' % (before, after, line, line_rule)
    x += ind
    x += '<w:jc w:val="%s"/>' % jc if jc else ''
    return x + '</w:pPr>'


def para(runs, **kw):
    return '<w:p>%s%s</w:p>' % (ppr(**kw), runs)


def border(side, color, sz=RULE_SZ, space=0, val='single'):
    return '<w:%s w:val="%s" w:sz="%d" w:space="%d" w:color="%s"/>' % (side, val, sz, space, color)


def cell(width, paras, fill=None, valign='top', span=1):
    mar = ''.join('<w:%s w:w="%d" w:type="dxa"/>' % (s, CELL_MAR[s]) for s in ('top', 'left', 'bottom', 'right'))
    return ('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s%s<w:tcMar>%s</w:tcMar><w:vAlign w:val="%s"/></w:tcPr>'
            '%s</w:tc>' % (width, '<w:gridSpan w:val="%d"/>' % span if span > 1 else '',
                           '<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % fill if fill else '', mar, valign,
                           paras))


def row(cells, header=False):
    tr = '<w:cantSplit/>' + ('<w:tblHeader/>' if header else '')
    return '<w:tr><w:trPr>%s</w:trPr>%s</w:tr>' % (tr, ''.join(cells))


def table_xml(widths, rows, rule, borders=True):
    # hairlines above, below and between rows; no vertical rules (schema order: top left bottom right insideH insideV)
    ruled = ('top', 'bottom', 'insideH') if borders else ()
    b = ''.join(border(s, rule) if s in ruled else '<w:%s w:val="nil"/>' % s
                for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'))
    grid = ''.join('<w:gridCol w:w="%d"/>' % w for w in widths)
    return ('<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:tblInd w:w="0" w:type="dxa"/>'
            '<w:tblBorders>%s</w:tblBorders><w:tblLayout w:type="fixed"/>'
            '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" '
            'w:noHBand="1" w:noVBand="1"/></w:tblPr><w:tblGrid>%s</w:tblGrid>%s</w:tbl>'
            % (sum(widths), b, grid, ''.join(rows)))


def inline_pic(rid, cx, cy, doc_id, name, line_color=None):
    ln = ('<a:ln w="6350"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln>' % line_color) if line_color else ''
    return ('<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="%d" cy="%d"/>'
            '<wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="%d" name="%s"/><wp:cNvGraphicFramePr>'
            '<a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr><a:graphic><a:graphicData '
            'uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr>'
            '<pic:cNvPr id="0" name="%s"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="%s"/>'
            '<a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/>'
            '<a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>%s</pic:spPr>'
            '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>') % (
        cx, cy, doc_id, name, name, rid, cx, cy, ln)


def _font_key(name):
    """Obfuscation key of an embedded font, derived from its file name so builds are byte-deterministic."""
    h = hashlib.md5(('doctemplate:' + name).encode()).hexdigest().upper()
    return '{%s-%s-%s-%s-%s}' % (h[:8], h[8:12], h[12:16], h[16:20], h[20:])


def _obfuscate(data, key):
    """ECMA-376 font obfuscation: XOR the first 32 bytes with the key's 16 bytes in reverse order."""
    hexs = key.strip('{}').replace('-', '')
    k = [int(hexs[i:i + 2], 16) for i in range(0, 32, 2)][::-1]
    return bytes(b ^ k[i % 16] for i, b in enumerate(data[:32])) + data[32:]


def _font_meta(data, category):
    """panose1, charset, family, pitch and sig of a fontTable entry, so a viewer that cannot use embedded
    fonts substitutes a sans for a sans and a serif for a serif."""
    if data is None:
        return ('<w:panose1 w:val="%s"/><w:charset w:val="00"/><w:family w:val="%s"/><w:pitch w:val="%s"/>'
                % (PANOSE[category], WORD_FAMILY[category], 'fixed' if category == 'mono' else 'variable'))
    from fontTools.ttLib import TTFont
    o = TTFont(io.BytesIO(data))['OS/2']
    p = o.panose
    own = '%02X' * 10 % (p.bFamilyType, p.bSerifStyle, p.bWeight, p.bProportion, p.bContrast, p.bStrokeVariation,
                         p.bArmStyle, p.bLetterForm, p.bMidline, p.bXHeight)
    panose = own if (p.bFamilyType == 2 and p.bSerifStyle) else PANOSE[category]
    return ('<w:panose1 w:val="%s"/><w:charset w:val="00"/><w:family w:val="%s"/><w:pitch w:val="%s"/>'
            '<w:sig w:usb0="%08X" w:usb1="%08X" w:usb2="%08X" w:usb3="%08X" w:csb0="%08X" w:csb1="%08X"/>' % (
                panose, WORD_FAMILY[category], 'fixed' if category == 'mono' else 'variable',
                o.ulUnicodeRange1, o.ulUnicodeRange2, o.ulUnicodeRange3, o.ulUnicodeRange4,
                o.ulCodePageRange1, o.ulCodePageRange2))


# ----------------------------------------------------------------------------------------------------------
# The document
# ----------------------------------------------------------------------------------------------------------
class Doc:
    """One document in the layout.

    short_title: the document's short name (running header, left; footer). client: who it is for (running
    header, right; footer). theme: None (neutral default), a slug, a path, a dict or a Theme. page: 'letter' or
    'a4'. logo: optional PNG for the first-page header, scaled to fit logo_box (width, height in inches).
    embed_fonts: False builds offline without fonts."""

    def __init__(self, short_title, client='', theme=None, page='letter', logo=None, img_dir=None,
                 embed_fonts=True, font_cache=None, jpeg_over=250000, footer_text=None, logo_box=(1.5, 0.6)):
        self.short_title, self.client = short_title, client
        self.footer_text = footer_text if footer_text is not None else (
            '%s · %s' % (client, short_title) if client else short_title)
        self.t = theme if isinstance(theme, Theme) else Theme(theme)
        self.page_w, self.page_h = PAGES[page]
        self.text_w = self.page_w - MARGINS['left'] - MARGINS['right']
        self.logo, self.img_dir, self.embed_fonts, self.font_cache = logo, img_dir, embed_fonts, font_cache
        self.jpeg_over, self.logo_box = jpeg_over, logo_box
        self.blocks = []            # (kind, xml, text)
        self.media = []             # (part name, bytes, rId)
        self.n_section, self.n_sub, self.n_appendix, self.fig_n = 0, 0, 0, 0
        self._doc_id = 100

    # ---------- run styles ----------
    def _b(self, **kw):
        kw.setdefault('color', self.t.ink)
        kw.setdefault('bold', self.t.body_bold)
        return dict(font=self.t.body_font, **kw)

    def _s(self, **kw):
        kw.setdefault('color', self.t.ink)
        return dict(font=self.t.strong_font, bold=self.t.strong_bold, **kw)

    # ---------- plumbing ----------
    def _add(self, kind, xml, text=''):
        prev = self.blocks[-1][0] if self.blocks else None
        if kind == 'table' and prev == 'table':
            self.blocks.append(('gap', self._gap_xml(120), ''))     # adjacent tables merge in Word: keep apart
        self.blocks.append((kind, xml, text))

    def _prev(self):
        return self.blocks[-1][0] if self.blocks else None

    def _widths(self, widths, n):
        """Column widths in twips from any relative weights (or twips); they always add up to the text width."""
        widths = list(widths or [1] * n)
        assert len(widths) == n, 'widths has %d values for %d columns' % (len(widths), n)
        tot = float(sum(widths))
        out = [int(round(self.text_w * w / tot)) for w in widths]
        out[-1] += self.text_w - sum(out)
        return out

    def _gap_xml(self, after):
        return para('', after=0, line=max(after, 20), line_rule='exact')

    # ---------- top of the document ----------
    def title(self, text):
        t = self.t
        self._add('title', para(run(text, font=t.title_font, bold=t.title_bold, color=t.title, sz=SZ['title']),
                                style='Title', before=0, after=100, line=LINE_TIGHT, keep_next=True), text)

    def meta(self, parts):
        text = META_SEP.join(p for p in parts if p)
        self._add('meta', para(run(text, **self._b(color=self.t.muted, sz=SZ['meta'])), after=280,
                               line=LINE_TIGHT), text)

    def lead(self, text):
        """The ask or the answer, in two or three sentences, behind a stripe in the accent."""
        pb = border('left', self.t.stripe, sz=18, space=10)
        self._add('lead', para(rich(text, **self._b(sz=SZ['lead'])), after=320, line=LINE_BODY, pbdr=pb,
                               ind='<w:ind w:left="220"/>'), text)

    # ---------- headings ----------
    def _heading(self, number, label, new_page, appendix=False):
        t = self.t
        lab = label.upper() if t.section_caps else label
        pb = (border('left', t.stripe, sz=STRIPE_SZ, space=8) + border('top', t.panel, space=3) +
              border('bottom', t.panel, space=3) + border('right', t.panel, space=4))
        runs = (run(number, font=t.section_font, bold=t.section_bold, color=t.number, sz=SZ['section']) +
                run('   ', **self._s(sz=SZ['section'])) +
                run(lab, font=t.section_font, bold=t.section_bold, color=t.ink, sz=SZ['section']))
        self._add('section', para(runs, style='Heading1', before=200 if new_page else 400, after=160,
                                  line=LINE_TIGHT, keep_next=True, keep_lines=True, page_break=new_page,
                                  pbdr=pb, shd=t.panel, ind='<w:ind w:left="200"/>'), number + ' ' + label)

    def section(self, label, new_page=False, number=None):
        """Numbered section heading: '3   How we ranked the fixes'. Numbers run 1, 2, 3 unless number= is given."""
        self.n_section += 1
        self.n_sub = 0
        self._heading(str(number or self.n_section), label, new_page)

    def appendix(self, label, new_page=True):
        """Lettered section heading for appendices: 'A   Data sources'."""
        self.n_appendix += 1
        self.n_sub = 0
        self._heading(chr(64 + self.n_appendix), label, new_page, appendix=True)

    def subsection(self, label, status=None):
        """Second level: '4.2  Checkout button' with an optional status chip on the right."""
        t = self.t
        self.n_sub += 1
        parent = chr(64 + self.n_appendix) if self.n_appendix else str(self.n_section)
        num = '%s.%d' % (parent, self.n_sub)
        chip = ''
        if status:
            fill, col = t.status[status]
            chip = '<w:r>%s<w:tab/></w:r>%s' % (rpr(**self._b(sz=SZ['sub'])), run(
                '  %s  ' % status, font=t.strong_font, bold=t.strong_bold, color=col, sz=SZ['chip'],
                caps=True, shd=fill, bdr=(t.muted if fill.upper() == 'FFFFFF' else None)))
        tabs = '<w:tab w:val="right" w:leader="none" w:pos="%d"/>' % self.text_w
        runs = run(num + '  ', **self._s(color=t.number, sz=SZ['sub'])) + run(label, **self._s(sz=SZ['sub'])) + chip
        self._add('subsection', para(runs, style='Heading2', before=280, after=120, line=LINE_TIGHT,
                                     keep_next=True, keep_lines=True, pbdr=border('bottom', t.rule, space=3),
                                     tabs=tabs), num + ' ' + label + (' ' + status if status else ''))

    def minor(self, text):
        """A small heading over a second table or list inside one section."""
        self._add('minor', para(run(text, **self._s(sz=SZ['minor'])), before=200, after=80, line=LINE_TIGHT,
                                keep_next=True, keep_lines=True), text)

    # ---------- text ----------
    def body(self, text, before=None, after=140, keep_next=False):
        """Body paragraph. Directly after a table it gets 6pt above unless before= is given."""
        if before is None:
            before = 120 if self._prev() in ('table', 'figure') else 0
        self._add('body', para(rich(text, **self._b()), before=before, after=after, keep_next=keep_next), text)

    def note(self, text, after=140):
        self._add('note', para(rich(text, **self._b(color=self.t.muted, sz=SZ['note'])), after=after,
                               line=LINE_TIGHT), text)

    def bullets(self, items, level=0, numbered=False):
        before = 120 if self._prev() in ('table', 'figure') else 0
        for i, it in enumerate(items):
            last = i == len(items) - 1
            self._add('bullet', para(rich(it, **self._b()), num=(level, 2 if numbered else 1),
                                     before=before if i == 0 else 0, after=160 if last else 60), it)

    def numbered(self, items):
        self.bullets(items, numbered=True)

    def gap(self, pt=6):
        self.blocks.append(('gap', self._gap_xml(pt * 20), ''))

    def page_break(self):
        """Next block on a new page, via an empty 1pt paragraph (page breaks inside table cells are ignored)."""
        self.blocks.append(('break', para('', page_break=True, line=20, line_rule='exact'), ''))

    # ---------- tables ----------
    def _cell_paras(self, text, bold=False, sz=SZ['cell'], color=None):
        out = []
        for line in str(text).split('\n'):
            if line.startswith('~'):
                out.append(para(rich(line[1:], **self._b(color=self.t.muted, sz=SZ['note'])), line=LINE_TIGHT,
                                before=40))
            else:
                kw = self._b(sz=sz, color=color or self.t.ink)
                if bold:
                    kw['bold'] = True
                out.append(para(rich(line, **kw), line=LINE_TIGHT))
        return ''.join(out)

    def table(self, header, rows, widths=None, status_col=None, label_col=False, bold_first=False, sz=None,
              zebra=False):
        """Rows of facts, steps or options. header: column titles (accent row, repeats on each page) or None.
        widths: relative weights or twips. status_col: index of a Keep/Rework/New/Remove/Optional/Later column.
        label_col: first column in the panel colour. zebra: panel colour on every second body row."""
        t = self.t
        sz = sz or SZ['cell']
        n = len(header) if header else len(rows[0])
        ws = self._widths(widths, n)
        trs = []
        if header:
            trs.append(row([cell(w, para(run(h, **self._s(color=t.accent_text, sz=sz)), line=LINE_TIGHT),
                                 fill=t.accent, valign='center') for h, w in zip(header, ws)], header=True))
        text = list(header or [])
        for k, r in enumerate(rows):
            cells = []
            band = t.panel if (zebra and k % 2 == 1) else None
            for i, (v, w) in enumerate(zip(r, ws)):
                text.append(str(v))
                if status_col is not None and i == status_col:
                    fill, col = t.status[v]
                    cells.append(cell(w, para(run(v, **self._s(color=col, sz=sz)), line=LINE_TIGHT), fill=fill))
                elif label_col and i == 0:
                    cells.append(cell(w, self._cell_paras(v, bold=True, sz=sz), fill=t.panel))
                else:
                    cells.append(cell(w, self._cell_paras(v, bold=bold_first and i == 0, sz=sz), fill=band))
            trs.append(row(cells))
        self._add('table', table_xml(ws, trs, t.rule), ' '.join(text))

    def facts(self, pairs, label_w=0.3, sz=None):
        """Two-column fact table: label in the panel colour, value beside it. label_w: share of the width."""
        self.table(None, pairs, widths=[label_w, 1 - label_w], label_col=True, sz=sz)

    # ---------- figures ----------
    def _media(self, src):
        if isinstance(src, str) and self.img_dir and not os.path.isabs(src):
            src = os.path.join(self.img_dir, src)
        data = open(src, 'rb').read() if isinstance(src, str) else src
        ext = os.path.splitext(src)[1].lower().lstrip('.') if isinstance(src, str) else 'png'
        ext = 'jpeg' if ext == 'jpg' else ext
        if ext == 'png' and self.jpeg_over and len(data) > self.jpeg_over:
            from PIL import Image
            im = Image.open(io.BytesIO(data)).convert('RGB')
            if im.resize((160, 160), Image.NEAREST).getcolors(1000) is None:   # photo or screenshot, not a diagram
                b = io.BytesIO()
                im.save(b, 'JPEG', quality=86, optimize=True)
                data, ext = b.getvalue(), 'jpeg'
        rid = 'rId%d' % (100 + len(self.media))
        name = 'image%d.%s' % (100 + len(self.media), ext)
        self.media.append((name, data, rid))
        return rid, name, data

    def _pic(self, src, width_in, max_h_in, frame=True):
        from PIL import Image
        rid, name, data = self._media(src)
        w, h = Image.open(io.BytesIO(data)).size
        wi = width_in if width_in * h / w <= max_h_in else max_h_in * w / h
        self._doc_id += 1
        return inline_pic(rid, int(wi * EMU_IN), int(wi * EMU_IN * h / w), self._doc_id, name,
                          self.t.rule if frame else None)

    def _caption(self, finding):
        self.fig_n += 1
        text = 'Figure %d.  %s' % (self.fig_n, finding)
        self._add('caption', para(run('Figure %d.  ' % self.fig_n, **self._s(color=self.t.number, sz=SZ['caption']))
                                  + run(finding, **self._s(sz=SZ['caption'])), style='Caption',
                                  before=240, after=100, line=LINE_TIGHT, keep_next=True, keep_lines=True), text)

    def _source(self, text):
        self._add('source', para(run('Source: ' + text, **self._b(color=self.t.muted, sz=SZ['note'])), before=80,
                                 after=200, line=LINE_TIGHT), text)

    def figure(self, path, finding, source=None, max_h=4.0, width=None, frame=True):
        """'Figure N.  <finding>' above, the image centred with a hairline edge, a muted source line below."""
        self._caption(finding)
        full = self.text_w / 1440.0
        pic = self._pic(path, min(width or full, full), max_h, frame)
        self._add('figure', para(pic, jc='center', keep_next=bool(source), line=LINE_TIGHT,
                                 after=0 if source else 200), '')
        if source:
            self._source(source)

    def figure_pair(self, left, right, finding, source=None, max_h=3.0):
        """Two images side by side, bottom-aligned, each with a muted sub-caption. left/right = (path, text)."""
        self._caption(finding)
        ws = self._widths([1, 1], 2)
        cells = []
        for (path, sub), w in ((left, ws[0]), (right, ws[1])):
            pic = self._pic(path, (w - CELL_MAR['left'] - CELL_MAR['right']) / 1440.0, max_h)
            cells.append(cell(w, para(pic, jc='center', line=LINE_TIGHT) +
                              para(run(sub, **self._b(color=self.t.muted, sz=SZ['sub_caption'])), before=60,
                                   jc='center', line=LINE_TIGHT), valign='bottom'))
        self._add('table', table_xml(ws, [row(cells)], self.t.rule, borders=False), left[1] + ' ' + right[1])
        if source:
            self._source(source)

    # ---------- parts ----------
    def _styles(self):
        t = self.t
        f = lambda name: '<w:rFonts w:ascii="{0}" w:hAnsi="{0}" w:cs="{0}" w:eastAsia="{0}"/>'.format(
            escape(name, {'"': '&quot;'}))
        heading = lambda sid, name, lvl, font: (
            '<w:style w:type="paragraph" w:styleId="%s"><w:name w:val="%s"/><w:basedOn w:val="Normal"/>'
            '<w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:keepLines/><w:outlineLvl w:val="%d"/>'
            '</w:pPr><w:rPr>%s<w:b/><w:color w:val="%s"/></w:rPr></w:style>' % (sid, name, lvl, f(font), t.ink))
        return ('<w:docDefaults><w:rPrDefault><w:rPr>%s<w:color w:val="%s"/><w:sz w:val="%d"/><w:szCs w:val="%d"/>'
                '<w:lang w:val="en-US"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="0" '
                'w:line="%d" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
                '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/>'
                '</w:style>'
                '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/>'
                '<w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/></w:pPr><w:rPr>%s<w:color w:val="%s"/>'
                '<w:sz w:val="%d"/></w:rPr></w:style>%s%s'
                '<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="caption"/><w:basedOn w:val="Normal"/>'
                '<w:next w:val="Normal"/><w:qFormat/><w:rPr>%s<w:b/></w:rPr></w:style>'
                '<w:style w:type="table" w:default="1" w:styleId="TableNormal"><w:name w:val="Normal Table"/>'
                '<w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar><w:top w:w="%d" w:type="dxa"/>'
                '<w:left w:w="%d" w:type="dxa"/><w:bottom w:w="%d" w:type="dxa"/><w:right w:w="%d" w:type="dxa"/>'
                '</w:tblCellMar></w:tblPr></w:style>' % (
                    f(t.body_font), t.ink, SZ['body'], SZ['body'], LINE_BODY, f(t.title_font), t.title, SZ['title'],
                    heading('Heading1', 'heading 1', 0, t.section_font), heading('Heading2', 'heading 2', 1, t.strong_font),
                    f(t.strong_font), CELL_MAR['top'], CELL_MAR['left'], CELL_MAR['bottom'], CELL_MAR['right']))

    def _numbering(self):
        t = self.t
        lvl = lambda i, fmt, text, left: (
            '<w:lvl w:ilvl="%d"><w:start w:val="1"/><w:numFmt w:val="%s"/><w:lvlText w:val="%s"/>'
            '<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="%d" w:hanging="260"/></w:pPr><w:rPr>'
            '<w:rFonts w:ascii="{f}" w:hAnsi="{f}" w:cs="{f}"/><w:color w:val="%s"/></w:rPr></w:lvl>'
            % (i, fmt, text, left, t.number if i == 0 else t.muted)).replace('{f}', escape(t.body_font, {'"': '&quot;'}))
        bullets = ''.join(lvl(i, 'bullet', '•–◦'[i % 3], 360 + 360 * i) for i in range(9))
        nums = ''.join(lvl(i, ('decimal', 'lowerLetter', 'lowerRoman')[i % 3], '%%%d.' % (i + 1), 360 + 360 * i)
                       for i in range(9))
        return ('<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="hybridMultilevel"/>%s</w:abstractNum>'
                '<w:abstractNum w:abstractNumId="2"><w:multiLevelType w:val="hybridMultilevel"/>%s</w:abstractNum>'
                '<w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num>'
                '<w:num w:numId="2"><w:abstractNumId w:val="2"/></w:num>' % (bullets, nums))

    def _furniture_runs(self, text, color):
        return run(text, **self._b(color=color, sz=SZ['furniture']))

    def _header_default(self):
        t = self.t
        tabs = '<w:tab w:val="right" w:leader="none" w:pos="%d"/>' % self.text_w
        runs = self._furniture_runs(self.short_title, t.muted)
        if self.client:
            runs += '<w:r>%s<w:tab/></w:r>' % rpr(**self._b(sz=SZ['furniture'])) + self._furniture_runs(
                self.client, t.muted)
        return para(runs, tabs=tabs, line=LINE_TIGHT, pbdr=border('bottom', t.rule, space=4))

    def _header_first(self, logo_run):
        return para(logo_run or '', line=LINE_TIGHT)

    def _footer(self):
        t = self.t
        tabs = '<w:tab w:val="right" w:leader="none" w:pos="%d"/>' % self.text_w
        # the PAGE field carries a result run in the footer's own style; without one LibreOffice draws the
        # number in the document default font and size
        page = ('<w:r>%s<w:tab/></w:r>%s<w:fldSimple w:instr=" PAGE "><w:r>%s<w:t>1</w:t></w:r></w:fldSimple>' % (
            rpr(**self._b(sz=SZ['furniture'])), self._furniture_runs('Page ', t.muted),
            rpr(**self._s(color=t.ink, sz=SZ['furniture']))))
        return para(self._furniture_runs(self.footer_text, t.muted) + page, tabs=tabs, line=LINE_TIGHT,
                    pbdr=border('top', t.rule, space=4))

    def _logo_run(self, rels):
        if not self.logo:
            return ''
        from PIL import Image
        data = open(self.logo, 'rb').read()
        w, h = Image.open(io.BytesIO(data)).size
        box_w, box_h = self.logo_box                   # inches: the logo is scaled to fit inside this box
        wi = min(box_w, box_h * w / float(h))
        rels.append(('rId1', REL, 'image', 'media/logo.png'))
        return data, inline_pic('rId1', int(wi * EMU_IN), int(wi * EMU_IN * h / w), 1, 'logo.png')

    def check_words(self):
        """never_mention names found anywhere in the text, header or footer (save() refuses to write them)."""
        if not self.t.never_mention:
            return []
        text = ' '.join(b[2] for b in self.blocks) + ' ' + self.short_title + ' ' + self.client + ' ' + self.footer_text
        text = text.lower()
        return [w for w in self.t.never_mention if w.lower() in text]

    def parts(self):
        t = self.t
        fonts = t.font_files(self.font_cache) if self.embed_fonts else {}
        root = lambda tag, inner: '%s<%s%s>%s</%s>' % (XML_HEAD, tag, NSDECL, inner, tag)
        rels = lambda items: '%s<Relationships xmlns="%s">%s</Relationships>' % (
            XML_HEAD, PKG_NS, ''.join('<Relationship Id="%s" Type="%s%s" Target="%s"/>' % i for i in items))
        p = {}
        body = ''.join(b[1] for b in self.blocks)
        sect = ('<w:sectPr><w:headerReference w:type="default" r:id="rId6"/><w:headerReference w:type="first" '
                'r:id="rId7"/><w:footerReference w:type="default" r:id="rId8"/><w:footerReference w:type="first" '
                'r:id="rId9"/><w:pgSz w:w="%d" w:h="%d"/><w:pgMar w:top="%d" w:right="%d" w:bottom="%d" w:left="%d" '
                'w:header="%d" w:footer="%d" w:gutter="0"/><w:pgNumType w:start="1"/><w:titlePg/></w:sectPr>' % (
                    self.page_w, self.page_h, MARGINS['top'], MARGINS['right'], MARGINS['bottom'], MARGINS['left'],
                    MARGINS['header'], MARGINS['footer']))
        p['word/document.xml'] = root('w:document', '<w:body>%s%s</w:body>' % (body, sect))
        p['word/styles.xml'] = root('w:styles', self._styles())
        p['word/settings.xml'] = root('w:settings', (
            ('<w:embedTrueTypeFonts/>' if fonts else '') + '<w:defaultTabStop w:val="720"/><w:characterSpacingControl '
            'w:val="doNotCompress"/><w:compat><w:compatSetting w:name="compatibilityMode" '
            'w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>'))
        p['word/numbering.xml'] = root('w:numbering', self._numbering())
        # font table: every font the runs name, with its embedded faces packaged the way Word writes them
        ft, ft_rels, n = '', [], 0
        for fname, embeds in t.font_plan():
            regular = fonts.get(next((f for k, f, _, _, _ in embeds if k == 'embedRegular'), ''))
            inner = _font_meta(regular, t.category(fname))
            for kind, file, _, _, _ in embeds:
                if file not in fonts:
                    continue
                n += 1
                key = _font_key(file)
                part = 'fonts/' + file.rsplit('.', 1)[0] + '.odttf'
                inner += '<w:%s r:id="rId%d" w:fontKey="%s"/>' % (kind, n, key)
                ft_rels.append(('rId%d' % n, REL, 'font', part))
                p['word/' + part] = _obfuscate(fonts[file], key)
            ft += '<w:font w:name="%s">%s</w:font>' % (escape(fname, {'"': '&quot;'}), inner)
        p['word/fontTable.xml'] = root('w:fonts', ft)
        if ft_rels:
            p['word/_rels/fontTable.xml.rels'] = rels(ft_rels)
        head_rels = []
        logo = self._logo_run(head_rels)
        p['word/header1.xml'] = root('w:hdr', self._header_default())
        p['word/header2.xml'] = root('w:hdr', self._header_first(logo[1] if logo else ''))
        if logo:
            p['word/media/logo.png'] = logo[0]
            p['word/_rels/header2.xml.rels'] = rels(head_rels)
        p['word/footer1.xml'] = root('w:ftr', self._footer())
        p['word/footer2.xml'] = root('w:ftr', self._footer())
        doc_rels = [('rId2', REL, 'settings', 'settings.xml'), ('rId3', REL, 'fontTable', 'fontTable.xml'),
                    ('rId4', REL, 'numbering', 'numbering.xml'), ('rId5', REL, 'styles', 'styles.xml'),
                    ('rId6', REL, 'header', 'header1.xml'), ('rId7', REL, 'header', 'header2.xml'),
                    ('rId8', REL, 'footer', 'footer1.xml'), ('rId9', REL, 'footer', 'footer2.xml')]
        for name, data, rid in self.media:
            p['word/media/' + name] = data
            doc_rels.append((rid, REL, 'image', 'media/' + name))
        p['word/_rels/document.xml.rels'] = rels(doc_rels)
        p['_rels/.rels'] = rels([('rId1', REL, 'officeDocument', 'word/document.xml')])
        wml = 'application/vnd.openxmlformats-officedocument.wordprocessingml.'
        ov = {'/word/document.xml': wml + 'document.main+xml', '/word/styles.xml': wml + 'styles+xml',
              '/word/settings.xml': wml + 'settings+xml', '/word/numbering.xml': wml + 'numbering+xml',
              '/word/fontTable.xml': wml + 'fontTable+xml', '/word/header1.xml': wml + 'header+xml',
              '/word/header2.xml': wml + 'header+xml', '/word/footer1.xml': wml + 'footer+xml',
              '/word/footer2.xml': wml + 'footer+xml'}
        exts = sorted({k.rsplit('.', 1)[1] for k in p if k.startswith('word/media/')})
        ct = ''.join('<Default Extension="%s" ContentType="image/%s"/>' % (e, e) for e in exts)
        ct += '<Default Extension="odttf" ContentType="%s"/>' % FONT_CT if ft_rels else ''
        ct += ('<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
               '<Default Extension="xml" ContentType="application/xml"/>')
        ct += ''.join('<Override PartName="%s" ContentType="%s"/>' % kv for kv in sorted(ov.items()))
        p['[Content_Types].xml'] = ('%s<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                                    '%s</Types>' % (XML_HEAD, ct))
        return p

    def save(self, path):
        """Write the .docx (byte-deterministic: same input, same bytes). Refuses a never_mention name."""
        hits = self.check_words()
        if hits:
            raise ValueError('documents for %s must not mention: %s' % (self.t.client, ', '.join(hits)))
        parts = self.parts()
        from xml.dom import minidom
        for name, data in parts.items():          # every XML part must parse
            if name.endswith('.xml') or name.endswith('.rels'):
                minidom.parseString(data.encode('utf-8'))
        order = ['[Content_Types].xml', '_rels/.rels'] + sorted(k for k in parts if k not in
                                                                  ('[Content_Types].xml', '_rels/.rels'))
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            for name in order:
                data = parts[name]
                z.writestr(zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0)),
                           data.encode('utf-8') if isinstance(data, str) else data, zipfile.ZIP_DEFLATED)
        return path


if __name__ == '__main__':
    args = sys.argv[1:]
    if '--fonts' in args:
        i = args.index('--fonts')
        th = Theme(args[i + 1] if len(args) > i + 1 and not args[i + 1].startswith('--') else None)
        files = th.font_files(verbose=True)
        ok, lines, _ = font_gate(files, th.font_plan(), th.spec.get('font_sigs'))
        print('\n'.join(lines))
        print('FONT GATE', 'PASS' if ok else 'FAIL', '(%s: %d files, %.0f KB; versions %s)' % (
            th.slug, len(files), sum(map(len, files.values())) / 1024.0, th.font_versions))
        sys.exit(0 if ok else 1)
    if '--sample' in args:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import sample_doc
        theme = args[args.index('--theme') + 1] if '--theme' in args else None
        print(sample_doc.build(args[args.index('--sample') + 1], theme=theme, embed_fonts='--no-embed' not in args))
        sys.exit(0)
    print(__doc__)
