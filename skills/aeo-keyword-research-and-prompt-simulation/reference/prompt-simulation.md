# Simulating prompts when observed data runs out

**Grounding is a source, not a gate.** If grounding is treated as the only legitimate path, pages where the question
tools return nothing ship with one prompt or none: a high-volume shortlist page carrying a single unrelated prompt is
worse than a labelled simulated prompt, and a client rejects it on sight. **Where observed data is thin, simulate, and
label it.**

This file is what to simulate TOWARDS: what real AI-era long tail looks like, why People Also Ask shape is the wrong
target, why non-branded is the default, and the simulation procedure. The templates themselves are in
`prompt-matrix.md`. Examples are invented, mostly for **ClientJ** (a bicycle-repair chain with city workshops, mobile
vans and fleet maintenance contracts). Shares below are typical
directions to check against the client's own split export, not fixed facts.

## The most important correction: PAA shape is the wrong target

The six tells in `question-data-harvest.md` are calibrated on People Also Ask, which is short by construction. Applied
as a length rule to an AI-era prompt set they strip out exactly the shape that earns impressions.

There are FOUR populations: what a person types into Google, what a person says to an assistant, what a **tracking tool**
submits on someone's behalf, and what the **engine** writes for itself when it looks for something to cite. Four strings,
four shapes, and the third is the trap: instrument rows (other trackers' persona prompts, fixed scoring templates run
over companies and capabilities, the client's own tracked prompts run daily) can carry a large share of a long-tail export's impressions and
most of its top phrasings. `prompt-matrix.md` carries the population table; `data/longtail_split.py` does the split.
Run it before any figure is reused.

| | People Also Ask / question-tool corpus | AI-era long tail (person -> assistant) | what the ENGINE writes to ground its answer |
|---|---|---|---|
| where you see it | AlsoAsked, PAA | Search Console 6+ word export, human rows | Bing Webmaster Tools AI performance report; the assistant UI while a prompt runs |
| typical length | about 6 words | about 10 to 14 words | about 5 to 8 words |
| compound (2+ connectives) | rare | common | rare |
| question opener | most rows | a minority of rows, a larger share of impressions | very rare |
| names a provider or tool noun | low | a large part of rows | a common share |

The engine strips the person's question to retrieval terms: it drops the persona, the framing and the question mark and
keeps the nouns. Calibrate these shares against the client's own observed data (its split export and captured
fan-outs) rather than reusing them as targets. A page can win the conversational shape and lose the retrieval that feeds it. Cover both, and never
carry one population's length rule onto another.

A prompt set averaging PAA length is a PAA set, not an AEO set. **Screen for realism, not brevity.** Keep the six tells
for spotting invented phrasing; never use length or a second clause as a disqualifier on its own.

## What the real long tail looks like

- **Openers.** A large share of demand has no question opener at all: a bare noun phrase (`mobile e-bike repair van
  weekend call out`). Then what, how, which, best. Question form is worth over-weighting, and a set that is
  100% question form is still wrong.
- **Structural features on human rows** (check them on the client's split export):
  - a `for <audience or use case>` tail, a common tail on human rows (calibrate the mix against the client's own
    observed data): `for commuters`, `for kids' bikes`, `for a delivery fleet`;
  - `in <market or surface>` on a meaningful share;
  - a competitor named on a minority;
  - vs / alternative / or on a smaller share than an unsplit export suggests;
  - `with <capability>` on a few;
  - a year stamp on very few (year stamps in an unsplit export are usually trackers stamping their templates);
  - persona preamble and output instruction on essentially none: those live in the instrument rows.
- **Clicks are near zero.** The query was answered without a visit, which is why impressions are the first-class metric
  and why a click-weighted keep/drop cut throws the category away. On the branded long tail the brand often sits at the
  top positions with no clicks at all: it is winning the answer and never seeing the visit, which is the whole argument
  for tracking prompts rather than rankings.
- **Long is not a quirk of a single client.** Exports from different categories show the same shape: long human queries and a
  steady share of impressions on queries with no question opener. Structural features measured on an unsplit export (or
  on its high-impression slice, where the instruments live) overstate comparisons, competitor names and year stamps;
  measure on the human rows.

## The second correction: real demand is overwhelmingly non-branded

Measured on split exports, most queries name no vendor at all; branded queries are few and heavy (a small share of rows
and a larger share of impressions, because a buyer who names you is already deep). That is a reason to cover them, not
to build the universe out of them.

- **NB (names nobody)** is the default form: the demand the client does not yet own.
- **OWN (names the client)** only where there is brand demand to defend. On a client with no brand search an OWN prompt
  measures nothing.
- **COMP (names a competitor, not the client)** is the displacement surface and the form most often left out. Write it
  from the client's real competitor set (the pairs buyers compare), never from a fixed scoring template run over
  companies, which is a tool's instrument.

The rewrite is not deletion: replace the brand with the category and move the specificity into a qualifier. `how long
does CompetitorB take to fix an e-bike motor?` becomes `which bike repair shops fix e-bike motors within a day?`. Expect single-query volume to collapse: non-branded head demand is spread over many near-duplicate
phrasings, so the family is large even when every row is small. Never judge an NB prompt against an OWN prompt's volume.

## Templates to simulate into (invented examples)

Fill the client's own verified terms. Shapes like these appear at the top of long-tail exports; when an example's volume
comes from an instrument, the shape is still worth learning (it was designed by people who write AI-native prompts for a
living) and the volume is a run count, not demand.

| shape | example |
|---|---|
| `which <tool> connects <data> to <job>?` | which apps connect a bike's ride mileage to service reminders? |
| `i need <outcome> before <event>, which <providers> can <deliver> in <time>?` | i need my road bike race-ready before a sportive, which repair shops can turn it around in two days? |
| `<category> worth it for <use case> or overkill?` | annual bike service plan worth it for a daily commuter or overkill? |
| `<job> and <job> in one place: who does both?` | wheel truing and e-bike motor diagnostics in one place: who does both near the station? |
| `what replaces <alternative> if <constraint>?` | what replaces a local bike shop if you live too far away to drop the bike off? |
| `is <brand> any good at <job>?` | is CompetitorC any good at rebuilding suspension forks? |
| `what should i look for in a <provider> when <situation>?` | what should i look for in a bike mechanic when the frame is carbon? |
| `<brand A> or <brand B>, which handles <job> better?` | CompetitorA or CompetitorB, which handles hydraulic brake bleeds better? |
| `i <situation>; which <category> <capability>?` | i look after forty delivery e-bikes; which repair services come out monthly to service them on site? |
| bare noun phrase | e-bike servicing with motor firmware updates for cargo bikes |

**Role framing is real** as a shape (a buyer saying who they are before asking); the output instruction a tracker appends
(a demand to order the answer as a ranked list) is not, so write the persona and never the instruction. A bare noun phrase with no question
mark is a large slice of real demand.

### Shapes enterprise exports add

Exports from enterprise B2B clients typically run even longer and add three features worth carrying into any simulation:
- **role or segment framing** (courier firms, bike-share operators, campus estates teams);
- **a constraint tail** (billed separately for each depot, with repairs done overnight on site, covering e-cargo models);
- **named standards and protocols** (a manufacturer's warranty certification, a battery-handling rule, a fleet
  telematics format): specificity is what makes a prompt answerable by one vendor rather than a category explainer.

Templates of that kind (invented examples, for ClientJ's fleet maintenance line):

| shape | example |
|---|---|
| `for a <segment> with <scale>, who offers <service> <constraint>?` | for a courier firm with eighty e-cargo bikes, who offers servicing billed separately for each depot? |
| `<service> providers certified for <standard>` | fleet bike maintenance providers certified for manufacturer warranty work |
| `which <providers> do <job> so <outcome>?` | which fleet repair services fix bikes overnight on site so they are back out by morning? |
| `does <brand> handle <job A> as well as <job B> for <segment>?` | does CompetitorD handle battery diagnostics as well as routine brake work for bike-share fleets? |
| `<brand A> or <brand B> when you run <scale> across <sites>?` | CompetitorC or CompetitorD when you run several hundred share bikes across three cities? |
| `who has the strongest reviews among <category> for <segment>?` | who has the strongest reviews among bike fleet maintenance firms for university campuses? |
| `which <providers> meet <standard> for <job>?` | which repair contractors meet the battery-handling rules for storing e-bike packs? |

**Spot the instrument rows.** An exact phrasing repeated at a near-uniform count across the window, often naming the
client, is a tracker reflected back, not a buyer. A placeholder or test token left in a template slot gives one away too.
The shape survives; the count does not.

### The evaluate-on-axis family belongs in the brief, not the tracked set

A large block of some exports is one template a tool runs, not a person: a fixed sentence that scores one named
company on one capability, one row per capability axis at a near-uniform count per axis, across the client and its competitors. That
is a tracking tool scoring vendors one capability at a time, often the client's own instrument reflected back.
- **Cover the axes in the BRIEF, never in the tracked set.** Write one axis string per capability the page can honestly
  claim and make sure the page has a heading or passage for each. The volume is a run count and the family fails G1.
- **A brand is only as visible as its weakest axis.** One "what is X" passage cannot surface this; per-axis coverage
  shows where the brand is absent in the category's dashboards.

## How to simulate, in order

0. **Split the client's long-tail export first** (`data/longtail_split.py`, with their tracked-prompt export if one
   exists) so every shape and figure comes from human rows. Instruments are shapes to learn from and volumes to ignore.
1. **Start from the page's own verified keywords.** The keyword supplies the subject; this file supplies the shape. Then
   grep the client's human Search Console rows for the page's subject before writing anything: on a services category the
   question tools return definitional and cost shapes and little else, and the client's own human rows are where
   provider-shaped phrasings live. Strip a tool's injections (a trailing year, a clause stating the asker's location) and keep
   the shape verbatim; label the row observed.
2. **Pick the shape from the page's job.** A service page or shortlist takes a provider-seeking template; a guide or
   glossary takes a definitional one. Never put a DIY how-to on a page whose job is to sell: the engine answers it
   without naming anyone.
3. **Add one real qualifier tail** from the client's actual ICP (audience, market, industry, integration, competitor).
   It is what makes a prompt answerable by a specific provider. Check the slot dictionary before filling: `*industry*`
   changes the requirements, `*segment*` changes the budget, and they are different qualifiers.
4. **Pick the form deliberately.** Default NB. Add OWN only where the client has brand demand to defend, and whenever you
   write an OWN prompt, write its COMP mirror (the competitor the buyer would otherwise be handed). Record the NB / OWN /
   COMP split.
5. **Length follows the population, not one house number.** Families A to K: the 10 to 14 word band human long-tail rows
   show; do not pad to reach it and do not trim below it to look like PAA. Family L: 5 to 8 words, no question mark.
6. **Write the fan-out block for every tracked row** (`prompt-matrix.md`): 2 to 5 strings the engine will run, observed
   first (run the prompt in an assistant with web search and in an AI search mode and record the searches it shows; then
   the Bing AI performance report), compressed from the prompt second (drop persona, verb and question mark; keep the
   nouns and the qualifier), one per claimed capability axis third. Label each (`O-ui`, `O-bing`, `O-as`, `O-gsc`,
   `S-compress`, `S-axis`; an observed string over 10 words that you trim becomes `S-compress`) and name the heading or
   passage the page must carry. The brief is built from these. Engines ground mostly in research-shaped material and
   very little in commercial-shaped material, so a service page with no research-shaped surface behind it is grounded by
   nothing.
7. **Label it.** A simulated prompt says so, names its family, says which trees were checked and came up empty, and is
   counted separately from observed rows.
8. **Audit it exactly like a grounded one.** `data/prompt_audit.py` does not care where a prompt came from; a harvested
   question on the wrong page fails the same checks as an invented one.

## What simulation does not license

Inventing a subject the client has no demand for, a competitor comparison nobody asks, or filling a page to hit a count.
A page with genuinely no demand gets no prompt and a written reason: the fix for a thin page is the fold, not a
simulated prompt.
