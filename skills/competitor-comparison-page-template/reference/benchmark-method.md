# Benchmark method: wide and packed

The rule: do not benchmark only the client's industry. Find the pages that do this page type best in any industry,
read many of them, and pack the client's page with every section that helps a buyer or an AI answer. Navigation and
information architecture stay inside the client's industry and competitors: menus, footers and URL placement are
counted on the client's own set only.

## Sets, one taxonomy
1. **Client set** (built per run, never published): about 10 to 20 "<brand> vs <rival>" pages by the client's
   rivals and category peers. Read here: menus, footers, where the page type is linked, URL patterns, and the page
   itself. Keep this set, its codings and its notes in the client's workspace, not in this skill.
2. **Carried vendor set** (12 pages): head-to-head pages by well-known SaaS vendors (CRM, customer support, work
   management, docs, website builder) and by vendors in ecommerce and SEO software. Shows what vendor pages usually
   do and usually skip. Notes: `reference/readings-saas-pages.md` and `reference/readings-cross-industry-pages.md`.
3. **Optional wide set** (per run): independent review sites and marketplaces in categories unrelated to the client
   and its rivals. They show the trust patterns vendors skip (disclosure, bylines, method, update logs). Code them
   against the same ids if you add them; the carried notes describe these patterns without a named example.
4. **One taxonomy.** Every section type (50 for this page type), each with an id, a one-line definition and the best
   exemplar, lives in `data/section_library.py`. Re-code the client set against the same ids in a private copy, so
   every count reads "client + carried = all". Reuse the carried codings unless the user asks for a refresh; re-read
   any page you quote.
5. **Pack.** Every type lands somewhere: a block, part of a block, or a "Not used" line with the reason
   (`reference/section-types.md`, Lands column). Order the blocks by the buyer's stages. Nothing is dropped silently.
6. **Statuses.** New, Rework (the content exists on the client's site), Optional (adds depth, never blocks the
   launch), Later (waits for content only the client can supply; list what is needed in a table).

## Reading each page
- Read pages in parallel (sub-agents work well): a plain fetch plus a JavaScript-rendered text read (tables and
  scorecards often render only with JavaScript), and return a fixed block per page: title and H1, date, byline,
  sections in order (heading, what it shows, what it gives users, what it gives AI answers) and screenshot hints with
  approximate heights.
- You decide set membership by hand; scripts only count. Record any substitution (a page that moved or no longer
  exists) in the appendix.
- Re-read in the browser every quote a caption, a Why cell or a Seen on cell rests on.
- Notes describe structure and claim patterns in your own words. Do not paste page copy into a deliverable.

## Reading the client set's navigation
- Comparison pages seldom sit in the main menu; the hub and the footer usually link them. Count where the client's
  rivals place theirs before recommending a slot.
- Pick one URL pattern and keep it, for example /compare/<brand>-vs-<rival> or /vs/<rival>. Brand first is the
  common default.
- Decide which page owns each "<brand> vs <rival>" query, so two pages on the site never target the same pair.

## Captures
- At least one screenshot per New or Rework block, from the best page for that block, and one for Later blocks when
  it helps the client see what to supply. Captions say only what the capture shows: re-read the image before writing.
- Browser mechanics: the capture recipe in `reference/lean-doc.md` (and the `web-screenshot-to-document` skill, if
  installed).

## Counting words
- Every cell names its base ("n of 12", "3 of the 9 SaaS pages").
- "n of N" only when all N were checked; otherwise name the pages seen.
- Assert every named example is in the set it illustrates (EXAMPLE_SETS in `data/packed_vs.py`).
- Read footnotes: a stat headed against a rival may measure something else, such as an older product or a different
  segment.
- A study the vendor commissioned is still evidence, but say it was commissioned.
