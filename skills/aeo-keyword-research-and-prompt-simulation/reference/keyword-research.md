# Phase 1 in full: category-anchored keyword research

The steps SKILL.md lists for Phase 1, with the reasoning and the checks. The Search Console pass, the seed chain,
the hand clean and the UI mechanics are in `seed-chain.md`; the traps are in `data-traps.md`; scope and the
product-fit gate are in `scope-and-fit.md`.

Worked examples in this file use invented clients: **ClientJ**, a bicycle-repair chain (a done-for-you service with
workshops, mobile vans and fleet contracts), **ClientN**, a ceramics studio, and **ClientV**, an online botanical-print
shop. Figures are illustrative.

## A1. Confirm the anchor

Scrape the brand's product or service page for the line, then verify the category on the analyst peer-review market
page (enterprise services) or G2 / Capterra (self-serve SaaS). Record the exact category label, sibling categories,
the market definition and the mandatory-feature groups the category page lists: structure clusters around those
groups. Build the cycle backlog: one cycle per line.

## A2. The competitor set: category + SERP + ads, never organic overlap

- The category page's listed vendors, with their review counts as an earned-authority benchmark.
- The ranking product or provider domains on the two or three category head terms.
- The advertisers on those terms (A4-ads).
- Tag each **Direct** (a pure play in the category) or **Partial** (a platform that ranks for the heads without being
  a pure play).

### The two-market split (before any demand verdict)

Before calling a cluster alive or dead, check whether it is two markets with different buyers, because the blended
trend line hides one of them. For ClientJ, `wheel truing` reads as one subject. Half its SERP is a **tools** market:
truing stands, spoke keys and step-by-step tutorials for home mechanics, sold by parts retailers. The other half is a
**done-for-you** market: workshops with booking calendars, van collection and a guarantee on the work. The services
half can grow while the tools half shrinks. Split the cluster, give each half its own verdict, and mine each half's competitors separately.

## A3. Seeds

On-page names (H1, title, feature names), the **literal category label** as a keyword, and the provider-noun variants
(`software`, `tools`, `platform`, `services`, `provider`, `company`, `agency`).

## A4. Competitor mining

- Scrape 3 to 5 rival pages for meta keywords, titles and H2s verbatim; some sites expose a whole taxonomy in a meta
  keywords field.
- Export every keyword for each relevant competitor **page**, not only the domain filtered to one seed: a domain export
  filtered to one word shows a fraction of what a page ranks for. Find the adjacent pages from the SERPs of your own
  kept keywords and hand-decide every new keyword with a reason.
- Backlink anchor-text distribution for the brand and the top rivals.

### A4-loop. The recirculation loop (the single most important process in Phase 1)

**No term is ever terminal.** Every new term, from any source, goes back through bulk sizing and then phrase-match
expansion. This is a loop, not a pipeline, and the list is finished only when a full lap surfaces no new relevant
group. The trigger is mechanical: if you see a term you have not sized, you size it.

| You see a term in | You immediately |
|---|---|
| a competitor's ad headline or sitelink | size it; expand it if it has volume |
| a Search Console query (any regex pass) | size it; expand the ones with volume |
| a gap-export row that survives brand-noise stripping | size, expand |
| a SERP result title or URL slug | size, expand |
| a competitor page's H1/H2, service name, package name or nav label | size, expand |
| a listicle title you are targeting for placement | size, expand |
| a forum or Q&A thread title in the citation data | size, expand |
| a coinage the client owns | size, expand, and record a zero as the category-creation finding |

The step, whatever the trigger: harvest the phrasing rivals use in their paid and organic copy (headlines, sitelinks,
landing paths, H1/H2, nav labels) and in forum titles and SERP slugs, size every phrase, expand each one with volume,
and read the expansion for a lane the current clusters do not hold. A new lane goes through the drift check like any
other cluster. Worked pattern (invented): a forum thread titled `anyone else's ceramic mugs crazing after a year?`
gives ClientN the phrase `mug crazing`; sized, it has volume, and its expansion (`crazing repair`, `refire crazed
glaze`) is decided row by row against the kiln-firing line.

Each lap: collect every unsized term the last lap produced, size them in bulk batches, expand the ones with volume,
harvest what that produces, lap again. Stop when a lap yields nothing new and relevant, and log the lap count: one lap
means you stopped too early. **A term that returns zero volume is still a result**: record it as category-creation
evidence with its source, never silently drop it, and do not re-run it next lap.

**The late-source lap.** A source that arrives after the first lap (a Search Console pull run late, competitor-page
exports, a reviewer's new seeds) gets a lap of its own, closed only when three steps have run on every keeper from it:
(1) bulk sizing; (2) phrase-match expansion on every keeper with volume AND on every product or category noun the
keepers contain that has no expansion yet; (3) the SERP reverse loop (seed-chain C8): SERP every keeper, then pull
rankings by URL for the non-exported pages that recur across those SERPs and hand-decide what they rank for. A keep/out
triage of a late source is the start of its lap, not the end. The failure this prevents: a late source triaged once,
its keepers never sized or expanded, and the product's own category noun never expanded at all.

### A4-ads. The ads transparency read (ad spend is a commercial signal no volume tool gives)

Pull every competitor's ads from the Google Ads Transparency Center in the browser (APIs that return only creative IDs
do not carry the copy) and read them as keyword data:

- Extract category nouns, value claims, proof and number claims, CTA phrasing, sitelink labels (sitelinks name
  sub-services) and landing-page paths (a dedicated path for a term proves it converts, whatever its volume).
- **A term with no organic volume that several rivals pay for is a confirmed commercial term.**
- Note who runs no ads: an uncontested paid channel is a finding.
- Note which concepts nobody advertises on. An absence across a whole category (every rival selling on price, none
  on a guarantee the client gives) is often a strong positioning finding.
- **Record coverage per advertiser: ads read against ads running.** A large advertiser can run a hundred or more
  creatives and a manual read samples them. A claim that only one rival advertises on a theme holds only for the ads
  read: write it as "among the ads read" and keep the per-advertiser counts in the working files.

## A5. Metrics

Volume, CPC, competition and trend per keyword; difficulty per head term from the keyword tool or, failing that, from
SERP composition (listicle- or incumbent-dominated = higher). A volume tool usually returns the exact keyword only, so
enumerate competitor-harvested terms and modifier variants and size each. When one branch of a multi-source volume
tool errors while the others return data, note it and use the data that returned; when no difficulty data is
available at all, estimate difficulty from SERP composition and say so in the Source cell. The deep difficulty
figures and the full long tail come from the phrase-match export (A8).

### A5-spike. Read the median month, not the headline

A headline volume can be dominated by one anomalous month, and inflated terms sort to the top of every list you build.

- Standing check on every keyword, default thresholds: **if the max month exceeds 5x the median, the headline sits at
  or below that max (within 10%), and the median is below the headline, report the median-based steady volume and put
  the headline in a note.** Example (invented): `pottery wheel hire` shows a headline of 4,000 and a median of 300;
  eleven months sit near the median and the twelfth, when a televised pottery contest aired, reached 4,200.
- Where the headline runs well above the trend's max, the two series disagree on scale, not on a spike: keep the
  headline and say so in the Source cell.
- Never silently swap one for the other: a genuine spike is a seasonality finding and the reviewer should see both.
- **Write all three conditions into the method text and name the series the median came from.** A shortened rule
  reads as a broken one to an auditor who finds rows meeting the short version with no note.
- When sizing is fanned out to subagents, put this rule in every agent's prompt: a later cleanup pass cannot tell an
  inflated headline from a real one.

### A5-absence. The open-goal sweep (cheap, run it before anything is scored)

Pull the top 20 for every commercial head term and look for one thing: the client's domain. A client absent from every
rising commercial head term is a finding worth leading with, and it costs one call per term.

- **Run the same sweep across the tracked competitors.** The more valuable absence is a question no rival answers: a
  non-branded prompt no competitor is named in, on a theme the client already offers, is among the most persuasive
  findings a run can report, and it exists only if the sweep covered rivals.
- Budget it: the client across all prompts, then every rival across the non-branded subset. **Absence is a finding**;
  write it as one, never as a blank cell.
- **Name the source and date behind every open-goal claim.** A live top 20 and a rank tracker's top 100 disagree by
  date and depth. Give the live-SERP finding from the live pull and the whole-map count from the tracker, never both in
  one sentence.

## A6. Clean and filter

- **Collapse synonym groups** to one primary per group, the rest Secondary (avoids cannibalization). Keep distinct
  volumes a tool returns for near-synonyms as secondaries.
- **Data traps** (`data-traps.md`): exclude terms whose volume belongs to another intent or category, visibly.
- Junk filters: brand variants, geo when not geo-targeting, foreign-language, corporate and navigational,
  other-brand-vs-other-brand comparisons.
- Then the hand clean in `seed-chain.md` C6.

### A-intent. SERP intent never disqualifies a keyword (it only tells you the page type)

**Never cut a keyword because its SERP is informational.** The SERP shows what Google ranks, not what the searcher
wants. A buyer with live commercial intent routinely types an informational query while researching a purchase they
have decided to make. An all-blog SERP means the route to that commercial intent is an informational page carrying the
commercial path.

What the SERP legitimately tells you:
- **Listicle-dominated** -> entry is via placement in those listicles.
- **Vendor service pages** -> a service page can rank directly.
- **Editorial / blog** -> an informational page with the commercial CTA and the internal path to the service page.
- **Wrong entity** (a ticker, a dictionary word, another industry) -> the only legitimate cut on SERP evidence.

The AEO consequence: informational seeds are what you build commercial and transactional **prompts** from. Answer
engines get buying questions in informational language constantly; cut every informational-SERP keyword and the prompt
universe has no commercial rows for that theme. Worked example (invented): for ClientV, the top 10 for `how to
preserve a wedding bouquet` is all how-to articles, yet three keepsake studios run ads on it and its trend climbs every
spring. Paid placement plus a rising season says buyers are inside that query. It stays, as a how-to guide that ends
in the pressing-and-framing service, and as the seed for "can I post my bouquet to someone to press and frame after
the wedding?".

**Rule: cut for irrelevance or wrong entity. Never for intent shape, never for low volume alone.**

## A7. Cluster, score, map

Category-aligned clusters with primary and secondary; difficulty Low / Med / High from the SERP; each keyword mapped to
an existing or new page; each keyword's answer type decided with the three questions in `intent-format-kpi.md` section 3
(the same questions run on every tracked prompt at B2). The page is an **output** of clustering on shared top-10 URLs (`prompt-universe.md`
B3-cluster), never an input.

### A7-title. Page titles come from the keyword and its SERP, never from a prompt

A page's title is written from its head keyword and the titles that already rank for it. A content generator writes to
the title it is given, so a title copied from a prompt, a question in a subtitle, or a segment the keyword set does not carry (a
title narrowed to one industry while the page's keywords are general) makes the page chase one phrasing and give up its head term. Answer
engines rewrite every prompt into their own searches, and reruns of a prompt share few cited sources, so a title copied
from one prompt carries nothing into the answers. Most titles that already rank for a head term carry the term
itself, which is the pattern to follow. The prompts still shape the page: they become its H2s, answer blocks
and FAQ entries, and the fan-out block names the heading each needs.

The title pass, before any title enters a page map or content plan:
1. **Head term.** Sort the page's keyword set by volume and take the highest term the ranking titles themselves use, in
   their wording (singular or plural, one word or two, as the titles split it).
2. **Format.** Read the top 8 to 10 titles for that term (reuse the clustering SERP; fetch only where none is stored)
   and match the dominant format: definition ("What Is X?"), how-to ("How to X"), list ("Best X in <year>"), service
   page ("X Services", "X Agency"), comparison ("X vs Y"). Where the SERP for a service term is informational, an
   informational title is right.
3. **Lead with the head term.** A subtitle after a colon carries a second keyword from the set or the leading prompt
   angle, only when it serves the same intent.
4. **No prompts, no narrowing.** No question title other than "What Is X?" on a definition SERP; no segment the set
   does not hold.
5. **Service pages** take the service keyword as buyers search it, with no guide subtitle and no question; the page's
   other questions (hire or do it in-house, pricing) become sections.
6. **One head term per page.** A title never carries another page's head term.
7. **Reviewer lines stand.** A page the reviewer ruled informational keeps an informational title.
8. **Mechanics.** At most 70 characters, no dashes, title case to match the content plan, a year only where the ranking
   titles carry one.
9. **Pages already published or queued.** Retitling a page already in the CMS is a content change for the owner, with
   the evidence.

Record each title with its head term, the SERP format and a one-line reason, and keep the old title in the delta.
**Gate titles against the head term before delivery and after every remap**: every word of the head term appears in
the title (word order may change only where the ranking titles reorder it, with the reason written). Moving keywords
between pages during review can change a page's head term without anyone touching its title.

### A7-placement. Read WHAT ranks, not just who

Classify the top 10 of every commercial head term by format:
- **Vendor service pages dominate** -> a page of the client's own can rank. Build it.
- **Listicles dominate** -> entry requires placement on someone else's list. That cluster's output is an outreach row,
  not a CREATE row, and also an owned listicle (the work optimises for AI answers as well as rank).

Getting this backwards commits a writer to a page that cannot rank, and it is
invisible unless you read the SERP composition. **Where the shape is listicle-dominated, the
listicles are a deliverable**: extract every "best/top X" URL from the head-term SERPs, count how many of those SERPs
each domain covers, and sort by reach.

## A8. Phrase-match deep dive

In the keyword tool's expansion view, use **phrase match** (broad match is noise), export, and consolidate in code.
Each row carries keyword, intent, volume, difficulty, CPC and SERP features. Verify each download. A seed that returns
"no data" produced no file, and that absence is a finding (an owned coinage with no established demand).

## A9. Adjacency expansion

SERP each seed, read who ranks, scrape the top competitor and listicle pages, mine the taxonomy they target (meta
keywords, titles, H2s), turn it into net-new keyword groups, size each, iterate on the winners. The seed SERP shows the
ecosystem the theme lives in, and its vendors hand you the adjacent groups. Cluster new groups by relevance to the
client, not by volume. Worked pattern (invented): ClientN's seed `wedding favour mugs` is led by personalised-gift
marketplaces, and their category menus list `ring dishes`, `place-setting bowls` and `hand-painted name tiles`. Each is
sized as its own group; only `ceramic ring dish` comes back with demand, so it alone gets a lap.

## A10. Segment-qualifier lens

When the reviewer names a focus segment (for example enterprise), size the **qualifier x theme matrix first**. Most cells
come back near zero because buyers self-qualify. Report that honestly and split: **Target** = the few qualifier terms
with real demand (often the highest CPCs in the set), **Frame** = everything else, captured by qualifying the base term
plus a persona and delivered as qualifier-framed prompt rewrites, not as keywords.

## A11. AI-Overview lens

The expansion export's SERP-features column flags AI Overview per keyword. Compute the **AI-Overview trigger rate per
cluster** (where AI answers already appear, which is where AEO visibility converts now). Prioritise low-difficulty
AI-Overview questions as citation targets, offer an AI-Overview Opportunities tab, and flag every prompt with AI Overview
Y/N and the difficulty of its grounding question.

## Prompt shapes Search Console reveals (feed them to Phase 2)

Search Console on an AEO client shows prompt shapes, not only keywords. Split the export first
(`data/longtail_split.py` with the client's tracked-prompt export): a client's own tracked prompts, run daily, come
back out of Search Console as impressions. Shapes from instrument rows are fine to learn from; their volumes are run
counts.

- **Forced-ranking prompts** ("<role> here. list the top <category> options for <job> and order them strongest to
  weakest"), several role variants of one prompt: another tracker's set executed against the client's pages. Evidence of
  what the category's instruments run, never buyer demand; never copy the output instruction into a tracked prompt.
- **Brief-style prompts**: a paragraph-long problem statement that ends by asking the assistant to find who could
  do the work. Each is a demand artefact: a buyer describing the job before any provider is named.
- **Multi-vendor comparison prompts** ("compare <a>, <b> and <c> on <attribute>"): check whether the client is named.
  Being surfaced for a comparison set you are not in is a reportable failure.
- **Non-English variants** of the same prompts: usually a tracker running its set in several languages. Check the human
  rows before calling it non-domestic demand.
- **Switching prompts**: "moving away from <rival>", "something like <client> but <attribute>", "what to use
  instead of <rival> for <job>".
- **Branded product prompts**: size each of the client's product names on its own; a product name can carry branded
  demand that its generic category word does not.

## Demand verdicts (do not pad; report the truth)

Give each line a verdict and size the work to it. Do not force a 15 to 20 keyword, 20-prompt set onto a line with no
demand. Invented example for the bicycle-repair chain (ClientJ):

- **Real matching demand** (full set): tune-ups and wheel builds; riders search the service by name and several local
  rivals advertise on it.
- **Capture-only** (small set, flagged): e-bike motor diagnostics. Riders describe the fault (`ebike cuts out going
  uphill`), not the service, so the service terms are near zero and the rows are written from symptom questions.
- **Naming mismatch** (small set, flagged): the fleet line, sold under ClientJ's own plan name, which nobody types;
  operators ask for `courier bike maintenance contract`, and only a handful of rows carry that noun yet.
- **Open goal**: a category where no brand has AI visibility for the shortlist prompt and the demand is real, such as
  cargo-bike servicing for nurseries and schools. Flag these explicitly as the most winnable lines.
