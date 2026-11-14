# The pipeline (run in this order)

1. **Prompt master.** Take the prioritized prompt list from the upstream prompt work (for example the
   final, cleaned prompt list of the `aeo-keyword-research-and-prompt-simulation` or `aeo-prompt-audit`
   skill). `prompt_id = 'p' + md5(normalized_text)[:8]`; normalization: collapse whitespace, strip
   wrapping quotes, lowercase, strip trailing `?.`. Hash ids are stable across sessions and
   reorderings, so after a workspace reset checkpoints re-seed without a refetch.
   `prompts_master.csv` columns: `prompt_id, prompt, tier, cluster, impressions, intent`.

2. **Fetch via sub-agent fan-out.** Split into batch CSVs of **12 prompts** under `batches/`. Launch
   general-purpose agents in parallel (up to 6 concurrent). Each agent loads the SERP tool, skips
   existing checkpoints, calls with the prompt text VERBATIM, writes compact JSON per prompt and returns
   counts and timing only. Template: `data/fetch_agent_prompt.md`. Key results to the requested id,
   never by position; retry transient errors up to three times; verify per id on disk.

3. **Checkpoint schema** `serps/{prompt_id}.json`:
   `{prompt_id, prompt, spell, item_types, results:[{r, domain, url, title}], paa, related_searches,
   ai_overview, fetched_at, elapsed_s}`. Raw URLs on disk; normalization is deferred to the engine, so a
   normalization bug costs a re-run, not a re-fetch. Skip-if-exists makes the fetch resumable.

   **SERP depth.** Fetch and store the **top-20** (`fetch_depth`) but cluster on the **top-10**
   (`cluster.topn`). Do NOT cluster on 20: a wider window inflates accidental overlap and breaks the T=2
   calibration. The extra depth exists for **near-miss detection**: a brand URL at rank 11–20 does not
   fire signal A (`signals.a_max_rank_considered`); it sets `near_miss = true`. A seed that ranks the
   brand just off page one is the strongest refresh candidate on the site, not a "does not rank".

4. **Cluster** (`data/cluster_engine.py`): centroid-greedy; membership is tested against the cluster
   CENTROID only, so there is no transitive chaining. Centroid priority: impressions descending, then
   shorter prompt. URL normalization: strip scheme, `www`, trailing slash and tracking parameters
   (including per-request tokens such as `srsltid`, which make one URL look like many); keep the path
   and meaningful query.

   **The join rule (defaults; reviewer sign-off required):**
   - `shared >= T` (T=2) → **join**
   - `shared == 1` → **join ONLY IF** the shared URL is specific (**document frequency `df <= 5`**
     across the corpus) **AND** it is not a generic hub host **AND** the prompt is not a brand
     comparison
   - otherwise → **own cluster**

   `df(url)` = how many corpus SERPs contain that URL. A URL present in many SERPs carries no
   information (IDF). The most shared URLs are typically category listicles that sit in a large share of
   all SERPs, and cross-competitor bleed ("BrewNest vs RivalOne" fusing into "BrewNest vs RivalTwo")
   starts only a little above the df cap. A domain-based hub list is **not sufficient on its own**: most
   of the promiscuous URLs are ordinary publishers, not hub domains.

   **1-shared joins are NEVER auto-accepted.** A large share prove coincidental on a topicality read
   even at df ≤ 5. Every one goes to the QA gate.

5. **Spell handling** (in the engine): `showing_results_for` plus a swap of a meaning token (a category
   term from `meaning_tokens` in config) → QUARANTINE, because Google replaced the results.
   `did_you_mean` → content check: count top-10 url+title mentioning the lost token; 0 → quarantine,
   ≤2 → watch, ≥3 → OK.

   **Requery protocol** for quarantine/watch: re-fetch with the KEYWORDIZED core phrase ("What's the
   best way to dial in espresso at home?" → "how to dial in espresso"). Patch the checkpoint, keep the
   original `prompt_id`, and record `requeried_as` and `original_spell_issue`.

   A prompt can PASS the token check yet still sit in a wrong-topic cluster; check the cluster CONTEXT
   of watch-listed prompts, not just token counts.

6. **Escalation adjudication (reasoning).** Final **singletons** are prompts that could not be mapped by
   SERP overlap. Do NOT treat them as new pages: that is a *negative* test. Test **demand**, then apply
   three guards.

   - **Demand:** seed-keyword volume plus 12-month trend direction. High volume → page candidate. Low
     but rising → page candidate. Neither → map to an existing page **with a written rationale**.
   - **Guard 1: the seed keyword is NOT the prompt.** Deriving a seed climbs to the head term and the
     prompt inherits a whole category's demand. "Why does my espresso taste sour?" → seed `espresso` →
     looks like a must-build page. It is not; it is a diagnostic question an existing dialing-in guide
     answers. **Seed volume says whether a topic deserves a page. The prompt says where it maps.**
   - **Guard 2: seed ownership.** Fetch the SERP for the seed at full depth and check whether the brand
     already ranks. A brand page at rank 11–20 is a refresh case, not a new page.
   - **Guard 3: page-inventory reasoning.** Existence is not ranking: a page can exist and not rank for
     its head term. Match each proposal against the real inventory **by judgment, not by token
     overlap** (token matching gives false positives and false negatives). Bias toward "already
     covered": refreshing beats duplicating.

   Typical outcome: most proposals turn out already covered, a few are genuine gaps carrying real,
   rising demand, and a few are strategic calls for the reviewer.

7. **Judgment pass (reasoning, not script).** Read every multi-cluster, every 1-shared join, all merge
   candidates and every low-confidence row against these arbiter rules:
   - brand-anchored SERPs are read by **COMPOSITION**, not by URL count; category-anchored SERPs by URL
     overlap;
   - **competitor-vs-competitor head-to-heads stay on their topical page**;
   - near-synonym category terms the client treats as different offers stay separate unless the SERP
     and the reviewer both merge them;
   - citations, mentions and rankings are three different things;
   - default to keep-separate.

   **Independence check for keyword evidence.** A prompt that is a verbatim Search Console query also
   exists as a keyword head, so its own keyword is the nearest neighbour of its SERP. Before a nearest
   keyword counts toward moving a prompt, check it is not a keyword already mapped to that same prompt.

   Verdicts land in **`overrides.csv`** (`prompt_text, target_page|REVIEW, confidence, rationale`), the
   auditable layer. **The engine is never hand-edited.** Copy override text exactly from
   `prompts_master.csv`; never hand-type it.

8. **Page assignment** (`data/page_assign.py`), per cluster, signals in order:
   - **A: brand-URL consensus**: the most frequent brand path across member SERPs, counted once per
     member SERP. `hits >= 2` **and best rank <= 5** → that page, **high**. `hits >= 2` **but best rank
     > 5** → **medium (rank-demoted)**. `hits == 1` in a ≤2-prompt cluster → medium/low by rank.
     Counting a rank-10 hit like a rank-1 hit labels many rows "high" on weak evidence.
   - **B: authored-intent prior**: the page inventory's `mapped_pages` majority. **Always `low`. Never
     independent evidence.** See `reference/signal-provenance.md`. Every B row is hand-read.
   - **A-weak:** a single brand hit in a larger cluster → low.
   - **C: NET-NEW**: only via the escalation adjudication in step 6.
   - Overrides win over signals. Output: `page_map.csv` (one row per prompt: page, role
     primary/secondary, signal, confidence, rationale, row-level evidence), `page_summary.csv`,
     `cluster_summary.csv`, `run_caveat.txt`.

9. **Re-add quarantined prompts** after assignment (they are excluded from `clusters.csv`; their override
   row carries the page). Assert final row count == prompt-master count.

   **Authored-page crosscheck, per result set.** When queries were pulled three times (SKILL.md step
   2a), assign each of a prompt's pulls to the result set whose keyword-cluster centroids it overlaps
   most, then join the prompt's per-set URL set to that set's centroids with the keyword join rule
   (2+ shared URLs; 1 only when df ≤ 5, not a hub, not a vs query). Report one of: AGREE,
   AGREE (split member), DISAGREE, MIXED (one set each way), PARTIAL (one set agrees, the other has no
   cluster) or NO CLUSTER. Everything except AGREE goes to the hand-read.
