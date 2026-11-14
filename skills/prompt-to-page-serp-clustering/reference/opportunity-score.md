# Opportunity Score, and the metric pull behind it

Step 9c. A page-level, 0–100 build-order ranking over the unified page universe. Runnable:
`data/opportunity_score.py`.

## Where the formula comes from

- **Base: Siege Media's KOB (Keyword Opposition to Benefit)**: traffic value divided by difficulty,
  higher is better, where traffic value = volume × CPC.
  <https://www.siegemedia.com/strategy/kob-analysis>
- **Shape: Minuttia's weighted-variable method**: weights sum to 100, score plotted 0–100, KD
  inversely proportional. <https://minuttia.com/keyword-selection/>

A reviewer asking for `(Volume / KD) × CPC` is asking for KOB. Say so and cite it rather than
presenting it as something invented for the engagement.

## The score

Aggregate from keyword to page:

- `KOB_page = SUM(volume × CPC) / volume-weighted mean KD`, KD floored at 5
- `Volume_page = SUM(volume)`
- `Trend_page` = volume-weighted mean of each keyword's trend ratio, where the ratio is the mean of the
  last six months of a 12-point monthly series over the mean of the first six, clamped to 0.5–2.0 and
  mapped so flat = 50

Default weights, summing to 100: **KOB 60, Volume 25, Trend 15.** Volume sits beside KOB so one
expensive keyword cannot carry a thin page.

**Impressions are an uplift of up to +15 on top, capped at 100, log-scaled against the highest page in
the set.** Not a weighted component. Every net-new page has zero impressions by definition and that is
the reason to build it, not a reason to rank it last. Impressions may raise a page's priority; they
must never lower it.

## The three rules

1. **Percentile rank, never log or min-max scaling.** `log1p(x)/log1p(max)` compresses the top of the
   set until a trend difference outweighs a many-fold difference in value, and a mid-size page can
   outrank the head page. Percentile rank is robust to the outlier and preserves order exactly.
2. **Never score an unobserved input as zero.** A large share of keywords can carry no CPC, especially
   for new or niche demand: the ad market has not priced them, which is not the same as no value. Zeroing
   them lets a tiny page outrank a large one. Where a page has no keyword carrying a CPC, redistribute
   the KOB points across the components that WERE observed, and report the coverage. The same logic is
   why impressions are an uplift.
3. **Pages with no keywords carry no score and say so in words** ("Prompt-only (no keyword data)"),
   never a blank and never a zero.

## State what it compares

The score ranks build order WITHIN one set. It is not a forecast and does not carry to another keyword
set, because percentile rank is relative to the pages in it. Put that on the methodology tab, and read
the score beside the reviewer's comments column, not instead of it.

## A 0.0 is the percentile floor, not a missing input

Percentile rank puts the lowest page at zero by construction. That is correct, and it is also the most
misreadable number in the deliverable: 0.0 reads as valueless when it means last in this set.

Distinguish the two cases in the basis text, and have your check distinguish them too:

- **0.0 because it is last**: say so ("the 0.0 is the percentile floor, not a missing input: this page
  has the lowest keyword volume in the set, so it ranks last by construction").
- **0.0 because an input was unobserved**: that is the bug rule 2 forbids and should fail the check.
  Test it as `score == 0 and volume > the set minimum`, not as `score == 0`, or the check fires on every
  correct run and gets switched off.

## Getting CPC and trend for a large set

Use a keyword tool's bulk overview (Semrush Bulk Keyword Overview, Ahrefs Keywords Explorer, or a
keyword API) for volume, KD, CPC and the 12-month series.

- **Prefer the CSV export or the API to the on-screen table.** Trend usually renders as a sparkline with
  no numbers; only the export carries the 12-point series (and SERP features).
- Respect the tool's batch size (often 100 keywords) and confirm each batch registered in full: a
  pasted list can register as a single keyword if separators are not recognised.

If you drive a keyword tool's web UI through browser automation instead of its API:

- **Keep each step in its own call** (clear, paste, analyze, read). Chaining them in one script can
  freeze the renderer and time out.
- **Verify the input holds the batch you just pasted before clicking analyze.** An async navigation
  from the previous batch can finish late and wipe the new one.
- **A browser-driver timeout does not mean the work failed.** Re-read state with a cheap call before
  retrying.
- **Menus toggle.** Open the export menu, confirm it is open, then choose CSV. Confirm the export
  file exists before re-exporting; if it seems absent, wait briefly and list the folder again.

## Refresh the whole metric set, not just the gap

Re-pulling a keyword set a month or a quarter later moves volume on a good share of rows. Scoring on
fresh CPC and stale volume from the same source is incoherent. Refresh page-level volumes on every
sheet that carries them, and regenerate any keyword or prompt list that prints volumes inline.

⛔ **Refresh the PRINTED ROW, not only the rollup.** Page totals can be rebuilt from a fresh pull while
many keyword rows still print last quarter's volume. Nothing fails, because each surface is internally
consistent; the workbook simply contradicts itself, and a reviewer reading a row next to its page total
finds the gap. After any re-pull, walk every sheet that prints a number and assert row-level equality
against the refreshed source, not just that totals add up.

⛔ **Keep the whole set on ONE metrics surface.** A tool's organic-research-by-URL report and its bulk
keyword overview are different indexes and can disagree noticeably on the same keyword. Whichever
surface priced the rest of the set prices the new rows, so a backfill harvested from URL reports still
needs a bulk-overview pass before scoring. Where a row comes back with no bulk data, carry the URL-report
figure and say so in the Source column rather than dropping the row or silently mixing sources.

URL reports often return no CPC, and many backfilled keywords have none in the bulk pull either. That is
rule 2 doing real work, not an edge case.
