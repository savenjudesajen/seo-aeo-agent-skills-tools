# Deliverable format

## When the reviewer supplies a reference export

Keyword tools that cluster keywords into pages (for example Semrush's keyword-to-page clustering
exports) usually ship a `Pages` tab that is a pivot or summary, and a `Keywords` tab that is the real
data: **one row per keyword**, with columns along the lines of:

`Database | Keyword | Tags | Seed keyword | Page | Topic | Page type | Volume | KD | CPC | Competitive
Density | #Results | Intent | SERP Features | Trend | Click potential | Content reference 1-10 |
Competitor on TOP 10 #1-10`

- **`Page` there is the cluster label** (the head keyword repeated down the group), and such tools mix
  intents inside one page group. **Bind `Page` to an actual site URL instead**; that is what drives the
  refresh/create split.
- **`Content reference 1-10`** is identical across a page group: the cluster-level shared source set (a
  writer's reference stack). Compute it as URLs ranked by frequency across the group's member SERPs,
  ties broken by best rank, top 10, filled from the primary's top 10.
- **`Competitor on TOP 10 #1-10`** is that row's own SERP top 10, i.e. the per-prompt checkpoint.
- **`Cited URL #1-5`** can be appended for answer-engine citations; leave it structurally present and
  empty until a citation source exists (see `citations-caveat.md`).

> **When the reviewer supplies a reference export, replicate its structure column-for-column, using
> the tool's exact column names. Do NOT improvise columns into it. Put the audit layer (signal,
> confidence, rationale, placement basis: the judgment columns the tool lacks) in SEPARATE tabs.**

## Workbook defaults

Use the client's own workbook template if they have one. Otherwise keep it to what the method needs:

- **Methodology**: the thresholds from `run_config.json`, the placement-basis counts, the citations
  caveat and the note that the Opportunity Score ranks build order within this set only.
- **Map**: one row per prompt with its page, signal, confidence, placement basis and a rationale on
  every row.
- **Pages**: one row per page with content type, Opportunity Score and any reviewer decision.
- **QA**: gate outputs, merge and 1-shared verdicts, spell-drift requeries.

Plain formatting is enough: a header row, filters, frozen headers. If the reviewer comments in the
workbook, give them their own column and never edit it.

Build it with one build script fed by JSON inputs, recalculate, and confirm zero formula errors.
