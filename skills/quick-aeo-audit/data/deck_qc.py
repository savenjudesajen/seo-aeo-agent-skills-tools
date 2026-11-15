# -*- coding: utf-8 -*-
"""
Quick AEO Audit deck gate. Python standard library only; runs offline; pure ASCII source.

Usage:
    python deck_qc.py deck.pptx [--stale "Old Client"]... [--tool "Name"]... [--allow-tool "Name"]...

Checks (each finding is an issue; exit 1 if any, exit 0 when clean):
  1. repeated substantive strings across slides (same >25-char block on two slides)
  2. near-duplicate slides (>45% overlap of distinctive words)
     Checks 1 and 2 skip slide chrome: footer, date and slide-number placeholders, and any
     ungrouped text shape whose top edge is in the footer band (the bottom 1/15 of the slide:
     at or below the footer rule add_chrome draws). Chrome repeats on every slide by design.
     Every other check still reads it.
     Chart text (categories, series names, titles of native charts) is read by checks 3-8;
     brand names repeat across charts by design, so checks 1 and 2 skip it.
  3. stale status or placeholder text (TODO, TBD, lorem, "awaiting access", ...)
  4. em or en dashes in slide text or speaker notes
  5. stock AI vocabulary in slide text or speaker notes
  6. "not just X but Y" cadence in slide text
  7. tool or vendor names in slide text (AI engine names are allowed). When the brands the
     audit tracks are themselves tool vendors (an AEO or SEO tools category), pass each
     tracked brand with --allow-tool: they are the data on the slides, not tool credits.
     An allowed name also allows a listed tool name it contains ("Peec AI" allows "Peec").
  8. stale client names passed with --stale (slides and notes)
  9. slides without speaker notes
 10. hardcoded page numbers that do not match the slide position
"""
import argparse
import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

STALE = [r"access request(ed)?", r"access required", r"awaiting access", r"pending access",
         r"once .{0,30}access is granted", r"\bTODO\b", r"\bTBC\b", r"\bTBD\b", r"\bXX+\b",
         r"early data", r"placeholder", r"lorem", r"insert .{0,20} here"]
STOCK_VOCAB = ["leverage", "leveraging", "robust", "seamless", "seamlessly", "unlock", "unlocks",
               "elevate", "elevates", "delve", "game-changer", "game changer", "cutting-edge",
               "best-in-class", "world-class", "supercharge", "revolutionize", "synergy",
               "holistic", "empower", "empowers", "in today's digital landscape", "tapestry"]
NOT_BUT = re.compile(r"\bnot (?:just|only|merely|simply)\b[^.!?]{0,80}\bbut\b", re.I)
DEFAULT_TOOLS = ["Semrush", "Ahrefs", "Moz", "Majestic", "Similarweb", "SpyFu", "DataForSEO",
                 "Keywords Everywhere", "Firecrawl", "Screaming Frog", "Profound", "Peec",
                 "Otterly", "python-pptx", "matplotlib", "LibreOffice",
                 "Claude in Chrome", "openpyxl"]
DASHES = (chr(0x2014), chr(0x2013))  # em dash, en dash (kept out of the source: pure ASCII)
STOP = set("the and for that with this from into your their are was were will would should could "
           "have has had not but its you our we us they them there here which when what how why who "
           "all any each per via than then also more most other such can may might must because been "
           "being does did done only just over under about".split())


def _local(name):
    """Local part of a namespaced tag or attribute name ('{uri}sp' -> 'sp')."""
    return name.rsplit("}", 1)[-1]


def _read_xml(z, name):
    return ET.fromstring(z.read(name))


def _children(el, local):
    return [c for c in el if _local(c.tag) == local]


def _descendants(el, local):
    return [c for c in el.iter() if _local(c.tag) == local]


def _rel_id(el):
    """The relationship-namespace 'id' attribute (r:id), not the plain numeric 'id'."""
    for k, v in el.attrib.items():
        if k.startswith("{") and _local(k) == "id":
            return v
    return None


def _rels(z, part):
    """{rId: (type, absolute part name)} for one part."""
    d, base = posixpath.split(part)
    rels_name = posixpath.join(d, "_rels", base + ".rels")
    out = {}
    if rels_name not in z.namelist():
        return out
    for rel in _descendants(_read_xml(z, rels_name), "Relationship"):
        target = rel.get("Target", "")
        if rel.get("TargetMode") == "External":
            continue
        full = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join(d, target))
        out[rel.get("Id")] = (rel.get("Type", ""), full)
    return out


def _para_text(p_el):
    return "".join(t.text or "" for t in _descendants(p_el, "t"))


def _body_text(tx_body):
    return "\n".join(_para_text(p) for p in _children(tx_body, "p"))


def _tx_body(el):
    found = _children(el, "txBody")
    return found[0] if found else None


CHROME_PLACEHOLDERS = {"ftr", "dt", "sldNum"}  # footer, date, slide number
# The footer band is the bottom 1/15 of the slide (0.5 in of a 7.5 in slide): where deck_helpers.add_chrome
# draws the footer rule, footer text and page number. Kept as a ratio of integers so the rule's own top edge
# (exactly 14/15 of the height) counts, with no float rounding.
FOOTER_BAND_NUM, FOOTER_BAND_DEN = 1, 15


def _shape_top(sp):
    """The shape's own top offset (spPr/xfrm/off@y) in EMU, or None when it inherits its position."""
    for sp_pr in _children(sp, "spPr"):
        for xfrm in _children(sp_pr, "xfrm"):
            for off in _children(xfrm, "off"):
                try:
                    return int(off.get("y"))
                except (TypeError, ValueError):
                    return None
    return None


def _is_chrome(sp, slide_height, grouped):
    """Footer, date or slide-number placeholder, or an ungrouped text shape whose top is in the footer band.

    A shape inside a group has its offset in the group's own coordinates, not the slide's, so only the
    placeholder rule applies to it.
    """
    for nv in _children(sp, "nvSpPr"):
        for ph in _descendants(nv, "ph"):
            if ph.get("type") in CHROME_PLACEHOLDERS:
                return True
    if grouped or not slide_height:
        return False
    top = _shape_top(sp)
    return top is not None and top * FOOTER_BAND_DEN >= slide_height * (FOOTER_BAND_DEN - FOOTER_BAND_NUM)


def _shapes(root, slide_height=None):
    """Yield (kind, text, is_slide_number_field) for text shapes and table cells.

    kind: "chrome" for footer-band text and footer/date/slide-number placeholders (see _is_chrome),
    "shape" for every other text shape, "cell" for table cells.
    """
    def walk(el, grouped):
        tag = _local(el.tag)
        if tag == "sp":
            body = _tx_body(el)
            if body is not None:
                is_field = any(f.get("type") == "slidenum" for f in _descendants(body, "fld"))
                kind = "chrome" if _is_chrome(el, slide_height, grouped) else "shape"
                yield kind, _body_text(body), is_field
            return
        if tag == "tbl":
            for tc in _descendants(el, "tc"):
                body = _tx_body(tc)
                if body is not None:
                    yield "cell", _body_text(body), False
            return
        for child in el:
            for item in walk(child, grouped or tag == "grpSp"):
                yield item

    for item in walk(root, False):
        yield item


def _chart_text(root):
    """The text a native chart shows: string category and series names, titles, axis titles."""
    parts = []
    for cache in _descendants(root, "strCache"):
        parts += [v.text or "" for v in _descendants(cache, "v")]
    parts += [t.text or "" for t in _descendants(root, "t")]  # rich text: chart and axis titles
    return "\n".join(p for p in parts if p.strip())


def _notes_text(root):
    parts = []
    for sp in _descendants(root, "sp"):
        ph = _descendants(sp, "ph")
        if not ph or ph[0].get("type") != "body":
            continue
        body = _tx_body(sp)
        if body is not None:
            parts.append(_body_text(body))
    return "\n".join(parts).strip()


def load_deck(path):
    """[{index, title, texts:[(kind, text, is_field)], notes}] in presentation order."""
    with zipfile.ZipFile(path) as z:
        pres = "ppt/presentation.xml"
        pres_rels = _rels(z, pres)
        pres_root = _read_xml(z, pres)
        sizes = _descendants(pres_root, "sldSz")
        slide_height = int(sizes[0].get("cy")) if sizes and sizes[0].get("cy", "").isdigit() else None
        slides = []
        for i, sid in enumerate(_descendants(pres_root, "sldId"), 1):
            _, part = pres_rels[_rel_id(sid)]
            root = _read_xml(z, part)
            texts = list(_shapes(root, slide_height))
            notes = ""
            for typ, target in sorted(_rels(z, part).values(), key=lambda r: r[1]):
                if typ.endswith("/notesSlide") and target in z.namelist():
                    notes = _notes_text(_read_xml(z, target))
                elif typ.endswith("/chart") and target in z.namelist():
                    texts.append(("chart", _chart_text(_read_xml(z, target)), False))
            title = next((t.strip().split("\n")[0] for k, t, _ in texts if k == "shape" and t.strip()),
                         "(untitled)")
            slides.append({"index": i, "title": title, "texts": texts, "notes": notes})
        return slides


def blocks(slide):
    """Substantive text blocks for checks 1 and 2: shapes over 40 characters, cells over 12. Not chrome."""
    out = []
    for kind, text, _ in slide["texts"]:
        t = text.strip().lower()
        if (kind == "cell" and len(t) > 12) or (kind == "shape" and len(t) > 40):
            out.append(t)
    return out


def signature(blks):
    toks = re.sub(r"[^a-z0-9 ]", " ", " ".join(blks)).split()
    return {t for t in toks if len(t) > 5 and t not in STOP}


def word_rx(term):
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])", re.I)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--stale", action="append", default=[], help="previous client name to catch (repeatable)")
    ap.add_argument("--tool", action="append", default=[], help="extra tool/vendor name to forbid (repeatable)")
    ap.add_argument("--allow-tool", action="append", default=[],
                    help="tool or vendor name allowed on slides (repeatable): a brand in the tracked set, "
                         "or a tool the client asked to see")
    args = ap.parse_args(argv)

    slides = load_deck(args.deck)
    # An allowed name allows each listed tool name it contains as a word: "Peec AI" allows "Peec".
    allowed = [a for a in args.allow_tool if a.strip()]
    tools = [t for t in DEFAULT_TOOLS + args.tool if not any(word_rx(t).search(a) for a in allowed)]
    tool_rx = [(t, word_rx(t)) for t in tools]
    vocab_rx = [(v, word_rx(v)) for v in STOCK_VOCAB]
    stale_rx = [(s, word_rx(s)) for s in args.stale if s.strip()]
    issues = []

    def add(section, msg):
        issues.append((section, msg))

    blk = [(s, blocks(s)) for s in slides]
    for a in range(len(blk)):
        for b in range(a + 1, len(blk)):
            sa, ca = blk[a]
            sb, cb = blk[b]
            shared = sorted(x for x in set(ca) & set(cb) if len(x) > 25)
            for x in shared[:2]:
                add("1 repeated string", "s%d <-> s%d: %s" % (sa["index"], sb["index"], x[:84]))
            ga, gb = signature(ca), signature(cb)
            if len(ga) >= 15 and len(gb) >= 15:
                ov = len(ga & gb) / float(min(len(ga), len(gb)))
                if ov > 0.45:
                    add("2 near-duplicate", "%3.0f%% s%d '%s' <-> s%d '%s'" % (
                        ov * 100, sa["index"], sa["title"][:36], sb["index"], sb["title"][:36]))

    for s in slides:
        i = s["index"]
        slide_text = "\n".join(t for _, t, _ in s["texts"])
        all_text = slide_text + "\n" + s["notes"]
        for pat in STALE:
            m = re.search(pat, slide_text, re.I)
            if m:
                add("3 stale/placeholder", "s%d: '%s'" % (i, m.group(0)))
        for d in DASHES:
            if d in all_text:
                add("4 dash", "s%d: %s found (%s)" % (i, "em dash" if d == DASHES[0] else "en dash",
                                                    "notes" if d not in slide_text else "slide"))
        for v, rx in vocab_rx:
            if rx.search(all_text):
                add("5 stock vocabulary", "s%d: '%s'" % (i, v))
        m = NOT_BUT.search(slide_text)
        if m:
            add("6 not-X-but-Y", "s%d: '%s'" % (i, m.group(0)[:70]))
        for t, rx in tool_rx:
            if rx.search(slide_text):
                add("7 tool name", "s%d: '%s'" % (i, t))
        for st, rx in stale_rx:
            if rx.search(all_text):
                add("8 stale client name", "s%d: '%s'" % (i, st))
        if not s["notes"]:
            add("9 missing notes", "s%d '%s'" % (i, s["title"][:40]))
        for kind, text, is_field in s["texts"]:
            t = text.strip()
            if kind in ("shape", "chrome") and not is_field and t.isdigit() and len(t) <= 2 and int(t) != i:
                add("10 page number", "s%d shows '%s'" % (i, t))

    if not issues:
        print("RESULT: clean (%d slides)." % len(slides))
        return 0
    current = None
    for section, msg in sorted(issues, key=lambda x: int(x[0].split()[0])):
        if section != current:
            print(section.upper())
            current = section
        print("   " + msg)
    print("\nRESULT: %d issue(s)." % len(issues))
    return 1


if __name__ == "__main__":
    sys.exit(main())
