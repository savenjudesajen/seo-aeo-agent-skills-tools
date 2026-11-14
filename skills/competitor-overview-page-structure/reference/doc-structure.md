# The deliverable: structure, writing rules, review, reply

## Outline
Built with `data/build_hub_doc.py` (python-docx, neutral layout), or with the doc-template-design skill in the
client's own template. Block model: `data/block_model.py`; wireframes: `data/wire_hub.py` (three desktop parts and a
phone view, drawn from `block_model.HUB`).

- Title "Structuring the <Client> competitor overview page"; meta line "Page structure recommendation · <Client> ·
  Prepared for <reader> · <month year>"; lead: what the site has today, the benchmark (client set plus the
  cross-industry sample), the number of hubs and section types, and the gap (who states their interest, who names an
  author).
- 1  What to build first: five or six decisions (#, Decision, Why, Seen on) and the three wireframe figures.
- 2  The recommended section order: the status legend and tally, the order table (#, Stage, Section, Status, Hubs
  with it, Best example), "What launches and what waits", the phone figure.
- 3  Why this order converts: the five stages and the conversion principles (fair reads as confident, say who
  wrote it, every claim checkable, text not symbols, one offer and one label, mobile behaviour).
- 4  What the client's site has today: 4.1 any existing comparison content (figure, what it is, verdict), 4.2 fixes
  before reuse (below).
- 5  Sections to build: one subsection per block or group of blocks in page order (hero; byline, disclosure and
  evaluation strip; short answer; on this page; compare by need and cards; the table in text; where each platform
  leads; where the product fits; category explainer, also considered and category changes; doubts and checklist;
  FAQ; how we compare and numbered sources; related reading, closing band and footer; Later blocks).
- 6  The comparison pages the hub lists: launch set (rival, category, why), URL pattern, what comes next, the
  template (competitor-comparison-page-template skill), page types after launch.
- 7  Navigation and URLs (menu and footer counts from the client set only). 8  CMS fields. 9  Build checks.
- A  The companies. B  The section library (45 types, count, best example, where each lands). C  Menu, footer and
  combined counts.

## Every subsection in section 5
One to three figures captioned with exactly what the capture shows and a source line (site path and month), then
For buyers, For AI answers (a count with its base) and one spec row per block labelled "Block N · Name (Status)".
Later blocks share a closing table: Block, Seen on, Needs from the client.

## Mobile notes (section 3)
One card per row under 768 px, two up to 1024 px. The hero stacks breadcrumb, H1, answer, byline, disclosure and
button, then the short answer and the proof strip two by two. The fit block becomes one card per tool, and On this
page a "Jump to" menu. The table shows the row labels, the client column and one rival picked from a select menu;
every column stays in the HTML (a script only hides columns).

## Fixes before reuse (section 4.2)
List the errors found in the existing content, each with its corrected line: spellings, duplicated or outdated
passages, and statistics checked against their sources. Every other place that mentions these fixes points here.

## Writing rules for this document (on top of the brand's own writing guidelines, if it has them)
- Write for the reader named on the cover (an agency, a designer, the client's team); the client is in third person
  when the reader is an agency.
- Fair to rivals in every example: a card concedes a niche before it says where the client differs; no "unlike X".
- Rivals named as each company writes them, checked on the rival's own site. Product names spelled one way
  throughout.
- Never write a line about a rival that the rival's own site contradicts. Rivals often sell more than they are known
  for (an acquisition adds a category): check the rival's current product pages before you assign its category.
- One name per block across the order table, wireframe, jump-link text, anchors and spec rows.
- Count language matches the set definition; no recency claim a later post can break.
- The figure for a block and the Appendix B best example name the same page.
- Shared CMS collections: say which fields this page adds to the collection a sibling document defined.
- Statistics the client cites are quoted with the report and its date, checked against the report itself; never a
  figure the report does not contain. Old survey figures get a current source or come out.
- Review scores carry their site, count and date. Never copy a score without its date.
- No process wording in the body or appendix: state the base and move on.

## Fresh-context reviewer (ask the user first)
Dump the document with `python3 dump_text.py <doc> > doc_text.txt`, then run a general-purpose sub-agent:
```
You are a fresh-context reviewer for a client-facing recommendation document. Do not edit any files; return a review
as your final message.
FILES: doc_text.txt (reading order; one-cell [TABLE] blocks are section bands; figures appear as captions and source
lines); block_model.py and public_sample.py (every count comes from them; bases: hubs, companies, menus and footers
read, comparison pages); build_hub_doc.py (each figure call names the image and caption); the image folder (open every
image, including the wireframes); the research notes behind the data.
CONTEXT: <who wrote it, who reads it, the client, the never-mention list, the status legend>. You may fetch the
client's live pages to check claims about its site.
CHECK: 1 counts and examples against the data; 2 captions against images; 3 consistency between the order table,
wireframes, stage table, specs, launch set, navigation, CMS table and build checks; 4 fairness to rivals and trademark
handling; 5 human prose, no internal dialogue; 6 usability for a designer and a content writer; 7 factual risk.
RETURN: numbered issues, most important first, with the quoted line, the problem and a rewrite (no em dashes, no
"rather than"), then a one-line verdict.
```
A first round typically finds a couple of dozen items: counts whose base drifted, captions that claim more than the
image shows, a block renamed in one place only, card or verdict wording that tips into attack, a missing rival,
exemplar swaps that left Appendix B behind, inconsistent button labels and dates. A second round finds a handful.
Ask the user before spending a third round; designer-side polish rarely needs one.

## Reply to the reader (draft; never sent without an explicit yes)
An intro line, five or six bullets each with the count that backs it, one line on what the document contains. No em
dashes. Deliver the file the way the user works (their connected folder or drive when there is one).
