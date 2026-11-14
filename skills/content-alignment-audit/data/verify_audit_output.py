#!/usr/bin/env python3
"""
Gate for a content alignment audit sheet (standard library only, runs offline).

Usage:
    python verify_audit_output.py audit_output.csv [--scrape-imp 5000]

Fails (exit 1) when:
    - fewer than 5 pages
    - a required column is missing
    - no similarity scores, or any score outside 0-1
    - fewer than 70% of rows have impressions
    - any row has a strategy outside the six, or more than 20% lack a rationale
    - any confidence is not HIGH / MEDIUM / LOW
    - a page above the scrape threshold has no Scrape_Summary
    - a REDIRECT or RETIRE row is HIGH confidence without Unique_Content = NO or PARTIAL
    - a non-leader REDIRECT, RETIRE or REPURPOSE row has no measured Value_Add between 0 and 1
Warns when more than 30% of rows are LOW confidence, and when a cluster leader's similarity is 1.0
(record its highest score to a cluster member instead of a placeholder).
If you cannot run Python, apply these checks by hand and say the script was not run.

Expected columns:
    URL, Impressions, Clicks, Position, Cluster_ID, Cluster_Leader, Similarity_Score, Value_Add, Strategy,
    Confidence, Rationale, Unique_Content, Scrape_Summary, GSC_Performance, Research_Notes,
    Action_Required, Effort_Level
"""

import argparse
import csv
import sys
from collections import Counter

REQUIRED = [
    "URL", "Impressions", "Clicks", "Position", "Cluster_ID", "Cluster_Leader",
    "Similarity_Score", "Value_Add", "Strategy", "Confidence", "Rationale", "Unique_Content",
    "Scrape_Summary", "GSC_Performance", "Research_Notes", "Action_Required", "Effort_Level",
]
STRATEGIES = {"REDIRECT", "REPURPOSE", "REFORMAT", "REFRESH", "RETIRE", "REMAIN"}
CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}


def num(value):
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return None


def verify(path, high_imp):
    failures = []
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except OSError as e:
        print(f"FAIL: could not read {path}: {e}")
        return False
    if not rows:
        print("FAIL: the sheet is empty")
        return False
    n = len(rows)
    print(f"Verifying {path}: {n} rows")

    # 1. Scope
    if n < 5:
        failures.append(f"at least 5 pages required; found {n}")

    # 2. Columns
    missing = [c for c in REQUIRED if c not in rows[0]]
    if missing:
        failures.append(f"missing columns: {missing}")
        for msg in failures:
            print(f"FAIL: {msg}")
        return False

    # 3. Similarity
    scores = []
    for i, r in enumerate(rows, start=2):
        s = num(r["Similarity_Score"])
        if s is None:
            failures.append(f"line {i}: similarity '{r['Similarity_Score']}' is not a number")
        elif not 0 <= s <= 1:
            failures.append(f"line {i}: similarity {s} outside 0-1")
        else:
            scores.append(s)
    if not [s for s in scores if s > 0]:
        failures.append("no similarity scores (all zero or missing)")

    # 4. Search Console metrics
    with_imp = sum(1 for r in rows if (num(r["Impressions"]) or 0) > 0)
    print(f"  rows with impressions: {with_imp}/{n}")
    if with_imp < 0.7 * n:
        failures.append(f"only {with_imp}/{n} rows have impressions")

    # 5. Strategies and rationale
    counts, no_reason = Counter(), 0
    for i, r in enumerate(rows, start=2):
        strat = r["Strategy"].strip()
        if strat not in STRATEGIES:
            failures.append(f"line {i}: strategy '{strat}' is not one of the six")
            continue
        counts[strat] += 1
        if len(r["Rationale"].strip()) < 10:
            no_reason += 1
    print("  strategies: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if no_reason > 0.2 * n:
        failures.append(f"{no_reason}/{n} rows lack a rationale")

    # 6. Confidence
    conf = Counter()
    for i, r in enumerate(rows, start=2):
        c = r["Confidence"].strip()
        if c not in CONFIDENCE:
            failures.append(f"line {i}: confidence '{c}' must be HIGH, MEDIUM or LOW")
        conf[c] += 1
    print("  confidence: " + ", ".join(f"{k} {conf.get(k, 0)}" for k in ("HIGH", "MEDIUM", "LOW")))
    if conf.get("LOW", 0) > 0.3 * n:
        print(f"  WARNING: {conf['LOW']}/{n} rows are LOW confidence; check that flags are not overused")

    # 7. Scrape evidence above the scrape threshold
    for i, r in enumerate(rows, start=2):
        if (num(r["Impressions"]) or 0) > high_imp and not r["Scrape_Summary"].strip():
            failures.append(f"line {i}: {r['URL']} is above {high_imp:g} impressions with no Scrape_Summary")

    # 7b. Measured value-add on consolidation and rewrite rows; measured leader similarity
    placeholder_leaders = 0
    for i, r in enumerate(rows, start=2):
        leader = r["Cluster_Leader"].strip().upper() == "TRUE"
        if leader and num(r["Similarity_Score"]) == 1.0:
            placeholder_leaders += 1
        if not leader and r["Strategy"].strip() in {"REDIRECT", "RETIRE", "REPURPOSE"}:
            va = num(r["Value_Add"])
            if va is None or not 0 <= va <= 1:
                failures.append(f"line {i}: {r['Strategy'].strip()} without a measured Value_Add (0-1)")
    if placeholder_leaders:
        print(f"  WARNING: {placeholder_leaders} cluster leader(s) have similarity 1.0; record the highest "
              "score to a cluster member")

    # 8. High-confidence removals need content evidence
    for i, r in enumerate(rows, start=2):
        if r["Strategy"].strip() in {"REDIRECT", "RETIRE"} and r["Confidence"].strip() == "HIGH" \
                and r["Unique_Content"].strip().upper() not in {"NO", "PARTIAL"}:
            failures.append(f"line {i}: HIGH-confidence {r['Strategy'].strip()} without a unique-content check")

    flagged = sum(1 for r in rows if r["Action_Required"].strip().lower() in {"true", "yes"})
    print(f"  action required / flagged: {flagged}/{n}")

    if failures:
        for msg in failures:
            print(f"FAIL: {msg}")
        print(f"{len(failures)} failure(s)")
        return False
    print("PASS: all gates passed; the sheet is ready for review")
    return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Gate for a content alignment audit sheet")
    ap.add_argument("csv_file")
    ap.add_argument("--scrape-imp", "--high-imp", dest="scrape_imp", type=float, default=5000,
                    help="scrape threshold: pages above it need a Scrape_Summary")
    a = ap.parse_args()
    sys.exit(0 if verify(a.csv_file, a.scrape_imp) else 1)
