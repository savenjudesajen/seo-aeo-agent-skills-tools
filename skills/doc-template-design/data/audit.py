# -*- coding: utf-8 -*-
"""Render-and-check audit for .docx files built with doctemplate.py (or any template you adopted).

  python3 audit.py render   <file.docx> <out_dir> [--dpi 100] [--color]   page PNGs + render.pdf
  python3 audit.py compare  <dir_a> <dir_b> [--out diff_dir]              pixel diff of two renders
  python3 audit.py snapshot <file.docx> <golden.json>                     store geometry + XML hashes of an
                                                                          approved build (your golden)
  python3 audit.py verify   <file.docx> <golden.json>                     geometry vs the golden (0.5pt)
  python3 audit.py xmlcheck <file.docx> <golden.json>                     XML parts vs the golden hashes
  python3 audit.py layout   <file.docx> [--out dir]                       layout gate + colour contact sheet
  python3 audit.py theme    <file.docx> [theme.json|slug]                 fonts drawn, palette, contrast, names

Needs LibreOffice (soffice), poppler (pdftoppm), Python packages pdfplumber, numpy and Pillow.
Rendering: LibreOffice in a fresh profile per file (fonts embedded in one file stay active for every later file
of the same soffice call, so files are never batched) -> PDF -> pdftoppm.
Pixel compare: per page, the share of pixels that differ by more than 48 grey levels, the largest differing
blob and a heat map (red = only in A, blue = only in B). PASS at 0 px; NEAR when every page is under 0.05% and no
blob is taller than 3 px (anti-aliasing between LibreOffice builds); else FAIL.
Geometry fingerprint (pdfplumber): every word with position, font, size and colour, every filled rectangle,
rule and curve, rounded to 0.1pt. It is portable: a golden made from your approved build proves later builds
still sit where that one did, without carrying the approved file around.
"""
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

THRESH = 48
HERE = os.path.dirname(os.path.abspath(__file__))


def render(docx, out_dir, dpi=100, color=False):
    os.makedirs(out_dir, exist_ok=True)
    for f in glob.glob(os.path.join(out_dir, 'page-*.png')):
        os.remove(f)
    tmp = tempfile.mkdtemp(prefix='dtaudit-')
    src = os.path.join(tmp, 'in.docx')
    shutil.copy(docx, src)
    subprocess.run(['soffice', '-env:UserInstallation=file://' + os.path.join(tmp, 'profile'), '--headless',
                    '--convert-to', 'pdf', '--outdir', tmp, src], check=True, capture_output=True, timeout=240)
    pdf = os.path.join(tmp, 'in.pdf')
    subprocess.run(['pdftoppm', '-r', str(dpi)] + ([] if color else ['-gray']) +
                   ['-png', pdf, os.path.join(out_dir, 'page')], check=True)
    pages = sorted(glob.glob(os.path.join(out_dir, 'page-*.png')))
    for i, p in enumerate(pages, 1):            # pdftoppm pads numbers by page count: normalise
        os.replace(p, os.path.join(out_dir, 'page-%d.png' % i))
    shutil.copy(pdf, os.path.join(out_dir, 'render.pdf'))
    shutil.rmtree(tmp, ignore_errors=True)
    return _pages(out_dir)


def _pages(d):
    return sorted(glob.glob(os.path.join(d, 'page-*.png')), key=lambda p: int(p.rsplit('-', 1)[1][:-4]))


def _blobs(mask):
    import numpy as np
    try:
        import cv2
        n, _, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
        boxes = [tuple(int(v) for v in stats[i][:4]) for i in range(1, n)]
    except ImportError:
        ys, xs = np.nonzero(mask)
        boxes = [(int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))] \
            if len(xs) else []
    return sorted(boxes, key=lambda b: -b[2] * b[3])


def compare(dir_a, dir_b, out=None):
    import numpy as np
    from PIL import Image
    pa, pb = _pages(dir_a), _pages(dir_b)
    res = {'pages_a': len(pa), 'pages_b': len(pb), 'pages': []}
    if out:
        os.makedirs(out, exist_ok=True)
    for i, (a, b) in enumerate(zip(pa, pb), 1):
        A = np.asarray(Image.open(a).convert('L'), dtype=np.int16)
        B = np.asarray(Image.open(b).convert('L'), dtype=np.int16)
        if A.shape != B.shape:
            res['pages'].append({'page': i, 'error': 'size %s vs %s' % (A.shape, B.shape)})
            continue
        mask = np.abs(A - B) > THRESH
        boxes = _blobs(mask)
        res['pages'].append({'page': i, 'diff_px': int(mask.sum()), 'diff_pct': round(100.0 * mask.mean(), 4),
                             'blobs': len(boxes), 'largest': boxes[:5]})
        if out:
            base = (np.minimum(A, B) * 0.35 + 255 * 0.65).astype(np.uint8)
            heat = np.stack([base, base, base], -1)
            heat[(A < B - THRESH)] = [220, 30, 30]
            heat[(B < A - THRESH)] = [30, 60, 220]
            Image.fromarray(heat).save(os.path.join(out, 'diff-%d.png' % i))
    worst = max([p.get('diff_pct', 100) for p in res['pages']] or [100])
    tallest = max([bx[3] for p in res['pages'] for bx in p.get('largest', [])] or [0])
    if res['pages_a'] != res['pages_b'] or any('error' in p for p in res['pages']):
        res['verdict'] = 'FAIL'
    elif all(p['diff_px'] == 0 for p in res['pages']):
        res['verdict'] = 'PASS'
    elif worst < 0.05 and tallest <= 3:
        res['verdict'] = 'NEAR'
    else:
        res['verdict'] = 'FAIL'
    return res


def _hex(c):
    if c is None:
        return None
    if isinstance(c, (int, float)):
        c = (c, c, c)
    if len(c) == 1:
        c = (c[0], c[0], c[0])
    if len(c) == 4:   # CMYK
        k = c[3]
        c = tuple((1 - min(1, v + k)) for v in c[:3])
    return '%02X%02X%02X' % tuple(int(round(v * 255)) for v in c[:3])


def fingerprint(pdf_path):
    import pdfplumber
    fp = {'pages': []}
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(extra_attrs=['fontname', 'size', 'non_stroking_color'],
                                       keep_blank_chars=True, use_text_flow=True)
            text = [[round(w['x0'], 1), round(w['top'], 1), round(w['x1'], 1), w['fontname'].split('+')[-1],
                     round(w['size'], 1), _hex(w['non_stroking_color']), w['text']] for w in words]
            fills = sorted({(round(r['x0'], 1), round(r['top'], 1), round(r['x1'], 1), round(r['bottom'], 1),
                             _hex(r.get('non_stroking_color'))) for r in page.rects if r.get('fill')})
            rules = sorted({(round(l['x0'], 1), round(l['top'], 1), round(l['x1'], 1), round(l['bottom'], 1),
                             round(l.get('linewidth') or 0, 2)) for l in page.lines})
            shapes = sorted({(round(c['x0'], 1), round(c['top'], 1), round(c['x1'], 1), round(c['bottom'], 1),
                              _hex(c.get('non_stroking_color'))) for c in page.curves})
            fp['pages'].append({'size': [page.width, page.height], 'text': text, 'fills': [list(f) for f in fills],
                                'rules': [list(r) for r in rules], 'shapes': [list(c) for c in shapes]})
    return fp


def _render_pdf(docx, dpi=50, color=False, out=None):
    out = out or tempfile.mkdtemp(prefix='dtpdf-')
    pngs = render(docx, out, dpi, color)
    return os.path.join(out, 'render.pdf'), pngs


# ---------------------------------------------------------------------------------------------- docx reading
def _docx_xml(docx, part):
    with zipfile.ZipFile(docx) as z:
        return z.read(part).decode('utf-8') if part in z.namelist() else ''


def page_geometry(docx):
    """(page width, page height, left margin, right margin, bottom margin) in points, from the first sectPr."""
    x = _docx_xml(docx, 'word/document.xml')
    num = lambda tag, attr, default: float(re.search(r'<w:%s [^>]*w:%s="(\d+)"' % (tag, attr), x).group(1)) / 20 \
        if re.search(r'<w:%s [^>]*w:%s="(\d+)"' % (tag, attr), x) else default
    return (num('pgSz', 'w', 612), num('pgSz', 'h', 792), num('pgMar', 'left', 72), num('pgMar', 'right', 72),
            num('pgMar', 'bottom', 72))


def heading_texts(docx, styles=('Heading1', 'Heading2', 'Caption')):
    """Texts of the paragraphs in the given styles, in document order (the blocks that must keep with next)."""
    x = _docx_xml(docx, 'word/document.xml')
    out = []
    for p in re.findall(r'<w:p>(.*?)</w:p>', x, re.S):
        m = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        if m and m.group(1) in styles:
            t = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))
            if t.strip():
                out.append((m.group(1), t))
    return out


def _norm(t):
    import html
    return html.unescape(html.unescape(t)).replace('’', "'").replace('‘', "'").replace(' ', ' ')


# ---------------------------------------------------------------------------------------------- layout gate
def layout(docx, pdf_path):
    """FAIL on: a heading or figure caption with nothing under it on its page (stranded), a page before the last
    under 25% full (stub), anything drawn outside the text column or below the bottom margin. WARN on a page
    under 35% full (thin) and on a last page with fewer than three lines."""
    fp = fingerprint(pdf_path)
    pw, ph, ml, mr, mb = page_geometry(docx)
    x0, x1, bottom = ml, pw - mr, ph - mb
    issues, warns = [], []
    n = len(fp['pages'])
    heads = [(s, _norm(t).split()) for s, t in heading_texts(docx)]
    hi = 0
    for i, pg in enumerate(fp['pages'], 1):
        words = [w for w in pg['text'] if 54 < w[1] < bottom - 2]          # skip the running header
        toks = [_norm(w[6]).split() for w in words]
        flat, owner = [], []
        for k, ts in enumerate(toks):
            for tkn in ts:
                flat.append(tkn)
                owner.append(k)
        while hi < len(heads):
            style, want = heads[hi]
            hit = next((k for k in range(len(flat) - len(want) + 1) if flat[k:k + len(want)] == want), None) \
                if want else None
            if hit is None:
                break
            y = max(words[owner[j]][1] + words[owner[j]][4] for j in range(hit, hit + len(want)))
            below = [w for w in words if w[1] > y + 2] + [f for f in pg['fills'] if f[1] > y + 2]
            imgs_below = any(c[1] > y + 2 for c in pg['shapes'])
            if not below and not imgs_below:
                issues.append('p%d stranded %s at a page foot: "%s"' % (i, style, ' '.join(want)[:60]))
            hi += 1
        content = [w[1] + w[4] for w in words] + [f[3] for f in pg['fills']]
        cb = max(content) if content else 0
        top = 90 if i > 1 else 120
        full = (cb - top) / (bottom - top) if cb else 0
        if i < n and cb and full < 0.25:
            issues.append('p%d stub page: content ends at %.0f of %.0f pt' % (i, cb, bottom))
        elif i < n and cb and full < 0.35:
            warns.append('p%d thin page: content ends at %.0f of %.0f pt, look at it' % (i, cb, bottom))
        for w in pg['text']:
            if w[0] < x0 - 2 or w[2] > x1 + 2:
                issues.append('p%d text outside the column: "%s" (x %.1f to %.1f)' % (i, w[6][:50], w[0], w[2]))
        for f in pg['fills']:
            if f[0] < x0 - 4 or f[2] > x1 + 4:
                issues.append('p%d fill outside the column: %s' % (i, f))
        if i == n and len(words) < 3:
            warns.append('p%d last page holds %d lines' % (i, len(words)))
    if hi < len(heads):
        warns.append('%d heading(s) not found in the render (check them by eye), first: "%s"' % (
            len(heads) - hi, ' '.join(heads[hi][1])[:60]))
    return ('FAIL' if issues else 'PASS'), issues, warns


def contact_sheet(page_pngs, out_png, cols=4, width=300):
    from PIL import Image
    ims = [Image.open(p).convert('RGB') for p in page_pngs]
    if not ims:
        return None
    sc = width / float(ims[0].width)
    th = int(ims[0].height * sc)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (width + 12) + 12, rows * (th + 12) + 12), (120, 120, 120))
    for k, im in enumerate(ims):
        sheet.paste(im.resize((width, th)), (12 + (k % cols) * (width + 12), 12 + (k // cols) * (th + 12)))
    sheet.save(out_png)
    return out_png


# ---------------------------------------------------------------------------------------------- golden
def xml_hashes(docx):
    """Hashes of every part except embedded fonts and media (font caches built on other machines can differ)."""
    with zipfile.ZipFile(docx) as z:
        return {p: hashlib.md5(z.read(p)).hexdigest()[:12] for p in sorted(z.namelist())
                if not p.startswith('word/fonts/') and not p.startswith('word/media/')}


def verify(fp_gold, fp_new, tol=0.5):
    out = []
    if len(fp_gold['pages']) != len(fp_new['pages']):
        out.append('page count %d, expected %d' % (len(fp_new['pages']), len(fp_gold['pages'])))
    for i, (g, n) in enumerate(zip(fp_gold['pages'], fp_new['pages']), 1):
        pool = list(n['text'])
        for t in g['text']:
            same = [x for x in pool if x[6] == t[6]]
            if not same:
                out.append('p%d text missing or reflowed: "%s" (expected at x %.1f, y %.1f)' % (i, t[6][:60], t[0], t[1]))
                continue
            best = min(same, key=lambda x: abs(x[0] - t[0]) + abs(x[1] - t[1]))
            pool.remove(best)
            dx, dy = best[0] - t[0], best[1] - t[1]
            if abs(dx) > tol or abs(dy) > tol:
                out.append('p%d text moved %+.1fpt x, %+.1fpt y: "%s"' % (i, dx, dy, t[6][:60]))
            if best[3:6] != t[3:6]:
                out.append('p%d text restyled %s -> %s: "%s"' % (i, t[3:6], best[3:6], t[6][:60]))
        for t in pool:
            out.append('p%d extra text: "%s" at x %.1f, y %.1f' % (i, t[6][:60], t[0], t[1]))
        for key in ('fills', 'rules', 'shapes'):
            left = [list(x) for x in n[key]]
            for f in g[key]:
                hit = [x for x in left if x[4] == f[4] and all(abs(a - b) <= tol for a, b in zip(x[:4], f[:4]))]
                if hit:
                    left.remove(hit[0])
                else:
                    out.append('p%d %s missing: %s' % (i, key[:-1], f))
            for x in left:
                out.append('p%d extra %s: %s' % (i, key[:-1], x))
    return ('PASS' if not out else 'FAIL'), out


# ---------------------------------------------------------------------------------------------- theme check
def theme_check(docx, pdf_path, theme=None):
    """Every font drawn is one of the theme's families (DejaVuSans or LiberationSans means an embed was not
    picked up), every fill and text colour is in the palette, every theme pair reads at 4.5:1, no
    never_mention name appears."""
    sys.path.insert(0, HERE)
    import doctemplate as dt
    t = theme if isinstance(theme, dt.Theme) else dt.Theme(theme)
    issues = []
    for name, fill, col in t.contrast_pairs():
        r = dt.contrast(fill, col)
        if r < 4.5:
            issues.append('%s: %s on %s reads at %.1f:1 (needs 4.5)' % (name, col, fill, r))
    fams = {r['family'].replace(' ', '') for r in t.fonts.values() if r}
    palette = {c.upper() for c in t.colors.values()} | {c for pair in t.status.values() for c in pair} | {'FFFFFF'}
    fp = fingerprint(pdf_path)
    seen, words = set(), []
    for i, pg in enumerate(fp['pages'], 1):
        for x0, y, x1, font, size, col, text in pg['text']:
            seen.add(font)
            words.append(text)
            if col and col.upper() not in palette | {'000000'}:
                issues.append('p%d text colour %s outside the theme: "%s"' % (i, col, text[:40]))
        for f in pg['fills']:
            if f[4] and f[4].upper() not in palette:
                issues.append('p%d fill %s outside the theme at y %.0f' % (i, f[4], f[1]))
    bad = sorted(f for f in seen if not any(f.split('-')[0].startswith(x) for x in fams))
    if bad:
        issues.append('fonts outside the theme (fallback?): ' + ', '.join(bad))
    text = ' '.join(words).lower()
    for w in t.never_mention:
        if w.lower() in text:
            issues.append('mentions "%s", which %s documents must never carry' % (w, t.client))
    return ('FAIL' if issues else 'PASS'), issues, sorted(seen)


if __name__ == '__main__':
    a = sys.argv[1:]
    cmd = a[0] if a else ''
    dpi = int(a[a.index('--dpi') + 1]) if '--dpi' in a else 100
    out = a[a.index('--out') + 1] if '--out' in a else None
    if cmd == 'render':
        print('\n'.join(render(a[1], a[2], dpi, '--color' in a)))
    elif cmd == 'compare':
        r = compare(a[1], a[2], out)
        print(json.dumps(r, indent=1))
        sys.exit(r['verdict'] == 'FAIL')
    elif cmd == 'snapshot':
        pdf, _ = _render_pdf(a[1])
        json.dump({'about': 'golden of an approved build: geometry of its LibreOffice render (%s) and its XML part '
                            'hashes' % subprocess.run(['soffice', '--version'], capture_output=True,
                                                      text=True).stdout.strip(),
                   'xml_md5': xml_hashes(a[1]), 'geometry': fingerprint(pdf)}, open(a[2], 'w'), separators=(',', ':'))
        print('SNAPSHOT written: ' + a[2])
    elif cmd == 'verify':
        pdf, _ = _render_pdf(a[1])
        gold = json.load(open(a[2]))
        verdict, lines = verify(gold.get('geometry', gold), fingerprint(pdf))
        print('\n'.join(lines[:80]))
        print('GEOMETRY', verdict, '(%d differences)' % len(lines))
        sys.exit(verdict != 'PASS')
    elif cmd == 'xmlcheck':
        gold, got = json.load(open(a[2]))['xml_md5'], xml_hashes(a[1])
        bad = sorted(set(gold) ^ set(got)) + [p for p in gold if p in got and got[p] != gold[p]]
        print('\n'.join('XML differs: %s' % p for p in bad))
        print('XML', 'PASS' if not bad else 'FAIL')
        sys.exit(bool(bad))
    elif cmd == 'layout':
        out = out or tempfile.mkdtemp(prefix='dtlayout-')
        pdf, pngs = _render_pdf(a[1], 60, True, out)
        verdict, issues, warns = layout(a[1], pdf)
        sheet = contact_sheet(pngs, os.path.join(out, 'contact.png'))
        print('\n'.join(issues + ['WARN ' + w for w in warns]))
        print('LAYOUT %s  (%d pages, contact sheet %s)' % (verdict, len(pngs), sheet))
        sys.exit(verdict != 'PASS')
    elif cmd == 'theme':
        pdf, _ = _render_pdf(a[1])
        verdict, issues, fonts = theme_check(a[1], pdf, a[2] if len(a) > 2 and not a[2].startswith('--') else None)
        print('\n'.join(issues[:60]))
        print('fonts drawn: ' + ', '.join(fonts))
        print('THEME', verdict, '(%d issues)' % len(issues))
        sys.exit(verdict != 'PASS')
    else:
        print(__doc__)
