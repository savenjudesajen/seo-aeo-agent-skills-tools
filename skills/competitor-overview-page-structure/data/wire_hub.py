# -*- coding: utf-8 -*-
"""Status-tagged wireframes of the recommended comparison hub, drawn from block_model.HUB so the wireframes, the order
table and the spec rows cannot drift. Needs Pillow. Neutral greys by default: pass the client's colours in STATUS_STYLE
when the document uses the client's template.

Output: wire_hub_1.png (capture and orient), wire_hub_2.png (evaluate), wire_hub_3.png (de-risk and convert) and
wire_hub_mobile.png (the launch page on a phone, in stacking order, Later blocks left out).
Run: python3 wire_hub.py [out_dir]"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import block_model as M   # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else 'img'
W_PX, X0, X1 = 1300, 40, 1260
TEXT, MUTED, LINE = (34, 34, 34), (110, 110, 110), (60, 60, 60)
# status: (fill, outline width, dashed outline)
STATUS_STYLE = {'New': ((255, 255, 255), 3, False), 'Rework': ((236, 236, 236), 2, False),
                'Optional': ((255, 255, 255), 2, True), 'Later': ((246, 246, 246), 1, True)}
# one or two placeholder lines per block, shown under the block name
HINTS = {
    'nav': ['No top-level Compare item. A Compare group in the footer as well'],
    'hero': ['Home > Compare. H1 asks the buyer\'s question; a 40 to 60 word answer names categories only'],
    'byline': ['Written by <name, role> . Reviewed by <name, role> . Last reviewed <month year>'],
    'disclose': ['Who wrote the page, and that <Client> sells a product compared here. Links How we compare'],
    'button': ['The same label closes the page'],
    'proof': ['<n> proof items; each shows what it measures, its source and its date'],
    'verdict': ['Names the rivals: when to choose each one, and where <Product> fits'],
    'effort': ['<n> platforms . <n> capabilities . <n> sources . reviewed <month year>'],
    'toc': ['Short answer | By need | Competitors | Table | Where each leads | Where it fits | FAQ | How we compare'],
    'need': ['<n> need tiles, one per tool type a buyer runs today; each links its row in the fit block'],
    'cards': ['Category tag . Rival name as it writes it . Best for: 6 to 12 words . Where <Client> differs: under 20 words'],
    'table': ['Columns: <Client>, then rivals in card order. One sentence per cell with a source number. No symbols'],
    'balance': ['Per rival: "Where <Rival> leads" and "Where <Client> leads", each sourced. One row of own limits'],
    'fit': ['The tool you run | It keeps doing | <Product> adds | Works with'],
    'explainer': ['One 30 to 50 word definition per tool type'],
    'considered': ['Tools buyers confuse with <Client>, one line each on why'],
    'market': ['Two or three dated shifts, each with a source'],
    'objections': ['<n> doubts in the buyer\'s words, each answered in two or three sentences with proof'],
    'stories': ['Named or role-attributed quotes from teams that switched or added <Product>'],
    'checklist': ['Neutral questions for any vendor. HTML text, then an ungated PDF link'],
    'faq': ['<n> questions from People Also Ask and AI prompts; answers in the HTML, may sit collapsed'],
    'method': ['Criteria, sources, reviewer, change log by month, corrections address, trademark line'],
    'sources': ['Sources 1 to n: title, publisher, date read, link'],
    'builder': ['Pick two vendors, see their rows from the table'],
    'related': ['<two or three resource links by intent>'],
    'closing': ['Same label as the hero button, then <secondary links>'],
    'footer': ['Compare: <Client> vs. <Rival> for each main rival, then All comparisons'],
}
assert set(HINTS) == set(M.KEYS)


def font(size, bold=False):
    for name in (('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), ('Arial Bold.ttf' if bold else 'Arial.ttf')):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def dashed_rect(d, box, width):
    x0, y0, x1, y1 = box
    for (a, b) in (((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)), ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))):
        length = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
        for s in range(0, length, 16):
            e = min(s + 9, length)
            if a[1] == b[1]:
                d.line([(a[0] + s, a[1]), (a[0] + e, a[1])], fill=LINE, width=width)
            else:
                d.line([(a[0], a[1] + s), (a[0], a[1] + e)], fill=LINE, width=width)


def box(d, x0, y0, x1, y1, key, title, lines=(), ts=20, ls=16):
    fill, width, dashed = STATUS_STYLE[M.HUB[M.NUM[key] - 1][3]]
    d.rectangle([x0, y0, x1, y1], fill=fill)
    if dashed:
        dashed_rect(d, (x0, y0, x1, y1), width)
    else:
        d.rectangle([x0, y0, x1, y1], outline=LINE, width=width)
    status = M.HUB[M.NUM[key] - 1][3]
    d.text((x0 + 12, y0 + 10), '%d  %s' % (M.NUM[key], title), font=font(ts, True), fill=TEXT)
    d.text((x1 - 12, y0 + 10), status.upper(), font=font(13, True), fill=MUTED, anchor='ra')
    yy = y0 + 18 + ts
    for ln in lines:
        d.text((x0 + 12, yy), ln, font=font(ls), fill=MUTED)
        yy += ls + 8


def header(d, title):
    d.text((X0, 24), title, font=font(26, True), fill=TEXT)
    x = X0
    for s in M.STATUSES:
        fill, width, dashed = STATUS_STYLE[s]
        if dashed:
            dashed_rect(d, (x, 70, x + 28, 90), width)
        else:
            d.rectangle([x, 70, x + 28, 90], fill=fill, outline=LINE, width=width)
        d.text((x + 36, 72), s, font=font(15), fill=TEXT)
        x += 150
    return 110


def stage_bar(d, y, stage):
    d.line([(X0, y + 14), (X1, y + 14)], fill=MUTED, width=1)
    d.text((X0, y), stage.upper(), font=font(14, True), fill=MUTED)
    return y + 34


def wrap(text, width_chars=110):
    out, cur = [], ''
    for w in text.split():
        if len(cur) + len(w) + 1 > width_chars:
            out.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    return out + ([cur] if cur else [])


def desktop(stages, title, path):
    rows = [r for r in M.HUB if r[1] in stages]
    est = 140 + sum(30 + 40 + 24 * len(wrap(HINTS[r[0]][0])) for r in rows) + 40 * len(stages)
    im = Image.new('RGB', (W_PX, est), 'white')
    d = ImageDraw.Draw(im)
    y = header(d, title)
    cur = None
    for r in rows:
        if r[1] != cur:
            cur = r[1]
            y = stage_bar(d, y + 6, cur)
        lines = wrap(HINTS[r[0]][0])
        h = 46 + 24 * len(lines)
        box(d, X0, y, X1, y + h, r[0], r[2][:90], lines)
        y += h + 12
    im.crop((0, 0, W_PX, y + 10)).save(path)
    return path


def mobile(path):
    keys = [r[0] for r in M.HUB if r[3] != 'Later']
    half_n = (len(keys) + 1) // 2
    pw, row = 420, 64
    ph = 40 + half_n * (row + 10)
    im = Image.new('RGB', (W_PX, ph + 160), 'white')
    d = ImageDraw.Draw(im)
    y = header(d, 'The hub at launch on a phone, in stacking order (%d blocks)' % len(keys))
    for p, part in enumerate([keys[:half_n], keys[half_n:]]):
        px = 140 + p * (pw + 180)
        d.rounded_rectangle([px, y + 10, px + pw, y + 10 + ph], radius=36, outline=TEXT, width=3, fill='white')
        by = y + 34
        for k in part:
            name = M.HUB[M.NUM[k] - 1][2].split(':')[0][:30]
            box(d, px + 16, by, px + pw - 16, by + row, k, name, (), ts=16)
            by += row + 10
        if p == 0:
            d.text((px + pw + 30, y + ph // 2), 'continues', font=font(16), fill=MUTED)
    im.save(path)
    return path


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    print(desktop(('Capture', 'Orient'), 'Recommended comparison hub, part 1 of 3: capture and orient',
                  os.path.join(OUT, 'wire_hub_1.png')))
    print(desktop(('Evaluate',), 'Part 2 of 3: evaluate', os.path.join(OUT, 'wire_hub_2.png')))
    print(desktop(('De-risk', 'Convert'), 'Part 3 of 3: de-risk and convert', os.path.join(OUT, 'wire_hub_3.png')))
    print(mobile(os.path.join(OUT, 'wire_hub_mobile.png')))
