# The since-refresh delta method, milestones and verdicts (canonical)

Every performance call comes from a **clean since-refresh read** anchored to each page's own go-live date,
**never** from a dashboard's rolling comparison-window delta.

## Windows (per page, refresh date R)

- **L** = the last complete Search Console day = the latest date the date picker (or the API) allows,
  usually today minus 3 (this absorbs the 2–3 day reporting lag). Never assume today; confirm L.
- **n** = L − R (complete post-refresh days).
- **POST** = `[R+1 … L]` (fully after the refresh; excludes refresh day R).
- **PRE** = `[R−n … R−1]` (equal length n, immediately before the refresh).
- **Delta(metric)** = POST − PRE, per URL, for clicks, impressions, CTR and average position.
  **A negative average-position delta means the page improved.**
- Sum clicks and impressions over a window; average position is impression-weighted across days and URLs.

## Milestones (the normalised "days since refresh" curve)

Also capture cumulative windows from R at **+7 / +14 / +28 / +90** wherever `R + m ≤ L`:
POST = `[R+1 … R+m]`, PRE = `[R−m … R−1]`. Plot the metric against the milestone to see whether a lift
builds or decays. As pages age, weekly runs fill in the later milestones.

## Maturity gate

If **n < 7**, the page is **not eligible for a verdict** → label it **Maturing** and re-measure after about
R+10. Exclude it from winners, losers and rollback lists.

## Sitewide control (always)

Pull the same POST and PRE windows with **no page filter** → whole-property totals.
`net_impr_vs_site = page impressions delta % − sitewide impressions delta %` (positive = beat the site).
Pull it **per distinct window**: the sitewide change depends on window length and recency, so never reuse
one figure across windows.

## Verdict taxonomy (from the clean read only)

- **Winner**: impressions up (or fell far less than the site) AND rank flat or improved.
- **Holding**: impressions roughly in line with the site; rank mixed. Neither a clear win nor a loss.
- **Rank slipped**: impressions held against the site but average position clearly worse (watch).
- **Decliner (audit)**: impressions worse than the site AND rank worse. Content audit or rollback
  candidate, *only past the maturity gate*.
- **Demand-drop (rank held)**: impressions fell sharply but rank held or improved → query or SERP demand
  changed (for example an AI Overview now answers the query), NOT the content. Investigate demand; do
  **not** roll back.
- **Maturing** (n < 7) · **No data** (refreshed after L, or no impressions in either window).

The default thresholds in `data/build_tracker.py` (`classify`) turn these definitions into numbers. They are
heuristics: tune them per site, keep the order of the rules (demand-drop is tested before decliner), and
record any change in the workbook's README sheet so week-to-week verdicts stay comparable.

## Rollback rule (strict)

Flag a URL for rollback or audit only if ALL of these hold:

1. it is past maturity (n ≥ 7);
2. on the clean read it is worse than its own pre-refresh baseline on BOTH impressions (delta < 0) AND
   average position (delta > 0);
3. its decline is not explained by the sitewide control.

A page that is down on a dashboard's rolling window but flat or up on the clean read is NOT a rollback
candidate.
