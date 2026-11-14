# Extended build: the full competitor comparison page template (only when the user asks for it by name)

The default deliverable is the lean two-section doc in `reference/lean-doc.md`. Use this file only when the user
asks for the full template doc: every block in page order with status-tagged wireframes, a fixed table row set,
fairness and evidence rules, how the template changes by rival category, URLs and titles, the CMS model, build checks
and a chat or email reply draft.

It turns a request for a reusable layout for one-rival comparison pages into one template a designer builds once and a content writer fills per rival: every block in page order, a fixed set of table rows
mapped from the company's own comparison matrix, the fairness and evidence rules that make a vendor-written
comparison believable, how the template changes by rival category, URLs and titles, the CMS model and the build
checks. It pairs with the `competitor-overview-page-structure` skill, if installed: the hub doc sets the launch set, URL pattern,
rival collection and call to action; this doc extends them.

## Before you start
1. When the hub doc exists, reuse its launch set, URL pattern, CTA label and target, rival fields, byline and
   disclosure wording and trademark line word for word.
2. Copy rules: the verify step in `reference/lean-doc.md` and the carried copy gate `data/qc_copy.py` (plus the
   brand's own writing guidelines, if it has them).
3. Use the company's own document template if it has one (the `doc-template-design` skill can set one up, if
   installed); otherwise the builder's neutral default.
4. Confirm scope, or state assumptions when the user is away: template only (default) or template plus finished
   pages per rival; the rivals; the CMS; who reads it. A template-only doc never writes claims about a specific rival
   beyond the benchmark evidence; wireframes use <Rival>.

## Workflow
1. **Inventory the company's raw material.** The comparison matrix (row labels verbatim: they become the table
   rows), the FAQ, the proof (customer figures, recognitions, quotes and their sources), any page that says whether the
   product works beside other tools, author and bio pages, blog posts that answer a rival's category question, pricing pages (none is a
   finding).
2. **Benchmark in three sets with one taxonomy** (`reference/benchmark-method.md`). Open `reference/site-index.md`
   first: its leaderboard names the sites with the best ideas and every entry points to the page and its notes. The
   SaaS and cross-industry sets are carried; build the client set (about 10 to 20 vs pages by the company's rivals
   and category peers) privately and re-code it against the same type ids. Benchmark the best pages from any
   industry, read many, and pack the page with every section that helps a buyer or an AI answer.
3. **Re-read on the live page** every quote a caption or Why row will rest on. Read footnotes: a stat headed against a
   rival may measure something else, such as an older product or a different segment.
4. **Pack the block model** (`reference/section-model.md`, `data/packed_vs.py`): every type lands in a block, a part
   of a block, or a "Not used" line with its reason (a vendor's house scores, winner cards, weights and a rival's
   incidents read as biased). Statuses: New, Rework (content exists on the company's site), Optional (never blocks
   launch), Later (waits for company content: certifications, product screenshots). Set the run's statuses in
   `STATUS_OVERRIDES`. Stages: Capture, Orient, Evaluate, De-risk, Convert.
5. **Map the company's matrix to a fixed row set**: neutral labels, a Best for row first, one category row the rival
   leads (one version per rival category), How it is bought last, claims that are not capabilities left out. Every
   compared row carries a Leads tag ({Company}, Both, <Rival>). Use the same rows as the hub's table.
6. **Decide how the template changes by rival category**: the question the takeaways settle, the row the rival leads,
   what the rival keeps doing beside the company's product, and the company context (a dated acquisition or merger,
   sourced). Compare with the rival's product that overlaps the company's, and name it in the column heading: many
   rivals sell more than the product they are known for.
7. **Capture proof**: at least one screenshot per New or Rework block, and one per Later block where it shows the
   company what to supply (`reference/exemplar-library.md`). Browser mechanics: the capture recipe in `reference/lean-doc.md`
   (and the `web-screenshot-to-document` skill, if installed). Crop map: `data/crop_map.py` (pointer fill, blur, stitching, re-crops).
8. **Build the doc**: wireframes with `data/wire_vs.py` (drawn from the block list), then
   `data/build_extended_doc.py` with a content spec copied from `data/extended_spec_example.py`. Outline and
   conventions: `reference/doc-structure.md`. CMS and checks: `reference/cms-and-build-checks.md`. Needs python-docx
   and Pillow.
9. **Verify**: `qc_copy.py` 0 hits (`--names` for benchmark companies that are also tool names, such as Ahrefs and
   Semrush), every rendered page viewed (whole tables, figures legible, no stub pages), the never-mention list clean,
   dash count 0, and every caption against its capture. Ask the user before spending a fresh-context reviewer round
   (the prompt is in `reference/doc-structure.md`). When a fix changes a count or rule the sibling docs share, fix and
   re-deliver those.
10. **Deliver** the .docx the way the user works and draft the chat or email reply. Never send a message on the
    user's behalf without an explicit yes.

## Definition of done
- [ ] 22 to 28 blocks across New, Rework, Optional and Later, each with a count out of its base and examples asserted
      to be in its set; every type in the taxonomy lands somewhere or has a "Not used" reason.
- [ ] Every New and Rework block has a screenshot whose caption says only what the capture shows.
- [ ] The row mapping table covers every row of the company's matrix (kept, merged, renamed or left out with a
      reason).
- [ ] Wireframes, order table, specs, jump links and anchors, rival-category table, CMS fields and build checks use the same
      block names; the wireframes are drawn from the block list.
- [ ] Consistent with the hub doc (and any sibling docs that share the same fields): URL pattern, rival fields, byline, disclosure, trademark
      line, FAQ collection, CTA, meta description rule, structured data method.
- [ ] qc_copy 0, every page viewed, never_mention clean; reply draft ready, not sent.

## Gotchas
- **Captions overstate.** Re-read the image before a caption is final; say only what the crop shows.
- **Claim only what was checked.** "n of N" only when all N were checked; otherwise name the pages seen.
- **Stats under a rival's name are not always about the rival.** Read the footnotes.
- **Dates cut both ways.** A visible date helps only while it is fresh. The year in the title moves with Last
  reviewed.
- **Pricing**: never state a price its owner does not publish. The rival column says "Pricing not published" with the
  date checked; the company's own model is template text it signs off.
- **Coexistence hides in FAQs and side offers** (an integration answer in an FAQ; a plugin to start on the rival's
  platform before migrating). Read FAQ answers and promo bands before counting a page out.
- **CMS**: the model and the structured-data method are in `reference/cms-and-build-checks.md` (table rows as their
  own collection filtered to the current rival, FAQ microdata where the CMS allows only attributes, no public pages
  for rows, sources or FAQ entries).
- **Layout**: a section that spills one or two rows onto a stub page: let the next short section flow (no new page)
  or add a page break before a subsection so its figure and table stay together; shrink figures before type.
- **Style**: apply the user's style rules (sample defaults in `reference/lean-doc.md`). Meta descriptions, default:
  about 70–80 or 170–180 characters; use the client's rule if they have one. FAQ questions and tracked prompts start
  from People Also Ask and AlsoAsked. No process narration in the doc.
