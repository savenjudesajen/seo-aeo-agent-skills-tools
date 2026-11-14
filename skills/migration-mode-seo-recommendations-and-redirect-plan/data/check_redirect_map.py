"""GATE for a staged redirect map. Run before the map ships, and again with --final before cutover.

Usage:
    python3 check_redirect_map.py redirect-map.csv           # planning stage
    python3 check_redirect_map.py redirect-map.csv --final   # cutover: no open placeholders allowed

Standard library only, offline. Exits 1 on any finding.

Reads a CSV export of the Redirect Map tab. Column names are matched case-insensitively; required:
    Legacy URL, Destination, Redirect type NOW, Redirect status
optional:
    Final type, Source

Checks
  - every row has a decision: Redirect status is one of the allowed values
  - no duplicate legacy URLs
  - staging / dev / test hosts are marked Exclude and are never a destination
  - Exclude rows carry no destination; other rows have a destination unless the type is 410
  - redirect types are 301 / 302 / 307 / 308 / 410
  - every 302/307 is a tracked placeholder (status "Awaiting build") whose final type is 301/308
  - no chains or loops: a destination must not itself be a legacy URL that redirects
  - homepage over-use: many deep URLs sent to the homepage are treated as soft 404s
  - with --final: no "Awaiting build" or "Scope decision" rows, no remaining 302/307
"""
import csv
import sys
from urllib.parse import urlsplit

STATUSES = {"ready", "awaiting build", "scope decision", "p0", "flipped to 301", "exclude"}
TYPES = {"301", "302", "307", "308", "410"}
TEMPORARY = {"302", "307"}
NON_PROD_LABELS = ("staging", "stage", "stg", "dev", "uat", "test", "qa", "preview", "sandbox")
HOMEPAGE_SHARE = 0.10     # flag when more than this share of deep URLs go to a homepage
HOMEPAGE_MIN = 3          # ... and at least this many rows do

REQUIRED = {"legacy url": "legacy", "destination": "dest", "redirect type now": "now",
            "redirect status": "status"}
OPTIONAL = {"final type": "final", "source": "source"}


def norm(url):
    """Comparable form of a URL: lower-case scheme and host, no fragment, no trailing slash on paths."""
    url = (url or "").strip()
    if not url:
        return ""
    s = urlsplit(url)
    path = s.path.rstrip("/") or "/"
    q = f"?{s.query}" if s.query else ""
    return f"{s.scheme.lower()}://{s.netloc.lower()}{path}{q}"


def is_non_prod(url):
    host = urlsplit(url).netloc.lower().split(":")[0]
    first = host.split(".")[0] if host else ""
    return any(first == lab or first.startswith(lab + "-") or first.endswith("-" + lab)
               for lab in NON_PROD_LABELS)


def is_home(url):
    return urlsplit(url).path in ("", "/") and not urlsplit(url).query


BLANK = {"-", "–", "—"}   # a lone hyphen, en dash or em dash in a cell means "empty"


def cell(value):
    value = (value or "").strip()
    return "" if value in BLANK else value


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        header = {(h or "").strip().lower(): h for h in reader.fieldnames or []}
        missing = [k for k in REQUIRED if k not in header]
        if missing:
            sys.exit(f"missing required column(s): {', '.join(missing)}")
        cols = {**{v: header[k] for k, v in REQUIRED.items()},
                **{v: header[k] for k, v in OPTIONAL.items() if k in header}}
        rows = []
        for line, raw in enumerate(reader, 2):
            row = {k: cell(raw.get(h)) for k, h in cols.items()}
            if not any(row.values()):
                continue
            row["line"] = line
            rows.append(row)
        return rows


def check(rows, final=False):
    findings = []

    def flag(row, msg):
        findings.append(f"line {row['line']}: {msg}  [{row['legacy'] or '(no legacy URL)'}]")

    seen = {}
    for r in rows:
        key = norm(r["legacy"])
        if not key:
            flag(r, "no legacy URL")
            continue
        if key in seen:
            flag(r, f"duplicate legacy URL (first on line {seen[key]})")
        else:
            seen[key] = r["line"]

    redirecting = {norm(r["legacy"]): r for r in rows
                   if r["status"].lower() != "exclude" and r["dest"] and r["now"] in TYPES - {"410"}}

    deep_total = deep_home = 0
    for r in rows:
        status, now, final_type = r["status"].lower(), r["now"], r.get("final", "")
        if status not in STATUSES:
            flag(r, f"Redirect status '{r['status']}' is not one of: {', '.join(sorted(STATUSES))}")
        if is_non_prod(r["legacy"]) and status != "exclude":
            flag(r, "staging/dev/test host must be marked Exclude")
        if r["dest"] and is_non_prod(r["dest"]):
            flag(r, f"destination is a staging/dev/test host: {r['dest']}")
        if status == "exclude":
            if r["dest"]:
                flag(r, "Exclude row should not carry a destination")
            continue
        if status == "scope decision":
            if final:
                flag(r, "Scope decision still open at cutover")
            continue
        if now not in TYPES:
            flag(r, f"Redirect type NOW '{now}' is not one of {', '.join(sorted(TYPES))}")
            continue
        if now != "410" and not r["dest"]:
            flag(r, "no destination (use a destination or a deliberate 410)")
            continue
        if now in TEMPORARY:
            if status != "awaiting build":
                flag(r, f"{now} without status 'Awaiting build': untracked temporary redirect")
            if final_type and final_type not in {"301", "308"}:
                flag(r, f"placeholder {now} must end as 301/308, Final type is '{final_type}'")
            if final:
                flag(r, f"{now} placeholder still in place at cutover; flip to 301")
        if status == "awaiting build" and final:
            flag(r, "Awaiting build still open at cutover")
        if r["dest"]:
            d = norm(r["dest"])
            if d == norm(r["legacy"]):
                flag(r, "redirects to itself")
            elif d in redirecting:
                hops, cur, path = 1, d, [norm(r["legacy"])]
                while cur in redirecting and hops < 20:
                    if cur in path:
                        flag(r, "redirect loop: " + " -> ".join(path + [cur]))
                        break
                    path.append(cur)
                    cur = norm(redirecting[cur]["dest"])
                    hops += 1
                else:
                    flag(r, f"chain of {hops} hops; map straight to the final URL {cur}")
            if not is_home(r["legacy"]):
                deep_total += 1
                if is_home(r["dest"]):
                    deep_home += 1

    if deep_total and deep_home >= HOMEPAGE_MIN and deep_home / deep_total > HOMEPAGE_SHARE:
        findings.append(f"homepage over-use: {deep_home} of {deep_total} deep URLs redirect to a homepage "
                        f"(> {HOMEPAGE_SHARE:.0%}); map to the closest relevant page or use 410")
    return findings


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        sys.exit("usage: python3 check_redirect_map.py redirect-map.csv [--final]")
    rows = load(args[0])
    findings = check(rows, final="--final" in argv)
    counts = {}
    for r in rows:
        counts[r["status"] or "(blank)"] = counts.get(r["status"] or "(blank)", 0) + 1
    print(f"{len(rows)} rows · " + " · ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    for f in findings:
        print("  " + f)
    print(f"RESULT: {len(findings)} finding(s)." if findings else "RESULT: clean.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
