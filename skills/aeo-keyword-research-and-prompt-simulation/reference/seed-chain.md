# The seed chain, and the Search Console pass that starts it

Open this when Phase 1 starts and keep it open: this part decides whether the keyword set is real or surface-level.
SKILL.md carries the order; the detail is here.

Examples use an invented client, **ClientJ**, a bicycle-repair chain whose engagement covers one segment:
**e-bike servicing** (motor and battery diagnostics, firmware updates, brake work on electric bikes). Figures are
illustrative.

## 1e. Search Console is step one, run as many narrow regexes

Search Console is the only source of the client's real demand, including the question-shaped long tail that has no
keyword-tool volume at all. For an AEO engagement those zero-volume questions are often the most valuable rows.

**The 1,000-row ceiling is the reason for the method.** The UI returns at most 1,000 query rows per view, so a broad
catch-all regex truncates silently. **Run one theme per regex. A pass that reports exactly 1,000 is truncated: split
it and re-run.**

**Iterate: each pass tells you the next regex.** Read the returned queries for vocabulary you did not seed, then run
that. A short stem that accidentally matches inside a longer word can expose a whole cluster (for ClientJ, a `charg` stem
meant for chargers also caught `charges` and `surcharge`, and with them a run of questions about what shops charge
to look at a dead e-bike, a pricing cluster no seed had asked for): read what the accident surfaced, keep what is in
scope, and run it again on purpose as its own regex.

**Mechanics.** The filter goes in the report URL, no dialog needed:
`.../performance/search-analytics?resource_id=<encoded property>&num_of_months=16&query=~<urlencoded regex>` (`~` =
matches regex, `!` = exact; `&breakdown=page` switches the table). Use 16 months. Run passes for at least: the brand's
product names, each named channel or platform, each competitor name, the category nouns, buying-intent words,
measurement words and question openers. If the property is not on the default signed-in account, test the account index
in the URL (`/u/0/`, `/u/1/` ...).

**Brand split: write the brand regex at Step 0 and split every pass into BRAND and NON-BRAND.**
1. Write ONE brand regex in the Scope Map before the first pass, from the client's product list and every legacy or
   acquired product name its pages and docs still carry, for example `client[ -]?j|\bj ?cycles\b|\bwheelwright\b` (invented).
   Wrap short names in `\b`. Grep the first theme pass for misspellings and add them.
2. The report takes one query filter at a time and its regex engine has no negative lookahead, so a theme regex cannot
   also exclude the brand. Export the theme pass as it is, apply the brand regex offline in the merge script, and label
   every row BRAND or NON-BRAND before any row is read, counted or sent to the keyword tool. The label transcribes the
   stated regex; it is not a relevance decision.
3. Run the brand regex as its own pass on every property, so brand demand is sized from a complete export.
4. Report brand and non-brand totals separately, state the brand regex in the Source column or the scope tab, and keep
   brand rows on the product page (navigational) or the Exclusions tab, never in category sizing.

**The regex is substring-matched, not word-matched. Use `\b`.** A short stem matches inside unrelated words (`rim` inside
`crime` and `primer`, `gear` inside `gearbox` for car repair) and turns a clean pass into a junk pass. Check
the top rows of every pass before trusting its count: if the head looks like a different topic, the regex leaked.

**A capped pass is itself a finding.** When a narrow, well-formed regex still returns 1,000, that family is
programmatic scale: report it as such (rows, impressions, clicks), not only split further.

**Per-URL queries.** For every page in the page map, filter by page (`&page=!<urlencoded full url>`) and read its
queries. A page with impressions and no clicks is a refresh candidate with evidence attached. Then **measure the prompt
shape** of what the page ranks for: count the prompt-shaped queries (six or more words, or opening with a question
word, or ending with a question mark: the one definition, used everywhere). A page ranking for questions it does not
answer in question form is the highest-value refresh in an estate, and it is visible only per URL.

**Two query classes worth naming:**
- **Quoted-operator vendor-evidence queries**: quote marks and site operators, three to five vendors, review-site
  evidence on one attribute. Research agents doing due diligence, not people. If the client ranks for them and is not
  in the vendor set, that is two failures: outside the consideration set and no review evidence to satisfy the query.
  Treat it as its own prompt family and its own brief.
- **`<competitor> alternatives` at scale.** Often the largest block in an established brand's export. Those SERPs are
  third-party roundups, so it is a placement play. Check the client's own `<brand> alternatives` separately: a defence
  priority that usually has real clicks.

**Getting a full table out of the browser.** Console returns truncate. Build a file from the parsed table and trigger
a client-side download, then verify it on disk:
```js
const tbl=[...document.querySelectorAll('table tr')].map(r=>[...r.cells].map(c=>c.innerText.replace(/\t|\n/g,' ').trim()));
const a=document.createElement('a');
a.href=URL.createObjectURL(new Blob([tbl.map(r=>r.join('\t')).join('\n')],{type:'text/tab-separated-values'}));
a.download='gsc_<pass>.tsv'; document.body.appendChild(a); a.click();
```
This satisfies the screen-read rule (the artefact on disk is the whole table).

**Browsers block repeat automatic downloads from one site.** After the first automatic download, the "multiple
downloads" permission silently blocks the rest, and the report's own export button is blocked the same way. When files
stop landing, stop and ask the user to allow downloads for that site; do not fall back to reading the table off the
screen. Use a browser profile where downloads save without a native Save dialog: an automated agent cannot operate an
OS dialog.

**Then feed the keyword tool.** Every interesting Search Console query becomes a seed (2c).

## 2c. The seed chain: Search Console -> gap -> overview -> expansion

Run it in this order every time. Skipping a step produces a surface-level list.

**C1. Competitors first, and the data picks them**: the comparison prompts Search Console shows the brand surfaced for,
the head-term SERPs, and the ads transparency read. Run the brand's own compare pages too. Cover both markets of the
two-market split (platform rivals and services rivals).

**C2. Keyword gap, in batches.** A gap tool compares the brand with a handful of competitors at once (often four): run
as many batches as the set needs; one is never enough. Work the "untapped" and "unique" views, not only "all" (mostly
shared commodity terms). After the first run, lift the resolved URL pattern and navigate directly for later batches.
On forms that clear filled fields when you add competitor slots, open the slots first, then fill them.

**C3. Strip brand noise before reading anything.** Competitor brand names dominate the top of every gap export: filter
them out, and strip the tool's long-tail concatenation artefacts (strings that read like a sentence of feature words,
doubled words, a competitor domain embedded in the phrase).

**C4. Bulk overview, in batches.** Run the relevant gap keywords, the existing keyword list and the Search Console
queries through the bulk overview for volume, difficulty, CPC and intent. Search Console questions often return no
volume: expected, and not a reason to drop them (C4-zero).

**C4-mechanics (web UIs change; verify each time).** Batch about 50 keywords per run even where the cap is higher:
paste and render slow sharply above that and long calls time out. Navigate fresh between batches. If the app ignores a
programmatic value write into its editor, a synthetic paste event usually works. Some result tables are not `<table>`
elements and render after several seconds: poll for the row elements and take a screenshot before concluding a submit
failed. Accumulate across batches in `localStorage` (page variables die on navigation; `sessionStorage` dies when a tab
group is recreated), then get the whole set out in one download. Keep the page URL short after each batch so later
tool results do not echo a multi-kilobyte URL. Further automation lessons that recur across keyword-tool web UIs:
- An editor that strips a leading newline merges the first pasted line into whatever the URL seeded: paste a
  duplicate of the first keyword ahead of the list and drop the merged artefact row afterwards.
- Never send destructive editing commands into the app's own editor; to reset it, use its clear control or navigate
  fresh. Once a large results table is on the page, the next paste can slow past a timeout, so navigate fresh first.
- A submit button that ignores a plain programmatic click often responds to the full pointer sequence (pointer and
  mouse down, then up, then click). Find the button inside the form's own container: a second control with the same
  label elsewhere on the page looks identical to a selector or a find-by-description tool.
- Do not hand-build an encoded URL parameter the app generates itself: many apps discard it and regenerate it from
  another parameter, so you land on a one-keyword report. Do not rewrite the URL history before results have
  rendered: it can desynchronise the app's route state until a fresh navigation.
- URL length has a ceiling (a few thousand characters returns an error), so long keyword lists go in by paste, not
  by URL.

**C4-zero. The zero-volume block is a deliverable.** List it. When many zero-volume terms share one shape
(`<service> on <new vehicle class>`, `<check> before <resale or rental>`) and several are live Search Console queries with
impressions, that is the proof a category has not formed in the keyword index yet, and often the most valuable output
of the run. Those terms are **prompt targets, not SEO targets**: they are asked in assistants, not typed into Google.

**C5. Phrase-match expansion of every seed with volume.** For every keyword in the overview with volume, open the
expansion tool on that exact term (phrase match, not broad) and harvest its long tail. This step produces the
non-obvious groups.

**C5-view.** If an expansion view says "no data" and disables export, check the tool's other grouping view of the same
seed before recording the seed as an orphan: some views hide data another view holds, and never record an orphan from
the view that showed nothing. An export menu clicked right after navigation can swallow the click, and a second blind
click closes it again: wait, check the menu item exists, then click it. Verify every export on disk
(`<seed>_phrase-match_<market>_<date>.csv` style names help).

**C5-orphan. An overview/expansion disagreement is a finding.** The overview is the exact-match index; the expansion is
the cluster index. A keyword with volume in the overview and no cluster in the expansion is an **orphan**: measured
demand, no surrounding vocabulary, nobody has built the topic. Orphans are the cheapest wins in a set. Never delete a
term because the expansion returned nothing: check the overview, and if it has volume, keep it and flag it.

**C5-tail. Read the tail's modifiers before trusting the head's difficulty and CPC.** A head term can look perfect and
be aimed at the wrong buyer: when its tail is `... student discount`, `... at a free community workshop`, `...
for under $X`, `... in <another country>`, the difficulty is low because the competing pages are cheap vendors and the
searcher is a bargain shopper.
Geography, price and cheap modifiers identify the real buyer. Run this on every head term.

**C5-definitional. Separate a category term's volume from its intent.** A cluster whose every member is definitional
(`X explained`, `what does X mean`, `X or Y which is which`), with no commercial modifiers, is not dead: it is a
**citation anchor**, not a money page. Whoever writes the definitive answer becomes the source engines quote. Brief it
that way and say so, so nobody expects leads from it.

## C6. Clean the list by hand, row by row. A regex may never decide relevance

A pattern rule fails both ways at once: it leaves junk in (every wrapper variant of the category term) and silently
deletes good rows (a zero-volume natural-language question that states exactly what the client sells). Both look the
same from outside: a list. You find them only by reading.

1. Print every candidate with volume, difficulty and CPC, sorted alphabetically so variants of one stem sit together.
2. Read in batches of about 150 and write a verdict for EVERY row: `IN|<play>|<reason>` or `OUT|<reason>`. Not a
   sample, not the top N.
3. The reason is a sentence a reviewer can argue with. "Tools market" is enough; "irrelevant" is not.
4. Only then write a script, and all it does is transcribe the verdicts. If it contains a relevance rule, step 2 was
   skipped.
5. Ship the reasons: a "Why it is in the set" column and an Exclusions tab that accounts for every cut row. The
   reviewer can then overturn a judgement instead of redoing the work.

**The inclusion test is four gates, and the order is the point.** A row failing gate 1 is out however good its numbers
and however well it matches the topic: a topic-first test passes strings that contain an on-topic word but are not
something a person would type, and every such row costs the file credibility.

- **Gate 1, SHAPE. Would a person type or say this?** No quote operators, stacked vendor lists, scraped titles,
  product-page sentences, grammarless noun stacks, year-suffixed tool output, machine-concatenated fragments. Evidence
  of shape: a keyword-tool volume is decent evidence a string is typed into Google. Search Console impressions are NOT:
  people paste operator strings and AI prompts into Google all day. Impressions decide targeting among the rows that
  pass this gate (data-traps 5c); they never prove shape. A keyword volume also does not prove a person says the string
  to an assistant: that evidence is the question harvest's (B3), where a keyword-verbatim row is tier 1b. So a
  zero-volume natural-language question with impressions passes gate 1 on its grammar, not its impressions, and an
  operator string with thousands of impressions fails it.
- **Gate 2, SUBJECT. Is the work the subject, or another vendor?** A comparison of three named vendors is about them.
  A navigational term sends the user to a platform.
- **Gate 3, ACTIONABLE. Can the client build a page for it, earn a placement against it, or be cited for it?** If the
  honest answer is "we would need to be placed IN this", it is a placement target for the placement brief.
- **Gate 4, SEGMENT.** The term names, or is unambiguously about, one of four things. Write the client's version of
  this list before reading:
  - **A DELIVERABLE** the segment produces (for ClientJ: a battery health report, a motor diagnostic, a firmware
    update, a full e-bike service).
  - **THE WORK** that produces it (torque-sensor calibration, brake bleeding, connector and loom repair, bearing swaps).
  - **AN OUTCOME** measured on it (range restored, fewer roadside failures, the maker's warranty kept valid).
  - **THE CATEGORY** (e-bike servicing, e-bike repair shop).

**The exclusion classes.** Name them up front so verdicts stay consistent across batches:

| Class | One clause each (ClientJ examples, invented) |
|---|---|
| Below the evidence floor | no difficulty, no CPC and no impressions (C6-floor) |
| Homonyms | the same word in another field's meaning (data-traps 5a) |
| Wrong side of the transaction | the searcher is the supplier (C6-side) |
| Wrong audience behind a good number | a CPC far below its group (C6-side) |
| Wrong geography, market or buyer | `... in <city abroad>`; single-rider terms on a fleet engagement |
| Positioning liabilities | on topic, still the wrong thing to be found for (C6-liability) |
| Rule-breaking tactics | `derestrict e-bike motor` |
| Whole-category wrapper | `bike shop` when the segment is e-bike servicing |
| Another product lane | the searcher wants to measure, test or view something in an app or device (`e-bike range calculator`), not have the work done |
| Free-tool or DIY intent | `bleed e-bike brakes at home` |
| Software category (tools / software / platform) | cut as ONE block with one sentence, so the client can reverse it in one decision (the product-vs-tools rule) |
| Adjacent discipline outside the segment | motorbike or mobility-scooter servicing |
| Another lane of the client's own work | a service the client sells that this engagement does not cover (road-bike wheel builds) |
| Vendor tier names | invented package words (`platinum care`); plain quality words stay IN |
| Practitioner talk | shop-floor terms mechanics use with each other and riders never type |
| Named competitor brand terms | a separate commercial decision, never silently targeted |
| Artefacts and operator strings | encoded strings, operator queries, programmatic page sets (one exemplar kept, data-traps 5b) |

**The product-vs-tools distinction (get it wrong and you cut the client's own market).** When the client sells a
product as well as a service, "tools" terms split, and the test is not what the tool does but **who already owns the
SERP**. Check it, do not reason about it:
- **OUT:** a query whose head noun is a tool or kit for an established job (`e-bike diagnostic tool`, `bike
  workstand`) resolves to the incumbent tool retailers. The buyer wants equipment; the engagement sells a service. Cut
  the class as one block with one sentence.
- **IN:** emerging vocabulary with no incumbent (`e-bike battery health certificate`, invented): nobody owns the
  SERP, so the client can. Thirty seconds on the SERP settles it.
Decide this before reading, or the batch will be inconsistent; mark any mid-review amendment in the reason rather than
quietly flipping earlier verdicts. Product shape never beats SERP ownership: a file with zero software rows is
defensible in one line, where a file with some software rows needs a paragraph nobody will accept.

**The vendor-alternatives rule.** For a segment engagement, almost all `<competitor> alternatives` volume is out of
scope. Keep a comparison query only if it contains a segment term (`is a dealer or an independent shop better for
e-bike servicing` stays; `<diagnostic app> alternatives` goes, however many impressions). Report the block's size separately as a
brand-defence item, so the demand is visible without polluting the keyword set.

**Keep a low-volume term if it is relevant; cut a high-volume one if it belongs to another intent.** For AEO, keep every
relevant zero-volume question: it is a prompt even when it is not a keyword.

**C6-output. One sheet, not four.** Do not split the cleaned list into Keywords / Money / Zero-volume / Search Console
tabs. Keyword-tool rows and Search Console queries share one sheet; a row with no tool volume carries its impressions
and clicks in those columns, and a "Demand evidence" column names the source that proved it. The reviewer reads one
list or cannot see the set: splitting the list is how irrelevant rows hide.

**C6-threshold. If you cannot read every query, say where you stopped.** Thousands of queries are not reviewable row by
row. Set a floor (default: 200 impressions OR at least one click), review every row above it, and STATE THE FLOOR in
the deliverable. A stated threshold is a decision; an unstated one is a silent cut, and pretending to have read every
row is the same dishonesty as a regex. Compute an "X or Y" floor as a union: computing one half undercounts, and the
number ends up in the deliverable.

**C6-reconcile. The Exclusions tab accounts for every item read, and folded is not cut.** Assert in the build script:
`items read = rows kept + variants folded + rows excluded`. Counting folded variants as excluded double-counts them.
State the identity in words in the TOTAL row.

**C6-gate. Run `data/verify_deliverable.py` against the saved file before shipping**: row-for-row match, duplicate and
near-duplicate sweep, the evidence floor, Search Console totals recomputed, group aggregates, head-is-top-row,
difficulty figures quoted in prose, cross-group superlative uniqueness, kept-vs-excluded collisions, double-booked
exclusion examples, README totals. It prints every surviving superlative for a human. Read the script before the hand
review: knowing what will be checked stops the errors being made.

**C6-fold. Redundancy loses a reviewer as fast as irrelevance.** `ebike motor repair` and `e-bike motor repairs`
as two rows break trust like a junk row does. Fold aggressively; folding is not deleting.
- Fold, never cut, a near-duplicate: the head keeps its volume, the variant goes into `Variants folded in` (count) and
  `Which variants` (list).
- Volume is HEAD volume only and never summed across variants, so any row can be checked against the tool. Search
  Console impressions and clicks ARE summed across head and variants. State both rules.
- The head is the highest-volume member; if a fold changes that, swap the head and push the old head into the variant
  list. Nothing is lost and the row count drops sharply.
- Normalise properly: `ies` -> `y`; words ending `ss` unchanged; else strip one trailing `s`; guard words of three
  letters or fewer (`us`, `vs`); fold compound spellings first (drop a hyphen inside a word, `e-bike` -> `ebike`; join a
  one-letter token to the next, `e bike` -> `ebike`), as `data/verify_deliverable.py` does; drop stopwords;
  lower-case; hash the sorted token tuple, and compare a spacing-insensitive key too (`wood working tools` /
  `woodworking tools`). Stripping `es` turns `services` into `servic`, which never matches.
- Run the collision sweep as a gate on the finished file: it keeps finding pairs after two full hand passes.
- Do not over-normalise two real head terms into one: when two standard names for a discipline are priced separately
  by the tool, keep both and say why (`data/verify_deliverable.py --exempt`).

**C6-floor. State an evidence floor and hold every row to it.** A row clears at least one of: a volume WITH a difficulty
figure, a CPC above zero, or Search Console impressions. A term at tiny volume with no difficulty, no CPC and no
impressions is a tool guessing. State the floor in the deliverable, then verify mechanically that no row breaks it.
**Credit the source of every difficulty figure**: a
figure from a later metrics refresh is not in the original export, so an auditor reads it as untraceable, and on a row
with a zero CPC the evidence floor then rests on it. Name the refresh and its date in the row's Source cell.

**C6-liability. Some rows are on topic and still the wrong thing to be found for.** Ask of every commercially strong row:
if the client ranked first for this tomorrow, would it help or embarrass them? Three tests, each a
cut: wording that casts the client as the thing it argues against; terms that promise what the client cannot deliver
(invented, for ClientJ: `guaranteed same-hour e-bike repair` when its vans book a day ahead); and terms exposed to a
platform policy or a regulation (removing a motor's legal speed limit). Say which test it failed.

**C6-side. Check which side of the transaction the searcher is on.** `sell my e-bike for parts` or `bike shop that
buys used batteries` read on topic and bring sellers to the shop, not customers. A sharp tell: a CPC an order of
magnitude below its group (people offloading old kit attract few bidders).

**C6-coverage. Before cleaning, check the head term is in the set.** Write down the five or six terms that MUST be in a
list on this topic, plus every product word in the client's brief, and grep the candidate pool. A clean list missing
the category head term is incomplete, and the client sees it in five seconds. A term the client's own brief names
overrides an earlier trap verdict, with the reason on the row. Run this check before the hand review, not after.

**C6-audit. The adversarial audit is a gate.** Run two independent subagents on the finished file and act on findings
one at a time with a written accept / partially accept / REJECT-with-evidence verdict. Rejecting matters as much as
accepting: check a claim like "these two rows are one intent" against both live SERPs before acting on it, and keep
the rejection and its evidence in the file (a typical case: an auditor wants two rows folded, the two top 10s share
no result, and both rows stay with the SERP comparison as the reason).
- **Auditor 1 reads as the CLIENT**: find the rows that would cost the file its credibility. Give it the business, the scope
  and the rules. It finds near-duplicates and inconsistencies you no longer see.
- **Auditor 2 reads as a FORENSIC accountant**: every number in the prose recomputed, every superlative proved or
  disproved, every stated rule checked for a counterexample. Expect it to find defects in a file that already passed
  the verification script (percentages that do not sum to their total, a rule stated in the README that one row breaks).
- **Re-read every page's prose after fixes land, then run the forensic audit last.** Per-page prose (findings, title
  reasons, SERP-shape notes) goes stale after remaps while every count still reconciles (invented: a SERP-shape note
  that still says listicles dominate after the page's head term changed). After the last remap, read each page's prose
  against its current rows, then audit.

**C6-figures. Make a false figure structurally impossible.** Never type a number into prose. Write each rationale as a
template with `{slot}`s, compute every slot from data, assert no `{` survives, and assert that every dollar figure and
bare integer in the finished string is one of that group's computed stats. Assert across groups too: only ONE group may
claim "the lowest difficulty", "the most expensive click", "the largest term".

**C6-traps. Four traps that corrupt figures silently. Check all four before quoting a Search Console number:**
1. **Page rows in the query pool.** A pages export merged into the query pool puts URLs in as "queries" and can carry
   most of a headline figure. Filter anything starting `http` or containing export UI text before counting.
2. **Curly vs straight apostrophes.** `what's` and `what’s` come back as separate rows. Normalise apostrophes, quotes
   and case, then re-aggregate.
3. **A floor stated as "X or Y" computed as "X".** Compute the union.
4. **An anomalous CPC or difficulty is a homonym tell.** A metric far out of line with its neighbours usually means
   another market shares the string (invented: `wheel refurbishment` priced several times its group because car
   alloy-wheel repairers bid on it). Check the meaning before the maths. Do not run the tell backwards: a $0.00 CPC alone proves nothing.

## C8. The SERP reverse loop (run it on every seed the reviewer calls good)

When the reviewer singles out a keyword as the right kind, it is the entrance to a class. The keyword tool's expansion
will not find the class when it is too new to have a cluster; the vocabulary lives on the pages that already rank.

1. **Search the seed** and capture the whole SERP, not the top three. Record the total results count: a total in the
   hundreds rather than millions is itself the finding (nobody owns it), as is a SERP that drifts to generic content
   after the first page.
2. **Run every ranking domain through an organic rankings report** and read what else those pages rank for. Prefer
   pure-play domains; a general news site returns noise.
3. **Read the ad landing pages if there are ads**: an advertiser has done the message testing. With no ads (itself a
   signal the class is uncontested), read the top organic pages.
4. **Scrape the top page and mine its structure, not its prose**: H2s, FAQ headings and comparison tables are targets
   someone has validated, and a comparison frame (dealer workshop, independent shop or mobile mechanic) is a prompt family.
5. **Permute the vocabulary against every piece of work in scope** and size it in one bulk batch. Expect most to be
   empty: that is the size of the opportunity, not a failed batch.

**Recognise the next good seed**: a piece of in-scope WORK in an emerging FRAME (for ClientJ, `battery health
certificate before selling an e-bike`, invented), with Search Console impressions already, no incumbent on the SERP and
single-digit difficulty. Keep the frame, swap the work (`motor check`, `brake inspection`): the swaps that carry demand
are new rows the client can own.

**And reject the drift, because expansion drifts fastest of all:**
- the frame applied to the whole CATEGORY rather than the segment (the same rule that cuts the whole-category service
  wrapper);
- a homonym of another market (the same frame word meaning a car-insurance or a phone-repair product);
- the frame applied to a PART the client could sell rather than the WORK it does (`battery health certificate`
  drifting to `replacement e-bike battery price`): a parts purchase, not a service, so it goes.

**C7. Mine the competitors' organic keywords and page taxonomy too.** The gap tool is no substitute for looking at
what each rival targets: organic rankings per rival, and their money pages scraped for meta, titles and H2s. Do it for
the services rivals as well as the platform rivals: the services rivals often hold the commercial vocabulary.

## 2e. Operational notes that save a run

- **Click by element reference, never by coordinate.** UIs re-flow between calls and the browser pane can resize
  itself; a coordinate click lands on a table row and silently re-filters the report to one query, which looks like a
  broken tool. Scroll the element into view first if it reports as outside the viewport.
- **Keyword-gap tools often resolve to a reusable URL after the first comparison**: lift it and navigate directly for
  later batches, switching the view (untapped, unique, common, all, weak, strong) by its parameter. Work untapped and
  unique first.
- **Organic rankings by URL**: for pages with a short ranking list, read the rows straight from the DOM, accumulate per
  page in `localStorage` and download once as a TSV. Faster than one export per page, and it satisfies the
  screen-read rule because the whole table lands on disk.
- **Read tables from the DOM, not `innerText`.** Column alignment drifts as soon as a cell wraps or is empty:
  ```js
  [...document.querySelectorAll('[role="row"]')]
    .map(r => [...r.querySelectorAll('[role="cell"],[role="gridcell"],[role="columnheader"]')]
    .map(c => c.innerText.replace(/\n/g,' ').trim()))
  ```
  Check every row returns the same cell count before trusting a number.
- **Rows per page can reset on every navigation.** Set it to the maximum after each navigate and confirm the pager. If
  it reads exactly `of 1000`, the pass is truncated.
- **Verify every export on disk**: list the downloads folder sorted by time, confirm name, size and timestamp. Parse a
  large listing with a script that returns only the newest entries rather than reading the whole listing. The
  downloads folder is not always the default path: confirm it first.
