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

## When you drive the UI with a browser-automation tool

- Pages re-render and zoom can reset between clicks, which shifts coordinates.
  Take a screenshot before each click sequence.
- Batch predictable multi-step sequences into one call where your tool allows
  it.
- If a screenshot times out ("renderer may be frozen"), wait about 2 seconds and
  retry the screenshot on its own before doing anything else.
