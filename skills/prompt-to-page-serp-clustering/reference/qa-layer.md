# The QA layer (standing, non-optional: run before every deliverable)

Five gates, in order; the deliverable ships only when all pass.

## 1. `integrity_gate.py` (script)

Coverage (map == target set, all tiers), unique ids, exactly one primary per page, every override
text-matched AND applied, no empty page or rationale, checkpoint validity, every spell case
dispositioned, `run_caveat.txt` present, and `run_config.json` thresholds equal to the signed-off
config.

Its most common catch: an override keyed on a RECONSTRUCTED prompt text (retyped from a truncated
display) that silently matched nothing. **Never hand-type override keys**: copy exact text from
`prompts_master.csv`, or key on `prompt_id` and resolve the text programmatically.

## 2. `qa_grain_check.py` (script)

Deterministic grain rules from hand-read findings: a prompt with "<competitor> alternatives / who are
X's competitors / brands like X" must land on the X-alternatives page when one exists.

- **Known false positive:** attributive uses such as "competitor price match" describe a feature or
  a comparison, not alternatives intent; the pattern requires plural or top-anchored forms.
- **Blind spot:** the regex cannot see the `X vs Y` shape and catches only a small share of it. That
  class is enforced by the reviewer rule (head-to-heads stay on their topical page), not by script.
- A gate with no competitors configured exits 2 and says SKIPPED; it never reports a pass.

Extend this script whenever a hand-read finds a systematic class.

## 3. 2-shared and 1-shared adjudication (reasoning)

Every member that joined a cluster on exactly the threshold, **and every 1-shared join**, is read
against its assigned page. This is threshold sensitivity done by judgment, not by tuning T. Expect most
to be kept and a meaningful minority corrected.

**1-shared joins are never auto-accepted**: a large share prove coincidental even at df ≤ 5. Read them
for topicality (is the shared page actually about this subject?), not as a second df check.

## 4. Low-confidence hand-read (reasoning)

Every `B:authored-intent` and weak-A row. Headline correction class to expect: the authored-intent
prior parks brand product questions on competitor comparison pages.

## 5. `fidelity_check.py` (script plus a re-fetch)

Re-fetch a stratified sample of roughly 10–25 prompts into `serps_qa/` (a fresh agent, do-not-skip
mode) and compare URL, domain and top-3 overlap against stored checkpoints.

What a healthy result looks like: most of the top 10 persists, agent-transcribed checkpoints are
indistinguishable from directly observed ones, and there are zero malformed URLs. That validates the
fan-out transcription design.

Hour-scale SERP churn is real: a volatile prompt can keep only a few of its URLs a few hours later. That
is fine if its page assignment rests on signal A or a recorded override.

> **Cluster membership is ephemeral evidence; page signals and recorded overrides are the durable
> layer.** Re-runs re-cluster, but decisions persist in `overrides.csv` with their rationale. That is
> what makes the process repeatable: after a complete re-cluster under a new join rule, only a small
> delta of rows needs re-reading.

Google can return the SAME URL at two ranks: **dedupe URL sets before overlap counting** (the scripts
do).

## 6. The verification habits (reasoning, every deliverable)

Not a script. Habits that each catch defects in work that already passed a gate, and that share one
shape: **a thing that looks like success is not evidence of success.**

- **A declared output column is not a populated one.** If the engine fails to carry a field (intent,
  say) from `prompts_master.csv` into `clusters.csv`, the page map and cluster summary ship that column
  EMPTY, and a reviewer reads it as "not collected" rather than "lost in transit". Test every carried
  field for **non-empty** values, not for presence; a fixture with blank fields makes a broken
  carry-through look like a pass.
- **Never trust a parallel sub-agent's reported total.** Concurrent writers return racy counts. Verify
  on disk, or with an **idempotency probe**: re-submit ONE known row and read back the skipped-duplicate
  count plus the true total.
- **When a tool returns an error, check whether the write actually LANDED before retrying.** Some
  wrappers report an error on a downstream write that succeeded; a blind retry duplicates it.
- **Before reporting a bug in someone else's tool, re-run the measurement with THEIR normalization.**
  An apparent anomaly (a URL that seems to appear in hundreds of SERPs) can be an artifact of your own
  analysis script stripping query strings that the engine keeps.
- **Token or slug matching cannot answer "does this page already exist?"** It gives false positives (a
  broad head term "matching" a narrow tactical page) and false negatives (`grinder-cleaning` not
  matching `how-to-clean-a-burr-grinder`). That question needs a reasoning pass over the real
  inventory.

## Build discipline

Build the deliverable from ONE build script fed by JSON inputs (merge verdicts, QA results,
methodology), never with ad-hoc code. Recalculate and check for zero formula errors.
