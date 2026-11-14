# -*- coding: utf-8 -*-
"""Industries page structure recommendation (.docx): a worked example for industries-page-structure.

Needs python-docx and Pillow. Copy this file next to benchmark.py and wire_industries.py, code the client set and
CLIENT_STATUS in benchmark.py, edit CONFIG and the content blocks for the client, render the wireframes into IMG,
put the cropped screenshots there too (or set $IND_IMG_DIR), then run:

    python3 build_industries_doc.py out.docx

Worked example: an invented client, Gallerywren (a ticketing and membership platform for visitor attractions, on
gallerywren.example.com). It has a few short pages per venue type under another parent, no overview page, two pages
that overlap, and a testimonial carousel where proof should be. Your client's starting point will differ: rewrite
the audit, the changes and the outline to fit it. data/qc_copy.py flags
the placeholder names it finds, and the builder prints MISSING FIGURE for every image it cannot find.

Layout: a neutral default (one sans-serif font, dark grey headings, light grey label cells, one fill per status).
When the client or agency has its own document template, rebuild the structure in that template (see the
doc-template-design skill) and keep only the content.

Every count comes from benchmark.py. Every best-example name goes through seen_hub() / seen_ind(), which fail the
build when the name is not in that set.
"""
import os
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import benchmark as B  # noqa: E402

# ============================== CONFIG ==============================
CLIENT = 'Gallerywren'
SITE = 'gallerywren.example.com'
READER = 'the web team'
OFFER = 'Book a ticketing demo'
MONTH = 'Month YYYY'                     # capture month for source lines
OUT = sys.argv[1] if len(sys.argv) > 1 else 'Industries_Page_Structure.docx'
IMG = os.environ.get('IND_IMG_DIR', os.path.join(HERE, 'img'))

# the client's existing industry pages: (name today, path today, what it has, verdict, new slug or merge target)
EXISTING = [
    ('Museums', '/who-we-serve/museums', 'Hero, feature list, demo form', 'Rework', 'museums'),
    ('Zoos', '/who-we-serve/zoos', 'Hero, testimonial carousel, demo form', 'Rework', 'zoos-and-aquariums'),
    ('Aquariums', '/who-we-serve/aquariums', 'Hero and the same feature list as Zoos', 'Merge', 'zoos-and-aquariums'),
    ('Gardens', '/who-we-serve/gardens', 'Hero, one customer quote, demo form', 'Rework', 'gardens-and-heritage'),
    ('Science centres', '/who-we-serve/science-centres', 'Hero, testimonial carousel, demo form', 'Rework',
     'science-centres'),
]
ROUTES = ['Timed entry', 'Memberships', 'Group bookings', 'Gate scanning']

# statuses for the example (overview blocks are shared with wire_industries.py)
EXAMPLE_STATUS = {
    'o_answer': 'New', 'o_proof': 'Rework', 'o_directory': 'New', 'o_route': 'Optional', 'o_jump': 'New',
    'o_answers': 'New', 'o_why': 'Rework', 'o_stories': 'Rework', 'o_research': 'Later', 'o_recognition': 'Later',
    'o_faq': 'New', 'o_trust': 'Rework', 'o_people': 'Later', 'o_ask': 'Optional', 'o_close': 'Rework',
    't_hero': 'Rework', 't_jump': 'New', 't_segments': 'Later', 't_pov': 'New', 't_jobs': 'New',
    't_standards': 'Rework', 't_partners': 'Optional', 't_proof': 'Rework', 't_research': 'Later', 't_people': 'Later',
    't_faq': 'New', 't_close': 'Rework',
}
for _k, _v in EXAMPLE_STATUS.items():
    B.CLIENT_STATUS.setdefault(_k, _v)

FONT = 'Arial'
INK = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x59, 0x63, 0x6E)
HEAD_FILL = '1F2937'
LABEL_FILL = 'F2F2F2'
STATUS_FILL = {'Keep': 'E5E7EB', 'New': 'A7F3D0', 'Rework': 'FDE68A', 'Optional': 'FFFFFF', 'Later': 'DBEAFE',
               'Merge': 'FCA5A5'}
CONTENT_W = 6.5


# ============================== DOC HELPERS ==============================
def _shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    tcPr.append(shd)


def _run(p, text, size=10, bold=False, color=INK):
    r = p.add_run(text)
    r.font.name = FONT
    r.font.size = Pt(size)
    r.bold = bold
    r.font.color.rgb = color
    return r


class Doc:
    def __init__(self, header_title, img_dir):
        self.d = Document()
        self.img = img_dir
        self.fig_n = 0
        self.missing = []
        sec = self.d.sections[0]
        for side in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'):
            setattr(sec, side, Inches(1))
        st = self.d.styles['Normal']
        st.font.name = FONT
        st.font.size = Pt(10)
        _run(sec.header.paragraphs[0], header_title, size=8, color=MUTED)

    def _p(self, keep_next=False, space_after=6, align=None, page_break=False):
        p = self.d.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(space_after)
        pf.keep_with_next = keep_next
        pf.page_break_before = page_break
        if align is not None:
            p.alignment = align
        return p

    def title(self, text):
        _run(self._p(space_after=4), text, size=22, bold=True)

    def meta(self, parts):
        _run(self._p(space_after=12), '  ·  '.join(parts), size=9, color=MUTED)

    def lead(self, text):
        _run(self._p(space_after=12), text, size=11, bold=True)

    def band(self, text, new_page=False):
        p = self._p(keep_next=True, space_after=8, page_break=new_page)
        p.paragraph_format.space_before = Pt(0 if new_page else 18)
        _run(p, text, size=16, bold=True)

    def heading(self, text):
        p = self._p(keep_next=True, space_after=4)
        p.paragraph_format.space_before = Pt(10)
        _run(p, text, size=11, bold=True)

    def body(self, text, keep_next=False):
        _run(self._p(keep_next=keep_next), text)

    def table(self, header, rows, weights, sz=9, status_col=None, bold_first=False):
        t = self.d.add_table(rows=1 + len(rows), cols=len(header))
        t.style = 'Table Grid'
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        total = float(sum(weights))
        widths = [Inches(CONTENT_W * w / total) for w in weights]
        for ri, row in enumerate([header] + rows):
            for ci, val in enumerate(row):
                cell = t.rows[ri].cells[ci]
                cell.width = widths[ci]
                p = cell.paragraphs[0]
                if ri == 0:
                    _shade(cell, HEAD_FILL)
                    _run(p, str(val), size=sz, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
                else:
                    if status_col is not None and ci == status_col:
                        _shade(cell, STATUS_FILL.get(str(val), 'FFFFFF'))
                    _run(p, str(val), size=sz, bold=(bold_first and ci == 0))
        self._p(space_after=4)

    def labels(self, pairs, label_w=1.9, sz=9.5):
        t = self.d.add_table(rows=len(pairs), cols=2)
        t.style = 'Table Grid'
        for ri, (lab, val) in enumerate(pairs):
            a, b = t.rows[ri].cells
            a.width, b.width = Inches(label_w), Inches(CONTENT_W - label_w)
            _shade(a, LABEL_FILL)
            _run(a.paragraphs[0], lab, size=sz, bold=True)
            _run(b.paragraphs[0], val, size=sz)
        self._p(space_after=4)

    def _picture(self, paragraph, name, max_w, max_h):
        path = os.path.join(self.img, name)
        if not os.path.exists(path):
            self.missing.append(name)
            _run(paragraph, 'MISSING FIGURE: ' + name, bold=True)
            return
        from PIL import Image
        with Image.open(path) as im:
            w, h = im.size
        scale = min(max_w / w, max_h / h)
        paragraph.add_run().add_picture(path, width=Inches(w * scale), height=Inches(h * scale))

    def figure(self, name, caption, source, max_h=4.0):
        self.fig_n += 1
        p = self._p(keep_next=True, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
        self._picture(p, name, CONTENT_W, max_h)
        cp = self._p(keep_next=True, space_after=0)
        _run(cp, 'Figure %d. ' % self.fig_n, size=9, bold=True)
        _run(cp, caption, size=9)
        _run(self._p(space_after=10), 'Source: ' + source, size=8, color=MUTED)

    def save(self, out):
        self.d.save(out)
        if self.missing:
            print('WARNING: %d figure(s) missing from %s: %s' % (len(self.missing), self.img, ', '.join(self.missing)))


# ============================== COUNT HELPERS ==============================
def nh(*ids):
    return B.cnt(B.hubs(*ids))


def ni(*ids):
    return B.cnt(B.inds(*ids))


def seen_hub(tid, *names):
    pool = B.hubs(tid)[0] | B.hubs(tid)[1]
    bad = [x for x in names if x not in pool]
    assert not bad, 'type %d overview set lacks %s' % (tid, bad)
    return ', '.join(names)


def seen_ind(tid, *names):
    pool = B.inds(tid)[0] | B.inds(tid)[1]
    bad = [x for x in names if x not in pool]
    assert not bad, 'type %d industry page set lacks %s' % (tid, bad)
    return ', '.join(names)


errs = B.check()
assert not errs, errs
NH, NI = B.N_HUB, B.N_IND
N_CO = len(set(B.CROSS) | set(B.CLIENT_HUBS) | set(B.CLIENT_IND) | set(B.CLIENT_NAV))
SRC = 'Recommended structure built from the %d-company benchmark, %s' % (N_CO, MONTH)
OV_T = B.tally([r[0] for r in B.OVERVIEW])
TP_T = B.tally([r[0] for r in B.TEMPLATE])

# ============================== CONTENT ==============================
d = Doc(header_title='Industries Page  |  %s' % CLIENT, img_dir=IMG)
d.title('%s industries: from scattered venue pages to an industries section' % CLIENT)
d.meta(['Page structure recommendation', CLIENT, 'Prepared for ' + READER, MONTH])
d.lead('%s has a page per venue type, but no overview page, so the /industries address returns an error and two '
       'pages cover the same buyers. This recommendation adds the overview page, merges the overlap, rebuilds the '
       'industry pages on one template and moves them to /industries. It is benchmarked against %d companies (%d '
       'overview pages and %d industry pages, %d section types).' % (SITE, N_CO, NH, NI, len(B.TYPES)))

# ---------- 1  The changes, by impact ----------
d.band('1  The changes, by impact')
d.table(['#', 'Change', 'Why', 'Example'], [
    ['1', 'Replace the testimonial carousel on the industry pages with stories that carry a result.',
     'A carousel shows one quote at a time and a quote alone is thin evidence. %d of %d industry pages carry '
     'stories, results or quotes.' % (ni(16, 17, 18), NI), seen_ind(16, 'Cognizant')],
    ['2', 'Give every industry page a point of view, priorities mapped to capabilities and a short FAQ.',
     '%d of %d industry pages map priorities or products to jobs. A visible FAQ appears on %d.' % (ni(11, 12), NI, ni(33)),
     seen_ind(11, 'IBM') + ', ' + seen_ind(33, 'SAP')],
    ['3', 'Publish the overview at /industries, with a one-line answer per industry and a jump bar.',
     '%d of %d overview pages give each industry its own line. %d carry jump navigation.' % (nh(5), NH, nh(3)),
     seen_hub(5, 'Accenture')],
    ['4', 'Merge the two overlapping pages and move all pages to /industries/<slug> with one redirect each.',
     'Two pages for the same buyers split links and confuse readers and answer engines.', '-'],
    ['5', 'Put a source and date under every figure and a Reviewed by line on every page.',
     'None of the %d pages names a reviewer. Industry pages naming a source for each figure: %d of %d.'
     % (NH + NI, ni(23), NI), seen_ind(23, 'Adobe')],
    ['6', 'Group the industry links under Solutions as By industry, end the group with All industries and add a '
     'footer group.', 'The menu links the venue pages today and no overview.', 'Client set'],
], [4, 38, 40, 18], sz=9)

# ---------- 2  What exists today ----------
d.band('2  What exists today', new_page=True)
d.table(['Page today', 'Address today', 'What it has', 'Verdict', 'New address'],
        [[e[0], e[1], e[2], e[3], ('/industries/' + e[4]) if e[3] != 'Merge' else 'Merged into /industries/' + e[4]]
         for e in EXISTING], [18, 20, 30, 10, 22], status_col=3, sz=9, bold_first=True)
d.labels([
    ('Parent address', '/industries returns an error today. It becomes the overview page.'),
    ('Reusable material', 'Customer stories, product screenshots and a partner list.'),
    ('Figures on the site', 'List every figure the current pages show with its source. Any figure without a source '
                            'is dropped until %s supplies a source.' % CLIENT),
])

# ---------- 3  The overview page ----------
d.band('3  The overview page', new_page=True)
d.body('%d blocks in six zones. Status compares each block with %s today. Counts are out of the %d overview pages '
       'unless the cell says otherwise. Tally: %s.'
       % (len(B.OVERVIEW), SITE, NH, ', '.join('%s %d' % (k, v) for k, v in sorted(OV_T.items()))), keep_next=True)
rows, last = [], None
for i, r in enumerate(B.OVERVIEW):
    rows.append([str(i + 1), r[1] if r[1] != last else '', r[2], B.CLIENT_STATUS.get(r[0], '-'), B.overview_cell(r),
                 ', '.join(r[5])])
    last = r[1]
d.table(['#', 'Zone', 'Block', 'Status', 'Pages with it', 'Best example'], rows, [4, 13, 35, 9, 22, 17],
        status_col=3, sz=8)
d.figure('wire_industries_1.png', 'The recommended overview page, block by block', SRC, max_h=8.4)
d.figure('wire_industries_launch.png', 'The overview at launch, with the Later blocks left out', SRC, max_h=5.5)
d.labels([
    ('Hero', 'An H1 that names the job and a 40 to 60 word answer naming the industries and what %s does for them. '
             'Button: "%s".' % (CLIENT, OFFER)),
    ('Directory', 'A coverage count of the kinds of venue served, then one entry per industry in the menu\'s order: '
                  'the name, one line in that industry\'s words, a link.'),
    ('Second route (Optional)', 'Four cards that start from the job: %s.' % ', '.join(ROUTES)),
    ('Answers per industry', 'One open, anchored block per industry with a question-shaped H2, a 50 to 80 word answer, '
                             'one sourced figure and proof by role. Example H2: "How do zoos stop timed-entry '
                             'slots overselling on busy days?"'),
    ('Questions and people', 'Six to eight FAQ items in the HTML, a trust line linking the security page, and a '
                             'Reviewed by line with the review date and numbered sources.'),
])

# ---------- 4  The industry page template ----------
d.band('4  The industry page template', new_page=True)
d.body('%d blocks for every industry page. Status compares each block with the current pages. Tally: %s.'
       % (len(B.TEMPLATE), ', '.join('%s %d' % (k, v) for k, v in sorted(TP_T.items()))), keep_next=True)
d.table(['#', 'Block', 'Status', 'Industry pages with it', 'Best example'],
        [[str(i + 1), r[1], B.CLIENT_STATUS.get(r[0], '-'), B.template_cell(r), ', '.join(r[3])]
         for i, r in enumerate(B.TEMPLATE)], [4, 46, 10, 18, 22], status_col=2, sz=8)
d.labels([
    ('Hero', 'Home > Industries > <industry>. An H1 under 60 characters and a 30 to 40 word answer that names the buyer '
             'types, as %s\'s hero line does.' % seen_ind(1, 'SAP')),
    ('Point of view', 'Two or three sentences on what is changing for the industry, written for this page only, with '
                      'one or two sourced figures.'),
    ('Priorities and capabilities', 'Three priorities in the industry\'s words, each with the capability that answers '
                                    'it and one matching resource.'),
    ('Standards', 'The standards and certifications that apply, limited to what %s confirms.' % CLIENT),
    ('Proof', 'A story with a result for each industry. Until one exists, a quote by role. No carousel.'),
    ('People and FAQ', 'The industry lead with a team bio, the Reviewed by line, and three to six FAQ items shown on '
                       'this page only.'),
    ('Closing', '"%s", and links to two sibling industries.' % OFFER),
])

# ---------- 5  Examples from the benchmark ----------
d.band('5  Examples from the benchmark', new_page=True)
d.heading('Routes in')
d.figure('cognizant_jump.png', 'A breadcrumb and a sticky local menu that mirrors the page\'s sections',
         'cognizant.com/us/en/industries/banking-technology-solutions, ' + MONTH, max_h=2.0)
d.figure('aws_segments.png', 'A segments row with one page per segment', 'aws.amazon.com/financial-services, ' + MONTH,
         max_h=2.6)
d.heading('Answers and figures')
d.figure('accenture_lines.png', 'Each industry entry opens with a challenge line in that industry\'s terms',
         'accenture.com/en/services, ' + MONTH, max_h=3.0)
d.figure('ibm_priorities.png', 'A business priority paired with the one resource that answers it',
         'ibm.com/industries/banking-financial-markets, ' + MONTH, max_h=3.0)
d.figure('adobe_sourced.png', 'A named source under each figure', 'business.adobe.com/industries/financial-services.html, '
         + MONTH, max_h=2.6)
d.heading('Evidence and people')
d.figure('microsoft_story.png', 'A story card with a quote, the speaker\'s title, a result and the products used',
         'microsoft.com/en-us/ai/financial-services, ' + MONTH, max_h=3.0)
d.figure('mckinsey_dated.png', 'Content cards that show their dates', 'mckinsey.com/industries/financial-services/'
         'how-we-help-clients, ' + MONTH, max_h=2.6)
d.figure('pwc_contacts.png', 'Named industry leaders with contact routes (contact details blurred)',
         'pwc.com/us/en/industries/financial-services.html, ' + MONTH, max_h=2.0)

# ---------- 6  Navigation, URLs and redirects ----------
d.band('6  Navigation, URLs and redirects', new_page=True)
d.table(['From', 'To', 'Type'], [[e[1], '/industries/' + e[4], '301'] for e in EXISTING], [40, 45, 15], sz=9)
d.labels([
    ('Menu', 'The Solutions menu gets a By industry group with the industry pages, ending with All industries. '
             '%s.' % B.count_cell('nav:menu', 'hub').capitalize()),
    ('Footer', 'An Industries group with the same pages in the same order.'),
    ('Internal links', 'Update every internal link to the new addresses. Do not rely on the redirects.'),
])

# ---------- 7  CMS model and launch checklist ----------
d.band('7  CMS model and launch checklist', new_page=True)
d.labels([
    ('Content model', 'An Industries post type holds each industry\'s name, slug, order, directory line, answer, point '
                      'of view, priorities and standards. Figures, sources, people and FAQ items get their own types and '
                      'are referenced, so each fact is written once. Case studies, reports and events get an industry '
                      'field.'),
    ('Before launch', 'Overview live with the moved pages. Redirects tested. Answers, figures and FAQ answers in the '
                      'HTML. Lists in the same order everywhere. No empty lists or placeholder text.'),
    ('Structured data', 'CollectionPage, ItemList and FAQPage on the overview. WebPage with about, BreadcrumbList and '
                        'FAQPage on each industry page. lastReviewed and reviewedBy on both.'),
    ('After launch', 'Tracked prompts per industry before launch, compared after about two months.'),
])

# ---------- Appendices ----------
d.band('A  The %d companies in the benchmark' % N_CO, new_page=True)
arows = [[c, 'Client set', '[overview page]', 'Yes' if c in B.CLIENT_IND else 'No'] for c in
         sorted(set(B.CLIENT_HUBS) | set(B.CLIENT_IND) | set(B.CLIENT_NAV))]
arows += [[c, B.GROUP[c].capitalize(), B.HUB_PAGE[c], 'Yes'] for c in B.CROSS]
d.table(['Company', 'Group', 'Overview page', 'Industry page in the set'], arows, [18, 14, 52, 16], sz=8,
        bold_first=True)

d.band('B  The section library: %d section types across %d pages' % (len(B.TYPES), NH + NI), new_page=True)
lib = [[t[0].split(' (')[0], '%d of %d' % (nh(tid), NH), '%d of %d' % (ni(tid), NI),
        ('%s, %s' % (t[3][0], t[3][1])) if t[3] else 'None in the set',
        t[6]] for tid, t in B.TYPES.items()]
d.table(['Section type', 'Overview pages', 'Industry pages', 'Best example', 'Where it lands'], lib,
        [28, 12, 12, 22, 26], sz=8, bold_first=True)

d.save(OUT)
print('saved', OUT, 'figures:', d.fig_n)
