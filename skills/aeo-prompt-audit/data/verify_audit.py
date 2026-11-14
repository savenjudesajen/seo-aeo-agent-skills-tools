#!/usr/bin/env python3
"""Gate for an AEO prompt audit workbook. Python standard library only; runs offline.

Usage:
  python3 verify_audit.py <audit.xlsx|audit.csv> [--sheet "Prompt Audit"] [--scope-ids <file>]
                          [--excluded-ids <file>] [--clusters "Cluster A,Cluster B"]

Checks (exit 1 on any FAIL):
 1. Every contract column header present; Source filled on every row.
 2. Decision, Reason code, Target cluster, Stage, KPI come from closed lists.
 3. Every row has a reason of at least 40 characters; no reason text repeated on more than 3 rows
    (a repeated reason means a script, not a reviewer, wrote it).
 4. REWRITE rows carry a rewrite text and an anchor; REMOVE (DUPLICATE) rows carry a Duplicate of that is a
    surviving row (KEEP/REWRITE) in the sheet or an id from an excluded set.
 5. No em dashes or en dashes anywhere.
 6. Every prompt id appears once; with --scope-ids, every in-scope prompt id appears.
 7. A REMOVE (DUPLICATE) reason that names another duplicate row must also name the row it now points to (catches
    reasons left stale when a harmonization pass re-points duplicate chains).
Warns (no fail) when REVIEW is more than 5% of rows.
It does not judge whether a decision is right. That is the hand read and the fresh-context check.
"""
import argparse
import collections
import csv
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

CONTRACT = ["Prompt ID", "Prompt", "Current topic", "Current tags", "Provenance", "Grounding keywords",
            "Grounding evidence", "Decision", "Reason code", "Reason", "Rewrite text", "Rewrite anchor",
            "Duplicate of", "Target cluster", "Stage", "KPI", "Source"]
DUPL = "REMOVE (DUPLICATE)"
DECISIONS = {"KEEP", "REWRITE", DUPL, "REMOVE", "REVIEW"}
CODES = {"POS-MISFIT", "OFF-FOCUS", "SUPERSEDED", "DUP", "COMP-ONLY", "INSTRUMENT", "NOT-ASKED", "BRAND-NAV",
         "NO-ANSWER", "LOW-VALUE", "GROUNDING-WEAK", "SHAPE-FIX", "REPOSITION", "ON-STRATEGY",
         "POSITIONING-MONITOR", "HELD"}
STAGES = {"Awareness", "Consideration", "Decision"}
KPIS = {"Mention", "Citation"}
DASHES = ("—", "–")

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def _col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def _text(node):
    return "".join(t.text or "" for t in node.iter("{%s}t" % NS["m"]))


def read_xlsx(path, sheet_name):
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = [_text(si) for si in root.findall("m:si", NS)]
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels.findall("{%s}Relationship" % PKG_REL_NS)}
        target = None
        for s in wb.find("m:sheets", NS):
            if s.get("name") == sheet_name:
                target = targets[s.get("{%s}id" % REL_NS)]
        if target is None:
            sys.exit(f"sheet '{sheet_name}' not found")
        target = target.lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        root = ET.fromstring(z.read(target))
    rows = []
    for row in root.iter("{%s}row" % NS["m"]):
        vals = {}
        for c in row.findall("m:c", NS):
            t = c.get("t")
            v = c.find("m:v", NS)
            if t == "s" and v is not None:
                val = shared[int(v.text)]
            elif t == "inlineStr":
                is_ = c.find("m:is", NS)
                val = _text(is_) if is_ is not None else ""
            else:
                val = v.text if v is not None else None
            vals[_col_index(c.get("r"))] = val
        width = max(vals) + 1 if vals else 0
        rows.append([vals.get(i) for i in range(width)])
    return rows


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [[c if c != "" else None for c in r] for r in csv.reader(f)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workbook")
    ap.add_argument("--sheet", default="Prompt Audit")
    ap.add_argument("--clusters", default="", help="comma list of allowed target clusters (else any non-empty)")
    ap.add_argument("--excluded-ids", default="", help="file of ids from excluded sets a REMOVE (DUPLICATE) row may point to")
    ap.add_argument("--scope-ids", help="file of every in-scope live prompt id")
    a = ap.parse_args()

    rows = read_csv(a.workbook) if a.workbook.lower().endswith(".csv") else read_xlsx(a.workbook, a.sheet)
    if not rows:
        sys.exit("empty sheet")
    hdr = [str(h).strip() if h is not None else "" for h in rows[0]]
    fails = []
    missing = [c for c in CONTRACT if c not in hdr]
    if missing:
        fails.append(f"1 contract: missing columns {missing}")
    ix = {h: i for i, h in enumerate(hdr)}
    data = [r for r in rows[1:] if any(c is not None and str(c).strip() for c in r)]

    def get(r, c):
        i = ix.get(c)
        if i is None or i >= len(r) or r[i] is None:
            return ""
        return str(r[i]).strip()

    clusters = {x.strip() for x in a.clusters.split(",") if x.strip()}
    excl = set(open(a.excluded_ids, encoding="utf-8").read().split()) if a.excluded_ids else set()
    decision_of = {get(r, "Prompt ID"): get(r, "Decision") for r in data}
    survivors = {pid for pid, d in decision_of.items() if d in ("KEEP", "REWRITE")}
    reasons = collections.Counter(get(r, "Reason") for r in data)
    ids = collections.Counter(get(r, "Prompt ID") for r in data)

    for r in data:
        pid = get(r, "Prompt ID")
        if not get(r, "Source"):
            fails.append(f"1 source empty: {pid}")
        d = get(r, "Decision")
        if d not in DECISIONS:
            fails.append(f"2 decision '{d}': {pid}")
        if get(r, "Reason code") not in CODES:
            fails.append(f"2 reason code '{get(r, 'Reason code')}': {pid}")
        if get(r, "Stage") not in STAGES:
            fails.append(f"2 stage '{get(r, 'Stage')}': {pid}")
        if get(r, "KPI") not in KPIS:
            fails.append(f"2 kpi '{get(r, 'KPI')}': {pid}")
        tc = get(r, "Target cluster")
        if not tc or (clusters and tc not in clusters):
            fails.append(f"2 target cluster '{tc}': {pid}")
        rs = get(r, "Reason")
        if len(rs) < 40:
            fails.append(f"3 reason too short: {pid}")
        if rs and reasons[rs] > 3:
            fails.append(f"3 reason repeated x{reasons[rs]}: {pid}")
        if d == "REWRITE" and not (get(r, "Rewrite text") and get(r, "Rewrite anchor")):
            fails.append(f"4 rewrite without text/anchor: {pid}")
        if d == DUPL:
            t = get(r, "Duplicate of")
            if not t or (t not in survivors and t not in excl):
                fails.append(f"4 duplicate target '{t}' not a survivor: {pid}")
            tokens = set(re.findall(r"[\w-]+", rs))
            named = sorted(x for x in tokens if x != t and x != pid and decision_of.get(x) == DUPL)
            if named and t not in tokens:
                fails.append(f"7 reason names duplicate row {named[0]} but points to {t}: {pid}")
        if ids[pid] > 1:
            fails.append(f"6 duplicate row for id {pid}")

    for r in rows:
        for c in r:
            if isinstance(c, str) and any(ch in c for ch in DASHES):
                fails.append("5 dash found: " + c[:60])
                break

    if a.scope_ids:
        scope = set(open(a.scope_ids, encoding="utf-8").read().split())
        miss = scope - set(ids)
        if miss:
            fails.append(f"6 {len(miss)} in-scope ids missing from the audit, e.g. {sorted(miss)[:5]}")

    counts = collections.Counter(get(r, "Decision") for r in data)
    print(f"rows {len(data)} | " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if data and counts.get("REVIEW", 0) / len(data) > 0.05:
        print(f"WARN: REVIEW is {counts['REVIEW']} of {len(data)} rows (over 5%); decide what the rules settle")
    if fails:
        print(f"FAIL ({len(fails)})")
        for f in fails[:60]:
            print("  " + f)
        sys.exit(1)
    print("AUDIT GATE: PASS")


if __name__ == "__main__":
    main()
