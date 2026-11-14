# Why audit a prompt set, and what transfers from a keyword audit

Vendor sources below write about their own tools; read their claims with that in mind.

## Triggers

| Trigger | What it looks like | Test that bites hardest |
|---|---|---|
| Repositioning | beginner to professional; budget to premium; consumer to business; a new category noun; a dropped line; a change of provider type in either direction | Positioning: does winning this make the brand look like what it sells now |
| Reporting dilution | prompts the brand does not want to win are inside the visibility and share-of-voice denominator | Focus and G4; branded prompts reported separately |
| Unknown or weak provenance | prompts simulated before grounding existed, or written by people nobody can name | Grounding and G1 |
| Scheduled | quarterly full pass, light review every 2 to 4 weeks | All, lightly |
| Off-cycle | product launch, competitor rebrand, a spike in an untracked question | The affected cluster only |

The SEO precedent for the repositioning trigger is the rebrand or site move: plan and benchmark before the change,
map old to new, and monitor both through the transition
(https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes). In keyword tracking that
means old and new brand terms tracked side by side for a while, then the new terms found and checked for
cannibalisation. For prompts it means: keep the old framing's data (archive, do not delete) and run the new set from
a dated start.

## How a keyword audit is run (the template we adapt)

- Start from what exists: review the published content and the tracked list, give every row a target URL and a status
  such as To Create / To Optimize / Updated (https://backlinko.com/keyword-mapping).
- Group by shared intent, judged by SERP overlap; one URL per cluster; an action per topic (Create, Optimize, No
  action); low-volume variants fold in as secondaries (https://ahrefs.com/blog/keyword-mapping).
- Assign a preferred URL to every tracked keyword and compare it with the URL that actually ranks
  (https://www.conductor.com/docs/platform/learning-center/library/keyword-tracking-best-practices/).
- Cut or deactivate keywords with no volume or no ranking for 6 to 12 months; device and location variants use
  tracking capacity, keep them only where they serve a goal (Conductor, same URL).
- Prioritise on traffic potential plus business potential (Ahrefs).
- Cannibalisation: one query, several URLs earning impressions; fix by merge, canonical, re-optimise or internal links
  (https://www.semrush.com/blog/keyword-cannibalization-guide/).
- Branded keywords in their own group, out of visibility metrics, because they mask non-branded movement
  (https://help.seomonitor.com/en/articles/6396378-branded-keywords-detected-automatically-separated).
- Typical columns: pillar, cluster, keyword, volume, difficulty, variations, target URL, status, action, last updated.

## What maps straight across to prompts

- Relevance to the current offering (the positioning test; prompt-tracking guides call it competitive relevance).
- One tracked unit per intent: one URL per keyword cluster becomes one prompt per intent (G2).
- Branded prompts segmented out of the headline number (SEOmonitor, for keywords): a brand name in the prompt makes
  the brand's own mention close to certain, so it hides movement on everything else.
- Funnel-stage balance and a mapped page per row, the way a keyword map gives every keyword a target URL.
- Business value as a gate (Ahrefs business potential): a prompt earns its slot only if winning it can lead to
  revenue.
- A schedule plus off-cycle triggers, the way a tracked keyword list gets a periodic review.

## What needs adapting

- **Volume.** Keyword volume is measured; prompt volume is modelled (consumer panels or keyword ratios). Rank with it,
  never cut on it (https://ahrefs.com/blog/how-ahrefs-estimates-ai-search-demand/;
  https://www.brainlabsdigital.com/ai-visibility-data-accuracy/). This skill's rule: zero volume never removes a
  relevant prompt by itself.
- **Cannibalisation becomes redundancy.** Several phrasings of one intent are replicas, not coverage, and they
  inflate share of voice.
- **Rankings become mention and citation rates across many runs.** Position is noise: under 1 in 100 chance of the
  same brand list twice (https://searchengineland.com/ai-recommendation-lists-rarely-repeat-study-468076).
- **Difficulty becomes influenceability**: who gets cited today, and can the brand's pages displace them.
- **"No ranking for 6 to 12 months" becomes "no movement after a content cycle, read weekly on enough runs."**
- **Personas and regions multiply cost** the way device and location variants do: some platforms run each prompt
  once per persona or per region, so every persona added multiplies the tracked runs.

## What is new for prompts

- **Positioning sensitivity.** A keyword is neutral; a prompt has an answer shape. "Best X for home use" is won by
  being named as a consumer pick; "cheapest X" by being named as the budget option; "best X for beginners" by being
  named as the entry-level choice. After a repositioning, wins in the old shape argue against the new positioning.
- **Provenance and grounding.** A keyword comes from a tool; a prompt was written by someone. Audit where it came from
  (keyword research, an earlier audit, unknown) before judging it.
- **Tracker echo.** The brand's own tracked prompts can come back out of Search Console as impressions and be
  mistaken for demand.
- **Instrument shapes.** Persona preamble plus "forced ranking", location injection, "evaluate the X company Y on Z":
  a tracking tool's strings, not a buyer's.
- **Phrased-only-by-an-SEO.** Keyword stacks and "best X" fragments fail G1 even when the keyword is good.
- **The denominator moves.** Adding or removing prompts moves visibility without changing what engines say. Log every
  change with a date so the trend line is not misread.

## Set size

Vendor guides suggest a starting set of somewhere between 15 and 200 prompts. A large inherited set that shrinks by
more than half in an audit is normal when it carried old-positioning framing and replicas.
