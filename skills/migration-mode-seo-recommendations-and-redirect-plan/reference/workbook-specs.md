# Workbook specs: the two deliverables

Contents: A. Technical + Migration workbook · B. Content Plan workbook · Conventions shared by both workbooks

Split the work into **two** workbooks so each stays usable; one mega-workbook gets abandoned. Build them
with `openpyxl` (or in the client's spreadsheet tool). Use the client's own spreadsheet template and
font if they have one; otherwise the neutral conventions at the end of this file.

---
## A. Technical + Migration workbook

| Tab | Contents |
|---|---|
| MENU | hub, with back-links from every sheet |
| Migration Checklist | phased, numbered, status dropdown |
| **Redirect Map** | the core artifact (below) |
| Priority Pages | ranked; marked **provisional** until Search Console data lands |
| URL Inventory | crawl ∪ Search Console ∪ GA4 ∪ backlink targets, with the source of each row |
| Schema Specs | JSON-LD split into "implement now" and "implement later" |
| Recommendations | tracker: Priority, Category, Recommendation, Owner, Status, comments from both sides |

### Redirect Map columns
`# · Legacy URL · Source · Current status · Destination · Redirect type NOW · Final type ·
Redirect status · Owner · Tested staging · Tested launch · Notes`

`Source` is one or more of `crawl`, `gsc`, `ga4`, `backlinks`. `Current status` is the legacy URL's
status today (200, 301, 302, 404 …), after following any existing redirect to its end.

**Staged model** (use it when the new domain or page list isn't confirmed; don't stall):

| Situation | Now | Final |
|---|---|---|
| Destination known | 301 | 301 |
| New equivalent not built | **302, tracked placeholder** | flip to 301 on release |
| No real destination | 301 to the closest relevant parent, or a deliberate 410 | same |
| Staging / dev host | **exclude, never migrate** | — |

The `Redirect status` column takes one of: `Ready` · `Awaiting build` · `Scope decision` · `P0` ·
`Flipped to 301` · `Exclude`. It is what stops the 302s being forgotten. Drive it from a data-validation
list so nobody types a new status.

Invented example rows (`example.com` → `example.org`, OldCMS → NewCMS):

| # | Legacy URL | Source | Current status | Destination | Now | Final | Redirect status |
|---|---|---|---|---|---|---|---|
| 1 | `https://example.com/` | crawl | 200 | `https://example.org/` | 301 | 301 | Ready |
| 2 | `https://example.com/index.php?cat=lights` | crawl, backlinks | 404 | `https://example.org/shop/lights` | 301 | 301 | P0 |
| 3 | `https://example.com/app/quote-builder` | ga4 | 200 | `https://example.org/quote` | 302 | 301 | Awaiting build |
| 4 | `https://es.example.com/` | gsc | 200 |  |  |  | Scope decision |
| 5 | `https://dev.example.com/` | crawl | 200 |  |  |  | Exclude |

Leave Destination, Now and Final **blank** on Scope decision and Exclude rows (the checker also reads
a lone dash as blank). Export this tab to CSV and run `python3 data/check_redirect_map.py <file>.csv`
before it ships; these five rows pass it, and `--final` flags rows 3 and 4 until they are settled. The
checker reads the column names above (case-insensitive) and needs at least `Legacy URL`,
`Destination`, `Redirect type NOW` and `Redirect status`.

**Source the rows from crawl ∪ Search Console ∪ GA4 ∪ backlink targets.** Analytics exposes gated paths
a crawler cannot see; a crawl-only map can silently drop the client's core product.

### Checklist phases, and the five additions a generic template lacks
Phases: 0 decisions · 1 pre-launch · 2 launch day · 3 post-launch · 4 performance review.

Add beyond any stock checklist:
1. **Phase 0, domain and brand decisions:** new domain, old domain retained (with owner and renewal),
   subdomain scope, product-line scope.
2. **Brand-navigational benchmark variant:** brand query volume, direct traffic, conversion
   completions, not rankings.
3. **AI / LLM continuity:** crawler directives on the new domain, entity seeding (`alternateName`,
   `sameAs`, reference data), monitoring old vs new name in AI answers.
4. **Offline / outreach coordination:** packaging, listings and third-party profiles carry the old
   name for years; uncoordinated, the redirect is cosmetic.
5. **Gated-surface verification:** account, checkout and login flows must survive cutover; that's
   where conversion lives.

### Migration scorecard (the deck's scorecard slide)
Measured values only, never a judged score out of 100. Each row comes from an artifact this skill
produces, so a run can fill it; a row whose data isn't in yet shows a field such as `N of M` or
`[DATE]` and a presenter note saying what fills it.

| Row | Value | Source |
|---|---|---|
| Legacy URLs with a decision | N of M (N%) | Redirect Map: rows with a Redirect status |
| Redirect-map checker findings | N | `data/check_redirect_map.py` output |
| P0 redirects still open | N | Redirect Map: status `P0` |
| Placeholder 302s awaiting a flip | N | Redirect Map: status `Awaiting build` |
| Subdomains crawled | N of M found | crawl vs subdomain hunt (DNS, certificate logs, GA4 hostnames) |
| Key events instrumented | yes / no | GA4 key events report |
| Non-brand share of Search Console clicks | N% | Search Console export 1 vs 2 |
| Planned page list received | yes / no, `[DATE]` | the client's written page list |

At cutover, re-run the same rows; the deck then shows before and after side by side.

Mechanics: a hidden settings sheet drives the status dropdown (data validation) and the conditional
formatting; freeze panes; gridlines off. **Renumber tasks when you reuse a checklist**: inherited
checklists often carry duplicate numbers at a phase boundary.

---
## B. Content Plan workbook

| Tab | Contents |
|---|---|
| MENU | hub |
| Summary | per competitor: set, traffic, pages, **homepage % of traffic**, top-3 %, content model |
| Pareto | pages needed to reach 50 / 80 / 90% of traffic, per competitor |
| **Content Ideas** | pages to create, from **two sources**: Search Console query gaps + competitor page-type patterns |
| **Keyword Opportunity** | the evidenced target list from the positions exports (below) |
| **Brand vs Non-Brand** | per competitor: total keywords, non-brand keywords, non-brand % of traffic, reading |
| **Case Study** | only when an exception exists: the exception's pages, non-brand traffic, keywords per page, the queries it captures |
| one tab per competitor | top pages, traffic, %, **cumulative %**, keywords, top keyword, intent, page type, **answer engines citing** |

### The three keyword-level tabs (built from the organic rankings / positions exports)
Top pages alone cannot produce these. Method and column maps: `reference/competitor-analysis-method.md`.

**Keyword Opportunity:** `Keyword · Volume/mo · Difficulty · CPC · Best rank · Who ranks · Theme ·
Intent · Their URL`. Non-brand keywords, filtered to the client's service, above a volume floor.
Highlight the low-difficulty rows; that column turns a list into a plan. Say in the subtitle that
**every row is demand a competitor already proves**, not demand you estimated. That sentence is why the
client trusts the tab.

**Brand vs Non-Brand:** one row per competitor, sorted by non-brand share of **traffic** (not keyword
count). Colour the reading cell: ≥15% has built real non-brand demand · 5–15% some · <5% brand name
only.

**Case Study:** one row per page of the competitor that solved it:
`Page · Non-brand traffic · Keywords it ranks for · Highest-volume queries it captures`. The
keywords-per-page column is the argument for depth over volume.

### Per-competitor tab conventions
Top 40 pages by traffic. Highlight every row inside the **80% cumulative band**, so the client sees the
Pareto without reading a number. Flag rebrand-transition pages (`is-now`, `new-name`, `rebrand`,
`formerly` in the path) with a contrasting fill; on a rebrand engagement that is the most transferable
tactic in the analysis. Colour the tab by set (direct vs indirect) so the two lists stay visually
separate.

### Content Ideas columns
`Priority · Page to create · Type (LP / Blog / Resource) · Funnel stage · Source (GSC / Competitor /
Both) · Evidence · Target query`.

Colour-code the Source cell: showing that some ideas come from the client's own data and some from the
category is what makes the sheet persuasive.

### Pareto is the headline
Compute cumulative % per competitor and highlight the rows inside the 80% band. The contrast to look
for: brand-concentrated direct competitors reaching 80% of traffic within a handful of pages, against
content-engine competitors that need hundreds. When it appears, that contrast **is** the content
argument.

---
## Conventions shared by both workbooks
- MENU hub with a `← MENU` back-link in `A1` of every sheet.
- Gridlines off; freeze panes below the header.
- The client's font throughout if they have a brand font; otherwise one neutral sans-serif.
- A one-sentence subtitle under every tab title saying what the sheet is and where the data came from,
  **including source, market and date** (e.g. "Organic rankings export, US database, pulled
  [MONTH YEAR]"). Never ship a tab whose provenance isn't on the tab.
