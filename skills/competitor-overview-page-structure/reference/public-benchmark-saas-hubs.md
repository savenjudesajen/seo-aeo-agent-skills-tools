# Public benchmark: SaaS comparison hubs (10 vendors)

Contents: HubSpot · Zendesk · monday.com · Asana · ClickUp · Notion · Airtable · Webflow · Intercom · Miro · Patterns across the 10

Research notes on how well-known SaaS vendors build their comparison hubs, paraphrased (no page copy). Use them as
the vendor half of the cross-industry set and as a reference for navigation patterns. Pages change often: re-read a
page before you cite or capture it, and update its row in `data/public_sample.py` when it has moved. Section type
ids refer to `section-types.md`.

## HubSpot
- Hub: /comparisons, a "software comparisons library". Linked only from a footer free-tools group; a "Why HubSpot"
  header column does not link it. Individual pages have no breadcrumb.
- Pages: mostly `<rival>-vs-hubspot`, some reversed, plus category roundups ("best CRM") in the same folder; about two
  dozen, all listed. Alternatives posts live on the blog and are not linked from the hub.
- Sections: hero with a one-paragraph positioning line; filter chips by content type and product line; a card list
  (logo, "<Rival> vs HubSpot", product tags, a Compare button); a third-party proof block (a review-site ranking and
  badges). No FAQ and no closing band.
- Worth copying: product-line filters plus product tags on each card, so a multi-product vendor lets buyers narrow to
  the product they are evaluating; category-level entries sit beside head-to-heads. Types: 1, 17, 29, 30, 31.

## Zendesk
- Hub: a "why choose" page under /service/comparison/ (browsers were redirected to a newer why-us page while fetches
  were served the hub; counted from the served page, not used as a screenshot exemplar). Footer Compare group links
  three vs pages directly; vs pages carry a breadcrumb back to the why-us section and a cross-link block to the rest.
- Pages: `zendesk-vs-<rival>` under the hub folder plus a few outliers; alternatives listicles in the same folder.
- Sections: hero with two buttons; an intro with anchor links; an at-a-glance stats graphic; a three-vendor table
  with qualitative ratings and the reason written into the cell (including total cost of ownership); seven
  differentiator blocks, each with a customer quote or stat; customer stories grouped under the rival each customer
  left; a four-question FAQ (including "who are the competitors"); a mid-page and a closing offer band; a text list of
  ten more comparisons; related posts. A visible last-updated date.
- Worth copying: switcher stories grouped by the rival left, reasons inside table cells, a dated hub, an FAQ that
  answers the competitor question directly. Types: 1, 4, 5, 13, 17, 18, 29, 38, 39, 42, 44, 45.

## monday.com
- Hub: /alternative ("alternatives and comparisons"). Linked from the footer Resources group, not the header.
- Pages: hub cards link blog comparison posts; separate `/alternative/<rival>` pages are linked from a related-content
  row; more vs posts sit on the blog.
- Sections: hero that states the data basis behind the comparisons (thousands of review-site reviews); eight rival
  cards (logo, a "Best for" line, a short neutral description, "Compare <Tool>"); a feature showcase; a short FAQ;
  related alternatives links; compliance badges; a closing band.
- Worth copying: a "Best for" line on every card that concedes each rival a niche before the click; the evidence
  base stated in the hero; the hub doubling as an alternatives index. Types: 1, 3, 7, 17, 29, 38, 42, 44, 45.

## Asana
- Hub: /compare, written as an enterprise "why us" page. Not linked from the header or footer; vs pages do not link
  back.
- Pages: `/compare/asana-vs-<rival>`; titles double as alternatives targeting. One vs page exists that the hub does not
  list.
- Sections: hero with two buttons and a customer logo wall; a five-item differentiator accordion; ROI stats; analyst and
  review-site proof; icon links to eight rivals placed right after the proof; one customer quote; a six-question FAQ
  that pre-empts the objections rivals raise (limits, downtime, rollout time); a closing band with a footnoted claim
  and an "accurate as of" date.
- Worth copying: competitor links placed directly after third-party proof; FAQ answers to the doubts rivals plant.
  Types: 1, 17, 18, 19, 27, 29, 38, 42, 45.

## ClickUp
- Hub: /compare, framed around switching. Not linked from the homepage nav; a footer Compare group lists eleven vs pages
  and a Help group links an import page.
- Pages: a core set at `/compare/<rival>-vs-clickup` and a long tail at `/compare/vs/<rival>`; alternatives posts on the
  blog, including its own.
- Sections: hero with an aggregate review rating; a tabbed table against three featured rivals with three-state cells
  (included, limited, not included) and a full-comparison link per tab; three differentiator blocks; integrations;
  security badges; a nine-question category-level FAQ (how to choose, switching, importing, pricing); a text list of
  two dozen comparisons including three-way pages; customer logos; a switch-framed closing band.
- Worth copying: the tabbed three-rival matrix with deep links, an FAQ written for unbranded buyer questions,
  three-way comparisons inside the list. Types: 1, 4, 17, 18, 29, 36, 37, 38, 42, 45.

## Notion
- No hub. Most indexed comparison URLs now redirect to the homepage; one switch page against a wiki tool is live.
  Not linked from nav.
- The live page is framed as a switch page (switch-titled, an importer named as proof of low switching cost, a
  "ready to move" close). Retiring comparison URLs into homepage redirects throws away their links and rankings.

## Airtable
- No hub (/compare returns 404). Three head-to-heads at the root plus two function-level pages ("for <department> vs
  others") that compare three rivals in one table and link a review-site comparison. Alternatives articles in a
  separate folder. Not linked from nav.
- Worth copying: function-led multi-rival pages that match how a department buys.

## Webflow
- No hub (/vs returns 404). A footer Compare group with five vs links repeats on every page and works as a
  site-wide index. Vs pages at `/vs/<rival>` pair the comparison with a total-cost estimate and a migration guide;
  alternatives posts on the blog.

## Intercom
- No hub. A rival-agnostic "why choose" page (numbered reasons, pricing, FAQ, customer quotes) carries the
  positioning and is linked from the footer and a header menu; named comparisons live in a learning-centre folder and
  on a sister product domain, plus one flagship vs page that opens with switcher quotes. The flagship vs page says its
  AI agent works with any helpdesk, the rival included.
- Worth copying: the coexistence line ("works with the tool you already run"), and FAQ answers on lock-in and
  integrations.

## Miro
- Two hubs that cross-link: /compare (two dozen head-to-heads as text links) and an alternatives index (about seventy
  "<tool> alternatives" pages). Neither is linked from nav; vs pages do not link back. Every title tag carries the
  year.
- Sections: hero with a review-site claim and a sign-up button; the text list; a cross-link to the alternatives index;
  a closing band; a site-wide trust row (compliance badges and an aggregate review count).
- Worth copying: covering "<Brand> vs X" and "X alternatives" demand on two linked hubs without mixing them.
  Types: 1, 17, 18, 29, 45.

## Patterns across the 10
- 6 have a hub (all readable), 4 rely on standalone pages. None puts a comparison hub in a header slot; the footer is
  where hubs live, and footer Compare groups of direct vs links often stand in for a hub link.
- Hub paths: /compare is the most common; others use /comparisons, /alternative or a why-us path. Child slugs are
  mostly `<brand>-vs-<rival>` or `<rival>-vs-<brand>`; some use the rival alone.
- Hubs list from about 8 to about 26 comparisons; half of them list about two dozen.
- Plain text links dominate; rich cards (logo, best-for line, product tags, a verb) are the minority.
- Common stack: hero with positioning, rival list, third-party proof, closing band. A review site is the default proof
  source; analyst proof is rare.
- Multi-rival tables on the hub are uncommon and take different forms (qualitative ratings with reasons, a tabbed
  three-state matrix). Four of the six hubs carry an FAQ.
- Dated statements appear where claims are specific (a last-updated date, an "accurate as of" footnote).
- Alternatives pages usually sit apart from the hub (blog or guides); only a few connect an alternatives index to the
  hub.
- Head-to-head pages (8 read): 2 of 8 offer to run beside the rival; 5 put their own brand first in the URL; 7 carry
  a table; 7 carry an FAQ and 6 of those include a switching question; only 1 names an author, 2 show an updated
  date and 2 show review-site ratings.
