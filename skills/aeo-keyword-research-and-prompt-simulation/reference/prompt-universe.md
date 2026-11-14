# Phase 2: building the prompt universe

Open this once the keyword set is FINAL, backfill included. B3 grounding has its own file
(`question-data-harvest.md`); this file assumes you have read it. Examples are invented, for **ClientJ** (a bicycle-repair
chain with city workshops, mobile vans and fleet maintenance contracts).

## The gate

**Phase 2 does not start until the keyword set is final, backfill included.** A prompt is derived from a keyword, so a
prompt simulated against a set still missing rows has to be rewritten when the backfill lands. The set is final when all
of these hold:
- the hand review is complete, with a written verdict on every row (seed-chain C6);
- the coverage check ran and found nothing missing (C6-coverage);
- thin pages were topped up to about 2 to 10 keywords or marked as deliberately carrying none;
- volumes were pulled fresh, not carried from a previous quarter;
- the reconciliation identity holds.

## B1. Keyword -> natural-language prompt

A prompt a real buyer would ask an answer engine, at the stage the keyword sits. One prompt = one answer type; **collapse
synonyms** (one prompt serves the group); **never track spelling or abbreviation variants** (they move cited sources less
than the model's own rerun noise); the one exception is an ambiguous shorthand, tracked spelled out AND short, with the
reason on the row (`intent-format-kpi.md` section 6). **Quality over quantity**: defer a low-fit keyword with a written
reason rather than invent a weak prompt.

- **Default caps: 2 to 12 tracked rows per page** (the verifier holds it; a service page typically 10 to 12, a listicle 6
  to 8; observed rows are uncapped), **and no more than about 20 per service line across its pages.** Thin pages get thin
  lists; do not pad a capture-only line.
- **Aim for a substantial universe** (dozens of prompts across lines). Do not lead the client with the raw prompt count:
  the count is not the story; the gap is.

**B1-waves. The tracking cap is not the design constraint: it decides load ORDER and nothing else.** The universe covers
the PAGE MAP; the platform's cap decides which prompts go in first. Sizing the universe to the cap leaves pages with no
prompt and no way to be measured.
- Build the full universe against the page map, then **ship it in waves.**
- **Wave 1 is revenue-weighted, not volume-weighted**: every Consideration and Decision prompt loads first; only then
  fill the remaining slots with the highest-volume Awareness prompts. Volume weighting spends a paid slot on the
  cheapest question in the set.
- Record the wave on the row, so the next load is a filter, not a re-derivation.

## B2. Tag every prompt

- **Topic**: the keyword cluster or service line (aim for about 20 prompts per topic over time, across cycles).
- **Stage**: Awareness / Consideration / Decision, the one vocabulary (cover all three; a platform's own stage names are
  mapped at load time). **Label by WHO IS DOING THE WORK, never by the question's grammar.** A how-to prompt is someone
  doing the job themselves: Awareness. Labelling "my disc brakes squeal when it rains, can I sort that out at home?" as
  Consideration makes a top-of-funnel set look like a funnel.
  - **Awareness** = learning what it is, or how to do it yourself.
  - **Consideration** = evaluating an APPROACH or a PROVIDER TYPE: doing it yourself vs hiring it out, whether the cost
    is justified, what to look for, how to vet one.
  - **Decision** = choosing a specific provider, or committing spend.
  A neat funnel that appears WITHOUT this test is usually a mislabelled top-of-funnel set: re-run the test before
  reporting any stage split.
- **Need, answer type and KPI**: the need (Know, Do, Website, Visit), one of the nine answer types (decided by what the
  answer must contain, by hand, with the reason on the row) and one of three KPIs (Mention, Citation, Evidence mention) following what the ANSWER will name
  (`intent-format-kpi.md`). Mention by default for the six provider-naming types; Citation by default for Steps, Fit and Concept (a "habits
  that make a chain last longer" prompt is a citation row, because the list is of habits, not vendors); Evidence mention
  for an explaining row whose prompt asks for proof or real examples the client holds first-hand (for example someone
  asking what a properly rebuilt wheel looks like, answered from a gallery of rebuilds the client has documented). Cue
  words alone mislabel a large share of rows, so every label is a hand decision with its reason.
  **These ship as columns or they do not exist** (a tag with no column never reaches a deliverable);
  `data/verify_tracked_set.py` fails a sheet without them. **State the KPI split for the set**: a set that is mostly
  citation rows, read against mention rate, looks like failure when it is not.
- **Play (provisional until tracked)**: Defend (70% or more mention), Strengthen (10 to 70%), Capture (under 10%).
  Provisional default: brand -> Defend, content-backed informational -> Strengthen, everything else -> Capture. Re-score
  from real data in Phase 3.
- **Wave** (B1-waves).

### B2-format. The page check: can the page supply the answer

Every page carries the answer shape its primary answer type needs and a check against its SERP-derived content type
(`intent-format-kpi.md` section 5):
- **match**: the page can supply that answer as it stands;
- **partial**: close, with one section to add in the brief (a guide carrying a provider-cost row, which needs the
  client's own price range);
- **mention route**: Solutions, Shortlist and Contrast rows on a selling page (Service or Product Page; a Listicle is
  a list page, not a selling page; Specifics and Transact there are match): the win is an accurate mention, and the
  list an engine cites will be someone else's;
- **MISMATCH**: explaining rows on a selling page, which an engine will not cite, or a Contrast row on a Product Page;
  restructure the page so the explanation leads, or write on the row that the page tracks nothing citable.
The check is one value per page, judged against the page's primary answer type (the most common primary among its
tracked rows; on a tie, the tied type that appears first), with a default per page type
(`intent-format-kpi.md` section 5); a page that departs from it says why on its rows.
What the page owes goes into `Page must carry`, the page notes and the brief.

## B3. Harvest the real question data first

Before a single prompt is written: `question-data-harvest.md` (source hierarchy, seeds, credits, capture, the six tells).

- **Tier 1, observed demand**: someone typed it; the only grounding. Run every question tool so its harvest is exported
  (or copied) and the file verified, never read off the screen; the reviewer must be able to re-check it. Breadth of
  seeds beats depth of expansion: the live People Also Ask block yields only a few questions per results page.
- **Tier 1b, the client's own verified keyword set, for commercial prompts.** A keyword with measured volume is people
  typing it; it is just not question-shaped, and the question tools go silent on buying queries. Where a prompt string IS
  a keyword in the signed-off set, that is grounding. **Count it separately**, never merged into the question tools, and
  exclude zero-volume terms. **Decide each by hand** against the keyword's volume, intent and page: an upgrade (the
  prompt already was the keyword verbatim), a swap to the searched string, or a reject (a near match that changes the
  subject, or would move a prompt onto a page already covering it). A near match is not a match.
- **Tier 2, authored content** (FAQ blocks on ranking pages, scraped from the top non-hub URLs): a hint about commercial
  angles, never grounding. Those headings are written for the page, by a marketer or a model, and carry the vendor's
  positioning. Re-ground every FAQ-sourced prompt in tier 1 or cut it; the tier-1 replacements are usually blunter and
  shorter.
- **Screen every prompt against the six tells** (`question-data-harvest.md`).
- **Grounding is a source, not a gate.** Where the question tools are thin, SIMULATE from the page's own verified demand
  and label it (`prompt-simulation.md`). A labelled simulated prompt that belongs on its page beats a harvested one that
  does not.
- **Hand-written is never unlabelled and never unaudited.** A prompt is written by hand only where no grounded phrasing
  exists in People Also Ask, the question tools, or the FAQ block of a page already ranking for the topic, and each such
  row names which sources came up empty. Learning the shape from the tools and writing your own string is what this rule
  stops: it looks like grounding and is not.
- **Record the anchor on every prompt**: the real query it is modelled on, or a note naming the sources checked and found
  empty. Ship the original wording beside any rewrite and report the grounded percentage.
- **Gate**: `data/ground_check.py` (run by `run_gates.py`). It measures verbatim and anchored matches, not sentence shape,
  because shape is what a written set fakes (an invented set can match a real corpus on length, clause rate and first
  person while barely grounded). Default floor 50%; it refuses tier-2 evidence, requires a family and reason on every
  simulated row, and fails a high rate scored against a thin corpus (under about 20 seeds). It prints the shape numbers
  for the reviewer and never gates on them.
- **Count a status field by its CONTENT, never by a prefix test.** A free-text status column accumulates prefixes
  ("DRAFT ... CHECKED ... HELD"), and `startswith` undercounts badly. Use `"X" in field` and cross-check against
  `ground_check.py`, which reads the prompt strings, not the labels.
- **No PAA block does not mean no demand.** Google often shows no question block for a buying query (services, a
  provider type, "alternatives"); a question tool's deep search usually still returns dozens of questions for the same
  seed. Go there before concluding a topic has no data.
- **First person is not automatically a tell.** People Also Ask and FAQ blocks use it ("How do I ...?"). Strip it where
  you invented it, keep it where the data shows it; stripping all of it over-corrects.
- **Some topics have no question data at all.** Practitioner vocabulary (the words an industry uses, not the words buyers
  search) can return nothing across a large harvest. That absence is a finding: it tells the client which pages have no
  demand behind them. Branded prompts are ungroundable by definition; mark them apart from rows that simply found nothing.
- **Read the autocomplete harvest, never ingest it.** A slice of any autocomplete corpus is a different subject that shares
  a word with the seed.

### B3-scope. The relevance test has three levels, and the third is the one that gets missed

Run all three over every prompt, in order, with the verdict per row:
1. **Grounding**: is this phrasing observed demand for the page it sits on?
2. **Surface**: does answering it mean changing the client's own pages, or work elsewhere (third-party sites, platforms,
   partners)? Match it to what the engagement covers. **Where the page is on the right side but the framing invites an
   answer from the wrong one, reframe rather than cut**: the same demand, re-asked so only the in-scope work answers it.
   A cut throws away the keyword behind the prompt; a reframe keeps it.
3. **Service line**: is this about the line THIS engagement tracks, or a neighbouring line the client also sells? This
   level fails silently, because a neighbouring-line prompt passes the first two cleanly. Two shapes:
   - **A neighbouring line the client sells.** Name the client's lines at Step 0 and hold each prompt against that list,
     not against the client's name. For ClientJ's fleet-maintenance engagement, "who fixes kids' bikes on a
     saturday morning?" is about the client's business (its walk-in workshops) and the wrong half of it.
   - **A prompt that drops its qualifier and climbs to the parent category.** "How often does a bike need a service?"
     on the e-bike motor diagnostics page: the page is in scope; the prompt walked out and now pulls the whole category.

**Reviewer approval of a PAGE is not scope clearance for its PROMPTS.** A page can be a legitimate build and still sit
outside the service line this set tracks; then its prompts are not loaded, and the row says why.

### B3-sim and B3-fanout

Where the harvest comes up thin, SIMULATE rather than ship a page with one prompt. Simulate from `prompt-matrix.md`
(read it first) with the method in `prompt-simulation.md`. A set that is provider shortlists by nature (a services
category; answer types Shortlist, Contrast and Destination, not Solutions) is simulated by design and runs the grounding gate with a lowered `--floor` AND a written
`--floor-reason`; it still reads the gate's possible-anchors list first, because an observed phrasing beats a constructed
one.

Every tracked prompt carries its **fan-out block**: 2 to 5 strings the engine will run to answer it, each with the heading
or passage the page must carry. Sources in order: observed in the assistant UI while the prompt runs (`O-ui`), the Bing
AI performance report (`O-bing`), an observed question-tool or Search Console string used as a retrieval string (`O-as`,
`O-gsc`); then compressed from
the prompt (`S-compress`: drop persona, verb and question mark, keep the nouns and the qualifier) and one per claimed
capability axis (`S-axis`).
- Fan-out is the most volatile layer there is: two runs of one prompt share only a small fraction of their fan-out
  queries. A block covers the retrieval NOUNS, never exact strings, and a string is called observed only after it shows
  up in three or more runs.
- An observed engine string keeps its `O-` label only when used verbatim at 10 words or fewer. Assistant search strings
  often run longer (strings of brand names, a site
  restriction); a trimmed one is `S-compress`.
- The bracket holds the bare label; any evidence count follows the arrow.
- The page brief is built from the fan-out blocks, not from the prompts, and fan-out strings are never loaded onto the
  platform. Fan-out is out of scope only by a written decision (`Not built: <decision and date>` in every fan-out cell).

### B3-cluster. The page column is an output of clustering, never an input

Even when the engagement is framed as "keywords for one page", every kept keyword is clustered on shared top-10 URLs
against the cluster CENTROID, and its page is the cluster's page (an existing page the brand ranks with, a page to
refresh, a new page, or an owned listicle), with a written reason on any keyword moved off its cluster's page. A map
where every row shows one page while the clusters point at many pages is wrong, and a reviewer will see it.
1. **Re-run the clustering whenever keywords are added** (a late source, expansion, competitor pages). A
   nearest-keyword shortcut is not a centroid check and ends in a pile of singletons.
2. **Every single-URL join is decided by hand** (accept or reject with a reason) before pages are set.
3. **If clustering points at more pages than the brief names, bring it to the reviewer before building**: it changes the
   deliverable.
The Keyword Map carries the centroid, the shared-URL count and the page reason on every row.

**Page capacity.** A cluster with no better existing page is not a reason to pile it onto the product page. A page
carries only the groups it can give a real section: typically the head term and its variants plus a handful of buyer
concerns the page can answer in full. A group forming its own SERP cluster with no centroid overlap with the
page's head gets its own page (a use-case or solution page, or a guide if its SERP is guide-led). Before choosing those
pages, read the client's content plan or go-to-market material: it may already plan one page per theme.

**Three pulls, two result sets.** A SERP feed can serve two different Google top 10s for the same query at random, at
times close to half and half. Related keywords share pages inside one set and almost none across sets, so a single pull
per keyword compares across sets much of the time and reads as staleness or noise. Rule:
- pull every keyword and every prompt **three times on the same day**;
- group a query's pulls into sets (4+ shared URLs = same set);
- line the sets up across queries (two two-set queries are linked when one alignment shares 2+ URLs and holds for 75%+ of
  their shared URLs);
- cluster each set separately with the centroid rule;
- compare any keyword, prompt or fan-out only with keywords inside the same set.
A query whose three pulls return one list is read only in its own set. A keyword's page is contradicted only when its
cluster points elsewhere in every set it appears in; even then a written reason (definition intent, an even split,
content type) can keep it, and every move goes to the reviewer with its per-set evidence first.

### B3-place. A prompt sits on the page that OWNS ITS KEYWORD

The keyword-to-page assignment is the SERP-clustered step, so a prompt derived from a page's mapped keyword inherits that
evidence, and the Keyword Map shows the tie. A keyword-less row (proof, cost, OWN, switching, persona) sits on its page's
core terms or on the cluster's core page; `data/prompt_audit.py` A2 blocks one that does neither. Never the reverse:
matching a prompt's wording against a page's keyword list is not placement.

### B3-crosscheck. Three sources per prompt, one verdict rule

Placement of every tracked prompt is checked against three independent sources, in order, only as far as needed:
- **S, the results page.** The prompt as written, pulled three times, compared inside each result set with the keyword
  sets: S is the page of the nearest keyword (2+ shared URLs; a tie across pages is no vote). Both sets on one page, or
  one set on a page with the other silent, gives S; the sets on different pages gives no S. S is independent only when
  the nearest keyword is not one of the prompt's own mapped keywords.
- **C, AI citations.** For every prompt S does not confirm: one run each in two answer engines that show sources. Credit
  each cited URL to the page(s) whose keywords rank it in any pull, split evenly across pages; C is the plurality page
  with 2+ credits; a tie is no vote. Citations stay a separate signal and never enter the keyword join.
- **F, assistant searches.** For prompts still unresolved: two runs with web search on in a fresh, logged-out or
  temporary session; pull each search the assistant runs once and join it to the clusters of the matching result set; F
  is a page with 2+ votes and at least half the landed votes. Tie-breaker only: placement rests on S and C.
- **Verdict.** MOVE: two independent sources point to the same other page. CONFIRMED: S agrees and nothing points
  elsewhere. SUPPORTED (keep): C or F points to the page. LOW CONFIDENCE: anything else; it stays and the first month of
  tracking decides. Independence check: when S and C agree on another page, recompute C without S's keywords; if C
  changes, they count as one vote.
- **Concept rows are flexible.** A Concept prompt may move to a use-case or selling page when two independent
  sources point there; the page then opens with a definition section, the tracked gate's "Concept row on a selling
  page" finding carries the reason, and the prompt's definition keywords go with it.
- **Page floor.** Apply a MOVE, then re-check the floor of the page it left. A move that leaves a page under two tracked
  prompts comes with a replacement grounded in a keyword whose cluster holds on that page in every set (its results page
  pulled three times before it goes in), or in the next grounded question for that page's own keywords (a Search Console
  or question-tool string) with its results page pulled, marked LOW CONFIDENCE until it has engine runs. With no such
  keyword, keep the prompt, flag it, and bring the page type to the reviewer.
- **Keywords never follow a prompt across pages.** After a move, every keyword mapped to the moved prompt is re-mapped to
  a prompt on its own page, and a keyword on the destination page that is the moved prompt verbatim moves onto it.
- **Side effects.** Moving a keyword moves citation credit for every prompt whose cited pages rank for it: re-score all
  prompts after keyword moves. A replacement prompt can land LOW CONFIDENCE itself.
- **Recording.** One Prompt Map column states each prompt's verdict and the numbers behind it (shared results per set,
  citation scores, search counts), with no method narration. Write `{page: [CONFIRMED and SUPPORTED prompts]}` for
  `run_gates.py --evidence`. Before delivery, recount every number in that column with a script against the score file
  and give it to a fresh-context checker: wording errors (two result sets written as one, a miscounted spread) pass every
  gate. An audit note "no SERP evidence file" means this step was skipped and the run is not done.
- **Engine-run hygiene.** Run answer engines one prompt at a time with a pause between runs (about 30 to 45 seconds;
  parallel bursts trip bot checks). A bot check is a blocker: stop and ask the reviewer to clear it, never work around
  it. Record the model on every assistant run: a free tier can fall back to a smaller model mid-session, and the fan-out
  shape changes with the model. Assistant search runs are the slowest signal by far: budget them, or agree up front how
  many runs per prompt the deliverable needs; because F is a tie-breaker, fewer runs per prompt still leave placement on
  S and C.

**Prompt clusters against keyword clusters.** Cluster the prompts on shared results-page URLs and compare them with the
keyword clusters: join a prompt page to a keyword page at 2 or more shared URLs (the calibration and engine of the
`prompt-to-page-serp-clustering` skill; use it rather than rebuilding one). The two sets were built from different
inputs, so agreement is evidence and disagreement is a finding about whichever is thinner. It is the only independent
test either set gets, and it is cheap because the results pages are already fetched. Prompts whose pages never merge
into a keyword page (for example prompts written from the intent ledger rather than from keywords)
show demand the KEYWORD set never reached. Read each non-merging prompt one of two ways and write which: demand the
keyword set missed (go back to the recirculation loop with it as a seed), or a prompt with nothing behind it (cut it).

### B3-spell, B3-coverage, B3-lean

- **B3-spell.** Read the spell / did-you-mean field on every prompt pull. When the engine rewrites the prompt's subject
  (an acronym read as a common word), that result set is not evidence for the prompt: pull the expanded wording, use it as
  the evidence, keep the observed wording as the tracked prompt, and say on the row which wording the evidence is for. A
  rewrite in Google warns that an answer engine may misread the shorthand too, so the page spells the term out next to the
  acronym.
- **B3-coverage, the mapping coverage pass.** After the first keyword-to-prompt pass, count the keywords per page that sit
  on a prompt only as the closest fit. Where 10 or more closest-fit keywords share one subject no tracked prompt carries,
  add ONE gap prompt for it, grounded the usual way (observed question first, keyword-verbatim row second), re-map that
  cluster by hand, and pull the new prompt's results before placing it. Stop when what is left is scattered long tail:
  never a prompt per keyword. The reason column keeps the "closest fit:" prefix, and the delivery note gives the remaining
  closest-fit count and the pages it sits on.
- **B3-lean, a prompt whose results lean to another page.** Rule on each by hand in the placement evidence cell: a prompt
  naming the client or its product stays on that product's page; a prompt whose anchor keyword sits on the page stays,
  with the other page named as the one that links in or carries a section; otherwise rewrite it to the page's own intent,
  or move it and move its keywords with it.

### B3-audit

`data/prompt_audit.py`, run by `run_gates.py`: does each prompt belong on its page. A selling page carries Mention rows
with a provider signal (a provider noun, a buying word, a brand, "solution(s)" or an analyst report name all count),
except that a row whose page check is its answer type's default (match or mention route) is never blocked for lacking
one: A1 reads the answer type; its
citation rows carry their explainer obligation; a selling page made only of citation rows is mis-typed unless marked
MISMATCH; keyword-less rows sit on core terms; stage and KPI on every row.

### B3-existing. Before any score: what the client already has

Check every candidate page against what the client already has, two ways:
1. **Live pages**: the content inventory's full URL list (or the sitemap, status-checked). A net-new topic that already
   has a live page is a refresh, not a build, and a keyword that page targets belongs to it.
2. **The client's own tracked prompts**: pull the whole set and use it as the `--tracked` file, because every one of those
   strings comes back out of Search Console as impressions. For example, a planned page whose expected uplift rests on
   impressions that are really the client's own tracker running its prompts is no uplift at all.
Impressions from tracked prompts inflate score uplift, so this runs before scoring.

### B3-set. The set-level pass, after every page is done

In this order: the keyword partition (every keyword to exactly one row); the "client can be THE answer" test
(competitor-only rows out); verticals to the hub with their keywords; glossary pages folded; shared intents tracked once
per topic cluster on its core page (displacement, fit, switching, proof, cost, OWN); one persona row in the set;
category-name variants collapsed to one shortlist row per page; the provider question on the service page and "best" on
its listicle; then `data/verify_tracked_set.py` with every near duplicate kept carrying a written reason
(`prompt-matrix.md`, allocation), the KPI split stated, and no abbreviation or spelling variant tracked twice unless the
shorthand is ambiguous and the row says so. Expect this pass to remove a substantial share of
rows; if it removes almost none, the rules were not applied.

### B3-delta. A second pass ships as a delta

When a content plan or tracker already holds approved rows for the set (a second pass, a rebuild on feedback), the
deliverable is a DELTA against those rows, never a fresh map: one line per existing row with its row id, the action (from
the closed list in `gates.md` section 4), the prompts kept by platform id, the prompts retired with a reason each, the
prompts added, the keyword moves, the new cell text, and the opportunity score as old -> new with rank.
- **Recompute the score over the FINAL approved set.** A set-relative score (percentiles) falls when the set shrinks to
  its strongest pages; an unexplained drop reads as lost value. Before recomputing, re-implement the original scoring
  and confirm it reproduces every original score exactly; only then recompute over the new set.
- **The Change column is computed, never typed**: diff the two data sets field by field (`gates.md` section 5). An
  independent read of a hand-written change column typically finds differences it never disclosed.
- **Every live id is kept or retired exactly once, and no new prompt duplicates a live text** (a "new" prompt that is the
  re-homed text of a retiring id becomes a kept id).
- While reading the existing rows, run the duplicate check on every sheet touched (same topic, same row id, same URL):
  rows marked duplicate may still be present.

## B4. The deliverable

ONE consolidated workbook with every requested layer (no separate file per phase), saved where the reviewer can open
it. See SKILL.md "Deliverable".

## B5. Load into the tracking platform

Map the set to whatever the client's tracker accepts. Platform mechanics (endpoints, field names, quirks) belong in that
platform's own documentation; what transfers is the discipline:

- **Map your stage vocabulary onto theirs at load time and record the mapping.** Read their accepted values off live
  records first: a value they reject is often stored as empty rather than refused, and the prompt arrives untagged.
- **Give this engagement its own container**, even when one with a matching name exists: read what is in it before
  reusing it. When the reviewer asks for a distinct label, create a distinct container as well as a tag, because a tag
  does not separate reporting if the platform groups by container. **Creating a shared container needs the owner's yes;
  a tag usually does not.** Ask for it in the first reply, with the reason, and carry on with everything else meanwhile.
- **Load only what the create call accepts, and find out what it silently drops.** Fields the platform derives (volume,
  intent, related keyword) come back empty however you send them. Read one created record back in full.
- **Pilot one record, read it back, then scale.**
- **Mark the prompt type.** A prompt naming the client, or the client against a competitor, is a brand prompt and is
  reported apart from category prompts. Check the platform's tracked-prompt cap per container before you plan the waves.
- **Before creating anything, text-match every prompt against what the tracker already holds** (case and punctuation
  folded): tag the existing ones instead of creating duplicates, and flag near-twins already tracked on their rows.
- **Every live prompt id is kept or retired exactly once, and no new prompt duplicates a live text.** A "new" prompt that
  is the re-homed text of a retiring id becomes a kept id; the build checks both before anything is written.
- **Retirements are staged, never deleted by you.** Tag the retirees and leave a filtered view with them selected, so the
  owner's only step is the delete click. Never delete tags or containers yourself: deletion is permanent.
- **Reconcile all three surfaces before calling it done**: the tracker, the page map and the delivery queue the team
  works from must agree on the count and on each prompt's page.
- Save the final set as next run's `--tracked` file (CSV with prompt, page, answer type, need, KPI): the
  platform runs these strings through Google, so they come back out of the client's Search Console as impressions and
  the next long-tail read has to split them out.

## Load-only asks (put a supplied prompt list into a tracker)

When the ask is to load a prompt list the user supplies, load that list as given and build nothing else: no added
prompts, no fan-out strings, no Prompt Map and no tracking sheet unless the owner asks for one. Ask what the output is
before building any further layer this skill can produce.

- **One tag for the whole list**, the one the owner named. Any type or grouping the list carries goes in a column or
  field of the content plan, never in extra tags.
- **Match against the tracker before creating anything.** Compare every prompt with what the tracker already holds,
  case- and punctuation-normalised. A prompt already tracked is tagged into the set, not created again.
- **Check the list with a short script** and report what fails instead of rewriting it silently: no empty rows, no exact
  or normalised duplicates, no em dashes, length within the verifier's bounds, no dangling pronouns (a follow-up turn
  such as "and does that cover parts?"), the list's own format held on every row.
  A supplied prompt changes only with the owner's yes.
- **Skipped, with the reason in the reply:** `run_gates.py` and the workbook gates, because no Prompt Map exists.
- **If the owner also asks you to write the prompts,** write them with B1 to B3 (harvest first, every simulated row
  labelled with its reason, labels and KPI decided once per kind of row and applied consistently), agree the mix of
  prompt kinds per page with the owner before loading, and state the grounded share. A question source that starts
  returning rate-limit errors is stopped and flagged, never retried in a loop or routed around.
- **Never delete tags or prompts yourself**: deletion is permanent and is the owner's click.
- **Read results by prompt kind only after several runs have accumulated**, because reruns share few cited sources.
- **When a prompt-writing step is embedded in another tool's generator**, its brief carries the output format, the closed
  type list, the shape and fit rules and an example, and nothing of the grounding tiers, matrix families, answer-type
  rules, KPI logic, thresholds, counts or sources. Show the owner the exact text before it is published. A generator that
  rewrites a page's whole entry on each run can change prompts already tracked: say so before it runs on a live page.
