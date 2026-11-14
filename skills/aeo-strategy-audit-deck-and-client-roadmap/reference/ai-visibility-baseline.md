# AI-visibility baseline and prompt tracking

Tool options for each step are in SKILL.md under Tools. The method is the same whichever you use.

## The pipeline

```
real-query seeds (real-query-mining.md) + keyword-gap themes + audience keywords
  -> generate -> filter -> cluster -> load into the tracker -> measure per prompt x brand x engine
  -> audit the set (keep / cut / rewrite)
```

### 1. Build the prompt universe

- Generate intent-balanced, deduplicated prompts per product or segment, seeded with the real phrasings
  from Search Console and Bing Webmaster Tools, every keyword-gap theme with volume, and the audience's
  affinity keywords.
- Add real buyer language where the client can share it: sales-call transcripts, discovery-call
  objections, RFP language, win/loss notes. That is material competitors don't have.
- Check demand selectively on the prompts you are unsure about (prompt-volume estimates are slow or
  costly; don't run them on everything).

### 2. Clean the list

Strip search operators, year stamps, foreign-language and geo variants you are not targeting, client
brand variants (in the non-branded set), other brands' names where they make the prompt branded, and
duplicates. Keep a record of what was removed and why.

### 3. Group it

Cluster by meaning so you can see the topic shape and spot thin or duplicated coverage. The clusters
become the themes on the Topical Authority Map.

### 4. Track it

Create a project or workspace for the client in the tracker with the domain and the competitor set, and
load the prompts with a topic, tags and a type (brand or category). Record the project identifier in the
strategy workbook so the next read uses the same set (`gotchas.md` #9 on import shape).

### 5. Measure

Run every prompt in every engine the audience uses (at minimum the ones it over-indexes on), and check
each brand in the competitor set, so share of voice compares like with like. Where an engine has no API,
run it in the browser (a temporary or logged-out chat) and record the answer. Keep the raw answers or
their citations; the accuracy check and the citation-source analysis reuse them.

### 6. Audit the set

Before the second month of tracking, review each prompt: its intent, the realistic metric (mention or
citation), the play it supports, and a keep / cut / rewrite call based on its first reads.

## Prompt taxonomy (aim for about 50 tracked prompts)

Spread across the funnel; the mix is the point.
- **Brand** (few): "What is <Brand>?", "Is <Brand> legit for <use case>?". These usually score near 100%
  and prove the branded layer works. Exclude them from the share-of-voice scoreboard.
- **Top of funnel, category and definitional:** "What is <category term>?", "How does X work?". Glossary
  and hub content wins these. Measure them on citation: they name no brand by nature.
- **Middle of funnel, comparison and alternatives:** "Best <category> for <buyer>", "Alternatives to
  <incumbent>", "<A> vs <B>". Comparison and listicle pages decide these.
- **Bottom of funnel, buyer scenario and persona:** low volume, highest intent. Source these from sales
  material and the audience personas.
- **Trust cluster:** the doubt queries from `real-query-mining.md`.
Keep non-branded prompts brand-neutral (don't name the client) so the score measures organic appearance.

## The scoreboard (what goes on the deck)

Per brand: **visibility** (share of prompts where the brand appears), **share of voice** (the brand's
share of all brand mentions across the set), **average position** in the answer, and sentiment. Track the
competitors side by side.

The pattern to look for, often the best slide in the deck: a challenger with a GOOD average position but
LOW visibility. When it is mentioned it appears ahead of the incumbents; it is simply mentioned on few
prompts. The fix is frequency, not perception.

Also look for a term the client coined already returning them first on a non-branded prompt. That is proof
the playbook works: coin it, define it, own the answer.

## Prompt-to-page mapping

When the question is "which page should own which prompt": collect the search-result URLs and the AI
citation URLs per prompt, build the client's page inventory from the sitemap, then cluster prompts by
shared URLs and assign each cluster to an owned page, or flag a content gap. See the sibling skill
`prompt-to-page-serp-clustering` for the full method.

## Cadence

Re-run the tracked set monthly. Visibility and share of voice are the monthly KPI, measured against the
onboarding baseline. Label the first read directional.
