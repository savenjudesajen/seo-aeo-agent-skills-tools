# What wins: the content strategy core of the deck

## The universal winning-page skeleton

The single most reusable asset in the engagement:

> **Question H1** -> **40-60 word answer-first block** -> **question-form H2s** -> **FAQ** -> **related links**

The answer block is what AI engines lift. Write for humans, structure for AI: answers are assembled from
content CHUNKS, not whole pages. The full eight-part skeleton is in `slide-execution-depth.md`.

## On-page signals that win citations

- Brand name plus the page's USP inside the first 200 words.
- A TL;DR or answer block at the very top.
- A named author with credentials (and `Person` schema).
- A visible "last updated" date.
- H3s for every enumerable item (types, steps, tools, FAQs): each becomes a liftable chunk.
- Simple, scannable prose: lists and tables outperform paragraphs for extraction.
- **Expert quotes and cited statistics.** The Princeton GEO study (Aggarwal et al., 2023) found adding
  quotations and statistics among the strongest single levers for visibility in generative answers. If the
  client has credentialed practitioners, put a short attributed quote on every key page. Competitors cannot
  copy the client's experts.

## Page-type economics (why the build order is what it is)

From the competitor Pareto work (`competitor-pareto-analysis.md`): knowledge-hub and glossary pages
usually earn far more traffic per page than blog posts, and the glossary is the most AI-citable unit there
is (a definition IS an answer). Confirm the pattern holds in this client's category with the page-type
table before you recommend it.

**Default build order: 1) Glossary 2) Knowledge hub 3) Guides 4) Blog.**
Blog is volume and comes last. This inverts what most clients expect, so show the traffic-per-page table.

## Glossary strategy

- The cheapest, most citable win. Substantial term pages (often 1,000-1,500 words), each a real definition
  of a term the category actually uses, including any term the client coined.
- Ships with `DefinedTerm` (in a `DefinedTermSet`) plus `FAQPage`.
- Coin it, define it, own the answer: if the client invented a term, they should already appear first for
  it on a non-branded prompt. Prove that, then generalise the play to the generic prompts the incumbents
  currently win.

## Knowledge-hub strategy

- One hub, two templates: a **concept** template and a **guide** template.
- Architecture: `/glossary/` plus a topic hub (`/learn/<topic>/` or similar) plus `/blog/`.
- Hub-and-spoke internal linking so authority compounds per topic (see the internal-linking slide).

## The content production cycle (one slide)

A repeatable cycle for every high-intent piece:
1. **Prompt generation:** build the prompt list from the client's themes, seeded from real queries.
2. **Prompt selection:** pick the prompts the client can actually win and has unique value on.
3. **Citation and top-result analysis:** study what AI cites today and where the gaps are.
4. **Outline:** read the top-cited pages; define sections that fully answer the query.
5. **Draft:** write against the outline in the client's voice, AEO-structured.
6. **Value addition:** layer first-party proof (original data, expert quotes, first-hand research), fed by
   the client's own material (webinars, sales-call transcripts, research, PDFs).
7. **Publish, mark up and measure:** ship with schema, re-run the tracked prompts, iterate.
Every published page feeds the next prompt cycle.

## Proving it works

Treat every tactic as an experiment measured on **citation share**, not vanity metrics. Keep an experiment
backlog scored on Impact / Confidence / Effort / Speed, run the highest-scoring ones first, and log the
result. The tracked prompt set is the instrument.
