# Harvesting real question data (run BEFORE any prompt is written)

"Ground the phrasing, never invent" is useless as a sentence: with no named source, no hierarchy and no measurable test,
it still produces a prompt set nobody would type. This file is the source, the hierarchy and the test.

Examples are invented, for **ClientJ** (a bicycle-repair chain with city workshops, mobile vans and fleet maintenance
contracts) and **ClientV** (an online botanical-print shop: prints, framing, pressed-flower keepsakes).

## The rule

**Hand-written phrasing is a last resort.** A prompt is written by hand only where no observed phrasing exists in the
sources below, and every hand-written row states what was checked and came up empty. Learning the *shape* from the
tools and then writing your own strings in that shape is the failure this rule stops: it reads as grounded, passes a
shape test, and is not grounded.

When several fixes raise a set's grounded share (forcing the last-resort rule, going heavy on the deepest question
tool, the tier-1b pass over the client's keyword set), report each step's effect separately; crediting one fix with all
of them misleads the next run.

## The source hierarchy

**Tier 1, observed demand: someone typed it.** The only thing that counts as grounding. (Grounding tiers are 1, 1b and
2; the Scope Map's T1 and T2 are service tiers, a different thing. Tier 1b is the client's own signed-off keyword set, a
keyword-verbatim prompt, counted on its own line by `data/ground_check.py`.)

| source | typical yield | cost model | notes |
|---|---|---|---|
| **AlsoAsked** | dozens of questions per seed | credits per search; deep searches cost several times a standard one; cached searches are usually free | The workhorse: go heavy here. Returns data even for commercial terms where Google shows no PAA block. Set the region and language explicitly (defaults may not match the client's market) |
| **Google People Also Ask** | a handful per SERP | free | Google's own read of the query. Expanding a question appends more on some SERPs and nothing on others, so **breadth of seeds beats depth of expansion** |
| **Answer Socrates** | large lists tagged by funnel stage, with volume and CPC | limited free searches; paid tiers separate plain from recursive searches | Spend free searches on the broadest seed. The bottom-funnel rows are the most useful single output. Compare plans on recursive searches, not the headline number |
| **AnswerThePublic** | autocomplete permutations | small free allowance | The weakest of the four (autocomplete, not observed questions); may sit behind a human-verification check: ask the user, never work around it |
| **The client's Search Console human rows** | the client's own long tail | free | After the split (`data/longtail_split.py`); where provider-shaped phrasings usually live |

Run each question tool where its harvest can be exported or copied out and verified as a file the reviewer can re-check,
rather than read off the screen. A partial harvest is reported as partial.

**When a source rate-limits or blocks** (an HTTP 429, a human-verification page, an empty page where results were
returning a moment ago), stop that source and flag the coverage it reached ("questions harvested for N of M seeds;
stopped at a rate limit"). Never retry in a loop, rotate sessions or route around the block: carry on only with the
sources that still answer, and state the gap in the grounding split.

**Tier 2, authored content: someone wrote it.** FAQ blocks on ranking pages, pulled by scraping the top non-hub URLs.

**A SERP FAQ is not demand.** Those headings are written for the page, by a marketer or a model, and carry the vendor's
positioning. Useful as a hint about commercial angles; never enough to call a prompt grounded. When FAQ-sourced prompts
are re-grounded in tier 1, the observed versions are consistently blunter and shorter (invented ClientJ and ClientV
examples):
- "Which factors determine the lifespan of a professionally built wheel?" -> "do hand built wheels last longer"
- "Why choose a mobile mechanic over a traditional workshop?" -> "is a mobile bike mechanic cheaper than a shop"
- "How should collectors care for archival botanical prints over decades?" -> cut: no tier-1 source asks anything
  like it

## The credit arithmetic: price the run before you start it

Read your plan's per-search costs off the tool before the run, and write them in the run notes. A typical shape:

| search | relative cost | when to use it |
|---|---|---|
| cached (any depth) | free | re-running a seed you already searched costs nothing, so never skip a seed to save budget |
| standard | 1 unit | the default; run it first on every seed |
| deep | several units | escalate only where standard came back thin or empty |

If a deep search costs four times a standard one, a monthly allowance buys a quarter as many deep searches as its
headline number, and with the recirculation loop adding laps a month may cover only one or two clusters. Count the
seeds and price the run BEFORE starting, and flag it if the run would exceed the allowance (many plans have no rollover).
Where a seed needs a second opinion, reach for a different tool's free tier rather than spending a credit on a term the
first tool already answered.

## Choosing seeds: there is a specificity sweet spot

- **Too broad** (`bike`, `cycling`, `flowers`, `wall art`): these cache reliably, so they feel productive, and they
  return trivia and general questions ("Who invented the bicycle?", "Which flower stands for friendship?"). Very few are
  usable.
- **Too narrow** (practitioner jargon, rare tactic names): these rarely cache, return an empty page and burn the live
  allowance.
- **The sweet spot: mid-specificity trade terms** (`e-bike repair shop`, `wheel building service`, `bike fleet
  maintenance`, `framed botanical prints`, `wedding bouquet preservation`). These cache AND return buyer-level
  questions.

**The plateau.** Grounding flattens after enough seeds: when more seeds stop moving the grounded share, say so rather
than grinding. On a paid tier the move is deep searches on the narrow uncached seeds, where the remaining buying
questions live; the broad ones are already cached and harvested.

## Capture the harvest where it survives

Two separate losses, one habit that prevents both:
- **The accumulator.** Keep it in `localStorage`, not `sessionStorage` and not a page variable. A page variable dies on
  the first navigation; `sessionStorage` dies when the tab group is recreated, which a long harvest does routinely.
- **The download.** Browsers throttle repeated automatic downloads from one site, so a Blob download that worked three
  times can fail silently the fourth, and closing the tab loses the harvest.

So: accumulate in `localStorage`, download it, and verify the file on disk. If downloads stop landing, stop and ask the
user to allow the site; return the accumulated JSON in the tool result as a backup copy, never as the substitute for the
file. Re-list the directory once before concluding a download failed (it can take seconds to appear): re-running a
harvest you already hold is the expensive mistake.

## Commercial queries: no PAA does not mean no demand

Buying queries (`mobile bike mechanic`, `bike fleet servicing contract`) often return no PAA block at all. That is
Google declining to treat a buying query as a question, not an absence of demand; AlsoAsked usually returns dozens of
questions for the same terms. Go there before concluding a topic has no data.

## Why phrasing, not topics

The instinct on hearing "these are not realistic" is to add topics. Usually topic coverage is fine (cost, quality,
timing, best-provider themes present at the corpus rate) and the defect is phrasing alone: an authored set runs longer
than the observed corpus, with many more second clauses and much more first person. Re-grounding brings it back to the
corpus shape.

## These shape numbers are PAA-calibrated. Do not use them as an AEO target

Everything in the previous section compares against People Also Ask and AlsoAsked, which are short by construction.
Real AI-era long tail is much longer (a 10 to 14 word median is typical), far more often compound, and a large part of it
carries a provider or tool noun (`prompt-simulation.md`). So the tells below catch INVENTED phrasing. They are not a
length limit. A prompt set averaging PAA length has been written to the PAA corpus and misses the shape that earns
impressions. Read `prompt-simulation.md` beside this file before screening anything.

## The six tells of an authored phrasing

The first three are measurable and flagged by script (`data/verify_tracked_set.py` holds the length; `data/ground_check.py`
reports the clause and first-person rates). The last three must be read.

1. **Over 25 words, or under 4.**
2. **A second clause**: and / but / when / while / without / before / after / if.
3. **First person where the data does not show it.** First person is NOT automatically a tell: PAA and FAQ blocks use
   it ("Can I replace a bike chain myself?"). Strip what you invented; keep what was observed.
4. **The compound definitional**: "What is X and how do I do it?" Observed corpora split these into two questions; an
   authored set is full of them.
5. **The invented qualifier**: "for total peace of mind", "the smart way", "with zero hassle", "from a trusted
   expert". A reviewer will quote these back.
6. **"actually" as an intensifier**, and practitioner vocabulary the buyer never uses.

Not tells, and all high-intent: "Is X worth it?", "Does X still work?", "in <year>", "free X", "best X for <segment>",
"X vs Y", "How much does X cost?". The failure is never that prompts are evaluative; it is evaluations phrased in
language nobody types.

## The absence of data is itself a finding

Practitioner terms often return nothing across the whole harvest: they are words the industry uses, not words buyers
search. Report it rather than papering over it; it tells the client which pages have no demand behind them. Branded
prompts (the client or a named competitor) cannot be grounded by definition: mark them separately from rows that simply
found nothing.

## Contamination: read the harvest, never ingest it

Autocomplete carries other meanings of the same words (for ClientJ, motorcycle repair, exercise-bike parts and
repair-stand reviews), and PAA drifts into adjacent subjects (a `bike mechanic` seed returns questions about
apprenticeships and becoming one; a `botanical print` seed returns questions about printing on fabric). Read and cut; never load the raw harvest.

## What to ship

- Every prompt carries the observed question it came from **and its source**, or an explicit note naming the sources
  checked and found empty.
- The original wording beside any rewrite.
- **The grounded percentage, per source.** A shape test cannot catch shape-borrowing, so the gate measures verbatim and
  anchored matches against the corpus and reads each row's Observed anchor column; a rewrite whose anchor is not in the
  corpus fails.
