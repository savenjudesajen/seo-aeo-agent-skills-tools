/* =============================================================================
 * Bing WMT AI Performance — harvest helpers
 * These are pasted into the page via the browser tool's JavaScript action,
 * one block at a time, while signed in to Bing WMT with the AI Performance
 * report open. They are confirmed-working; the header-by-reference handling is
 * load-bearing, so paste rather than retype.
 *
 * Block names match the steps in SKILL.md:
 *   Step 2  — interception shim (safe to re-run)
 *   Step 3a — inputs + replay helper (SITE_URL, BEGIN/END, FILTER)
 *   Step 3b — harvest functions (pages list, per-URL queries, batch)
 *   Step 4  — reading data back out
 *
 * Site-agnostic: nothing here is tied to a specific website. Set the four
 * inputs at the top of Step 3a and the same code harvests any property
 * verified in the signed-in Bing WMT account.
 *
 * Security: never print .headers from any capture. Print only .body / .url.
 * The anti-forgery token lives in these headers and must stay in-page.
 * ========================================================================== */


/* -----------------------------------------------------------------------------
 * Step 2 — Interception shim (idempotent).
 * Patches fetch + XHR so every /api/ call the Bing app makes is recorded into
 * window.__cap, including its request headers (which carry the anti-forgery
 * token). After running this, toggle "Pages" <-> "Grounding Queries" in the UI
 * so the app re-fires and the trap captures a real, fully-formed request.
 *
 * Re-running it (Maintenance in SKILL.md) only clears window.__cap: the
 * originals are kept on window and the patch is installed once, so nothing is
 * redeclared and fetch/XHR are never double-wrapped.
 * -------------------------------------------------------------------------- */
window.__cap = [];

if (!window.__capInstalled) {
  window.__capOrig = {
    fetch: window.fetch,
    open: XMLHttpRequest.prototype.open,
    send: XMLHttpRequest.prototype.send,
    setRequestHeader: XMLHttpRequest.prototype.setRequestHeader
  };

  // fetch()
  window.fetch = function (...a) {
    try {
      const u = typeof a[0] === 'string' ? a[0] : a[0].url;
      if (u.includes('/api/')) {
        window.__cap.push({ url: u, method: a[1] && a[1].method, body: a[1] && a[1].body, headers: a[1] && a[1].headers });
      }
    } catch (e) {}
    return window.__capOrig.fetch.apply(this, a);
  };

  // XMLHttpRequest
  XMLHttpRequest.prototype.open = function (m, u) { this.__u = u; this.__m = m; this.__h = {}; return window.__capOrig.open.apply(this, arguments); };
  XMLHttpRequest.prototype.setRequestHeader = function (k, v) { if (this.__h) this.__h[k] = v; return window.__capOrig.setRequestHeader.apply(this, arguments); };
  XMLHttpRequest.prototype.send = function (b) {
    if (this.__u && this.__u.includes('/api/')) window.__cap.push({ url: this.__u, method: this.__m, body: b, headers: this.__h });
    return window.__capOrig.send.apply(this, arguments);
  };

  window.__capInstalled = true;
}

// To inspect what got captured, print only bodies, never headers:
//   window.__cap.filter(c => c.url.includes('stats')).map(c => c.body)


/* -----------------------------------------------------------------------------
 * Step 3a — Inputs and replay helper.
 * Reuses a captured request's headers by reference (token never leaves the
 * browser) and lets you page through any URL / endpoint.
 *
 * SITE_URL:  the verified property as Bing stores it (often the www root),
 *            which is not necessarily the URL you're filtering queries for.
 * BEGIN/END: the date window in RFC1123 format; ISO 8601 fails.
 * FILTER:    URL substring for the pages list (goes in AIFilterKeyword, not
 *            Query). "" = every cited page under the property.
 * Stored on window, so re-pasting this block never redeclares anything.
 * -------------------------------------------------------------------------- */
window.__cfg = {
  SITE_URL: "https://www.example.com/",          // <-- set: verified property
  BEGIN:    "Mon, 01 Jan 2024 00:00:00 GMT",     // <-- set: RFC1123, not ISO (example only)
  END:      "Sun, 31 Mar 2024 00:00:00 GMT",     // <-- set: RFC1123, not ISO (example only)
  FILTER:   ""                                   // <-- set: e.g. "/guides/" or "blog.example.com"
};

if (!window.__cap.find(c => c.url.includes('aiperformance/') && c.headers)) {
  throw new Error('No captured request with headers yet — toggle a view in the UI, then re-run.');
}

window.__replay = async function (pageUrl, pageNum, pageSize, endpoint, extra) {
  // Use the newest capture, so a fresh one after Maintenance is picked up.
  const caps = window.__cap.filter(c => c.url.includes('aiperformance/') && c.headers);
  const cap = caps[caps.length - 1];
  if (!cap) return { status: 0, raw: 'no capture with headers; toggle a view and retry' };

  const cfg = window.__cfg;
  const body = Object.assign({
    SiteUrl: cfg.SITE_URL,
    DateRange: { BeginTimeStamp: cfg.BEGIN, EndTimeStamp: cfg.END },
    Pagination: { PageNum: pageNum || 1, PageSize: pageSize || 100 },
    SortParameters: { SortField: "Citations", SortOrder: "Desc" },
    AIFilterKeyword: "",   // domain / URL-substring filter — used for the pages list
    Query: "",
    Page: pageUrl || ""    // specific page URL — used for the queries list
  }, extra || {});

  const hdrs = Object.assign({}, cap.headers);   // reuse app's headers (token included)
  hdrs['content-type'] = 'application/json';

  const r = await fetch('/webmasters/api/aiperformance/' + (endpoint || 'searchqueries/stats'), {
    method: 'POST',
    headers: hdrs,
    body: JSON.stringify(body),
    credentials: 'include'
  });
  const t = await r.text();
  let j; try { j = JSON.parse(t); } catch (e) { return { status: r.status, raw: t.slice(0, 200) }; }
  return { status: r.status, data: j };
};


/* -----------------------------------------------------------------------------
 * Step 3b — Harvest functions. Paste after Step 3a, then call them.
 * Each one pages until TotalNumOfRecords, with a 12-page cap.
 * -------------------------------------------------------------------------- */

// (A) Domain-wide pages list — which pages Copilot cites, ranked by citations.
//     Note: the substring filter goes in AIFilterKeyword, not Query.
//     Defaults to window.__cfg.FILTER; pass a substring to override.
//     Usage: await window.__harvestPages()   or   await window.__harvestPages('/guides/')
window.__harvestPages = async function (filter) {
  const kw = (filter === undefined) ? window.__cfg.FILTER : filter;
  window.__pages = [];
  let page = 1, total = 0, capped = false;
  while (true) {
    if (page > 12) { capped = true; break; }
    const res = await window.__replay('', page, 100, 'pages/stats', { AIFilterKeyword: kw });
    if (res.status !== 200 || !res.data || !res.data.Pages) break;
    window.__pages.push(...res.data.Pages);
    total = res.data.TotalNumOfRecords || 0;
    if (window.__pages.length >= total) break;
    page++;
  }
  return { filter: kw, captured: window.__pages.length, total: total, capped: capped };
};

// (B) Per-URL queries — the grounding queries + citation counts for one page.
//     Pass the full page URL as the first arg (goes into the Page field).
window.__harvest = window.__harvest || {};
window.__harvestOne = async function (fullUrl) {
  const rows = [];
  let page = 1;
  while (page <= 12) {
    const res = await window.__replay(fullUrl, page, 100, 'searchqueries/stats');
    if (res.status !== 200 || !res.data || !res.data.Queries) break;
    rows.push(...res.data.Queries);
    const total = res.data.TotalNumOfRecords || 0;
    if (rows.length >= total) break;
    page++;
  }
  window.__harvest[fullUrl] = rows;
  return rows.length;
};

// (C) Batch over many URLs, polite 400ms spacing.
window.__harvestBatch = async function (urls) {
  for (const u of urls) {
    await window.__harvestOne(u);
    await new Promise(r => setTimeout(r, 400));
  }
  return Object.fromEntries(Object.entries(window.__harvest).map(([k, v]) => [k, v.length]));
};


/* -----------------------------------------------------------------------------
 * Step 4 — Reading data back out (JS action return values truncate, ~1KB).
 * Don't return the whole dataset at once. Instead read a slice per call:
 *
 *   JSON.stringify(window.__harvest['https://www.example.com/guides/...']).slice(0, 1000)
 *   JSON.stringify(window.__harvest['https://www.example.com/guides/...']).slice(1000, 2000)
 *   ...
 *
 * or one key at a time. Transcribe each chunk into a local file as you go.
 *
 * Row shape per query:
 *   { GroundingQuery, Intent: [...], TopicClusters: [...], Citations, CitationRate }
 * -------------------------------------------------------------------------- */
