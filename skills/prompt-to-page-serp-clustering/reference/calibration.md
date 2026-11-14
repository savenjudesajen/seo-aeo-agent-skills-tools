# Calibration and findings

These are stated defaults. Every threshold below needs reviewer sign-off per project; record the
values that produced a map in `run_config.json` (the engine writes it).

## Default thresholds

- **T = 2 (absolute shared-URL count, never a ratio).** T=3 under-merges question-form prompts because
  their SERPs rotate more than keyword SERPs; the T≥3 habit from keyword clustering does not port to
  prompts. A Jaccard or percentage form voids the T=2 plus df≤5 calibration; don't switch to one.
- **`one_shared_max_df = 5`.** Raising it (to 10, say) lets mid-tail listicles through as join
  evidence; lowering it (to 3) refuses many genuine specific co-citations. If you sweep it, run the
  1-shared hand-read at each value and let the reviewer pick.
- **`a_high_confidence_max_rank = 5`.** Counting a rank-8 or rank-10 hit as "high" mislabels clusters
  that rest entirely on weak visibility.
- **`a_max_rank_considered = 10`, `near_miss_rank_range = [11, 20]`, `fetch_depth = 20`,
  `cluster.topn = 10`, `min_serp_urls = 3`.**
- **Fetch batch 12, up to 6 concurrent agents, 3 retries** (see `failure-modes.md` for why).
- **Assignment margin 25%**, **page profile = up to 5 keywords**, **content-type rank weights 3/2/1**,
  **same-set rule 4+ shared URLs**, **set alignment 2+ URLs holding for 75%+**, **drift flag below a
  third of the top 10**.

## The structural finding

**SERP clustering fragments intent finer than pages; page assignment re-aggregates.** An intent space
such as "espresso grinders" can split into several clusters by greedy order while brand-URL consensus
reunites them on one guide page.

**Do NOT loosen T to force big clusters.** Unification belongs to the page layer, where it is
evidence-based.

### Corollary: the errors are asymmetric

Over-splitting is **cheap and self-correcting**; over-merging is **expensive** and only a hand-read
catches it. So thresholds should be **strict**.

Two prompts sharing a brand page do not need to be merged: signal A places both on it independently.
Merging buys nothing there and risks a lot. A good share of the joins a df≤5 rule escalates already
have a brand URL in their own SERP, so A places them regardless and escalation costs nothing for those.

## Other findings worth checking on any run

- **Greedy-order artifact.** A definitional prompt ("What is a burr grinder?") can meet T=2 against an
  earlier, high-impression product-list centroid and get trapped there while its true home (a pillar
  guide) forms later. Big centroids form first, so edge-overlap prompts need the read.
- **Brand-anchor validation.** Brand-vs-competitor clusters should separate cleanly per competitor.
  Cross-competitor bleed happens at the shared-URL floor through brand-review roundup posts; a
  brand-anchor override fixes it.
- **Google blends what the inventory splits.** Two inventory pages can share one cluster. Keep them
  separate per the inventory's grain and raise it as a consolidation question for the reviewer.
- **Gap finding.** Check whether the brand ranks top-10 for its own "<brand> alternatives" query. If it
  doesn't, that supports a dedicated alternatives page.
- **Tier shape.** Prompts in the first priority tier are usually authored from the existing page
  universe, so expect them to land almost entirely on existing pages; net-new pages tend to appear only
  in later tiers.
- **Spell cases.** Most `did_you_mean` cases pass the content check (the SERP kept the original
  meaning); the rare `showing_results_for` swap of a category token poisons the SERP. Requerying with
  the keywordized core phrase recovers it.

## NET-NEW is a negative test

Before re-derivation, a raw net-new list typically looks like a page per prompt, each backed by a single
prompt with near-zero impressions and a negligible share of total demand. It is a *gap signal*, never a
page plan. After re-derivation on positive evidence (demand + seed ownership + inventory reasoning),
only a handful survive, and those carry real, rising demand.
