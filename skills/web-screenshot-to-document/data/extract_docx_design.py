#!/usr/bin/env python3
"""
extract_docx_design.py - read a .docx and print its design tokens, so a figure is
built to the template that exists rather than to a remembered one.

Run this first, every time, on whatever file the deliverable is going into.
Standard library only.

    python3 extract_docx_design.py target.docx            # human-readable report
    python3 extract_docx_design.py target.docx --json     # token file for insert_figure.py --tokens

The JSON contains only the tokens it could measure; anything missing falls back
to insert_figure.py's neutral defaults. Review it before use: the values are
picked by frequency, and one odd table can mislead it.
"""
import json
import re
import sys
import zipfile
from collections import Counter

CAPTION_RE = re.compile(r"^\s*(Table|Figure|Fig\.?|Exhibit|Image)\s*\d+")


def half(v):
    return f"{float(v) / 2:g}pt"


def part(z, name):
    try:
        return z.read(name).decode("utf8")
    except KeyError:
        return ""


def para_text(p_xml):
    return "".join(re.findall(r"<w:t(?:\s[^>]*)?>([^<]*)</w:t>", p_xml))


def first(pattern, text, flags=0):
    m = re.search(pattern, text, flags)
    return m.group(1) if m else None


def text_column(pgsz, pgmar):
    """Text-column width in dxa (page width minus left and right margins), or None."""
    if not pgsz or not pgmar:
        return None
    w = first(r'w:w="([\d.]+)"', pgsz)
    left = first(r'w:(?:left|start)="([-\d.]+)"', pgmar)
    right = first(r'w:(?:right|end)="([-\d.]+)"', pgmar)
    if not (w and left and right):
        return None
    return int(float(w) - float(left) - float(right))


def table_props(tbl):
    """Read the table-level properties of one <w:tbl> (ignores nested tables' rows)."""
    tblpr = first(r"<w:tblPr>(.*?)</w:tblPr>", tbl, re.S) or ""
    width = first(r'<w:tblW w:w="([\d.]+)"', tblpr)
    indent = first(r'<w:tblInd w:w="([-\d.]+)"', tblpr) or "0"
    layout = first(r'<w:tblLayout w:type="(\w+)"', tblpr) or "auto"
    mar = first(r"<w:tblCellMar>(.*?)</w:tblCellMar>", tblpr, re.S)
    if mar is None:
        mar = first(r"<w:tcMar>(.*?)</w:tcMar>", tbl, re.S) or ""
    cell = first(r'<w:(?:left|start)\b[^>]*w:w="([\d.]+)"', mar)
    borders = first(r"<w:tblBorders>(.*?)</w:tblBorders>", tblpr, re.S)
    if borders is None:
        borders = first(r"<w:tcBorders>(.*?)</w:tcBorders>", tbl, re.S) or ""
    bsz = first(r'<w:(?:top|left|start)\b[^>]*w:sz="([\d.]+)"', borders)
    bcol = first(r'<w:(?:top|left|start)\b[^>]*w:color="([0-9A-Fa-f]{6}|auto)"', borders)
    return width, indent, layout, cell, bsz, bcol


def caption_runs(doc):
    """Return (text, props) for paragraphs that look like Table/Figure captions."""
    out = []
    for p in re.findall(r"<w:p\b.*?</w:p>", doc, re.S):
        text = para_text(p).strip()
        if not CAPTION_RE.match(text):
            continue
        r = first(r"<w:r\b[^>]*>(.*?)</w:r>", p, re.S) or ""
        props = {
            "style": first(r'<w:pStyle w:val="([^"]+)"', p),
            "font": first(r'<w:rFonts[^>]*w:ascii="([^"]+)"', r),
            "size": first(r'<w:sz w:val="([\d.]+)"', r),
            "color": first(r'<w:color w:val="([0-9A-Fa-f]{6})"', r),
            "bold": bool(re.search(r'<w:b(?:\s+w:val="(?:1|true)")?\s*/>', r)),
        }
        out.append((text[:80], props))
    return out


def measure(path):
    z = zipfile.ZipFile(path)
    doc, sty = part(z, "word/document.xml"), part(z, "word/styles.xml")
    report = {"path": path}

    report["page_size"] = first(r"(<w:pgSz[^/]*/>)", doc)
    report["page_margins"] = first(r"(<w:pgMar[^/]*/>)", doc)
    report["text_column"] = text_column(report["page_size"], report["page_margins"])

    d = first(r"<w:rPrDefault>(.*?)</w:rPrDefault>", sty, re.S) or ""
    report["default_font"] = first(r'w:ascii="([^"]+)"', d)
    report["default_size"] = first(r'<w:sz w:val="([\d.]+)"', d)

    heads = []
    for sid, body in re.findall(
        r'<w:style [^>]*w:styleId="(Heading\d|Title|Subtitle|Caption)"[^>]*>(.*?)</w:style>', sty, re.S
    ):
        heads.append({
            "style": sid,
            "font": first(r'<w:rFonts[^>]*w:ascii="([^"]+)"', body),
            "size": first(r'<w:sz w:val="([\d.]+)"', body),
            "color": first(r'<w:color w:val="([0-9A-Fa-f]{6})"', body),
            "bold": bool(re.search(r'<w:b(?:\s+w:val="(?:1|true)")?\s*/>', body)),
        })
    report["styles"] = heads

    report["text_colors"] = Counter(re.findall(r'<w:color w:val="([0-9A-Fa-f]{6})"', doc)).most_common(8)
    report["shading"] = Counter(re.findall(r'<w:shd[^>]*w:fill="([0-9A-Fa-f]{6})"', doc)).most_common(8)

    grids = Counter()
    borders = Counter()
    for tbl in re.findall(r"<w:tbl>.*?</w:tbl>", doc, re.S):
        w, ind, lay, cm, bsz, bcol = table_props(tbl)
        grids[(w or "?", ind, lay, cm or "?")] += 1
        if bsz or bcol:
            borders[(bsz or "?", bcol or "?")] += 1
    report["table_grids"] = grids.most_common()
    report["table_borders"] = borders.most_common()

    report["captions"] = caption_runs(doc)
    report["fonts_embedded"] = sorted(
        {n.split("/")[-1].split("-")[0] for n in z.namelist() if n.startswith("word/fonts/")}
    )
    report["drawings"] = doc.count("<w:drawing>")
    return report


def tokens_from(report):
    """Turn a measurement into the token keys insert_figure.py understands."""
    t = {}
    if report["table_grids"]:
        (w, ind, _lay, cm), _n = report["table_grids"][0]
        if w != "?":
            t["grid_width"] = int(float(w))
        t["grid_indent"] = int(float(ind))
        if cm != "?":
            t["cell_margin"] = int(float(cm))
    if "grid_width" not in t and report["text_column"]:
        # no table width to copy: fall back to the text column
        t["grid_width"] = report["text_column"]
    if report["table_borders"]:
        (bsz, bcol), _n = report["table_borders"][0]
        if bsz != "?":
            t["border_size"] = int(float(bsz))
        if bcol not in ("?", "auto"):
            t["border_color"] = bcol.upper()
        elif bcol == "auto":
            t["border_color"] = "000000"
    caps = [c for c in report["captions"]]
    if caps:
        props = Counter(json.dumps(p, sort_keys=True) for _t, p in caps).most_common(1)[0][0]
        p = json.loads(props)
        if p.get("style"):
            t["caption_style"] = p["style"]
        if p.get("font"):
            t["caption_font"] = p["font"]
        if p.get("size"):
            t["caption_size"] = int(float(p["size"]))
        if p.get("color"):
            t["caption_color"] = p["color"].upper()
        t["caption_bold"] = bool(p.get("bold"))
    return t


def print_report(r):
    print(f"# design tokens: {r['path']}\n")
    print("## page")
    for k in ("page_size", "page_margins"):
        if r[k]:
            print("   ", re.sub(r"\s+", " ", r[k]))
    if r["text_column"]:
        print(f"    text column = {r['text_column']} dxa ({r['text_column'] / 1440:.2f}in)")
    size = half(r["default_size"]) if r["default_size"] else "?"
    print(f"\n## default run\n    font={r['default_font'] or '?'}  size={size}")

    print("\n## heading / caption styles")
    for h in r["styles"]:
        s = half(h["size"]) if h["size"] else "-"
        print(f"    {h['style']:10s} font={h['font'] or '-':16s} size={s:7s} "
              f"color=#{h['color'] or '-':7s} {'bold' if h['bold'] else ''}")

    print("\n## palette (by frequency in the body)")
    print("    text colors :", r["text_colors"])
    print("    shading     :", r["shading"], "  (a frequent dark or accent fill may be a section band)")

    print("\n## table grid  (a figure reuses the dominant row)")
    for (w, ind, lay, cm), n in r["table_grids"] or []:
        print(f"    width={w:>8s} indent={ind:>6s} layout={lay:<6s} cellMargin={cm:<6s} x{n}")
    if not r["table_grids"]:
        print("    no tables - the JSON falls back to the text column; or use the client's own template")

    print("\n## table borders  (size in eighths of a point)")
    for (sz, col), n in r["table_borders"] or []:
        print(f"    sz={sz:<4s} color={col:<7s} x{n}")
    if not r["table_borders"]:
        print("    none set on tables - check the table style in styles.xml, or use the default")

    print("\n## caption convention already in the document")
    if r["captions"]:
        for text, p in r["captions"][:8]:
            print(f"    {text!r}  {p}")
    else:
        print("    none - use 'Figure N. <what the reader should notice>'")

    print("\n## fonts embedded")
    print("   ", r["fonts_embedded"] or "none embedded")

    n = r["drawings"]
    print("\n## images already in the body")
    print(f"    <w:drawing> count = {n}",
          "-> no precedent, follow the table grid" if n == 0 else "-> look at how existing images are framed")


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    report = measure(args[0])
    if "--json" in argv:
        print(json.dumps(tokens_from(report), indent=2))
    else:
        print_report(report)


if __name__ == "__main__":
    main(sys.argv[1:])
