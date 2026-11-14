# Carried scripts

All scripts use only the Python standard library and read `config.json` from the working directory
(override the path with the `AEO_CONFIG` env var). **No brand, competitor, hub host or threshold is
hard-coded.** To run this process for another project, edit `config.json`, never the scripts.

| Script | Role | Run when |
|---|---|---|
| `cluster_engine.py` | Clustering, corpus document frequency, spell triage | After all SERP checkpoints exist |
| `page_assign.py` | Rank-weighted signal assignment and overrides | After clustering, after every override change |
| `integrity_gate.py` | **Gate**: coverage, primaries, overrides applied, thresholds recorded | Before every deliverable |
| `qa_grain_check.py` | **Gate**: competitor-alternatives grain | Before every deliverable |
| `fidelity_check.py` | **Gate**: re-fetch stability against stored checkpoints | Before every deliverable |
| `reconcile.py` | **Gate**: every researched keyword and prompt accounted for | Before every deliverable, and after backfill |
| `opportunity_score.py` | Page-level Opportunity Score | After the keyword sheet is final |

## Expected working directory

```
prompts_master.csv        prompt_id, prompt, tier, cluster(topic), impressions, intent
serps/{prompt_id}.json    per-prompt checkpoints
serps_qa/{prompt_id}.json fresh re-fetch sample (fidelity gate)
audit_pages_lookup.json   page inventory: {prompt_id: {mapped_pages: "/a|/b"}} (optional)
overrides.csv             prompt_text, target_page, confidence, rationale
config.json
```

## Run order

```bash
python3 cluster_engine.py     # -> clusters.csv, merge_candidates.csv, escalated.csv, run_config.json, ...
python3 page_assign.py        # -> page_map.csv, page_summary.csv, cluster_summary.csv, run_caveat.txt
python3 qa_grain_check.py     # must print: GRAIN CHECK: PASS (0 flags)
python3 integrity_gate.py     # must print: INTEGRITY GATE: PASS (0 failures)
python3 fidelity_check.py     # inspect URL/domain/top-3 overlap; exits 1 on any malformed URL
python3 reconcile.py --keywords ... --kw-map ... --prompts ... --pr-map ... --unified ...
python3 opportunity_score.py --rows keyword_rows.json
```

Check the exit code of every step. A crashed step leaves the previous run's output on disk and the next
step will happily consume it.

The two reasoning gates (1-shared/2-shared adjudication, B-signal hand-read) are **not** scripts; they
are read passes whose verdicts land in `overrides.csv`. Never skip them.

## The invariant

**The engine is never hand-edited.** Judgment enters only as an `overrides.csv` row with a rationale.
That is what makes a re-cluster cheap: after a complete rule change only a small delta of rows needs
re-reading; the rest are carried by overrides.
