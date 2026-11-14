# The prompt simulation matrix

**Read this FIRST, before writing a single prompt.** It is the primary reference for Phase 2. Grounding tells you a
phrasing was observed; this tells you what shape to put a prompt in when observed data runs out, which is most pages on
most clients.

Slots are marked `*like this*`. Every example below is **invented** and uses three fictional clients: **ClientJ** (a
bicycle-repair chain: city workshops, mobile vans, and fleet maintenance contracts for courier and bike-share operators),
**ClientN** (a ceramics studio: classes, open-studio memberships, a kiln-firing service for home potters, commissioned
tableware) and **ClientV** (a botanical-print shop selling art prints, custom framing and pressed-flower keepsakes
online), with competitors CompetitorA to CompetitorF. The shapes are what matter; fill them from your
client's own verified terms. Any figure in this file is an illustrative default, not a measurement.

**The evidence base is your client's own exports.** Templates come from the client's Search Console long tail (6+ words,
split by population), the Bing Webmaster Tools AI performance report, the searches an assistant shows while it answers a
tracked prompt (fan-outs), and the question harvest. Near-zero clicks are normal on all of them: impressions and
citations are the whole return.

**Not all of it is people.** Split every export by who wrote the query (next section, `data/longtail_split.py`) before
citing any figure. On a client whose prompts are tracked daily, a large share of the long-tail impressions can be review
sites' tool strings, other trackers' prompts and the client's own tracked prompts read back out of Search Console as
"demand". **Label every example you take from an export with its population; a volume on a row marked `instrument`,
`tracker` or `template` is a count of how often a tool ran that string, not of how often a buyer asked it.** The shapes
are still good shapes; the volumes are not demand.

**This matrix grows.** Every new client's long-tail export is a new column of evidence. When a client's split export
shows a family that is not here, add it with a synthetic example of its shape (never the client's query) and note the
kind of client it came from. A family seen on a single client is a hypothesis; on two, a pattern. Adding to it is part of
finishing an engagement, not a separate project.

---

## Who wrote the query: the populations

The single most consequential thing in this file. A prompt universe built from one population and measured against
another looks wrong to the client and is wrong, and a volume read from the wrong population is not demand at all.

| | person -> Google | person -> assistant (HUMAN) | instrument (a tool's prompt) | engine fan-out |
|---|---|---|---|---|
| **who wrote it** | a person | a person | a tracking tool, on someone's behalf: the client's own tracker, a competitor's, or a review site's | the engine itself, to answer the prompt it was given |
| **where it shows** | short Search Console queries, keyword tools, PAA | Search Console 6+ word export, question-opener rows | Search Console 6+ word export: persona + output-instruction rows, `score <brand> ... on <axis>` templates, exact 10+ word phrasings repeated several times a day | Bing AI performance report; the assistant UI while a prompt runs ("searching for ..."). Never a labelled Search Console population |
| **typical length** | 2 to 4 words; PAA about 6 | about 11 to 13 words on average, median around 10 to 11 | 10 to 50 words; persona trackers run long | Bing grounding about 5 to 8 words; assistant fan-outs about 8 to 12; almost never a question |
| **impressions per phrasing** | | flat: small numbers per phrasing, few outliers | one phrasing carrying hundreds to thousands over a quarter | n/a (citations) |
| **example (invented)** | `kiln firing service` | `do any studios fire pottery you made at home, or only their own students' work?` | `you are a shopping assistant. a renter in her thirties wants botanical wall art under 200 dollars. return five shops as a numbered list with prices.` | `kiln firing service home potters drop off` |
| **what it is FOR** | the keyword set and page mapping | the shapes a TRACKED prompt takes; the only volume that is demand | the measurement surface of the category: what its dashboards run. Design your own instrument to be comparable; never cite it as demand | what the PAGE must be retrievable for; the brief is built from it |

### The population labels (what `data/longtail_split.py` assigns)

| label | what it is | treat as |
|---|---|---|
| HUMAN | a question-opener phrasing a person wrote | demand; the shapes a tracked prompt takes |
| REPEAT | a human-shaped phrasing of 10+ words repeated several times a day for weeks | an instrument; read REPEAT rows as sets |
| REPEAT-SET | one 8+ word template with a slot swapped across variants, each under the REPEAT floor (invented: `is it worth paying to have a funeral bouquet pressed and framed properly`, with `wedding` and `anniversary` swapped into the same slot; the script groups rows sharing their first five words, last two words and length) | one instrument |
| OWN-TRACK | a match to the client's own tracked-prompt export (`--tracked`) | the client's instrument reflected back; never demand |
| TRACKER | persona preamble plus output instruction, harness text, context tags | instrument |
| PERSONA_SHORT | a short persona opening `as a`, `i am a` or `i'm a`, then a request, one phrasing per product noun (`as a first-time potter, suggest beginner classes near me`) | instrument |
| STACK | three or more vendor names in one string, usually "comparison" plus a year; runs only when the vendor names are passed with `--vendors` | instrument |
| TEMPLATE | a query starting with `evaluate the ` (anything follows); `best ` or `top ` followed immediately by a provider noun (tool(s), platform(s), software, solution(s), service(s), agency/agencies, company/companies, provider(s), app(s), vendor(s); `--template-noun` adds category nouns, for best/top only); `tool to`, `tools to`, `tool for` or `tools for` (anything follows); or `leading`, `highest-rated` / `highest rated`, `most reliable` or `most affordable` (anything follows). `--template-pattern` adds regex alternatives (no default), for example a `score <brand>, a <category> provider, on <axis>` opener. Checked after TRACKER, PERSONA_SHORT and STACK | instrument; family D axes |
| PREFIX | a noun string whose first character is `+` or `%`, often with a year | a tool's operator string |
| AGENT | search operators and watch or crawl instructions (`site:`, `inurl:` or `intitle:` queries; `watch <domain> for ...`; `list every page on <domain>`) | not demand |
| NOISE | a review site's or directory's tool strings hitting the site by collision, passed per client with `--noise` | not demand |
| other | non-English rows, bare noun phrases, templates no rule knows yet | read it; never count it as HUMAN |

Two more labels are applied **by hand** after reading the rows: **ACCOUNT-RESEARCH** (strings that research one
named organisation rather than the category it buys or sells in, typically run by sales-intelligence agents; not
demand) and any new tracker
form you spot before a rule exists for it.

The human-question opener list in the script is English. Non-English human questions land in "other". If the client
sells into non-English markets, extend the opener list with those languages' question words before trusting the split,
and read the non-English rows: they often carry real vertical demand.

Consequences, and they are not optional:

- **Split before you cite.** Run `data/longtail_split.py` on every long-tail export before a single figure from it goes
  into a deliverable or into this file. Pass the client's own tracked-prompt export with `--tracked` (their platform can
  usually export it even where a tool cannot read it back); with no export, the REPEAT flag is the fallback. REPEAT is a
  threshold, not a match: 8 to 9 word instrument prompts slip under it, so read REPEAT rows as sets, and the same brand
  or the same template noun across dozens of phrasings is one instrument. Where the client has a Search Console bulk
  export to a warehouse, run the same split there on the full table (`data/longtail_split_bigquery.sql`), which avoids
  the row cap of a UI export.
- **Re-split on every pull.** A split describes its own window only: which populations dominate can change completely
  from one pull to the next. The human rows keep their shape across pulls (length, qualifier tail, compound share), so
  the shape rules below hold whatever the pull.
- **A volume on a tracker's prompt is a run count.** Thousands of impressions on one long phrasing is the number of
  times a tool ran it and the page was cited, not the number of buyers who asked. Never rank a page, size a family or
  defend a prompt on it.
- **The tracked set takes the HUMAN shapes**: 12 to 15 words, a question opener on most rows, a qualifier tail on about
  40% (a default target), no persona preamble, no output instruction, no location injection. The "AI-native" tells
  (a persona plus an order to rank the answer) are the tells of a tracking tool, and a tracked prompt written to
  look like one measures the category's dashboards, not its buyers.
- **The brief takes the fan-out.** Every tracked prompt carries the 2 to 5 engine queries the page must be retrievable
  for (the fan-out block, below). The engine's strings are observed in the Bing report and in the assistant UI, or
  simulated by compression. A Search Console row is never labelled fan-out: Search Console cannot separate a tool's
  template from the engine's sub-query and Google does not document which it reports. Almost no assistant fan-out string
  ever appears verbatim in a Search Console export, which is direct evidence of the same point.
- **Do not screen a simulated prompt with PAA-calibrated rules.** "Over 8 words" and "has a second clause" are tells of a
  bad PAA question and tells of a *good* assistant prompt. Screening on them removes exactly the shape that earns
  impressions.
- **Length targets are per population.** 12 to 15 words for families A to K; 5 to 8 for family L (Bing grounding), 8 to
  12 for assistant fan-outs. Never one number across the sheet.
- **A page can win the person's question and lose the engine's.** They are different strings with different SERPs. Cover
  both or say in the deliverable which one you covered.

**The shape tells, condensed** (public analyses of AI-mode queries in Search Console reach the same split
independently):

| what you see | what it is | what to do |
|---|---|---|
| `yes`, `sure`, `show me`, `ok` as queries, at a low average position | a reply inside an AI conversation, logged as a query | below the 6-word floor anyway; never count it as demand |
| a trailing sentence or tag stating the asker's location or market, one fixed evaluation template run over companies and facets, the same sentence daily for weeks | a tracking tool | instrument; exclude from every demand figure |
| an XML-like wrapper carrying company and market fields around a question; a ranking instruction written in another language | a tracking tool's harness | TRACKER; keep only the final question as a candidate anchor |
| a demographic persona of a hundred words or more (age band, job title, motivations, pain points, then a question), sometimes in several languages | a tracker generated from ICP fields | TRACKER; keep only the final question as a candidate anchor |
| an instruction to search the web, return a fixed number of results and not invent any, around a question | an agent harness logged verbatim | instrument; exclude |
| an instruction to the assistant (`walk me through it slowly`), first-person context (`i commute on a ten-year-old steel frame`), a dangling pronoun (`how long does that take`, `is that normal`), politeness (`thanks, could you explain more`) | a person in a conversation | HUMAN. First-person context is a legitimate tracked shape (the persona without the tool's template); an instruction, a dangling pronoun or a please is a conversation turn, not a prompt to track |

Two more points from the same public analyses: a large share of AI-mode impressions carry no query string at all, so a
long-tail export sees well under the whole of what happened; and the passage that answers the question travels into the
AI response, not the title, which is why the fan-out block's obligation is a heading or a passage.

### Buyer shapes: where each one goes

- **A value challenge is an OWN row the page must answer honestly.** When a prompt sets the client against a cheaper
  route (`why would I pay for a ClientN membership if CompetitorD charges per firing?`), the page owes a plain
  cost-versus-value passage; without one the row cannot be won.
- **Industry-qualified demand belongs on the vertical hub**, as family A or E (`do any bike repair firms specialise in
  hospital staff cycle schemes?`), never on a generic page.
- **Review-sentiment rows are family I OWN rows** (`what do reviews say about ClientV's packaging?`). Review sites answer
  them, so the brief points at those surfaces; the page alone cannot carry them.
- **Measurement questions are NB rows in family G** (`how would a courier firm know fleet servicing is cutting
  downtime?`).
- **Hire versus do-it-yourself is decided at G4**: track only the version the page can win.
- **Delegated search is a family B variant without the persona template**: the asker lays out a situation and hands the
  search over (`two of our cargo bikes have dead motors and the nearest shop is forty minutes away. who could take this
  on?`). Treat it as one of the highest-intent service shapes and track it in that form.

---

## How to use it

1. Take the page's own verified keywords and build its **facet table** first (below). The facets fill `*category*`,
   `*product*` and `*capability*`, and they also decide which prompts are allowed to exist at all.
2. Take the page's JOB (from its content type) and pick the families that match it; each family header names its page
   types.
3. Fill the client-specific slots from the Scope Map, using the slot dictionary below.
4. **Default to the non-branded form** (the branded axis section). Branded prompts are the minority of real demand on
   almost every client.
5. Hit the length target for the family's population.
6. Label the prompt as simulated, name the family and the form it came from, and audit it with `data/prompt_audit.py`
   exactly as you would a harvested one.
7. Write its fan-out block (below): 2 to 5 strings the engine will run, observed in the assistant UI or the Bing report
   first, compressed from the prompt second, each labelled. The page brief is built from these, not from the prompts.

---

## Keyword containment: what gets TRACKED, and what is only kept

SERP clustering decides WHICH page a prompt belongs to among the candidates. It does not decide whether the prompt belongs
in the tracked set at all. Clustering joins on shared URLs, and two subjects sharing a SERP are not the same subject: a
cost question and a shortlist question can land on the same listicle and still be about different things. Left alone,
that fills a page with prompts it was never built to answer.

**A tracked prompt set is a measurement instrument, not a research output.** Every row runs daily, costs credits and moves
the page's visibility number. A prompt about a subject the page does not target does not measure the page; it adds noise.
The tracked list is narrow on purpose.

### The four gates (vetoes, in order, on every candidate row)

**G1 ASKED.** Would THIS client's buyer type this into an assistant, in these words? Not "is it a plausible English
question". A prompt only a practitioner would phrase that way fails, however good the keyword behind it. Write the ICP
down in one sentence before you start, and read every row against that person.

**G2 ONE INTENT.** Is this buying intent already covered by another row? **Cost is ONE intent** whether you say per bike,
per visit, per year, a plan or a callout fee. If two prompts would be answered by the same paragraph on the page, they are
one prompt. This is where most of the bloat lives: a set with six cost rows has not found six questions, it has found one
and written it six ways.

**G3 ANSWERABLE ON THE PAGE.** Can the page carry an answer, in some form, even if not in the prompt's own long-tail
wording? Every tracked prompt is a content obligation: putting it on the sheet means somebody has to make the page able
to answer it. If the honest answer is "this page would never say that", it is not a tracked prompt. Write the obligation
on the row so the brief inherits it.

**G4 WORTH WINNING.** If an engine cites us here, does it move the business? Three ways to fail: the answer names nobody
(definitional) on a page that sells; the asker is not a buyer; or **winning it argues against us**. On a guide or glossary
a definitional row is a CITATION row (`intent-format-kpi.md`): it passes G4 when the page can be the cited source, and it
is measured on citations, never on mentions. The last failure gets missed. "Could our warehouse staff learn to
fix the delivery e-bikes themselves instead of paying a contract?" is a real buyer question, and a balanced answer sends
half of them to the do-it-yourself route; being cited inside an answer that recommends the alternative is a loss wearing a
win's clothes. Track the version the page can win ("if a courier firm needs its bikes serviced overnight at the depot,
who does that?"), not the version that reopens the decision. The same failure in another coat: **a head-to-head between
TOOLS on a SERVICE page** (two home repair-stand brands set against each other on a workshop's servicing page) argues for
a tool over the service. The general rule behind all three: **a tracked prompt has to be one the
client can be THE answer to.** Read every row and ask whether the best possible answer would put the client in it; if the
best answer is a set of other companies, the row measures them, not the client. A prompt that sets three competitors
against each other and asks which wins (the three-name template under family C) has three answers and none of them is
the client: cut it wherever it appears, service page or listicle. The COMP form that survives is "what are the alternatives
to <competitor>", because it has an open slot. A listicle earns the comparison by listing the names, not by tracking
them.

### Containment is coverage guidance, not a veto

Making keyword containment the entry test is too blunt and throws out good prompts: a persona row ("I manage the fleet
for a courier start-up and half our cargo bikes sit broken every week; which repair services take on fleets?") carries a
qualifier the keyword set lacks and is still one of the most valuable rows on its page, because the role is a term the page should own.

Use containment for what it is good at:
- **Coverage**: the facet table says what the page is for and how much of the list each part deserves.
- **Drift detection**: a prompt whose subject belongs to another page's keyword set is usually that page's prompt. Re-home
  it rather than deleting it.

Then let the four gates decide. A prompt slightly outside the keyword set that passes all four belongs; a prompt dead
centre in the keyword set that fails G4 does not.

### Families D and L are brief inputs, never tracked rows

Template rows like `score <X>, a <category> provider, on <Y>` show the signature of a machine: zero or near-zero clicks
across many thousands of impressions, very few distinct four-word openings across thousands of rows (against thousands
of distinct openings in the human-shaped set), and near-uniform counts per row. That is a template a machine runs, not a
question a person asks. Which machine matters:

- **Family D is a tracking tool's template, not the engine's.** Its rows can be a review site's strings hitting the
  site by collision (NOISE), a tool's category-taxonomy fill, or one instrument scoring one axis at a time at a
  near-uniform count; whichever it is, the client's own tracker included, the volume is a run count. Family D fails G1
  by construction. Re-read the template's slots on every pull and give the brief one
  heading per axis the current template scores.
- **Family L is the engine's own fan-out.** The Bing AI performance report lists the queries the engine wrote to ground
  its answers: short noun phrases, almost never questions. Some are compressions of instrument prompts, which changes
  nothing about what they are: the retrieval string, whoever asked the question above it.

Both stay in the method and leave the tracked set. Family D tells you the AXES the category's dashboards score a vendor
on, so the brief covers each axis the client can honestly claim, one heading or passage per axis, and the deliverable
says which tool's template it is answering. Family L tells you the STRINGS the engine retrieves on, so the brief carries
them as headings and passages. Neither is loaded onto the tracking platform: the platform sends prompts to assistants,
and these are what a tool or an assistant writes for itself.

**Tracked families: A, B, C, E, F, G, H, I, J in their HUMAN shapes, and K only on a guide or glossary page as Citation
rows. Brief-input families: D (axes) and L (fan-out).**

**Treat family B's export volume as tracker output until the split says otherwise.** The tells: persona rows that
recur across role variants with the same output instruction, or that reappear in several languages with the same
wording. Either is one tracker's set, and its volume is a run count. That does not invalidate the persona SHAPE: a 15 to 20 word prompt in which a buyer says who they are
before asking is real behaviour, and it overlaps its page better than a bare shortlist does (see the SERP-placement
section below). It invalidates the volume. Write persona rows without the output instruction unless a forced ranking is
a deliberate instrument decision applied to the whole set and stated as one.

### The fan-out block: every tracked prompt carries the queries the engine will run

A tracked prompt is what the platform measures. The engine does not retrieve on it: it fans out into its own searches,
and the page is cited only if one of those retrieves it. Google calls this query fan-out and reports nothing about it at
query level; Bing lists the strings; the assistant UI shows them while the prompt runs. A tracked prompt without its
fan-out is a measurement with no content plan behind it, and a page written only for the conversational shape can lose
the retrieval that feeds it.

Every tracked row carries a **fan-out block**: 2 to 5 strings the page must be retrievable for, each labelled with where
it came from, in this order of preference:

1. **O-ui**: run the tracked prompt in an assistant with web search on and in an AI search mode; record the "searching
   for" queries it shows. Per prompt, cheap, and the one observation available for every row. Do it for every row that
   will be tracked. **O-ui is used only for a string kept verbatim at 10 words or fewer.** Observed assistant search
   strings are often longer than that (vendor lists, "official documentation"); a trimmed engine string is S-compress.
2. **O-bing**: a family L string from the Bing AI performance report on the same subject, with its citation count after
   the arrow.
3. **O-as** / **O-gsc**: an observed question-tool or Search Console string used as a retrieval string (never labelled as
   the engine's fan-out).
4. **S-compress**: the tracked prompt compressed to its noun phrase, family L style: drop the persona, the verb and the
   question mark, keep the nouns and the qualifier. `if a courier firm needs its bikes serviced overnight at the
   depot, who does that?` -> `overnight depot bike servicing courier fleet`.
5. **S-axis**: one string per capability axis the page claims, in the family D frame with the category noun and no brand:
   `bike fleet servicing hydraulic brake bleeding`.

**The consensus core goes in the brief, not in the block.** Two runs of one prompt share only a small fraction of their
fan-out strings, but the words present in at least half of a prompt's observed fan-outs (kept in first-seen order) are
stable: `where can i get a wedding bouquet pressed and framed?` -> `pressed bouquet framing wedding keepsake service`. It is a word set
for the brief, not a phrase: never use it as a tracked prompt, never as a fan-out line (it has no label in the closed
list), and never as an ad keyword. An assistant's ads matching runs on its own model, so fan-outs do not describe what ads
are matched on.

Three gates on a fan-out string, mirroring the four on a tracked prompt:

- **R1 ATTACHED**: it names the tracked prompt it serves. A fan-out with no prompt above it is drift.
- **R2 ENGINE-SHAPED**: 5 to 10 words, noun phrase, no persona, no question mark, no output instruction. Observed strings
  of 10 words or fewer pass by definition; longer ones are trimmed and become S-compress; simulated ones are written to
  this shape.
- **R3 MATCHABLE**: the page has, or the brief commits to, a heading or passage carrying those terms. Write it on the row
  the way G3's content obligation is written. This is the line the writer works from.

Format of each line: `<string>  [<label>]  ->  <heading or passage>`; the bracket holds the bare label, and any evidence
count follows the arrow. Call a string observed only after it has appeared in three or more runs (fan-out is the most
volatile layer there is). The page brief is the deduplicated union of the page's fan-out blocks, grouped by section, not
the list of tracked prompts. Many prompts share fan-outs; that is expected, and it is what makes a page cohesive rather
than a list of answers. Fan-out strings are never loaded onto the tracking platform.

**Running the engines for O-ui.** Run the answer engines one prompt at a time with a pause between runs (30 to 45 seconds
is a safe default); a parallel burst trips bot checks. A bot check or captcha is a blocker: stop and ask the reviewer to
clear it, never work around it. Record the model on every assistant run: a free account can fall back to a smaller model
mid-session, and the fan-out shape changes with the model. Assistant fan-out runs are the slowest signal in the method,
so budget them or agree up front how many runs per prompt the deliverable needs; where runs are cut short, the fan-out
is a tie-breaker only and placement rests on the SERP and citation evidence.

**What instrument rows are still good for.** A TEMPLATE row (`mobile bike repair services for delivery fleets`) is what
the category's tools submit, and their dashboards are what buyers and competitors look at. Keep the page-level set of
them in the brief under its own heading, "instrument surface", separate from the fan-out block: being retrievable for
them is how the client shows up in other people's measurements. Do not confuse the two, and do not track either.

### The intent ledger sizes the list

Coverage is counted in INTENTS, not keywords. For a page whose job is to sell:

| intent | what the buyer is doing | value if cited | track? |
|---|---|---|---|
| shortlist | wants names | HIGH, the whole game | yes |
| qualified shortlist | wants names for their segment or vertical | HIGH, pre-qualified | one per live segment |
| displacement | has a name in mind, wants alternatives | HIGH, we take a slot | yes |
| head to head | comparing named vendors | HIGH if we are one of them | one |
| fit | has a constraint: will this work for me | HIGH, the buyer self-qualifies | yes |
| capability | needs a specific thing done | HIGH | one per real differentiator |
| switching | has an incumbent | HIGHEST intent in the set | yes |
| proof | wants evidence it worked | MEDIUM-HIGH | one |
| cost | forming a budget | MEDIUM | **one simulated row; every grounded cost row is tracked** (a pricing question and a cost-control question are different observed needs) |
| build vs buy | deciding whether to hire at all | LOW to NEGATIVE (G4) | reframe or hold |
| selection criteria | how to evaluate a provider | LOW here, HIGH on the guide | on the guide only |
| definitional | learning the category | NONE on a selling page (a citation row on its guide or glossary) | no |

These ledger intents are buying jobs on a selling page; each tracked row still carries one of the nine answer types in
`intent-format-kpi.md`: shortlist, qualified shortlist and displacement are Shortlist; head to head is Contrast (an "or" between two approaches that names no provider is Fit); fit,
capability and proof are Shortlist in the NB form (which providers in a named category clear the constraint) and
Specifics when they name the client or one provider; cost is Specifics for a provider's price and Fit for a generic
budget; switching is Shortlist (Solutions when the asker states only the problem, Contrast when it names the incumbent
against one rival); build vs buy is Fit; selection criteria is Fit on its guide; definitional is Concept.

Roughly one prompt per live ledger intent, plus a second only where a facet carries a genuinely distinct buyer. **Default caps:
a service page tracks 10 to 12 SIMULATED rows, a listicle 6 to 8**, weighted to shortlist, qualified shortlist, head to
head and proof, because that is what a shortlist page is for. A page with 40 tracked prompts has not found 40 questions.

**Grounded precedence.** The caps exist to stop over-simulation, so they bind SIMULATED rows only. A prompt grounded in
observed data (a Search Console query, a question-tool row, a keyword with volume, an engine template that names the
client) is never dropped to meet a row cap, the OWN budget or a one-per-intent rule, and never counts toward any of them; it
is cut only for failing relevance, the page's scope or the sensibility test. A page can end above the cap with every row justified, each observed row saying what it
rests on.
`data/verify_tracked_set.py` counts only non-observed rows against the cap and the OWN budget.

**Families C and I are the containment exception.** A head-to-head or review-surface prompt names vendors, and the vendor
names ARE the provider nouns, so containment is tested on the category phrase rather than the full keyword: `anything like
CompetitorB's drop-in wheel sessions but cheaper?` can carry real impressions with no category noun at all, and forcing
one in produces a string nobody types.

### Allocation across the set (the second pass a reviewer asks for)

A first set usually fails on set-level rules rather than on the quality of single rows, and these rules typically shrink
it a long way. They fall into four groups: what each page carries, where keywords sit, what is tracked only once, and size.

**What each page carries.**

- **A service page and its listicle share a subject by design**, in different shapes: the provider question on the
  service page ("can someone service our courier bikes at the depot so we stop wheeling them in?"), the list question on
  the listicle ("which fleet bike servicing companies get the strongest reviews?"). Two pages of the same type carrying the same question is a cut, and a listicle keeps one proof
  row per line, not one per listicle.
- **Glossary and definitional pages fold into the service page that owns the service.** The definitional keywords map to
  the shortlist row (a definition paragraph on the page), and any product-shaped keyword among them (`spoke tension
  check service`) gets a provider-shaped row of its own.
- **Verticals live only on the vertical hub**, and their keywords move there with them (`bike servicing for hospital
  staff schemes` leaves the servicing page for the hub's healthcare section). No vertical prompt on a generic page. A
  segment is not an industry: `bike servicing for small fleets` stays on the servicing page. A vertical keyword on a line with
  no hub maps to that page's head row and the page carries an industries line.

**Where keywords sit.**

- **The keyword partition is the spine of the deliverable.** Every keyword on a page maps to exactly one prompt row, or
  to a keyword-only row with the reason it earns no prompt (a geo qualifier, a held vertical). A prompt may carry no
  keyword and say so ("an intent row on the head term": proof, cost, OWN, switching). Never cite a keyword on a row that
  does not own it: a head-to-head row "anchored" to the head keyword is what makes a sheet unreadable. Ship the keyword
  first sheet (Keyword Map: keyword, volume, page, mapped prompt, note) beside the Prompt Map, and run
  `data/verify_tracked_set.py`, which checks the partition (every keyword once, every mapped prompt tracked on that
  page).
- **Category-name variants are one shortlist row per page.** Acronym, full phrase, "services" and provider-noun forms all map
  to that row and the page carries every phrasing in its first hundred words; the tracked string is the biggest short
  keyword's.

**What is tracked only once.**

- **Shared intents are tracked ONCE per topic cluster, on the cluster's core page** (the biggest service page of the
  cluster): displacement, in-house fit, switching, proof, cost, OWN positioning. The other pages in the cluster carry the
  same sections in their copy and are not tracked on them. A page-specific angle stays where it is (a same-day row
  on the puncture-repair page, a motor-diagnostics row on the e-bike page).
- **One persona row in the whole set**, on the page where the role matters most, with the persona and without the output
  instruction. A persona pattern copied onto every page is one question repeated across the cluster.

**Size, spelling and hand-off.**

- **Thin pages get thin lists.** After the cluster pass a three-row service page is normal; the floor is two.
- **Spelling follows the client's market.** "colour" and "color" are different strings to an engine; keyword anchors
  stay verbatim as observed.
- **Save the final set as next run's `--tracked` file.** Once the platform runs it through Google, these exact strings
  come back out of the client's Search Console as impressions.

### Build the facet table before writing a prompt

Group the page's keywords into the facets they actually express, with each facet's share of the page's volume. That
table is the brief: it says what the page is about AND how much of the prompt set each part deserves. Worked example
(invented, round figures), ClientJ's `/repairs/e-bike`:

| facet | keywords | volume | share |
|---|---|---|---|
| core | e-bike repair / e-bike repair shop / electric bike mechanic / e-bike service | 5,000 | 50% |
| motor | e-bike motor repair, hub motor diagnostics | 2,500 | 25% |
| battery | e-bike battery check, e-bike battery replacement | 1,200 | 12% |
| mobile | mobile e-bike repair, e-bike repair at home | 800 | 8% |
| cargo | cargo e-bike servicing | 300 | 3% |
| conversion | conversion kit fitting | 200 | 2% |
| insurance | e-bike damage report for an insurance claim | 0 | |

Write the list against it. Weight the shortlist and persona families towards the facets that carry the volume, and give
each small facet ONE prompt in a capability or fit shape so it is covered without being duplicated. A zero-volume keyword
the client put on the page still earns a prompt: it names a real buyer the keyword tool cannot see, and tracking is how
you find out whether the demand exists in AI.

The facets the table does NOT contain are just as load-bearing (here: selling new e-bikes, battery recycling drop-off,
rider safety courses, bike-fit sessions). Each is another page's
subject, or nobody's.

### Two lists, not one

A prompt that fails containment is usually a GOOD prompt on the WRONG page. Sort the failures before you discard
anything:

- **RE-HOME**: another page in the map holds that subject in its keywords. Move it there and say so; a large share of
  the failures usually re-home to another page in the map, where they pass.
- **EXPLORATION**: no page's keywords hold it. Keep the prompt in a separate list with the reason; do NOT load it. These
  are the most interesting rows in the set, because a real question no page targets is either a section the page needs
  or a page that does not exist.
- **CUT**: only for a near-duplicate of something already kept.

A prompt can pass containment and still fail the page JOB: `is e-bike repair any different from servicing a normal
bike?` carries the page's biggest keyword verbatim and is still wrong on a page built to sell, because an engine answering a bare definition
explains the category and names nobody. Containment is a necessary test, not a sufficient one; the audit's A1 still runs
after it.

### What this does to the counts

SERP clustering produces a superset, and the four gates cut it down: rows go because they are another page's
prompts, a second phrasing of an intent already covered, or a content input, and rows written from the intent ledger
come in. If most of what clustering produced survives, the gates are not being run.

### Observed instrument templates that still earn a tracked row

An instrument string is never demand (its impressions are run counts), but when a template names the client or the
client's exact category on a topic the page covers, it is direct evidence of what the engines are being asked, and the
matrix must carry a row for it. Read every Search Console AI pass for these shapes and decide each one explicitly in the
Prompt Map:

| observed template (shape) | what to track | form, family |
|---|---|---|
| a fixed assessment template naming the client on one topic (`score <client>, a <category> provider, on <topic>`, and garbled variants of it) | ONE plain OWN question on the topic, anchored on the template: `score ClientJ, a bike servicing provider, on e-cargo bike support` becomes `Does ClientJ service e-cargo bikes?`. State in the basis that the figure is an engine run count | OWN, G |
| the same template naming a competitor | no row; it proves the template runs across the category, so cite it on the OWN row and use it to pick the COMP mirror | evidence |
| one price string iterated over many countries (`<category> cost <segment> <country>`) | ONE pricing row in the market's own form (no country), with the country spread in the basis. A separate observed need from the brand's own price question, so it is not folded into the cost row | NB, H |
| a capability string naming a specialised buyer (`<client product> <capability> <specialised buyer>`) | anchor the specialised-segment shortlist row (B) on it, or an OWN capability row (F) if the page has none | NB or OWN, B or F |
| persona preamble plus question (`a retired teacher who wants a weekend hobby asks: which ...`) | keep the QUESTION only, drop the persona and any output instruction, and read it as a candidate anchor like any human question | as the question dictates |
| `<category> industry growth <region>` (a market-size template) | no row; TEMPLATE | evidence |

Two rules from the same reading:

- **A keyword tool may price some tracker noun stacks** (a small volume on a string with no grammar, such as `fleet
  bike service log monthly pdf report depot`). A volume on a noun stack does not make it a keyword (seed-chain
  gate 1, shape). Record it as evidence for the prompt it supports and put it in the corpus, never on the Keyword Map.
- **The tracked row is written in the human shape, not the template's.** The template is the anchor; the prompt is what a
  buyer would type.

---

## Slot dictionary

Slots are not interchangeable. Four of these look alike and are not, and collapsing them is how a page ends up with five
prompts that say the same thing.

| slot | it is | it is not | example fill |
|---|---|---|---|
| `*category*` | the thing being bought, in the buyer's words | the client's product name | bike repair shops |
| `*product*` | a named line or bundle inside the category | the category | a fleet maintenance plan |
| `*capability*` | one feature or axis the product is judged on | a benefit | hub motor diagnostics, wheel truing |
| `*job*` | the outcome the buyer is trying to reach | a feature | keeping a delivery fleet on the road |
| `*audience*` | the buying group by function | the company | facilities teams, daily commuters, trade buyers |
| `*role*` | one named job title, used for persona framing | a department | fleet manager, facilities coordinator |
| `*segment*` | company size or maturity | industry | sole trader, single-depot, multi-depot, national |
| **`*industry*`** | **the buyer's vertical, which changes the requirements** | **size or function** | **couriers, hospitals, universities, hotels, local councils, bike-share** |
| `*standard*` | a named compliance or protocol requirement | a generic "compliance" | a named safety standard, a manufacturer's warranty programme, a battery-transport rule |
| `*need*` | a constraint stated as a want | a feature list | invoicing per depot, servicing overnight |
| `*location*` | geographic market | a language | ireland, northern italy |
| `*competitor*` | a vendor the client is actually compared to | any vendor in the space | CompetitorD |

**Slot relevance is per client.** `*location*` carries real demand for a client with geographic markets and almost none
for a pure-SaaS client; `*industry*` is the opposite on an enterprise client. Check the client's own export before
generating a slot's worth of prompts, and say in the deliverable which slots you judged live.

**`*industry*` is the slot most often missed.** It appears across a meaningful slice of a typical long-tail export and
behaves differently from `*segment*`: it changes the *requirements*, not the budget. `for a university bike
scheme, who services bikes left outside all winter?` and `hospital staff bikes need a signed safety check each year:
which repair firms provide one?` are the same service with different acceptance criteria. Generate one per vertical the client actually sells into, not per vertical that exists.

---

## The branded / non-branded axis

Every template has two forms. On every client measured, the large majority of rows name no vendor at all. Read rows and
impressions together: branded queries are few and heavy, a small share of the surface and a much larger share of the
impressions, because a buyer who names you is already deep. That is a reason to cover them, not a reason to build the
universe out of them. Measure the split on the split export: instruments inflate the branded share at the top of the list
(many of the repeated phrasings name the client), not the shape of the demand underneath.

**Three forms, marked in the `form` column of every table below:**

- **NB**: names no vendor. The default: the demand the client does not yet own.
- **OWN**: names the client. Use where the client has brand demand to defend, and only there. On a client with no brand
  search, an OWN prompt measures nothing.
- **COMP**: names a competitor but not the client. The displacement surface, and the one most often left out.

**The rewrite rule.** Any OWN template becomes NB by replacing the brand with the category and moving the specificity
into a qualifier, not by deleting it:

- OWN `does *brand* offer *capability*?` -> NB `which *category* offer *capability* for *segment*?` (`does ClientV
  offer museum-grade framing?` -> `which art print shops offer museum-grade framing for first-time buyers?`)
- OWN `is *brand* good for *audience*?` -> NB `which *category* suit *audience* who *situation*?` (`is ClientN good for
  nervous beginners?` -> `which pottery studios suit nervous beginners who have never touched clay?`)
- OWN `can *brand* handle *requirement* for *industry*?` -> NB `*industry*: which *category* can handle *requirement*?`
  (`can ClientJ handle e-cargo bikes for a courier fleet?` -> `courier fleets: which repair firms can handle e-cargo
  bikes?`)

Single-query volume collapses in the NB form, because non-branded head demand is spread across thousands of
near-duplicate phrasings: any one of them is small; the *family* is large. Never judge an NB prompt by comparing its
single-query volume to an OWN prompt's.

**Default mix** of the SIMULATED rows across the set, unless the client's own export says otherwise: about 60% NB,
25% OWN, 15% COMP on a client with real brand demand; about 80% NB, 0% OWN, 20% COMP on a client without it. Where the
mix and the OWN budget (one simulated OWN row per topic cluster, `--own-budget`) conflict, the budget wins. Observed
rows never count toward the mix, the budget or any cap.

**Before writing OWN prompts, filter the branded rows to the frame the pages sell in** (service-shaped queries for a
services page set, product-shaped for a product set). Total branded volume says nothing about what OWN prompts will
measure; only the filtered slice does. If what remains reads the brand in another role (invented: ClientN's branded
queries asking about birthday-party bookings while the pages sell courses and memberships), report that as a
positioning finding in the deliverable and keep the OWN rows few, aimed at whether engines name the brand in the role
it sells.

### Which families can be placed on SERP evidence at all

Measure this before promising an evidence-backed placement map: for each matrix-authored prompt, count the non-hub top-10
URLs it shares with the keyword profile of the page it was written for. The typical order, from most to least overlap:

| overlap band | families |
|---|---|
| highest (most prompts share URLs with their page) | K definitional, I analyst / review proof, B persona |
| middle | L engine grounding, C head to head, A discovery / shortlist |
| low (most prompts share none) | E fit, F capability, G outcome / proof, H selection criteria |
| near zero | J migration, D evaluate on axis |

Three things fall out of it:

- **Family B overlaps its page BETTER than family A does.** The engine strips the persona and the output instruction and
  resolves the query to the underlying shortlist, so a 20-word persona prompt and a bare "best X providers" land on much
  the same SERP. Persona framing is therefore free specificity: it makes the prompt AI-native without costing retrieval,
  the opposite of the intuition that a long conversational prompt is a retrieval risk.
- **D and J cannot be placed by SERP overlap and never will be.** An evaluate-on-axis prompt names a vendor, so its SERP
  returns that vendor's pages; a migration prompt resolves to switching guides. Both are legitimate and both need a
  stated placement basis rather than a pretended evidence trail.
- **The families with the LOWEST overlap are the ones the page most needs to answer**: proof, criteria, migration,
  capability. Low overlap there is not a bad prompt; it is a page that owns the subject and not yet the surface, and the
  output is a section requirement.

---

## A. Discovery and shortlist
**Page types: Listicle, Service Page. Stage: Decision. Population: assistant, 12 to 15 words.** The buyer wants a name.
Large single phrasings in this family are instruments (one long string served many times a day for months) or bare
noun-phrase templates: shapes to learn from, volumes to ignore. Real shortlist demand in an assistant is thousands of
near-duplicate phrasings, none large.

| form | template | example (invented) |
|---|---|---|
| NB | `*category* near *place* for *audience*` | pottery classes near the canal for complete beginners |
| NB | `which *category* are worth it for *job*?` | which bike servicing plans are worth it for daily commuting? |
| NB | `who does *product* for *audience* in *location*?` | who does mobile e-bike repair for commuters in cork? |
| NB | `good *category* for *industry*: any names?` | good fleet bike servicing firms for hospitals: any names? |
| NB | `*industry* *job*: which *category* handle it?` | university bike schemes, end-of-term fleet checks: which repair firms handle it? |
| NB | `*category* that focus on *industry*` | bike repair firms that focus on courier fleets |
| NB | `does any *category* have a *industry* *capability*?` | does any framing shop have a wedding-only bouquet preservation service? |
| NB | `budget *category* around *location* for *segment*` | budget fleet bike servicing around dublin for single-depot firms |
| NB | `*category* under *price* in *year*` | botanical art prints under 50 dollars in 2027 |
| NB | `free or low-cost *category* for *audience*` | free or low-cost wheel-throwing tasters for teenagers |
| NB | `where do *audience* go for *category*?` | where do home potters go to get their work fired? |
| NB | `*category* that *user type* rate highest` | e-bike repair shops that delivery riders rate highest |
| NB | `*category* that suit *situation*` | botanical prints that suit renters who cannot drill into walls |
| NB | `top-rated *category* using *standard*` | top-rated art print shops using archival pigment inks |

## B. Persona and forced comparison
**Page types: Listicle, Service Page. Stage: Decision. Population: assistant, 15 to 25 words.** The persona is the
non-branded carrier: the prompt is specific without naming anyone, and a buyer who says who they are before asking is
real behaviour. But the high-volume persona rows in an export are tracking tools' prompts, and the **output-format
instruction** at the end is the tell of the tool, not of the buyer. Write the persona, drop the instruction, read the
volumes as run counts.

| form | template | example (invented) |
|---|---|---|
| NB | `*role* here. *problem*. which *category* would suit us?` | fleet manager here. our cargo bikes need their brakes checked every week. which repair firms would suit us? |
| NB | `i run *segment* *industry* *operation*; who should i call for *job*?` | i run a small hotel with ten guest bikes; who should i call for a spring safety check? |
| NB | `*situation*, and i want *category* able to *job*. any suggestions?` | our first anniversary is coming up, and i want a print shop able to turn the wedding bouquet into framed art. any suggestions? |
| NB | **situation first, then the ask:** `*situation*. we need a *provider* who can *job*.` | bikes keep coming back to our hire stand with slow punctures. we need a mechanic team who can check every bike between hires. |
| NB | **delegated search:** `*situation*. any idea who could *job* for us?` | three staff e-bikes arrive next month and nobody here can maintain them. any idea who could keep them running for us? |
| COMP | `*role* buying for *industry*: does *competitor A* or *competitor B* have more experience there?` | facilities coordinator buying for a hospital: does CompetitorA or CompetitorB have more experience with staff bike schemes? |
| OWN | `for *segment*, would you pick *brand* or *competitor*?` | for a beginner who only has weekends free, would you pick ClientN or CompetitorB? |
| OWN | `i need *capability*. is *brand* or *competitor* stronger on that?` | i need conservation framing with uv-filtering glass. is ClientV or CompetitorD stronger on that? |
| OWN | `trying to *job*: *brand* or *competitor*, which fits better?` | trying to keep twelve courier bikes running: ClientJ or CompetitorC, which fits better? |

## C. Head to head
**Page types: Listicle, Service Page. Stage: Decision. Population: assistant.** On split exports,
vs/alternative-shaped rows and rows naming a competitor are a modest share of the human rows; unsplit exports (and the
high-impression slice in particular, which is where instruments live) make comparison look several times bigger than it
is. This is the one family where a branded form is the default, because a comparison needs two names.

| form | template | example (invented) |
|---|---|---|
| OWN | `*brand* or *competitor* for *job*?` | ClientN or CompetitorA for a six-week wheel course? |
| COMP | `for *job*, how do *competitor A* and *competitor B* differ?` | for bouquet preservation, how do CompetitorB and CompetitorE differ? |
| OWN | `is *brand* or *competitor* better at *job*?` | is ClientJ or CompetitorC better at servicing a mixed fleet of e-bikes and cargo bikes? |
| NB | `*tier A* or *tier B* *category*: which makes sense for *situation*?` | open-edition or limited-edition botanical prints: which makes sense for a first purchase? |
| COMP | `*competitor* alternatives for *audience*` | CompetitorD alternatives for home potters who only need firing |
| OWN | `leaving *competitor*: is *brand* a good next choice?` | leaving CompetitorE: is ClientV a good next choice for framed prints? |
| OWN | `*brand* compared with *competitor A* and *competitor B* on *job*` | ClientJ compared with CompetitorA and CompetitorF on overnight depot servicing |
| OWN | `does *brand* fit *existing setup*, or would another *category* fit better?` | does ClientV's framing fit an existing picture-rail system, or would another shop fit better? |
| OWN | **value challenge:** `*competitor* is cheaper per *pricing basis*; what does *brand* add for the extra cost?` | CompetitorC is cheaper per firing; what does ClientN add for the extra cost? |

Labels follow `intent-format-kpi.md` section 3: rows naming two or more options are Contrast; the alternatives row
is Shortlist; the NB tier row names no provider and is Fit, Citation.

The three-name form (three competitors set against each other, `*competitor A*, *competitor B* or *competitor C* for
*segment*?`) shows up in exports and is cut wherever it appears (G4): it has no slot for the client.

## D. Evaluate on a capability axis (brief input, never tracked)
**Page types: Service Page, Product Page. Population: tool template, 8 to 12 words.** A tracking tool probing one
capability at a time; the template belongs to a tool, not a buyer. What it tells you is which AXES the category's dashboards score a vendor on. Take the client's
capability list, write one axis string per capability the page can honestly claim, and make sure the page has a heading
or passage for each: a brand is only as visible as its weakest axis, and a single "what is X" passage cannot surface
that.

This family is inherently named-entity: the shape requires a subject. The COMP form is the displacement surface, the same
axes scored against the competitor the buyer would otherwise be handed; the NB criteria form lives in family H. Neither
form is loaded onto the platform.

| form | template | example (invented) |
|---|---|---|
| OWN | `score *brand*, a *category* provider, on *capability*` | score ClientJ, a bike servicing provider, on hydraulic brake bleeding |
| COMP | `score *competitor*, a *category* provider, on *capability*` | score CompetitorB, a pottery studio, on kiln availability |
| COMP | `score *person* on *capability*` | score PersonA on botanical watercolour technique |
| OWN | `score *brand*, a *category* provider, on *capability* for *industry*` | score ClientJ, a bike servicing provider, on fleet care for universities |
| OWN | `score *brand*, a *category* provider, on *content cluster*` | score ClientV, an art print shop, on plastic-free packaging |

Run the split and name the noise pattern before counting this family: a figure read off the unsplit export can be
wrong in both directions (total size and how often the client is named).

## E. Fit and suitability
**Page types: Service Page, Product Page. Stage: Consideration. Population: assistant.** The buyer has a constraint and
wants to know if you clear it.

| form | template | example (invented) |
|---|---|---|
| NB | `is there a *category* set up for *segment*?` | is there a bike servicing firm set up for national fleets? |
| NB | `do any *category* cater to *audience*?` | do any pottery studios cater to people with limited hand strength? |
| NB | `*industry* and *industry*: what kind of *category* meets *requirement*?` | hotels and universities: what kind of bike servicing meets a yearly signed safety check? |
| NB | `which *category* can document *capability* to *standard*?` | which framing shops can document conservation framing to a museum standard? |
| NB | `*need* plus *need 2*: which *product* covers both?` | invoicing per depot plus servicing overnight: which fleet maintenance plan covers both? |
| NB | `*segment* with *constraint*: can any *category* *job*?` | a gift shop opening in ten days: can any print studio frame forty prints that fast? |
| NB | `need *capability*, *capability* and *capability* for *team size*: who offers all three?` | need wheel time, glaze access and firing for two people: which studio memberships offer all three? |
| OWN | `does *brand* take on *industry* with *requirement*?` | does ClientJ take on hospital fleets with a yearly signed safety log? |
| OWN | `who is *brand* really for, *use case A* or *use case B*?` | who is ClientN really for, hobbyists or potters training to sell their work? |
| OWN | `does *brand* only do *narrow offer*, or *broad offer* too?` | does ClientV only sell prints, or frame and hang them too? |
| OWN | `would *brand* be the right *category* for *job*?` | would ClientJ be the right repair firm for a bike-share scheme's winter overhaul? |

## F. Capability and can-it
**Page types: Service Page, Product Page. Stage: Consideration. Population: assistant.** Treat large volumes in
this family as run counts until the split says otherwise; human capability questions are small and specific.

| form | template | example (invented) |
|---|---|---|
| NB | `is there an app that *job* and *capability*?` | is there an app that logs every repair on my bike and reminds me when the chain is due? |
| NB | `how can i keep track of *metric* over time?` | how can i keep track of my e-bike battery's health over time? |
| NB | `any software linking *data type* to *workflow*?` | any software linking rider damage reports to a repair booking calendar? |
| NB | `*job* from *surface*: what helps?` | spotting worn brake pads from a phone photo: what helps? |
| NB | `*scale constraint*: which *category* can manage it?` | four hundred bikes across five cities: which repair firms can manage it? |
| NB | `who offers *capability* for *job A*, *job B* and *job C*?` | who offers custom wheel builds for road, gravel and cargo bikes? |
| NB | `does any *category* break *metric* down by *dimension A* and *dimension B*?` | does any fleet servicing firm break repair costs down by bike and by depot? |
| NB | `tracking *metric* across *surface*` | tracking tyre wear across a delivery fleet |
| OWN | `will *brand* *job*?` | will ClientN fire pieces made at another studio? |
| OWN | `could *brand* take the place of *alternative*?` | could ClientJ take the place of our in-house mechanic and our parts supplier? |
| OWN | `*standard*, *standard*, *standard*: does *product* include them for *job*?` | brake checks, tyre swaps, battery tests: does ClientJ's fleet plan include them for cargo bikes? |
| OWN | `with *brand*, can i see *capability* across *scope*?` | with ClientJ, can i see each bike's service status across all our depots? |
| OWN | `is *brand* usable by *role* for *job A* and *job B*?` | is ClientV usable by interior designers for ordering and tracking framed sets? |
| OWN | `*brand*: how does it *job* to *place A* and *place B*?` | ClientV: how does it ship framed prints to both ireland and france? |

## G. Outcome, proof and differentiation
**Page types: Research Post, Service Page. Stage: Consideration. Population: assistant.**

| form | template | example (invented) |
|---|---|---|
| NB | `what do *audience* track to judge *job* on *dimension*, *dimension* and *dimension*?` | what do fleet managers track to judge servicing on downtime, cost and rider complaints? |
| NB | `is it possible to *job* without *missing input*?` | is it possible to get better at the wheel without private lessons? |
| NB | `how do *category* spot *problem* early?` | how do bike mechanics spot a failing e-bike motor early? |
| NB | `*category* with documented results on *outcome*` | fleet servicing firms with documented results on fewer breakdowns |
| NB | `examples where *approach* paid off for *audience*` | examples where planned fleet maintenance paid off for couriers |
| NB | `is *approach* worth the money, and how would i tell?` | is a pottery studio membership worth the money, and how would i tell? |
| NB | `what should i measure to see whether *outcome*?` | what should i measure to see whether regular servicing is cutting downtime? |
| OWN | `what does *brand* do for *role* who *situation*?` | what does ClientJ do for fleet managers who are short of mechanics? |
| OWN | `compared with other *category*, how does *brand* *job*?` | compared with other pottery studios, how does ClientN help beginners progress? |
| OWN | `*brand* or *competitor*: which has the edge on *job*?` | ClientV or CompetitorD: which has the edge on large-format prints? |
| OWN | `how is *brand* different from a *category*?` | how is ClientJ different from a regular bike shop? |
| OWN | `why choose *brand* over *alternative*?` | why choose ClientN over an evening class at a community centre? |
| OWN | `who uses *brand* instead of *alternative*?` | who uses ClientJ instead of the manufacturer's own repair network? |
| OWN | `is *approach* with *brand* worth it for *segment*?` | is the ClientJ yearly fleet plan worth it for a ten-bike courier firm? |
| OWN | `examples of *brand* work for *segment*` | examples of ClientV framing for boutique hotels |
| OWN | `what do people gain from *brand* for *job*?` | what do people gain from ClientV for keeping a wedding bouquet? |

## H. Selection criteria
**Page types: Guide. Stage: Consideration. Population: assistant.** This is where a DIY-shaped question legitimately
lives, and it is non-branded by nature. It is also the NB outlet for family D's capability axes: what family D asks about
one vendor, family H asks about the category.

| form | template | example (invented) |
|---|---|---|
| NB | `what separates a good *category* from a bad one?` | what separates a good bike mechanic from a bad one? |
| NB | `*category*: how do i compare them side by side?` | pottery studios: how do i compare them side by side? |
| NB | `before i pick a *category*, how can i check it *capability*?` | before i pick a framing shop, how can i check it uses acid-free mounts? |
| NB | `picking a *category* for *audience*: what matters most?` | picking a pottery studio for a child's birthday party: what matters most? |
| NB | `which questions should a *segment* ask a *category*?` | which questions should a national fleet ask a bike servicing firm? |
| NB | `warning signs when choosing a *category*` | warning signs when choosing a bike repair shop |
| NB | `how do i vet a *provider* for *service* in *year*?` | how do i vet a framer for a gallery wall in 2027? |
| NB | `what's the right way to *job*?` | what's the right way to store a pressed bouquet before it is framed? |
| NB | `my *industry* business needs a *category*; where do i start?` | my holiday-let business needs a bike servicing contract; where do i start? |
| OWN | `who can *job* with *brand* for a *segment*?` | who can hang a ClientV gallery wall for a small office? (services demand on the client's own product) |

## I. Analyst and third-party proof
**Page types: Research Post, Listicle. Stage: Decision. Population: assistant, short.** Strong on enterprise clients, weak
on self-serve. Check the client's category has an analyst surface before generating these, and check properly: the
review-surface shape (G2, Capterra, Gartner Peer Insights, an analyst ranking such as a Gartner Magic Quadrant or a
Forrester Wave) can shrink sharply after the split. Real review-surface asking is COMP by nature and not a cheap volume gain, and appending a review-site name to a comparison to chase those figures builds an instrument's prompt, not a
buyer's. Review-sentiment OWN rows are answered from review sites: the brief points at the review surfaces, because the
page cannot carry them alone.

| form | template | example (invented) |
|---|---|---|
| NB | `*ranking or award* *category* *year* winners` | national cycling trade awards bike repair 2027 winners |
| NB | `which *category* made *ranking*?` | which pottery studios made the city magazine's best-of list this year? |
| NB | `*category* with the most published stories of *outcome*` | fleet servicing firms with the most published stories of fewer breakdowns |
| OWN | `how do reviews rate *brand*'s *capability*?` | how do reviews rate ClientV's print colour accuracy? |
| OWN | `common complaints about *brand* *topic*` | common complaints about ClientJ mobile van waiting times |
| OWN | `what do *audience* dislike about *brand*?` | what do members dislike about ClientN's open-studio hours? |
| COMP | `*competitor A* vs *competitor B* vs *competitor C* *review surface* *capability*` | CompetitorF vs CompetitorC vs CompetitorA google reviews turnaround |
| COMP | `*competitor A* *competitor B* *review surface* comparison` | CompetitorD CompetitorE google reviews comparison |
| COMP | `*competitor* *evaluation axis* *review surface*` | CompetitorB kiln waiting time reviews |
| NB | `top *category* *year* reviews *competitor* *competitor* *competitor*` | top bike servicing firms 2027 reviews CompetitorB CompetitorC CompetitorE |

The last four rows are instrument shapes shown so you recognise them; none is a tracked row.

## J. Migration and consolidation
**Page types: Service Page. Stage: Decision. Population: assistant.** The highest-intent family in the set and the one
most often missing from a prompt universe. The NB forms describe the migration rather than naming a destination vendor.

| form | template | example (invented) |
|---|---|---|
| NB | `we've outgrown *old setup*; who can move us onto *target*?` | we've outgrown fixing bikes in our own yard; who can move us onto a proper servicing contract? |
| NB | `how much work does it take to move *workload* from one *category* to another?` | how much work does it take to move forty bikes from one servicing firm to another? |
| NB | `*change* without *disruption*: what kind of provider manages that?` | changing fleet servicing firms without bikes standing idle: what kind of provider manages that? |
| NB | `when switching *category*, who carries over *asset*?` | when switching bike servicing firms, who carries over each bike's repair history? |
| NB | `*situation with incumbent*; we need a *category* that keeps *requirement*. who fits?` | our contract with CompetitorA ends in may and we need a new servicing firm that keeps every bike's service record. who fits? |
| NB | `moving from *old way* to *new way*: how do people do it?` | moving from paper job cards to app-booked fleet servicing: how do people do it? |
| OWN | `what does moving from *competitor* to *brand* involve?` | what does moving from CompetitorA to ClientJ involve for a courier fleet? |
| OWN | `does switching from *competitor* to *brand* pay off for *segment*?` | does switching from CompetitorC to ClientJ pay off for a twenty-bike fleet? |
| OWN | `should we merge our *contracts* under *brand*?` | should we merge our repair and parts contracts under ClientJ? |

## K. Definitional
**Page types: Guide, Glossary. Stage: Awareness. Population: keyword, short.** Real but small, and **never on a page whose
job is to sell**: an engine answering these explains the topic and names nobody. On a guide or glossary these are
Citation rows.

| form | template | example (invented) |
|---|---|---|
| NB | `*category*: what does it mean?` | giclee printing: what does it mean? |
| NB | `*A* or *B*: what's the difference?` | bisque firing or glaze firing: what's the difference? |
| NB | `*A*, *B* and *C*: how are they different?` | stoneware, earthenware and porcelain: how are they different? |
| NB | `how does *category* work?` | how does wheel truing work? |

## L. Engine grounding queries (brief input, never tracked)
**Page types: all. Stage: all. Population: ENGINE.** Sources: the Bing AI performance report (queries the engine wrote,
with citation counts) and the assistant's own "searching for" strings captured while tracked prompts run.

| | Bing AI grounding | assistant fan-out |
|---|---|---|
| typical length | about 5 to 8 words | about 8 to 12 words |
| question form | almost never | essentially never |
| carries a year | rarely | on a noticeable minority |
| strings per prompt per run | n/a | a dozen or more |
| anchors | category and capability nouns | authority sources (official documentation, platform policies) and vendor names |

These are not written by a person. When an assistant needs to ground an answer it writes its own search query, and that
query looks nothing like what the person asked: a keyword-dense noun phrase with no verb, no question mark, no persona and
no output instruction. This is the string that actually retrieves the page, so it is the string the page has to match.
The engine is not being lazy: it strips the person's question down to retrieval terms, dropping the persona, the
politeness and the framing and keeping the nouns. A page written only for the conversational shape can lose the
retrieval that feeds it.

This is the family the fan-out block is built from (observation order: assistant UI first, the Bing report second,
compression third). Where no observation exists, take the family A to K prompts already written for the page, compress
each to its noun phrase, and keep the ones that read like a search a machine would run.

| form | template | example (invented) |
|---|---|---|
| NB | `*capability* *category* *audience*` | depot visits mobile bike repair couriers |
| NB | `*metric* benchmarks *content type*` | downtime per bike benchmarks fleet maintenance |
| NB | `*A* vs *B* *property*` | stoneware vs porcelain chip resistance |
| NB | `*schema type* schema *content type*` | Product schema art print listings |
| NB | `*category* booking *integration* sync` | bike repair booking calendar sync |
| NB | `*segment* *category* price per *unit*` | small fleet bike servicing price per bike |
| NB | `*industry* *standard* rules *category*` | courier e-bike battery transport rules servicing |
| NB | `*problem* *setting* reasons` | glaze crawling home kiln reasons |
| NB | `*category* software must-have features` | bike fleet tracking software must-have features |
| NB | `*category* sites compared` | pottery class booking sites compared |
| NB | `picking *category* for *job*` | picking framing shop large format botanical prints |
| NB | `*year* *category* membership prices` | 2027 pottery studio membership prices |
| NB | `*audience* *process* checklist` | fleet manager spring safety check checklist |
| NB | `home *capability* tools` | home wheel truing tools |
| NB | `*capability* tool for *category*` | chain wear gauge for e-bikes |
| OWN | `*brand* *capability* *audience*` | ClientJ overnight depot servicing courier fleets |
| OWN | `*brand* *product* *benefit*` | ClientN membership unlimited kiln access |
| OWN | `*brand* compared other *category*` | ClientV compared other art print shops |
| COMP | `*competitor* *capability* *issue*` | CompetitorB firing waiting times |
| COMP | `*competitor* *pricing basis* *segment*` | CompetitorC pay per repair small fleets |

**Read the intent labels the engine assigns** where the report gives them, by citation share, and use them to check
coverage against the client's own report rather than against an assumed shape:

- **Where research-labelled or informational grounding dominates the citations**, the engine is grounding in
  explanatory material and naming vendors from it. A service page with no research-shaped surface behind it is then
  cited by nothing, which argues for a guide and research-post tier behind the money pages. A page that draws only
  commercial grounding will not be cited in a research answer.
- **Check citations per query by label**: if comparison queries carry a disproportionate share of citations for their
  count, comparison content earns its place.
- **Check provider share by prompt stage in captured assistant fan-outs.** Count how many fan-outs per prompt name a
  provider at each stage. Where Awareness prompts send the engine mostly to definitions and authority sources while
  Consideration and Decision prompts send it to providers, that supports G4 cutting Awareness rows on a selling page.
- **Check non-English grounding queries separately**: compare their share of queries with their share of citations.
  If the client sells into non-English markets and those queries carry more than their share, generate the family L
  compressions in those languages too.

---

## The structural features to carry into every simulated prompt

1. **Length by population.** Families A to K: 12 to 15 words (human long-tail rows average about 11 to 13 words; PAA
   runs about 6 and is the wrong yardstick). Family L: 5 to 8 words for Bing-style grounding, 8 to 12 for assistant
   fan-outs.
2. **Question form by population.** Human rows are question-opener by construction (a large minority of all 6+ word
   queries once instruments are out), and a further sizeable slice of the demand is noun-phrase shaped; engine grounding
   strings are almost never questions. Do not put a question mark on a family L string.
3. **A qualifier tail on roughly 40% of the A to K prompts**: `for *audience*`, `near *location*`, `in *industry*`, `with
   *capability*`, `under *budget*`. It is what makes a prompt answerable by one provider rather than by a
   category explainer. Compound prompts (two needs joined by "and", "or" or a comma) are normal on about a quarter of
   human rows.
4. **Named specifics, not generic nouns**: named standards, protocols, file formats, platforms and engines (ChatGPT,
   Perplexity, Gemini). Specificity is not noise; it is the thing that makes the answer nameable.
5. **Role, segment or industry framing**: a fleet manager at a courier firm, facilities teams, hospitals and
   universities, single-depot, national.
6. **No output-format instruction, no persona preamble template, no location injection** unless it is an instrument
   decision applied to the whole set and stated as one. A ranking instruction, an instruction addressed to the
   model, or a clause stating the asker's location or market is the signature of a tracking tool in the data, not of a
   buyer.
7. **Default to NB.** Reach for OWN only where the client has brand demand to defend, and always pair the OWN set with
   its COMP mirror.

## What the matrix does not license

Inventing a subject the client has no demand for, inventing a competitor nobody compares them to, inventing an industry
the client does not sell into, or filling a page to hit a count. A page with genuinely no demand behind it still gets no
prompt and a written reason. The matrix makes a thin page's prompts BETTER; it does not make a thin page worth keeping.
