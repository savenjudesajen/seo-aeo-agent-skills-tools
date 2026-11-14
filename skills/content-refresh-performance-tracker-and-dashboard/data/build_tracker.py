#!/usr/bin/env python3
"""Build or APPEND a content-refresh performance tracker workbook (+ CSV mirrors).

Usage:  python3 build_tracker.py input.json        (needs: pip install openpyxl)

input.json shape (all values come from the run; see reference/workbook-build.md for an example):
{
  "config": {"client": "ExampleSite", "output_dir": ".", "output_xlsx": "Example_Refresh_Tracker.xlsx"},
  "report_date": "YYYY-MM-DD", "week_ending": "YYYY-MM-DD", "gsc_last_day": "YYYY-MM-DD",
  "per_page": [ {url, slug, section, refresh_date, cohort, days_since_refresh,
                 post_start, post_end, pre_start, pre_end,
                 clicks_post, clicks_pre, impr_post, impr_pre, pos_post, pos_pre,
                 site_impr_delta_pct, note, verdict (optional)} ... ],
  "milestones": [ {cohort, n_pages, milestone_days, post_window, pre_window,
                   c_clicks_post, c_clicks_pre, c_impr_post, c_impr_pre, c_pos_post, c_pos_pre,
                   s_clicks_post, s_clicks_pre, s_impr_post, s_impr_pre, s_pos_post, s_pos_pre} ... ],
  "sitewide": [ {window_label, days, post_window, pre_window, clicks_post, clicks_pre,
                 impr_post, impr_pre, pos_post, pos_pre} ... ]
}
Append-only: if the xlsx exists, new rows are appended after the last used row of each sheet
(headers and formatting kept). Verdicts are auto-classified unless provided.
Nothing about any specific site is hard-coded.
"""
import csv
import json
import os
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

MATURITY_MIN_DAYS = 7
VERDICT_COLORS = {"Winner": "C6EFCE", "Holding": "FFF2CC", "Rank slipped": "FCE4D6",
                  "Decliner (audit)": "FFC7CE", "Demand-drop (rank held)": "DDEBF7",
                  "Maturing": "EDEDED", "No data": "EDEDED"}
PER_PAGE_COLS = ["report_date", "week_ending", "gsc_last_day", "url", "slug", "section",
                 "refresh_date", "cohort", "days_since_refresh", "post_start", "post_end", "pre_start", "pre_end",
                 "clicks_post", "clicks_pre", "clicks_delta", "impr_post", "impr_pre", "impr_delta", "impr_delta_pct",
                 "pos_post", "pos_pre", "pos_delta", "site_impr_delta_pct", "net_impr_vs_site_pct", "verdict", "note"]
MILE_COLS = ["report_date", "cohort", "n_pages", "milestone_days", "post_window", "pre_window",
             "cohort_clicks_delta_pct", "cohort_impr_delta_pct", "cohort_pos_delta",
             "site_clicks_delta_pct", "site_impr_delta_pct", "site_pos_delta", "net_impr_lift_pts", "net_pos_lift"]
SITE_COLS = ["report_date", "window_label", "days", "post_window", "pre_window",
             "clicks_post", "clicks_pre", "clicks_delta_pct", "impr_post", "impr_pre", "impr_delta_pct",
             "pos_post", "pos_pre", "pos_delta"]


def pct(a, b):
    if a is None or b in (None, 0):
        return None
    return round((a - b) / b * 100, 1)


def diff(a, b, nd=None):
    if a is None or b is None:
        return None
    return round(a - b, nd) if nd is not None else a - b


def classify(days_since_refresh, impr_pct, net, pos_delta):
    """Verdict taxonomy from reference/delta-method.md.

    Starting heuristics (percentage points for impressions, positions for rank). Tune per site,
    keep the rule order, and record changes in the README sheet.
    """
    if days_since_refresh is None or days_since_refresh < 0:
        return "No data"
    if days_since_refresh < MATURITY_MIN_DAYS:
        return "Maturing"
    if impr_pct is None or pos_delta is None:
        return "No data"
    if net is not None and net <= -15 and pos_delta <= 0.5:
        return "Demand-drop (rank held)"
    if net is not None and net <= -5 and pos_delta > 1.0:
        return "Decliner (audit)"
    if pos_delta > 3 and (net is None or net < 0):
        return "Decliner (audit)"
    if (impr_pct >= 0 and pos_delta <= 0.3) or (net is not None and net >= 8 and pos_delta <= 0.5):
        return "Winner"
    if pos_delta > 3:
        return "Rank slipped"
    return "Holding"


def style_header(ws, ncols):
    fill = PatternFill("solid", fgColor="404040")
    font = Font(color="FFFFFF", bold=True, size=10)
    thin = Side(style="thin", color="D0D0D0")
    border = Border(thin, thin, thin, thin)
    for c in range(1, ncols + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill, cell.font, cell.border = fill, font, border
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def ensure_sheet(wb, title, cols):
    if title in wb.sheetnames:
        ws = wb[title]
        hdr = [c.value for c in ws[1]]
        if hdr[:len(cols)] != cols:
            sys.exit(f"{title}: header differs from the schema; refusing to append (column order is fixed)")
        return ws
    ws = wb.create_sheet(title)
    ws.append(cols)
    style_header(ws, len(cols))
    ws.freeze_panes = "A2"
    return ws


def build(inp):
    cfg = inp["config"]
    rd, we, gl = inp["report_date"], inp["week_ending"], inp["gsc_last_day"]
    out_dir = cfg.get("output_dir", ".")
    out = os.path.join(out_dir, cfg["output_xlsx"])
    first_time = not os.path.exists(out)
    wb = Workbook() if first_time else load_workbook(out)
    if first_time and "Sheet" in wb.sheetnames:
        wb.remove(wb["Sheet"])

    pp = ensure_sheet(wb, "per_page", PER_PAGE_COLS)
    existing = {(r[3], r[0]) for r in pp.iter_rows(min_row=2, values_only=True) if r and r[3]}
    for r in inp.get("per_page", []):
        if (r.get("url"), rd) in existing:
            sys.exit(f"per_page already has {r.get('url')} for report_date {rd}; refusing to duplicate")
        cp, cpre = r.get("clicks_post"), r.get("clicks_pre")
        ip, ipre = r.get("impr_post"), r.get("impr_pre")
        ppost, ppre = r.get("pos_post"), r.get("pos_pre")
        site = r.get("site_impr_delta_pct")
        ipct = pct(ip, ipre)
        pdelta = diff(ppost, ppre, 1)
        net = round(ipct - site, 1) if (ipct is not None and site is not None) else None
        verdict = r.get("verdict") or classify(r.get("days_since_refresh"), ipct, net, pdelta)
        pp.append([rd, we, gl, r.get("url"), r.get("slug"), r.get("section"), r.get("refresh_date"),
                   r.get("cohort"), r.get("days_since_refresh"), r.get("post_start"), r.get("post_end"),
                   r.get("pre_start"), r.get("pre_end"), cp, cpre, diff(cp, cpre),
                   ip, ipre, diff(ip, ipre), ipct, ppost, ppre, pdelta, site, net, verdict, r.get("note")])
        vc = VERDICT_COLORS.get(verdict) or VERDICT_COLORS.get(verdict.split(" (")[0])
        if vc:
            pp.cell(row=pp.max_row, column=PER_PAGE_COLS.index("verdict") + 1).fill = PatternFill("solid", fgColor=vc)

    mc = ensure_sheet(wb, "milestone_curve", MILE_COLS)
    for m in inp.get("milestones", []):
        ci, si = pct(m["c_impr_post"], m["c_impr_pre"]), pct(m["s_impr_post"], m["s_impr_pre"])
        cc, scl = pct(m["c_clicks_post"], m["c_clicks_pre"]), pct(m["s_clicks_post"], m["s_clicks_pre"])
        cpd, spd = diff(m["c_pos_post"], m["c_pos_pre"], 1), diff(m["s_pos_post"], m["s_pos_pre"], 1)
        mc.append([rd, m["cohort"], m.get("n_pages"), m["milestone_days"], m.get("post_window"), m.get("pre_window"),
                   cc, ci, cpd, scl, si, spd,
                   round(ci - si, 1) if (ci is not None and si is not None) else None,
                   round(cpd - spd, 1) if (cpd is not None and spd is not None) else None])

    sc = ensure_sheet(wb, "sitewide_control", SITE_COLS)
    for s in inp.get("sitewide", []):
        sc.append([rd, s["window_label"], s.get("days"), s.get("post_window"), s.get("pre_window"),
                   s["clicks_post"], s["clicks_pre"], pct(s["clicks_post"], s["clicks_pre"]),
                   s["impr_post"], s["impr_pre"], pct(s["impr_post"], s["impr_pre"]),
                   s["pos_post"], s["pos_pre"], diff(s["pos_post"], s["pos_pre"], 1)])

    if first_time:
        widths = {"url": 52, "slug": 32, "note": 55, "verdict": 22}
        for i, name in enumerate(PER_PAGE_COLS, 1):
            pp.column_dimensions[get_column_letter(i)].width = widths.get(name, 13)
        pp.freeze_panes = "D2"
        pp.auto_filter.ref = f"A1:{get_column_letter(len(PER_PAGE_COLS))}1"
        rm = wb.create_sheet("README")
        rm.column_dimensions["A"].width = 110
        for i, line in enumerate([
                f"{cfg.get('client', '')}: content-refresh performance tracker",
                "Every page is judged against its OWN go-live date: POST=[R+1..L] vs equal PRE=[R-n..R-1].",
                "net_impr_vs_site = page impressions delta% - sitewide impressions delta%. n<7 = Maturing (unscored).",
                "Verdicts come only from this clean since-refresh read, never a dashboard rolling delta.",
                "Verdict thresholds: see classify() in build_tracker.py; record any per-site change here.",
                "Go-live source: (record sheet / CMS / sitemap / manual here).",
                "Weekly runs APPEND a dated snapshot (report_date). Keep column order fixed for the dashboard.",
                "Dashboard: milestone_curve line | per_page net-vs-site bar | verdict counts."], 1):
            rm.cell(row=i, column=1, value=line).alignment = Alignment(wrap_text=True, vertical="top")
        if mc.max_row > 1:
            ch = LineChart()
            ch.title = "Net impressions lift vs sitewide by milestone"
            ch.x_axis.title, ch.y_axis.title = "days since refresh", "net lift (pts)"
            ch.height, ch.width = 8, 16
            data = Reference(mc, min_col=MILE_COLS.index("net_impr_lift_pts") + 1, min_row=1, max_row=mc.max_row)
            cats = Reference(mc, min_col=MILE_COLS.index("milestone_days") + 1, min_row=2, max_row=mc.max_row)
            ch.add_data(data, titles_from_data=True)
            ch.set_categories(cats)
            mc.add_chart(ch, "P2")

    wb.save(out)
    # CSV mirrors for a Looker Studio CSV source
    for sheet in ("per_page", "milestone_curve"):
        with open(os.path.join(out_dir, sheet + ".csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for row in wb[sheet].iter_rows(values_only=True):
                w.writerow(row)
    print("saved", out, "| per_page rows total:", wb["per_page"].max_row - 1)


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as fh:
        build(json.load(fh))
