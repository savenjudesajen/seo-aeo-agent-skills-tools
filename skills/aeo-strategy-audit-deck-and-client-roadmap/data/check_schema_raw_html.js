// GATE: what schema is ACTUALLY server-rendered (what non-JavaScript AI crawlers see).
//
// Run it in the browser on a page of the client's site: paste into the DevTools console, or pass the
// file's contents to a browser-automation tool's "execute JavaScript" action. It only reads; it changes
// nothing.
//
// Two modes (set MODE below):
//   'page'    - the current page: raw-HTML JSON-LD types, enrichment flags, canonical, noindex.
//   'sitemap' - every URL in the same-origin sitemap (nested sitemap indexes followed): a sitewide count
//               of pages carrying each @type, pages with no JSON-LD, noindex pages and fetch errors.
//
// WHY THIS EXISTS: SEO-tool flags such as `has_micromarkup` track Microdata, NOT JSON-LD, and a crawl with
// structured-data extraction off reports zero schema. Both produce false "no schema" findings. Claiming a
// client's schema is invisible to AI on that basis is the most expensive mistake in this skill.
//
// HOW TO READ THE OUTPUT:
//  - raw_ldjson_types non-empty  => schema IS server-rendered and crawlers see it. Pitch enrichment.
//  - rendered > raw              => some schema is injected client-side only (AI crawlers may miss it).
//  - service_workers > 0         => the fetch may be intercepted; confirm with View Source.
//  - has_AggregateRating false + a rating visibly on the page => the enrichment win.
//  - noindex true on a money page => stop; this is the headline finding.

const MODE = 'page';                 // 'page' or 'sitemap'
const SITEMAP_PATH = '/sitemap.xml'; // used in 'sitemap' mode
const MAX_URLS = 2000;               // safety cap for 'sitemap' mode
const CONCURRENCY = 6;

(async () => {
  const LD_RE = /<script[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;

  function collectTypes(node, out) {
    if (Array.isArray(node)) { node.forEach(n => collectTypes(n, out)); return; }
    if (!node || typeof node !== 'object') return;
    if (node['@type']) [].concat(node['@type']).forEach(t => out.push(String(t)));
    if (node['@graph']) collectTypes(node['@graph'], out);
  }

  function analyse(html) {
    const types = [];
    let valid = true, m;
    LD_RE.lastIndex = 0;
    while ((m = LD_RE.exec(html)) !== null) {
      try { collectTypes(JSON.parse(m[1]), types); }
      catch (e) { valid = false; types.push('PARSE_ERROR'); }
    }
    return {
      types,
      valid,
      canonical: (html.match(/rel=["']canonical["'][^>]*href=["']([^"']+)/i) || [])[1] || null,
      noindex: /<meta[^>]+name=["'](robots|googlebot)["'][^>]+content=["'][^"']*noindex/i.test(html),
    };
  }

  async function fetchText(url) {
    const res = await fetch(url, { cache: 'no-store', credentials: 'omit' });
    return { status: res.status, text: await res.text() };
  }

  if (MODE === 'page') {
    const swRegs = navigator.serviceWorker ? await navigator.serviceWorker.getRegistrations() : [];
    const { status, text } = await fetchText(location.href);
    const a = analyse(text);
    return JSON.stringify({
      url: location.href,
      status,
      service_workers: swRegs.length,
      raw_ldjson_blocks: (text.match(/application\/ld\+json/gi) || []).length,
      raw_ldjson_types: a.types,
      raw_ldjson_valid_json: a.valid,
      rendered_ldjson_blocks: document.querySelectorAll('script[type="application/ld+json"]').length,
      has_AggregateRating: a.types.includes('AggregateRating') || text.includes('AggregateRating'),
      has_Review: a.types.includes('Review'),
      has_BreadcrumbList: a.types.includes('BreadcrumbList'),
      has_Person: a.types.includes('Person'),
      has_FAQPage: a.types.includes('FAQPage'),
      canonical: a.canonical,
      noindex: a.noindex,
    }, null, 2);
  }

  // 'sitemap' mode: same-origin sitemap, nested indexes followed.
  const queue = [new URL(SITEMAP_PATH, location.origin).href], seenMaps = new Set(), urls = [];
  while (queue.length && urls.length < MAX_URLS) {
    const sm = queue.shift();
    if (seenMaps.has(sm)) continue;
    seenMaps.add(sm);
    const { text } = await fetchText(sm);
    const locs = [...text.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/gi)].map(x => x[1].replace(/&amp;/g, '&'));
    const isIndex = /<sitemapindex/i.test(text);
    for (const loc of locs) {
      if (new URL(loc, location.origin).origin !== location.origin) continue;
      if (isIndex) queue.push(loc); else if (urls.length < MAX_URLS) urls.push(loc);
    }
  }

  const typeCounts = {}, noLd = [], noindex = [], errors = [];
  let i = 0;
  async function worker() {
    while (i < urls.length) {
      const url = urls[i++];
      try {
        const { status, text } = await fetchText(url);
        if (status >= 400) { errors.push(`${status} ${url}`); continue; }
        const a = analyse(text);
        if (!a.types.length) noLd.push(url);
        if (a.noindex) noindex.push(url);
        new Set(a.types).forEach(t => { typeCounts[t] = (typeCounts[t] || 0) + 1; });
      } catch (e) { errors.push(`ERR ${url}`); }
    }
  }
  await Promise.all(Array.from({ length: CONCURRENCY }, worker));

  return JSON.stringify({
    sitemaps_read: seenMaps.size,
    urls_checked: urls.length,
    capped: urls.length >= MAX_URLS,
    pages_per_type: typeCounts,
    pages_without_ldjson: noLd.length,
    pages_without_ldjson_sample: noLd.slice(0, 25),
    noindex_pages: noindex,
    fetch_errors: errors.slice(0, 50),
  }, null, 2);
})()
