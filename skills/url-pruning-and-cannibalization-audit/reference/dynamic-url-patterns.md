# URLs with a ? parameter

Group by pattern, count URLs, check each pattern's Google evidence (indexed or not, impressions,
sessions), research, then choose.

## Principles

- robots.txt controls crawling, not indexing. A URL blocked by robots.txt can stay in the index, and
  Google cannot see a noindex on a page it cannot crawl. Do not block URLs that are still indexed. Block
  only patterns that are not indexed and waste crawl. (Google Search Central, robots.txt introduction,
  developers.google.com/search/docs/crawling-indexing/robots/intro)
- Google has said publicly that a page left on noindex for a long time is eventually treated as nofollow
  too, so do not rely on noindex pages to pass links.
- Google advises that each paginated page carry a self-referencing canonical, not a canonical to page 1.
  (developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading)
- Blocking UTM parameters in robots.txt does nothing useful (Google has said so publicly). Leave them,
  keep internal links free of UTMs, rely on canonicals.
- Some CMSs cannot set a per-parameter robots tag natively. A head script that injects
  `<meta name="robots" content="noindex">` when the URL carries a pagination parameter works, because
  Google renders JavaScript. Prefer a server-side or template-level rule where the platform allows it.
- Before noindexing pagination, confirm every item is in the sitemap and linked from a crawlable
  category, so pages 2 and up are not the only route to content.

## Starting rules by pattern

| Pattern | Default |
|---|---|
| Collection list pagination, indexable pages 2+ | Add noindex (template rule or head script), keep crawlable |
| Pagination already noindex | Let it be. Recheck indexed ones in 4 to 8 weeks. If the template is touched, drop the canonical and keep noindex |
| Two pagination parameters on one URL (`?p1=2&p2=3`) | Block in robots.txt (for example `Disallow: /*?*p1=*&p2=`) only if not indexed, then fix the template |
| Pagination on a static page | Canonical to the base page |
| UTM on live or redirecting URLs | Let it be |
| Form or token parameters (submission IDs) | Let it be; tell the owner if content is gated |
| Faceted filters and sort orders | Canonical to the unfiltered page; block in robots.txt only patterns that are not indexed and explode crawl |

## Output

One row per pattern with: example, URL count, what it is, current state, Google and traffic evidence,
options and their impact, recommendation, how to do it, Review, research basis (URLs), Source. Where a
robots.txt edit is needed, give the exact rule and say to test it in a robots.txt tester first. State
when the platform or plan blocks editing robots.txt through the API.
