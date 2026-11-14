"""In-place editing helpers for a template deck.

Rule: don't rebuild the design. Open the template (the client's own if they have one) and replace
text and table content only, preserving every shape, colour, font and layout. Mechanics and
placeholder rationale go in SPEAKER NOTES, never on the slide.

Usage in a build script:
    from tpl_edit import load, edit, note, set_text, set_table
    prs = load("Template.pptx")
    ...
    prs.save("Deliverable.pptx")

Builder script: needs python-pptx.
"""
from copy import deepcopy

from pptx import Presentation
from pptx.text.text import _Paragraph


def _first_run(paragraph):
    runs = list(paragraph.runs)
    if not runs:
        paragraph.add_run()
        runs = list(paragraph.runs)
    return runs


def _put(paragraph, text):
    """Write text into the first run and drop the others, keeping the first run's formatting."""
    runs = _first_run(paragraph)
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def set_text(shape, new):
    """Replace a shape's text, PRESERVING run and paragraph formatting from the template.

    Same line count: each paragraph keeps its own format and gets its line in place.
    Different line count: paragraph 1's XML is cloned so every new line inherits its format.
    """
    tf = shape.text_frame
    lines = new.split("\n") if isinstance(new, str) else list(new)
    paras = list(tf.paragraphs)

    if len(lines) == len(paras):
        for p, ln in zip(paras, lines):
            _put(p, ln)
        return

    p0 = paras[0]
    _put(p0, lines[0])
    for p in paras[1:]:
        p._p.getparent().remove(p._p)
    for ln in lines[1:]:
        newp = deepcopy(p0._p)
        p0._p.getparent().append(newp)
        para = _Paragraph(newp, tf)
        if list(para.runs):
            _put(para, ln)


def set_cell(cell, val):
    tf = cell.text_frame
    _put(tf.paragraphs[0], str(val))
    for extra in list(tf.paragraphs)[1:]:
        extra._p.getparent().remove(extra._p)


def set_table(shape, rows):
    """Fill a template table.

    Template tables have a FIXED row count: rows beyond it are dropped, so this warns. Unused
    template rows are blanked, not deleted. Watch for an unused trailing column too: a 4-column
    table holding 3 columns of data reads as a mistake.
    """
    tbl = shape.table
    nr, nc = len(tbl.rows), len(tbl.columns)
    if len(rows) > nr:
        print(f"WARNING: {len(rows)} rows supplied but the table holds {nr}; "
              f"{len(rows) - nr} will be dropped")
    widest = max((len(r) for r in rows), default=0)
    if 0 < widest < nc:
        print(f"WARNING: data has {widest} columns but the table has {nc}; the last column will be empty")
    for r in range(nr):
        for c in range(nc):
            val = rows[r][c] if r < len(rows) and c < len(rows[r]) else ""
            set_cell(tbl.cell(r, c), val)


def note(slide, text):
    """Presenter note: mechanics, placeholder rationale, internal context.
    Everything that is not client-facing goes here."""
    slide.notes_slide.notes_text_frame.text = text


def edit(slide, mapping):
    """mapping: {shape_index: new_text_or_table_rows}. Indices come from dump_pptx.py."""
    shapes = list(slide.shapes)
    for idx, val in mapping.items():
        sh = shapes[idx]
        if getattr(sh, "has_table", False) and sh.has_table:
            set_table(sh, val)
        else:
            set_text(sh, val)


def load(template_path):
    """Open a COPY of the template; always save to a different output path."""
    return Presentation(template_path)
