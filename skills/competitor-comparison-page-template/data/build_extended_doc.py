# -*- coding: utf-8 -*-
"""Extended build: the full "{Company} vs <Rival>" page template doc, rendered from a content spec.

  python3 build_extended_doc.py spec.py [--out file.docx]

The spec (a Python file defining SPEC, or a .json file) holds the run's own words; this script adds the parts that
come from the data so they cannot drift: the section order table (packed_vs.VS), the section library appendix
(section_library + packed_vs.LANDS) and the benchmark page list. See data/extended_spec_example.py for every field
and reference/doc-structure.md for the outline and the writing rules.

Tokens you can use in any text of the spec:
  {Company}      the spec's company field; {Product} the spec's product field
  {N}            number of benchmark pages
  {of:2}         "12 of 12" for section type 2 (several ids: {of:22,23,24})
  {n:43}         the count alone
  {blk:hero}     "Block 1 · Breadcrumb, H1 ... (New)" for a packed_vs key, used as a spec-row label
  {status:New}   how many blocks carry that status; {blocks} total blocks; {launch} New plus Rework

Block types inside a section: body, heading, table, labels, figure, page_break, and the generated ones:
order_table, stage_table, library_table, pages_table.
Needs python-docx (and Pillow for figures). Neutral default styling: use the company's own template if it has one.
"""
import json
import os
import re
import runpy
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import packed_vs as P          # noqa: E402
import section_library as L    # noqa: E402

DARK, GRAY, WHITE = RGBColor(0x2B, 0x2B, 0x2B), RGBColor(0x5A, 0x5A, 0x5A), RGBColor(0xFF, 0xFF, 0xFF)
STATUS_FILL = {'New': 'E4EEF8', 'Rework': 'FFF3DC', 'Optional': 'EFEFEF', 'Later': 'F1E7F5'}
NUM = {r[0]: i + 1 for i, r in enumerate(P.VS)}
TEXT_W = 6.7
SUBS = {}          # {Company} and {Product} from the spec's company and product fields


def fill_tokens(s):
    if not isinstance(s, str):
        return s

    def rep(m):
        kind, val = m.group(1), m.group(2)
        if kind == 'of':
            return '%d of %d' % (L.cnt(*[int(x) for x in val.split(',')]), L.N)
        if kind == 'n':
            return str(L.cnt(*[int(x) for x in val.split(',')]))
        if kind == 'blk':
            r = P.VS[NUM[val] - 1]
            return 'Block %d · %s (%s)' % (NUM[val], r[2].split(':')[0], r[3])
        if kind == 'status':
            return str(P.STATUS.get(val, 0))
        raise KeyError(m.group(0))
    s = re.sub(r'\{(of|n|blk|status):([^}]+)\}', rep, s)
    for k, v in SUBS.items():
        s = s.replace(k, v)
    return s.replace('{N}', str(L.N)).replace('{blocks}', str(len(P.VS))).replace('{launch}', str(len(P.LAUNCH)))


def shade(cell, hx):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hx)
    tcPr.append(sh)


def run(p, text, size=10, bold=False, italic=False, color=DARK):
    r = p.add_run(fill_tokens(text))
    r.font.name = 'Calibri'; r.font.size = Pt(size); r.bold = bold; r.italic = italic; r.font.color.rgb = color
    return r


class Doc:
    def __init__(self, spec, base):
        self.spec, self.base = spec, base
        SUBS.update({'{Company}': spec.get('company', '{Company}'), '{Product}': spec.get('product', '{Product}')})
        self.acc_hex = spec.get('accent', '404040').upper()
        self.acc = RGBColor.from_string(self.acc_hex)
        self.img = os.path.join(base, spec.get('img_dir', 'img'))
        self.d = Document()
        st = self.d.styles['Normal']
        st.font.name = 'Calibri'; st.font.size = Pt(10); st.font.color.rgb = DARK
        for s in self.d.sections:
            s.top_margin = s.bottom_margin = Inches(0.7)
            s.left_margin = s.right_margin = Inches(0.9)
            if spec.get('header'):
                hp = s.header.paragraphs[0]
                run(hp, fill_tokens(spec['header']), size=8, color=GRAY)
        self.d.core_properties.title = spec['title']
        self.fig_n = 0

    def para(self, text, size=10, bold=False, color=DARK, after=4, keep=False, italic=False):
        p = self.d.add_paragraph(); p.paragraph_format.space_after = Pt(after); p.paragraph_format.keep_with_next = keep
        run(p, text, size=size, bold=bold, color=color, italic=italic)
        return p

    def band(self, text, new_page=False, status=None):
        p = self.d.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto')
        sh.set(qn('w:fill'), self.acc_hex); pPr.append(sh)
        p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True; p.paragraph_format.page_break_before = new_page
        run(p, ' ' + text + (('    ' + status) if status else ''), size=13, bold=True, color=WHITE)

    def subband(self, text, status):
        p = self.d.add_paragraph()
        p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run(p, text + '  ', size=11.5, bold=True, color=self.acc)
        run(p, status, size=10, bold=True, color=GRAY)

    def table(self, head, rows, widths, status_col=None, bold_first=False, size=8.5):
        t = self.d.add_table(rows=0, cols=len(head))
        t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
        hr = t.add_row()
        for i, h in enumerate(head):
            c = hr.cells[i]; c.text = ''
            run(c.paragraphs[0], h, size=size + 0.5, bold=True, color=WHITE); shade(c, self.acc_hex)
        th = OxmlElement('w:tblHeader'); th.set(qn('w:val'), 'true'); hr._tr.get_or_add_trPr().append(th)
        for r in rows:
            row = t.add_row(); row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            for i, v in enumerate(r):
                c = row.cells[i]; c.text = ''
                run(c.paragraphs[0], str(v), size=size, bold=(bold_first and i == 0))
                if status_col is not None and i == status_col and v in STATUS_FILL:
                    shade(c, STATUS_FILL[v])
        total = float(sum(widths))
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(TEXT_W * w / total)
        self.para('', after=2)
        return t

    def labels(self, pairs, label_w=0.28):
        self.table(['', ''], [[a, b] for a, b in pairs], [label_w, 1 - label_w], bold_first=True)

    def figure(self, name, caption, source, max_w=6.2, max_h=3.2):
        path = os.path.join(self.img, name)
        self.fig_n += 1
        if not os.path.exists(path):
            print('MISSING figure', name)
            self.para('[Figure %d missing: %s]' % (self.fig_n, name), color=GRAY)
        else:
            from PIL import Image
            w, h = Image.open(path).size
            width = min(max_w, max_h * w / float(h))
            p = self.d.add_paragraph(); p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(path, width=Inches(width))
        self.para('Figure %d. %s' % (self.fig_n, caption), size=8.5, bold=False, after=0, keep=True, italic=True)
        self.para('Source: %s' % source, size=7, color=GRAY, after=6)

    # ---- generated blocks
    def order_table(self):
        rows = [[str(i + 1), r[1], r[2], r[3], r[4], r[5]] for i, r in enumerate(P.VS)]
        self.table(['#', 'Stage', 'Section, in page order', 'Status', 'Pages with it', 'Best example'], rows,
                   [4, 9, 33, 9, 24, 21], status_col=3)

    def stage_table(self):
        groups = {s: [r[2].split(':')[0] for r in P.VS if r[1] == s] for s in P.STAGES}
        why = self.spec.get('stage_why', {})
        self.table(['Stage', 'Sections', 'Why here'],
                   [[s, ', '.join(groups[s]), why.get(s, '')] for s in P.STAGES], [16, 40, 44], bold_first=True)

    def library_table(self):
        rows = []
        for tid, t in L.TYPES.items():
            p = L.pages(tid)
            rows.append([t[0].split(' (')[0], '%d + %d = %d' % (len(p & L.SAAS), len(p & L.CROSS), len(p)),
                         t[1].split(';')[0], P.LANDS[tid]])
        self.table(['Section type', 'Pages (%d + %d)' % (len(L.SAAS), len(L.CROSS)), 'Best example', 'On the company\'s pages'], rows,
                   [26, 12, 36, 26], bold_first=True, size=7.5)

    def pages_table(self):
        rows = [[k if v[2] == 'saas' else '%s (%s)' % (v[1], v[0]),
                 'Vendor, SaaS' if v[2] == 'saas' else v[3].capitalize(), v[4]] for k, v in L.PAGES.items()]
        rows += [[r[0], r[1], r[2]] for r in self.spec.get('client_set', [])]
        self.table(['Page', 'Group', 'Address'], rows, [34, 20, 46], bold_first=True, size=7.5)

    def build(self, out):
        s = self.spec
        self.para(s['title'], size=20, bold=True, after=2)
        if s.get('meta'):
            self.para(s['meta'], size=10, color=self.acc, bold=True, after=8)
        if s.get('lead'):
            self.para(s['lead'], size=10.5, after=8)
        for sec in s['sections']:
            self.band(sec['heading'], new_page=sec.get('new_page', False))
            for b in sec.get('blocks', []):
                k = b['type']
                if k == 'body':
                    self.para(b['text'], keep=b.get('keep', False))
                elif k == 'heading':
                    self.para(b['text'], size=11.5, bold=True, color=self.acc, keep=True)
                elif k == 'subband':
                    self.subband(b['text'], b.get('status', ''))
                elif k == 'table':
                    self.table(b['head'], b['rows'], b['widths'], b.get('status_col'), b.get('bold_first', False))
                elif k == 'labels':
                    self.labels(b['pairs'], b.get('label_w', 0.28))
                elif k == 'figure':
                    self.figure(b['img'], b['caption'], b['source'], b.get('max_w', 6.2), b.get('max_h', 3.2))
                elif k == 'page_break':
                    self.d.add_page_break()
                elif k in ('order_table', 'stage_table', 'library_table', 'pages_table'):
                    getattr(self, k)()
                else:
                    raise ValueError('unknown block type %r' % k)
        self.d.save(out)
        return out


def load_spec(path):
    if path.endswith('.json'):
        return json.load(open(path, encoding='utf-8'))
    return runpy.run_path(path)['SPEC']


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    spec_path = os.path.abspath(args[0])
    base = os.path.dirname(spec_path)
    spec = load_spec(spec_path)
    out = os.path.abspath(args[args.index('--out') + 1]) if '--out' in args else os.path.join(base, spec['out'])
    d = Doc(spec, base)
    d.build(out)
    print('saved', out, '| figures:', d.fig_n, '| blocks:', len(P.VS), '| pages in benchmark:', L.N)


if __name__ == '__main__':
    main()
