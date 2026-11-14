#!/usr/bin/env python3
"""PRE-SHIP GATE: duplicate and stale-content audit for a .pptx deck. Python 3 standard library only.

    python3 dedupe_audit.py deck.pptx [--overlap 0.45]

Exits 1 on any finding so it can gate a build, 2 if the file cannot be read.

Why: the failure mode is ADDITIVE EDITING. A later pass adds slides and never reconciles them against
what is already in the deck. Each new slide looks fine on its own; the duplication only shows when
someone reads the whole thing. It bites hardest when cutting a long deck down to the condensed version.

It also catches STALE STATUS TEXT ("early data", "access requested", TBC, TODO) left in after the real
data landed. Same class of bug: the engagement moved on, the deck did not.

Checks:
  1. repeated substantive strings (over 25 characters) across slides
  2. near-duplicate slides: distinctive-token overlap above --overlap (default 0.45)
  3. stale status text
See reference/gotchas.md #10 for how to resolve each kind.
"""
import argparse
import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"

STALE = [r"access request(ed)?", r"access required", r"awaiting access", r"pending access",
         r"once .{0,30}access is granted", r"\bTODO\b", r"\bTBC\b", r"\bTBD\b",
         r"early data", r"placeholder", r"lorem"]

STOP = set("""the and for that with this from into your their are was were will would should could
have has had not but its you our they them there here which when what how why who all any each per via
than then also more most other such can may might must because been being does did done only just over
under about""".split())


def slide_parts(zf):
    rels_xml = ET.fromstring(zf.read("ppt/_rels/presentation.xml.rels"))
    targets = {r.get("Id"): posixpath.normpath(posixpath.join("ppt", r.get("Target", "")))
               for r in rels_xml.findall("{%s}Relationship" % REL)}
    pres = ET.fromstring(zf.read("ppt/presentation.xml"))
    ids = pres.find("{%s}sldIdLst" % P)
    return [] if ids is None else [targets[s.get("{%s}id" % R)] for s in ids.findall("{%s}sldId" % P)]


def para_text(el):
    lines = []
    for p in el.iter("{%s}p" % A):
        lines.append("".join(t.text or "" for t in p.iter("{%s}t" % A)))
    return "\n".join(lines).strip()


def shapes(root):
    """Yield ('text', str) for each text shape and ('cell', str) for each table cell."""
    for sp in root.iter("{%s}sp" % P):
        body = sp.find("{%s}txBody" % P)
        if body is not None:
            yield "text", para_text(body)
    for tc in root.iter("{%s}tc" % A):
        yield "cell", para_text(tc)


def title_of(items):
    for kind, t in items:
        if kind == "text" and t:
            return t.split("\n")[0]
    return "(untitled)"


def blocks(items):
    out = []
    for kind, t in items:
        if (kind == "cell" and len(t) > 12) or (kind == "text" and len(t) > 40):
            out.append(t.lower())
    return out


def sig(blks):
    toks = re.sub(r"[^a-z0-9 ]", " ", " ".join(blks)).split()
    return {t for t in toks if len(t) > 5 and t not in STOP}


def main():
    ap = argparse.ArgumentParser(description="Duplicate and stale-content audit for a deck.")
    ap.add_argument("deck")
    ap.add_argument("--overlap", type=float, default=0.45)
    args = ap.parse_args()
    try:
        zf = zipfile.ZipFile(args.deck)
        parts = slide_parts(zf)
        slides = []
        for i, part in enumerate(parts, 1):
            items = list(shapes(ET.fromstring(zf.read(part))))
            slides.append((i, title_of(items), blocks(items), items))
    except (OSError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        print("cannot read %s: %s" % (args.deck, exc))
        sys.exit(2)

    problems = 0

    print("1. REPEATED SUBSTANTIVE STRINGS ACROSS SLIDES")
    hit = 0
    for a in range(len(slides)):
        for b in range(a + 1, len(slides)):
            ia, ta, ca, _ = slides[a]
            ib, tb, cb, _ = slides[b]
            shared = {x for x in (set(ca) & set(cb)) if len(x) > 25}
            if shared:
                hit += 1
                print("   s%d '%s'  <->  s%d '%s'" % (ia, ta[:38], ib, tb[:38]))
                for x in sorted(shared)[:2]:
                    print("       repeated: %s" % x[:84])
    problems += hit
    if not hit:
        print("   none")

    print("\n2. NEAR-DUPLICATE SLIDES (same purpose, different words)")
    hit = 0
    for a in range(len(slides)):
        for b in range(a + 1, len(slides)):
            ia, ta, ca, _ = slides[a]
            ib, tb, cb, _ = slides[b]
            sa, sb = sig(ca), sig(cb)
            if len(sa) < 15 or len(sb) < 15:
                continue
            ov = len(sa & sb) / min(len(sa), len(sb))
            if ov > args.overlap:
                hit += 1
                print("   %4.0f%%  s%d '%s'  <->  s%d '%s'" % (ov * 100, ia, ta[:36], ib, tb[:36]))
    problems += hit
    if not hit:
        print("   none above %d%%" % round(args.overlap * 100))

    print("\n3. STALE STATUS TEXT (state changed, deck did not)")
    hit = 0
    for i, title, _, items in slides:
        for _, t in items:
            if any(re.search(p, t, re.I) for p in STALE):
                hit += 1
                print("   s%d '%s': %s" % (i, title[:32], t.strip()[:64]))
                break
    problems += hit
    if not hit:
        print("   none")

    print("\nRESULT: %d issue(s) - reconcile before shipping." % problems if problems else "\nRESULT: clean.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
