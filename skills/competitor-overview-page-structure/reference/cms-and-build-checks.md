# CMS fields and build checks: comparison hub

A default model. Adapt field names to the client's CMS; keep the rules. Placeholders: `<Client>`, `<Product>`,
`<Rival>`.

## CMS fields
One Competitors collection feeds the hub cards, the footer group and the comparison pages, and its template is the
comparison page. Launch the hub and its comparison pages on the same day: before then the items stay in draft, so a
draft rival shows no card, link or page (a hub launched first ships with no cards and an empty footer group). When a
sibling page (an industries, solutions or use-case page) already defined FAQ, Sources and People collections, reuse
them and say which fields the hub adds. A static hub page binds its byline and review date from a one-item "Page facts"
collection.

| Field | Type | Rule |
|---|---|---|
| Competitors: name, slug, order, footer order | Plain text, slug, number x2 | The name as the company writes it, slug `<client>-vs-<rival>`, card order, footer order for the main rivals |
| Category, also sells | Option, plain text | The rival's category from a short option list; "Also sells" shows as a second tag, hidden when blank |
| Best for, where <Client> differs | Plain text x2 | What the rival does well, in 6 to 12 words. One line on the client, under 20 words |
| Where the rival leads, where <Client> leads | Plain text x2 | One sourced line each, for the "Where each platform leads" block |
| In the footer | Switch | On for the main rivals |
| Last reviewed | Date | Shown on the rival's comparison page |
| SEO title, meta description, social image | Plain text x2, image | Title under 60 characters, for example "<Client> vs. <Rival> (<year>): Key Differences" (update the year when you review). Meta description within the client's own length rule (default below) |
| Page facts: author, reviewer, last reviewed, change log | Reference x2 (People), date, rich text | One item per hub page. A one-item list on the page holds the byline, the change log and the CollectionPage structured data built from the same fields, so every "Last reviewed" reads one date |
| People: bio link | Link | The bio each name links to (an about page until a team page exists) |
| Sources (shared): number, title, publisher, URL, date read, page, competitor | Number, plain text x2, link, date, option, reference | Page is an option so a list can filter on it; the hub lists its own sources sorted by number. Numbers restart on each page |
| FAQ items (shared): question, answer, page, rival | Plain text x2, option or switch, reference | Plain-text answers of 40 to 80 words for FAQPage markup. Hub questions leave Rival empty. Each question shows on one page only. No template page |
| Hub page copy: short answer, doubts, checklist | Rich text on the page | Edited on the hub |
| Comparison table (hub) | HTML embed or rich text | One HTML table, edited by hand with the review date. Cells as text. Its Best for cells repeat each card's Best for field word for word, and the quarterly owner edits both |

Meta descriptions: follow the client's own length rule. The author's default when the client has none: about 170 to
180 characters, or a short form of about 70 to 80.

### CMS notes (a few common platforms as examples)
Confirm each point on the client's own CMS; these are starting points, not a complete list.

Webflow:
- A text comparison table needs a code embed. A code embed cannot read CMS fields, and the Editor cannot change it
  (Designer access is needed): say who owns the table edits.
- A static page binds CMS fields through a one-item Collection List (the Page facts collection).
- Filtering a list needs Option fields.
- One FAQPage per page, as microdata custom attributes on the FAQ Collection List.
- Switch off template page publishing for FAQ, Sources and Page facts collections so no question, source or page
  record goes live as a page of its own.

WordPress:
- Model Competitors, Sources and FAQ items as custom post types with custom fields; keep the FAQ and Sources types
  out of the sitemap and without public single pages.
- A table block or HTML in the editor keeps the comparison table as text; avoid table plugins that render rows only
  with JavaScript.

Headless CMS:
- Content types map one to one to the field model above; the front end must render the table, cards and FAQ answers
  in the server HTML, not only after a client-side fetch.

## Build checks for search and AI answers

| Check | Rule |
|---|---|
| Live text | The short answer, table, cards, strengths and doubt answers are HTML text, visible on load. FAQ answers are in the HTML on load and may sit collapsed. Nothing that matters exists only after a script runs |
| Structured data | BreadcrumbList in the page code. CollectionPage with author, reviewedBy and lastReviewed from the Page facts item. ItemList on the cards and FAQPage on the FAQ list. No Review or AggregateRating markup for the client or its rivals |
| Collection pages | No FAQ, source or page-facts record publishes as a page of its own |
| Empty states | Hide the empty state of every list. A rival in draft shows no card or footer link, a tag with no value hides, a glossary link shows only once the glossary is live |
| Trademarks | Rival names in text only, no rival logos. How we compare carries the trademark and no-affiliation line. Analyst research only where the client's licence allows quoting it |
| Dates and sources | The hub and every comparison page show "Last reviewed <month year>" and a change log. One owner rechecks each rival every quarter and when a rival relaunches. Review-site rows keep their "as of" date |
| Names | Rivals' names as each company writes them, in the table, cards, titles and URLs |
| One page per search | Once the hub is indexed, any existing comparison landing page that stays carries noindex and links to the hub, so two client pages do not compete for the same comparison searches. Before design starts, pull that page's search queries for the last 12 months from the client's Search Console and carry any comparison terms into the hub's title and H1 |
| Internal links | Each card links its comparison page. Each comparison page links back to the hub and to two related comparisons |
| Measure | Before launch, take FAQ questions and tracked prompts from People Also Ask data first, add the comparison prompts ("<rival> alternatives", "<rival> vs <rival>", "best <category> platform") to the client's AI visibility tracking, and record which answers name the client in at least two assistants. Compare mentions, citations and search clicks 60 days after launch |
