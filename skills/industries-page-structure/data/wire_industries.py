# -*- coding: utf-8 -*-
"""Status-tagged wireframes of the recommended industries overview page (desktop), drawn with Pillow.

Two images: the full page by zone, and the page at launch (Later blocks left out). Block names, numbers and zones
come from benchmark.OVERVIEW and statuses from benchmark.CLIENT_STATUS, so the wireframe and the block table cannot
drift. EXAMPLE_STATUS below fills CLIENT_STATUS for the invented worked example (a ticketing platform for visitor attractions);
replace it with the client's statuses.

Palette and fonts are a neutral default. When the doc uses the client's or agency's template, set the palette and
FONT_FILES to match it.

Run: python3 wire_industries.py [out_dir]
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benchmark as B  # noqa: E402

# ============================== CONFIG ==============================
OUT = sys.argv[1] if len(sys.argv) > 1 else 'img'
INDUSTRIES = ['Museums', 'Zoos and aquariums', 'Gardens and heritage', 'Science centres']
ROUTES = ['Timed entry', 'Memberships', 'Group bookings', 'Gate scanning']
OFFER = 'Book a ticketing demo'
EXAMPLE_STATUS = {
    'o_answer': 'New', 'o_proof': 'Rework', 'o_directory': 'New', 'o_route': 'Optional', 'o_jump': 'New',
    'o_answers': 'New', 'o_why': 'Rework', 'o_stories': 'Rework', 'o_research': 'Later', 'o_recognition': 'Later',
    'o_faq': 'New', 'o_trust': 'Rework', 'o_people': 'Later', 'o_ask': 'Optional', 'o_close': 'Rework',
}
FONT_FILES = {
    'regular': ['DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/Library/Fonts/Arial.ttf', '/System/Library/Fonts/Supplemental/Arial.ttf'],
    'bold': ['DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
             '/Library/Fonts/Arial Bold.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'],
}
INK = (31, 41, 55)
MUTED = (89, 99, 110)
LINE = (156, 163, 175)
WHITE = (255, 255, 255)
# status -> (chip fill, box fill, outline, dashed)
ST = {
    'Keep': ((229, 231, 235), WHITE, INK, False),
    'New': ((167, 243, 208), (236, 253, 245), INK, False),
    'Rework': ((253, 230, 138), (255, 251, 235), INK, False),
    'Optional': (WHITE, WHITE, LINE, True),
    'Later': ((219, 234, 254), WHITE, (96, 125, 160), True),
}
X0, X1 = 40, 1260

for k, v in EXAMPLE_STATUS.items():
    B.CLIENT_STATUS.setdefault(k, v)
STATUS = {r[0]: B.CLIENT_STATUS.get(r[0], 'New') for r in B.OVERVIEW}
NUM = {r[0]: i + 1 for i, r in enumerate(B.OVERVIEW)}
NAME = {r[0]: r[2] for r in B.OVERVIEW}
# extra lines drawn inside each block of the full wireframe
DETAIL = {
    'o_answer': ['Home > Industries. H1 names the job. The answer names the industries and what the product does,',
                 'in text an AI answer can quote. Button: ' + OFFER],
    'o_proof': ['Two or three figures or one recognition, each with a source line'],
    'o_directory': ['Coverage count, then one entry per industry: name, one line in its own words, link'],
    'o_route': ['  |  '.join(ROUTES)],
    'o_jump': ['Industries  |  ' + '  |  '.join(INDUSTRIES[:3]) + '  ...  |  Evidence  |  FAQ'],
    'o_answers': ['Per industry, in directory order: what is changing, question-shaped H2, 50 to 80 word answer,',
                  'one sourced figure, standards the client confirms, proof by role, "Explore <industry>"'],
    'o_why': ['The product in one line, then one paragraph of named, dated firsts'],
    'o_stories': ['Cards tagged by industry: result, quote by role, product used'],
    'o_research': ['Typed, dated cards filtered by industry: report, post, event'],
    'o_recognition': ['Firm, report, year, placement'],
    'o_faq': ['Six to eight questions, answers in the HTML, FAQPage markup'],
    'o_trust': ['One line, links to the trust page and certifications'],
    'o_people': ['Industry leads with team bios. Reviewed by <name, role>  ·  Last reviewed <month year>  ·  Sources'],
    'o_ask': ['Two suggested questions that open an AI assistant with a neutral prompt'],
    'o_close': ['"' + OFFER + '" (same label as the hero), newsletter field, related links'],
}
_cache = {}


def font(size, weight='regular'):
    key = (weight, size)
    if key not in _cache:
        f = None
        for path in FONT_FILES[weight]:
            try:
                f = ImageFont.truetype(path, size)
                break
            except OSError:
                continue
        if f is None:
            try:
                f = ImageFont.load_default(size=size)
            except TypeError:
                f = ImageFont.load_default()
        _cache[key] = f
    return _cache[key]


class Wire:
    def __init__(self, w, h):
        self.im = Image.new('RGB', (w, h), 'white')
        self.d = ImageDraw.Draw(self.im)

    def text(self, x, y, t, size=14, weight='regular', col=INK):
        self.d.text((x, y), t, font=font(size, weight), fill=col)

    def chip(self, x, y, status):
        t = status.upper()
        w = self.d.textlength(t, font=font(12, 'bold')) + 14
        self.d.rectangle([x, y, x + w, y + 20], fill=ST[status][0], outline=INK, width=1)
        self.text(x + 7, y + 4, t, 12, 'bold')
        return w

    def dashed(self, x0, y0, x1, y1, col):
        for xx in range(x0, x1, 14):
            self.d.line([xx, y0, min(xx + 7, x1), y0], fill=col, width=2)
            self.d.line([xx, y1, min(xx + 7, x1), y1], fill=col, width=2)
        for yy in range(y0, y1, 14):
            self.d.line([x0, yy, x0, min(yy + 7, y1)], fill=col, width=2)
            self.d.line([x1, yy, x1, min(yy + 7, y1)], fill=col, width=2)

    def box(self, y, k, lines=(), ts=15):
        status = STATUS[k]
        h = ts + 22 + 20 * len(lines)
        _, fill, outline, dashed = ST[status]
        if dashed:
            self.dashed(X0, y, X1, y + h, outline)
        else:
            self.d.rectangle([X0, y, X1, y + h], fill=fill, outline=outline, width=2)
        cw = self.d.textlength(status.upper(), font=font(12, 'bold')) + 14
        self.chip(X1 - 10 - cw, y + 8, status)
        title = '%d  %s' % (NUM[k], NAME[k])
        if len(title) > 100:
            title = title[:97] + '...'
        self.text(X0 + 12, y + 8, title, ts, 'bold')
        for i, ln in enumerate(lines):
            self.text(X0 + 12, y + ts + 16 + i * 20, ln, 13, 'regular', MUTED)
        return y + h + 10

    def header(self, title, statuses):
        self.text(X0, 20, title, 24, 'bold')
        x = X0
        for s in statuses:
            x += self.chip(x, 62, s) + 8
        self.text(x + 6, 65, 'Compared with the client\'s site today', 13, 'regular', MUTED)
        return 100

    def zone(self, y, name):
        self.d.rectangle([X0, y, X1, y + 26], fill=INK)
        self.text(X0 + 10, y + 5, name.upper(), 13, 'bold', WHITE)
        return y + 34

    def save(self, path, bottom):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.im.crop((0, 0, self.im.width, bottom + 10)).save(path)
        return path


def page(title, keep, path, detail=True):
    w = Wire(1300, 2600)
    y = w.header(title, [s for s in B.STATUSES if any(STATUS[r[0]] == s for r in B.OVERVIEW if keep(r))])
    for zone in B.ZONES:
        rows = [r for r in B.OVERVIEW if r[1] == zone and keep(r)]
        if not rows:
            continue
        y = w.zone(y, zone)
        for r in rows:
            y = w.box(y, r[0], DETAIL.get(r[0], []) if detail else [], ts=15 if detail else 13)
        y += 4
    return w.save(path, y)


p1 = page('Recommended industries overview page (desktop)', lambda r: True,
          os.path.join(OUT, 'wire_industries_1.png'))
n_launch = sum(1 for r in B.OVERVIEW if STATUS[r[0]] in ('Keep', 'New', 'Rework'))
n_opt = sum(1 for r in B.OVERVIEW if STATUS[r[0]] == 'Optional')
p2 = page('The page at launch: %d blocks plus %d optional' % (n_launch, n_opt), lambda r: STATUS[r[0]] != 'Later',
          os.path.join(OUT, 'wire_industries_launch.png'), detail=False)
print('saved', p1, p2)
