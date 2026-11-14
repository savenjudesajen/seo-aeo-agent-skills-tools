# -*- coding: utf-8 -*-
"""theme_from_probe.py (doc-template-design): turn brand probes of a client's live site into a theme proposal.

    python3 theme_from_probe.py probes/<slug>_home.json probes/<slug>_page.json --client "Name" \
        --domain site.example --out themes/<slug>.json [--alias ...] [--prepared-by "Team"] \
        [--prepared-for "Agency"] [--relationship "..."] [--never-mention "Name" ...]
        [--accent HEX] [--highlight HEX] [--accent-text HEX] [--panel HEX] [--muted HEX] [--ink HEX]
        [--body-font "Family:400"] [--title-font "Family:700"] [--strong-font "Family:700"]
        [--section-font "Family:400[:caps]"] [--no-section-font] [--offline]

    python3 theme_from_probe.py --confirm themes/<slug>.json --note "approved on the preview, <date>"

A probe is the JSON brand_probe.js returns on a page (read back with dump_probe.js and the browser's page-text
tool). Every choice is printed with its evidence. The output is a PROPOSAL: build the preview with
showcase.py --theme, show it to the user, and run --confirm only after a yes (it builds and gates the fonts, pins
their versions and signatures and stamps "confirmed"). When the user corrects a value, rerun with the override
rather than editing the JSON, so the contrast rules still apply.

How a brand maps onto the layout's roles (reference/brand-themes.md has the reasoning):
  - accent: the most used saturated colour (filled buttons x4, border length x2, filled area, links, logo,
    brand tokens such as --primary or --brand); framework default palettes and deleted variables are ignored
  - light accent (luminance 0.4+, e.g. a pale yellow or a light coral): too light for white text, so table header rows use the
    darkest text colour with the accent as their text (when it reads at 4.5:1); the accent becomes the stripe
  - mid accent (a red, a blue): header rows in the accent with white or dark text, accent stripe
  - dark accent (a navy, an aubergine): header rows in the accent, their text the brand's bright highlight when
    one reads at 4.5:1 on it, else white
  - ink = body text colour of running text on light backgrounds; title = heading colour on light backgrounds;
    rule = a light neutral border colour; muted = the site's secondary grey kept between 4.5 and 7.5:1 on white
    (a lighter grey is darkened along its hue to 5:1); panel = a neutral panel colour 1.12 to 1.45:1 against white
  - dark site (half the page area dark and no dark text on a light background anywhere): documents are white
    pages, so the site's page colour becomes the ink and its darkest readable grey the muted colour
  - section label face: a family other than the body's on 60%+ of styled calls to action (at least three) goes on
    section headings only, in capitals when most of those buttons are
  - every text/fill pair is checked at 4.5:1; a failing pair takes white or the dark text instead
  - fonts: body = family carrying most running text (13 to 20px), title = largest h1-h3 family and weight,
    strong = body family bold. A family not on Google Fonts is licensed: documents use the closest open family
    from SUBSTITUTES and the output says so. Never embed a client's web font files (their licence covers the
    website, not documents).
"""
import argparse
import colorsys
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# licensed families -> closest open Google Fonts family (judged by proportions, x-height and tone)
SUBSTITUTES = {
    # sans
    'helvetica': 'Inter', 'helvetica neue': 'Inter', 'arial': 'Arimo', 'neue haas unica': 'Inter',
    'graphik': 'Inter', 'suisse intl': 'Inter', "suisse int'l": 'Inter', 'söhne': 'Inter', 'sohne': 'Inter',
    'aktiv grotesk': 'Inter', 'untitled sans': 'Inter', 'akkurat': 'Inter', 'maison neue': 'Inter',
    'abc diatype': 'Inter', 'matter': 'Inter', 'haffer': 'Inter', 'sf pro': 'Inter', 'sf pro display': 'Inter',
    'sf pro text': 'Inter', '-apple-system': 'Inter', 'system-ui': 'Inter', 'segoe ui': 'Noto Sans',
    'calibre': 'Inter', 'basis grotesque': 'Inter', 'aeonik': 'Manrope', 'circular': 'DM Sans',
    'circular std': 'DM Sans', 'gt walsheim': 'DM Sans', 'apercu': 'DM Sans', 'proxima nova': 'Montserrat',
    'gotham': 'Montserrat', 'avenir': 'Nunito Sans', 'avenir next': 'Nunito Sans', 'museo sans': 'Nunito Sans',
    'futura': 'Jost', 'futura pt': 'Jost', 'gilroy': 'Plus Jakarta Sans', 'sofia pro': 'Outfit',
    'brandon grotesque': 'Josefin Sans', 'favorit': 'Space Grotesk', 'tt commons': 'Inter', 'tt norms': 'Inter',
    'effra': 'Inter', 'frutiger': 'Noto Sans', 'myriad pro': 'Source Sans 3', 'din': 'Barlow', 'din pro': 'Barlow',
    'univers': 'Inter', 'akzidenz-grotesk': 'Inter', 'calibri': 'Carlito',
    # serif
    'tiempos': 'Source Serif 4', 'tiempos headline': 'Source Serif 4', 'tiempos text': 'Source Serif 4',
    'publico': 'Source Serif 4', 'lyon': 'Source Serif 4', 'lyon text': 'Source Serif 4', 'gt sectra': 'Fraunces',
    'canela': 'Cormorant', 'domaine': 'Playfair Display', 'domaine display': 'Playfair Display',
    'freight text': 'Crimson Pro', 'freight display': 'Playfair Display', 'recoleta': 'Fraunces',
    'editorial new': 'Newsreader', 'gt super': 'Newsreader', 'georgia': 'Gelasio', 'times new roman': 'Tinos',
    'times': 'Tinos', 'minion pro': 'Crimson Pro', 'garamond': 'EB Garamond', 'cambria': 'Caladea',
    # mono
    'sf mono': 'IBM Plex Mono', 'menlo': 'IBM Plex Mono', 'consolas': 'Inconsolata', 'monaco': 'IBM Plex Mono',
    'courier new': 'Cousine', 'gt america mono': 'IBM Plex Mono',
}
DEFAULT_SUB = {'sans': 'Inter', 'serif': 'Source Serif 4', 'mono': 'IBM Plex Mono'}
GENERIC = {'sans-serif', 'serif', 'monospace', 'cursive', 'fantasy', 'system-ui', 'ui-sans-serif', 'ui-serif',
           'ui-monospace', '-apple-system', 'blinkmacsystemfont', 'inherit', 'initial'}
SYSTEM = {'arial', 'helvetica', 'helvetica neue', 'segoe ui', 'georgia', 'times new roman', 'times', 'verdana',
          'tahoma', 'trebuchet ms', 'courier new'}
ALERT = 'A4262C'
# Bootstrap 4 publishes these on :root whether or not the site uses them: not brand evidence
BOOTSTRAP4 = {'--blue': '#007bff', '--indigo': '#6610f2', '--purple': '#6f42c1', '--pink': '#e83e8c',
              '--red': '#dc3545', '--orange': '#fd7e14', '--yellow': '#ffc107', '--green': '#28a745',
              '--teal': '#20c997', '--cyan': '#17a2b8', '--white': '#fff', '--gray': '#6c757d',
              '--gray-dark': '#343a40', '--primary': '#007bff', '--secondary': '#6c757d', '--success': '#28a745',
              '--info': '#17a2b8', '--warning': '#ffc107', '--danger': '#dc3545', '--light': '#f8f9fa',
              '--dark': '#343a40'}


# ---------------------------------------------------------------------------------------------- colours
def rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def hexof(r, g, b):
    return '%02X%02X%02X' % tuple(int(round(max(0, min(1, c)) * 255)) for c in (r, g, b))


def lum(h):
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(lin, rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def chroma(h):
    c = rgb(h)
    return max(c) - min(c)


def sat(h):
    return colorsys.rgb_to_hls(*rgb(h))[2]


def hue(h):
    return colorsys.rgb_to_hls(*rgb(h))[0] * 360


def chromatic(h):
    return chroma(h) >= 0.12 and sat(h) >= 0.3


def neutral(h):
    return chroma(h) < 0.08


def blend(c, base='FFFFFF', a=0.25):
    """c laid over base at opacity a (a tint when base is white)."""
    x, y = rgb(c), rgb(base)
    return hexof(*(y[i] * (1 - a) + x[i] * a for i in range(3)))


def darken_to(h, target, bg='FFFFFF'):
    """Same hue and saturation, lightness lowered until the colour reads at target:1 on bg."""
    hh, l, s = colorsys.rgb_to_hls(*rgb(h))
    while contrast(hexof(*colorsys.hls_to_rgb(hh, l, s)), bg) < target and l > 0:
        l -= 0.005
    return hexof(*colorsys.hls_to_rgb(hh, max(l, 0), s))


def on(fill, want, fallback_dark):
    """The text colour for a fill: the wanted one when it reads at 4.5:1, else white or the dark text."""
    if want and contrast(fill, want) >= 4.5:
        return want
    return max(('FFFFFF', fallback_dark), key=lambda c: contrast(fill, c))


def css_color(v):
    """'#abc', '#aabbcc', '#aabbccdd' (alpha >= 0.8), 'rgb(a)(...)', 'white', 'black' -> 'AABBCC' or None."""
    v = (v or '').strip().lower()
    named = {'white': 'FFFFFF', 'black': '000000'}
    if v in named:
        return named[v]
    m = re.fullmatch(r'#([0-9a-f]{3,8})', v)
    if m:
        x = m.group(1)
        if len(x) in (3, 4):
            x = ''.join(c * 2 for c in x)
        if len(x) == 8 and int(x[6:], 16) < 204:
            return None
        return x[:6].upper() if len(x) in (6, 8) else None
    m = re.fullmatch(r'rgba?\(\s*([\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)(?:[ ,/]+([\d.]+%?))?\s*\)', v)
    if m:
        a = m.group(4)
        if a and (float(a.rstrip('%')) / (100 if a.endswith('%') else 1)) < 0.8:
            return None
        return '%02X%02X%02X' % tuple(int(float(m.group(i))) for i in (1, 2, 3))
    return None


# ---------------------------------------------------------------------------------------------- evidence
def norm_weight(w):
    return min((100, 200, 300, 400, 500, 600, 700, 800, 900), key=lambda x: abs(x - int(float(w))))


class Evidence:
    """Colour and font evidence from one or more probes, each probe weighted equally."""

    def __init__(self, probes):
        self.bg, self.text, self.text_light, self.border = Counter(), Counter(), Counter(), Counter()
        self.button, self.link, self.heading, self.logo = Counter(), Counter(), Counter(), Counter()
        self.tokens = defaultdict(list)              # colour -> [token names]
        self.body_fonts, self.faces, self.declared = Counter(), set(), defaultdict(set)
        self.headings, self.cta_faces = [], []
        n = float(len(probes))
        for p in probes:
            for f in p.get('fontFaces', []):
                fam = f['family'].strip()
                self.declared[fam.lower()].add(f.get('weight'))
                if f.get('status') == 'loaded':
                    self.faces.add(fam.lower())
        for p in probes:
            share = lambda pairs: {c: w / float(sum(x[1] for x in pairs) or 1) for c, w in pairs if c}
            for key, counter in (('bg', self.bg), ('text', self.text), ('border', self.border), ('links', self.link)):
                for c, s in share(p.get(key, [])).items():
                    counter[c] += s / n
            filled = [b for b in p.get('buttons', []) if b.get('bg') or b.get('before')]
            for b in filled:
                self.button[b.get('bg') or b.get('before')] += 1.0 / len(filled) / n
            for b in p.get('buttons', []):
                if b.get('bg') or b.get('before') or b.get('border'):          # styled calls to action only
                    txt = b.get('text', '')
                    caps = b.get('transform') == 'uppercase' or (txt.upper() == txt and any(ch.isalpha() for ch in txt))
                    self.cta_faces.append((self.resolve(b.get('family')), norm_weight(b.get('weight') or 400), caps))
            light = [t for t in p.get('textStyles', []) if t.get('ctx') == 'L']
            tot = float(sum(t['chars'] for t in light) or 1)
            for t in light:
                if t.get('color'):
                    self.text_light[t['color']] += t['chars'] / tot / n
            body = [t for t in p.get('textStyles', []) if 13 <= t['size'] <= 20]
            body_tot = float(sum(t['chars'] for t in body) or 1)
            for t in body:
                self.body_fonts[(self.resolve(t['family']), int(float(t['weight'])))] += t['chars'] / body_tot / n
            for h in p.get('headings', []):
                self.headings.append(dict(h, resolved=self.resolve(h['family'])))
                c = h.get('innerColor') or h.get('color')
                if c:
                    self.heading[c] += 1.0 / n
            for L in p.get('logos', [])[:1]:
                for c, _ in L.get('fills') or []:
                    if c:
                        self.logo[c] += 1.0 / n
            for name, v in (p.get('vars') or {}).items():
                if re.search(r'--bs-|deleted', name) or BOOTSTRAP4.get(name) == v.strip().lower():
                    continue                                   # framework defaults and deleted variables
                c = css_color(v)
                if c:
                    self.tokens[c].append(name)
        self.dark_area = sum(w for c, w in self.bg.items() if lum(c) < 0.05)
        self.dark_site = not self.text_light and self.dark_area >= 0.5

    def resolve(self, stack):
        """The family a CSS font stack renders with: first loaded web font, else first system font, else first."""
        names = [x.strip().strip('"\'') for x in (stack or '').split(',') if x.strip()]
        for x in names:
            if x.lower() in self.faces:
                return x
        for x in names:
            if x.lower() in SYSTEM:
                return x
        return next((x for x in names if x.lower() not in GENERIC), names[0] if names else 'Inter')

    def token_score(self, c, pattern):
        return sum(1 for t in self.tokens.get(c, []) if re.search(pattern, t, re.I))


# ---------------------------------------------------------------------------------------------- choices
def pick_accent(ev, why):
    scored = []
    for c in set(ev.bg) | set(ev.border) | set(ev.button) | set(ev.link) | set(ev.heading) | set(ev.tokens):
        if not chromatic(c):
            continue
        s = (4 * ev.button[c] + 2 * ev.border[c] + 1.5 * min(ev.bg[c], 0.3) + ev.link[c] + 0.5 * ev.heading[c] +
             ev.logo[c] + 0.6 * min(ev.token_score(c, r'primary|brand|accent'), 3))
        scored.append((s, c))
    scored.sort(reverse=True)
    if not scored:
        return None
    c = scored[0][1]
    why['accent'] = '%s: %s' % (c, ', '.join(x for x in (
        '%.0f%% of filled buttons' % (100 * ev.button[c]) if ev.button[c] else '',
        '%.0f%% of border length' % (100 * ev.border[c]) if ev.border[c] else '',
        '%.1f%% of background area' % (100 * ev.bg[c]) if ev.bg[c] >= 0.001 else '',
        'link colour' if ev.link[c] else '',
        'tokens ' + ', '.join(ev.tokens[c][:3]) if ev.tokens.get(c) else '') if x))
    why['accent_runners_up'] = ', '.join('%s (%.2f)' % (c2, s2) for s2, c2 in scored[1:4])
    return c


def pick_highlight(ev, dark, why):
    """A bright brand colour that reads at 4.5:1 on a dark accent (for header-row text)."""
    scored = []
    for c in set(ev.tokens) | set(ev.bg) | set(ev.text) | set(ev.border):
        if not chromatic(c) or lum(c) < 0.3 or contrast(c, dark) < 4.5:
            continue
        scored.append((ev.token_score(c, r'primary|brand|accent') + ev.bg[c] * 3 + ev.text[c] * 2 + ev.border[c] +
                       0.3 * len(ev.tokens.get(c, [])), c))
    if not scored:
        return None
    c = max(scored)[1]
    why['highlight'] = '%s: %.1f:1 on %s' % (c, contrast(c, dark), dark)
    return c


def pick_ink(ev, why):
    if ev.dark_site:
        inks = sorted(((w, c) for c, w in ev.bg.items() if lum(c) < 0.02 and chroma(c) < 0.1), reverse=True)
        if inks:
            w, c = inks[0]
            why['ink'] = ('%s: dark site (%.0f%% of page area dark, no dark text on light backgrounds): the main page '
                          'colour (%.0f%% of area) is the ink on white pages' % (c, 100 * ev.dark_area, 100 * w))
            return c
    pool = ev.text_light or Counter({c: w for c, w in ev.text.items() if lum(c) < 0.2})
    dark = [(w, c) for c, w in pool.items() if lum(c) < 0.2]
    if not dark:
        why['ink'] = '1D2630: no dark text measured (default ink)'
        return '1D2630'
    w, c = max(dark)
    why['ink'] = '%s: %.0f%% of running text on light backgrounds' % (c, 100 * w / (sum(pool.values()) or 1))
    return c


def pick_title(ev, ink, why):
    on_light = [c for c, w in ev.heading.most_common() if lum(c) < 0.2]
    darkest = min([c for c in list(ev.text) + [ink] if lum(c) < 0.2], key=lum)
    c = on_light[0] if on_light else darkest
    why['title'] = '%s: %s' % (c, 'heading colour on light backgrounds' if on_light else 'darkest text colour')
    return c


def pick_muted(ev, ink, why):
    lt = lum(ink)
    measured = [(w, c) for c, w in ev.text.items() if neutral(c) and lum(c) > lt + 0.02 and contrast(c, 'FFFFFF') > 1.6]
    tokens = [c for c in ev.tokens if neutral(c) and lum(c) > lt + 0.02 and
              ev.token_score(c, r'secondar|muted|subtle|grey|gray|caption|meta')]
    for w, c in sorted(measured, reverse=True):
        if 4.5 <= contrast(c, 'FFFFFF') <= 7.5:
            why['muted'] = '%s: secondary text on the site (%.1f:1 on white)' % (c, contrast(c, 'FFFFFF'))
            return c
    for c in sorted(tokens, key=lambda c: -ev.token_score(c, r'secondar|muted|subtle')):
        if 4.5 <= contrast(c, 'FFFFFF') <= 7.5:
            why['muted'] = '%s: token %s (%.1f:1 on white)' % (c, ev.tokens[c][0], contrast(c, 'FFFFFF'))
            return c
    src = [c for w, c in sorted(measured, reverse=True)] + tokens
    if src:
        c = darken_to(src[0], 5.0)
        why['muted'] = '%s: site grey %s darkened from %.1f:1 to %.1f:1 on white' % (
            c, src[0], contrast(src[0], 'FFFFFF'), contrast(c, 'FFFFFF'))
        return c
    why['muted'] = '59636E: default muted (no site grey found)'
    return '59636E'


def pick_panel(ev, why):
    ok = lambda c: neutral(c) and 1.12 <= contrast(c, 'FFFFFF') <= 1.45       # visibly grey, still light
    measured = sorted(((w, c) for c, w in ev.bg.items() if ok(c) and w >= 0.01), reverse=True)  # a panel, not a sliver
    if measured:
        why['panel'] = '%s: panel background, %.0f%% of area' % (measured[0][1], 100 * measured[0][0])
        return measured[0][1]
    tokens = [c for c in ev.tokens if ok(c) and ev.token_score(c, r'card|canvas|surface|panel|neutral|grey|gray|light')]
    if tokens:
        c = max(tokens, key=lambda c: ev.token_score(c, r'card|canvas|surface|panel'))
        why['panel'] = '%s: token %s' % (c, ev.tokens[c][0])
        return c
    why['panel'] = 'EEF1F4: default panel'
    return 'EEF1F4'


def pick_rule(ev, panel, why):
    """A light neutral border colour, darker than the panel (hairlines must show on white and on the panel)."""
    cands = [(w, c) for c, w in ev.border.items() if neutral(c) and 1.3 <= contrast(c, 'FFFFFF') <= 2.2]
    if cands:
        why['rule'] = '%s: border colour, %.0f%% of border length' % (max(cands)[1], 100 * max(cands)[0])
        return max(cands)[1]
    c = darken_to(panel, 1.6)
    why['rule'] = '%s: panel colour darkened to 1.6:1 on white (no light border colour measured)' % c
    return c


def pick_secondary(ev, accent):
    """A second brand colour clearly apart from the accent's hue (used for Rework when the accent is red)."""
    best = None
    for c in set(ev.bg) | set(ev.tokens) | set(ev.border):
        if chromatic(c) and min(abs(hue(c) - hue(accent)), 360 - abs(hue(c) - hue(accent))) > 60:
            s = ev.bg[c] * 3 + ev.border[c] + 0.2 * len(ev.tokens.get(c, []))
            if best is None or s > best[0]:
                best = (s, c)
    return best[1] if best else None


def build_colors(ev, a, why):
    brand = a.accent or pick_accent(ev, why)
    if a.accent:
        why['accent'] = '%s: set by the user' % brand
    ink = a.ink or pick_ink(ev, why)
    title = pick_title(ev, ink, why)
    dark = min([title, ink], key=lum)
    muted = a.muted or pick_muted(ev, ink, why)
    panel = a.panel or pick_panel(ev, why)
    rule = pick_rule(ev, panel, why)
    c = {'ink': ink, 'title': title, 'muted': muted, 'panel': panel, 'rule': rule, 'alert': ALERT}
    if brand is None:
        why['scheme'] = 'no saturated brand colour: neutral scheme on the darkest text colour'
        c.update(accent=dark, accent_text='FFFFFF', stripe=dark)
    elif lum(brand) >= 0.4:
        why['scheme'] = 'light accent: dark header rows with accent text, accent stripe'
        c.update(accent=dark, accent_text=on(dark, a.accent_text or brand, 'FFFFFF'), stripe=brand)
    elif lum(brand) >= 0.1 or chroma(brand) >= 0.5:
        why['scheme'] = 'mid accent: accent header rows, accent stripe'
        c.update(accent=brand, accent_text=on(brand, a.accent_text or 'FFFFFF', dark), stripe=brand)
    else:
        hl = a.highlight or pick_highlight(ev, brand, why)
        why['scheme'] = 'dark accent: accent header rows%s, accent stripe' % (' with highlight text' if hl else '')
        c.update(accent=brand, accent_text=on(brand, a.accent_text or hl or 'FFFFFF', 'FFFFFF'), stripe=brand)
    # section numbers: the brand colour when it reads on the panel, else the header-row colour, else the ink
    c['number'] = next((x for x in (brand, c['accent'], ink) if x and contrast(panel, x) >= 4.5), ink)
    red = brand and chromatic(brand) and (hue(brand) < 20 or hue(brand) > 340)
    if brand and lum(brand) >= 0.4:
        rework = brand
    elif red:
        sec = pick_secondary(ev, brand)
        rework = blend(sec, a=0.3) if sec else blend('F2B33D', a=0.4)
    elif brand:
        rework = blend(brand, a=0.25)
    else:
        rework = blend('F2B33D', a=0.4)
    later = blend(muted, a=0.2)
    status = {'Keep': [panel, on(panel, ink, 'FFFFFF')], 'Rework': [rework, on(rework, ink, 'FFFFFF')],
              'New': [c['accent'], c['accent_text']], 'Remove': [ALERT, 'FFFFFF'], 'Optional': ['FFFFFF', muted],
              'Later': [later, on(later, ink, 'FFFFFF')]}
    why['status'] = 'Rework %s%s' % (rework, ' (second brand colour: the accent is red, so Rework must not read '
                                              'as Remove)' if red else '')
    why['header_contrast'] = '%.1f:1' % contrast(c['accent'], c['accent_text'])
    return c, status


# ---------------------------------------------------------------------------------------------- fonts
def category(name, stack=''):
    n = name.lower()
    if 'mono' in n or 'code' in n:
        return 'mono'
    if 'sans' not in n and re.search(r'serif|slab|garamond|caslon|baskerville|bodoni|times|georgia|tiempos|'
                                     r'lyon|canela|domaine|freight|publico|sectra|recoleta|playfair|merriweather|lora', n):
        return 'serif'
    if 'monospace' in stack.lower():
        return 'mono'
    return 'serif' if re.search(r'(^|,)\s*serif\s*$', stack.lower()) else 'sans'


def open_family(family, why, role, offline=False):
    """(family used in the docx, npm version or None, substitute note or None)."""
    from doctemplate import gf_package
    if offline and family.lower() not in SUBSTITUTES:
        why.setdefault(role + '_font', '%s: availability on Google Fonts not checked (offline)' % family)
        return family, None, None
    if not offline:
        try:
            v, _ = gf_package(family)
            return family, v, None
        except Exception:
            pass
    sub = SUBSTITUTES.get(family.lower()) or DEFAULT_SUB[category(family)]
    note = '%s is not a Google Font (licensed); documents use %s, the closest open family' % (family, sub)
    why[role + '_font'] = note
    v = None
    if not offline:
        v, _ = gf_package(sub)
    return sub, v, note


def build_fonts(ev, a, why):
    if ev.body_fonts:
        (body_fam, body_w), share = max(ev.body_fonts.items(), key=lambda kv: kv[1])
    else:
        (body_fam, body_w), share = ('Inter', 400), 0
    body_w = norm_weight(body_w) if norm_weight(body_w) in (300, 400, 500) else 400
    why['body_font'] = '%s %d: %.0f%% of running text' % (body_fam, body_w, 100 * share /
                                                          (sum(ev.body_fonts.values()) or 1))
    heads = sorted([h for h in ev.headings if h['tag'] in ('h1', 'h2', 'h3')], key=lambda h: -h['size'])
    if heads:
        t_fam, t_w = heads[0]['resolved'], norm_weight(heads[0]['weight'])
        why['title_font'] = '%s %d: largest heading (%s, %.0fpx)' % (t_fam, t_w, heads[0]['tag'], heads[0]['size'])
    else:
        t_fam, t_w = body_fam, 700
    strong_w = 700 if ('700' in ev.declared.get(body_fam.lower(), set()) or not ev.declared.get(body_fam.lower())) else 600
    spec = {'body': (body_fam, body_w), 'title': (t_fam, t_w), 'strong': (body_fam, strong_w)}
    for role, arg in (('body', a.body_font), ('title', a.title_font), ('strong', a.strong_font)):
        if arg:
            f, _, w = arg.partition(':')
            spec[role] = (f.strip(), int(w or 400))
            why[role + '_font'] = '%s %s: set by the user' % (f.strip(), w or 400)
    caps = False
    if a.section_font:
        f, _, rest = a.section_font.partition(':')
        w, _, cp = rest.partition(':')
        spec['section'], caps = (f.strip(), int(w or 400)), cp.strip().lower() == 'caps'
        why['section_font'] = '%s %s%s: set by the user' % (f.strip(), w or 400, ' in capitals' if caps else '')
    elif not a.no_section_font and len(ev.cta_faces) >= 3:
        fam, k = Counter(f for f, _, _ in ev.cta_faces).most_common(1)[0]
        if k / float(len(ev.cta_faces)) >= 0.6 and fam.lower() != body_fam.lower():
            w = Counter(x for f, x, _ in ev.cta_faces if f == fam).most_common(1)[0][0]
            caps = sum(1 for f, _, cp in ev.cta_faces if f == fam and cp) / float(k) >= 0.6
            spec['section'] = (fam, w)
            why['section_font'] = ('%s %d%s: the label face of %d of %d styled calls to action; section headings '
                                   'only' % (fam, w, ' in capitals' if caps else '', k, len(ev.cta_faces)))
    fonts, versions, subs = {}, {}, {}
    for role in ('body', 'title', 'strong', 'section'):
        if role not in spec:
            continue
        fam, w = spec[role]
        used, v, note = open_family(fam, why, role, a.offline)
        if note:
            subs[fam] = used
        fonts[role] = {'family': used, 'weight': w}
        if role == 'section' and caps:
            fonts[role]['caps'] = True
        if v:
            versions[used] = v
    return fonts, versions, subs


# ---------------------------------------------------------------------------------------------- main
def confirm(path, note):
    import datetime
    from doctemplate import Theme, font_gate
    theme = json.load(open(path, encoding='utf-8'))
    th = Theme(dict(theme, font_sigs=None))
    files = th.font_files()
    ok, lines, sigs = font_gate(files, th.font_plan())
    print('\n'.join(lines))
    if not ok:
        sys.exit('font gate failed: theme not confirmed')
    theme['font_versions'] = th.font_versions
    theme['font_sigs'] = {f: s for f, s in sorted(sigs.items())}
    theme['confirmed'] = {'on': datetime.date.today().isoformat(), 'note': note}
    open(path, 'w', encoding='utf-8').write(json.dumps(theme, indent=2, ensure_ascii=False) + '\n')
    print('confirmed %s (%d font files pinned)' % (path, len(sigs)))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if '--confirm' in argv:
        note = argv[argv.index('--note') + 1] if '--note' in argv else 'approved by the user on the preview'
        return confirm(argv[argv.index('--confirm') + 1], note)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('probes', nargs='+')
    ap.add_argument('--client', required=True)
    ap.add_argument('--slug')
    ap.add_argument('--domain', action='append', default=[])
    ap.add_argument('--alias', action='append', default=[])
    ap.add_argument('--prepared-by')
    ap.add_argument('--prepared-for', help='work delivered to an agency about its client')
    ap.add_argument('--relationship')
    ap.add_argument('--never-mention', action='append', default=[])
    for k in ('accent', 'highlight', 'accent-text', 'panel', 'muted', 'ink'):
        ap.add_argument('--' + k)
    for k in ('body-font', 'title-font', 'strong-font'):
        ap.add_argument('--' + k)
    ap.add_argument('--section-font', help='"Family:weight" or "Family:weight:caps" for section headings')
    ap.add_argument('--no-section-font', action='store_true')
    ap.add_argument('--offline', action='store_true', help='skip the npm lookups (font availability unchecked)')
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    for k in ('accent', 'highlight', 'accent_text', 'panel', 'muted', 'ink'):
        if getattr(a, k):
            setattr(a, k, getattr(a, k).lstrip('#').upper())
    probes = [json.load(open(p, encoding='utf-8')) for p in a.probes]
    ev = Evidence(probes)
    why = {}
    colors, status = build_colors(ev, a, why)
    fonts, versions, subs = build_fonts(ev, a, why)
    slug = a.slug or re.sub(r'[^a-z0-9]+', '-', a.client.lower()).strip('-')
    logo = next((dict(url=L.get('src'), size='%dx%d' % (L['w'], L['h'])) for p in probes
                 for L in p.get('logos', [])[:1]), None)
    theme = {
        'client': a.client, 'slug': slug,
        'domains': a.domain or sorted({p.get('host', '').replace('www.', '') for p in probes}),
        'aliases': sorted(set([a.client] + a.alias)),
        'relationship': a.relationship, 'prepared_by': a.prepared_by, 'prepared_for': a.prepared_for,
        'never_mention': a.never_mention, 'colors': colors, 'status': status, 'fonts': fonts,
        'font_versions': versions, 'substitutes': subs, 'logo': logo,
        'provenance': {'probes': [{'url': p.get('url'), 'at': p.get('at')} for p in probes], 'why': why},
        'confirmed': None,
    }
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        open(a.out, 'w', encoding='utf-8').write(json.dumps(theme, indent=2, ensure_ascii=False) + '\n')
    print('Theme proposal for %s (%s)' % (a.client, slug))
    for k in ('scheme', 'accent', 'accent_runners_up', 'highlight', 'ink', 'title', 'muted', 'panel', 'rule',
              'status', 'header_contrast', 'body_font', 'title_font', 'strong_font', 'section_font'):
        if k in why:
            print('  %-18s %s' % (k, why[k]))
    print('  colours  ' + '  '.join('%s=%s' % kv for kv in colors.items()))
    print('  fonts    ' + '  '.join('%s=%s %d' % (k, v['family'], v['weight']) for k, v in fonts.items()))
    if subs:
        print('  SUBSTITUTED (tell the user): ' + '; '.join('%s -> %s' % kv for kv in subs.items()))
    if a.out:
        print('wrote ' + a.out)
    return theme


if __name__ == '__main__':
    main()
