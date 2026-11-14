# Browser-run pull (mode C)

Contents: How to run it · One-time credential store (the user runs this, not the agent) · Helper block · If requests are blocked

Use this when your agent's sandbox cannot reach Google's API hosts but a connected, signed-in browser can.
From a `search.google.com` tab, an in-page `fetch` to the token endpoint and the Search Analytics endpoint
works and the JSON is readable (Google's APIs allow cross-origin reads), so the whole flow is two fetches.

## How to run it

1. Open (or reuse) a browser tab on `https://search.google.com/search-console`. Any `search.google.com`
   page is a valid origin. If several browsers are connected, ask the user which one to use.
2. Paste the helper block below with your browser tool's "run JavaScript in page" action. Top-level `await`
   works and the last expression is what comes back; don't wrap calls in an async IIFE, or you get back a
   pending promise (`{}`).
3. Call `window.__gscQueries(...)` or `window.__gscQueriesBatch(...)` as in SKILL.md.
4. Read the rows back in slices. Many JavaScript actions truncate their return value at about 1 KB, so
   don't return the whole set at once:

   ```js
   JSON.stringify(window.__gscRows).slice(0, 1000)
   JSON.stringify(window.__gscRows).slice(1000, 2000)   // ...and so on
   ```

   Append each slice to a local `.json` file as you go, then convert to CSV.

## One-time credential store (the user runs this, not the agent)

On a `search.google.com` tab, the user opens the developer console and runs this with their own values, so
the secret never passes through the conversation. It persists in that browser profile.

```js
localStorage.setItem('gsc_creds', JSON.stringify({
  client_id: 'YOUR_DESKTOP_OAUTH_CLIENT_ID',
  client_secret: 'YOUR_CLIENT_SECRET',
  refresh_token: 'YOUR_REFRESH_TOKEN'
}));
```

`localStorage` is plain text in that browser profile: anything that can run script on `search.google.com`
there (including browser extensions with access to the site) can read it. Use a browser profile you trust,
keep the OAuth client limited to the `webmasters.readonly` scope, and when the pull is done the user clears
it from the same console:

```js
localStorage.removeItem('gsc_creds'); delete window.__gsc_tok;
```

To revoke the refresh token itself, remove the app's access at `myaccount.google.com/permissions`.

## Helper block

Security: the credentials and access token stay in page memory. Never return, print or log
`localStorage.gsc_creds`, `window.__gsc_tok` or any `Authorization` header. The helpers return only rows.

```js
// Token exchange: refresh token -> access token, cached on window.__gsc_tok.
// Returns true to the caller, never the token itself.
window.__gscToken = async function () {
  if (window.__gsc_tok && window.__gsc_tok.exp > Date.now() + 60000) return true;
  const c = JSON.parse(localStorage.getItem('gsc_creds') || '{}');
  if (!c.refresh_token) throw new Error('No gsc_creds in localStorage: run the one-time credential store first.');
  const body = new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: c.refresh_token,
    client_id: c.client_id,
    client_secret: c.client_secret || ''
  });
  const r = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString()
  });
  const j = await r.json();
  if (!j.access_token) throw new Error('token exchange failed: ' + (j.error || r.status) + ' ' + (j.error_description || ''));
  window.__gsc_tok = { v: j.access_token, exp: Date.now() + (j.expires_in || 3600) * 1000 };
  return true;
};

// Queries for one page (or the whole property if pageUrl is empty), paging with startRow.
//   siteUrl   : 'sc-domain:example.com' or 'https://www.example.com/' (un-encoded)
//   pageUrl   : full page URL, or a path fragment with pageOperator 'contains'
//   startDate, endDate : 'YYYY-MM-DD'
//   opts      : { rowLimit=1000, pageOperator='equals', dimensions=['query'], dataState='final', searchType }
// Full rows land on window.__gscRows; the return value is a compact summary.
window.__gscQueries = async function (siteUrl, pageUrl, startDate, endDate, opts) {
  opts = opts || {};
  await window.__gscToken();
  const dims = opts.dimensions || ['query'];
  const limit = Math.min(opts.rowLimit || 1000, 25000);
  const url = 'https://www.googleapis.com/webmasters/v3/sites/' +
              encodeURIComponent(siteUrl) + '/searchAnalytics/query';
  const rows = [];
  for (let startRow = 0; ; startRow += limit) {
    const body = { startDate, endDate, dimensions: dims, rowLimit: limit, startRow,
                   dataState: opts.dataState || 'final' };
    if (pageUrl) body.dimensionFilterGroups = [{ groupType: 'and', filters: [
      { dimension: 'page', operator: opts.pageOperator || 'equals', expression: pageUrl }] }];
    if (opts.searchType) body.type = opts.searchType;
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + window.__gsc_tok.v },
      body: JSON.stringify(body)
    });
    const j = await r.json();
    if (j.error) throw new Error('query failed: ' + j.error.code + ' ' + j.error.message);
    const batch = j.rows || [];
    for (const x of batch) {
      const row = { page: pageUrl || '(whole property)' };
      dims.forEach((d, i) => { row[d] = x.keys[i]; });
      row.clicks = x.clicks; row.impressions = x.impressions;
      row.ctr = +(x.ctr * 100).toFixed(2); row.position = +x.position.toFixed(1);
      rows.push(row);
    }
    if (batch.length < limit) break;
    await new Promise(res => setTimeout(res, 250));
  }
  window.__gscRows = rows;
  return { site: siteUrl, page: pageUrl || '(whole property)', dateRange: startDate + '..' + endDate,
           count: rows.length, top: rows.slice(0, 20) };
};

// Several pages in one run, 250 ms apart. Full sets land on window.__gscBatch[pageUrl];
// the return value maps each page to its row count or its error.
window.__gscBatch = {};
window.__gscQueriesBatch = async function (siteUrl, pageUrls, startDate, endDate, opts) {
  for (const p of pageUrls) {
    try { await window.__gscQueries(siteUrl, p, startDate, endDate, opts); window.__gscBatch[p] = window.__gscRows; }
    catch (e) { window.__gscBatch[p] = { error: String(e) }; }
    await new Promise(res => setTimeout(res, 250));
  }
  return Object.fromEntries(Object.entries(window.__gscBatch)
    .map(([k, v]) => [k, Array.isArray(v) ? v.length : v]));
};
```

Read a batch back per page the same way:
`JSON.stringify(window.__gscBatch['https://example.com/some/page']).slice(0, 1000)`.

## If requests are blocked

Some browser-automation tools block page requests that carry an `Authorization` header. Re-run the block
once. If it still fails, open the Search Console UI deep link
`https://search.google.com/search-console/performance/search-analytics?resource_id=<property>&breakdown=query&page=!<URL>`
(URL-encode both values) and read the rendered Queries table, or switch to mode A (connector or export).
