#!/usr/bin/env python3
"""
insert_figure.py - place a screenshot into an existing .docx, in place, styled to
that document's own design tokens.

Never rebuilds the document. Opens it, injects a figure block at an anchor, saves
to the same path (or --out). Needs python-docx and Pillow.

Tokens: neutral defaults below, overridden by a token file (--tokens, written by
extract_docx_design.py --json), overridden by individual flags. Never edit the
defaults for a single client; pass that client's tokens instead.
See reference/on-template-figure-design.md.

Usage
  # see what you can anchor to
  python3 insert_figure.py --doc brief.docx --list-anchors

  # one screenshot, after the 2nd paragraph containing "Reference examples"
  python3 insert_figure.py --doc brief.docx --tokens figure-tokens.json \\
      --image shots/returns-policy.png \\
      --caption "Figure 1. The returns policy sits in the first screen of the product page" \\
      --source "example.com/products/kettle, March 2026" \\
      --after "Reference examples" --occurrence 2

  # two-up comparison under a band
  python3 insert_figure.py --doc brief.docx --tokens figure-tokens.json \\
      --image a.png --image b.png \\
      --sub-caption "example.org" --sub-caption "example.net" \\
      --band "Competitor reference" \\
      --caption "Figure 2. Both FAQ pages open with a search box; only one groups questions by topic" \\
      --source "example.org/help and example.net/faq, March 2026" \\
      --after-index 42
"""
import argparse
import json
import os
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Emu, Pt, RGBColor

# ---- neutral default tokens (override with --tokens or flags) ----------------
DEFAULTS = {
    "grid_width": 9360,          # dxa: 6.5in, Letter with 1in margins
    "grid_indent": 0,            # dxa
    "cell_margin": 115,          # dxa, all four sides
    "border_size": 4,            # eighths of a point -> 0.5pt
    "border_color": "BFBFBF",
    "caption_font": None,        # None = inherit the document's font
    "caption_size": 20,          # half-points -> 10pt
    "caption_color": "262626",
    "caption_bold": True,
    "caption_style": None,       # e.g. "Caption"
    "body_font": None,           # source line + sub-captions; None = inherit
    "source_size": 16,           # half-points -> 8pt
    "muted_color": "595959",
    "band_fill": "F2F2F2",
    "band_color": "262626",
    "band_size": 20,             # half-points
    "band_height": 400,          # dxa, atLeast
    "max_image_height_in": 8.0,  # keeps caption + frame + source on one page
}
EMU_IN = 914400
DXA_IN = 1440
GUTTER_IN = 0.12                 # space between images in a two-up
CAPTION_RE = re.compile(r"^\s*figure\s+\d+", re.I)


def load_tokens(args):
    t = dict(DEFAULTS)
    if args.tokens:
        with open(args.tokens, encoding="utf8") as fh:
            extra = json.load(fh)
        unknown = set(extra) - set(DEFAULTS)
        if unknown:
            sys.exit(f"unknown token key(s) in {args.tokens}: {sorted(unknown)}")
        t.update(extra)
    for key in DEFAULTS:
        val = getattr(args, key, None)
        if val is not None:
            t[key] = val
    for key in ("border_color", "caption_color", "muted_color", "band_fill", "band_color"):
        if t[key]:
            t[key] = str(t[key]).lstrip("#").upper()
    return t


def _el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn("w:" + k), str(v))
    return e


def _style_run(run, font, size_hp, color=None, bold=False):
    if size_hp:
        run.font.size = Pt(size_hp / 2)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    if font:
        run.font.name = font
        rpr = run._r.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts")
            rpr.insert(0, rf)
        for a in ("ascii", "hAnsi", "cs", "eastAsia"):
            rf.set(qn("w:" + a), font)


def _space(par, before=0, after=0, line=240):
    ppr = par._p.get_or_add_pPr()
    old = ppr.find(qn("w:spacing"))
    if old is not None:
        ppr.remove(old)
    ppr.append(_el("w:spacing", after=after, before=before, line=line, lineRule="auto"))


def _keep(par):
    ppr = par._p.get_or_add_pPr()
    for tag in ("w:keepNext", "w:keepLines"):
        if ppr.find(qn(tag)) is None:
            ppr.append(_el(tag, val="1"))


def _table_grid(table, ncols, t):
    """Write the document's table geometry and borders onto the new table."""
    tblpr = table._tbl.tblPr
    for tag in ("w:tblStyle", "w:tblW", "w:jc", "w:tblInd", "w:tblBorders",
                "w:tblLayout", "w:tblCellMar", "w:tblLook"):
        old = tblpr.find(qn(tag))
        if old is not None:
            tblpr.remove(old)
    gw = int(t["grid_width"])
    tblpr.append(_el("w:tblW", w=gw, type="dxa"))
    tblpr.append(_el("w:jc", val="left"))
    tblpr.append(_el("w:tblInd", w=int(t["grid_indent"]), type="dxa"))
    b = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b.append(_el("w:" + side, val="single", sz=int(t["border_size"]), space="0",
                     color=t["border_color"]))
    tblpr.append(b)
    tblpr.append(_el("w:tblLayout", type="fixed"))
    grid = table._tbl.find(qn("w:tblGrid"))
    if grid is not None:
        table._tbl.remove(grid)
    grid = OxmlElement("w:tblGrid")
    for w in _col_widths(gw, ncols):
        grid.append(_el("w:gridCol", w=w))
    tblpr.addnext(grid)


def _col_widths(gw, ncols):
    each = gw // ncols
    return [(gw - each * (ncols - 1)) if i == 0 else each for i in range(ncols)]


def _cell_pad(cell, t, width, shade=None, valign="top"):
    """Cell width, shading, margins and vertical alignment, written on the cell itself."""
    tcpr = cell._tc.get_or_add_tcPr()
    for tag in ("w:tcW", "w:shd", "w:tcMar", "w:vAlign"):
        old = tcpr.find(qn(tag))
        if old is not None:
            tcpr.remove(old)
    tcpr.insert(0, _el("w:tcW", w=int(width), type="dxa"))
    if shade:
        tcpr.append(_el("w:shd", val="clear", color="auto", fill=shade))
    m = OxmlElement("w:tcMar")
    for side in ("top", "left", "bottom", "right"):
        m.append(_el("w:" + side, w=int(t["cell_margin"]), type="dxa"))
    tcpr.append(m)
    tcpr.append(_el("w:vAlign", val=valign))


def _fit(path, ncols, t):
    from PIL import Image
    w, h = Image.open(path).size
    frame_in = (int(t["grid_width"]) - 2 * int(t["cell_margin"]) * ncols) / DXA_IN
    out_w = (frame_in - GUTTER_IN * (ncols - 1)) / ncols
    out_h = out_w * h / w
    if out_h > float(t["max_image_height_in"]):
        out_h = float(t["max_image_height_in"])
        out_w = out_h * w / h
    return Emu(int(out_w * EMU_IN)), w


def _para_text(p):
    return "".join(x.text or "" for x in p.iter(qn("w:t")))


def _figure_counts(doc, anchor_p):
    """Count figure captions before and after the anchor, in body order (no anchor = end)."""
    before = after = 0
    seen = False
    for p in doc.element.body.iter(qn("w:p")):
        if CAPTION_RE.match(_para_text(p)):
            if seen:
                after += 1
            else:
                before += 1
        if p is anchor_p:
            seen = True
    return before, after


def _text_column_note(doc, t):
    """Say when the figure's grid differs from the text column, so a wrong token gets noticed."""
    sec = doc.sections[-1]
    if not (sec.page_width and sec.left_margin is not None and sec.right_margin is not None):
        return
    col = int((sec.page_width - sec.left_margin - sec.right_margin) / 635)   # EMU -> dxa
    gw, ind = int(t["grid_width"]), int(t["grid_indent"])
    if abs(gw - col) > 0.02 * col or ind != 0:
        print(f"note: figure grid {gw} dxa (indent {ind}) vs text column {col} dxa; "
              "fine if the document's tables use this grid, otherwise check the tokens")


def _anchor(doc, args):
    body = list(doc.paragraphs)
    if args.after_index is not None:
        if not 0 <= args.after_index < len(body):
            sys.exit(f"--after-index {args.after_index} out of range (0-{len(body) - 1})")
        return body[args.after_index]
    if not args.after:
        sys.exit("give --after TEXT, --after-index N or --at-end")
    hits = [p for p in body if args.after.lower() in p.text.lower()]
    if not hits:
        sys.exit(f"anchor not found: {args.after!r} (run --list-anchors)")
    if len(hits) < args.occurrence:
        sys.exit(f"only {len(hits)} match(es) for {args.after!r}, asked for #{args.occurrence}")
    return hits[args.occurrence - 1]


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doc", required=True)
    ap.add_argument("--out")
    ap.add_argument("--image", action="append", default=[])
    ap.add_argument("--sub-caption", action="append", default=[])
    ap.add_argument("--caption", help='e.g. "Figure 2. What the reader sees first"')
    ap.add_argument("--caption-position", choices=("above", "below"), default="above")
    ap.add_argument("--source", help='e.g. "example.com/pricing, March 2026" ("Source: " is added)')
    ap.add_argument("--band", help="optional header row above the image(s)")
    ap.add_argument("--after", help="anchor paragraph text (substring)")
    ap.add_argument("--after-index", type=int)
    ap.add_argument("--occurrence", type=int, default=1)
    ap.add_argument("--at-end", action="store_true")
    ap.add_argument("--list-anchors", action="store_true")
    ap.add_argument("--tokens", help="JSON token file (extract_docx_design.py --json)")
    for key, val in DEFAULTS.items():
        flag = "--" + key.replace("_", "-")
        if isinstance(val, bool):
            ap.add_argument(flag, dest=key, type=lambda s: s.lower() in ("1", "true", "yes"))
        elif isinstance(val, int):
            ap.add_argument(flag, dest=key, type=int)
        elif isinstance(val, float):
            ap.add_argument(flag, dest=key, type=float)
        else:
            ap.add_argument(flag, dest=key)
    return ap


def main():
    args = build_parser().parse_args()
    doc = Document(args.doc)

    if args.list_anchors:
        for i, p in enumerate(doc.paragraphs):
            if p.text.strip():
                print(f"{i:4d}  [{p.style.name}]  {p.text.strip()[:110]}")
        return

    t = load_tokens(args)
    if not args.image:
        sys.exit("--image is required")
    for p in args.image:
        if not os.path.exists(p):
            sys.exit(f"missing image: {p}")

    anchor = None if args.at_end else _anchor(doc, args)
    before, after = _figure_counts(doc, None if anchor is None else anchor._p)
    number = before + 1
    cap = args.caption or f"Figure {number}."
    if not CAPTION_RE.match(cap):
        cap = f"Figure {number}. {cap}"

    n = len(args.image)
    widths = _col_widths(int(t["grid_width"]), n)
    table = doc.add_table(rows=(2 if args.band else 1), cols=n)
    _table_grid(table, n, t)
    for row in table.rows:
        row._tr.get_or_add_trPr().append(_el("w:cantSplit", val="1"))

    r = 0
    if args.band:
        band = table.rows[0]
        band._tr.get_or_add_trPr().append(_el("w:trHeight", val=int(t["band_height"]), hRule="atLeast"))
        c = band.cells[0] if n == 1 else band.cells[0].merge(band.cells[-1])
        _cell_pad(c, t, int(t["grid_width"]), shade=t["band_fill"], valign="center")
        par = c.paragraphs[0]          # direct formatting only: a heading style here would
        _space(par)                    # put the band text into the table of contents
        _keep(par)
        _style_run(par.add_run(args.band), t["caption_font"], t["band_size"], t["band_color"], bold=True)
        r = 1

    small = []
    for i, img in enumerate(args.image):
        cell = table.rows[r].cells[i]
        _cell_pad(cell, t, widths[i])
        par = cell.paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _space(par)
        width, px = _fit(img, n, t)
        if px < 1000 * (1 if n == 1 else 0.5):
            small.append(f"{img} ({px}px)")
        par.add_run().add_picture(img, width=width)
        if i < len(args.sub_caption):
            sub = cell.add_paragraph()
            sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _space(sub, before=40)
            _style_run(sub.add_run(args.sub_caption[i]), t["body_font"], t["source_size"], t["muted_color"])

    cap_p = doc.add_paragraph()
    if t["caption_style"]:
        try:
            cap_p.style = doc.styles[t["caption_style"]]
        except KeyError:
            print(f"note: style {t['caption_style']!r} not in this document; using direct formatting")
    _style_run(cap_p.add_run(cap), t["caption_font"], t["caption_size"], t["caption_color"],
               bold=bool(t["caption_bold"]))

    src_p = None
    if args.source:
        src = args.source if args.source.lower().startswith("source:") else "Source: " + args.source
        src_p = doc.add_paragraph()
        _style_run(src_p.add_run(src), t["body_font"], t["source_size"], t["muted_color"])

    # order the block and keep it on one page
    cell_pars = [p for row in table.rows for c in row.cells for p in c.paragraphs]
    if args.caption_position == "above":
        _space(cap_p, before=200, after=80)
        _keep(cap_p)
        order = [cap_p._p, table._tbl] + ([src_p._p] if src_p is not None else [])
        if src_p is not None:
            _space(src_p, before=60, after=160)
            for p in cell_pars:
                _keep(p)
    else:
        for p in cell_pars:
            _keep(p)
        _space(cap_p, before=80, after=60 if src_p is not None else 200)
        order = [table._tbl, cap_p._p] + ([src_p._p] if src_p is not None else [])
        if src_p is not None:
            _keep(cap_p)
            _space(src_p, before=0, after=200)

    if anchor is not None:
        prev = anchor._p
        for el in order:
            prev.addnext(el)
            prev = el
    else:
        body = doc.element.body
        sect = body.find(qn("w:sectPr"))
        for el in order:
            if sect is not None:
                sect.addprevious(el)
            else:
                body.append(el)

    _text_column_note(doc, t)
    out = args.out or args.doc
    doc.save(out)
    print(f"placed {cap!r} ({n} image{'s' if n > 1 else ''}) -> {out}")
    if after:
        print(f"warning: {after} figure caption(s) after this one now need renumbering")
    if small:
        print("warning: narrow source image(s), may look soft: " + ", ".join(small))


if __name__ == "__main__":
    main()
