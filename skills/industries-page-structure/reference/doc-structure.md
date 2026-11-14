# The deliverable: structure, writing rules, review, reply

A Word .docx built by `data/build_industries_doc.py` (neutral default layout, python-docx and Pillow) from the block
models in `data/benchmark.py` and the wireframes from `data/wire_industries.py`. When the client or agency has its own
document template, rebuild the structure in it (see `doc-template-design`).

## Shape the outline to the starting point
There is no fixed outline. Pick the parts that answer the client's situation, in this order of priority:
- **No industry pages yet**: lead with the overview page and the launch set, then the template, then navigation.
- **Industry pages but no overview** (the worked example): lead with the changes by impact, then an audit of the
  existing pages (keep, rework, merge), then the overview, the template, and a redirect map.
- **An overview page that underperforms**: lead with a gap review of the current page against the block model,
  what already works first, then the changes.
- **A design file to review**: lead with block-by-block verdicts on the design, then specs the developer needs.

Parts most docs need:
- Title, meta line (page structure recommendation, client, prepared for, month) and a lead paragraph: the client's
  starting point, what the doc recommends, the benchmark in one sentence (companies, pages, section types).
- **The changes**: five to seven decisions in a table (change, why with a count and its base, best example).
- **What exists today**: the client's current pages, menu and proof, with a verdict for each, and every figure on
  the live site checked against its source.
- **The overview page**: the block table (zone, block, status, pages with it, best example), the wireframe, the
  launch wireframe with Later blocks left out, and short specs for the blocks that need them.
- **The industry page template**: the block table and specs; the launch-set table when industries are new
  (coverage, demand, client proof), and fallbacks for launch.
- **Benchmark examples**: captures grouped by theme or by block, each captioned with exactly what it shows.
- **Navigation, URLs and redirects** (`reference/navigation-and-urls.md`).
- **CMS model and launch checklist** (`reference/cms-and-build-checks.md`), condensed to what the client's CMS needs.
- **Appendices**: the companies in the benchmark; the section library with where each type lands; client-set menu
  and footer counts and any combined counts with what they add up.

## Specs for a block
For each block that needs one: what it gives the buyer, what it gives an AI answer (with a count and its base), then
the spec: heading wording, position, word or character limits, what each element holds, where it links, when it
hides, and one finished example in quotes. For Later blocks, what the client must supply.

## Writing rules for this doc
- Decide the voice from the reader: "your" for the client's own team, third person for an agency or designer.
- One base per count, and say it: menus (client set only), overview pages (all), industry pages (all).
- Every company named for a block is in that block's set (the builder's `seen_hub()` / `seen_ind()` assert it).
- Define the status words once.
- Examples of page copy go in quotes (the copy gate treats quoted questions as quoted material).
- Standards and regulation copy: only what the client confirms.
- No process words (how pages were read, which tool captured what). The appendix states the base and the capture
  month.
- Wireframe, block tables, specs, navigation labels, CMS model and checklist must agree. Generate what you can from
  `benchmark.py`; check the rest by hand.

## Layout notes
- Each numbered part starts on a new page. A stub page means trimming the part before, not shrinking the type. Break
  the page before a subsection when its figure and its table would otherwise split.
- Figures scale to fit; a wide table capture gets the full text width.

## Fresh-context reviewer (ask the user before spending a round)
Dump the doc with `python3 data/dump_text.py <doc>.docx > doc_text.txt`, then run a general-purpose sub-agent:
```
You are a fresh-context reviewer for a client-facing recommendation document. Do not edit any files; return a review
as your final message.
FILES: doc_text.txt (reading order; tables appear between [TABLE] markers; figures appear as captions and source
lines); benchmark.py (every count comes from it); build_industries_doc.py (each figure call names the image and
caption); the image folder (open every image); the reading notes behind the data.
CONTEXT: <who wrote it, who reads it, the client, words the client does not want used, status legend>. You may fetch
the client's live pages to check claims about its site.
CHECK: 1 counts and examples against the data; 2 captions against images; 3 consistency between the block tables,
wireframe, specs, template, navigation, CMS model and checklist; 4 human prose, no internal dialogue; 5 usability for
a designer and a content writer (where, what, mobile, empty states); 6 factual risk (standards, claims about the
client's site, cited statistics).
RETURN: numbered issues, most important first, with the quoted line, the problem and a rewrite (no em dashes, no
"rather than"), then a one-line verdict.
```
Check the review's claims about the client's own site (button labels, product names, people's titles) against the
live pages before you accept them. Fix every material issue, rebuild, re-run the gates.

## Chat or email reply (draft; never sent without a yes)
An intro line, five or six bullets (one per decision, each with the count that backs it), one line on what the doc
contains. No em dashes, no headings.
