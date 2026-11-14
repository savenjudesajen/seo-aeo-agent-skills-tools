# Technical and schema audit for AEO

## Rule zero

Run `data/check_schema_raw_html.js` on the homepage and every money page BEFORE writing a word about
schema, and fetch every sitemap URL for a sitewide count. Report what IS present before what is missing.
See `gotchas.md` #1.

## Crawl configuration (set before crawling)

In Screaming Frog (Configuration > Spider), or the equivalent settings in another crawler:
- **Extraction:** enable JSON-LD, Microdata, RDFa, Schema.org validation and Google rich-result
  validation, plus store HTML and store rendered HTML.
- **Crawl:** enable crawling all subdomains if the client runs any. Locale and marketing subdomains are
  often where the conversion tools and forms live.
- After the crawl, run **Crawl Analysis**, or orphan-page and near-duplicate counts come back as a
  misleading zero.
- Even with extraction enabled, some automated or headless crawl setups store no structured data. Treat
  the raw-HTML scan as the source of truth for schema, and use the crawl for response codes, indexability,
  canonicals, directives, headings, redirect chains, inlinks and crawl depth.

## The checks that matter for AEO

1. **Are the flagship pages even indexable?** A `noindex` (or `noindex,nofollow`) on a product or flagship
   page is the highest-impact finding this audit can produce: invisible to Google AND to AI crawlers, and
   one setting to fix. Always check the money pages for noindex / nofollow first.
2. **FAQ blocks with no FAQPage schema.** Pages often already have clean question-and-answer blocks with
   no markup. Wrapping them is the fastest AEO win after an indexability fix.
3. **Structured-data coverage.** Is there an entity layer at all (Organization + WebSite + WebPage +
   BreadcrumbList)? Then per-page-type schema. A new site is an opportunity: ship a clean `@graph` from
   day one.
4. **Missing enrichment on existing schema.** Common: base schema present but no `AggregateRating`,
   `Review` or `BreadcrumbList`. If the page visibly shows a rating or testimonials, they are unmarked
   citation material.
   - Accuracy rule: a marked-up rating has to equal the genuine, visible, verifiable number on the page.
     Never mint a rating. If the on-page number and the third-party source disagree, resolve it with the
     client before publishing.
5. **Canonicals and host consistency.** Pages served on `www` but self-canonicalising to non-www (or the
   reverse) send mixed signals. Pick ONE host and make the canonical, og:url, sitemap and internal links
   agree, then a single-hop 301 for every other variant (non-www, http, trailing slash).
6. **Redirect chains.** Post-migration sites often 301 through intermediates. Flatten to one hop. A
   PageSpeed "avoid multiple page redirects" flag is the tell; the crawl gives the actual chain list and
   the inlink count behind each (a sitewide template link pointing at a redirect is a common big one).
7. **Heading structure.** Count pages with no H2 from the crawl's H2 filter; on content pages this is
   often the single largest structural gap for extraction.
8. **Speed.** Often NOT the problem on a modern stack. Use real-user field data (Chrome UX Report through
   PageSpeed Insights) plus lab data, and say so plainly when it is fine rather than padding the deck.
9. **Thin content and low extractable text.** A homepage with a few hundred words of real text gives AI
   little to lift.
10. **Author and E-E-A-T signals.** Bylines often exist with no author bio pages and no `Person` schema, so
    the expertise is unattributable.
11. **AI crawler access.** Resolve robots.txt per AI user-agent token (named groups never merge with `*`),
    check llms.txt on the client and 3-5 competitors, and draft one for the client
    (`robots-txt-and-llms-txt`). Report healthy access first.

## Ordering the recommendations

Inside the technical section: the one-setting, same-week fixes first (indexability, FAQPage wrap), then
the entity schema layer, then enrichment (AggregateRating / Review / BreadcrumbList), then hygiene
(canonical, host, redirects), then content depth. Clients that move fast want the ordering, not a list. In
the overall roadmap these sit below the content work (SKILL.md, roadmap rule), except a noindex on a money
page, which is fixed in week 1.

## Schema by page type

- Glossary term: `DefinedTerm` (+ `DefinedTermSet`) + `FAQPage`
- Knowledge-hub concept or guide: `Article` or `TechArticle`, `HowTo` where procedural, + `FAQPage`
- Product: `Product` or `SoftwareApplication` (+ `AggregateRating` only when a real, visible rating
  exists); a service delivered to people is `Service`
- Sitewide entity layer: `Organization` (industry subtype where one exists, + `sameAs`), `WebSite`,
  `WebPage` in an `@graph`, `BreadcrumbList`
- Authors: `Person` with credentials, linked from each article
