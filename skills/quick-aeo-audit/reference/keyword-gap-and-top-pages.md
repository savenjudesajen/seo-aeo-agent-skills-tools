# Keyword gap and competitor top pages

Use the API of your SEO suite if it has units. If it returns a "not enough API
units" notice, stop retrying, tell the user the account owner must allocate
units, and get the same data from the web UI export instead. The click-paths
below are for Semrush; Ahrefs (Content Gap, Top Pages) works the same way.

## Check for existing exports first

Users often export some reports themselves before asking. Before driving any UI,
ask the user (or check the folder they point you to) for recent keyword-gap and
top-pages exports, and read those instead of re-exporting. Semrush names them
`gap.keywords_<timestamp>.xlsx` and `<domain>-organic.PagesV3-<db>-<timestamp>.xlsx`.

## Keyword gap (client vs competitors)

1. Open the Keyword Gap tool with the client domain in the first row and the
   right country database. Competitor rows passed as URL parameters often do not
   populate: enter them by hand. Take a screenshot first to confirm the user is
   logged in.
2. Click the "Add domain" field, type competitor 1, then dismiss the
   autocomplete by clicking a neutral area. The typed value holds; you do not
   need to pick a suggestion.
3. Add rows for competitors 2 and 3 and fill them.
4. Click "Compare".
5. In the keyword details table for the client, open the "Untapped" tab
   (keywords at least one competitor ranks for and the client does not). Note
   the untapped count and the per-domain keyword overlap totals.
6. Export: confirm the export covers all rows (not just the visible page) and
   choose Excel.
7. Ask the user for the downloaded file (or for access to the folder it landed
   in) and read it with openpyxl.

Typical columns: Keyword, Intents, Volume, Keyword Difficulty, CPC, Competition
Density, the client's position, each competitor's position, the ranking URLs,
Results.

Bucket the untapped keywords by non-brand THEME (the sub-topics of the
category). DROP competitor brand and navigational terms (`gotchas.md` #11). Sum volume per
theme: the theme totals are the addressable content gap and feed the
keyword-gap chart.

## Competitor top pages

1. Open the Organic Research "Pages" (top pages) report for one competitor
   domain, same country database.
2. Export to Excel.
3. Read the columns: URL, Traffic %, Number of Keywords, Traffic, Primary
   Intent, and, where the export has them, the AI-citation columns ("Answer
   Engines" = which AI engines cite the page; "LLM Prompts" = how many AI
   prompts cite it). Those AI columns are free per-page citation data; use them.
4. Compute the Pareto: the share of the competitor's organic traffic held by
   its top 5 pages, and the primary intent of each.
5. Classify those pages: navigational (home, sign-in, account or app pages) or
   category content (guides, comparisons, solution pages). If most of the
   traffic is navigational, the competitor's authority comes from its brand
   rather than its content, and the category content space is still open. If
   it is category content, name the page types the client would have to beat.

## Without an SEO-suite export

When no Keyword Gap or Top Pages export is reachable (no account, no API units
and no browser session to drive the UI), build the keyword gap from live search
results instead:

1. Take the category keywords from Phase 2 (solution, comparison and
   buyer-scenario terms; not the definitional umbrella terms).
2. Pull Google's top 20 organic results for each one, in the client's country,
   from any SERP API or the Unilytics MCP: `aeo_serp_urls` (`top_n` 20; Google
   US only) or `serp_results` (any country, by `location_code`). A fetch can take
   a few minutes: a result marked pending is not a result, so call again until it
   is complete. A result marked partial, or with results dropped, is incomplete:
   pull it again, and if it stays incomplete, leave that keyword out of the gap
   and say so on the method slide.
3. A keyword is in the gap when the client's domain is not in its complete top 20. For
   each one, note who ranks: a competitor's own page, a third-party list or
   comparison, or a forum, video or social post.
4. Bucket the gap keywords by non-brand theme and sum their monthly volume from
   Phase 2, exactly as with an export. The method slide says the gap is measured
   against Google's top 20 for N keywords, not against a suite's full keyword
   database, so the totals are smaller than an export's.

The share of the top 20s that are third-party lists is often the most useful
number here: it tells the client that the route into AI answers runs through
other people's pages.

Competitor top pages has no substitute: search results show who ranks for your
keywords, not where a competitor's traffic comes from. Leave the optional top
pages slide out and tell the reviewer, in chat, that it needs an export.

## When you drive the UI with a browser-automation tool

- Pages re-render and zoom can reset between clicks, which shifts coordinates.
  Take a screenshot before each click sequence.
- Batch predictable multi-step sequences into one call where your tool allows
  it.
- If a screenshot times out ("renderer may be frozen"), wait about 2 seconds and
  retry the screenshot on its own before doing anything else.
