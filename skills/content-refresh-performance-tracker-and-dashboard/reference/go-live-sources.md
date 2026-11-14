# Phase 1 detail: where the go-live / refresh dates come from

Each page's refresh date **R** anchors its whole measurement. The source differs from site to site, so
**ask the user first**, then extract `{url, refresh_date}` for every refreshed page and group pages by
`refresh_date` into **cohorts** (pages sharing an R share one POST/PRE window, so one pull covers the
cohort).

## Source A: a refresh-tracking sheet (most reliable when it exists)

A workbook the team maintains with a **refresh date** column, and often a notes column where the refresh is
also written as text. This is the *intended* refresh date: prefer it over a CMS `modified` date.

- Read it robustly: download the file as .xlsx and open it with `openpyxl` (`data_only=True`). A
  natural-language read of a Drive file can misalign rows that start with empty cells, and a public CSV
  export URL is often blocked by credentialed-fetch guards. If the user pastes the sheet into chat, use that.
- Record the URL column, the refresh-date column, the notes column and the first data row in the site's
  `config.json` (`go_live_source`), so weekly runs read the same cells.
- When the date cell is empty but the notes hold a dated refresh entry, backfill R from the notes and mark
  the row so the user can confirm it.
- Only count rows that describe a substantive refresh; skip rows marked as planned, in progress or minor
  edits if the sheet distinguishes them.

## Source B: the CMS (WordPress and similar)

- WordPress REST: `GET {origin}/wp-json/wp/v2/posts?slug={slug}&_fields=slug,modified,modified_gmt`
  (use `/wp-json/wp/v2/pages` for pages). If you fetch from a browser, do it from a no-query page on the
  same origin (for example `{origin}/wp-json/`) with credentials omitted.
- **Caveat:** `modified` changes on ANY edit (a typo fix, a plugin re-save), not only a real content refresh,
  so it over-reports refreshes. If a tracking sheet exists, use the sheet; use `modified` only to fill gaps
  or when no sheet exists, and say so in the README sheet.

## Source C: sitemap `<lastmod>`

- Fetch `sitemap.xml` (and its sub-sitemaps) and parse `<lastmod>` per `<loc>`. Coarse, and it shares the
  `modified` caveat, but good for a whole-site first pass when nothing else exists.

## Source D: a manual list

- The user supplies `{url, date}` pairs (a paste or a CSV). Normalise URLs (scheme, host, trailing slash)
  to match how Search Console reports them, and proceed.

## Output of Phase 1

A list of `{url, slug, section, refresh_date}` for every refreshed page, plus a `cohort` label per distinct
`refresh_date`. No dated list → do not start Phase 2.
