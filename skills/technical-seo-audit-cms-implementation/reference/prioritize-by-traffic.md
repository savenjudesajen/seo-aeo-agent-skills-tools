# Prioritise which pages to fix first - by Search Console traffic

Every on-page item (metas, titles, H1s, title same as H1, image alt) has a long worklist, and traffic
is power-law: a few pages carry most of the value. **Order the worklist by Search Console impressions
and fix the highest-traffic pages first.** This is a reusable pre-step for any item.

## 1. Get the traffic data (two ways)

1. **Your own Search Console connector**, if one is connected for the site: pull page-level clicks
   and impressions for the longest window available (Search Console keeps 16 months).
2. **Search Console "Pages" export**: the user exports the Search results performance report. The
   `Pages` sheet has `Top pages | Clicks | Impressions | CTR | Position`. Note: **the UI export caps
   at the top 1,000 rows**, so anything not listed is the low-traffic tail. Read it with openpyxl or
   any spreadsheet library. (For more than 1,000 pages, the Search Console API returns more rows per
   request and can page through them.)

## 2. Join to the flagged set

- Normalise both sides to a path key: strip protocol and host, trailing slash, query string and
  fragment; lowercase.
- Map each flagged URL to its impressions. Not in the export: tail (low priority).
- Do the join outside the browser (Python with openpyxl or csv) whenever the flagged set is already
  on disk. It is cleaner and avoids the browser tool's output limits.

## 3. Pick the threshold and tiers

- "Important" = a defensible impressions cut that the user agrees with: for example the pages that
  together make up the top ~80% of impressions, the top N pages, or simply "present in the Search
  Console top 1,000". If the cut materially changes scope, confirm it with the user.
- Deeper is better for the top: bespoke, content-aware copy for the important tier; deterministic or
  templated fill for the tail, only if the user said the tail can be lighter.

## 4. Sequence

- Important tier first, with the highest-value treatment (content-aware alt, custom title/H1 splits,
  hand-written metas).
- Tail second, lighter (filename-derived alt, pattern titles), or handed to a bulk or developer pass.
- This keeps quality where it matters and pace on the rest.

## 5. Output-limit caveat (if joining inside the browser)

A path-to-impressions map for 1,000 URLs is tens of KB. Browser-automation tools often truncate
returns (around 1.5 KB) and redact URL-bearing strings, so you can't pull the flagged set out of the
page mid-run to join elsewhere. If you must join in the page, **inject** the map once (input
direction) and compute the join in the browser, returning only small counts or the list of important
post/node IDs. Prefer the outside-the-browser join whenever the data is already on disk.
