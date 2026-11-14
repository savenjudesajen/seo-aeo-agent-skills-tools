# Fetch-agent prompt template

Fill the braces and give this to each fetch sub-agent, one batch file per agent.

> You are a mechanical SERP-fetch worker. Your batch file: `{batches_dir}/{file}.csv` (columns:
> prompt_id,prompt).
>
> **SETUP:** (1) Load the SERP tool `{serp_tool}`. (2) Read the batch file; check `{serps_dir}` with a
> file-read or glob tool and skip prompt_ids that already have a `.json`.
>
> **FOR EACH remaining row:** call the SERP tool with the prompt text VERBATIM as the query, location
> `{location}` (for example United States), top 20 results. Extract the spell-correction field verbatim,
> the list of SERP block types, the url-bearing organic items in provider rank order (up to 20), AND the
> question and answer blocks: People Also Ask (every question, with its answer url and domain when
> present), related searches (the query list) and the AI Overview (its text and cited references).
> Write one compact object to `{serps_dir}/{prompt_id}.json`:
> `{"prompt_id","prompt","spell","item_types","results":[{"r","domain","url","title"}],"paa":[{"question","answer_url","answer_domain"}],"related_searches":[...],"ai_overview":{"text","references":[...]},"fetched_at","elapsed_s"}`.
> Store `paa`, `related_searches` and `ai_overview` as empty when the SERP has no such block, so a
> missing block is distinguishable from an unfetched one. Copy URLs EXACTLY; titles may truncate to 100
> characters. Key every result to the prompt_id you REQUESTED it for, never by position in a batch. On
> an error, retry up to three times with identical arguments; after the third failure log the id to a
> `_failures` file and CONTINUE.
>
> **RULES:** never paste full responses into your final message; process every row; report unprocessed
> rows as REMAINING (never as "skipped").
>
> **FINAL MESSAGE:** fetched / skipped / remaining / failed counts with ids; min/median/max `elapsed_s`;
> the list of prompts with a non-null spell field; the list of short SERPs (fewer than 10 results).

## Capture People Also Ask on the FIRST pass, always

Clustering needs only organic URLs, so it is tempting to store only those. Don't. The step after
clustering sources prompts per cluster, and its primary input is People Also Ask, recursed to depth 2. A
fetch that discarded PAA forces a full re-fetch of the corpus at full cost, for data already in hand.
Most commercial and question SERPs carry a PAA block.

Also verify the provider actually RETURNS these blocks before budgeting around them. A wrapper that
trims responses to save tokens can flatten People Also Ask and related searches to `{}` while leaving
them at their positions, so the payload looks well-formed and merely empty. Check one response for
question text before concluding a block is absent from that SERP.

## Why batches of 12

An agent's context holds roughly a dozen full SERP responses (about 10 KB each) before it stops and
**confabulates completion**: it reports unfetched rows as "skipped". Batch size 12 is the safe number.
Never trust agent counts; the orchestrator verifies every requested id on disk.

## Concurrency

Up to 6 concurrent agents is a sensible default; back off if the provider rate-limits. With several
agents sharing one shell, have them check file existence with file-read or glob tools rather than shell
listings.
