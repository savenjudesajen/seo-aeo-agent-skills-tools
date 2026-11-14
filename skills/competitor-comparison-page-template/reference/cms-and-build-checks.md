# CMS model and launch checklist

A starting point for building the template in any headless or visual CMS. Rename things to match the site and keep
the intent. Ranges are suggestions; follow the company's style guide where it has one.

## How to model it
- **One item per rival.** The comparison page is the template page of a rival collection. If the site already has a
  collection for competitors (for example one that feeds a hub page), extend it rather than starting a new one.
- **Template text versus per-rival text.** Anything true on every page (the company's own pricing model, its
  onboarding steps, the method note) lives once in the template. Only what changes by rival goes in fields.
- **Rows as their own collection.** Store table rows separately (label, position, rival, the two cells, who leads,
  source numbers) so every page renders the same labels in the same order, and a new row reaches every page at once.
- **Reuse shared collections.** Sources, authors and FAQ entries are usually shared with other templates. Filter them
  by rival on the page rather than copying them.
- **Empty means hidden.** Optional blocks (company context, rival-specific proof, the take-away file) disappear when
  their field is empty, so a thin page never shows a blank heading.

## Fields per rival, in page order

| Area | Field | Guidance |
|---|---|---|
| First screen | Difference line | One sentence, roughly 12 to 25 words, in the rival's category terms. |
| First screen | Short answer | Three to five bullets; each claim also appears, sourced, in the table. |
| Orient | Choose lists | Two short lists, one per product, two to four lines each. |
| Evaluate | Where each leads | A few points per side, a bold lead-in and one sentence; the rival's side first. |
| Evaluate | Shared ground | A handful of one-line points. |
| Evaluate | Question sections | Up to five pairs of heading plus body; the heading carries the answer, the body is one short paragraph. |
| Evaluate | Working together | What the rival keeps doing, what the product adds, how they connect. |
| Evaluate | Rival pricing | What the rival publishes, or "not published", plus the date checked. |
| Evaluate | Company context | Optional dated line with a source link. |
| De-risk | Rival-specific proof | Optional quote or rating with source and date. |
| De-risk | Getting started note | One line specific to switching from this rival. |
| De-risk | Byline and log | Writer and checker (references to the authors collection) and a dated change log. |
| Convert | Related pages | Two or three references to other comparison items. |
| Convert | Take-away file, AI prompt | Optional; a prompt, if used, is neutral and names the page address. |

Row collection: label, position, rival, company cell, rival cell, who leads (company, both, rival), source numbers.
Keep each cell to a single sentence.

## Before launch

**Rendering and markup**
- All comparison content is in the HTML on first load; collapsed FAQ answers still sit in the markup.
- Structured data: WebPage with the review date and reviewer, BreadcrumbList, Person for the writer and the checker,
  and one FAQPage per page. In a CMS that only allows attributes on list elements, add microdata to
  the FAQ list: FAQPage on the list wrapper, Question with mainEntity on each item, name on the question text, and
  Answer with acceptedAnswer on the answer wrapper with text on the answer body (types from schema.org). Leave out
  Review and AggregateRating markup for both vendors.
- Items in the row, source and FAQ collections do not get public pages of their own; author pages may stay public
  for bios.

**Claims and sign-off**
- Each statement about the rival points to a source with the date it was read: the rival's own pages, a review site,
  or research the company may quote.
- A number says what it is compared with. Review-site scores appear for both vendors, with date and review count, or
  not at all.
- Legal approves the template, the row labels, the first page per rival and every new rival claim. Rival names in
  text only, no rival logos, and a trademark note in the method section.

**Site fit**
- No other page on the site competes for the same "<brand> vs <rival>" query; merge, redirect or de-index the
  duplicate as the hub plan decides.
- Each page is linked from the hub, a footer group, related comparison pages and relevant blog posts, and links back
  to the hub.

**Upkeep and measurement**
- Name an owner. Recheck each page on a fixed cycle (every few months) and whenever the rival changes its product or
  pricing; the review date, the change log and any year in the title move together.
- Track search impressions, clicks and position per page from your own Search Console connector or export.
- Track AI answers for prompts about each rival that do not name the company (start from People Also Ask and AlsoAsked
  for the rival's alternatives and comparisons), using a prompt-tracking tool such as Profound or Peec AI. Note whether
  answers cite the page itself. Compare both against a baseline a couple of months after launch.
