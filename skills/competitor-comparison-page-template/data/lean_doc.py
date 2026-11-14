# -*- coding: utf-8 -*-
'''Lean comparison-page structure doc: a page-order table, then the same order in screenshots.

  python3 lean_doc.py spec.py [--crop] [--render] [--out file.docx]

  --crop    cut each figure from its raw capture (spec crops: figure name -> [raw name, [x0, y0, x1, y1]])
  --render  convert to PDF with LibreOffice, rasterize the pages, print page count and free space per page
  --out     write the .docx here instead of the spec out path

Spec: a Python file that defines SPEC (see data/lean_spec_example.py, which documents every field),
or a .json file with the same keys. Paths in the spec are relative to the spec file folder.
Needs python-docx and Pillow. --render also needs LibreOffice and poppler (pdftoppm).
Environment (optional): SOFFICE  the LibreOffice command or a wrapper script (default: soffice);
             DOCX_VALIDATOR  a script that validates a .docx (run as: python3 $DOCX_VALIDATOR file.docx).
'''
import glob, json, os, runpy, subprocess, sys
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

DARK = RGBColor(0x2B, 0x2B, 0x2B)
GRAY = RGBColor(0x5A, 0x5A, 0x5A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x1E, 0x7A, 0x34)
AMBER = RGBColor(0xB0, 0x6A, 0x00)
BLUE = RGBColor(0x1F, 0x5F, 0x9E)
# status: (text colour, cell fill). None means the accent colour from the spec.
STATUS = {'Keep': (GREEN, 'E7F4EA'), 'Rework': (AMBER, 'FFF3DC'), 'Add': (BLUE, 'E4EEF8'), 'Remove': (None, 'FBE5E8')}
# copy-gate words: em dash, en dash, the percent sign, banned words. Names to keep out come from the spec never_mention.
BANNED = [chr(8212), chr(8211), '%', 'leverage', 'robust', 'seamless', 'comprehensive', 'ensure', 'optimiz',
          'monetiz', 'genuinely', 'honestly', 'straightforward']
AVAIL = 6.7         # text width in inches: 8.5 in page, 0.9 in side margins
MAX_ACTION = 30     # words in the What to do cell
MAX_CAPTION = 35    # words in a caption
WORD_BUDGET = 1300  # whole doc, tables and captions included; the lean doc aims for 900 to 1,300


# ---------------------------------------------------------------- low-level helpers
def shade(cell, hx):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hx)
    tcPr.append(sh)


def cell_margins(cell, top=40, bottom=40, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    m = OxmlElement('w:tcMar')
    for k, v in (('top', top), ('left', left), ('bottom', bottom), ('right', right)):
        e = OxmlElement('w:' + k); e.set(qn('w:w'), str(v)); e.set(qn('w:type'), 'dxa'); m.append(e)
    tcPr.append(m)


def run(p, text, size=10, bold=False, italic=False, color=DARK):
    r = p.add_run(text)
    r.font.name = 'Calibri'; r.font.size = Pt(size); r.bold = bold; r.italic = italic; r.font.color.rgb = color
    return r


def set_cell(cell, text, bold=False, color=DARK, size=9, bg=None):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(0)
    run(p, text, size=size, bold=bold, color=color)
    if bg:
        shade(cell, bg)
    cell_margins(cell)
    return p


def words(text):
    return len(text.split())


# ---------------------------------------------------------------- the document
class Lean:
    def __init__(self, spec, base):
        self.spec, self.base = spec, base
        self.acc_hex = spec.get('accent', '404040').upper()
        self.acc = RGBColor.from_string(self.acc_hex)
        self.img = os.path.join(base, spec.get('img_dir', 'img'))
        self.month = spec['month_year']
        self.company_tag = spec.get('company_tag', 'Company today')
        self.sources = spec.get('sources', {})
        d = self.doc = Document()
        n = d.styles['Normal']
        n.font.name = 'Calibri'; n.font.size = Pt(10); n.font.color.rgb = DARK
        for s in d.sections:
            s.top_margin = Inches(0.6); s.bottom_margin = Inches(0.6)
            s.left_margin = Inches(0.9); s.right_margin = Inches(0.9)
        z = d.settings.element.find(qn('w:zoom'))      # python-docx omits w:percent and the validator wants it
        if z is not None and z.get(qn('w:percent')) is None:
            z.set(qn('w:percent'), '100')
        d.core_properties.title = spec['title']
        d.core_properties.author = spec.get('author', '')

    def style_of(self, status):
        col, bg = STATUS[status]
        return (col or self.acc), bg

    def title(self, text, sub):
        p = self.doc.add_paragraph(); p.paragraph_format.space_after = Pt(2)
        run(p, text, size=21, bold=True)
        q = self.doc.add_paragraph(); q.paragraph_format.space_after = Pt(2)
        run(q, sub, size=12, bold=True, color=self.acc)

    def h1(self, text, before=12, page_break=False):
        p = self.doc.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        pb = OxmlElement('w:pBdr'); b = OxmlElement('w:bottom')
        b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), '6'); b.set(qn('w:space'), '2'); b.set(qn('w:color'), self.acc_hex)
        pb.append(b); pPr.append(pb)
        p.paragraph_format.space_before = Pt(before); p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        if page_break:
            p.paragraph_format.page_break_before = True
        run(p, text, size=15, bold=True, color=self.acc)

    def tnote(self, text, after=4):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(3); p.paragraph_format.space_after = Pt(after)
        run(p, text, size=9, italic=True, color=GRAY)
        return p

    def body(self, text, size=10, space=4):
        p = self.doc.add_paragraph(); p.paragraph_format.space_after = Pt(space)
        run(p, text, size=size)
        return p

    def spacer(self, pts=3, keep=True):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0); p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.keep_with_next = keep
        r = p.add_run(' '); r.font.size = Pt(pts)

    def order_table(self, rows, widths=(0.5, 1.6, 0.8, 3.8)):
        t = self.doc.add_table(rows=0, cols=4)
        t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
        hr = t.add_row()
        for i, h in enumerate(('#', 'Section', 'Status', 'What to do')):
            set_cell(hr.cells[i], h, bold=True, color=WHITE, size=9.5, bg=self.acc_hex)
        trPr = hr._tr.get_or_add_trPr(); th = OxmlElement('w:tblHeader'); th.set(qn('w:val'), 'true'); trPr.append(th)
        for num, sec, st, txt in rows:
            row = t.add_row(); row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            c = row.cells
            set_cell(c[0], str(num), bold=True, color=GRAY, size=9.5)
            set_cell(c[1], sec, bold=True, size=9.5)
            col, bg = self.style_of(st)
            set_cell(c[2], st, bold=True, color=col, size=9.5, bg=bg)
            set_cell(c[3], txt, size=9.5)
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
        for i, w in enumerate(widths):
            t.columns[i].width = Inches(w)
        return t

    def band(self, num, name, status, page_break=False):
        p = self.doc.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        pb = OxmlElement('w:pBdr'); left = OxmlElement('w:left')
        left.set(qn('w:val'), 'single'); left.set(qn('w:sz'), '24'); left.set(qn('w:space'), '4'); left.set(qn('w:color'), self.acc_hex)
        pb.append(left); pPr.append(pb)
        sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), 'F2F2F2')
        pPr.append(sh)
        pf = p.paragraph_format
        pf.space_before = Pt(8); pf.space_after = Pt(3); pf.keep_with_next = True; pf.left_indent = Inches(0.08)
        pf.tab_stops.add_tab_stop(Inches(6.65), WD_TAB_ALIGNMENT.RIGHT)
        if page_break:
            pf.page_break_before = True
        run(p, str(num) + '  ', size=11.5, bold=True, color=self.acc)
        run(p, name, size=11.5, bold=True)
        col, _bg = self.style_of(status)
        run(p, chr(9) + status, size=10.5, bold=True, color=col)

    def tag_of(self, it):
        kind = it.get('kind', 'today')
        if kind == 'today':
            return self.company_tag, self.acc
        return 'Pattern: %s (%s)' % (it['name'], kind), BLUE

    def figs(self, items, widths=None, chain=False):
        '''One borderless row of 1 to 3 figures. Each cell: picture(s), caption with tag, 7 pt source line.'''
        k = len(items)
        t = self.doc.add_table(rows=1, cols=k); t.autofit = False; t.alignment = WD_TABLE_ALIGNMENT.LEFT
        t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        cw = widths or [AVAIL / k] * k
        for i, it in enumerate(items):
            cell = t.rows[0].cells[i]; cell.width = Inches(cw[i])
            p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(2); p.paragraph_format.keep_with_next = True
            imgs = it['img'] if isinstance(it['img'], list) else [it['img']]
            for j, nm in enumerate(imgs):
                pp = p if j == 0 else cell.add_paragraph()
                pp.paragraph_format.space_after = Pt(2); pp.paragraph_format.keep_with_next = True
                pic = pp.add_run().add_picture(os.path.join(self.img, nm + '.png'), width=Inches(it['w']))
                spPr = pic._inline.xpath('.//pic:spPr')[0]          # thin grey outline so the crop reads as a screenshot
                ln = OxmlElement('a:ln'); ln.set('w', '9525')
                sf = OxmlElement('a:solidFill'); clr = OxmlElement('a:srgbClr'); clr.set('val', 'BFBFBF')
                sf.append(clr); ln.append(sf); spPr.append(ln)
            tag, tc = self.tag_of(it)
            c = cell.add_paragraph(); c.paragraph_format.space_after = Pt(0); c.paragraph_format.keep_with_next = True
            run(c, tag + '. ', size=8.5, bold=True, color=tc); run(c, it['cap'], size=8.5)
            s = cell.add_paragraph(); s.paragraph_format.space_after = Pt(0); s.paragraph_format.keep_with_next = chain
            src = self.sources.get(it['src'], it['src'])
            run(s, 'Source: %s, %s' % (src, self.month), size=7, color=GRAY)
            cell_margins(cell, top=0, bottom=40, left=0 if i == 0 else 100, right=100 if i < k - 1 else 0)
        for i, w in enumerate(cw):
            t.columns[i].width = Inches(w)
        return t

    def build(self, out):
        s = self.spec
        self.title(s['title'], s['subtitle'])
        if s.get('basis'):
            self.tnote(s['basis'], after=2)
        s1 = s.get('section1', {})
        self.h1(s1.get('heading', '1. Page order'), before=8)
        if s1.get('intro'):
            self.body(s1['intro']).paragraph_format.keep_with_next = True
        self.order_table([(r['num'], r['name'], r['status'], r['do']) for r in s['rows']])
        s2 = s.get('section2', {})
        self.h1(s2.get('heading', '2. Screenshots in page order'), before=0, page_break=s2.get('page_break', True))
        if s2.get('note'):
            self.tnote(s2['note'], after=2)
        for r in s['rows']:
            self.band(r['num'], r['name'], r['status'], page_break=r.get('page_break', False))
            frs = r.get('figrows', [])
            for j, fr in enumerate(frs):
                self.figs(fr['items'], fr.get('widths'), fr.get('chain', False))
                if j < len(frs) - 1:
                    self.spacer(keep=True)          # keeps two stacked tables from merging
        self.doc.save(out)
        return out


# ---------------------------------------------------------------- crop, lint, check, render
def load_spec(path):
    if path.endswith('.json'):
        return json.load(open(path, encoding='utf8'))
    return runpy.run_path(path)['SPEC']


def crop_all(spec, base):
    from PIL import Image
    raw = os.path.join(base, spec.get('raw_dir', 'raw')); out = os.path.join(base, spec.get('img_dir', 'img'))
    os.makedirs(out, exist_ok=True)
    for name, (src, box) in spec.get('crops', {}).items():
        im = Image.open(os.path.join(raw, src + '.png')).convert('RGB')
        if box[2] > im.size[0] or box[3] > im.size[1]:
            print('WARNING crop %s: box %s is outside %s' % (name, box, im.size))
        c = im.crop(tuple(box))
        c.save(os.path.join(out, name + '.png'), optimize=True)
        print('crop', name, c.size)


def lint(spec, base):
    warns, seen = [], set()
    img = os.path.join(base, spec.get('img_dir', 'img'))
    for r in spec['rows']:
        tag = 'row %s' % r['num']
        if r['num'] in seen:
            warns.append(tag + ': duplicate number')
        seen.add(r['num'])
        if r['status'] not in STATUS:
            warns.append('%s: status %r is not one of %s' % (tag, r['status'], '/'.join(STATUS)))
        if words(r['do']) > MAX_ACTION:
            warns.append('%s: action is %d words (max %d)' % (tag, words(r['do']), MAX_ACTION))
        if not r.get('figrows'):
            warns.append(tag + ': no screenshot')
        for fr in r.get('figrows', []):
            for it in fr['items']:
                if words(it['cap']) > MAX_CAPTION:
                    warns.append('%s: caption is %d words (max %d): %s' % (tag, words(it['cap']), MAX_CAPTION, it['cap'][:40]))
                if it.get('kind', 'today') != 'today' and not it.get('name'):
                    warns.append(tag + ': pattern figure without a name')
                for nm in (it['img'] if isinstance(it['img'], list) else [it['img']]):
                    if not os.path.exists(os.path.join(img, nm + '.png')):
                        warns.append('%s: missing image %s' % (tag, nm))
    return warns


def check(path, spec):
    d = Document(path)
    txt = [p.text for p in d.paragraphs]

    def walk(tbl):
        for r in tbl.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    txt.append(p.text)
                for t2 in c.tables:
                    walk(t2)
    for t in d.tables:
        walk(t)
    full = chr(10).join(txt)
    bad = [w for w in BANNED + list(spec.get('never_mention', [])) if w.lower() in full.lower()]
    print('forbidden hits:', bad)
    n = words(full)
    print('words:', n, '| pictures:', len(d.inline_shapes), '| rows:', len(spec['rows']))
    if n > WORD_BUDGET:
        print('LINT %d words is over the %d budget: cut text, not screenshots' % (n, WORD_BUDGET))
        bad = bad + ['word budget']
    return bad


def render(path):
    from PIL import Image
    pdfdir = os.path.join(os.path.dirname(os.path.abspath(path)), 'pdf')
    os.makedirs(pdfdir, exist_ok=True)
    for f in glob.glob(os.path.join(pdfdir, 'p-*.png')):
        os.remove(f)
    helper = os.environ.get('SOFFICE', 'soffice')
    cmd = ['python3', helper] if helper.endswith('.py') else [helper]
    subprocess.run(cmd + ['--headless', '--convert-to', 'pdf', '--outdir', pdfdir, path], check=True, capture_output=True)
    pdf = os.path.join(pdfdir, os.path.splitext(os.path.basename(path))[0] + '.pdf')
    subprocess.run(['pdftoppm', '-r', '50', '-png', pdf, os.path.join(pdfdir, 'p')], check=True)
    pages = sorted(glob.glob(os.path.join(pdfdir, 'p-*.png')))
    print('pages:', len(pages), '| images in', pdfdir)
    for i, f in enumerate(pages, 1):
        im = Image.open(f).convert('L'); w, h = im.size; px = im.load(); last = 0
        for y in range(h - 1, -1, -1):
            if any(px[x, y] < 245 for x in range(0, w, 3)):
                last = y
                break
        print('  page %d: %.1f in free above the bottom margin' % (i, (h - last) / 50.0 - 0.6))


def main():
    args = sys.argv[1:]
    paths = [a for i, a in enumerate(args) if not a.startswith('--') and (i == 0 or args[i - 1] != '--out')]
    if not paths:
        print(__doc__)
        sys.exit(1)
    spec_path = os.path.abspath(paths[0]); base = os.path.dirname(spec_path)
    spec = load_spec(spec_path)
    out = os.path.join(base, spec['out'])
    if '--out' in args:
        out = os.path.abspath(args[args.index('--out') + 1])
    if '--crop' in args:
        crop_all(spec, base)
    warns = lint(spec, base)
    for w in warns:
        print('LINT', w)
    Lean(spec, base).build(out)
    print('saved', out)
    bad = check(out, spec)
    val = os.environ.get('DOCX_VALIDATOR', '')
    if val and os.path.exists(val):
        r = subprocess.run(['python3', val, out], capture_output=True, text=True)
        print('validate:', (r.stdout.strip().splitlines() or ['no output'])[-1])
    if '--render' in args:
        render(out)
    if warns or bad:
        sys.exit(2)


if __name__ == '__main__':
    main()
