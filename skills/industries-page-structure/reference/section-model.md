# Section model: blocks for the industries overview page and the industry page template

The 45 section types (`reference/section-types.md`) grouped into blocks a designer builds. The grouping, order,
counts and best examples live in `data/benchmark.py` (`OVERVIEW`, `TEMPLATE`, `SITE`), so the doc, the wireframe and
these tables print the same thing. Counts below come from the public sample (12 overview pages, 12 industry pages).
Once you code the client set, the script prints combined counts: use those in the doc.

This is a starting grouping, not a template to copy. Merge, split or reorder blocks for the client's buyers and
proof, and say why in the doc.

## Prevalence labels (from the public sample only)
- **Common**: 6 or more of the 12 pages carry it. Buyers expect it; leaving it out needs a reason.
- **Less common**: 2 to 5 of 12. Adds depth; often the place to stand out.
- **Rare**: 1 of 12. Worth it when the client has the material.
- **Not seen**: open ground. No page in the sample does it; count it as a new type before you claim it.

## Statuses (set per client, never preset)
Set each block's status against the client's live site in `CLIENT_STATUS`, and define the words once in the doc:
- **Keep**: already on the client's site in the right form.
- **New**: nothing like it exists today.
- **Rework**: the content exists elsewhere on the site and moves here in a new form.
- **Optional**: adds reach, never blocks the launch.
- **Later**: waits for content only the client can supply. List what each one needs.
Rule of thumb: a block is New unless its content already exists elsewhere on the site (Rework) or depends on
material the client does not have yet, such as published stories, research, recognition, a trust page or named
people (Later).

## Overview page: 15 blocks in six zones
| # | Zone | Block | Pages with it | Prevalence | Best examples |
|---|---|---|---|---|---|
| 1 | Top of page | Hero: H1, a 40 to 60 word answer naming the industries served, one button | 12 of 12 overview pages (3 with a button) | Common | SAP (industry page), IBM |
| 2 | Top of page | Proof beside the answer: scale figures, results or a recognition, each sourced | 7 of 12 overview pages | Common | AWS, IBM |
| 3 | Find your industry | Industry directory: a coverage count, then one entry per industry with a line in its own vocabulary | 12 of 12 overview pages (9 give each industry a line, 2 state a coverage number) | Common | Deloitte, AWS, Accenture |
| 4 | Find your industry | A second route in, by problem, process or job | 3 of 12 overview pages | Less common | SAP, Microsoft |
| 5 | Find your industry | Jump navigation: breadcrumb and a sticky bar of anchors | 8 of 12 overview pages | Common | PwC, Microsoft |
| 6 | Answers per industry | One open, anchored block per industry: challenge, question-shaped H2, answer, a sourced figure, standards, proof, link | None of 12 overview pages, 8 of 12 industry pages | Not seen on overview pages | Deloitte (industry page), Adobe (industry page) |
| 7 | Answers per industry | Why the company: differentiators or a paragraph of named firsts | 3 of 12 overview pages | Less common | AWS, Oracle |
| 8 | Evidence | Stories and results tagged by industry | 3 of 12 overview pages | Less common | Microsoft, IBM |
| 9 | Evidence | Research, outlooks and events: typed, dated cards per industry | 5 of 12 overview pages | Less common | PwC, IBM |
| 10 | Evidence | Recognition: firm, report, year and placement | 2 of 12 overview pages, 4 of 12 industry pages | Less common | IBM, Accenture |
| 11 | Questions and trust | FAQ in the buyer's words, answers in the HTML | 1 of 12 overview pages, 1 of 12 industry pages | Rare | Microsoft, SAP (industry page) |
| 12 | Questions and trust | Trust and standards: a line with links to the evidence | 1 of 12 overview pages, 4 of 12 industry pages | Less common | Microsoft, SAP (industry page) |
| 13 | Questions and trust | People: named industry leads, and a Reviewed by line with date and sources | None of 12 overview pages, 6 of 12 industry pages (none show a reviewer or page date) | Not seen on overview pages | Deloitte (industry page) |
| 14 | Questions and trust | Suggested questions for an AI assistant | 1 of 12 overview pages | Rare | Microsoft |
| 15 | Next step | Closing band: the one offer, a newsletter option, related links | 10 of 12 overview pages | Common | AWS, McKinsey |

Site-wide, specified with the navigation (`reference/navigation-and-urls.md`): an announcement banner pointed at the
newest research or event (2 of 12 overview pages, IBM), a By industry menu group and an Industries footer group
(both counted on the client set).

## Industry page template: 12 blocks
| # | Block | Industry pages with it | Prevalence | Best examples |
|---|---|---|---|---|
| 1 | Hero: industry H1, a 30 to 40 word answer naming the buyer types, button | 12 of 12 | Common | SAP |
| 2 | Jump navigation | 9 of 12 | Common | PwC, Adobe |
| 3 | Segment links, a page per segment | 9 of 12 | Common | AWS, Microsoft |
| 4 | Point of view: the industry's challenge, with sourced figures | 8 of 12 (1 with a named source for every figure) | Common | Deloitte, Adobe |
| 5 | Priorities mapped to capabilities, each with a matching resource | 10 of 12 | Common | IBM, Oracle |
| 6 | Standards, regulations and trust evidence | 4 of 12 | Less common | Microsoft, SAP |
| 7 | Partners mapped to industry jobs | 4 of 12 | Less common | Microsoft |
| 8 | Proof: stories, results, quotes and recognition | 11 of 12 | Common | Microsoft, Adobe |
| 9 | Research, outlooks and events for the industry, dated | 12 of 12 | Common | McKinsey, Deloitte |
| 10 | People: the industry lead, and a Reviewed by line with sources | 6 of 12 (none show a reviewer) | Common | Deloitte |
| 11 | FAQ for the industry | 1 of 12 | Rare | SAP |
| 12 | Closing band with two sibling industries | 10 of 12 | Common | Microsoft, AWS |

## Why this order
- **Answer first.** A reader arrives from search, an AI answer or the menu wanting to know whether the company serves
  their industry. The hero answers that in text, with proof beside it, before anything asks for attention.
- **Then routes, not reading.** The directory, the second route and the jump bar get each reader to their own
  industry or problem in one move. A long page is fine when nobody has to scroll through other industries.
- **Then the substance, per industry.** Each answer block is self-contained, so it can be linked, quoted and cited on
  its own, and it carries its own figure and proof.
- **Evidence, then questions.** Stories, research and recognition show the claims hold; the FAQ, trust line and named
  people answer what a buyer asks before a call.
- **One next step.** The closing band repeats the hero's offer with the same label.

## Open ground in the public sample
- **A named reviewer and a review date**: none of the 24 pages shows one. The cheapest authorship and freshness
  signal an industries page can add.
- **Per-industry answers on the overview**: no overview page carries them; the industry pages that state a challenge
  or a sourced figure are the model.
- **Sourced figures on the overview**: no overview page carries one in its body.
- Anything in "Not seen on any of the 24 pages" (`reference/section-types.md`) that the client's proof supports.

## Principles for every block
- **One offer, one label** in the hero and the closing band. The site menu can keep its own button.
- **The industry's own words.** Write each line in the vocabulary that industry's buyers search with: a law firm
  looks for matter intake and conflict checks, a university for enrolment and term dates, an airline for aircraft
  turnaround.
- **Sourced, dated numbers**, checked against the original report, replaced when the source publishes a new edition.
- **Open, anchored blocks.** No tabs or carousels for industry content: readers and crawlers should see every
  industry without a click.
- **Lists in step.** Menu, coverage count, directory, jump bar and footer name the same industries in the same order.
- **Proof near the claim.** An answer block with no industry proof yet runs its figure full width rather than
  inventing proof.

## Mobile
Directory entries go one per row under 768px and two up to 1024px. The hero stacks H1, answer, button, then proof.
Each answer block stacks its figure and proof under the answer. The jump bar becomes a "Jump to" menu.
