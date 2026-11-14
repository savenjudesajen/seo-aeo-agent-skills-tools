# Looker Studio build gotchas - read before touching charts

Each of these pushes you off Looker Studio's default behaviour and costs time if you meet it
mid-build. They apply to a blank report and to a duplicated template alike.

## 1. Daily spikes / zeros on a chart that should be monthly
**Symptom:** the trend line or actions column shows a point per DAY, with 0 on every day
that isn't the 1st of a month; the x-axis reads "Jan 1", "Feb 1"...
**Cause:** the date dimension is at Day granularity.
**Fix (per chart):** select the chart via its y-axis (not a bar) -> in Setup, click the
dimension chip's **type / calendar icon** -> **Data type -> Date & Time -> Year Month**.
The chip then reads `month (Year Month)` and the points collapse to one per month.
If the chart goes black right after, it is a stale render: **reload the page**.

## 2. Months out of chronological order (Aug, Apr, Jul, May...)
**Cause:** bar and column charts default to sorting by the METRIC, not by month.
**Fix:** Setup -> **Sort** -> set the sort field to the **month** field, **Ascending**.
It now reads oldest -> newest left to right. (Descending reverses it.)

## 3. Scorecards read "No data" / "vs Previous Period"
**Cause:** the tile has a comparison date range but the data covers only ONE period, so
there is no prior period to compare and the tile renders "No data".
**Fix:** select each scorecard -> Style tab -> **Comparison date range = None**. Also delete
any orphaned "vs Previous Period" text label a template ships with.

## 4. A single click blanks / blacks every chart
**Cause:** clicking a data point (bar, line point, slice) in edit OR view mode creates a
**cross-filter** that filters the whole page to that one value or day.
**Fix:** press the report **Reset** button (top of the canvas). To SELECT a chart for editing
without triggering a cross-filter, click its **y-axis / empty plot area** or use the
**hover pencil**, never a data element.

## 5. Deleting the wrong thing removes the whole page (worst gotcha)
Some templates stack invisible decorative image components on top of tiles and text; they
intercept clicks. You have to delete those overlays to reach the real component, BUT:
- If the right panel header says **"Group properties"** and the selection spans the page,
  the ENTIRE page is selected as one group. **Pressing Delete removes everything on it.**
- Only press Delete when the panel shows a single component's properties (e.g.
  "Image properties").
- **Recovery:** File -> Version history -> See version history -> pick the last good
  timestamp -> Restore. Then reload.

## 6. The Excel-upload data source rejects programmatic file drops
The embedded Excel connector's dropzone (framework-controlled) ignores synthetic
drop/change events (`isTrusted` is false). To swap data: open **Edit connection**, push the
file into the real file `<input>` with the automation tool's file-upload action (by element
reference), then reload the report, OR have the USER click the native "Upload File" and pick
the file you handed them. Confirm the swap by watching a KPI tile jump to the full total.

## 7. Changing a field's data type blanks dependent charts
After changing `month` to Year Month (or editing a calculated field), charts may render
black until the cache refreshes. Reload the page once; the data is fine.

## 8. Filters must carry across pages
When you add date-range / State / City / Brand controls, set them to apply report-wide (or
duplicate them on each page) so Page 2 respects the same selection as Page 1.
