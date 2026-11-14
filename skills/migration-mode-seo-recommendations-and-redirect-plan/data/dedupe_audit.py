"""PRE-SHIP GATE for a .pptx deck. Run before every delivery.

Usage: python3 dedupe_audit.py Deck.pptx [--stale "regex" ...]
  --stale adds a pattern for a blocker that has just cleared (e.g. --stale "page list (is )?pending");
  repeat it for several.
Exits 1 on any finding so it can gate a build. Standard library only; reads the .pptx zip directly,
offline. Slide text only: presenter notes are not checked (they are allowed to discuss status).

Why: the failure mode is ADDITIVE EDITING. A later pass adds slides (competitor, content, AEO) and
never reconciles them with what is already in the deck. Each new slide looks fine on its own; the
duplication only shows when someone reads the whole deck.

It also catches STALE STATUS TEXT, such as "access requested" left on slides after access was granted
and the data already used elsewhere in the same deck: the engagement moved on, the deck did not.

Checks:
  1. repeated substantive strings across slides (table cells > 12 chars, text boxes > 40 chars,
     shared strings > 25 chars)
  2. near-duplicate slides (> 45% overlap of distinctive tokens, both slides with >= 15 tokens)
  3. stale status text (patterns below)
"""
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

STALE_PATTERNS = [
    r"access request(ed)?", r"access required", r"awaiting access", r"pending access",
    r"once .{0,30}access is (granted|available)", r"\bTODO\b", r"\bTBC\b", r"\bTBD\b",
]

STOP = set("""the and for that with this from into your their are was were will would
should could have has had not but its you our we us they them there here which when
what how why who all any each per via than then also more most other such can may
might must because been being does did done only just over under about""".split())

CELL_MIN, BOX_MIN, SHARED_MIN = 12, 40, 25
OVERLAP, MIN_TOKENS = 0.45, 15


def _local(el_or_name):
    """Tag or attribute name without its XML namespace (OOXML parts are matched by local name)."""
    name = el_or_name if isinstance(el_or_name, str) else el_or_name.tag
    return name.rsplit("}", 1)[-1]


def _children(el, name):
    return [c for c in el if _local(c) == name]


def _descendants(el, name):
    return [d for d in el.iter() if _local(d) == name]


def _para_text(p_el):
    return "".join(t.text or "" for t in _descendants(p_el, "t"))


def _shapes(tree_el):
    """Yield ('text', str) and ('table', [cell strings]) for every shape, recursing into groups."""
    for el in tree_el:
        tag = _local(el)
        if tag == "grpSp":
            yield from _shapes(el)
        elif tag == "sp":
            for body in _children(el, "txBody"):
                yield "text", "\n".join(_para_text(p) for p in _children(body, "p"))
        elif tag == "graphicFrame":
            for tbl in _descendants(el, "tbl"):
                cells = ["\n".join(_para_text(p) for p in _descendants(tc, "p"))
                         for tc in _descendants(tbl, "tc")]
                yield "table", cells


def read_slides(path):
    """Return [(number, title, texts, cells)] in presentation order."""
    with zipfile.ZipFile(path) as z:
        pres = ET.fromstring(z.read("ppt/presentation.xml"))
        rels = ET.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in _descendants(rels, "Relationship")}
        out = []
        for n, sld in enumerate(_descendants(pres, "sldId"), 1):
            rid = next(v for k, v in sld.attrib.items() if _local(k) == "id" and k.startswith("{"))
            target = targets[rid]
            part = posixpath.normpath(target.lstrip("/") if target.startswith("/")
                                      else posixpath.join("ppt", target))
            root = ET.fromstring(z.read(part))
            trees = [t for c in _children(root, "cSld") for t in _children(c, "spTree")]
            texts, cells = [], []
            for kind, val in _shapes(trees[0] if trees else []):
                if kind == "text":
                    texts.append(val)
                else:
                    cells.extend(val)
            title = next((t.strip().split("\n")[0] for t in texts if t.strip()), "(untitled)")
            out.append((n, title, texts, cells))
        return out


def blocks(texts, cells):
    out = [c.strip().lower() for c in cells if len(c.strip()) > CELL_MIN]
    out += [t.strip().lower() for t in texts if len(t.strip()) > BOX_MIN]
    return out


def sig(blks):
    toks = re.sub(r"[^a-z0-9 ]", " ", " ".join(blks)).split()
    return {t for t in toks if len(t) > 5 and t not in STOP}


def main(path):
    slides = [(n, title, blocks(texts, cells), texts + cells) for n, title, texts, cells in read_slides(path)]
    problems = 0

    print("=" * 76)
    print("1. REPEATED SUBSTANTIVE STRINGS ACROSS SLIDES")
    print("=" * 76)
    hit = 0
    for a in range(len(slides)):
        for b in range(a + 1, len(slides)):
            ia, ta, ca, _ = slides[a]
            ib, tb, cb, _ = slides[b]
            shared = sorted(x for x in (set(ca) & set(cb)) if len(x) > SHARED_MIN)
            if shared:
                hit += 1
                print(f"\n  s{ia} '{ta[:40]}'  <->  s{ib} '{tb[:40]}'")
                for x in shared[:3]:
                    print(f"      repeated: {x[:88]}")
    print("  none" if not hit else "")
    problems += hit

    print("=" * 76)
    print(f"2. NEAR-DUPLICATE SLIDES (> {OVERLAP:.0%} distinctive-token overlap)")
    print("=" * 76)
    hit = 0
    for a in range(len(slides)):
        for b in range(a + 1, len(slides)):
            ia, ta, ca, _ = slides[a]
            ib, tb, cb, _ = slides[b]
            sa, sb = sig(ca), sig(cb)
            if len(sa) < MIN_TOKENS or len(sb) < MIN_TOKENS:
                continue
            ov = len(sa & sb) / min(len(sa), len(sb))
            if ov > OVERLAP:
                hit += 1
                print(f"  {ov * 100:4.0f}%  s{ia} '{ta[:38]}'  <->  s{ib} '{tb[:38]}'")
    print("  none" if not hit else "")
    problems += hit

    print("=" * 76)
    print("3. STALE STATUS TEXT (state changed, deck didn't)")
    print("=" * 76)
    hit = 0
    for n, title, _, raw in slides:
        for t in raw:
            if any(re.search(p, t, re.I) for p in STALE_PATTERNS):
                hit += 1
                print(f"  s{n} '{title[:34]}': {t.strip()[:68]}")
                break
    print("  none" if not hit else "")
    problems += hit

    print("=" * 76)
    print(f"RESULT: {problems} issue(s); reconcile before shipping." if problems else "RESULT: clean.")
    print("=" * 76)
    return 1 if problems else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    decks = []
    while args:
        a = args.pop(0)
        if a == "--stale" and args:
            STALE_PATTERNS.append(args.pop(0))
        else:
            decks.append(a)
    if len(decks) != 1:
        sys.exit('usage: python3 dedupe_audit.py Deck.pptx [--stale "regex" ...]')
    sys.exit(main(decks[0]))
