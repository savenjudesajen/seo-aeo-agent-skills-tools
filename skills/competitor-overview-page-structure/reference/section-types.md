# Section types: comparison hubs (45 types)

One taxonomy for every hub you read. Code each page against these ids, keep the codings in
`data/public_sample.py` (the shipped public sample plus `CLIENT_SET`), and every count then reads
"client set + public sample = all".

"Public sample" counts are out of the 11 coded public hubs (6 SaaS vendors, 3 vendors in other industries,
2 software marketplaces). A 0 means vendor and marketplace hubs in the sample do not carry the type; most of those
types come from review publishers' "best of" comparison pages. Read three to five publisher pages in categories
unrelated to the client on each run to get live exemplars for them, and code them into `CLIENT_SET` with kind
`publisher` so the counts include them.

| id | Section type | Public sample | Example in the public sample, or the publisher pattern | Default landing on the client hub |
|---|---|---|---|---|
| 1 | Hero with scope or promise line | 11 | Every hub. Strongest when the first line carries a fact, not only a claim | Hero |
| 2 | Verdict or short summary (top summary or closing bottom line) | 0 | Publisher pattern: two or three sentences naming the top picks and who each suits, under a label of its own | The short answer |
| 3 | Ranked or labelled "best for" list | 1 | monday.com gives every rival card a "Best for" niche before the link | Competitor cards: Best for line |
| 4 | Multi-product comparison table | 3 | Zendesk writes the reason into each rating cell; ClickUp tabs one table across three rivals with three-state cells | Comparison table |
| 5 | Own score or rating with a stated scale | 2 | Capterra shows a rating and review count for both sides of each pair | Not used: rival scores set by a vendor read as biased, so the table shows third-party ratings |
| 6 | Sub-scores and weighted scoring | 0 | Publisher pattern: a rating card with sub-ratings and published criterion weights | Not used: How we compare lists the criteria instead |
| 7 | Methodology statement ("how we compare") | 3 | G2 puts a one-sentence "how this list is built" note on each algorithmic list; Capterra explains every comparison dimension | How we compare |
| 8 | Effort or scale stats behind the evaluation | 2 | Capterra and G2 state how many verified reviews sit behind their data | Evaluation strip (optional) |
| 9 | Inclusion or selection criteria | 0 | Publisher and marketplace pattern: the rules a product must meet to be listed | How we compare: which vendors are included and why |
| 10 | Author byline with credentials | 0 | Publisher pattern: named authors with role and credentials, linked to bios | Byline |
| 11 | Fact-checker or editor credit | 0 | Publisher pattern: a named editor or fact-checker next to the author | Byline: reviewed by |
| 12 | Expert bios and signed expert quotes | 0 | Publisher pattern: "about the authors" plus short quotes signed with name and title | Byline names link to bios |
| 13 | Visible last-updated date | 1 | Zendesk shows a last-updated date on its hub | Byline: last reviewed date |
| 14 | Change log | 0 | Publisher pattern: dated entries saying what was retested or changed | How we compare: change log |
| 15 | Money disclosure and paid-placement labels | 1 | Capterra labels paid placements inside the featured block and separates them from ranked lists | Disclosure line |
| 16 | Trust box ("why trust us", review verification) | 1 | Capterra closes with three short statements: method, review verification, how it is paid | How we compare, with the disclosure line |
| 17 | Third-party proof (ratings, analyst or data rankings with source) | 8 | Ahrefs shows an external, dated ranking table with a link to the source; Asana pairs an analyst recognition with a review-site rating | Proof strip and the table's ratings row |
| 18 | Customer logos, testimonials and proof-stat bands | 7 | Ahrefs pairs its figures with the rival's per metric and explains where the rival's raw number is larger | Proof strip, customer stories (later) |
| 19 | Footnotes and citations | 1 | Asana footnotes the claim in its closing band with an "accurate as of" date | Numbered sources |
| 20 | Product review cards | 0 | Publisher pattern: one block per product with rank, rating, test date, short spec and a button | Competitor cards |
| 21 | Pros and cons | 0 | Publisher and marketplace pattern: what the reviewer likes and does not like, including about the top pick | Where each platform leads |
| 22 | Proof screenshots and captioned evidence | 1 | Capterra annotates screenshots of its own comparison tool | Not used: rivals' screens |
| 23 | Video reviews | 0 | Publisher pattern: a short video review per product | Not used at launch: no comparison video |
| 24 | Raw benchmark table | 0 | Publisher pattern: measured test results for every product, with a worked example | Not used: no lab benchmark |
| 25 | Also tested or excluded, with reasons | 0 | Publisher pattern: known products that did not make the list, one line each on why | Also considered (optional) |
| 26 | Candid limitations or disagreement | 0 | Publisher pattern: the reviewer's honest weak points for every pick, the top one included; the vendor version states a setup or use its product does not support | Where each platform leads |
| 27 | Objection handling (named doubts with answers) | 1 | Asana's FAQ answers the doubts rivals raise (limits, downtime, rollout time) | Doubts answered |
| 28 | Industry-context or market-critique section | 1 | Ahrefs gives a rival's change of ownership its own section and answers with its own independence | How the category is changing (optional) |
| 29 | Rival directory (links to every comparison) | 10 | Capterra's pair cards show price and two scores for both sides; Shopify splits featured, single and three-way comparisons | Competitor cards |
| 30 | Use-case, segment or device directory | 3 | G2 offers popular categories as a second way in; Shopify tags each card with the segment it serves | Compare by need |
| 31 | Filters, sort and segment tags | 2 | HubSpot filters comparisons by product line and tags every card with the products it covers | Compare by need |
| 32 | Interactive comparison builder | 2 | Capterra builds a two-to-four product comparison; G2 has an open "X vs Y" picker | Side-by-side builder (later) |
| 33 | Calculator or personalised benchmark tool | 1 | Shopify links a self-benchmark report on the reader's current site | Not used unless the product has something to calculate |
| 34 | Quadrant or market map | 0 | Marketplace pattern: a quadrant of leaders and challengers drawn from review data | Not used: a vendor-drawn market map reads as biased |
| 35 | Category explainer ("what is X") | 0 | Publisher pattern: a short "what is X and how does it work" section before the picks | What each type of tool does |
| 36 | Buying guide or how-to-choose | 2 | Capterra gives three short buyer tips; ClickUp's FAQ answers how to choose | Buyer's checklist |
| 37 | Switching or migration help | 2 | Shopify puts a migration reassurance straight after the rival list; ClickUp answers switching questions in its FAQ | Comparison pages carry the switch path |
| 38 | FAQ | 4 | Zendesk answers "who are the competitors" directly; ClickUp writes its FAQ for unbranded buyer questions | FAQ |
| 39 | Jump links or table of contents | 1 | Zendesk opens with anchor links to each section | On this page |
| 40 | Pricing snapshot and deals | 1 | Shopify shows a starting price without leaving the hub | Comparison table: pricing model row |
| 41 | Winner or award badges | 0 | Publisher pattern: a "winner" badge on the top pick | Not used: a vendor naming itself winner reads as biased |
| 42 | Capability tour ("why us") | 6 | Ahrefs numbers its exclusive features, each with a screenshot | Where the product fits |
| 43 | Advisor, chat, lead capture and downloads | 4 | Capterra offers an advisor call; Ahrefs offers a downloadable comparison brochure for internal buy-in | Checklist download and the main offer |
| 44 | Related guides | 2 | Zendesk ends with related posts; monday.com links its alternatives pages | Related reading |
| 45 | Conversion CTA (trial, sign-up, visit-site buttons) | 10 | Shopify repeats its trial offer in the hero and the closing band | Button and closing band |

## Not visible as sections, but check on every page
- Structured data (BreadcrumbList, CollectionPage, FAQPage, ItemList, Article). Several hubs in the sample carry
  none.
- Content that exists only after JavaScript runs (advisor blocks, email forms, whole competitor lists). Read the
  server HTML and the rendered page and note which blocks an AI crawler that does not run scripts would miss.
- Some sites serve a differently structured page to AI user agents than to browsers. When the two reads differ,
  record both and count what the browser shows.
