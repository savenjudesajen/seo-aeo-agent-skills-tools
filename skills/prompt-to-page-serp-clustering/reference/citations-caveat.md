# Citations: what exists, what it can do, and the caveat

## What each kind of tool returns

| Tool kind | Returns | Use here |
|---|---|---|
| Google SERP API | Organic URLs with ranks, titles, spell, SERP features | The clustering signal |
| Lean SERP URL list | Organic URLs, sometimes without ranks | Bulk passes only (see `provider-comparison.md`) |
| Brand-visibility / mention tool | Whether, how often and where an engine MENTIONED a brand, often with sentiment | Mention-rate enrichment per page group. **Not citations.** |
| Prompt-tracking tool with a citation export | URLs an answer engine cited per prompt and model | Placement check after the join |
| Running the prompt in an engine yourself (Google AI Mode, Perplexity) and reading its sources | Cited URLs for one run of one prompt | Placement check after the join |
| SERP API that returns the AI Overview block | Google's AI Overview text and the pages it cites | One more Google signal |

Some clustering tools accept citation URLs as an input field. If you have none, leave it empty; never
fill it with organic URLs and call them citations.

## AI Overview blocks: verify the payload

Some SERP APIs list an `ai_overview` block in the SERP's block types whether or not its content came
through, and for a long time many returned it as an empty stub. **Read the block's CONTENT on the first
fetch of a run** and record whether it came back populated, so a regression shows up on day one rather
than at the deliverable.

Even when populated, these are **Google's** citations, from Google's own generation on the same SERP as
the organic results. Report them as one more Google signal. They do not stand in for ChatGPT's or
Perplexity's citations, and they never enter the clustering join, which is calibrated on organic overlap
alone.

## Using cited sources as a placement check

When cited URLs exist for a prompt:

1. Cluster and assign pages exactly as usual, on organic overlap only.
2. For each cited URL, find the page whose queries rank it (its own SERPs or its page profile) and credit
   the citation to that page.
3. Compare: does the cited evidence agree with the SERP placement? Disagreements go to the hand-read.

## The caveat every deliverable carries

> Clusters are formed from Google organic SERP overlap as a PROXY for what answer engines cite.
> Citations, where available, are a SEPARATE signal and are never pooled into the join decision.

`page_assign.py` writes this to `run_caveat.txt` and the integrity gate fails if it is missing. When
citations were not measured for a run, say so in the methodology tab rather than implying they were.
