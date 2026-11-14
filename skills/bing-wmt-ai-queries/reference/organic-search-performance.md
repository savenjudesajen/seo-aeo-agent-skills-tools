# Harvesting classic organic queries from Bing Webmaster Tools Search Performance

Companion to the AI Performance method in SKILL.md. Same interception trick, a
different report. This is Bing's traditional web-search demand (not Copilot):
per-query Impressions, Clicks, CTR and average position, filterable to a single
URL. It is dense (dozens of queries per URL) where AI Performance is sparse, so
union the two for keyword research.

## Endpoints (all POST, same-origin, cookie + X-CSRF-Token auth)
- `/webmasters/api/searchperf/keyword/stats` -> query list: `{ KeywordTrafficStats[], TotalNumOfRecords, SiteUrl }`
- `/webmasters/api/searchperf/page/stats` -> page list: `{ PageTrafficStats[], TotalNumOfRecords, SiteUrl }`
- `/webmasters/api/searchperf/traffic/datestats` -> time series (Home dashboard tile)

## Field names (get these wrong and rows read as undefined)
- Query text is `Keyword` (not `Query`).
- Page URL is `Page` (not `PageUrl`). Note the AI pages list uses `PageUrl`; the classic one uses `Page`.
- Rows also carry `Impressions`, `Clicks`, `ClickThroughRate`, `AvgImpressionPosition`, plus trend labels `ImpressionsTrend` / `ClicksTrend` / `AvgImpressionPositionTrend` (Increasing | Decreasing | Constant) and `Unformatted*` numeric variants.
- Page rows carry an opaque `PageId`. The query list filters by this id, not by URL.

## The gotcha that wastes the most time: the route
The classic report lives at `/webmasters/searchperf` and you must arrive via
in-app navigation (Home -> "View complete report", or the left-nav "Search
Performance") so the single-page app mounts and fires `keyword/stats`. The URL
`/webmasters/searchperformance` renders an empty "No pages found" shell and never
fires a data call. Do not conclude "no data" from it. If unsure whether the
property has any classic data, load Home: the Search Performance tile fires
`traffic/datestats` and shows Total Clicks / Impressions.

## Procedure (per URL)
1. Sign in (human) and open Home or the Search Performance report as above.
2. Install the same fetch/XHR interception shim (Step 2 of `data/harvest.js`; it
   records every `/api/` call, which includes `searchperf/`). Enter the report so
   the app fires `keyword/stats`; capture one real request (headers borrowed by
   reference, never printed).
3. Resolve the target URL's PageId: POST `page/stats` (body below, `KeywordId: null`),
   paging until the row whose `Page` equals your URL is found or the whole page
   list (`TotalNumOfRecords`) has been read. Keep its `PageId` in-page only
   (it is blocked from being returned to the model; never print or return it).
   Report "URL not in page list" only after the full list was read.
4. POST `keyword/stats` with that `PageId`, paging until `TotalNumOfRecords`, to
   get every organic query for the page.
5. Read back in chunks (per Step 4 of SKILL.md); persist Keyword + metrics + trend.

## Request body
```
// keyword/stats (query list). page/stats is symmetric with KeywordId:null.
{
  SiteUrl:        "<verified property, e.g. https://blog.example.com/>",
  DateRange:      { BeginTimeStamp, EndTimeStamp },   // RFC1123, same as AI method
  PageId:         <opaque id from page/stats, or null for site-wide>,
  Pagination:     { PageNum: 1, PageSize: 250 },
  SortParameters: { SortField: "Impressions", SortOrder: "Desc" }
}
```

## Tested self-contained replay (paste in-page after a keyword/stats request is captured)
```js
(async () => {
  const rec = window.__cap.find(r => r.url.includes('searchperf/keyword/stats'));
  const hdrs = rec.headers;                 // borrowed by reference; never printed
  const base = JSON.parse(rec.body);
  const post = (u,b)=>fetch(u,{method:'POST',headers:hdrs,body:JSON.stringify(b),credentials:'same-origin'}).then(r=>r.json());
  const pageEp = rec.url.replace('keyword/stats','page/stats');
  const TARGET = "<full page URL>";
  const MAX_PAGES = 25;                     // safety cap; hitting it is reported, not hidden
  const sort = {SortField:'Impressions',SortOrder:'Desc'};

  // 1) Page through the page list until TARGET is found or the list is exhausted.
  let row = null, seen = 0, pageTotal = 0;
  for (let n = 1; n <= MAX_PAGES && !row; n++) {
    const pj = await post(pageEp, {...base, KeywordId:null, Page:'', Pagination:{PageNum:n,PageSize:400}, SortParameters:sort});
    const rows = pj.PageTrafficStats || [];
    pageTotal = pj.TotalNumOfRecords || 0;
    seen += rows.length;
    row = rows.find(p => (p.Page||'') === TARGET) || null;
    if (!rows.length || seen >= pageTotal) break;
  }
  if (!row) {
    window.__org = (seen >= pageTotal)
      ? {error:'URL not in page list', pagesRead: seen, total: pageTotal}
      : {error:'page cap hit before the URL was found; raise MAX_PAGES', pagesRead: seen, total: pageTotal};
    return;
  }

  // 2) Page through the query list for that PageId until TotalNumOfRecords.
  const queries = []; let qTotal = 0, capped = false;
  for (let k = 1; ; k++) {
    if (k > MAX_PAGES) { capped = true; break; }
    const qj = await post(rec.url, {...base, PageId: row.PageId, Page:'', Pagination:{PageNum:k,PageSize:250}, SortParameters:sort});
    const rows = qj.KeywordTrafficStats || [];
    qTotal = qj.TotalNumOfRecords || 0;
    queries.push(...rows.map(q => ({k:q.Keyword, i:q.Impressions, c:q.Clicks, ctr:q.ClickThroughRate, pos:q.AvgImpressionPosition, trend:q.ImpressionsTrend, posTrend:q.AvgImpressionPositionTrend})));
    if (!rows.length || queries.length >= qTotal) break;
  }

  window.__org = {
    page: {impr: row.Impressions, clicks: row.Clicks, ctr: row.ClickThroughRate, pos: row.AvgImpressionPosition, imprTrend: row.ImpressionsTrend, posTrend: row.AvgImpressionPositionTrend},
    total: qTotal, collected: queries.length, capped: capped,
    summedImpr: queries.reduce((s, q) => s + (Number(q.i) || 0), 0),   // compare with page.impr
    queries: queries
  };
})();
// then read window.__org.queries back in slices; never print headers or PageId.
// collected < total (or capped: true) means the pull is incomplete: say so.
```

## Reading the organic data
- Dense, not sparse. A single URL can return dozens of organic queries (vs 0-9 AI). Weight by Impressions; the long tail is mostly 1-impression variants, misspellings, non-English queries and occasional spam. Keep raw, flag spam, do not hand-curate away signal.
- Trend is the refresh signal. `ImpressionsTrend` / `AvgImpressionPositionTrend` = Decreasing on the target URL flags a page losing ground, which is exactly what a refresh should reverse.
- Sanity-check completeness. The sum of per-query Impressions should be close to the page row's Impressions (a few unattributed is normal). If it is far off, you paged short.
- Retention is about 6 months. Widen DateRange to the maximum useful window; older data ages out.

## Guardrails
Identical to the AI method: same-origin read-only `stats` calls only; headers, token and `PageId` borrowed by reference and never printed, logged or returned; sign-in stays human.
