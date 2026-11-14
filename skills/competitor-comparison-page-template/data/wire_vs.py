# -*- coding: utf-8 -*-
"""Wireframes for a "{Company} vs <Rival>" comparison page template, drawn from the block list in packed_vs.py.

  python3 wire_vs.py [out_dir] [--company Name] [--product Name] [--button "Label"] [--accent 404040]

Draws three desktop images (capture and orient; evaluate; de-risk and convert) and a phone view of the launch
page: wire_vs_1.png, wire_vs_2.png, wire_vs_3.png and wire_vs_mobile.png. Block names, numbers and statuses come
from packed_vs.VS (after STATUS_OVERRIDES), so the wireframes and the order table cannot drift. The rival stays a
placeholder: claims about a named rival belong in sourced copy, never in a wireframe. Every text line is a
placeholder that says what goes there; replace the table rows with the run's fixed row set.

Self-contained: needs Pillow only. Uses a TrueType font when one is found, else Pillow's default font.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import packed_vs as P      # noqa: E402


def opt(name, default):
    if name in sys.argv:
        return sys.argv[sys.argv.index(name) + 1]
    return default


_pos = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith('--') and not sys.argv[i - 1].startswith('--')]
OUT = _pos[0] if _pos else 'img'
CO = opt('--company', '{Company}')
PROD = opt('--product', '{Product}')
BUTTON = opt('--button', '<the site\'s one button label>')
ACCENT = opt('--accent', '404040')
ACC = tuple(int(ACCENT[i:i + 2], 16) for i in (0, 2, 4))

ST = {r[0]: r[3] for r in P.VS}
NUM = {r[0]: i + 1 for i, r in enumerate(P.VS)}
TEXT, MUTED, LINE = (43, 43, 43), (110, 110, 110), (190, 190, 190)
FILL = {'New': (228, 238, 248), 'Rework': (255, 243, 220), 'Optional': (239, 239, 239), 'Later': (241, 231, 245)}
EDGE = {'New': (31, 95, 158), 'Rework': (176, 106, 0), 'Optional': (120, 120, 120), 'Later': (120, 70, 140)}
W, X0, X1 = 1300, 40, 1260
TS, LS = 20, 16

# Placeholder row set: replace with the run's fixed rows (Best for first, How it is bought last, one row the rival
# leads). The row count here is only an example.
ROWS = ['Best for', '<Capability row>', '<Capability row>', '<Capability row>', '<Capability row>',
        '<Row the rival leads>', '<Support or service row>', 'How it is bought']
LEADS = ['', 'Leads: <tag>', 'Leads: <tag>', 'Leads: <tag>', 'Leads: <tag>', 'Leads: <Rival>', 'Leads: <tag>', '']

# Getting-started steps: as many as the company's onboarding has (three here as an example).
START_STEPS = [('Try or talk', ['Trial, demo', 'or call']), ('Set up or import', ['From <Rival>,', 'step by step']),
               ('First value', ['What a new user', 'gets first'])]

_FONTS = {}


def font(size, bold=False):
    key = (size, bold)
    if key in _FONTS:
        return _FONTS[key]
    names = (['DejaVuSans-Bold.ttf', 'Arial Bold.ttf', 'arialbd.ttf', 'Helvetica.ttc'] if bold else
             ['DejaVuSans.ttf', 'Arial.ttf', 'arial.ttf', 'Helvetica.ttc'])
    dirs = ['', '/Library/Fonts', '/System/Library/Fonts', '/System/Library/Fonts/Supplemental',
            '/usr/share/fonts/truetype/dejavu', 'C:/Windows/Fonts']
    f = None
    for d in dirs:
        for n in names:
            try:
                f = ImageFont.truetype(os.path.join(d, n) if d else n, size)
                break
            except OSError:
                continue
        if f:
            break
    if f is None:
        try:
            f = ImageFont.load_default(size)
        except TypeError:          # Pillow before 10.1
            f = ImageFont.load_default()
    _FONTS[key] = f
    return f


class Wire:
    def __init__(self, height):
        self.im = Image.new('RGB', (W, height), (255, 255, 255))
        self.d = ImageDraw.Draw(self.im)

    def text(self, x, y, s, size=16, bold=False, color=TEXT):
        self.d.text((x, y), s, font=font(size, bold), fill=color)

    def wrap(self, s, size, width):
        words, lines, cur = s.split(), [], ''
        for w_ in words:
            t = (cur + ' ' + w_).strip()
            if self.d.textlength(t, font=font(size)) <= width or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w_
        if cur:
            lines.append(cur)
        return lines

    def header(self, title, statuses):
        self.d.rectangle([0, 0, W, 64], fill=ACC)
        self.text(X0, 20, title, 22, True, (255, 255, 255))
        x = X0
        for s in statuses:
            self.d.rectangle([x, 80, x + 22, 102], fill=FILL[s], outline=EDGE[s], width=2)
            self.text(x + 30, 80, s, 16)
            x += 160
        return 120

    def navbar(self, y, stage):
        self.d.line([X0, y + 18, X1, y + 18], fill=LINE, width=2)
        self.text(X0, y, stage.upper(), 15, True, MUTED)
        return y + 30

    def box(self, x0, y0, x1, y1, status, title, lines=(), title_size=TS, line_size=LS):
        self.d.rectangle([x0, y0, x1, y1], fill=FILL[status], outline=EDGE[status], width=2)
        self.text(x0 + 12, y0 + 10, title, title_size, True)
        tag = status
        tw = self.d.textlength(tag, font=font(14, True))
        self.text(x1 - 12 - tw, y0 + 12, tag, 14, True, EDGE[status])
        yy = y0 + 18 + title_size
        for ln in lines:
            for part in self.wrap(ln, line_size, x1 - x0 - 24):
                self.text(x0 + 12, yy, part, line_size, False, MUTED)
                yy += line_size + 8

    def save(self, path, bottom):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.im.crop((0, 0, W, min(bottom, self.im.size[1]))).save(path)
        return path


def label(k, text):
    return '%d  %s' % (NUM[k], text)


def full(w, y, k, title, lines=(), h=84):
    w.box(X0, y, X1, y + h, ST[k], label(k, title), lines)
    return y + h + 12


def cell(w, x0, y0, x1, y1, lines, sizes, bolds):
    w.d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255), outline=TEXT, width=1)
    yy = y0 + 10
    for t, sz, b in zip(lines, sizes, bolds):
        w.text(x0 + 12, yy, t, sz, b, TEXT if b else MUTED)
        yy += sz + 8


def columns(w, y, k, title, heads, body, h):
    """A full-width block with n side-by-side cells: a bold head, then muted lines."""
    w.box(X0, y, X1, y + h, ST[k], label(k, title))
    n = len(heads)
    top = y + 52
    cw = (X1 - X0 - 24 - (n - 1) * 12) // n
    for i, (hd, lines) in enumerate(zip(heads, body)):
        x = X0 + 12 + i * (cw + 12)
        cell(w, x, top, x + cw, y + h - 12, [hd] + lines, [17] + [15] * len(lines), [True] + [False] * len(lines))
    return y + h + 12


def statuses():
    return [s for s in ('New', 'Rework', 'Optional', 'Later') if s in P.STATUS]


def part1():
    w = Wire(2400)
    y = w.header('Comparison page wireframe, part 1 of 3: capture and orient', statuses())
    y = w.navbar(y, 'Capture')
    top = y + 10
    w.d.rectangle([X0, top, X1, top + 560], fill=(250, 250, 250), outline=(205, 205, 205))
    l0, l1 = X0 + 14, X0 + 700
    w.box(l0, top + 12, l1, top + 220, ST['hero'], label('hero', 'Breadcrumb, H1, the difference in one line'),
          ['Breadcrumb to the comparison hub. H1: %s vs <Rival>' % CO,
           'One sentence in the rival\'s category terms on how the two differ'])
    w.box(l0, top + 232, l1, top + 318, ST['byline'], label('byline', 'Writer, checker, last reviewed'),
          ['Names link to bios; the date links to the change log'])
    w.box(l0, top + 330, l1, top + 440, ST['disclose'], label('disclose', 'Disclosure line'),
          ['Who publishes the page and what it sells; links How we compared'])
    w.box(l0, top + 452, l1, top + 546, ST['button'], label('button', 'Button: ' + BUTTON),
          ['The closing band repeats it'])
    r0, r1 = X0 + 716, X1 - 14
    w.box(r0, top + 12, r1, top + 546, ST['proof'], label('proof', 'Proof strip'),
          ['A few sourced proof points: customer logos, a scale figure, a rating or a recognition',
           'The same strip on every comparison page, never labelled as a comparison',
           'A source line under it: what each point measures, and its date'])
    y = top + 572
    y = w.navbar(y, 'Orient')
    y = full(w, y + 10, 'answer', 'Key takeaways: the short answer',
             ['A few bullets on what each product is for, one of them a rival strength, and whether they run '
              'together'], h=96)
    y = columns(w, y, 'choose', 'Choose-if lists, side by side',
                ['Choose %s if' % CO, 'Choose <Rival> if'],
                [['<A need it meets best>', '<One or two more lines>'],
                 ['<A need the rival meets best,', 'in words its customers accept>']], h=170)
    y = full(w, y, 'toc', 'On this page: links that carry each section\'s answer',
             ['Summary | Table | Pricing | Switching | Questions | Sources'], h=84)
    return w.save(os.path.join(OUT, 'wire_vs_1.png'), y + 4)


def part2():
    w = Wire(2600)
    y = w.header('Part 2 of 3: evaluate', statuses())
    y = w.navbar(y, 'Evaluate')
    tt = y + 10
    cols = ['Row', CO, '<Rival>', 'Leads']
    th = 60 + 44 + len(ROWS) * 42 + 56
    w.box(X0, tt, X1, tt + th, ST['table'], label('table', 'At-a-glance table: the same rows on every page'))
    gx0, gx1 = X0 + 14, X1 - 14
    edges = [gx0, gx0 + 360, gx0 + 690, gx0 + 1020, gx1]
    for j, c_ in enumerate(cols):
        w.d.rectangle([edges[j], tt + 52, edges[j + 1], tt + 96], fill=(236, 236, 236), outline=TEXT, width=1)
        w.text(edges[j] + 8, tt + 64, c_, 15, True)
    for i, r in enumerate(ROWS):
        yy = tt + 96 + i * 42
        for j in range(len(cols)):
            w.d.rectangle([edges[j], yy, edges[j + 1], yy + 42], fill=(255, 255, 255), outline=TEXT, width=1)
        w.text(gx0 + 8, yy + 11, r, 15, True)
        w.text(edges[1] + 8, yy + 11, 'A sentence, source [n]', 15, False, MUTED)
        w.text(edges[2] + 8, yy + 11, 'A sentence, source [n]', 15, False, MUTED)
        w.text(edges[3] + 8, yy + 11, LEADS[i], 15, False, MUTED)
    w.text(gx0, tt + 96 + len(ROWS) * 42 + 14,
           'Reviewed <Month Year>, sources numbered below. Leads tag: %s, Both or <Rival>.' % CO, 16, False, MUTED)
    y = tt + th + 12
    y = columns(w, y, 'leads', 'Where each one leads, the rival first', ['Where <Rival> leads', 'Where %s leads' % CO],
                [['A few points, each a bold lead-in', 'plus one sourced sentence'],
                 ['A few points, plus an honest', 'trade-off where one applies']], h=170)
    y = full(w, y, 'shared', 'What both do: the shared ground, one line per point',
             ['<A capability both products cover, so the reader can skip that row>'], h=84)
    w.box(X0, y, X1, y + 256, ST['rounds'], label('rounds', 'Sections by buying question: the answer in each heading'))
    for i in range(3):
        w.text(X0 + 20, y + 56 + i * 40, 'H2  <Buyer question>: <short answer>', 17, False, MUTED)
    w.text(X0 + 20, y + 56 + 3 * 40, 'Up to five sections, one short paragraph each, a link to the matching product page',
           15, False, MUTED)
    y += 268
    y = columns(w, y, 'together', 'Where they work together',
                ['What <Rival> keeps doing', 'What %s adds' % PROD, 'How they connect'],
                [['From the rival\'s', 'own pages'], ['<One or two lines>'], ['Integration, import', 'or export']], h=170)
    y = columns(w, y, 'bought', 'How each one is bought', [CO, '<Rival>'],
                [['Pricing model, first step and', 'contract, as %s signs them off' % CO],
                 ['What the rival publishes, sourced,', 'or "not published" with the date checked']], h=170)
    y = full(w, y, 'security', 'Security and data handling: certifications for both, with scope and date', h=56)
    y = full(w, y, 'context', 'Company context: dated ownership or product changes, each sourced', h=56)
    return w.save(os.path.join(OUT, 'wire_vs_2.png'), y + 4)


def part3():
    w = Wire(2400)
    y = w.header('Part 3 of 3: de-risk and convert', statuses())
    y = w.navbar(y, 'De-risk')
    y = columns(w, y + 10, 'evidence', 'Proof measured against this rival (hidden while empty)',
                ['A customer quote', 'Ratings for both', 'Outside research'],
                [['Role and date; runs both', 'or switched'], ['Site, score, review', 'count and date'],
                 ['Dated and', 'linked']], h=170)
    y = columns(w, y, 'start', 'Getting started beside <Rival>: the steps the company\'s onboarding has',
                ['%d  %s' % (i, s[0]) for i, s in enumerate(START_STEPS, 1)], [s[1] for s in START_STEPS], h=170)
    w.box(X0, y, X1, y + 250, ST['faq'], label('faq', 'FAQ: a handful of questions per rival, answers in the HTML'))
    for i, q in enumerate(['Which is easier to set up, %s or <Rival>?' % PROD, 'Does %s work with <Rival>?' % PROD,
                           'How do I move my data from <Rival>?',
                           'How is %s priced compared with <Rival>?' % PROD, 'When is <Rival> the better choice?']):
        w.text(X0 + 20, y + 56 + i * 36, '+  ' + q, 17, False, MUTED)
    y += 262
    y = full(w, y, 'method', 'How we compared: writer, checker, what was checked, change log, corrections',
             ['What was checked on each product and when; dated change log entries; how to report an error; '
              'a trademark note from the legal team'], h=112)
    y = full(w, y, 'sources', 'Numbered sources: title, publisher, date read, link', h=56)
    y = full(w, y, 'screens', '%s in action: one annotated screenshot, customer data removed' % PROD, h=56)
    y = w.navbar(y, 'Convert')
    y = full(w, y + 10, 'asset', 'Take-away: the comparison as a one-page PDF, ungated', h=56)
    y = full(w, y, 'related', 'Related comparisons: two, same category first, then All comparisons', h=56)
    y = full(w, y, 'ai', 'Ask an AI assistant: a neutral prompt that names this page', h=56)
    y = full(w, y, 'closing', 'Closing band: ' + BUTTON,
             ['One sentence on the offer, then the hero\'s button'], h=84)
    return w.save(os.path.join(OUT, 'wire_vs_3.png'), y + 4)


# Phone stacking order: page order, except the takeaways move above the proof strip so the answer shows first.
SHORT = {'hero': 'H1 and difference line', 'byline': 'Byline', 'disclose': 'Disclosure line', 'button': 'Button',
         'answer': 'Key takeaways', 'proof': 'Proof strip', 'choose': 'Choose-if lists', 'toc': 'Jump-to menu',
         'table': 'Table: a card per row', 'leads': 'Where each leads, stacked', 'shared': 'What both do',
         'rounds': 'Sections by question', 'together': 'Work together, stacked', 'bought': 'How each is bought',
         'security': 'Security and data', 'context': 'Company context', 'evidence': 'Proof against this rival',
         'start': 'Getting started', 'faq': 'FAQ accordion', 'method': 'How we compared', 'sources': 'Sources',
         'screens': 'Product in action', 'asset': 'PDF take-away', 'related': 'Related comparisons',
         'ai': 'Ask an AI assistant', 'closing': 'Closing band'}
assert set(SHORT) == set(NUM)


def mobile():
    order = [r[0] for r in P.VS if r[3] != 'Later']
    if 'answer' in order and 'proof' in order:
        order.remove('answer')
        order.insert(order.index('proof'), 'answer')
    per = (len(order) + 1) // 2
    pw, row = 400, 70
    ph = 30 + per * row + 20
    w = Wire(140 + ph + 40)
    n_opt = sum(1 for k in order if ST[k] == 'Optional')
    y = w.header('The page at launch on a phone, in stacking order (%d blocks, %d optional)' % (len(order), n_opt),
                 [s for s in ('New', 'Rework', 'Optional') if s in P.STATUS])
    for p_, part in enumerate([order[:per], order[per:]]):
        px, py = 150 + p_ * (pw + 200), y + 10
        w.d.rounded_rectangle([px, py, px + pw, py + ph], radius=36, outline=TEXT, width=3, fill=(255, 255, 255))
        by = py + 30
        for k in part:
            w.box(px + 16, by, px + pw - 16, by + row - 10, ST[k], '%d  %s' % (NUM[k], SHORT[k]), title_size=17)
            by += row
        if p_ == 0:
            w.text(px + pw + 40, py + ph // 2 - 10, 'continues', 17, False, MUTED)
    return w.save(os.path.join(OUT, 'wire_vs_mobile.png'), y + ph + 30)


if __name__ == '__main__':
    for f in (part1, part2, part3, mobile):
        print('saved', f())
