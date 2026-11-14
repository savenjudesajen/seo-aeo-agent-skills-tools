# Gates: what enforces each rule, and the contract the deliverable has to meet

A rule that lives only as a sentence in a long contract is a rule that is not applied: a tag with no column, no
page-note segment and no check never reaches a deliverable, and a script that exists but is not run enforces nothing.
The principle every change to this skill is held to:

> **A rule that can be checked by a script is checked by a script the definition of done names. A rule that cannot be
> scripted is a field the reviewer can see on the sheet. A vocabulary is a closed list in one place. Two rules that
> contradict each other are one rule and a pointer.**

## 1. The one command

```
python3 data/run_gates.py --workbook <deliverable.xlsx> --corpus <corpus.json> --asked <N> --market us \
    --brands brands.json \
    [--returned <file the reviewer sent back> [--previous <last file sent to the reviewer>]] [--evidence <serp_evidence.json>] \
    [--qualifiers <qualifiers.txt>] [--acronyms <acronyms.txt>] [--report gate_report.json] \
    [--floor 0.2 --floor-reason "<why>"] [--min-seeds 20] [--own-budget 1] [--sheet "Prompt Map"] \
    [--require-sheets "Scope Map,Exclusions"] [--skip-cols "<header prefix>:<reason>"] [--strict] \
    [--skip <gate>:"<reason>"]
-> ALL GATES: PASS
```

| flag | what it does |
|---|---|
| `--workbook` | the deliverable; every input except the corpus is derived from it (Prompt Map, Keyword Map) |
| `--corpus` | the observed question corpus (question tools, People Also Ask, Search Console human rows) the grounding gate reads |
| `--asked N` | the number of sheets asked for; the workbook may carry N + 1 |
| `--market us` or `uk` | the client's spelling market |
| `--sheet` | the prompt sheet's name when it is not `Prompt Map` |
| `--returned`, `--previous` | the workbook the reviewer sent back (runs the review gate) and the last one sent to the reviewer (lists the reviewer's direct edits). A pass that follows a review MUST be given `--returned` |
| `--evidence` | the SERP-cluster file for audit A6 |
| `--brands` | REQUIRED (run_gates.py and prompt_audit.py exit with a message without it): the path to `brands.json`, one JSON list of strings: the client's brand and product names plus every tracked competitor's name (for example `["ClientV", "ProductA", "CompetitorB"]`); anything else, or an empty list, stops with a message, and `run_gates.py` asks for it whenever the workbook has a prompt sheet. OWN and Specifics rows on a mention-route page count as provider-naming only through these names |
| `--qualifiers` | one segment or audience qualifier per line for audit A3, replacing the default list |
| `--acronyms` | one `abbr=expansion` per line, added to the default map for tracked check 11 |
| `--floor`, `--floor-reason`, `--min-seeds` | the grounding floor (default 0.50), the written reason any lower floor needs, and the corpus-adequacy minimum |
| `--own-budget` | simulated OWN rows allowed per topic cluster (default 1: one OWN row per topic cluster); observed rows never count toward it |
| `--require-sheets` | sheets that must exist (keyword side: `"Scope Map,Exclusions"`) |
| `--skip-cols` | a column exempt from the narration check, with its written reason (repeatable) |
| `--strict` | the hygiene gate fails on its flags instead of printing them for the hand read |
| `--skip gate:reason` | records a gate as skipped with a written reason; a skip without a reason is a FAIL |
| `--report` | the machine-readable report, kept in the working files |

`run_gates.py` derives every input except the corpus from the workbook itself, so "no input file" is never a reason a
gate did not run. A gate that cannot run is a FAIL unless skipped with a written reason, printed in the report.
Keyword-side workbooks (no prompt sheet) run the hygiene gate and record the three prompt gates as skipped. Keep the
report in the working files and cite it in the Source column of the delta ("gates: ALL PASS, <date>"). All gate scripts
use only the Python standard library and run offline.

| gate | script | what it holds the file to |
|---|---|---|
| hygiene | `data/verify_workbook_hygiene.py` | every sheet: a Source column filled on every row (prose sheets exempt); no em dash anywhere; no method narration in a finding cell ("captured live", "API", "MCP", "tool call", "screenshot", "pipeline"); tool names outside provenance columns flagged for the hand read; AI vocabulary flagged; closed vocabularies wherever the column exists (Content type, Tier, Scope, Stage, KPI); `--asked N` caps the workbook at N + 1 sheets; `--market` flags the other market's spellings except in columns whose header starts with Keyword; `--require-sheets`; every reason column filled; `--skip-cols` exempts named columns with a written reason |
| tracked | `data/verify_tracked_set.py` | the Prompt Map contract (section 2; a missing contract column, including Cluster (or Topic), which the OWN budget needs, is a hard fail) and the set rules: instrument signatures (the tracker tells live once, in `data/tracker_tells.py`, shared with the long-tail split; the verifier flags a location or market clause on a tracked prompt, the split strips it before matching), length (4 or 5 to 25 words by basis), dangling pronouns, 2 rows per page minimum and 12 simulated rows maximum, one simulated cost row per selling page (Service Page or Product Page only), one persona row per page and per set, OWN budget (one simulated OWN row per topic cluster by default; observed rows never count), exact and near duplicates (token overlap 0.6 or more across pages), fan-out shape and labels, mixed spelling, the keyword partition, answer type (one of the nine; an unknown value fails) and KPI on every row, the hand-read answer-type findings (a Concept row on a selling page; a citation row on a MISMATCH page; a row whose KPI is not its answer type's default, Evidence mention on an explaining row allowed; a page whose page check is not its primary answer type's default, one finding per page; every page whose primary type is Destination, to confirm it is the destination the prompt names), abbreviation variants tracked twice, family D or L tracked, wave consistent with stage, one-family pages, the page check identical on every tracked row of a page (a page whose rows disagree fails) |
| audit | `data/prompt_audit.py` | does each prompt belong on its page: A1 provider-naming rows against page type read through the KPI and the answer type (a row whose page check is its type's default, match or mention route, is never blocked for lacking provider words); A2 core-term containment for keyword-less rows; A3 qualifier match; A4 shape (reported); A5 a page with keywords and no prompt; A6 SERP evidence when given; A7 stage on every row and the Awareness share on selling pages; KPI on every row |
| grounding | `data/ground_check.py` | verbatim, anchored-rewrite and keyword-verbatim (1b) grounding against the observed corpus, per source; the floor (below 50% only with a written `--floor-reason`); possible anchors listed for simulated rows; no observed row whose anchor is missing from the corpus; no row resting on tier-2 evidence only; every simulated row with a family and a reason; corpus adequacy |
| keyword list | `data/verify_deliverable.py` | the cleaned keyword workbook in the seed-chain C6 layout (Keywords, Group Summary, Exclusions, README): row-for-row match, duplicate and near-duplicate sweep, the evidence floor, Search Console totals, group aggregates, superlative uniqueness, kept-vs-excluded collisions. Layout-specific: on a differently shaped deliverable, say so and run the hygiene gate; a layout mismatch never passes for a pass |
| long tail | `data/longtail_split.py` | a 6+ word Search Console export split by who wrote the query before any long-tail figure is cited: HUMAN (a person asking; the only population whose volume is demand), REPEAT (one exact 10+ word phrasing repeated at `--per-day` or more across the window), REPEAT-SET (8+ word phrasings that are one template with a slot swapped, `--set-min` variants or more), OWN-TRACK (matches the client's own tracked-prompt export, `--tracked`), TRACKER (persona framing, output instructions, harness wrappers, over `--max-human-words` words, default 40), PERSONA_SHORT (a short persona plus a request), STACK (three or more vendor names in one string; `--vendors`), TEMPLATE (a query opening `evaluate the `, `best` or `top` plus a provider noun, `tool(s) to` / `tool(s) for`, or `leading`, `highest-rated`, `most reliable` or `most affordable`; `--template-noun` adds category nouns for best/top, `--template-pattern` adds regex alternatives, no default; checked after TRACKER, PERSONA_SHORT and STACK), PREFIX (an operator prefix such as `+` or `%`), AGENT (site watchers and operator strings), NOISE (third-party strings hitting the site by collision; `--noise`), other (read before trusting any share). Hand-run, not wrapped by `run_gates.py` |
| review | `data/review_round.py` | a pass that follows a reviewer round: every message of every comment quoted, with what was done, in a `Reviewer decision` column; every returned sheet still exists; a returned column that has gone is a WARN. `--previous` lists the reviewer's direct edits and column changes for the reply. Skipped, with the reason printed, on a first pass |

## 2. The contract (what `verify_tracked_set.py` check 12 requires)

**Prompt Map**, one row per tracked prompt, headers matched by prefix, case-insensitive. A one-sheet map may carry a
`Row` column: TRACKED rows are the prompts the gates read; PAGE, NOT TRACKED, KEYWORD ONLY, MOVED OUT and FOLD rows are
context for the reviewer and are skipped by the tracked checks.

| column | allowed values / shape | rule it carries |
|---|---|---|
| Page | the page key | |
| Content type (SERP-derived) | Guide, Service Page, Product Page, Listicle, Glossary, Research Post | from what ranks, never from the keywords' wording |
| Answer shape and page check | `<answer shape> (<match / partial / mention route / MISMATCH>)`, repeated on every tracked row of the page; the check is read only from the trailing parenthesis | B2-format, `intent-format-kpi.md` section 5 |
| Cluster (or Topic) | the topic cluster | B2 topic |
| Cluster core page | Yes / No | shared intents tracked once, on the core page |
| Answer type (primary / secondary) | `<Primary>` or `<Primary> / <Secondary>` (space, slash, space), each one of the nine answer types; the primary is the text before ` / ` | `intent-format-kpi.md` section 3 |
| Need | Know / Do / Website / Visit | `intent-format-kpi.md` section 2 |
| KPI this prompt can move | Mention / Citation / Evidence mention | follows what the answer will name |
| Why that KPI | a reason | hand-authored |
| Stage (who does the work) | Awareness / Consideration / Decision | B2 |
| Play (provisional) | Defend / Strengthen / Capture | B2 |
| Wave | 1 to 9; 1 for Consideration and Decision rows, 2+ for Awareness fill | B1-waves |
| Prompt | the tracked string, 4 or 5 to 25 words | B1, B3 |
| Form | NB / OWN / COMP | prompt-matrix |
| Family | A to L; a tracked row is never D or L | prompt-matrix |
| Keywords mapped to this prompt | one keyword per line with its volume, or `(no keyword anchor)` | the keyword partition |
| Why a buyer asks it | a reason; near-duplicate reasons appended here | G1, B3-set |
| Page must carry | the content obligation | G3 |
| Fan-out block | 2 to 5 lines, each `<string>  [<label>]  ->  <heading or passage>`; labels O-ui, O-bing, O-as, O-gsc, S-compress, S-axis; no question mark; 10 words or fewer; or `Not built: <decision and date>` | B3-fanout |
| Basis | starts with `observed` or `simulated`; a simulated row names its family and what was checked | B3, B3-sim |
| Observed anchor (verbatim source string) | the corpus string an observed row rests on; empty for simulated rows | grounding: anchored rewrites |
| Source | provenance | standing rule |

Recommended beside these: Placement evidence (B3-crosscheck verdict and numbers), Title / head term / SERP format (page
rows), Launch status.

**Keyword Map**, one row per keyword: Keyword, Volume, Page, Mapped to prompt (`KEYWORD ONLY, <reason>` for a held
keyword; pages written `EXISTING:<url>` are exempt from the partition), Source. Note and "Originally mapped to" are
recommended.

**Delta** (a second pass on existing approved rows): one line per existing row with ids, action, the page
check, the KPI split, old -> new score with rank, kept / retired / added prompts, keyword moves, the new cell text,
flags, Source. A second pass on a workbook with no external content plan carries the same delta as a computed `Change
vs <previous> (<date>)` column on the Prompt Map plus a Page Summary sheet (per page: page check, KPI split, keyword
count and volume, changes, flags; then set-level lines: KPI split, page checks, shorthand verdicts, grounding split).

**After a reviewer round** the Prompt Map carries a `Reviewer decision (<date>)` column beside the reviewer's own Comments
column, with a cell for every message of every comment that quotes it and says what was done; the Page Summary carries a
`Launch status` (LAUNCH, HOLD or REMOVED, with the reviewer and the date).

Engagement-specific columns (an intent ledger, a tracker id, a content-plan row id) are welcome beside these; they are
not required.

## 3. Rule to gate: where every rule in the definition of done is held

| rule | held by |
|---|---|
| Every keyword on exactly one row of its page, every mapped prompt tracked there | tracked 9 |
| Answer type and KPI on every row, KPI split stated | tracked 10, 12; audit KPI |
| Every page's page check, MISMATCH written up | tracked 12, 13; audit A1 page-level |
| Each page's check is its primary answer type's default for the page type (primary = most common primary type on the page; on a tie, the tied type that appears first), or the rows say why | tracked 10 (printed for the hand read, one finding per page; defaults in `intent-format-kpi.md` section 5) |
| A Destination page is the destination its prompts name | tracked 10 (printed for the hand read on every Destination page) |
| Each row's KPI is its answer type's default (Evidence mention allowed on an explaining row), or the row says why | tracked 10 (printed for the hand read) |
| The page check identical on every tracked row of a page | tracked 10 (hard flag: the value differs across the page's tracked rows) |
| No abbreviation or spelling variant tracked twice; ambiguous shorthand the one exception | tracked 11 |
| Stage from the three-value vocabulary, tested by who does the work | tracked 13 (vocabulary); audit A7; the label itself is a hand decision |
| Play on every row, provisional until tracked | tracked 13 |
| Wave on every row, wave 1 revenue-weighted | tracked 13 |
| Family on every row, D and L never tracked, no page written from one family | tracked 13 |
| Fan-out block on every row, labelled, no fan-out string loaded | tracked 7, 13; the platform load is a hand check |
| Observed rows verbatim or anchored; simulated rows labelled; grounded share and per-source split | grounding |
| Each prompt belongs on its page; selling pages carry mention rows; a selling page of citation rows blocked | audit A1 |
| Keyword-less rows sit on the page's core terms or the core page | audit A2 |
| Placement evidence when SERP clusters exist | audit A6 with `--evidence`; otherwise the partition and A2 |
| One simulated cost row per selling page (Service Page or Product Page only), one persona row per set, one simulated OWN row per topic cluster (`--own-budget`; observed rows never count toward budgets or caps) | tracked 5 |
| Near duplicates kept only with a written reason | tracked 6 (printed for the hand read) |
| Prompt length, instrument signatures, dangling pronouns | tracked 1 to 3 |
| Spelling follows the client's market | tracked 8; hygiene 7 |
| Every sheet carries a Source column | hygiene 1 |
| No em dashes | hygiene 2 |
| No narration of how the data was gathered; no AI vocabulary | hygiene 3, 4 |
| Content type from the six values, SERP-derived | hygiene 5, tracked 13 (the value); SERP-derived is a hand check |
| Scope Map with T1 / T2; clusters marked IN SEGMENT / DRIFT / ADJACENT-ASK | hygiene 5 (values), `--require-sheets "Scope Map"` |
| Exclusions tab accounting for every cut, a reason on every row | hygiene 1 and the reason-column check; verify_deliverable 7 where the layout matches |
| Ship only what was asked plus one sheet | hygiene 6 with `--asked` |
| The cleaned keyword list: duplicates, near duplicates, evidence floor, totals, superlatives | verify_deliverable |
| Long-tail figures only after the split | longtail_split (hand-run; the run notes name the split) |
| Every reviewer comment answered, every message of a thread; the design the reviewer signed off kept | review; the reviewer's edits without a comment listed by `--previous` and answered in the reply |

Hand checks no script can make (each named in the definition of done): the service list confirmed; question tools run
with the harvest exported and verified; the credit cost counted before the run; three relevance levels per prompt;
topics with no question data reported; the demand verdict per line; the open-goal sweep; placement-only labels; the
eligibility and liability pass; B3-existing; the delta shape on a second pass; the "client can be THE answer" read;
verticals only on the hub and shared intents once per cluster; live URL status checks; the seed chain in order and the
loop closed; competitors' organic keywords and the ads read; the tools-versus-services split; no keyword cut for an
informational SERP; the client's own category noun; no unverified visibility-tool field in the deliverable; the final set
saved as next run's `--tracked` file; the platform load reconciled; a load-only ask shipped as a load under the one tag
named; nothing of this method in a brief embedded in another tool; the reviewer's direct edits each carried or declined.

## 4. Vocabularies (closed lists, one place)

| decision | values | where it is made |
|---|---|---|
| Scope tier | T1 (publicly supported), T2 (needs messaging sign-off) | Step 0 Scope Map |
| Drift mark per cluster | IN SEGMENT, DRIFT, ADJACENT-ASK | drift check, every lap |
| Keyword verdict per row | `IN|<play>|<reason>` or `OUT|<reason>` | seed-chain C6 |
| Trap decision | Excluded, Not a target, kept but FLAGGED, one exemplar kept | data-traps |
| Audit-finding verdict | accept, partially accept, REJECT with evidence | seed-chain C6-audit |
| Content type | Guide, Service Page, Product Page, Listicle, Glossary, Research Post | from the SERP |
| Grounding tier | tier 1 (observed: question tools, PAA, Search Console human rows), tier 1b (client's signed-off keyword set, keyword-verbatim), tier 2 (authored FAQ blocks, never grounding), S (simulated, labelled) | B3; not the Scope tiers |
| Basis | `observed: <source> "<anchor>"` or `simulated, family <X>; <what was checked>` | Prompt Map |
| Stage | Awareness (learning it, or doing it yourself), Consideration (evaluating an approach or provider type), Decision (choosing a provider, committing spend) | B2; a tracking platform's own stage vocabulary is mapped to these at load time |
| Answer type | Destination, Transact, Contrast, Specifics, Shortlist, Solutions, Steps, Fit, Concept (section 3 decision order); KPI default Mention for the first six, Citation for the last three | `intent-format-kpi.md` |
| Page type (for the page check) | selling page = Service Page, Product Page; list page = Listicle, not a selling page; guide = Guide, Research Post; glossary = Glossary | `intent-format-kpi.md` section 5 |
| Need | Know, Do, Website, Visit (Google Search Quality Rater Guidelines user intents) | `intent-format-kpi.md` |
| KPI | Mention, Citation, Evidence mention | B2 |
| Play | Defend (70%+ mention), Strengthen (10 to 70%), Capture (under 10%); provisional until tracked | B2, Phase 3 |
| Form | NB, OWN, COMP | prompt-matrix |
| Family | A to L (D and L are brief inputs, never tracked) | prompt-matrix |
| Fan-out label | O-ui, O-bing, O-as, O-gsc, S-compress, S-axis | B3-fanout |
| Page check (in `Answer shape and page check`) | match, partial, mention route, MISMATCH | B2-format |
| Placement verdict | MOVE, CONFIRMED, SUPPORTED, LOW CONFIDENCE | B3-crosscheck |
| Delta action | ADD ROW, UPDATE ROW (UPDATE ROW (fold into <cluster>) when an earlier row is kept and re-scoped), UPDATE SLUG, REMOVE, FOLD INTO EXISTING, APPEND NOTES, DUPLICATE (owner decision), HOLD: not loaded, NOT LOADED: page deleted, NO CHANGE | B3-delta; HOLD and NOT LOADED record a reviewer's comment, NO CHANGE names a sheet the pass left alone (`reviewer-round.md`) |
| Prompt Map row type (optional `Row` column) | TRACKED, PAGE, NOT TRACKED, KEYWORD ONLY, MOVED OUT, FOLD | only TRACKED rows are gated as prompts |
| Long-tail population | HUMAN, REPEAT, REPEAT-SET, OWN-TRACK, TRACKER, PERSONA_SHORT, STACK, TEMPLATE, PREFIX, AGENT, NOISE, other | `longtail_split.py`; a Search Console row is never labelled fan-out |
| Launch status | LAUNCH, HOLD, REMOVED, each with the reviewer and the date | `reviewer-round.md` |
| Prompt-shaped query (in an export) | six or more words, or opens with a question word, or ends with a question mark | the same definition everywhere |

## 5. Standing decisions (resolved conflicts; do not re-litigate)

- **Containment.** A row with a mapped keyword is contained by construction; only a keyword-less row with no core term is
  blocked (families C and I exempt). Containment is coverage guidance, not a veto.
- **Length.** Reported, never blocked at set level; the verifier holds 4 or 5 to 25 words per row. Observed phrasing comes
  first, even when PAA-short.
- **Keywords per prompt.** A page with keywords and no prompt is blocked; a high keyword-to-prompt ratio is a flag to check
  each row's keywords are one intent. One intent, one prompt.
- **Informational rows on selling pages** (a Listicle is a list page, not a selling page). A citation row on a selling page is a flag carrying its explainer obligation; a
  Mention row with no provider signal is blocked; a selling page made only of citation rows is blocked unless its page
  check says MISMATCH.
- **Placement.** The keyword-to-page assignment is the SERP-clustered step; a prompt sits on the page that owns its
  keyword; keyword-less rows sit on core terms or the core page; prompt-level SERP evidence (B3-crosscheck) feeds
  `--evidence`.
- **Grounding** reads Basis and Observed anchor, counts verbatim, anchored and keyword-verbatim (1b) on separate lines, and
  fails an observed row whose anchor is not in the corpus.
- **Stage vocabulary** is Awareness / Consideration / Decision everywhere.
- **Storage** for any browser accumulator is `localStorage` everywhere (`sessionStorage` dies when the tab group is
  recreated).
- **Keyword-gap forms.** Open every competitor slot first, then type the domains: on some tools adding a slot after
  typing clears the fields.
- **Programmatic sets.** One exemplar stays on the sheet with the set size on its row; the rest are cut as one block.
- **A term the client's own brief names overrides an earlier trap verdict**, and the row says so.
- **Evidence of shape.** Shape first (seed-chain gate 1); impressions then decide targeting among rows that passed.
- **The "too long" tell** is over 25 or under 4 words, matching the verifier (a PAA-calibrated "over 8" cut real prompts).
- **Floor on a provider-shortlist set.** The 50% floor fits an informational set. A provider-shortlist set (segment-,
  capability- and proof-qualified shortlists, alternatives, head-to-heads and destination rows: answer types Shortlist,
  Contrast and Destination, never Solutions, the most harvestable provider-naming shape) cannot clear it honestly, so it runs with a
  lower `--floor` AND a written `--floor-reason`; a lowered floor with no reason fails, so the bar is never lowered
  silently. Every other grounding check still runs, the report prints shortlist-shaped rows apart from the harvestable
  rest, and it lists POSSIBLE ANCHORS for simulated rows (observed strings sharing most of their words). "Simulated by
  design" is never a licence to skip the search: a best-of row labelled simulated while the harvest holds a near-identical
  best-of question is an anchored rewrite.
- **The Change column of a second pass is computed, never typed.** Diff the two data sets field by field (prompt text,
  keywords per row, reasons, carry, fan-out, basis, labels) and print one clause per difference; every removed or added
  prompt is also on a ledger with its reason, and the build fails on a changed prompt that is not listed.
- **Fan-out label format.** The bracket holds the bare label from the closed list; any evidence count follows the arrow
  (`[O-bing 14 cit]` fails check 13; `[O-bing]  ->  <heading>, 14 citations` passes). `O-ui` is kept only for an assistant
  search string used verbatim at 10 words or fewer and seen in three or more runs; a trimmed engine string is
  `S-compress`.
- **Provider signals (audit A1).** A prompt carries a provider signal when it asks for providers, products, vendors,
  agencies, tools, platforms, companies or "solution(s)", names an analyst report or ranking (for example a Gartner
  Magic Quadrant or a Forrester Wave), carries a buying word (book, buy, order, sign up, quote, download, subscribe,
  trial) or names one of the `--brands`: the answers to those name vendors. A Mention row without any of them is blocked,
  unless its page check is its answer type's default (match or mention route): A1 reads the answer type, so a
  Specifics or Transact row that is a match on its selling page is never blocked for lacking provider words. A row
  with a provider signal is never blocked for want of the word "provider".
- **Edit in place versus rebuild.** A rebuild counts as in place when it carries every direct edit the reviewer made
  (`review_round.py --previous`), keeps the reviewer's column order and adds new columns beside theirs.
- **Patterns versus one cell.** A comment on wording generalizes; a comment on a page's state or slug applies to that page,
  and the siblings it could reach go on the flags line for one yes. The default changes the first time the reviewer says
  "all of them".
- **HOLD versus REMOVED.** HOLD keeps every row in the map and every page total and loads nothing; REMOVED takes the page
  and its prompts out of the tracked set and keeps its keywords on the Keyword Map as KEYWORD ONLY rows.
- **Keyword text in a delta.** The market-spelling check skips a column only when its header starts with Keyword, so a
  delta column holding the client's keyword strings carries the word in its header.
- **Verbatim exclusion keywords that contain method words** (`<keyword containing a narration word such as "screenshot">`) cannot be
  reworded: clean the reason and note cells, and exempt the keyword column from the narration check with a written reason
  (`--skip-cols`).
- **Traffic notes name the site, not the tool**: "Google search on <domain>: N impressions" in a note; the tool belongs in
  the Source column.
