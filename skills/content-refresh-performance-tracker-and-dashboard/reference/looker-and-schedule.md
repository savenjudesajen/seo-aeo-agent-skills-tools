# Phase 5: weekly auto-update and Looker Studio dashboard (recipe and pitfalls)

## Weekly scheduled task

Create a recurring task in your agent host's scheduler (or cron / a CI schedule), with the cron in LOCAL
time, for example `0 9 * * 1` (Mondays 09:00). Its prompt must be self-contained:

1. Read the tracker to get the page list and refresh dates, and check the go-live source for NEW refreshes
   (new pages join as a new cohort).
2. Copy last week's workbook (or `per_page.csv`) aside for the append-only check.
3. Confirm L, then re-pull Search Console through Route A or B (`gsc-pull.md`) for every page, milestone
   window and sitewide window.
4. **Append** a dated snapshot with `data/build_tracker.py` (never overwrite).
5. Run `data/verify_tracker.py <workbook> --previous <last week's copy>`; stop and report if it fails.
6. Refresh the dashboard source (below) and print a short run summary: pages scored, verdict counts,
   new Maturing pages, anything that failed.

Unattended Search Console pulls through a browser need exactly one connected browser and the right `/u/N/`
account.

## Looker Studio: two source options

- **CSV file upload**: simplest to stand up, but the source needs a **manual re-upload** each week to
  refresh. Upload `per_page.csv` and `milestone_curve.csv` as separate data sources (different schemas).
- **Google Sheet** source (auto-refresh): the Sheet must belong to the SAME Google account as the Looker
  Studio report; the weekly task pushes rows to it, so the refresh is hands-off. Prefer this when the
  client wants zero-touch updates.

## Build recipe (follow in order)

**1. Add the CSV source.** Create report → Add data → CSV File Upload → authorise (a one-time Google Cloud
Storage OAuth: the USER must approve it; never approve OAuth on their behalf). Then create the dataset (name
it) → add file. Adding a file opens a native OS file picker that browser automation cannot drive, so the
USER selects the CSV. The dataset dialog's Continue button may sit in a cross-origin frame that ignores
synthetic clicks: ask the user to click it, or use a file-upload action if the page exposes a real
`<input type=file>` element. Everything after the source is added is in the main document and works with
drag and drop plus the properties panel.

**2. Fix field types (required: CSV imports numbers as Text).** Numeric columns arrive as Text (more often
when a column has blank cells, such as `clicks_delta` for Maturing rows), so metrics won't aggregate. Fix
it at the source: Resource → Manage added data sources → edit the per_page source → for each `*_delta`,
`*_pct`, `pos_*`, `impr_*` and `clicks_*` field, open its Type menu → **Numeric → Number**. Use plain
**Number**, NOT Percent: the values are already percentage points (for example `25.0`), and Percent would
show them 100 times too large. Submenus can render slowly; hover, wait, then click. Use the field search box
to isolate one field at a time. Click Done.

**3. Build the charts** (drag and drop plus the properties panel):

- **Verdict tally**: search the Data panel for `verdict` and drag it onto the canvas (this creates a table) →
  metric = Record Count. Gives Winner, Decliner and other counts. Optionally switch it to a bar chart.
- **Per-page win/loss bar**: drag `slug` onto the canvas → add metric `net_impr_vs_site_pct` → chart type
  horizontal bar. In Setup, set the number of bars higher than your page count and turn OFF "Group the rest
  as Others"; otherwise it shows the top 10 and a misleading large "Others" bar. Make the chart tall enough
  for labels. (A bar chart can't colour each bar by verdict; use the verdict tally for that, or a sorted
  table with conditional formatting.) Filter it to the latest `report_date`.
- **Lift against age** (a milestone view from per_page alone): a scatter chart with dimension `slug`,
  X = `days_since_refresh`, Y = `net_impr_vs_site_pct`. Shows whether lift holds as pages age.
- **Cohort milestone line**: add `milestone_curve.csv` as a second source (same file-picker step as #1):
  dimension `milestone_days`, metrics `net_impr_lift_pts`, `cohort_impr_delta_pct` and
  `site_impr_delta_pct`.

**4. Name the report** (click the title). Looker Studio saves automatically.

## Neutral default layout

Use the client's own dashboard template if they have one. Otherwise: one page; a header row with the report
date and the verdict counts; the cohort milestone line across the top; the per-page bar (or sorted table)
below it; the lift-against-age scatter at the bottom; a date or `report_date` filter control. Plain
greys with one accent colour, and the verdict colours from the workbook if you colour a table.

## Remaining pitfalls

- **Slow rendering**: the editor often times out on screenshots. Retry once; menus can appear before their
  text renders (wait, then act).
- **Stale element search**: an element search can show a previous view while a full page read shows the
  live dialog. Trust the full page read's references; reference-based clicks work better than coordinate
  clicks inside frames.
- **Google account split**: build the report in the Google account that owns the Search Console property
  (`/u/N/`), not the account the Drive or Gmail connectors use.
