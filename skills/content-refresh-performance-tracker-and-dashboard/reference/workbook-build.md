# The tracker workbook (schema and builder)

Tidy **long** format, so a dashboard can pivot it and weekly runs can **append** (never overwrite). Build
it with `data/build_tracker.py` (Python 3 with `openpyxl`): it reads one JSON file with the pulled data and
the config and writes or appends to the .xlsx. Stamp every appended row with `report_date`, `week_ending`
and `gsc_last_day`.

## Sheet `per_page`: one row per URL × report week (the master "which pages worked")

`report_date, week_ending, gsc_last_day, url, slug, section, refresh_date, cohort,
days_since_refresh, post_start, post_end, pre_start, pre_end, clicks_post, clicks_pre,
clicks_delta, impr_post, impr_pre, impr_delta, impr_delta_pct, pos_post, pos_pre, pos_delta,
site_impr_delta_pct, net_impr_vs_site_pct, verdict, note`

## Sheet `milestone_curve`: one row per cohort × milestone (the +7/+14/+28/+90 curve)

`report_date, cohort, n_pages, milestone_days, post_window, pre_window,
cohort_clicks_delta_pct, cohort_impr_delta_pct, cohort_pos_delta,
site_clicks_delta_pct, site_impr_delta_pct, site_pos_delta, net_impr_lift_pts, net_pos_lift`

## Sheet `sitewide_control`: one row per window used this run

`report_date, window_label, days, post_window, pre_window, clicks_post, clicks_pre,
clicks_delta_pct, impr_post, impr_pre, impr_delta_pct, pos_post, pos_pre, pos_delta`

## Sheet `README`

Method, verdict definitions and thresholds, dashboard connection steps, the weekly-append rule, and the
go-live source used (say so when CMS or sitemap dates stand in for a tracking sheet).

## Rules

- **Append-only**: load the existing workbook, append after the last used row of each sheet, save back.
  `openpyxl.load_workbook` keeps formatting; re-check any native charts after saving. Never change the
  column order: it breaks the dashboard's data source.
- **Keep last week's copy** (workbook or `per_page.csv`) before appending, so
  `data/verify_tracker.py --previous` can prove the earlier rows are untouched.
- **Types**: store percentage deltas as real numbers in percentage points (`-20.0`, not `"-20.0%"`) and
  positions as numbers, so charts aggregate. (A CSV import into Looker Studio still defaults them to Text:
  see `looker-and-schedule.md`.)
- Dates are ISO `YYYY-MM-DD` text, so the gate script and dashboards read them the same way.
- The builder also writes `per_page.csv` and `milestone_curve.csv` (same headers) for a CSV dashboard
  source.

## Input JSON for the builder

```json
{
  "config": {"client": "ExampleSite", "output_dir": ".", "output_xlsx": "Example_Refresh_Tracker.xlsx"},
  "report_date": "2030-01-07", "week_ending": "2030-01-06", "gsc_last_day": "2030-01-04",
  "per_page": [{"url": "https://blog.example.com/keyword-a-guide/", "slug": "keyword-a-guide",
    "section": "blog", "refresh_date": "2029-12-05", "cohort": "2029-12-05", "days_since_refresh": 30,
    "post_start": "2029-12-06", "post_end": "2030-01-04", "pre_start": "2029-11-05", "pre_end": "2029-12-04",
    "clicks_post": 120, "clicks_pre": 100, "impr_post": 5000, "impr_pre": 4000,
    "pos_post": 8.0, "pos_pre": 9.0, "site_impr_delta_pct": -10.0, "note": ""}],
  "milestones": [],
  "sitewide": [{"window_label": "2029-12-05 cohort", "days": 30, "post_window": "2029-12-06..2030-01-04",
    "pre_window": "2029-11-05..2029-12-04", "clicks_post": 9000, "clicks_pre": 10000,
    "impr_post": 450000, "impr_pre": 500000, "pos_post": 20.0, "pos_pre": 20.0}]
}
```

All values above are invented for illustration.
