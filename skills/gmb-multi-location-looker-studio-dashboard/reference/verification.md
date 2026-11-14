# Verification procedure (the most important step)

Contents: Leg A - Sheet internal + vs raw export (measured) · Leg B - Sheet vs dashboard (to the digit) · Leg C - Sheet vs the LIVE GBP console (the real ground truth) · Leg D - Filters (test them, don't assume) · When no Python runtime is available

A Business Profile dashboard is only "done" when its numbers are proven: the sheet
reconciles internally, it matches the dashboard to the digit, and it matches the LIVE
Google Business Profile console. Then the filters are tested, not assumed. Run every leg.

The worked numbers below are arbitrary: **ClientA**, a fictional 9-location pet-grooming
chain in made-up towns across three made-up regions (XA, XB, XC), with six months of data
(October to March). They only show what each check looks like; the values are round on
purpose.

---

## Leg A - Sheet internal + vs raw export (measured)
1. Run the gate: `python3 data/verify_totals.py path/to/long.csv`.
   It re-derives every row (impressions = the 4 view columns; interactions = calls +
   directions + website_clicks, plus messages + bookings if those columns exist), flags any
   mismatch, negative or non-numeric value, flags any location missing a month, and prints
   per-month, per-state and grand totals + engagement rate. Exit code 1 = do NOT ship.
2. Open the raw monthly export and spot-check at least 5 cells by hand across a large
   location, a mid one, and a near-zero or new one (e.g. a location that was 0 in month 1).
   Every picked cell must be exact. Watch for the comma-quoting grid shift (SKILL.md
   Section 4).

## Leg B - Sheet vs dashboard (to the digit)
- Each KPI tile (Impressions, Interactions, Engagement rate, Locations) must equal the
  script's grand totals exactly.
- The trend chart's per-month data labels must equal the script's per-month totals.
- The state bar must equal the script's per-state totals.
- If ANY tile is off, the connected source is stale or partial. The classic failure: only
  the most recent month's rows got uploaded, so the tile shows one month, not all of them.
  Re-upload the full long file, reload the report, and confirm the tile jumps to the full
  total.

## Leg C - Sheet vs the LIVE GBP console (the real ground truth)
This is what clients actually mean by "is it correct?". Check at least 2 locations: one
large, one small.

1. While signed into the account that manages the profiles (note the `authuser=<N>` /
   `u/<N>` index), search Google for the exact profile name as it appears in the location
   group (e.g. `Ashvale Store, Unit 4`). The manager card ("You manage this Business Profile" / "View profile") appears.
2. **Impressions cross-check (free, instant):** the card shows "**N monthly views**". It
   should equal your latest full-month `impressions` for that location. If it doesn't match
   any single month, note the window the card is using before you treat it as a mismatch.
3. Click **Performance**. The time period defaults to the trailing ~6 months (Standing
   fact 2), so it will not show months older than that.
4. On the **"Business Profile interactions"** line, **hover each monthly point** and read the
   exact tooltip (e.g. "14 - Feb"). Compare it to your `interactions` for that
   location-month. Tooltips are the only exact read: the chart has no accessible data table
   or aria labels.
5. **Reconcile the period total.** The panel's big number covers the whole trailing window,
   including a PARTIAL current month. So `panel total ~= your sum for the full months in the
   window + a partial current month`.
6. **Messages/Bookings check (Standing fact 6).** If the hovered GBP interactions read HIGHER
   than your `interactions`, the location has messages/bookings you dropped: add those columns
   back to the model and re-run the gate. If they match exactly, messages + bookings = 0,
   confirmed.

### Worked example (fictional ClientA)
| Location | Metric | Sheet / dashboard | Live GBP console |
|---|---|---|---|
| Ashvale (small, XB) | Nov interactions | 9 | 9 |
| Ashvale | Feb interactions | 14 | 14 |
| Ashvale | Mar impressions | 310 | 310 ("monthly views") |
| Corrin Bay (large, XA) | Dec interactions | 52 | 52 |
| Corrin Bay | Mar interactions | 47 | 47 |
| Corrin Bay | Mar impressions | 820 | 820 ("monthly views") |

Period total for Corrin Bay (panel window Nov-Apr): panel 251 = sheet Nov-Mar 233
(44 + 52 + 49 + 41 + 47) + ~18 for the partial current month (April).

Gate totals: impressions 21,000; interactions 1,575; engagement 7.50%; 9 locations.
Per month impressions: Oct 3,000 / Nov 3,400 / Dec 4,100 / Jan 3,800 / Feb 3,200 /
Mar 3,500 (sum = 21,000). Per month interactions: Oct 240 / Nov 260 / Dec 300 / Jan 290 /
Feb 250 / Mar 235 (sum = 1,575). Per region: XA 9,800 (4 locations) / XB 7,000 (3) /
XC 4,200 (2).
In a real run, record which months matched the raw export cell-for-cell and which (usually
the derived last month) were matched against the live console instead.

## Leg D - Filters (test them, don't assume)
Do this in **View** mode (no risk of editing components).
1. **Date-range delta test (the definitive one).** Note the full-range impressions tile
   (ClientA: 21,000). Open the date control, move the START forward or the END back by one
   month, Apply. The tile must drop by exactly that month's known total (ClientA, start moved
   forward: 21,000 -> 18,000 = minus October's 3,000; interactions 1,575 -> 1,335 = minus
   October's 240). Then set it back to the full range.
2. **Default check.** Reload the /view URL fresh. The date control must open on the FULL data
   range, not a leftover sub-range. If it opens narrow, fix the control's default date range
   in edit mode (Auto / all available dates).
3. **State / City list controls.** Open the dropdown: each value shows its own metric total
   (ClientA city dropdown: Dunmere 2.6K = its six-month impressions 2,640). Those must match
   the sheet. Pick one value and confirm the tiles and the Locations count update (e.g.
   XC -> 4,200 impressions, 2 locations). Then clear it.
4. **Cross-filter hygiene.** If a chart click blanked the page, that's an accidental
   cross-filter: press the report **Reset** button; the page should return to full totals.

## When no Python runtime is available
The reconciliation is still mandatory, so do it by hand: sum the impressions column per month,
confirm the monthly subtotals add up to the grand total, and confirm each equals the
trend-chart label. Also count rows per location to confirm no month is missing. The
arithmetic is additive, so hand summation is exact, just slower.
