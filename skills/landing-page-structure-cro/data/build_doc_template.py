# -*- coding: utf-8 -*-
"""
Data-driven .docx builder for a landing-page structure and CRO recommendation.

Edit the CONFIG and DATA blocks for the page you are working on, put the cropped images in IMG_DIR, then:
    pip install python-docx pillow
    python build_doc_template.py
    python check_deliverable.py <OUT>          # the gate: must print PASS
    soffice --headless --convert-to pdf <OUT> ; pdftoppm -jpeg -r 80 <out>.pdf pg

Every sample value below starts with "TBD" so the gate fails until you replace it.
A missing image is replaced by a visible "[image: …]" placeholder (the gate fails on those too), so the
document still builds while you are capturing.
Default styling is neutral; if the client has a document template, set FONT and ACCENT to match it.
"""
import os

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

try:
    from PIL import Image
except ImportError:
    Image = None

# ============================ CONFIG (edit me) ============================
SITE_NAME   = 'TBD Brand'                          # the brand whose page this is
PAGE_URL    = 'https://www.example.com/product'    # TBD: the target page
POSITIONING = 'TBD: one-line positioning the page must carry.'
FONT        = 'Calibri'
ACCENT_HEX  = '1F3A5F'                             # neutral navy; swap for the client's accent if they have a template
IMG_DIR     = './img'
OUT         = './Page_Structure_Recommendation.docx'
COMPETITORS = ['TBD CompetitorA', 'TBD CompetitorB', 'TBD CompetitorC']
CAPTURE_DATE = 'TBD: YYYY-MM-DD'

ACCENT = RGBColor.from_string(ACCENT_HEX)
DARK = RGBColor(0x2B, 0x2B, 0x2B); GRAY = RGBColor(0x5A, 0x5A, 0x5A); WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x1E, 0x7A, 0x34); BLUE = RGBColor(0x1F, 0x4E, 0x79); AMBER = RGBColor(0xB0, 0x6A, 0x00)
# The one status set (SKILL.md Step 3): Keep / Rework / Move / Promote / New.
STATUS = {'Keep': GREEN, 'Rework': AMBER, 'Promote': AMBER, 'Move': BLUE, 'New': ACCENT}
N = len(COMPETITORS)

# ============================ DATA (edit me) ============================
# Cover: optional old -> new mapping when the page is being repositioned -> (old, new)
MAPPING = [
    ('TBD: old section or message', 'TBD: new section or message'),
]
GAP_SUMMARY = 'TBD: one line, e.g. "N sections to add, N to rework, N to promote."'

# Part 1: ordered section list -> (num, section, status, drawn_from, prevalence)
ORDER_LIST = [
    ('1', 'TBD Hero: who it is for + outcome + leading action', 'Rework', 'All', f'{N}/{N}'),
    ('2', 'TBD Jump-link bar with the action pinned', 'New', 'TBD CompetitorA, TBD CompetitorB', f'2/{N}'),
    # ... fill from the de-duplicated master list, in page order ...
]
# Part 2: CRO stages -> (stage_header, [(section, status, why_here), ...]). No per-stage preamble.
STAGES = [
    ('STAGE 1 - CAPTURE (above the fold)', [
        ('TBD Hero', 'Rework', 'TBD: names the audience and the outcome; one leading action.'),
        ('TBD Jump-link bar', 'New', 'TBD: keeps the action in reach on a long page.'),
    ]),
    # ... stages 2 to 6 ...
]
DO_FIRST = ['TBD: the two or three changes with the most impact for the least effort']
# Part 2b: conversion principles cross-check -> (principle, what_changed). Only the changes they drove.
PRINCIPLES = [
    ('One action leads', 'TBD: what changed on this page.'),
]
# Part 3: current page -> (name, img, caption, what_it_is, verdict, recommendation)
CURRENT = [
    ('1. Hero', 'cur_hero.png', 'hero', 'TBD: what it is', 'Rework', 'TBD: recommendation'),
]
# Part 4: missing sections with proof -> (title, [(img, competitor_name, source_url)], why, recommendation)
GAPS = [
    ('TBD How it works', [('gap_how_it_works.png', 'TBD CompetitorA', 'https://competitor-a.example/product')],
     'TBD: why it matters', 'TBD: recommendation'),
]
SOURCES = [f'{SITE_NAME} (current) - {PAGE_URL}'] + [f'{c} - TBD url' for c in COMPETITORS]

# ============================ HELPERS ============================
doc = Document()
normal = doc.styles['Normal']; normal.font.name = FONT; normal.font.size = Pt(10.5); normal.font.color.rgb = DARK
for s in doc.sections:
    s.top_margin = Inches(0.8); s.bottom_margin = Inches(0.8); s.left_margin = Inches(0.9); s.right_margin = Inches(0.9)


def shade(cell, hx):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hx); tcPr.append(sh)


def set_cell(cell, text, bold=False, color=DARK, size=9, align='left', bg=None):
    cell.text = ''; p = cell.paragraphs[0]
    p.alignment = {'left': WD_ALIGN_PARAGRAPH.LEFT, 'center': WD_ALIGN_PARAGRAPH.CENTER,
                   'right': WD_ALIGN_PARAGRAPH.RIGHT}[align]
    r = p.add_run(text); r.bold = bold; r.font.size = Pt(size); r.font.color.rgb = color
    if bg:
        shade(cell, bg)


def title(t, sub=None):
    r = doc.add_paragraph().add_run(t); r.bold = True; r.font.size = Pt(23); r.font.color.rgb = DARK
    if sub:
        r = doc.add_paragraph().add_run(sub); r.bold = True; r.font.size = Pt(13); r.font.color.rgb = ACCENT


def h1(t):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(15); p.paragraph_format.space_after = Pt(4)
    r = p.add_run(t); r.bold = True; r.font.size = Pt(16); r.font.color.rgb = ACCENT
    pPr = p._p.get_or_add_pPr(); pb = OxmlElement('w:pBdr'); b = OxmlElement('w:bottom')
    b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), '6'); b.set(qn('w:space'), '2'); b.set(qn('w:color'), ACCENT_HEX)
    pb.append(b); pPr.append(pb)


def h2(t, color=DARK):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(11); p.paragraph_format.space_after = Pt(2)
    r = p.add_run(t); r.bold = True; r.font.size = Pt(12.5); r.font.color.rgb = color


def stage_head(t):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(10); p.paragraph_format.space_after = Pt(2)
    r = p.add_run(t); r.bold = True; r.font.size = Pt(11); r.font.color.rgb = WHITE
    pPr = p._p.get_or_add_pPr(); sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), '2B2B2B'); pPr.append(sh)


def body(t, size=10.5, space=6):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(space)
    r = p.add_run(t); r.font.size = Pt(size); r.font.color.rgb = DARK


def label(lbl, txt, lc=None):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(6)
    r = p.add_run(lbl + ' '); r.bold = True; r.font.size = Pt(10.5); r.font.color.rgb = lc or ACCENT
    r2 = p.add_run(txt); r2.font.size = Pt(10.5); r2.font.color.rgb = DARK


def caption(text):
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER; c.paragraph_format.space_after = Pt(10)
    r = c.add_run(text); r.italic = True; r.font.size = Pt(8.5); r.font.color.rgb = GRAY


def add_image(fname, cap, max_w=6.6, max_h=5.4):
    """Embed an image capped by width AND height, with a thin grey border and an italic caption."""
    path = os.path.join(IMG_DIR, fname)
    if not (Image and os.path.exists(path)):
        caption('[image: %s]  %s' % (fname, cap))
        return
    with Image.open(path) as im:
        w, h = im.size
    width = max_w
    if width * h / w > max_h:
        width = max_h * w / h
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(1)
    run = p.add_run(); run.add_picture(path, width=Inches(width))
    try:
        sp = run._r.xpath('.//pic:spPr')[0]; ln = OxmlElement('a:ln'); ln.set('w', '6350')
        sf = OxmlElement('a:solidFill'); cl = OxmlElement('a:srgbClr'); cl.set('val', 'C9C9C9')
        sf.append(cl); ln.append(sf); sp.append(ln)
    except IndexError:
        pass
    caption(cap)


def header_row(tbl, labels, bg=ACCENT_HEX):
    for i, lab in enumerate(labels):
        set_cell(tbl.rows[0].cells[i], lab, bold=True, color=WHITE, size=9.5, bg=bg)


# ============================ BUILD ============================
title(f'{SITE_NAME} page - section structure recommendation', POSITIONING)
body(f"Benchmarked against {N} competitors: {', '.join(COMPETITORS)}.")
body(GAP_SUMMARY)
if MAPPING:
    t = doc.add_table(rows=1, cols=2); t.style = 'Table Grid'; header_row(t, ['Today', 'Recommended'])
    for old, new in MAPPING:
        c = t.add_row().cells; set_cell(c[0], old); set_cell(c[1], new)

doc.add_page_break(); h1('Part 1 - Recommended section list, in page order')
t = doc.add_table(rows=1, cols=5); t.style = 'Table Grid'; t.alignment = WD_TABLE_ALIGNMENT.CENTER
header_row(t, ['#', 'Section (page order)', 'Status today', 'Drawn from', 'Prev.'])
for num, sec, st, src, prev in ORDER_LIST:
    c = t.add_row().cells
    set_cell(c[0], num, align='center', bold=True); set_cell(c[1], sec, bold=(st in ('New', 'Promote')))
    set_cell(c[2], st, bold=True, color=STATUS.get(st, DARK), align='center')
    set_cell(c[3], src, size=8.5, color=GRAY); set_cell(c[4], prev, align='center')

doc.add_page_break(); h1('Part 2 - Recommended page structure, sequenced for conversion')
for hdr, rows in STAGES:
    stage_head(hdr)
    tb = doc.add_table(rows=1, cols=3); tb.style = 'Table Grid'
    header_row(tb, ['Section', 'Status', 'Why here'], bg='595959')
    for sec, st, why in rows:
        c = tb.add_row().cells
        set_cell(c[0], sec, bold=True); set_cell(c[1], st, bold=True, color=STATUS.get(st, DARK), align='center')
        set_cell(c[2], why, size=8.7)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
h2('Do first')
for item in DO_FIRST:
    p = doc.add_paragraph(style='List Bullet'); p.add_run(item).font.size = Pt(10)

doc.add_page_break(); h1('Part 2b - Conversion principles cross-check')
t = doc.add_table(rows=1, cols=2); t.style = 'Table Grid'
header_row(t, ['Principle', 'What changed or was confirmed'])
for a, b in PRINCIPLES:
    c = t.add_row().cells; set_cell(c[0], a, bold=True); set_cell(c[1], b)

doc.add_page_break(); h1('Part 3 - The current page, section by section')
for name, img, cap, what, verdict, rec in CURRENT:
    h2(name)
    add_image(img, f'Current page - {cap}. Source: {PAGE_URL}')
    label('What it is:', what)
    label(f'Verdict - {verdict}:', rec, lc=STATUS.get(verdict, ACCENT))

doc.add_page_break(); h1('Part 4 - The missing sections, with competitor examples')
for tl, imgs, why, rec in GAPS:
    h2(tl, ACCENT)
    for fn, comp, url in imgs:
        add_image(fn, f'Where it appears - {comp}. Source: {url}')
    label('Why it matters:', why); label('Recommendation:', rec, lc=BLUE)

doc.add_page_break(); h1('Appendix - Sources and method')
body(f'Pages captured on {CAPTURE_DATE}. Sections were listed top to bottom on every page, grouped into '
     f'section types, counted across the {N} competitors and sequenced with a six-stage conversion model.')
for s in SOURCES:
    p = doc.add_paragraph(style='List Bullet'); r = p.add_run(s); r.font.size = Pt(9.5)

doc.save(OUT)
print('saved', OUT)
