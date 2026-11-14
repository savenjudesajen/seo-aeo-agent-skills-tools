# CMS model and launch checklist: industries pages

A checklist to adapt, not a finished spec. Name the fields in the client's CMS (Webflow collections, HubSpot custom
modules or HubDB tables, WordPress custom post types with custom fields) and tune the limits to the client's design.

## Principle: write each fact once
Everything that appears in more than one place (an industry's name, a figure, a person, a source) lives in one CMS
item and is referenced wherever it shows. The menu, the directory, the jump bar, the footer and the industry pages
then cannot drift apart, and a draft item disappears everywhere at once.

## Collections and what each needs

**Industries** (one item per industry)
- Identity: display name exactly as the menu shows it, a plain slug, a sort order shared by every list.
- Directory entry: one line in the industry's vocabulary (roughly 8 to 15 words) and an optional hook (a standard,
  a regulation or a proof point the client has confirmed).
- Overview answer block: a short "what is changing" opener, a question-shaped heading (keep it under about 90
  characters) and an answer (roughly 50 to 80 words), plus references to one figure and one piece of proof.
- Industry page: hero heading and a short answer naming the buyer types (roughly 30 to 40 words), a point of view
  written for this page only (never the overview text again), priorities with their matching resources,
  capabilities written as outcomes, the standards or regulations the product supports, two sibling industries.
- Search fields: SEO title (under about 60 characters, leading with the industry's search term), meta description
  per the client's house rule, social image.
- Review fields: a reviewer (reference to People) and a last-reviewed date.

**Figures** (one item per number)
- Value, a label that says what was measured and over what period, source title, source URL, source date, industry
  reference, and a switch for "show on the overview".

**Sources**
- Number, title, URL, date read, and the page it supports. Feeds the numbered source list on each page.

**People**
- Name, role, credential, photo, short bio, and a team page. Used for reviewers and industry leads.

**FAQ items**
- Question, plain-text answer (roughly 40 to 80 words), industry reference, a switch for "show on the overview",
  optional glossary link. Each question shows on one page only.

**Existing collections**
- Add an industry reference field to blog posts, reports, events and case studies, so the research row and the
  proof block can filter by industry.

## Before launch
- [ ] The overview publishes the same day as the first industry pages, returns 200 and links every live industry
      page. The obvious parent address works.
- [ ] No placeholder or test copy, and no placeholder alt text, on any crawlable address.
- [ ] Answers, figures, standards, directory lines, event details and FAQ answers are in the HTML on load: no hover,
      click, tab or carousel needed to see them.
- [ ] Every figure shows its source and date; every page shows Reviewed by and Last reviewed.
- [ ] Menu, coverage count, directory, jump bar and footer list the same industries in the same order.
- [ ] Product and plan names are spelled the same on every page.
- [ ] Empty lists hide themselves (an industry with no event yet shows no empty row); links to pages that are not
      live stay hidden.
- [ ] Helper collections (Figures, Sources, FAQ) do not publish item pages of their own.
- [ ] Each industry page links the overview and two sibling industries; every tagged post, report and event links
      its industry page.

## Structured data
- Overview: CollectionPage with lastReviewed and reviewedBy, BreadcrumbList, an ItemList of the industry pages, and
  one FAQPage for the overview FAQ.
- Industry page: WebPage with `about` set to the industry, lastReviewed and reviewedBy, BreadcrumbList, and one
  FAQPage for that industry's questions.
- When the CMS renders lists from collections, attach ItemList and FAQPage as microdata on the list wrapper and its
  items (itemscope, itemtype, itemprop mainEntity, acceptedAnswer, text) rather than hand-written JSON-LD that can
  drift from the visible list.
- Validate with Google's Rich Results Test. Markup must match visible content: no FAQPage without a visible FAQ.

## CMS notes
- Webflow: a visibility switch on an item does not stop its collection page from publishing; keep unfinished items
  as drafts. One Collection List shows one collection, so a mixed row (report, post, event) is several lists side by
  side, each filtered and limited. FAQ answers read by FAQPage markup must be plain text.
- HubSpot and WordPress: the same model works with HubDB tables or custom post types; check that list modules can
  filter by the industry reference.

## After launch
- Add tracked prompts for each launch industry to the client's AI-visibility tracking (questions from People Also
  Ask and AlsoAsked), and compare mentions and citations after about two months.
- One owner rechecks every figure each quarter and whenever a source publishes a new edition; the last-reviewed date
  changes only when a figure, an answer or a standard changes.
