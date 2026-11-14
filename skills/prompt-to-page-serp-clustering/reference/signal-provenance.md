# Signal provenance: the authored-intent trap

**Read this before trusting any page-inventory prior.**

## The tempting mistake

A page inventory often carries a column that looks like noise: a provenance or source tag on each
prompt with values such as `generated`, `tracked`, `reviewer-picked` or `both`. It is easy to read it as
reviewer tier marks and ignore it. **Don't.** It is prompt provenance, and it is the most diagnostic
column in the inventory.

## How to test it

Cross-tab the provenance tag against whether the prompt has a `mapped_pages` value:

| provenance | has a `mapped_pages` value |
|---|---|
| `generated` | all of them |
| `reviewer-picked` | all of them |
| `both` | all of them |
| `tracked` | none of them |

A clean all/all/all/**none** split like this (run the cross-tab on your own inventory; the pattern is
what matters) tells you how the mapping was made.

## Why it happens

When prompts are **generated from the keywords a page already ranks for** (Search Console page/query
pairs → simulated prompts), a generated prompt's `mapped_pages` is **the page it was authored from**.
That is grounded, but it is keyword-grain and aligned with the prompt by construction. Prompts that were
only ever *observed* (the tracked set in a prompt-tracking tool) were never mapped at all.

## The consequence

**Signal B is a prior, not evidence.**

- When **signal A** fires you are *testing* the author's intent against what Google actually serves.
- When **signal B** fires you are merely *re-asserting* it.
- Worse: a `tracked` prompt sitting in a cluster of `generated` prompts **inherits their synthetic
  labels**.

## The rules that follow

1. Name the signal **`B:authored-intent`**, never "audit consensus".
2. Its confidence is **always `low`**. Never present it as consensus or medium confidence.
3. **Every B row goes to the hand-read gate.** No exceptions.
4. Expect it to be wrong at the row level in a characteristic way: it parks "BrewNest alternatives" on a
   competitor comparison page, and brand-product questions ("Does BrewNest sell replacement gaskets?",
   "Which grinders does BrewNest stock?") on comparison pages. That is usually the single
   largest correction class in the low-confidence hand-read.

## Also: confidence is inherited from the CLUSTER, not the row

A prompt that joined on thin overlap inherits its cluster's "high" confidence even when its **own** SERP
contains no brand URL. A large share of hand-read corrections are `A / high` rows of exactly this shape.

Guard: expose `shared_with_centroid` and "brand URL in this prompt's own SERP (rank)" next to
confidence, so a reader can see whether a row rests on its own evidence or its cluster's.
`page_assign.py` also sets `needs_review = yes` automatically on any A row whose own SERP holds no
brand URL.
