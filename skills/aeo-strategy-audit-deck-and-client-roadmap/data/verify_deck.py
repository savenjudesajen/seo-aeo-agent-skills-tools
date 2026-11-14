#!/usr/bin/env python3
"""GATE for an AEO audit deck (.pptx). Measured, not claimed. Python 3 standard library only.

Usage:
    python3 verify_deck.py deck.pptx [--max-slides 15] [--long] [--font "Font Name"]
                                     [--ban "ToolName" --ban "OtherTool" ...]

Exit 0 = PASS, 1 = FAIL, 2 = bad usage or unreadable file.

Checks:
  1. slide count <= --max-slides (default 15, the condensed-deck cap); skipped with --long
  2. no placeholder text anywhere (slides, tables, presenter notes)
  3. no incomplete-status wording anywhere ("not checked", "partial baseline", ...): finish the work
     or raise the gap in chat instead
  4. no em dashes in slide text
  5. no --ban terms (e.g. the internal tool names you used) in slide body text; notes may name sources
  6. with --font: every explicitly set Latin font is that font (theme font references are ignored)
"""
import argparse
import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
PLACEHOLDERS = [r"lorem", r"ipsum", r"\btodo\b", r"\[insert", r"placeholder", r"xxxx", r"\btbd\b", r"\btbc\b"]
INCOMPLETE = [r"not checked", r"not tested", r"not run\b", r"not asked", r"partial baseline",
              r"needs search console", r"not available", r"not assessed", r"this pass", r"\bpending\b",
              r"scoped into", r"requires .{0,30}pull"]
EM_DASH = "—"


def rels_of(zf, part):
    """Return ({rel id: target part path}, {rel id: rel type}) for a part inside the package."""
    folder, name = posixpath.split(part)
    rels_path = posixpath.join(folder, "_rels", name + ".rels")
    targets, types = {}, {}
    if rels_path not in zf.namelist():
        return targets, types
    for rel in ET.fromstring(zf.read(rels_path)).findall("rel:Relationship", NS):
        if rel.get("TargetMode") == "External":
            continue
        targets[rel.get("Id")] = posixpath.normpath(posixpath.join(folder, rel.get("Target", "")))
        types[rel.get("Id")] = rel.get("Type", "")
    return targets, types


def slide_parts(zf):
    pres = "ppt/presentation.xml"
    rels, _ = rels_of(zf, pres)
    root = ET.fromstring(zf.read(pres))
    ids = root.find("p:sldIdLst", NS)
    if ids is None:
        return []
    return [rels[s.get("{%s}id" % NS["r"])] for s in ids.findall("p:sldId", NS)]


def notes_part(zf, slide):
    rels, types = rels_of(zf, slide)
    for rid, target in rels.items():
        if types.get(rid, "").endswith("/notesSlide"):
            return target
    return None


def texts(root):
    """Every paragraph's text in a part."""
    out = []
    for p in root.iter("{%s}p" % NS["a"]):
        t = "".join(x.text or "" for x in p.iter("{%s}t" % NS["a"]))
        if t.strip():
            out.append(t)
    return out


def fonts(root):
    seen = {}
    for tag in ("rPr", "defRPr", "endParaRPr"):
        for rpr in root.iter("{%s}%s" % (NS["a"], tag)):
            latin = rpr.find("a:latin", NS)
            if latin is not None:
                face = latin.get("typeface", "")
                if face and not face.startswith("+"):
                    seen[face] = seen.get(face, 0) + 1
    return seen


def main():
    ap = argparse.ArgumentParser(description="Gate an AEO audit deck.")
    ap.add_argument("deck")
    ap.add_argument("--max-slides", type=int, default=15)
    ap.add_argument("--long", action="store_true", help="long-form deck: skip the slide-count cap")
    ap.add_argument("--font", help="expected font for every explicitly set run")
    ap.add_argument("--ban", action="append", default=[], help="term banned from slide body text")
    args = ap.parse_args()

    try:
        zf = zipfile.ZipFile(args.deck)
        slides = slide_parts(zf)
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        print("cannot read %s: %s" % (args.deck, exc))
        sys.exit(2)

    fails, font_counts = [], {}
    if not args.long and len(slides) > args.max_slides:
        fails.append("SLIDE COUNT: %d > %d" % (len(slides), args.max_slides))

    for i, part in enumerate(slides, 1):
        root = ET.fromstring(zf.read(part))
        body = texts(root)
        notes = []
        npart = notes_part(zf, part)
        if npart and npart in zf.namelist():
            notes = texts(ET.fromstring(zf.read(npart)))
        for face, n in fonts(root).items():
            font_counts[face] = font_counts.get(face, 0) + n

        for where, lines in (("slide", body), ("notes", notes)):
            for t in lines:
                low = t.lower()
                for pat in PLACEHOLDERS:
                    if re.search(pat, low):
                        fails.append("PLACEHOLDER on slide %d (%s): %r" % (i, where, t[:70]))
                for pat in INCOMPLETE:
                    if re.search(pat, low):
                        fails.append("INCOMPLETE-STATUS on slide %d (%s): %r" % (i, where, t[:70]))
        for t in body:
            if EM_DASH in t:
                fails.append("EM DASH on slide %d: %r" % (i, t[:70]))
            for term in args.ban:
                if term.lower() in t.lower():
                    fails.append("BANNED TERM %r in slide %d body: %r" % (term, i, t[:70]))

    if args.font:
        others = {f: n for f, n in font_counts.items() if f != args.font}
        if others:
            fails.append("FONT: runs set to %s (expected only %s)" % (others, args.font))

    print("slides=%d explicit_fonts=%s" % (len(slides), font_counts))
    if fails:
        print("FAIL")
        for f in fails:
            print("  - %s" % f)
        sys.exit(1)
    print("PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
