# Section types: one-rival comparison pages (50 types)

Counts come from `data/section_library.py`: 12 published comparison pages on vendors' own sites, 9 by SaaS leaders and 3 by vendors in other industries (Ahrefs, Semrush, Shopify). Run the script to reprint them. Best examples are paraphrased; re-read the live page before you capture or describe it. "Not in this set" marks a pattern seen on independent review sites, described without a named example. The last column says where each type lands on the company's comparison pages (`data/packed_vs.py`, LANDS).

When you run this for a client, re-code the client's private set against the same ids and add a column for it; keep that copy out of anything you publish.

| id | Section type | Pages: SaaS + other = all | Other-industry pages with it | Best example | Lands on the company's page |
|---|---|---|---|---|---|
| 1 | Commercial disclosure (affiliate, advertiser, independence) | 0 + 0 = 0 | - | Not in this set: review sites put a one-line note on how they are funded above the H1 | Disclosure line |
| 2 | Verdict or thesis in the first screen | 9 + 3 = 12 | Ahrefs, Semrush, Shopify | Semrush: a two-sentence scope contrast in the hero that describes the rival fairly enough to be quoted | Difference line and key takeaways |
| 3 | Byline with author credentials | 1 + 0 = 1 | - | monday.com: a named author with photo, an updated date and a read time on a blog-format comparison | Byline |
| 4 | Why-trust-us box with testing-scale stats | 0 + 0 = 0 | - | Not in this set: review sites add a box saying how many products they tested and how | How we compared |
| 5 | Visible updated or published date | 2 + 0 = 2 | - | Zendesk: a last-updated date directly under the hero image | Byline: last reviewed |
| 6 | As-of stamps on figures and evidence (with a correction channel on one vendor) | 2 + 3 = 5 | Ahrefs, Semrush, Shopify | Ahrefs: an as-of month under a sourced third-party table; Semrush adds a report-an-error link under its data | Numbered sources with the date read |
| 7 | Update log (dated changelog) | 0 + 0 = 0 | - | Not in this set: review sites keep a short dated list of what changed in each revision | How we compared: change log |
| 8 | Key takeaways or short summary (reasons-to-switch list on vendor pages) | 5 + 1 = 6 | Shopify | monday.com: a takeaways list near the top in which one bullet is a rival strength | Key takeaways |
| 9 | Jump links, table of contents or section cards | 1 + 1 = 2 | Shopify | Shopify: a numbered list of reasons, each a one-line proof and a jump link to its section | On this page |
| 10 | Winner or product cards / overall house rating | 0 + 0 = 0 | - | Not in this set: review sites show a card per product with a house score and a winner label | Not used: a vendor rating both products reads as biased |
| 11 | At-a-glance spec or key-differences table | 4 + 0 = 4 | - | monday.com: an at-a-glance table in text whose first row is Best for | At-a-glance table |
| 12 | Checkmark or yes/no feature grid | 5 + 2 = 7 | Ahrefs, Semrush | Webflow: a three-way table with an icon plus a one-sentence reason in every cell | Not used: ticks hide the difference, so the table uses sentences |
| 13 | Per-category numeric scorecard for both products | 0 + 0 = 0 | - | Not in this set: review sites score both products per testing category in one table | Not used: scores a vendor sets read as biased |
| 14 | Winner per category (scoreboard, verdict in the heading, per-row winner label) | 1 + 0 = 1 | - | monday.com: every dimension heading states its verdict, parity verdicts included | Table: the Leads tag on each row |
| 15 | Head-to-head rounds per dimension | 2 + 0 = 2 | - | monday.com: one section per buying dimension with a short per-vendor comparison inside | Sections by buying question |
| 16 | Similarities or shared ground | 3 + 0 = 3 | - | Asana: a grid that marks the rival as equal on half its rows | What both do |
| 17 | Best-for or choose-if guidance | 1 + 0 = 1 | - | monday.com: paired go-with-us-if and go-with-the-rival-if lists | Choose-if lists |
| 18 | Concessions: rows or rounds the rival wins | 1 + 1 = 2 | Ahrefs | Ahrefs: shows the one metric where the rival is larger and explains why it is not like for like | Where each one leads: Where <Rival> leads |
| 19 | Differentiator blocks (one-sided strengths) | 7 + 3 = 10 | Ahrefs, Semrush, Shopify | Ahrefs: a numbered list of things only it can do, one screenshot per item | Where each one leads: Where {Company} leads |
| 20 | Hands-on test results with numbers | 0 + 0 = 0 | - | Not in this set: review sites publish measured tests with the conditions stated | Proof measured against this rival |
| 21 | Visual evidence (screenshots of both, side-by-side video) | 0 + 0 = 0 | - | Not in this set: review sites film the same task in both products side by side | {Product} in action |
| 22 | Pricing compared for both | 4 + 1 = 5 | Semrush | Zendesk: a two-column price table that states each side's billing basis | How each one is bought |
| 23 | Total cost, renewal or billing model explained | 0 + 1 = 1 | Shopify | Shopify: total cost split into setup, platform and operating components, with a calculator | How each one is bought: the cost model |
| 24 | Free trial and refund terms compared | 0 + 0 = 0 | - | Not in this set: review sites compare trial length and refund terms for both products | How each one is bought: trial or first step |
| 25 | Interactive tool or live data (calculator, live quote, deal widget, comparison builder) | 2 + 1 = 3 | Shopify | Asana: an ROI calculator framed as making the case for a switch | Not used unless the product has something to calculate |
| 26 | Security, audits and certifications compared | 2 + 1 = 3 | Shopify | Webflow: certifications as a row of its comparison table, crediting the rival's enterprise tier where equal | Security and data handling |
| 27 | Incident or track-record section | 0 + 1 = 1 | Shopify | Shopify: risk on the rival's side cited from a public database rather than asserted | Not used: a vendor listing a rival's incidents reads as an attack |
| 28 | Data-handling table (what each collects) | 0 + 0 = 0 | - | Not in this set: review sites tabulate what each product collects, read from both privacy policies | Security and data handling |
| 29 | Customer support compared | 3 + 0 = 3 | - | monday.com: a support section with a heading per vendor | Sections by buying question: support |
| 30 | Ease of use, setup or implementation compared | 3 + 0 = 3 | - | monday.com: an ease-of-use section with a heading per vendor and user quotes | Getting started beside <Rival> |
| 31 | Platform or integration coverage compared | 5 + 0 = 5 | - | monday.com: an integrations section with a parity verdict | Where they work together: how they connect |
| 32 | Third-party user ratings with the source named | 2 + 1 = 3 | Semrush | monday.com: review-site scores for both products, each with its review count | Proof: review-site ratings for both, dated |
| 33 | Independent third-party evidence (labs, analysts, public datasets, press awards, legal cases) | 4 + 2 = 6 | Ahrefs, Shopify | Ahrefs: a third-party ranking table, dated and linked to the full report, in which the rival also appears | Proof: analyst research and public data |
| 34 | Customer testimonials | 8 + 2 = 10 | Semrush, Shopify | Zendesk: story cards from customers who switched from the rival, each with a metric | Proof strip, and proof measured against this rival |
| 35 | Logo wall and customer-scale stats | 7 + 3 = 10 | Ahrefs, Semrush, Shopify | Ahrefs: a logo wall with one customer-scale share figure | Proof strip |
| 36 | Reviewer demographics (segment, industry) | 0 + 0 = 0 | - | Not in this set: review marketplaces show which company sizes and industries review each product | Not used unless {Company} has review-site data of its own |
| 37 | Pros and cons for both (incl. AI review summary) | 0 + 0 = 0 | - | Not in this set: review sites list pros and cons for both products, often as counted review themes | Where each one leads |
| 38 | Company and market context (ownership, acquisition, roadmap) | 1 + 2 = 3 | Ahrefs, Shopify | Ahrefs: an industry-context section on the rival's change of ownership, answered with its own independence | Company context (optional) |
| 39 | Methodology section | 0 + 0 = 0 | - | Not in this set: review sites explain how they compared, criterion by criterion | How we compared |
| 40 | Weighted scoring criteria | 0 + 0 = 0 | - | Not in this set: review sites list the criteria with a weight each | Not used: How we compared lists the rows, not weights |
| 41 | Migration or getting-started path | 6 + 1 = 7 | Shopify | Shopify: named migration partners for this exact switch | Getting started beside <Rival> |
| 42 | Buyer education or tip callouts | 0 + 0 = 0 | - | Not in this set: a short block that teaches how to judge any product in the category | Sections by buying question: a tip line where it helps |
| 43 | FAQ | 8 + 1 = 9 | Shopify | Airtable: question-led sections, one answering a current rival user with a module-by-module equivalence map | FAQ |
| 44 | Final verdict section | 1 + 0 = 1 | - | monday.com: a closing conclusion that restates when each product fits, with a button | Not used: the answer sits at the top |
| 45 | Related comparisons or vs-hub links | 4 + 1 = 5 | Semrush | monday.com: an alternatives link and a run of further comparisons near the end | Related comparisons |
| 46 | Alternatives to both products | 0 + 0 = 0 | - | Not in this set: review marketplaces list alternatives to each product with ratings | Related comparisons: All comparisons on the hub |
| 47 | Take-away asset (CSV export, brochure, white paper, emailed comparison) | 2 + 2 = 4 | Ahrefs, Shopify | Notion: the detailed comparison as a downloadable guide | Take-away PDF (optional) |
| 48 | Closing CTA band | 7 + 3 = 10 | Ahrefs, Semrush, Shopify | Ahrefs: a closing band with a live sign-up counter, a sign-up button and a downloadable brochure | Closing band |
| 49 | Legal or non-endorsement disclaimer | 0 + 0 = 0 | - | Not in this set: a footnote saying the rival has not reviewed or approved the comparison | Disclosure line and the trademark line |
| 50 | Reader feedback or community Q and A | 0 + 0 = 0 | - | Not in this set: review marketplaces show community questions per product | Not used: no reader comments |
