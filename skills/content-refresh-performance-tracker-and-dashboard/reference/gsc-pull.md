# Pulling the since-refresh search data (routes and pitfalls)

First-party Search Console data: use your own Search Console connector or API export when you have one.
The two routes below are for when you need to pull it yourself.

## Route A (preferred): the Search Analytics API, as in `gsc-url-queries`

Use the official Search Analytics API (`searchanalytics.query`) with a `page` filter, following the
`gsc-url-queries` skill. If your sandbox cannot reach `googleapis.com`, a browser session signed in to the
right Google account can call the same API (it is CORS-readable), which is what that skill describes. Each
call returns in seconds and needs no UI clicking.

- Loop the POST and PRE date ranges (and each milestone window) per page.
- Sum clicks and impressions; take the impression-weighted average position.
- Run the same windows with no page filter for the sitewide control.
- One cohort (pages sharing an R) shares its windows, so batch the cohort's URLs per window.

## Route B (fallback): the Search Console UI by direct URL navigation (no click flow)

Navigate straight to a fully specified Performance URL (this also resets a stuck page):

```
https://search.google.com/u/{N}/search-console/performance/search-analytics?resource_id={ENC_PROPERTY}
  &start_date=YYYYMMDD&end_date=YYYYMMDD&compare_start_date=YYYYMMDD&compare_end_date=YYYYMMDD
  &metrics=CLICKS%2CIMPRESSIONS%2CCTR%2CPOSITION&page=~{ENC_REGEX}&breakdown=page
```

- `page=~` takes a **URL-encoded regex**: an OR-chain of the cohort's slugs (`|` = `%7C`, `/` = `%2F`,
  `?` = `%3F`, `$` = `%24`). Anchor short or ambiguous slugs with `/?$` (for example
  `keyword-b/?$`) so a short slug doesn't also match longer URLs that contain it.
- Omit `page=` to read the **sitewide control** for the same windows.
- Read the four metric cards (cohort aggregate: clicks, impressions, CTR, position, POST against PRE) from a
  screenshot, and the per-URL rows from the Pages tab table through the page's accessibility tree.
- Put the compare dates **in the URL**: the date params apply when the compare params are present; the
  date picker otherwise ignores date params on a cold load.

## Browser-automation pitfalls on Search Console

- Some browser-automation tools block running page JavaScript on URLs that carry a query string. On those
  pages, read with screenshots and the accessibility tree instead of page scripts.
- The page renderer can be slow: a screenshot may time out. **Retry once** before changing approach; the
  browser connection occasionally drops.
- An element search can return a stale accessibility tree (a previous view) while a full page read shows
  the live dialog. Trust the full page read for current element references.
- The Pages tab table sometimes drops a cell whose value is 0 or blank. Anchor on the impressions triplet
  (post, pre, difference) and compute the deltas yourself.
- **Google account index `/u/N/`**: the property (and Looker Studio) may belong to a different Google account
  than the Drive or Gmail connectors. Find the right `/u/N/` index and use it in the URL.
- **One browser only** for unattended runs: with two or more connected browsers, browser selection can
  stall the run. Treat that as a stop and report it.
