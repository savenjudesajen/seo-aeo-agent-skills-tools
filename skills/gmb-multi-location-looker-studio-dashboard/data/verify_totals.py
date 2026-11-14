#!/usr/bin/env python3
"""verify_totals.py - reconciliation gate for a Business Profile long fact table.

Usage:  python3 verify_totals.py path/to/long.csv

Expected columns (header row):
  month, location, city, state, search_mobile, search_desktop, maps_mobile,
  maps_desktop, calls, directions, website_clicks, impressions, interactions
Optional columns: messages, bookings (when present they count towards interactions,
matching Google's "Business Profile interactions" definition).

Checks (measured, not claimed):
  1. impressions == search_mobile + search_desktop + maps_mobile + maps_desktop   (every row)
  2. interactions == calls + directions + website_clicks [+ messages + bookings]  (every row)
  3. no negative / non-numeric values
  4. every location has a row for every month in the file (catches a missing last month)
  5. prints per-month, per-state and grand totals + engagement rate
Exit 0 = all checks pass; exit 1 = at least one problem (do NOT ship the dashboard).
Standard library only; runs offline.
"""
import csv
import sys
from collections import defaultdict

VIEW = ["search_mobile", "search_desktop", "maps_mobile", "maps_desktop"]
ACT_BASE = ["calls", "directions", "website_clicks"]
ACT_OPTIONAL = ["messages", "bookings"]


def to_int(v):
    try:
        return int(float(v if v not in (None, "") else 0))
    except (TypeError, ValueError):
        return None


def main(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        rows = list(reader)
    if not rows:
        print("NO ROWS - wrong file?")
        return 1

    required = ["month", "location", "state"] + VIEW + ACT_BASE + ["impressions", "interactions"]
    missing_cols = [c for c in required if c not in header]
    if missing_cols:
        print(f"FAIL - missing column(s): {', '.join(missing_cols)}")
        return 1
    act = ACT_BASE + [c for c in ACT_OPTIONAL if c in header]

    problems = []
    by_month_imp = defaultdict(int)
    by_month_int = defaultdict(int)
    by_state_imp = defaultdict(int)
    by_state_int = defaultdict(int)
    months_per_loc = defaultdict(set)
    g_imp = g_int = 0
    for r in rows:
        tag = f"{r.get('month')},{r.get('location')}"
        vals = {}
        for k in VIEW + act + ["impressions", "interactions"]:
            iv = to_int(r.get(k))
            if iv is None:
                problems.append(f"{tag}: non-numeric {k}={r.get(k)!r}")
                iv = 0
            if iv < 0:
                problems.append(f"{tag}: negative {k}={iv}")
            vals[k] = iv
        imp_calc = sum(vals[k] for k in VIEW)
        int_calc = sum(vals[k] for k in act)
        if imp_calc != vals["impressions"]:
            problems.append(f"{tag}: impressions col {vals['impressions']} != sum(views) {imp_calc}")
        if int_calc != vals["interactions"]:
            problems.append(f"{tag}: interactions col {vals['interactions']} != sum(actions) {int_calc}")
        m, s, loc = r.get("month"), r.get("state"), r.get("location")
        months_per_loc[loc].add(m)
        by_month_imp[m] += vals["impressions"]
        by_month_int[m] += vals["interactions"]
        by_state_imp[s] += vals["impressions"]
        by_state_int[s] += vals["interactions"]
        g_imp += vals["impressions"]
        g_int += vals["interactions"]

    all_months = set(by_month_imp)
    for loc, ms in sorted(months_per_loc.items(), key=lambda kv: str(kv[0])):
        gap = sorted(all_months - ms)
        if gap:
            problems.append(f"{loc}: no row for month(s) {', '.join(gap)}")

    print(f"rows={len(rows)}  locations={len(months_per_loc)}  months={len(all_months)}")
    print(f"interactions = {' + '.join(act)}")
    print("\nPER MONTH (impressions / interactions):")
    for m in sorted(by_month_imp):
        print(f"  {m}: {by_month_imp[m]:>8,} / {by_month_int[m]:>6,}")
    print("\nPER STATE (impressions / interactions):")
    for s in sorted(by_state_imp, key=lambda k: -by_state_imp[k]):
        print(f"  {s}: {by_state_imp[s]:>8,} / {by_state_int[s]:>6,}")
    er = (g_int / g_imp * 100) if g_imp else 0
    print(f"\nGRAND TOTAL  impressions={g_imp:,}  interactions={g_int:,}  engagement={er:.2f}%")

    if problems:
        print(f"\nFAIL - {len(problems)} problem(s) (first 50):")
        for p in problems[:50]:
            print("  -", p)
        return 1
    print("\nPASS - every row reconciles and every location has every month.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
