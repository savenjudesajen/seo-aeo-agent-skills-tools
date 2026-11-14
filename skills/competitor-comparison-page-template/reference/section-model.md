# Section model: the "{Company} vs <Rival>" comparison page (packed)

Built on 12 published comparison pages on vendors' own sites: 9 by SaaS leaders and 3 by vendors in other
industries (Shopify, Ahrefs, Semrush). Every page is coded against one taxonomy of 50 section types
(`reference/section-types.md`). Counts read "n of 12" unless the cell says otherwise, and come from
`data/packed_vs.py` (run it to reprint them). `{Company}` is the company that publishes the page, `{Product}` the
product compared, `<Rival>` the competitor.

Vendor pages alone never show some of the trust blocks this model recommends (a disclosure line, a method, a change
log). Those come from patterns common on independent review sites; their count is 0 of 12 and the model says so.
When you run this for a client, add the client's own rival pages as a private set (`reference/benchmark-method.md`)
and recount; keep that set out of anything you publish.

## The 26 blocks in page order
Default status assumes a company with no comparison pages yet: every block New, except three depth blocks that are
Optional because they never block a launch. Re-decide each status against the live site on every run.

| # | Stage | Block | Default status | Pages with it | Best examples |
|---|---|---|---|---|---|
| 1 | Capture | Breadcrumb, H1 "{Company} vs <Rival>" and the difference in one line | New | 12 of 12 state a verdict or thesis in the first screen | Semrush, Ahrefs, Airtable |
| 2 | Capture | Byline: written by, reviewed by, last reviewed | New | 1 of 12 name an author, 2 of 12 show a date | monday.com |
| 3 | Capture | Disclosure: {Company} wrote this page and sells {Product} | New | 0 of 12 (a review-site pattern a vendor can adopt) | none in this set |
| 4 | Capture | Button: the one call to action the site uses for this audience | New | all 9 SaaS pages, and Shopify and Ahrefs | Shopify, Ahrefs, Airtable |
| 5 | Capture | Proof strip: a few sourced proof points | New | 10 of 12 show logos or customer-scale numbers | Ahrefs, Shopify, Asana |
| 6 | Orient | Key takeaways: the short answer, one point a rival strength | New | 6 of 12 open with takeaways or a short answer | monday.com, Shopify, HubSpot |
| 7 | Orient | Choose {Company} if, Choose <Rival> if | New | 1 of 12 | monday.com |
| 8 | Orient | On this page: jump links that carry each section's answer | New | 2 of 12 | Shopify, monday.com |
| 9 | Evaluate | At-a-glance table: the same rows in text on every page, dated, a Leads tag on each row | New | 10 of 12 carry a table, a winner per row on 1 | monday.com, Webflow, Zendesk |
| 10 | Evaluate | Where each one leads, <Rival> first | New | 2 of 12 concede a row or a point to the rival, 10 list one-sided strengths | monday.com, Ahrefs |
| 11 | Evaluate | What both do: the ground they share | New | 3 of 12 | Asana, Webflow |
| 12 | Evaluate | Sections by buying question, the answer in each heading | New | 2 of 12 run one section per dimension | monday.com, Zendesk |
| 13 | Evaluate | Where they work together: keep <Rival>, add {Product} | New | 3 of the 9 SaaS pages, and Shopify | Intercom, HubSpot, Shopify |
| 14 | Evaluate | How each one is bought: pricing model, trial, contract | New | 5 of 12 compare pricing, the cost model explained on 1 | Zendesk, Shopify, monday.com |
| 15 | Evaluate | Security and data handling: certifications for both | New | 3 of 12 compare security or certifications | Webflow, monday.com |
| 16 | Evaluate | Company context: ownership and acquisitions, dated and sourced | Optional | 3 of 12 | Ahrefs, Notion |
| 17 | De-risk | Proof measured against this rival: quotes, ratings and research, each dated | New | 10 of 12 quote customers, 3 name the source of review-site ratings, 6 cite analysts or public data | Ahrefs, Shopify, monday.com |
| 18 | De-risk | Getting started beside <Rival>: what a <Rival> customer needs | New | 7 of 12 | Airtable, Shopify, Notion |
| 19 | De-risk | FAQ: the questions <Rival> customers ask | New | 9 of 12 | Airtable, Intercom, Webflow |
| 20 | De-risk | How we compared: writer, reviewer, pages checked, change log, corrections | New | 0 of 12 (a review-site pattern a vendor can adopt) | none in this set |
| 21 | De-risk | Numbered sources, each with the date it was read | New | 5 of 12 stamp figures with an as-of date | Ahrefs, Semrush, HubSpot |
| 22 | De-risk | {Product} in action: one annotated screenshot | New | 0 of 12 | none in this set |
| 23 | Convert | Take-away: the comparison as a one-page PDF | Optional | 4 of 12 | Notion, Ahrefs |
| 24 | Convert | Related comparisons, then All comparisons | New | 5 of 12 | monday.com, ClickUp, Zendesk |
| 25 | Convert | Ask an AI assistant: a neutral prefilled prompt | Optional | 0 of 12 | none in this set |
| 26 | Convert | Closing band: one line on the offer, then the button | New | 10 of 12 | Ahrefs, Shopify, Webflow |

Default status tally: New 23, Optional 3. Launch set: 23 blocks. A real run moves blocks to Rework (the content
exists on the site in another form) or Later (it waits for content only the company can supply).

## Stages
Capture (first screen: pair, difference, who wrote it, button, proof), Orient (takeaways, choose-if lists, jump
links), Evaluate (table, leads, shared ground, sections by question, work together, how each is bought, security,
company context), De-risk (proof against this rival, getting started, FAQ, how we compared, sources, product in
action), Convert (take-away, related comparisons, AI prompt, closing band).

## Status rules
- New: nothing like it on the company's site. Rework: the content exists somewhere on the site and moves here in a
  new form. Optional: adds depth, never blocks the launch. Later: waits for content only the company can supply
  (certifications, product screenshots); list what is needed in a table.
- A type that would read as biased from a vendor (house scores, winner cards, weights, a rival's incidents) gets a
  "Not used" reason in the type map, never a quiet omission.

## Principles
- Concede first: only 2 of 12 vendor pages give the rival a row or a point (one blog-format comparison, one numeric
  face-off). Real concessions are rare on vendor pages, which makes them stand out; independent review sites concede
  routinely, and vendors that copy the habit read as fair.
- Say who wrote it: 1 of 12 names an author (a blog-format comparison), none names a reviewer. A byline with a
  reviewer is open ground for any vendor.
- Every claim dated: 5 of 12 stamp figures with an as-of date. A data-as-of note more than a year old, or proof cards
  dated years back, read as neglect.
- Replace or run beside: 3 of the 9 SaaS pages offer to run alongside the rival, and Shopify offers a way to start on
  the rival's platform before migrating. Settle it on every page.
- Text, not ticks: a sentence per cell is what AI answers quote. Grids that are all yes versus no prove nothing.
- One source of truth: when the summary, table, sections and FAQ are written separately they contradict each other.
  Feed every number from one place.
- Ship it in the HTML: some comparison tables render only with JavaScript and are invisible to a plain fetch.
