#!/usr/bin/env python3
"""Metrics gate for the mockup: diff the live-page spec against the mock spec field by field.

Both files come from the same probe (probe.js), so their keys line up. Numeric fields use per-field
tolerances; colours and strings must match exactly. Prints an aligned PASS/FAIL table, the score and the
failing fields. Exit code 0 = every field within tolerance.

Standard library only, offline.
usage: python3 metrics_parity.py spec/live.json spec/mock.json
"""
import json
import sys

# Absolute tolerances for numeric fields (0 = exact).
TOL = {"fs": 1.0, "fw": 0, "lh": 2.0, "pt": 3, "pr": 3, "pb": 3, "pl": 3, "rad": 1,
       "w": 8, "h": 8, "gap": 3, "cols": 10}
STRING_FIELDS = {"color", "bg", "ff", "disp", "ai", "td"}
SKIP = {"nw", "nh"}  # natural image size: informational, not scored
# A declared font name that resolves to a different family at render: map it here (lowercase).
# Example: {"brand sans display": "brand sans"}
FONT_ALIASES = {}


def fmt(v):
    return json.dumps(v) if isinstance(v, (list, dict)) else str(v)


def compare_field(f, rv, mv):
    """Return (ok, note) for one field."""
    if f == "cols":
        rv, mv = rv or [], mv or []
        ok = len(rv) == len(mv) and all(abs(a - b) <= TOL["cols"] for a, b in zip(rv, mv))
        return ok, "±%d" % TOL["cols"]
    if f == "ff":
        a = FONT_ALIASES.get(str(rv).lower(), str(rv).lower())
        b = FONT_ALIASES.get(str(mv).lower(), str(mv).lower())
        return a == b, ""
    if f in STRING_FIELDS:
        return str(rv).upper() == str(mv).upper(), ""
    if isinstance(rv, (int, float)) and isinstance(mv, (int, float)):
        t = TOL.get(f, 2)
        return abs(rv - mv) <= t, "Δ%.1f/±%g" % (abs(rv - mv), t)
    return rv == mv, ""


def main(argv):
    live_path = argv[1] if len(argv) > 1 else "spec/live.json"
    mock_path = argv[2] if len(argv) > 2 else "spec/mock.json"
    with open(live_path, encoding="utf-8") as fh:
        live = json.load(fh)
    with open(mock_path, encoding="utf-8") as fh:
        mock = json.load(fh)

    rows, npass, nfail = [], 0, 0
    for el in sorted(set(live) | set(mock)):
        if el == "meta":
            continue
        r, m = live.get(el), mock.get(el)
        if r is None or m is None:
            rows.append((el, "-", fmt(r), fmt(m), "MISSING", "FAIL"))
            nfail += 1
            continue
        for f in sorted(set(r) | set(m)):
            if f in SKIP:
                continue
            ok, note = compare_field(f, r.get(f), m.get(f))
            rows.append((el, f, fmt(r.get(f)), fmt(m.get(f)), note, "ok" if ok else "FAIL"))
            npass += ok
            nfail += not ok

    hdr = ("elem", "field", "LIVE", "MOCK", "tol", "")
    widths = [max(len(str(row[i])) for row in rows + [hdr]) for i in range(6)]
    print("  ".join(str(h).ljust(widths[i]) for i, h in enumerate(hdr)))
    print("  ".join("-" * widths[i] for i in range(6)))
    for row in rows:
        print("  ".join(str(row[i]).ljust(widths[i]) for i in range(6)))
    total = npass + nfail
    verdict = "PASS" if nfail == 0 else "FAIL (%d off)" % nfail
    print("\nMETRICS GATE: %d/%d fields within tolerance => %s" % (npass, total, verdict))
    print("FAILS:", ", ".join("%s.%s" % (row[0], row[1]) for row in rows if row[5] == "FAIL") or "none")
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
