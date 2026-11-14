# -*- coding: utf-8 -*-
"""Build the competitor overview (comparison hub) page structure document as .docx. Needs python-docx (and the
figures you cropped). Neutral default layout: one sans-serif font, dark grey text, one accent colour for section
bands and status cells. Use the client's own template when they have one (swap THEME, or build with the
doc-template-design skill and keep the outline below).

Every count comes from block_model.py (which reads public_sample.py plus the client set). Fill CONTENT for the run:
anything left as '<...>' prints a warning so no placeholder ships. Figures listed in FIGURES are inserted when the
image exists in IMG_DIR and listed as missing otherwise.
Run: python3 build_hub_doc.py [out.docx]  (env HUB_IMG_DIR overrides the image folder)"""
import os
import re
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import block_model as M   # noqa: E402
import public_sample as S  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'Competitor_Overview_Page_Structure.docx')
IMG_DIR = os.environ.get('HUB_IMG_DIR', os.path.join(HERE, 'img'))
THEME = {'font': 'Arial', 'text': '222222', 'muted': '6E6E6E', 'accent': '2F4F6F', 'band_text': 'FFFFFF',
         'status': {'New': 'DCE6F0', 'Rework': 'EDEDED', 'Optional': 'FFFFFF', 'Later': 'F6F6F6'}}

C, P = M.CLIENT['name'], M.CLIENT['product']
CONTENT = {
    'date': '<month year>',
    'prepared_for': '<the design agency or the client team>',
    'today': '<one sentence: what the client site has for comparisons today>',
    # (decision, why: a count with its base from block_model, seen on). Write five or six rows for the run, the most
    # important first. Typical subjects: menu and footer placement, the comparison format, authorship and the
    # client's interest, what the first screen answers, how doubts are answered, how buyers are routed.
    'decisions': [
        ('<decision 1>', '<count with its base>', '<pages>'),
        ('<decision 2>', '<count with its base>', '<pages>'),
        ('<decision 3>', '<count with its base>', '<pages>'),
    ],
    'site_today': [  # (label, text) for section 4
        ('Existing comparison content', '<what exists (a landing page, blog posts, a sales sheet or nothing), where '
                                        'it sits, what it claims; verdict: keep, merge into /compare, redirect or '
                                        'noindex>'),
        ('Fixes before reuse', '<errors found in the existing content, each with its corrected line (see '
                               'reference/doc-structure.md, Fixes before reuse)>'),
    ],
    'launch_set': [  # (rival as it writes its name, category, why it is in the launch set)
        ('<Rival>', '<category>', '<already compared on the site / demand / rival targets the client>'),
    ],
    'blocks': {},   # key -> {'buyers': ..., 'ai': ..., 'spec': ...}; missing keys get a placeholder row
}
# figures per block key: (file, caption that says only what the image shows, source line)
FIGURES = {
    'hero': [], 'cards': [], 'table': [], 'balance': [], 'fit': [], 'faq': [], 'method': [], 'footer': [],
}
WIREFRAMES = [('wire_hub_1.png', 'The recommended comparison hub, part 1 of 3: capture and orient'),
              ('wire_hub_2.png', 'Part 2 of 3: evaluate'), ('wire_hub_3.png', 'Part 3 of 3: de-risk and convert')]

WARN = []


def rgb(h):
    return RGBColor.from_string(h)


def shade(cell, hexcolor):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hexcolor)
    tcpr.append(shd)


class Doc:
    def __init__(self):
        self.d = Document()
        st = self.d.styles['Normal']
        st.font.name = THEME['font']
        st.font.size = Pt(10.5)
        st.font.color.rgb = rgb(THEME['text'])
        self.fig_n = 0

    def _check(self, text):
        for m in re.findall(r'<[^<>]{2,300}>', text):
            WARN.append(m)
        return text

    def para(self, text, size=10.5, bold=False, color=None, italic=False, after=6):
        p = self.d.add_paragraph()
        r = p.add_run(self._check(text))
        r.font.size, r.bold, r.italic = Pt(size), bold, italic
        r.font.color.rgb = rgb(color or THEME['text'])
        p.paragraph_format.space_after = Pt(after)
        return p

    def title(self, text, meta):
        self.para(text, 22, True, after=4)
        self.para(' · '.join(meta), 10, color=THEME['muted'], after=14)

    def band(self, text, new_page=False):
        if new_page:
            self.d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        t = self.d.add_table(rows=1, cols=1)
        c = t.rows[0].cells[0]
        shade(c, THEME['accent'])
        r = c.paragraphs[0].add_run(text)
        r.bold, r.font.size, r.font.color.rgb = True, Pt(13), rgb(THEME['band_text'])
        self.d.add_paragraph().paragraph_format.space_after = Pt(2)

    def heading(self, text):
        self.para(text, 12, True, after=4)

    def table(self, header, rows, widths=None, status_col=None, size=9):
        t = self.d.add_table(rows=1, cols=len(header))
        t.style = 'Table Grid'
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, h in enumerate(header):
            c = t.rows[0].cells[i]
            shade(c, 'E4E4E4')
            r = c.paragraphs[0].add_run(h)
            r.bold, r.font.size = True, Pt(size)
        for row in rows:
            cells = t.add_row().cells
            for i, v in enumerate(row):
                r = cells[i].paragraphs[0].add_run(self._check(str(v)))
                r.font.size = Pt(size)
                if status_col is not None and i == status_col and v in THEME['status']:
                    shade(cells[i], THEME['status'][v])
        if widths:
            for row in t.rows:
                for i, w in enumerate(widths):
                    row.cells[i].width = Inches(w)
        self.d.add_paragraph().paragraph_format.space_after = Pt(2)

    def labels(self, pairs):
        self.table(['', ''], pairs, widths=[1.8, 4.9])

    def figure(self, fname, caption, source=None, width=6.3):
        path = os.path.join(IMG_DIR, fname)
        self.fig_n += 1
        if os.path.exists(path):
            self.d.add_picture(path, width=Inches(width))
        else:
            WARN.append('missing figure ' + fname)
            self.para('[Figure %d: %s]' % (self.fig_n, fname), 9, color=THEME['muted'], italic=True)
        self.para('Figure %d. %s' % (self.fig_n, caption), 9, True, after=2)
        if source:
            self.para('Source: ' + source, 8.5, color=THEME['muted'])

    def save(self, path):
        self.d.save(path)


d = Doc()
d.title('Structuring the %s competitor overview page' % C,
        ['Page structure recommendation', C, 'Prepared for ' + CONTENT['prepared_for'], CONTENT['date']])
d.para('%s This recommendation sets out a comparison hub at /compare, benchmarked against %d coded hubs (the '
       'client\'s set plus a public sample of SaaS and cross-industry hubs, Appendix A). They show %d section types, '
       'and the recommended hub carries %d blocks.' % (CONTENT['today'], M.N, len(M.LANDS), len(M.HUB)))

# 1  What to build first
d.band('1  What to build first')
d.table(['#', 'Decision', 'Why', 'Seen on'], [[str(i), a, b, c_] for i, (a, b, c_) in enumerate(CONTENT['decisions'], 1)],
        widths=[0.3, 2.7, 2.3, 1.4])
for f, cap in WIREFRAMES:
    d.figure(f, cap, 'Recommended structure, ' + CONTENT['date'])

# 2  Section order
d.band('2  The recommended section order', new_page=True)
d.para('The hub in %d blocks, in page order, grouped by the job each does for the buyer. Status compares each block '
       'with the site today. %d blocks are new, %d rework existing content, %d are optional and %d come later. '
       'Counts are out of the %d hubs unless the cell says otherwise.'
       % (len(M.HUB), M.TALLY['New'], M.TALLY['Rework'], M.TALLY['Optional'], M.TALLY['Later'], M.N))
d.table(['#', 'Stage', 'Section, in page order', 'Status', 'Hubs with it', 'Best example'],
        [[str(i), r[1], r[2], r[3], r[4], r[5] or 'Review publishers (Appendix B)'] for i, r in enumerate(M.HUB, 1)],
        widths=[0.3, 0.7, 2.2, 0.7, 1.6, 1.2], status_col=3, size=8.5)
d.heading('What launches and what waits')
d.labels([('Launch (%d blocks)' % len(M.LAUNCH), 'The new and rework blocks.'),
          ('Needs from %s at launch' % C, '<what only the client can provide: who approves the answers and where '
                                           'corrections go, the people named on the page, the basis and date of '
                                           'every proof figure, sourced facts on each rival, at least one honest '
                                           'limit>'),
          ('Optional (%d)' % M.TALLY['Optional'], 'Each adds depth and none blocks the launch.'),
          ('Later (%d)' % M.TALLY['Later'], 'Listed in section 5 with what each needs from the client.')])
d.figure('wire_hub_mobile.png', 'The hub at launch on a phone, in stacking order', 'Recommended structure')

# 3  Why this order converts
d.band('3  Why this order converts', new_page=True)
stage_rows = []
for st, why in zip(M.STAGES, [
        'Within one screen a buyer learns what the page covers, who stands behind it and what it asks of them.',
        'Buyers place themselves, by the tool they use now or by the rival they are weighing.',
        'Detail sits here for the buyers who want it, including the plain answer to replace or add.',
        'Questions that would otherwise wait for a sales call get answered, with sources a reader can check.',
        'A single next step, worded the same as the button at the top.']):
    stage_rows.append([st, ', '.join(r[2].split(':')[0] for r in M.HUB if r[1] == st), why])
d.table(['Stage', 'Sections', 'Why here'], stage_rows, widths=[0.9, 2.6, 3.2])

# 4  What the site has today
d.band('4  What the site has today', new_page=True)
d.labels(CONTENT['site_today'])

# 5  Sections to build
d.band('5  Sections to build, with benchmark examples', new_page=True)
later = []
for i, r in enumerate(M.HUB, 1):
    k, stage, name, status, count, best = r
    if status == 'Later':
        later.append(['%d . %s' % (i, name), count, CONTENT['blocks'].get(k, {}).get('needs', '<what the client '
                                                                                             'supplies>')])
        continue
    d.heading('Block %d . %s (%s)' % (i, name, status))
    for f, cap, src in FIGURES.get(k, []):
        d.figure(f, cap, src)
    b = CONTENT['blocks'].get(k, {})
    d.labels([('For buyers', b.get('buyers', '<what the block gives a buyer>')),
              ('For AI answers', b.get('ai', '<what an answer engine can quote>; ' + count)),
              ('Block %d . %s (%s)' % (i, name.split(':')[0], status), b.get('spec', '<spec: heading, copy, '
                                                                                     'component, anchors>'))])
d.heading('Blocks that wait for client content')
d.table(['Block', 'Seen on', 'Needs from the client'], later, widths=[2.2, 2.0, 2.5])

# 6  Comparison pages
d.band('6  The comparison pages the hub lists', new_page=True)
d.table(['Rival', 'Category', 'Why it is in the launch set'], [list(x) for x in CONTENT['launch_set']],
        widths=[1.6, 1.4, 3.7])
d.labels([('URL', '/compare/<client>-vs-<rival>, brand first: %d of the %d SaaS comparison pages put their own brand '
                  'first in the URL.' % (len(S.VS['url_brand_first']), len(S.VS_ALL))),
          ('Template', 'Built block by block with the competitor-comparison-page-template skill.'),
          ('After launch', '"<Rival> alternatives" pages (%d of %d SaaS companies publish them), pages comparing two '
                           'rivals, and a switch page.' % (len(S.NAV['alternatives_pages']), len(S.SAAS)))])

# 7  Navigation and URLs
d.band('7  Navigation and URLs', new_page=True)
d.labels([('Menu', 'A "Compare %s" link under the product menu, or under a Why menu when the site has one. No '
                   'top-level item.' % P),
          ('Footer', 'Heading COMPARE, the main rivals by name, then "All comparisons" (/compare).'),
          ('Title and description', '<title under 60 characters>; a meta description within the client\'s own length '
                                    'rule that names the launch rivals and the offer.'),
          ('URLs', '/compare for the hub and /compare/<client>-vs-<rival> for each page. Any existing comparison '
                   'landing page follows the verdict in section 4; when it stays, it carries noindex once /compare is '
                   'indexed and links to it.')])

# 8  CMS fields
d.band('8  CMS fields', new_page=True)
d.table(['Field', 'Type', 'Rule'], [
    ['Competitors: name, slug, order, footer order', 'Plain text, slug, number x2',
     'The name as the company writes it, slug <client>-vs-<rival>, card order, footer order.'],
    ['Category, also sells', 'Option, plain text', '"Also sells" shows as a second tag, hidden when blank.'],
    ['Best for, where the client differs', 'Plain text x2', '6 to 12 words; under 20 words.'],
    ['Where the rival leads, where the client leads', 'Plain text x2', 'One sourced line each.'],
    ['In the footer', 'Switch', 'On for the main rivals.'],
    ['Last reviewed', 'Date', 'Shown on the rival\'s comparison page.'],
    ['SEO title, meta description, social image', 'Plain text x2, image', 'Title under 60 characters.'],
    ['Page facts: author, reviewer, last reviewed, change log', 'Reference x2, date, rich text',
     'One item per hub page so every "Last reviewed" reads one date.'],
    ['Sources (shared): number, title, publisher, URL, date read, page, competitor', 'Mixed',
     'Numbers restart on each page.'],
    ['FAQ items (shared): question, answer, page, rival', 'Mixed', 'Answers of 40 to 80 words; each question on one '
                                                                   'page only.'],
    ['Comparison table (hub)', 'HTML embed or rich text', 'Cells as text, edited with the review date.'],
], widths=[2.4, 1.5, 2.8])

# 9  Build checks
d.band('9  Build checks for search and AI answers', new_page=True)
d.labels([
    ('Live text', 'Short answer, table, cards, strengths and doubt answers are HTML text, visible on load. FAQ answers '
                  'are in the HTML on load and may sit collapsed.'),
    ('Structured data', 'BreadcrumbList; CollectionPage with author, reviewedBy and lastReviewed; ItemList on the '
                        'cards; FAQPage on the FAQ. No Review or AggregateRating markup for the client or its rivals.'),
    ('Empty states', 'A rival in draft shows no card or footer link; a tag with no value hides.'),
    ('Trademarks', 'Rival names in text only, no rival logos; a trademark and no-affiliation line.'),
    ('Dates and sources', '"Last reviewed <month year>" and a change log on the hub and every comparison page; one '
                          'owner rechecks each rival every quarter and when a rival relaunches.'),
    ('One page per search', 'Once /compare is indexed, any comparison landing page that stays carries noindex and '
                            'links to it.'),
    ('Internal links', 'Each card links its comparison page; each comparison page links back to /compare and to two '
                       'related comparisons.'),
    ('Measure', 'Before launch, add the comparison prompts to AI visibility tracking and record which answers name '
                'the client; compare mentions, citations and search clicks 60 days after launch.'),
])

# Appendices
d.band('A  The hubs in the benchmark', new_page=True)
d.table(['Company', 'Group', 'Kind', 'Hub'],
        [[k, v[0], v[1], v[2]] for k, v in sorted(M.H.items(), key=lambda kv: (kv[1][0], kv[0].lower()))],
        widths=[1.4, 0.9, 1.0, 3.4], size=8.5)
d.band('B  The section library: %d section types across %d hubs' % (len(M.LANDS), M.N), new_page=True)
TYPE_NAMES = {}
try:
    with open(os.path.join(HERE, '..', 'reference', 'section-types.md'), encoding='utf-8') as fh:
        for line in fh:
            m = re.match(r'^\| (\d+) \| ([^|]+) \|', line)
            if m:
                TYPE_NAMES[int(m.group(1))] = m.group(2).strip()
except OSError:
    pass
d.table(['#', 'Section type', 'Hubs', 'On the client\'s hub'],
        [[str(t), TYPE_NAMES.get(t, 'type %d' % t), str(len(M.hubs(t))), M.LANDS[t]] for t in sorted(M.LANDS)],
        widths=[0.3, 2.4, 0.6, 3.4], size=8.5)

d.save(OUT)
print('saved', OUT, 'figures:', d.fig_n)
if WARN:
    print('WARNING: %d placeholder(s) or missing figure(s) still in the document:' % len(WARN))
    for w in sorted(set(WARN)):
        print('  ', w)
