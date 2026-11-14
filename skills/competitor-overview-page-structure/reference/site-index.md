# Site index: the shipped sample of comparison hubs

Contents: Leaderboard: which sites had the most reusable ideas · Every site · Notes files

Every public site whose comparison pages ship with this skill: 10 SaaS vendors and 5 hubs from other industries
(3 vendors, 2 marketplaces). Section type ids refer to `section-types.md`; block numbers to `section-model.md`;
codings live in `data/public_sample.py`. Open the leaderboard to see which sites had the most reusable ideas, then
the site's notes before re-reading the live page. Re-check anything dated before you reuse it: pages change. Before
a run, check that none of these sites is in the client's own category or competitor set; leave out any that is.

The client set (named rivals and category peers) and the review publishers you add on a run are not listed here:
record them in `CLIENT_SET`, and keep their notes with the client's working files.

## Leaderboard: which sites had the most reusable ideas

Ranked by how many section types a site is the named example for, then by blocks that cite it, then by types carried.

| Site | Group | Kind | Example for (types) | Cited in blocks | Types carried |
|---|---|---|---|---|---|
| Capterra | cross-industry | marketplace | 10 | 6 | 12 |
| Shopify | cross-industry | vendor | 6 | 4 | 11 |
| Zendesk | SaaS | vendor | 5 | 7 | 12 |
| Ahrefs | cross-industry | vendor | 5 | 2 | 8 |
| ClickUp | SaaS | vendor | 4 | 4 | 10 |
| G2 | cross-industry | marketplace | 4 | 4 | 8 |
| Asana | SaaS | vendor | 3 | 1 | 9 |
| monday.com | SaaS | vendor | 2 | 3 | 9 |
| HubSpot | SaaS | vendor | 1 | 0 | 5 |
| Semrush | cross-industry | vendor | 0 | 2 | 5 |
| Miro | SaaS | vendor | 0 | 1 | 5 |
| Intercom | SaaS (vs page only) | vendor | 0 | 1 | not coded (no hub) |
| Notion, Airtable, Webflow | SaaS (pages only) | vendor | 0 | 0 | not coded (no hub) |

## Every site

### Capterra
- Page: capterra.com/compare/ (marketplace compare hub).
- Example for: own rating with a scale (5), methodology (7), effort stats (8), paid-placement label (15), trust box
  (16), captioned screenshots (22), rival directory as pair cards (29), comparison builder (32), buying tips (36),
  advisor offer (43).
- Cited in blocks 4 (disclosure), 8 (evaluation strip), 11 (cards), 20 (checklist), 22 (how we compare), 24 (builder).
- Types carried: 1, 5, 7, 8, 15, 16, 22, 29, 32, 36, 43, 45. Notes: `public-benchmark-cross-industry-hubs.md`.

### Shopify
- Page: shopify.com/compare.
- Example for: rival directory with featured, single and three-way splits (29), segment tags (30), self-benchmark
  tool (33), migration reassurance (37), pricing snapshot (40), the same offer in the hero and the closing band (45).
- Cited in blocks 5 (button), 10 (compare by need), 19 (customer stories), 26 (closing band).
- Types carried: 1, 18, 29, 30, 31, 33, 37, 40, 42, 43, 45. Notes: cross-industry file.

### Zendesk
- Page: the comparison hub under zendesk.com/service/comparison/ (see the redirect note in the SaaS file).
- Example for: table with reasons in the cells (4), last-updated date (13), FAQ (38), anchor links (39), related
  posts (44).
- Cited in blocks 2 (hero), 9 (on this page), 12 (table), 19 (stories), 21 (FAQ), 25 (related), 27 (footer).
- Types carried: 1, 4, 5, 13, 17, 18, 29, 38, 39, 42, 44, 45. Notes: `public-benchmark-saas-hubs.md`.

### Ahrefs
- Page: ahrefs.com/vs (serves a single head-to-head).
- Example for: dated external ranking (17), paired data band (18), industry context (28), numbered exclusive features
  (42), downloadable brochure (43).
- Cited in blocks 6 (proof strip) and 17 (how the category is changing).
- Types carried: 1, 4, 17, 18, 28, 42, 43, 45. Notes: cross-industry file.

### ClickUp
- Page: clickup.com/compare.
- Example for: tabbed three-rival table (4), unbranded how-to-choose FAQ (36, 38), switching questions (37).
- Cited in blocks 12 (table), 20 (checklist), 21 (FAQ), 27 (footer Compare group).
- Types carried: 1, 4, 17, 18, 29, 36, 37, 38, 42, 45. Notes: SaaS file.

### G2
- Page: g2.com/compare.
- Example for: "how this list is built" notes (7), verified-review scale (8), category entry points (30), open
  "X vs Y" picker (32).
- Cited in blocks 8 (evaluation strip), 10 (compare by need), 22 (how we compare), 24 (builder).
- Types carried: 1, 7, 8, 29, 30, 32, 43, 45. Notes: cross-industry file.

### Asana
- Page: asana.com/compare.
- Example for: analyst plus review-site proof (17), a dated footnote (19), FAQ that answers rivals' objections (27).
  Cited in block 18 (doubts answered).
- Types carried: 1, 17, 18, 19, 27, 29, 38, 42, 45. Notes: SaaS file.

### monday.com
- Page: monday.com/alternative; a vs article against a work-management rival offers to run beside it.
- Example for: "Best for" line on every card (3), alternatives links as related reading (44).
- Cited in blocks 11 (cards), 14 (where the product fits, from its vs page) and 25 (related reading).
- Types carried: 1, 3, 7, 17, 29, 38, 42, 44, 45. Notes: SaaS file.

### HubSpot
- Page: hubspot.com/comparisons.
- Example for: product-line filters and tags (31).
- Types carried: 1, 17, 29, 30, 31. Notes: SaaS file.

### Semrush
- Page: semrush.com/vs/. Cited in blocks 5 (button) and 6 (proof strip).
- Types carried: 1, 17, 18, 29, 45. Notes: cross-industry file.

### Miro
- Pages: miro.com/compare/ and its alternatives index. Cited in block 26 (closing band).
- Types carried: 1, 17, 18, 29, 45. Notes: SaaS file.

### Intercom
- No hub; a why-choose page and a flagship vs page that offers to work beside the rival. Cited in block 14.
- Notes: SaaS file.

### Notion, Airtable, Webflow
- No coded hub (pages only). Their navigation and vs-page patterns are in the SaaS file and in
  `data/public_sample.py` (navigation and vs-page sections).

## Notes files

| File | Sites |
|---|---|
| `public-benchmark-saas-hubs.md` | Airtable, Asana, ClickUp, HubSpot, Intercom, Miro, monday.com, Notion, Webflow, Zendesk |
| `public-benchmark-cross-industry-hubs.md` | Ahrefs, Capterra, G2, Semrush, Shopify |
