# Competitor and Pareto analysis

Contents: 1. Tier the competitors · 2. Pull top pages · 2b. Read the AI-citation columns. This is free AEO data. · 2a. Also pull Organic Positions. This is not optional. · 3. Compute the Pareto · 4. Classify by page type and compute traffic per page · 5. Pick 2-3 models to study · 6. Put it in the workbook, not on the slide · Output

This phase produces the two most persuasive slides in the deck. Do it early: it reframes the engagement
from "we need hundreds of pages" to "we need a few dozen of the right ones".

The tables below show layouts only: N and M% stand for the values you measure.

## 1. Tier the competitors

Two tiers, and the contrast is the story:
- **The peer cohort** (similar-stage challengers, including the client): little organic presence. Nobody
  owns the category's answers yet.
- **The adjacent incumbents**: established players with content engines. They are the proof the playbook
  works.

If the client gives you no competitor list, derive it: the review site's category grid (positions and
ratings) plus who the AI engines co-mention on your tracked prompts. Validate every domain
(`gotchas.md` #5).

**Do not prune the list to "relevant" competitors.** The adjacent set is a strategy-pattern sample, not a
ranking comparison. Two lists, two jobs: the peer cohort answers "where do we lose today", the incumbents
answer "what does winning look like in this category". Never merge them into one analysis.

## 2. Pull top pages

From Semrush (Organic Research, Pages), Ahrefs (Top Pages) or an API equivalent: URL, traffic, traffic
share, keyword count. The top 100 pages per domain is enough.

**If the API is out of credits, the web UI still works.** Agency seats run dry often; that kills the API
path, not the data source. Drive the UI with a browser-automation tool, e.g.:

```
Top Pages   https://www.semrush.com/analytics/organic/pages/?db=us&q=<domain>&searchType=domain
Positions   https://www.semrush.com/analytics/organic/positions/?db=us&q=<domain>&searchType=domain
```

Before leaving each domain, note the header figures: organic traffic, organic pages, total pages, homepage
share of traffic, homepage top keyword. Those alone let you build the summary table if an export never
arrives. Export quirks: `gotchas.md` #11.

### Export columns to look for

Column order changes between tool versions, so map by the header row, never by position. The fields that
matter:

- **Top Pages:** URL, Traffic %, **Number of Keywords**, Traffic, Traffic Change, **Answer Engines** (or
  equivalent AI-citation flags), Top Keyword, Primary Intent, **LLM / AI Prompts**.
- **Organic Positions (rankings):** Keyword, Position, Previous Position, Search Volume, Keyword
  Difficulty, CPC, **URL**, Traffic, Traffic %, Keyword Intents, Position Type.

Keywords-per-page (Top Pages) and the ranking URL (Positions) are the two most under-used fields in
either export. Together they build the case-study slide.

## 2b. Read the AI-citation columns. This is free AEO data.

Some keyword tools' top-pages exports carry **per-page AI-citation data** that prompt trackers do not give
you at page level:
- **Answer Engines:** which engines cite that page (values such as Google, Google AI, ChatGPT search,
  Gemini).
- **AI Prompts:** how many distinct AI prompts the page surfaces for.

Compute per competitor: **share of pages cited by any engine**, **total AI prompts**, and **AI prompts per
ranking page**. Then look at the outliers, because the outliers are the slide. The table layout:

| Competitor | Pages in export | Pages cited by an engine | Total AI prompts | Prompts per page | Reading |
|---|---|---|---|---|---|
| CompetitorX | N | N (M%) | N | N | what the ratio says about its content model |

Questions to test: does a smaller estate earn citations on a larger share of its pages than a bigger one?
Is a large programmatic estate cited on only a small fraction of its pages? Does any single page earn
more prompts than a peer's whole site? State the denominator you used: exports are capped, so on a very
large estate the percentage is "of the top N pages by traffic", not of the whole site.

This is the evidenced version of the skill's core claim. "You do not need hundreds of pages" stops being
an opinion and becomes a measurement: **volume does not buy citations; answering a real question does.**
Pair it with the Pareto on the same slide. It also gives you a per-page AI baseline for the client's own
domain on day one, before prompt tracking has accumulated any data.

## 2a. Also pull Organic Positions. This is not optional.

**Two exports, two different questions. Do not confuse them.**

| Export | Tells you | Does NOT tell you |
|---|---|---|
| Top Pages | how traffic is **distributed** across a site | what the site **ranks for**, or whether demand exists |
| **Organic Positions** | the **actual keywords**, volume, difficulty, intent, and the ranking URL | - |

**Never infer the size of a category's search market from a top-pages export.** A top-pages export can
make a market look small. Positions can show a competitor ranking for high-volume non-brand terms from a
few posts. Check Positions before you claim anything about demand.

Required before any claim about category demand:

1. **Export Organic Positions for every comparator**, not just Top Pages.
2. **Classify every keyword brand vs non-brand** and report **non-brand share of traffic** per competitor.
   That one number is the honest answer to "are they brand-dependent?". Build a token list per domain
   and include **misspellings, legacy names, product names and acquired brands**: a misspelled brand is
   still brand traffic, and a company that rebranded or acquired others carries several brand
   vocabularies at once:
   ```python
   BRAND = {
       "competitora.example.com": ["competitora", "competiter a", "oldname", "acquiredco"],
       "competitord.example.com": ["competitord", "compd", "productname"],
   }
   ```
   Weight by **traffic, not keyword count**: a large non-brand keyword count can still earn almost none of
   a site's traffic, so the count alone says little. Banding that reads well:
   15%+ has built real non-brand demand, 5-15% some, under 5% brand name only.
3. **Filter the non-brand set to keywords relevant to the client's service**, with volume and difficulty
   attached. This is an **evidenced content target list**: demand a competitor has already proven, not
   demand you estimated.
4. **Find the exception.** If one competitor has materially more non-brand traffic than the rest, that is
   the most valuable slide in the deck. It turns an abstract recommendation into a case study: this model
   works in this exact category, for this exact buyer, and here are the pages that did it.

Output a brand vs non-brand table:

| Competitor | Total keywords | Non-brand keywords | Non-brand % of traffic | Reading |
|---|---|---|---|---|
| CompetitorX | N | N | M% | the band it falls in (real non-brand demand / some / brand name only) |

**The lesson generalises:** when you are about to explain *why* a market looks the way it does, check
whether you measured the thing you are explaining, or only something correlated with it.

## 3. Compute the Pareto

Sort pages by traffic, take the cumulative sum, and count how many pages reach 80% of the domain's
traffic. The deck line takes the form "N pages get CompetitorX to 80% of its traffic", and the conclusion:
a few dozen well-built pages can match a mid-tier incumbent; quality and structure beat volume, which is
the right play for a challenger.

Read the Pareto together with 2a. A very low page count for 80% of traffic means one of two things, and
they lead to opposite recommendations:
- **concentrated on brand** (homepage plus login dominate, non-brand share near zero): the site has no
  content engine;
- **concentrated on a few winning assets** (a glossary hub, a cost guide): the site has a content engine
  and it is efficient.
The brand vs non-brand split tells you which one you are looking at. The Pareto alone cannot.

## 4. Classify by page type and compute traffic per page

Bucket every top page: glossary / knowledge hub / guides / blog / product / other, then average traffic
per page by type. Use an ordered URL-pattern classifier, first match wins, tuned to the category. Keep
**Careers** and **Account / Login** as their own buckets rather than folding them into "other": if
careers or login pages rank among a competitor's biggest traffic pages, it has no content engine, and
saying so plainly is worth more than a Pareto number.

```python
import re

def classify(url):
    path = re.sub(r"^https?://[^/]+", "", url.lower()).rstrip("/")
    if path in ("", "/"):                                                   return "Homepage"
    if any(s in path for s in ["/blog", "/insights", "/article", "/news"]):  return "Blog"
    if any(s in path for s in ["/glossary", "/terms", "/what-is"]):          return "Glossary"
    if any(s in path for s in ["/learn", "/knowledge", "/hub", "/academy"]): return "Knowledge hub"
    if any(s in path for s in ["/resource", "/guide", "/ebook", "/webinar", "/case-stud"]):
        return "Guide / resource"
    if any(s in path for s in ["/login", "/register", "/account", "/portal"]): return "Account / Login"
    if any(s in path for s in ["/career", "/job"]):                          return "Careers"
    if any(s in path for s in ["/product", "/platform", "/solution", "/pricing"]): return "Product"
    return "Other"
```

Output one row per page type: page type, pages, total traffic, traffic per page, AI prompts per page,
and the role it plays (education, definitions, volume, links). Sort by traffic per page; the order is a
finding for this category, not a given.

This is what justifies (or overturns) the default build order (glossary, hub, guides, blog) in
`what-wins-content.md`. Also note structural facts that land hard, in the form "a single hub carries M% of
CompetitorX's traffic".

With Positions data, go one level deeper on the winners: for the 5-10 pages carrying the most non-brand
traffic, report **how many keywords each page ranks for**. "One article ranks for N keywords" is a far
stronger argument for depth over volume than a traffic number, and it is the most persuasive line for a
client who thinks they need hundreds of pages.

## 5. Pick 2-3 models to study

Name the specific competitors whose architecture you are recommending and say what each does well (for
example "a definitions-led glossary plus learn hub", "a question-led blog engine", "a comparison-page
library"). Concrete beats abstract.

## 6. Put it in the workbook, not on the slide

Top 40 pages per competitor, one tab each, columns: `# | URL | Traffic | Traffic % | Cumulative % |
Keywords | Top keyword | Intent | Page type | Answer engines`. **Highlight every row inside the 80%
cumulative band** so the client sees the Pareto without reading a number. Colour the tabs by tier so the
peer cohort and the incumbents stay visually separate. Put the source and pull date in a subtitle on every
tab.

The deck gets at most four slides out of all this: the landscape, the Pareto (read against brand share),
the exception as a case study, and the evidenced demand list. Everything else is workbook.

## Output

- A tiered competitor table with organic visits.
- **AI-citation coverage per competitor** (pages cited, total AI prompts, prompts per page) from 2b.
- **A brand vs non-brand table** from Organic Positions.
- The Pareto stat.
- The page-type economics table.
- **The evidenced keyword target list** (non-brand, relevant, with volume and difficulty).
- 2-3 named models to study, including **the exception** if one exists.

Parsing is a dozen lines of openpyxl or pandas against the header names above; there is no carried script
for it.
