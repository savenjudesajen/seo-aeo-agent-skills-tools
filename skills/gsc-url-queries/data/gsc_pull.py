#!/usr/bin/env python3
"""Pull URL-level Google Search queries from the official Search Console Search Analytics API.

Standard library only. Credentials come from environment variables the user sets once:

    GSC_CLIENT_ID      OAuth client ID (Desktop app client)
    GSC_CLIENT_SECRET  OAuth client secret
    GSC_REFRESH_TOKEN  refresh token for the scope webmasters.readonly

Nothing about a property is hard-coded. The script never prints the credentials or the access token.

Examples:
    python gsc_pull.py --site sc-domain:example.com --page https://example.com/pricing \
        --start 2026-01-01 --end 2026-03-31 --out queries.csv
    python gsc_pull.py --site https://www.example.com/ --pages-file urls.txt \
        --start 2026-01-01 --end 2026-03-31 --out queries.json
    python gsc_pull.py --site sc-domain:example.com --page /blog/ --operator contains \
        --start 2026-01-01 --end 2026-03-31 --out blog.csv
    python gsc_pull.py --list-sites
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TOKEN_URL = "https://oauth2.googleapis.com/token"
API_BASE = "https://www.googleapis.com/webmasters/v3/sites"
MAX_ROW_LIMIT = 25000


def access_token() -> str:
    """Exchange the refresh token for an access token. The token stays in memory."""
    env = {k: os.environ.get(k, "") for k in ("GSC_CLIENT_ID", "GSC_CLIENT_SECRET", "GSC_REFRESH_TOKEN")}
    missing = [k for k, v in env.items() if not v and k != "GSC_CLIENT_SECRET"]
    if missing:
        sys.exit("Missing environment variable(s): " + ", ".join(missing) + ". Run the one-time setup in SKILL.md.")
    body = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": env["GSC_REFRESH_TOKEN"],
        "client_id": env["GSC_CLIENT_ID"],
        "client_secret": env["GSC_CLIENT_SECRET"],
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        err = _error_text(e)
        sys.exit(f"Token exchange failed ({e.code}): {err}")
    if not data.get("access_token"):
        sys.exit("Token exchange returned no access token: " + str(data.get("error", "unknown error")))
    return data["access_token"]


def _error_text(e: urllib.error.HTTPError) -> str:
    try:
        payload = json.loads(e.read().decode("utf-8", "replace"))
    except Exception:
        return e.reason or "no detail"
    err = payload.get("error")
    if isinstance(err, dict):
        return f"{err.get('code', '')} {err.get('message', '')}".strip()
    return f"{err or ''} {payload.get('error_description', '')}".strip()


def _call(url: str, token: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if body is not None else "GET",
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def list_sites(token: str) -> list[dict]:
    return _call(API_BASE, token).get("siteEntry", [])


def query_page(token: str, site: str, page: str | None, start: str, end: str, *, operator: str = "equals",
               dimensions: list[str] | None = None, data_state: str = "final", search_type: str | None = None,
               row_limit: int = 1000) -> list[dict]:
    """All rows for one page (or the whole property if page is None), paging with startRow."""
    dimensions = dimensions or ["query"]
    row_limit = max(1, min(row_limit, MAX_ROW_LIMIT))
    url = f"{API_BASE}/{urllib.parse.quote(site, safe='')}/searchAnalytics/query"
    rows: list[dict] = []
    start_row = 0
    while True:
        body = {"startDate": start, "endDate": end, "dimensions": dimensions,
                "rowLimit": row_limit, "startRow": start_row, "dataState": data_state}
        if page:
            body["dimensionFilterGroups"] = [{"groupType": "and", "filters": [
                {"dimension": "page", "operator": operator, "expression": page}]}]
        if search_type:
            body["type"] = search_type
        batch = _call(url, token, body).get("rows", [])
        for x in batch:
            row = {"page": page or "(whole property)"}
            for dim, key in zip(dimensions, x.get("keys", [])):
                row[dim] = key
            row.update(clicks=x.get("clicks", 0), impressions=x.get("impressions", 0),
                       ctr=round(x.get("ctr", 0) * 100, 2), position=round(x.get("position", 0), 1))
            rows.append(row)
        if len(batch) < row_limit:
            return rows
        start_row += row_limit
        time.sleep(0.25)


def write_rows(rows: list[dict], out: str) -> None:
    if out.lower().endswith(".json"):
        with open(out, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
        return
    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields or ["page", "query", "clicks", "impressions", "ctr", "position"])
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list-sites", action="store_true", help="list the properties the account can see and exit")
    ap.add_argument("--site", help="property id: sc-domain:example.com or https://www.example.com/")
    ap.add_argument("--page", action="append", default=[], help="page URL or path fragment (repeatable)")
    ap.add_argument("--pages-file", help="file with one page URL per line")
    ap.add_argument("--whole-property", action="store_true", help="no page filter")
    ap.add_argument("--start", help="start date YYYY-MM-DD")
    ap.add_argument("--end", help="end date YYYY-MM-DD")
    ap.add_argument("--operator", default="equals",
                    choices=["equals", "contains", "notEquals", "notContains", "includingRegex", "excludingRegex"])
    ap.add_argument("--dimensions", default="query", help="comma-separated, e.g. query,device")
    ap.add_argument("--data-state", default="final", choices=["final", "all"])
    ap.add_argument("--search-type", help="web, image, video, news, discover, googleNews")
    ap.add_argument("--row-limit", type=int, default=1000)
    ap.add_argument("--out", default="gsc_queries.csv", help=".csv or .json")
    a = ap.parse_args(argv)

    token = access_token()
    if a.list_sites:
        for s in list_sites(token):
            print(f"{s.get('siteUrl')}\t{s.get('permissionLevel')}")
        return 0

    if not (a.site and a.start and a.end):
        ap.error("--site, --start and --end are required")
    pages = list(a.page)
    if a.pages_file:
        with open(a.pages_file, encoding="utf-8") as f:
            pages += [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    if not pages and not a.whole_property:
        ap.error("give --page, --pages-file or --whole-property")
    targets = pages or [None]

    all_rows: list[dict] = []
    summary: dict[str, object] = {}
    for i, p in enumerate(targets):
        try:
            rows = query_page(token, a.site, p, a.start, a.end, operator=a.operator,
                              dimensions=[d.strip() for d in a.dimensions.split(",") if d.strip()],
                              data_state=a.data_state, search_type=a.search_type, row_limit=a.row_limit)
            all_rows += rows
            summary[p or "(whole property)"] = len(rows)
        except urllib.error.HTTPError as e:
            summary[p or "(whole property)"] = f"error {e.code}: {_error_text(e)}"
        if i < len(targets) - 1:
            time.sleep(0.25)

    write_rows(all_rows, a.out)
    print(json.dumps({"site": a.site, "dateRange": f"{a.start}..{a.end}", "operator": a.operator,
                      "dataState": a.data_state, "out": a.out, "rows": len(all_rows),
                      "perPage": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
