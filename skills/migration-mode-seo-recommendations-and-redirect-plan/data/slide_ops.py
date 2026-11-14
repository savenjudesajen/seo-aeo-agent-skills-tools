"""Safe slide duplication and insertion for template decks.

Three traps this file guards against:
  - Removing a slide id from the slide list leaves ORPHAN slide parts, which causes duplicate
    relationships and ghost slides. Never drop-and-re-add to get idempotency; rebuild
    deterministically from the template instead.
  - A cloned slide's header bar can have an EMPTY text frame. A naive "strip shapes that have no
    text" removes it, leaving light title text on a light background. Identify it by FILL +
    GEOMETRY, never by "has text".
  - Inserting a slide shifts later indices: duplicate ALL slides first, then move them.

Builder script: needs python-pptx.
"""
import copy
import io

from pptx.util import Inches

PICTURE = 13  # MSO_SHAPE_TYPE.PICTURE


def duplicate_slide(prs, index):
    """Clone a slide. Pictures are re-added from their blob because a deep copy of a picture
    element breaks its relationship id."""
    src = prs.slides[index]
    dst = prs.slides.add_slide(src.slide_layout)
    for shp in list(dst.shapes):          # strip the layout's placeholders
        shp._element.getparent().remove(shp._element)
    for shp in src.shapes:
        if shp.shape_type == PICTURE:
            dst.shapes.add_picture(io.BytesIO(shp.image.blob), shp.left, shp.top, shp.width, shp.height)
        else:
            dst.shapes._spTree.append(copy.deepcopy(shp._element))
    return dst


def move_slide(prs, from_idx, to_idx):
    lst = prs.slides._sldIdLst
    items = list(lst)
    lst.remove(items[from_idx])
    lst.insert(to_idx, items[from_idx])


def title_of(slide):
    for sh in slide.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip():
            return sh.text_frame.text.strip().split("\n")[0]
    return ""


def find_slide(prs, substring):
    """Anchor by TITLE TEXT, not index: robust to shifts between runs."""
    for i, s in enumerate(prs.slides):
        if substring.lower() in title_of(s).lower():
            return i
    return None


def is_header_bar(shp, fill_hex, max_top=Inches(0.75), min_width=Inches(10)):
    """The full-width bar behind a slide title. It often has an EMPTY text frame, so identify it by
    solid fill colour + position + width. Read fill_hex (e.g. "1F2937") from dump_pptx.py output
    or the template's theme; tune max_top / min_width to the template's geometry."""
    if shp.top is None or shp.width is None:
        return False
    if shp.top >= max_top or shp.width <= min_width:
        return False
    try:
        return shp.fill.type == 1 and str(shp.fill.fore_color.rgb).upper() == fill_hex.upper()
    except Exception:
        return False


def strip_body(slide, keep_texts=(), keep_prefixes=(), header_fill_hex=None):
    """Remove body shapes from a cloned slide, keeping pictures (logos), the header bar, page
    numbers and any shape whose text is in keep_texts or starts with one of keep_prefixes
    (titles, eyebrows, footers: read them from dump_pptx.py)."""
    for shp in list(slide.shapes):
        if shp.shape_type == PICTURE:
            continue
        if header_fill_hex and is_header_bar(shp, header_fill_hex):
            continue
        if getattr(shp, "has_table", False) and shp.has_table:
            shp._element.getparent().remove(shp._element)
            continue
        t = shp.text_frame.text.strip() if shp.has_text_frame else ""
        if t in keep_texts or t.isdigit() or any(t.startswith(p) for p in keep_prefixes):
            continue
        if shp.has_text_frame:
            shp._element.getparent().remove(shp._element)


def fix_invisible_cells(prs):
    """Some template cells are EMPTY and their run carries NO formatting (size and colour unset).
    Text written into them falls back to the default size and colour, which can be invisible on a
    dark header row. Clone the run properties of a formatted donor run in the same row.
    Returns the number of runs fixed."""
    fixed = 0
    for slide in prs.slides:
        for sh in slide.shapes:
            if not (getattr(sh, "has_table", False) and sh.has_table):
                continue
            t = sh.table
            for r in range(len(t.rows)):
                donor = None
                for c in range(len(t.columns)):
                    for run in t.cell(r, c).text_frame.paragraphs[0].runs:
                        if run.font.size is not None:
                            donor = run
                            break
                    if donor:
                        break
                if donor is None:
                    continue
                src_rpr = donor._r.get_or_add_rPr()
                for c in range(len(t.columns)):
                    for run in t.cell(r, c).text_frame.paragraphs[0].runs:
                        if run.font.size is None and run.text.strip():
                            dst = run._r
                            old = dst.find(src_rpr.tag)
                            if old is not None:
                                dst.remove(old)
                            dst.insert(0, copy.deepcopy(src_rpr))
                            fixed += 1
    return fixed
