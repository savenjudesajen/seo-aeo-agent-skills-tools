# Keyword cannibalization (phase 3, on the cleaned URL list)

Contents: 1. Data (stop and flag if missing) · 2. Noise filter · 3. Metrics (`data/cannibalization_pairs.py`; starting defaults, calibrate per site) · 4. Decide each High and Medium pair (by hand) · 5. Patterns to look for across the site · 6. The cannibalization pairs workbook · 7. Run order

Similarity asks whether two of the site's pages read alike. Cannibalization asks whether Google shows two
of the site's pages for the same searches. They catch different problems, so this phase runs after
pruning and the page value check, on the cleaned URL list, and before internal linking. Internal linking
needs it: the anchor split it produces tells the linking work which page owns which wording.
- Similar text, few shared queries: Google already treats the pages as different jobs. Most
  high-similarity pairs in the review band stay separate after an intent read.
- Shared queries, different text: the case similarity misses. Offer pages and articles, a review article
  and a competitor page about the same rival, variants of one page per platform or city.

## 1. Data (stop and flag if missing)

- **Preferred: the Search Console bulk export in BigQuery** (`searchdata_url_impression`). Run the SQL in
  `data/sql/` (BigQuery console, CLI or API) and download the results as CSV (console downloads are
  size-capped, so aggregate in BigQuery):
  - `query_by_page.sql`: query x page totals for the window.
  - `weekly_rotation_summary.sql`: one row per contested query with the number of times the site's top
    URL changed. Weekly rows for every contested pair get very large, so the rotation is computed in
    BigQuery.
  - `page_search_totals.sql` and `ga4_sessions_by_channel.sql`: for the page value check.
- `sum_position` in the bulk export is zero-based: average position is `sum_position / impressions + 1`.
- Without the export: the Search Console API at query and page level, or your own Search Console
  connector. For a short list, the per-page Queries export in the Search Console UI is the same source.
  Missing query-level data is a stop-and-flag; page-level clicks are no substitute.
- Window: the longest the export holds, up to 16 months. Note in Method how many days each recent merge
  has had.
- Map the data onto the cleaned list: apply the redirect file (old path to its final target, skipping
  self-redirects from case or trailing-slash variants) and drop URLs that are no longer live and
  indexable.
- Per-URL backlinks: a backlink tool's per-page export. Word count: the live page with navigation, header
  and footer removed.

## 2. Noise filter

Rank trackers and AI-prompt monitors fill Search Console with long synthetic queries. Brand queries,
queries over eight words and queries with operators can hold a large share of impressions.
- Brand pattern with misspellings and spacing variants. For a brand called ExampleCo:
  `example ?co|exampel ?co|examplco|exmaple ?co`. Record the pattern in Method.
- Drop queries longer than eight words, and queries with quotes, `site:`, `-site` or `%`.
- Without the filter, many flagged pairs rest on a single machine-written query (a long question naming
  some unrelated company, for example) that no person searched.

## 3. Metrics (`data/cannibalization_pairs.py`; starting defaults, calibrate per site)

- **Shared query** for a pair: both URLs have 10+ impressions on it, both average position 20 or better,
  and the other page (the one that is not the owner) holds 20% or more of the site's impressions on it.
- **Query overlap %**: the other page's impressions on shared queries divided by its non-branded
  impressions.
- **Rotating query**: the site's top URL for the query changed three or more times across the weeks.
- **Severity**:
  - High: overlap 30%+ with 2+ shared queries and a contested query of 100+ impressions or a rotating
    query.
  - Medium: overlap 10 to 29% on the same terms, or 3+ rotating queries at any overlap. The rotation rule
    catches large pages whose overlap looks small: a big pillar can swap weekly with a sibling on many
    shared queries while its overlap stays in single digits.
  - Low: the rest.
- **Owner pick**: the page map first; then a page typed Offer or Campaign landing over supporting
  content on the same query; then most clicks, impressions and position. Page types are labels you
  assign (`--page-types`, list in `sheet-columns.md`); untyped pages are Home for `/`, Article under an
  `--article-prefix` folder, and Other for the rest. Untyped pages never get the buying-page preference:
  the homepage and listing pages otherwise take ownership of non-brand queries.
- **Text similarity** on the text scale: pages read alike at 0.30 and above. The 0.90 threshold belongs to
  embedding scores.

## 4. Decide each High and Medium pair (by hand)

1. **Read both live pages**: title, H1, H2 list, word count, meta description.
2. **Check the results page for the top shared query** (Google, in the site's main market). It says what
   kind of page Google wants for it: guides and definitions, tool lists, vendor pages or service pages.
   It also gives today's positions, which can reverse the window average (a page that averaged in the
   teens can rank top 5 today while the assumed owner has dropped to page two).
3. **Pick the owner** from intent and data. Name a different owner from the script's pick when intent
   says so, and give the reason. Examples: a broad buyer's guide owns the head term over narrower how-to
   pages, and a dedicated competitor page owns "CompetitorA pricing" over a review article that
   mentions it.
4. **Choose the Resolution**:
   - **Merge into owner**: the pages read alike (0.30+ text, or a confirmed same task) and share queries.
     Merge first, then 301 to the owner (`merge-execution.md`). Give the Redirect target.
   - **Re-target**: refresh the other page. Take the shared query out of its title, H1 and leading H2s,
     lead with its own angle, and link to the owner with the query as anchor. Write the anchor split.
   - **Split anchors**: different intent or small volume; both pages stay as they are. Write the anchor
     split: which wording links to which page.
   - **Wait**: under 6 months old, or a merge with under four weeks of data. Give the Recheck date.
5. **Never merge a buying page (Offer, Campaign landing) into supporting content.** An article that
   outranks the buying page is re-targeted to support it.
6. **Positioning calls go back to the site owner.** When the shared term is one the offer pages no
   longer use, flag it as a positioning question.
7. Every Reason gives the top shared query, both positions, the overlap and the swaps, then the
   resolution.

## 5. Patterns to look for across the site

- **Entity twins across folders**: two pages about the same competitor in different sections
  (`/blog/competitora-review` and `/competitors/competitora`). Often neither ranks well for the
  competitor's name because they split it.
- **Variants**: one page or template written per platform, city or integration, titles differing only in
  that word.
- **Help or FAQ answers against the long guide** on the same question.
- **Hubs ranking for an item's query**: a listing page swapping with the item page.
- **Off-site copies**: search the exact title of each pillar. A syndicated copy (LinkedIn, Medium, a
  partner blog) can outrank the original; ask for a canonical or a link back.
- **Merge survivors**: after a merge, check whether Google moved the merged page's head term to a sibling
  page and not to the survivor. If it did, the sibling may be the better owner for that term.

## 6. The cannibalization pairs workbook

Use the client's own format if they have one and map the fields onto it; otherwise the default layout in
`sheet-columns.md` (Cannibalization pairs, Query evidence, Method), which the gate reads.
- Cannibalization pairs: one row per pair (Pair ID, Severity, Owner and Other URL with their page types,
  top shared query, pair metrics, Resolution, Redirect target, Anchor split, Recheck date, Reason,
  Source).
- Query evidence: every query behind a pair, one row per query and ranking URL, sorted by total
  impressions.
- Method: scope, window, query filter and brand pattern, the shared-query and severity definitions, owner
  rule, page-type labels used, and related fixes found along the way (redirects pointing at hubs,
  off-site copies).
- When filling a client's existing spreadsheet, clear its sample hyperlinks before writing (see the
  gotcha in SKILL.md) and link every URL cell.

## 7. Run order

1. Pull the four SQL outputs for the same window. Map them onto the cleaned list.
2. Compute text similarity for every pair that shares a query (`similarity-grouping-and-merge-check.md`
   section 2).
3. Run `python data/cannibalization_pairs.py qp.csv out --brand "<pattern>" --rotation rot.csv --live
   live.txt --redirects rules.csv --page-types types.tsv [--article-prefix /blog/] --similarity sim.tsv
   [--primary pagemap.tsv]`.
4. For each High and Medium pair: live read, results-page check, owner, Resolution, anchor split,
   Reason.
5. Recompute every number quoted in a Reason from the pair metrics before building. A Reason written from
   memory fails this check more often than it passes.
6. Build the workbook. Run `python data/verify_audit_workbook.py <workbook>`; on a workbook without the
   audit sheets it checks only the Merge candidates and Cannibalization pairs sheets.
7. Hand the anchor splits to the internal linking work.
