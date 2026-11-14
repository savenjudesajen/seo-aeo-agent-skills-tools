# -*- coding: utf-8 -*-
"""
python-pptx helpers for the Quick AEO Audit deck (builder script).

Two jobs:
  (A) edit an existing template IN PLACE (path A, the client has a template),
  (B) add native chart/table slides with matching chrome (both paths).

Requires: python-pptx, Pillow. Pure ASCII on purpose (some editors and
pipelines truncate files at multibyte em dashes). See reference/gotchas.md.

The palette and font below are the neutral defaults from
reference/deck-layout.md. Change them to the client's brand values if the
client supplies a template or brand guide.
"""
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Semantic colours (keep these: they carry meaning in tables)
GREEN = "166534"   # Yes / Aligned / Owns it
RED = "9B1C1C"     # No / Misaligned / Competitor
AMBER = "854D0E"   # Rarely / Partial / Open goal
# Neutral palette (swap for the client's brand if they have one)
DARK = "1F2933"    # titles, labels
MUTED = "5F6B7A"   # body text
ACCENT = "2563EB"  # client highlight, title rule, takeaway border
TINT = "EAF1FD"    # takeaway box and table header fill (light accent tint)
RULE = "D5DAE1"    # footer rule, table header underline
WHITE = "FFFFFF"
ALTROW = "F7F8FA"
FONT = "Arial"
MARGIN = 0.6       # left/right page margin in inches

EMU_PER_INCH = 914400


def E(inch):
    """Inches to EMU."""
    return Emu(int(inch * EMU_PER_INCH))


# ---------- (A) editing an existing template ----------
def find(slide, n):
    """Match a shape by numeric id prefix 'Google Shape;<n>;' (full names vary per file)."""
    pre = "Google Shape;%d;" % n
    for sh in slide.shapes:
        if sh.name.startswith(pre):
            return sh
    return None


def dump_structure(prs):
    """Print slide index, shape name and the first 60 chars of text: use it to find numeric ids."""
    for i, sl in enumerate(prs.slides, 1):
        for sh in sl.shapes:
            txt = sh.text_frame.text.strip().replace("\n", " ")[:60] if sh.has_text_frame else ""
            print("s%d | %s | %s" % (i, sh.name, txt))


def _drop_runs_after(p, keep=1):
    for extra in list(p.runs)[keep:]:
        extra._r.getparent().remove(extra._r)


def _style(run, color=None, bold=None, size=None):
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.font.bold = bold
    if size is not None:
        run.font.size = Pt(size)


def set_cell(cell, text, color=None, bold=None):
    """Replace a table cell's text in place, keeping its font; override colour/bold for semantics."""
    tf = cell.text_frame
    for extra_p in list(tf.paragraphs)[1:]:
        extra_p._p.getparent().remove(extra_p._p)
    p = tf.paragraphs[0]
    if p.runs:
        r = p.runs[0]
        r.text = text
        _drop_runs_after(p, 1)
    else:
        r = p.add_run()
        r.text = text
        r.font.size = Pt(11)
    _style(r, color, bold)


def set_simple(shape, text, color=None, bold=None, size=None):
    """Replace the first paragraph's text of a shape, keeping the first run's formatting."""
    p = shape.text_frame.paragraphs[0]
    if p.runs:
        r = p.runs[0]
        r.text = text
        _drop_runs_after(p, 1)
    else:
        r = p.add_run()
        r.text = text
    _style(r, color, bold, size)


def set_callout_body(shape, body, label_runs=1):
    """Callout whose first run(s) are a styled label and the rest is the body (path A, some templates).

    Replaces the text of the first body run and drops the rest, keeping the label run(s) and their styling.
    """
    p = shape.text_frame.paragraphs[0]
    runs = p.runs
    if len(runs) > label_runs:
        runs[label_runs].text = body
        _drop_runs_after(p, label_runs + 1)
    elif runs:
        runs[-1].text = runs[-1].text.rstrip() + " " + body


def renumber_footers(prs):
    """Set every pure-digit (<=2 char) text shape to its 1-based slide position. Re-run after adding slides."""
    for i, sl in enumerate(prs.slides, 1):
        for sh in sl.shapes:
            if sh.has_text_frame and not getattr(sh, "has_table", False):
                t = sh.text_frame.text.strip()
                if t.isdigit() and len(t) <= 2:
                    set_simple(sh, str(i))


def _all_runs(prs):
    for sl in prs.slides:
        for sh in sl.shapes:
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    for c in row.cells:
                        for p in c.text_frame.paragraphs:
                            for r in p.runs:
                                yield r
            elif sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        yield r


def voice_sweep(prs, old_name=None, new_name=None):
    """Replace em/en dashes and, optionally, a previous client's name across every run."""
    em = chr(0x2014)
    en = chr(0x2013)

    def fix(t):
        t = t.replace(" " + em + " ", ": ").replace(" " + en + " ", ": ")
        t = t.replace(em, "-").replace(en, "-")
        if old_name and new_name:
            t = t.replace(old_name, new_name)
        return t

    for r in _all_runs(prs):
        r.text = fix(r.text)


def set_notes(slide, what_to_say, insight):
    """Speaker notes in the two-part format every slide needs."""
    slide.notes_slide.notes_text_frame.text = (
        "What to say: " + what_to_say.strip() + "\nInsight for the call: " + insight.strip())


# ---------- (B) adding native slides with chrome ----------
def blank_layout(prs):
    """The layout with the fewest placeholders."""
    best, fewest = None, None
    for lay in prs.slide_layouts:
        n = len(lay.placeholders)
        if fewest is None or n < fewest:
            best, fewest = lay, n
    return best


def add_blank_slide(prs):
    slide = prs.slides.add_slide(blank_layout(prs))
    for ph in list(slide.placeholders):
        ph._element.getparent().remove(ph._element)
    return slide


def _rect(slide, left, top, width, height, fill):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    s.fill.solid()
    s.fill.fore_color.rgb = RGBColor.from_string(fill)
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def _textbox(slide, left, top, width, height, text, size=12, bold=False, color=DARK,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.name = FONT
    r.font.color.rgb = RGBColor.from_string(color)
    return tb


CONTENT_TOP = 1.35  # inches: first free y below the title block


def add_chrome(prs, slide, title, logo_path=None, footer_text="Confidential", kicker=None):
    """Light chrome on a white slide (path B default).

    Optional small uppercase kicker above the title (e.g. the section name), a dark title
    left-aligned at the page margin, a short accent rule under it, an optional logo
    top-right, a thin grey rule above the footer, footer text left and the page number right.
    Content starts at CONTENT_TOP.
    """
    sw, sh = prs.slide_width, prs.slide_height
    m = E(MARGIN)
    if kicker:
        _textbox(slide, m, E(0.3), E(8), E(0.25), kicker.upper(), size=10, bold=True, color=ACCENT)
    _textbox(slide, m, E(0.5), sw - 2 * m - E(2.0), E(0.6), title, size=24, bold=True, color=DARK,
             anchor=MSO_ANCHOR.BOTTOM)
    _rect(slide, m, E(1.15), E(1.2), E(0.05), ACCENT)
    if logo_path:
        # Fit the logo in a 1.6 x 0.5 in box at the top-right margin.
        from PIL import Image
        iw, ih = Image.open(logo_path).size
        width_in = min(1.6, 0.5 * iw / float(ih))
        slide.shapes.add_picture(logo_path, sw - m - E(width_in), E(0.4), width=E(width_in))
    _rect(slide, m, sh - E(0.5), sw - 2 * m, E(0.01), RULE)
    _textbox(slide, m, sh - E(0.45), E(6), E(0.3), footer_text, size=8, color=MUTED)
    _textbox(slide, sw - m - E(0.6), sh - E(0.45), E(0.6), E(0.3), "0", size=8, color=MUTED,
             align=PP_ALIGN.RIGHT)  # placeholder digit: renumber_footers() fixes it


def add_takeaway(prs, slide, body, label="Takeaway"):
    """Light tinted box with a left accent border near the bottom: bold label line + body line."""
    sw, sh = prs.slide_width, prs.slide_height
    m = E(MARGIN)
    top, height = sh - E(1.45), E(0.8)
    _rect(slide, m, top, E(0.08), height, ACCENT)
    box = _rect(slide, m + E(0.08), top, sw - 2 * m - E(0.08), height, TINT)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = E(0.2)
    first = tf.paragraphs[0]
    lab = first.add_run()
    lab.text = label
    lab.font.size = Pt(10)
    lab.font.bold = True
    lab.font.name = FONT
    lab.font.color.rgb = RGBColor.from_string(ACCENT)
    second = tf.add_paragraph()
    b = second.add_run()
    b.text = body
    b.font.size = Pt(13)
    b.font.name = FONT
    b.font.color.rgb = RGBColor.from_string(DARK)


def add_table(slide, rows, left, top, width, height, verdict_col=None, verdict_colors=None):
    """Native table: tinted header row with dark bold text, alternating body rows, optional coloured verdict column.

    rows: list of lists of strings, first row = header.
    verdict_colors: dict mapping a verdict string (e.g. "Yes", "No", "Partial") to a hex colour.
    """
    nrows, ncols = len(rows), len(rows[0])
    table = slide.shapes.add_table(nrows, ncols, left, top, width, height).table
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.cell(ri, ci)
            cell.fill.solid()
            if ri == 0:
                cell.fill.fore_color.rgb = RGBColor.from_string(TINT)
                color, bold = DARK, True
            else:
                cell.fill.fore_color.rgb = RGBColor.from_string(WHITE if ri % 2 else ALTROW)
                color, bold = (DARK if ci == 0 else MUTED), False
                if verdict_col is not None and ci == verdict_col and verdict_colors:
                    color, bold = verdict_colors.get(val, MUTED), True
            p = cell.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = str(val)
            r.font.size = Pt(10.5)
            r.font.name = FONT
            _style(r, color, bold)
    return table


def reorder_after_add(prs, before_ids, at_index):
    """Move slides added after the `before_ids` snapshot so they start at 0-based at_index.

    Idiom:
        before = list(prs.slides._sldIdLst)
        ... add_blank_slide(prs) x N ...
        reorder_after_add(prs, before, 8)   # the new slides become slides 9, 10, ...
        renumber_footers(prs)
    """
    xml = prs.slides._sldIdLst
    new_ids = [e for e in list(xml) if e not in before_ids]  # in add order
    for e in new_ids:
        xml.remove(e)
    for off, e in enumerate(new_ids):
        xml.insert(at_index + off, e)
