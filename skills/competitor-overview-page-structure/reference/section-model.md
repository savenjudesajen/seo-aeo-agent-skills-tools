# Section model: the competitor overview page (comparison hub, packed, cross-industry)

Every hub you read is coded against the 45 types in `section-types.md`; the types are packed into the 27 blocks
below, ordered by the buyer's five stages. The source of truth is `data/block_model.py`: names, statuses, counts and
best examples there feed the order table, the wireframes and the spec rows, so they cannot drift. Navigation counts
come from the client set only (menus and footers are industry-specific); page structure is benchmarked across any
industry.

Counts below are the shipped public sample (11 hubs; navigation from the 10 SaaS menus and footers). On a real run
they change as soon as the client set is coded in, so always print them from the script.

## The 27 blocks in page order

| # | Stage | Block | Default status | Public sample | Best public examples | What to capture |
|---|---|---|---|---|---|---|
| 1 | Capture | Menu link: "Compare <Product>" under the product or Why menu | New | 0 of 10 SaaS menus give comparisons a top-level item; 5 of 10 footers link them | Client set only | The menu of the best peer that links its hub from a Why or product menu |
| 2 | Capture | Breadcrumb, question H1 and a 40 to 60 word answer | New | 11 of 11 open with a hero, 1 asks a question in the H1 | Zendesk | A hero whose first line answers with a fact |
| 3 | Capture | Byline: written by, reviewed by, last reviewed date | New | 0 of 11 name an author, 1 shows a date | Review publishers | A publisher byline with author, reviewer and date |
| 4 | Capture | Disclosure: <Client> wrote this page and sells <Product> | New | 1 of 11, no vendor hub | Capterra | A disclosure line placed before the picks |
| 5 | Capture | Button: the main offer | Rework | 7 of 11 put a button in the hero | Shopify, Semrush | The hero with its button |
| 6 | Capture | Proof strip: <n> proof items, each with its source and date | Rework | 9 of 11 show ratings, logos or customer proof | Semrush, Ahrefs | A ratings row or proof band that shows its sources |
| 7 | Capture | The short answer: which tool fits which job | New | 0 of 11 | Review publishers | A boxed verdict of two or three sentences |
| 8 | Capture | Evaluation strip: what was compared, from how many sources, when | Optional | 2 of 11 | G2, Capterra | A stat line about the evaluation itself |
| 9 | Capture | On this page: jump links to each section | New | 1 of 11 | Zendesk | Anchor links under the hero, or a sticky contents rail |
| 10 | Orient | Compare by need: start from the tool a buyer runs today | New | 3 of 11 | Shopify, G2 | A second way in by use case or segment |
| 11 | Orient | Competitor cards: category, best for, where <Client> differs, link | New | 10 of 11 link a list of comparisons; 1 gives each a best-for line | monday.com, Capterra | Cards with a best-for line; pair cards with a mini verdict |
| 12 | Evaluate | Comparison table in text: dated, sourced, with a row each rival leads | New | 3 of 11 carry a table, 2 name three or more products | Zendesk, ClickUp | A multi-rival table with reasons in the cells |
| 13 | Evaluate | Where each platform leads, <Client> included | New | 0 of 11 | Review publishers | Pros and cons that include the top pick's weak points, or a vendor stating its own limit |
| 14 | Evaluate | Where <Product> fits beside the tools a buyer runs | New | 2 of the 8 SaaS comparison pages offer to run beside the rival | Intercom, monday.com | A "works with the tool you already run" block |
| 15 | Evaluate | What each type of tool does | New | 0 of 11 | Review publishers | A category definition before the comparison |
| 16 | Evaluate | Also considered: tools buyers confuse with <Client>, and why | Optional | 0 of 11 | Review publishers | A short "did not make the list, and why" block |
| 17 | Evaluate | How the category is changing, with dates and sources | Optional | 1 of 11 | Ahrefs | An industry-context section |
| 18 | De-risk | Doubts answered: the objections buyers raise | New | 1 of 11 | Asana | Named objections with answers |
| 19 | De-risk | Customer stories from teams that switched to or added <Product> | Later | 7 of 11 | Zendesk, Shopify | Stories grouped by the tool the customer left |
| 20 | De-risk | Buyer's checklist: questions to ask any vendor, <Client> included | New | 2 of 11 | Capterra, ClickUp | A neutral "what to look for" list |
| 21 | De-risk | FAQ: questions in the words buyers type into AI assistants | Rework | 4 of 11 | Zendesk, ClickUp | Direct answers to "who are the competitors" and how-to-choose questions |
| 22 | De-risk | How we compare: criteria, sources, change log, corrections | New | 3 of 11 show a method, criteria, trust box or change log | Capterra, G2 | A method and verification block |
| 23 | De-risk | Numbered sources for every claim | New | 1 of 11 footnotes a claim, 0 number their sources | Review publishers | Numbered, dated footnotes |
| 24 | De-risk | Side-by-side builder: pick two vendors | Later | 2 of 11 | Capterra, G2 | A two-to-four product picker |
| 25 | Convert | Related reading: <two or three resource links by intent> | New | 2 of 11 | Zendesk, monday.com | Resource cards by intent |
| 26 | Convert | Closing band: the main offer, then <secondary links> | New | 8 of 11 close with a call to action | Shopify, Miro | One line and one button |
| 27 | Convert | Footer: a Compare group naming the main rivals, then All comparisons | New | 3 of 10 SaaS footers name each main rival | Zendesk, ClickUp | A footer Compare group |

The default statuses in `data/block_model.py` are placeholders, not a recommendation. Set every status against the
client's live site, block by block: Rework only where the content already exists on the site in another form, New
where it does not, Optional where it adds depth without blocking the launch, Later where it waits on material only
the client can supply. Print the tally from the script after you set them.

## The open ground
Vendor hubs in the public sample almost never name an author, show a reviewer, state their commercial interest,
give a verdict up front, concede a rival's strengths or number their sources. Review publishers do all of these.
That gap is the usual recommendation: a vendor hub that borrows the publisher's trust patterns while staying fair
reads as more confident, and gives answer engines attributable, dated, quotable facts. Confirm the gap on the
client set each run (in some categories one or two vendors already do part of it; name them).

## Patterns to recommend against
- Cards that put down the rival in a word or two in place of a niche it does well. Some vendor hubs in crowded
  categories do this; it reads as defensive and an answer engine may quote it against the client.
- Joke or loaded table rows. A table with tongue-in-cheek rows mixed with factual ones can mislead answer engines
  that lift it cell by cell.
- Undated review scores and year stamps in titles. Both go stale within months; a stale year in a title reads as
  abandoned.
- Unsourced proof stats placed above the rival list. Copy the placement only with a source on every number.
- A vendor naming itself "winner" or drawing its own market map.

## Patterns worth copying when they fit
- Customer stories grouped under the rival the customer left, so proof maps to the tool the reader is leaving.
- A head-to-head hub and an alternatives index that cross-link, covering "<Brand> vs X" and "X alternatives"
  demand without mixing them on one page.
- Three-way comparison pages ("X vs Y vs <Brand>") in the directory for "X vs Y" searches.
- A switching reassurance right after the rival list, linking a switch page.
- Reasons written into table cells (not only ratings or ticks), so a cell quotes on its own.

## Rules that come out of review rounds
- One name per block everywhere: the order table, wireframe label, jump-link text, anchor and spec row carry the
  same words ("Where each platform leads" / #where-each-leads). A rename is a search across all five, plus the
  Appendix B landing map.
- Count language matches the set definition: "footers link the hub or its comparison pages", not "link comparison
  pages", when the set counts both.
- No recency claim a later post can break: name the role of a page ("a research post"), not its age ("the newest
  research").
- A figure's exemplar and the Appendix B best example name the same page.
- Shared CMS collections: say which fields this page adds to the collection another document defined.
