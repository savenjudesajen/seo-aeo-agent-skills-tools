# Benchmark method: cross-industry and packed

Do not benchmark only the client's industry. Find the pages that do this page type best in any industry, read many
of them, and pack the client's page with every section that helps a buyer or an AI answer. Navigation and IA stay
inside the client's industry and competitors: menus, footers and URL placement are counted on the client set only.

## Two sets, one taxonomy
1. **Client set**: the client's named rivals first (a rival with no hub is a finding, not a gap to skip), then
   category peers, then two or three category leaders the buyer also knows. Read here: menus, footers, where the page
   type is linked, URL patterns, which rivals target each other, and the hub itself. Code each hub into
   `CLIENT_SET` in `data/public_sample.py`.
2. **Cross-industry set**: the shipped public sample (10 SaaS vendors and 5 hubs from other industries, coded in
   `data/public_sample.py`, read in `public-benchmark-saas-hubs.md` and `public-benchmark-cross-industry-hubs.md`)
   plus three to five review-publisher "best of" pages you read on the run. Mix three kinds:
   - review publishers: they show the trust patterns vendors skip (disclosure, bylines, method, update logs,
     verdicts, also-tested lists);
   - marketplaces: builders, ratings with counts, buying guides, paid-placement labels;
   - category-leading vendors in other industries: what a vendor can adopt without reading as biased.
   Pick publishers and vendors from categories unrelated to the client, so the benchmark never maps back to a
   client and the client's own category is covered by the client set alone.
3. **One taxonomy.** Code every page against the 45 ids in `section-types.md`. When a hand check on the live page
   disagrees with a coding, change the coding and add the reason to `OVERRIDES`. Reuse the public codings unless the
   user asks for a refresh; re-code only the client set and the publishers you add.
4. **Pack.** Every type lands somewhere: a block, part of a block, or a "Not used" line with its reason
   (`LANDS` in `data/block_model.py`, Appendix B of the document). Order the blocks by the buyer's stages. Nothing
   is dropped silently.
5. **Statuses.** New, Rework (the content exists on the client's site in another form), Optional (adds depth, never
   blocks the launch), Later (waits for content only the client can supply; list what is needed in a table).

## What to look for on the client set
- Where each hub is linked: a Why <brand> menu, a Resources menu, a product menu, the footer, or nowhere. Top-level
  Compare items are rare in every set read so far.
- The hub label and H1: "<Brand> vs. the competition", a question H1, or a keyword-plus-year H1.
- Hub anatomy. In crowded categories vendor hubs are often thin (H1, one-line intro, a list of rivals, a demo band,
  under 1,000 words). That thinness is the opportunity.
- Search plays around the hub: rival-versus-rival pages, competitor profile directories, "<rival> alternatives"
  listicles in a resources or academy section, switch pages, year stamps in titles.
- Cross-targeting: which rivals publish pages about each other, and which rival publishes none while others target
  it (the client can own that comparison).
- Keyword landing pages with a stripped header and footer: the site's navigation passes them no internal links.

## Reading each page
- Read pages in parallel (sub-agents work well): a plain fetch plus a JavaScript-rendered read (tables, scorecards
  and competitor lists often render only with JavaScript), plus a heading audit for the complete heading list. Each
  read returns a fixed block per page: title and H1, date shown, byline, sections in order (heading, what it shows,
  what it gives buyers, what it gives AI answers), and screenshot hints with approximate heights.
- You decide set membership by hand; scripts only count. Record redirects, 404s and substitutions in the appendix.
- When a page is served differently to a fetch than to a browser (a redirect, a different template, a different
  text for AI user agents), count from what you can verify, note both, and do not use it as a screenshot exemplar.
- Long pages get cut off by text extractors (around 30,000 characters is common). Read the second half with a
  targeted read or the browser before you code it.
- Paraphrase what a page does in your notes and the document; quote a heading only where a caption or a "Why" cell
  rests on the exact words, and re-read that quote in the browser first.

## Demand, results and AI answers
- Keyword volumes and cost per click for "<rival> alternatives", "<rival> vs <rival>" and "<brand> vs <rival>".
  Expect small but commercial demand; the cost per click is the argument.
- Who ranks for the two biggest terms (vendor comparison pages often hold most of the top results).
- Three unbranded comparison prompts in at least two AI assistants: which vendors are named, and whether the client
  is named only when the prompt names it.
- State each figure with its market, source and month.

## Captures
- At least one screenshot per New or Rework block, from the best page for that block, and one for a Later block
  when it helps the client see what to supply. Captions say only what the capture shows: re-read the image before
  writing the caption.
- Crop out rows and elements the caption does not discuss (an undated rating row under the dated one you mean, a
  promo banner).
- Blur personal contact details. Do not paint over a pointer that sits on text: re-capture instead.
- Browser mechanics (a hidden window, the pointer, cookie banners, zooming a page so a table fits): see the
  web-screenshot-to-document skill. Crop with `data/crop_captures.py`.

## Counting words
- Every cell names its base ("n of 11", "2 of the 8 SaaS comparison pages").
- Denominators drift: companies, menus and footers read, hubs, comparison pages. State each base and keep them apart.
- "4 of the 6" only when all 6 were checked. Otherwise name the ones seen.
- Assert every named example is in the set it illustrates (`EXAMPLE_SETS` in `data/block_model.py`).
