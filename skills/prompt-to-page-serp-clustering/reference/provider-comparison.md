# Provider choice: full-SERP API vs lean URL-list provider

Two kinds of SERP source can feed this pipeline. Run a small A/B (a dozen prompts fetched both ways)
at the start of a new project before committing the corpus to one.

| Dimension | Full SERP API (e.g. DataForSEO Google organic, advanced) | Lean URL list (e.g. a search/scrape API returning URLs only) |
|---|---|---|
| Response | Ranks, titles, descriptions, spell correction, SERP features, People Also Ask (roughly 10 KB) | Bare URL list (well under 1 KB), often 6–10 URLs rather than a full 10 |
| Agreement | baseline | usually most of its URLs appear in the full SERP's top 10; brand-anchored queries agree closely; volatile queries stay volatile |
| Spell drift | Google applies `did_you_mean` / `showing_results_for`; a few poison the SERP | can be more drift-resistant (no rewrite applied), but has no spell field to prove it |
| Drift detection | `spell` field plus content check | URL-token screen: for prompts carrying a category token, count URLs that carry it; 0 → flag |
| Cost | one call per fetch | similar metered cost; check whether the provider bills more than one unit per fetch |
| Agent transport | heavy (about 12 per agent) | light (about 24 per agent) |
| Losses | none | **no ranks** (fatal for rank-weighted signal A), no titles (weaker judgment context), no spell provenance, short SERPs (thinner overlap denominators) |

Also check whether a provider parameter you pass actually changes the source: some wrappers ignore it
and return the default provider. Confirm from the response or from billing, not from the request.

## Preference

Because signal A is rank-weighted, **ranks matter on the page-assignment path itself**. Default to the
full SERP API for the corpus. Use a lean provider only for bulk passes where ranks are not needed, and
always use the full SERP for flagged or ambiguous prompts (titles and spell for adjudication), the
fidelity QA sample and any rank-faithful export columns. If your lean source does return ranks and
spell, most of these losses disappear; check its fields.

## Caveats

- **Mixed providers.** If tiers are fetched with different providers, same-page prompts still overlap
  across providers but shared counts run slightly lower on cross-provider pairs. **Do NOT tighten T
  upward on a mixed corpus.**
- **Short SERPs.** The integrity gate flags checkpoints with fewer than 5 results; the engine holds out
  SERPs with fewer than `min_serp_urls` distinct URLs as REVIEW.
