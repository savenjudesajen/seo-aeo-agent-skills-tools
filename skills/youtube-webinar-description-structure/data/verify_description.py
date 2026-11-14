"""Gate for youtube-webinar-description-structure (Python standard library, runs offline).

Usage: python verify_description.py packages.json [--allow-dashes] [--definition-opener "TEXT" ...]
packages.json: list of {id, yt_title, head_term, description, tags, has_transcript}
tags may be a comma-separated string or a list. Exit 1 on any FAIL; WARNs are printed for a human to read.
--allow-dashes: skip the em/en dash check (use only when the client's style guide allows dashes).
--definition-opener: add the "What is" wording of another language (repeatable); a question title is
  accepted only when it opens with one of these (a definition title on a definition SERP).
"""
import json
import re
import sys

DASHES = ("–", "—")
TS = re.compile(r"^\s*(\d{1,2}:)?\d{1,2}:\d{2}\s+\S", re.M)
DEFINITION_OPENERS = ["what is", "what are", "qué es", "qué son"]


def secs(t):
    p = [int(x) for x in t.split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2] if len(p) == 3 else p[0] * 60 + p[1]


def check(row, allow_dashes=False, openers=None):
    f, w = [], []
    title, desc = row.get("yt_title", ""), row.get("description", "").replace("\\n", "\n")
    head = (row.get("head_term") or "").lower()
    tags = row.get("tags", "")
    tags = [t.strip() for t in tags.split(",")] if isinstance(tags, str) else tags
    tags = [t for t in tags if t]
    if not allow_dashes:
        for name, txt in (("title", title), ("description", desc), ("tags", ",".join(tags))):
            if any(d in txt for d in DASHES):
                f.append(f"{name}: em or en dash")
    if len(title) > 70:
        f.append(f"title {len(title)} chars > 70")
    openers = [o.lower() for o in (openers or DEFINITION_OPENERS)]
    if "?" in title and not any(title.lower().lstrip("¿").startswith(o) for o in openers):
        f.append("title is a question (prompt as title)")
    if head and head not in title.lower()[:45]:
        w.append("head term not in first 45 chars of title")
    if head and head not in desc.lower()[:200]:
        f.append("head term not in first 200 chars of description")
    if not 1200 <= len(desc) <= 5000:
        f.append(f"description {len(desc)} chars outside 1200..5000")
    lines = [l for l in desc.split("\n") if l.strip()]
    if not lines:
        f.append("description is empty")
        return f, w
    if not any("http" in l for l in lines[:3]):
        f.append("no link in first 3 lines")
    if "http" in lines[0]:
        f.append("first line is a link (hook must come first)")
    if len(lines[0]) > 200:
        w.append(f"hook line {len(lines[0])} chars")
    bullets = [l for l in lines if l.lstrip().startswith("- ")]
    if not 3 <= len(bullets) <= 7:
        f.append(f"{len(bullets)} learn bullets, want 4 to 6 (3 to 7 accepted)")
    stamps = [m.group(0).split()[0] for m in TS.finditer(desc)]
    if stamps:
        s = [secs(t) for t in stamps]
        if s[0] != 0:
            f.append("chapters do not start at 00:00")
        if len(s) < 3:
            f.append("fewer than 3 chapters (YouTube ignores them)")
        if any(b - a < 10 for a, b in zip(s, s[1:])):
            f.append("chapters not ascending or shorter than 10s")
        if row.get("has_transcript") and len(s) < 6:
            w.append(f"only {len(s)} chapters on a transcript-backed row, want 6 or more")
    elif row.get("has_transcript"):
        f.append("transcript available but no chapters")
    hashtags = re.findall(r"#\w+", lines[-1])
    if not 3 <= len(hashtags) <= 5:
        f.append(f"{len(hashtags)} hashtags on last line, want 3 to 5")
    if not 8 <= len(tags) <= 15:
        f.append(f"{len(tags)} tags, want 8 to 15")
    if len(",".join(tags)) > 500:
        f.append("tags over 500 chars")
    return f, w


def main(argv):
    args, openers, allow_dashes, i = [], list(DEFINITION_OPENERS), False, 0
    while i < len(argv):
        a = argv[i]
        if a == "--allow-dashes":
            allow_dashes = True
        elif a == "--definition-opener" and i + 1 < len(argv):
            openers.append(argv[i + 1])
            i += 1
        elif a.startswith("--"):
            print(f"unknown option {a}")
            sys.exit(2)
        else:
            args.append(a)
        i += 1
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    with open(args[0], encoding="utf-8") as fh:
        rows = json.load(fh)
    bad = 0
    for r in rows:
        f, w = check(r, allow_dashes, openers)
        if f or w:
            print(r.get("id"), "FAIL:" if f else "WARN:", "; ".join(f + [f"(warn) {x}" for x in w]))
        bad += bool(f)
    print(f"{len(rows)} rows, {bad} failing")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
