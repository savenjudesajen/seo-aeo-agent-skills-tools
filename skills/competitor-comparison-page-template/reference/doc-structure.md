# The extended deliverable: content groups, block notes, writing rules, review, covering message

> Extended build only. The default deliverable is the two-section lean doc in `reference/lean-doc.md`. Use this file
> only when the user asks for the full template doc.

Built with `data/build_extended_doc.py` from a content spec (start from `data/extended_spec_example.py`). Block
model `data/packed_vs.py`; wireframes `data/wire_vs.py` (three desktop parts and a phone view, drawn from
`packed_vs.VS` so the wireframes and the order table cannot drift). A full build runs long; keep every part to
what a designer and a writer need.

## Content groups
Order them to suit the reader; these are the groups a full template doc needs, not a fixed table of contents.
- **Overview.** Title, a one-line meta (what it is, for whom, the month) and a short lead: what the company has
  today, the benchmark behind the template, the block count, and the gaps the benchmark leaves open (few vendors
  concede anything, none names a checker). Then a short choices table (choice, reason from the benchmark) and the
  desktop wireframes.
- **Block order.** The status tally, the generated order table (stage, block, status, count with its base, best
  example), a line on what is needed at launch and what can follow, and the phone wireframe.
- **Stages.** The generated stage table with one line on the job of each stage.
- **Block notes.** One note per block, keyed by the block number and name from `data/packed_vs.py` (the `{blk:key}`
  token). What each note must settle is below.
- **Existing content map.** Each piece of comparison content the company already has, and the block it moves into
  (kept, merged, renamed, or left out with the reason).
- **Rival categories.** How the template changes by type of rival (table below).
- **Site placement.** URL pattern, titles, meta descriptions and internal links (below).
- **CMS model and launch checks.** From `reference/cms-and-build-checks.md`.
- **Appendices.** The benchmark pages; the section library (50 types: counts, best example, where each lands);
  and, kept private, what the client's own rival set showed, each count out of that set.

## Block notes
Each note: one to three figures (`reference/exemplar-library.md`), each captioned with what the capture shows; a
two-line label table (what the block gives a buyer, what it gives an AI answer, with a count and its base); then the
rules below in the company's own words. A note that covers blocks with different statuses shows each block's status.
Write all sample copy fresh for every company.

- **Hero, button and proof strip (blocks 1, 4, 5).** Breadcrumb path with markup; an H1 naming both products, the
  rival spelled as it spells itself; one quotable line on how they differ, checked against the rival's own claims;
  no rival logo; the hub's button label and target; a few proof points with a source line, never presented as a
  comparison.
- **Byline and disclosure (blocks 2, 3).** Who wrote the page and in what role, who checked it, the month of the last
  review, links to bios and to the change log. A disclosure in the company's words: who publishes the page, what it
  sells, how to send a correction, and a link to the method.
- **Takeaways and choose-if lists (blocks 6, 7).** A short set of bullets on what each product is for, including a
  point where the rival is the stronger choice and whether the two can be used together; every claim also appears,
  sourced, in the table. Two short lists of who should pick which, the rival's list in terms its customers would
  agree with.
- **On this page (block 8).** The site's existing jump-link component; labels that carry the answer where possible;
  short, stable anchors named after the blocks (for example #summary, #table, #pricing, #switching, #questions,
  #sources); a compact menu on phones.
- **The table (block 9).** One row set shared by every comparison page and the hub; a sentence per cell; a numbered
  source on every claim about the rival; a tag on each compared row saying who is ahead ({Company}, Both or <Rival>),
  with at least one row where the rival is ahead. Open with a who-it-suits row and close with a buying row; neither
  needs a tag. The review month and sources sit under the table; the table is live HTML with no icons.
- **Where each one leads and shared ground (blocks 10, 11).** Two columns with the rival's strengths on the left; a
  few points per side, each a bold lead-in and one sourced sentence; where the company's product gives something up,
  say so. Then a short list of what both do, so readers know which rows they can skip.
- **Sections by buying question (block 12).** Up to five headings written as the buyer's question with the answer in
  the heading, a short body each, a link to the matching product page, an optional tip line; hide a section that has
  nothing to say.
- **Working together (block 13).** What <Rival> keeps doing (from its own pages), what {Product} adds, and how they
  connect (an integration, an import, an export). Name an integration only after the company confirms it.
- **How each one is bought (block 14).** The company's pricing model, first step and terms as it approves them; the
  rival's published pricing with source and date, or "not published" with the date checked.
- **Security and company context (blocks 15, 16).** Certifications for both products from each company's trust
  page, with scope and date, once the company supplies its own; dated, sourced lines on the rival's ownership or
  product changes, hidden when empty.
- **Proof against this rival (block 17).** A quote from a customer who uses both or moved over, with role and date;
  review-site ratings for both with site, score, review count and date, or none at all; outside research, dated and
  linked. Hidden until a rival has such proof. Say what each number is measured against.
- **Getting started (block 18).** The steps a new customer actually takes, as many as the company's onboarding has
  (for example a trial or call, then setup or import, then first value); one line specific to this rival from the CMS.
- **FAQ (block 19).** A handful of questions per rival (four to eight), seeded from People Also Ask and AlsoAsked for
  the rival's alternatives and comparison queries. Useful seeds: which is easier to set up; does {Product} work with
  <Rival>; how do I move my data from <Rival>; how is {Product} priced compared with <Rival>; when is <Rival> the
  better choice. Short answers that stay in the HTML when collapsed; each question lives on one page only.
- **Method and sources (blocks 20, 21).** Who wrote and who checked, with a one-line credential each; what was checked
  on each product and when; a change log under its own anchor; how to report an error; a trademark note from the
  company's legal team. Numbered sources: title, publisher, date read, link.
- **Product in action (block 22).** One annotated screenshot of the company's own product with customer data blurred,
  supplied by the company; never a capture of the rival's product.
- **Take-away, related pages, AI prompt and closing (blocks 23 to 26).** An optional ungated one-page PDF; two related
  comparisons from the same category, then the full list; an optional AI-assistant link whose prompt is neutral and
  names the page (never one that argues the company's case); a full-width closing band with one sentence and the
  hero's button.
- **What the company must supply.** A short table (block, what is needed, who supplies it) for every block whose
  status is Later.

## Rival categories
Columns: Launch rivals | Main question for the summary | Where the rival is stronger | What a customer of the rival
keeps using. One row per category of rival. Under the table, settle: which of the rival's products the comparison
is against (many rivals sell more than the product they are known for, so name it in the column heading), which
pages carry company context from day one, the order in which later rivals get pages, and whether rival-versus-rival
pages are in scope.

## Site placement
- One URL pattern for every page, lowercase, brand first by default (for example /compare/{company}-vs-<rival>).
- A breadcrumb with BreadcrumbList markup.
- A title under 60 characters that names both products; if it carries a year, the year changes with the last review.
- A meta description that states the difference and the month of the last review.
- Linked from the hub, the footer and related comparisons; comparison pages seldom sit in the main menu.

## Writing rules (on top of the brand's own writing guidelines, if it has them; `data/qc_copy.py` is carried)
- Template only: example copy uses <Rival> placeholders, phrased per rival category, checked against each rival's own
  claims before use. Wireframes never carry a claim about a named rival.
- No price its owner does not publish.
- Company context carries a date and a source.
- Quote benchmark pages only after re-reading the capture; say what a footnote says a number measures.
- One base per cell, stated. Counts live in the overview, the block order, the label tables and the appendix.
- Spell out product and category acronyms on first use.
- Write for the reader of the doc; refer to the company in the third person when the reader is a third party.

## Fresh-context reviewer (ask the user first)
Dump the doc with `python3 data/dump_text.py <doc> > doc_text.txt`, then run a general-purpose sub-agent:
```
You are a fresh-context reviewer for a recommendation document. Do not edit any files; return a review as your
final message.
FILES: doc_text.txt (reading order; one-cell [TABLE] blocks are section bands; figures appear as captions and source
lines); packed_vs.py and section_library.py (every count comes from them; state the bases); the content spec (each
figure names its image and caption); the image folder (open every image, including the wireframes); the benchmark
notes; the sibling docs' text dumps for consistency.
CONTEXT: <who wrote it, who reads it, the company, never-mention list, status legend>. You may fetch the company's
live pages to check claims about its site.
CHECK: 1 counts and examples against the data; 2 captions against images; 3 consistency between the order table,
wireframes, stage table, block notes, rival-category table, site placement, CMS tables and launch checks; 4 fairness to rivals and
trademark handling; 5 human prose, no internal dialogue; 6 usability for a designer and a content writer (where,
what, mobile, empty states); 7 factual risk (company statistics, rival claims, coexistence position, review markup).
RETURN: numbered issues, most important first, with the quoted line, the problem and a rewrite (no em dashes, no
"rather than"), then a one-line verdict.
```
A review round on a long doc costs time, so ask before spending one; self-review every caption against its capture
regardless, and re-check every count against the data.

## Covering message (draft only; never sent without a yes)
Keep it brief: name the document and the size of the benchmark, give three to six findings that each carry a count
and its base, and end with one line on what the document contains. Write it fresh for each company and reader.
