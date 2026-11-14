#!/usr/bin/env python3
"""Gate checker for the content-refresh tracker. Measured, not claimed.

Usage:
  python3 verify_tracker.py Tracker.xlsx                     # or per_page.csv
  python3 verify_tracker.py Tracker.xlsx --previous last_week.xlsx

Prints PASS/FAIL per gate and exits 1 on any FAIL. Python standard library only; runs offline
(an .xlsx is read directly from its XML parts).

Gates:
  - per_page schema and column order
  - every_page_has_R: every row has a parseable refresh_date
  - delta_anchored_to_R: days_since_refresh = L - R, POST = [R+1..L], PRE = [R-n..R-1]
  - impr_delta_pct recomputes from impr_post / impr_pre
  - sitewide_control_present: scored rows carry site_impr_delta_pct; net = impr% - site%;
    the sitewide_control sheet has rows (xlsx input only)
  - maturity_gate: n < 7 -> Maturing
  - verdict in the allowed set
  - no duplicate (url, report_date)
  - append_only (with --previous): every earlier row is still present, unchanged, in the same place
"""
import csv
import posixpath
import re
import sys
import zipfile
from datetime import date, datetime, timedelta
from xml.etree import ElementTree as ET

MATURITY_MIN_DAYS = 7
PER_PAGE_COLS = ["report_date", "week_ending", "gsc_last_day", "url", "slug", "section", "refresh_date",
                 "cohort", "days_since_refresh", "post_start", "post_end", "pre_start", "pre_end", "clicks_post",
                 "clicks_pre", "clicks_delta", "impr_post", "impr_pre", "impr_delta", "impr_delta_pct", "pos_post",
                 "pos_pre", "pos_delta", "site_impr_delta_pct", "net_impr_vs_site_pct", "verdict", "note"]
ALLOWED = {"Winner", "Holding", "Rank slipped", "Decliner (audit)", "Demand-drop (rank held)",
           "Maturing", "Maturing (n<7)", "No data"}


# ---------------------------------------------------------------- readers
# Elements are matched by local name, so the reader does not depend on the OOXML namespace URIs.
def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _children(el, name):
    return [c for c in el if _local(c.tag) == name]


def _first(el, name):
    found = _children(el, name)
    return found[0] if found else None


def _text_runs(el):
    """Concatenate the <t> runs of a string item, skipping phonetic (<rPh>) runs."""
    out = []
    for child in el:
        name = _local(child.tag)
        if name == "t":
            out.append(child.text or "")
        elif name == "r":
            out.extend(t.text or "" for t in _children(child, "t"))
    return "".join(out)


def _rel_id(el):
    for key, value in el.attrib.items():
        if key.endswith("}id"):
            return value
    return None


def _col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read_xlsx(path):
    """Return {sheet_name: [row lists]} using only zipfile + ElementTree."""
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            shared = [_text_runs(si) for si in _children(ET.fromstring(z.read("xl/sharedStrings.xml")), "si")]
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        targets = {r.get("Id"): r.get("Target") for r in rels}
        sheets = {}
        for s in _children(_first(wb, "sheets"), "sheet"):
            target = targets[_rel_id(s)]
            part = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            rows = []
            for row in (e for e in ET.fromstring(z.read(part)).iter() if _local(e.tag) == "row"):
                vals = []
                for c in _children(row, "c"):
                    i = _col_index(c.get("r")) if c.get("r") else len(vals)
                    while len(vals) < i:
                        vals.append(None)
                    t = c.get("t")
                    v = _first(c, "v")
                    if t == "s" and v is not None:
                        val = shared[int(v.text)]
                    elif t == "inlineStr":
                        inline = _first(c, "is")
                        val = _text_runs(inline) if inline is not None else None
                    else:
                        val = v.text if v is not None else None
                    vals.append(val)
                rows.append(vals)
            sheets[s.get("name")] = rows
    return sheets


def read_any(path):
    if path.lower().endswith(".csv"):
        with open(path, newline="", encoding="utf-8-sig") as f:
            return {"per_page": [row for row in csv.reader(f)]}
    return read_xlsx(path)


# ---------------------------------------------------------------- helpers
def num(x):
    if x in (None, ""):
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def as_date(x):
    if x in (None, ""):
        return None
    s = str(x).strip()
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        pass
    n = num(s)
    if n is not None and 20000 < n < 80000:  # Excel serial date
        return date(1899, 12, 30) + timedelta(days=int(n))
    return None


def norm(x):
    n = num(x)
    if n is not None:
        return round(n, 6)
    return "" if x is None else str(x).strip()


def padded(row, width):
    row = list(row or [])
    return row + [None] * (width - len(row))


# ---------------------------------------------------------------- gates
def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    path = argv[0]
    previous = argv[argv.index("--previous") + 1] if "--previous" in argv else None
    checks = []

    def gate(name, ok, detail=""):
        checks.append((name, ok, detail))

    book = read_any(path)
    gate("per_page sheet exists", "per_page" in book)
    if "per_page" not in book or not book["per_page"]:
        return report(checks)
    rows = book["per_page"]
    hdr = [h if h is None else str(h).strip() for h in rows[0][:len(PER_PAGE_COLS)]]
    gate("schema/column order matches", hdr == PER_PAGE_COLS, f"got {hdr[:6]}...")
    if hdr != PER_PAGE_COLS:
        return report(checks)
    ix = {n: i for i, n in enumerate(PER_PAGE_COLS)}
    data = [padded(r, len(PER_PAGE_COLS)) for r in rows[1:] if r and any(v not in (None, "") for v in r)]

    no_r = bad_anchor = unparsed = bad_delta = no_site = bad_net = bad_mat = bad_verdict = dups = 0
    seen = set()
    for r in data:
        g = lambda k: r[ix[k]]  # noqa: E731
        key = (g("url"), g("report_date"))
        dups += key in seen
        seen.add(key)
        verdict = (g("verdict") or "").strip()
        bad_verdict += verdict not in ALLOWED

        R, L = as_date(g("refresh_date")), as_date(g("gsc_last_day"))
        if R is None:
            no_r += 1
            continue
        if L is None:
            unparsed += 1
            continue
        n = (L - R).days
        dsr = num(g("days_since_refresh"))
        if dsr is not None and int(dsr) != n:
            bad_anchor += 1
        if n >= 1:  # a post window exists
            want = {"post_start": R + timedelta(days=1), "post_end": L,
                    "pre_start": R - timedelta(days=n), "pre_end": R - timedelta(days=1)}
            for k, v in want.items():
                got = as_date(g(k))
                if got is None:
                    unparsed += 1
                    break
                if got != v:
                    bad_anchor += 1
                    break

        ip, ipre, ipct = num(g("impr_post")), num(g("impr_pre")), num(g("impr_delta_pct"))
        if ip is not None and ipre not in (None, 0) and ipct is not None:
            bad_delta += abs(round((ip - ipre) / ipre * 100, 1) - ipct) > 0.2
        site, net = num(g("site_impr_delta_pct")), num(g("net_impr_vs_site_pct"))
        scored = n >= MATURITY_MIN_DAYS and ipct is not None
        if scored and (site is None or net is None):
            no_site += 1
        if ipct is not None and site is not None and net is not None:
            bad_net += abs(round(ipct - site, 1) - net) > 0.2
        if 0 <= n < MATURITY_MIN_DAYS and verdict.split(" (")[0] != "Maturing":
            bad_mat += 1

    gate("every_page_has_R (refresh_date present and parseable)", no_r == 0, f"{no_r} rows without R")
    gate("delta_anchored_to_R (n = L-R, POST=[R+1..L], PRE=[R-n..R-1])", bad_anchor == 0 and unparsed == 0,
         f"{bad_anchor} mis-anchored rows, {unparsed} rows with unparseable dates")
    gate("impr_delta_pct recomputed matches", bad_delta == 0, f"{bad_delta} mismatched rows")
    gate("sitewide control on every scored row", no_site == 0, f"{no_site} scored rows without site delta/net")
    gate("net_impr_vs_site = impr% - site%", bad_net == 0, f"{bad_net} mismatched rows")
    if "sitewide_control" in book or not path.lower().endswith(".csv"):
        sw = [r for r in book.get("sitewide_control", [])[1:] if r and any(v not in (None, "") for v in r)]
        gate("sitewide_control sheet has rows", len(sw) > 0, "sheet missing or empty")
    gate("maturity gate applied (n<7 -> Maturing)", bad_mat == 0, f"{bad_mat} violations")
    gate("verdict in allowed set", bad_verdict == 0, f"{bad_verdict} invalid")
    gate("no duplicate (url, report_date)", dups == 0, f"{dups} duplicates")

    if previous:
        old = read_any(previous).get("per_page", [])
        old_rows = [padded(r, len(PER_PAGE_COLS)) for r in old[1:] if r and any(v not in (None, "") for v in r)]
        changed = sum(1 for i, r in enumerate(old_rows)
                      if i >= len(data) or [norm(v) for v in r[:len(PER_PAGE_COLS)]]
                      != [norm(v) for v in data[i][:len(PER_PAGE_COLS)]])
        gate("append_only (earlier rows unchanged)", changed == 0 and len(data) >= len(old_rows),
             f"{changed} earlier rows changed or missing")
    return report(checks)


def report(checks):
    for name, ok, detail in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail and not ok else ""))
    return 1 if any(not ok for _, ok, _ in checks) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
