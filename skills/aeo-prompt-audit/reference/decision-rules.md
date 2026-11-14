# Decision rules (the reviewer brief)

Copy this file into the run as RULEBOOK.md and fill the bracketed parts for the client. Every parallel reviewer gets
the same file, and nothing else about the client beyond the batch and the excluded sets.

## 1. The frame (fill per client)

- [Positioning sentence, quoted from the homepage and the owner.]
- [What the brand does not sell, in the owner's words.]
- [Competitor set: who the brand wants to beat, split into the competitors that count for Compare rows and the
  vendors that do not.]
- [The owner's framing rule, in their words: the kind of answer the brand does not want to be named in.]
- [Focus clusters, held clusters, excluded sets with their file names and counts.]

## 2. Closed lists

**Target cluster**: [the focus clusters], plus `Brand Positioning Monitor` (a small number of rows, kept to see how
engines describe the brand: matters most after a repositioning), plus `Out of focus`. Held clusters (not yet
researched) keep valid prompts with code HELD.

**Decision**: KEEP, REWRITE, REMOVE (DUPLICATE), REMOVE, REVIEW (REVIEW under about 5% of a batch; one owner choice,
stated as a choice). REMOVE (DUPLICATE) means the prompt asks the same question as a prompt we keep: it stops being
tracked, and Duplicate of names the prompt that still covers the question. REMOVE means the question itself goes. On
the platform both are retired the same way (archived with history); their data does not combine. Never call a
duplicate MERGE: readers take it to mean the prompt stays tracked.

**Reason code**: POS-MISFIT (frames the brand as a segment, tier, provider type or offer it no longer sells), OFF-FOCUS,
SUPERSEDED (same intent as a prompt in an excluded set: give its id), DUP (same intent as a surviving audited row:
give its id), COMP-ONLY (the brand cannot be the answer), INSTRUMENT (a tracking tool's string), NOT-ASKED (no buyer
would phrase it so), BRAND-NAV, NO-ANSWER, LOW-VALUE, GROUNDING-WEAK, SHAPE-FIX, REPOSITION, ON-STRATEGY,
POSITIONING-MONITOR, HELD.

**Stage**: Awareness, Consideration, Decision, labelled by who does the work, not by grammar.
**KPI**: Mention (the answer names providers) or Citation (the answer is conceptual; success is our page cited).

## 3. The tests, in order (stop at the first fail)

1. **Positioning and focus.** In a focus cluster, and winning it makes the brand look like what it sells now.
   Informational and how-to questions are positioning-neutral (Citation KPI) and usually pass; shortlists in the old
   positioning's shape fail (a "best X for home use" list for a brand that now sells to businesses, a "cheapest X"
   list for a brand that moved upmarket, a "best X for beginners" list for a brand that now serves professionals, or a
   shortlist of the provider type the brand stopped being, in either direction).
2. **Excluded-set overlap.** Read the excluded files for the true duplicate; any platform similarity hint is only a
   hint. Run this on KEEP and REWRITE rows as hard as on removals: independent checks find most misses among
   survivors whose closest excluded prompt was never looked up.
3. **G1 asked.** Would the ideal buyer type this into an assistant in these words? Keyword stacks, fragments, SEO-only
   phrasing fail as NOT-ASKED; tracker shapes (persona plus forced ranking, location injection, "evaluate the X
   company Y on Z", review-site strings) fail as INSTRUMENT.
4. **G4 worth winning.** The brand can be THE answer. Competitor-only questions fail. Build-versus-buy or
   do-it-yourself questions whose balanced answer argues against buying what the brand sells fail unless reframed.
   Brand navigation ("<brand> login", "<brand> pricing page") fails as BRAND-NAV.
5. **G3 answerable.** Some page of the brand's could carry the answer.
6. **G2 one intent.** Same intent as another row: keep the best-grounded, best-shaped phrasing; mark the rest
   REMOVE (DUPLICATE). Cost is one intent however worded; abbreviation and plural variants are one intent.
7. **Grounding.** Read the grounding keywords and their impressions or volume; read the echo count. All-echo grounding
   is GROUNDING-WEAK: decide on relevance. Platform volume ranks, it never cuts.
8. **Shape.** A question a person asks an assistant: typically 8 to 16 words, a qualifier only where the keyword
   carries one, no persona preamble, no output instruction, market spelling, no vendor named unless it is a Compare
   row. A worthwhile intent in a bad shape is a REWRITE.

## 4. Rewrites

- Anchored on the row's own keyword, quoted in Rewrite anchor.
- A reframe toward what the brand sells now needs the matching noun in the keyword set: the new segment or tier
  (premium, professional, business, commercial, enterprise) or the noun for the provider type the brand now is, or
  the row is a Compare row.
- No invented segment, industry or competitor.
- Not a duplicate of any surviving row or excluded-set prompt.
- Never convert a shortlist into a how-to to save it; if the how-to intent exists elsewhere, REMOVE
  (DUPLICATE) or REMOVE.

## 5. Compare rows

- Head-to-head and displacement are two intents in the ledger, so a competitor can hold up to two rows across the
  WHOLE set: one "<brand> vs <competitor>" and one "alternatives to <competitor>". Every other phrasing is REMOVE
  (DUPLICATE) pointing at them. Prefer the phrasing with real (non-echo) grounding. Never fold a head-to-head into an
  alternatives row.
- Drop the alternatives row when the competitor's alternatives list is a list of the wrong kind (the
  engines answer it with options in a segment, tier or provider type the brand is not), and keep only the
  head-to-head.
- Feature-level comparisons ("<brand> vs X for <feature>") pass only when the brand still competes feature by
  feature in that segment; judge them against the positioning sentence.
- Vendors outside the competitor set (an adjacent category the brand does not compete in) are OFF-FOCUS.

## 5b. REVIEW is for calls the rules do not settle

If a test above already decides the row, decide it. REVIEW is for a genuine business choice (a product line nobody has
ruled on, a monitor the owner may want), written as the choice. When one REVIEW row stands for a whole group (the
largest shortlist standing for all of them), say so in its reason so the owner decides the group once.

## 6. Unknown-provenance rows

Write the seed keyword (2 to 5 words, as people search), look it up in the client's keyword universe, then size it.
Record the volume and its source. Only size rows that are not already removed on positioning, focus or duplicate
grounds.

## 7. Reasons

One or two sentences written for that row: what it asks, which test decided it, and the evidence (keyword and
impressions, the duplicate id, the competitor). No em dashes. No method narration. First person plural for an
in-house team. A reason that could sit on any other row is not a reason.

Example shapes (fictional):
- KEEP, ON-STRATEGY: "Asks how to choose a repotting mix for low-light plants, a Consideration question our care
  guides answer; grounded on 'repotting mix low light' with steady impressions."
- REMOVE (DUPLICATE), DUP: "Same intent as P-0412 (how often to water a snake plant), which is better grounded;
  this phrasing only adds the plural."

## 8. Output per reviewer

A hand-typed decisions file and a JSONL with: id, decision, target_cluster, reason_code, reason_code_2, reason,
rewrite_text, rewrite_anchor, duplicate_of, stage, kpi, seed_keyword, seed_volume, seed_volume_source. Verify line
count, ids, no dashes, REWRITE fields, REMOVE (DUPLICATE) targets that survive.
