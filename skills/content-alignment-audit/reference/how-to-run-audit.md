# How to Run a Content Alignment Audit: Complete Walkthrough

Contents: Before you start · Phase 1: Data preparation · Phase 2: Semantic similarity · Phase 3: Content analysis · Phase 4: Apply the decision matrix · Phase 5: Build the report · Phase 6: Delivery and review · Implementation checklist · Monitoring after implementation · Common mistakes

This guide walks through a full audit with the six-strategy framework. The examples use a fictional
coffee-equipment blog on example.com with invented, round figures.

## Before you start

### What you need
1. **The site** (for example `https://example.com`) or the URL list in scope.
2. **Search Console page data** with URL, Impressions, Clicks, Position.
   - Export: Search Console → Performance → set the date range → Pages tab → Export; or pull it through
     your own Search Console connector.
   - Default range: the last 90 days.
3. **A crawler that produces page embeddings**, set up per `sf-ui-setup-guide.md`, or a page-text
   similarity method for pages without vectors.
4. **Time:** a few hours. Most of it goes into the crawl, clustering and scraping; recommendations and the
   report usually take 1–2 hours.

### Setup checklist
- [ ] Crawler connected, embeddings provider connected, embedding options on before the crawl
- [ ] Search Console export ready with the four columns
- [ ] robots.txt and any firewall allow the crawler
- [ ] Somewhere to write the output spreadsheet

## Phase 1: Data preparation

### Step 1: Load and validate the Search Console data

**Check:**
- Duplicate rows (aggregate URL × query exports to one row per URL)
- Every URL on the audited host (remove other properties)
- Impressions and Clicks numeric
- Rows missing Position (note them)

**Red flags:**
- More than 10% of rows without Position: a tracking gap, note it in the summary
- URLs from other hosts: remove them
- A single page with a huge impression outlier: check its queries; it may be ranking for something
  unrelated to its topic

**Output:** a clean, one-row-per-URL table.

### Step 2: Mark priority pages

- Sort by impressions descending
- Flag pages above the priority threshold (default > 1,000 impressions): audit priorities
- Flag pages ranking beyond position 20: refresh or reformat candidates
- Flag pages with CTR far below the norm for their position (for example position 5 with CTR under 1%):
  a title or snippet problem

As a rough guide, positions 1–3 often see CTRs in the high teens or more and positions 11–20 a few
percent; use the site's own curve when you have it.

**Output:** the sorted table with priority flags.

## Phase 2: Semantic similarity

### Step 3: Crawl

- Start a crawl of the site (or list mode with the URL list) with embeddings on
- Wait until the crawl and the embeddings API both reach 100%, then run crawl analysis
- Export: all internal URLs with title, H1, word count, indexability, internal inlinks and the embedding
  vector column; plus the semantically similar pairs

**Check:**
- Pages crawled vs pages in the sitemap
- Pages with an embedding vector (should be nearly all indexable HTML pages; investigate gaps)
- Errors and blocked pages (note them)

**Troubleshooting:**
- The crawl runs too long: crawl from the sitemap or the URL list only
- No embeddings: check the provider connection and settings (see `screaming-frog-integration.md`), or
  compute similarity from page text
- Many blocked pages: check robots.txt and firewall rules for the crawler's user agent

### Step 4: Cluster similar pages

**Bands (defaults):**
- **High duplication** (> 0.85): REDIRECT, RETIRE or REFRESH candidates
- **Moderate overlap** (0.70–0.84): REPURPOSE or REFORMAT candidates
- **Low similarity** (< 0.70): distinct content, usually REMAIN

**Algorithm:**
1. Sort pages by impressions descending (word count as a tie-break)
2. For each unclustered page, collect every unclustered page with similarity > 0.85 to it
3. Group them into a cluster; the first page is the leader; mark all as clustered
4. Repeat until every page is clustered or standalone

`../data/run_audit.py` implements this from a similarity-pairs CSV: the crawler's export, or the output
of `../data/similarity_pairs.py` when you need the 0.70–0.95 band or pages without a vector.

**Example output:**
```
cluster_1: 3 pages, leader /guides/cold-brew-ratio (1,500 impressions)
cluster_2: 2 pages, leader /guides/espresso-at-home (3,000 impressions)
cluster_3: 2 pages, leader /guides/choosing-a-burr-grinder (1,200 impressions)
standalone: 40 pages with no neighbour above 0.85
```

### Step 5: Join with Search Console

For each page record the cluster ID, similarity to the leader, performance vs the leader and the
impression ratio (page impressions / leader impressions).

**Example:**
```
URL:                /blog/cold-brew-ratio-tips
Cluster:            cluster_1
Cluster leader:     /guides/cold-brew-ratio
Similarity:         0.93
Impressions:        200      (leader 1,500; ratio 13%)
Position:           12       (leader 4)
```

## Phase 3: Content analysis

### Step 6: Choose pages to scrape

**Priority:**
1. Every page above the scrape threshold (default > 5,000): confirm nothing unique would be lost
2. Cluster members above 0.85 similarity to the leader: confirm they really are duplicates
3. Pages in the 0.70–0.84 band: decide whether REPURPOSE is viable
4. Pages ranking 8–20 with unique-content potential: find refresh or reformat opportunities

Batch the scrape by cluster. Most audits need tens of pages scraped, not the whole site.

### Step 7: Scrape and analyse

**Capture per page:** H1, the first 150 words, subsection topics, unique content signals, internal links,
structure quality, word count.

**Unique value-adds:**
- examples or case studies not on similar pages
- original research, data or statistics
- a proprietary method or framework
- a different audience level (beginner vs advanced)
- a different use case or segment (home vs office, small business vs enterprise)

**Quality issues:**
- thin content (under about 500 words for the topic's depth)
- poor heading structure
- broken links
- outdated information
- missing or mismatched structured data

**Example:**
```
Page A (/guides/cold-brew-ratio)
- H1: "Cold Brew Ratio: How Much Coffee per Litre"
- Length: about 1,800 words
- Unique: ratio table by strength, a dilution calculator, three worked examples
- Quality: clear H2s, links to grinder and filter guides

Page B (/blog/cold-brew-ratio-tips)
- H1: "Cold Brew Ratio Tips"
- Length: about 1,200 words
- Unique: none; same ratios and examples in a shorter form
- Quality: mirrors Page A's structure

Similarity 0.93; the scrape confirms B is redundant -> REDIRECT B to A
```

**Measure the value-add** of each compared page as in `decision-matrix.md`: unique H2/H3 sections and
their words over all words. Page B above scores 0.00 (0 of 5 sections, 0 of 1,200 words).

**Output:** scrape findings per page with a measured value-add and the count behind it.

## Phase 4: Apply the decision matrix

### Step 8: Recommend

1. Find the first strategy whose conditions all hold (`decision-matrix.md`)
2. Set confidence: HIGH (all criteria clearly met), MEDIUM (most met, interpretation needed), LOW (unclear
   or several strategies viable; flag)
3. Write the rationale with the specific data points

**Simplified flow:**
```
Similarity > 0.90?
  YES -> cluster leader?  YES -> REMAIN
                          NO  -> unique content? YES -> REPURPOSE (or REFRESH the leader with it)
                                                 NO  -> REDIRECT (RETIRE if traffic and links are near zero)
  NO  -> similarity 0.70-0.89?
           YES -> unique content? YES -> REPURPOSE, or REFORMAT if both pages should stay in different formats
                                  NO  -> REDIRECT or REFRESH (depends on which page ranks better)
           NO  -> check structure and ranking:
                    poor structure      -> REFORMAT
                    good content, dated -> REFRESH
                    performing          -> REMAIN
```

**Example recommendations:**

| Page | Similarity | Impressions | Position | Decision | Confidence | Why |
|------|-----------|-------------|----------|----------|-----------|-----|
| /blog/cold-brew-ratio-tips | 0.93 | 200 | 12 | REDIRECT to /guides/cold-brew-ratio | HIGH | High similarity, low volume, nothing unique, leader ranks 8 places better |
| /blog/what-is-pour-over | 0.76 | 2,000 | 11 | REPURPOSE as a beginner explainer | MEDIUM | Distinct intent, some unique content, needs a rewrite brief |
| /guides/descaling-your-machine | 0.40 | 4,000 | 5 | REFRESH (update dated steps and products) | HIGH | Ranks well, evergreen, facts out of date |
| /blog/grinder-list-old | 0.94 | 30 | 40 | RETIRE (410) | HIGH | Near-duplicate of the grinder guide, almost no impressions, no backlinks |
| /guides/cold-brew-ratio | 0.93 | 1,500 | 4 | REMAIN | HIGH | Cluster leader performing well |

### Step 9: Flag uncertain cases

**Mark LOW and flag when:**
- similarity sits in an ambiguous band (0.88–0.92) without clear differentiation
- scrape data is missing or incomplete
- a page above the scrape threshold would change substantially
- the page has external backlinks and would be redirected or retired
- several strategies are equally valid

For flagged rows, give all the research and let the user decide. Don't flag rows whose criteria are
clearly met.

## Phase 5: Build the report

### Step 10: Output spreadsheet

Use `../data/audit_output_template.csv`. Columns:
- URL, Impressions, Clicks, Position
- Cluster_ID, Cluster_Leader (TRUE/FALSE), Similarity_Score (a leader's highest score to a cluster member;
  a standalone page's nearest neighbour)
- Value_Add (0–1, measured; N/A where there is no comparison)
- Strategy (REDIRECT, REPURPOSE, REFORMAT, REFRESH, RETIRE, REMAIN)
- Confidence (HIGH, MEDIUM, LOW)
- Rationale (1–2 sentences)
- Unique_Content (YES, NO, PARTIAL)
- Scrape_Summary (key content findings)
- GSC_Performance (how the page performs vs its leader)
- Research_Notes (alternatives considered, edge cases)
- Action_Required (TRUE/FALSE: manual review or implementation needed)
- Effort_Level (Zero, Very Low, Low, Low-Medium, Medium, Medium-High)

**Sort:** Cluster_ID, then impressions descending (leaders first), then Action_Required TRUE first.

**Example rows:**
```
URL,Impressions,Clicks,Position,Cluster_ID,Cluster_Leader,Similarity_Score,Value_Add,Strategy,Confidence,Rationale,...
https://example.com/guides/cold-brew-ratio,1500,90,4,cluster_1,TRUE,0.93,N/A,REMAIN,HIGH,Cluster leader performing well,...
https://example.com/blog/cold-brew-ratio-tips,200,4,12,cluster_1,FALSE,0.93,0.00,REDIRECT,HIGH,Near-duplicate of the leader with lower volume,...
https://example.com/blog/what-is-pour-over,2000,60,11,standalone,FALSE,0.76,0.40,REPURPOSE,MEDIUM,Distinct beginner intent; rewrite as an explainer,...
```

### Step 11: Evidence per strategy

**REDIRECT:** which sections overlap, Search Console comparison (impressions, clicks, position, CTR),
scrape confirmation that nothing unique remains, backlink check, note that a 301 can be reversed if the
target suffers.

**REPURPOSE:** the unique content found, rewrite guidance (what to change, what to keep), the target
audience or intent after the rewrite, effort.

**REFRESH:** what is outdated (statistics, examples, references), what is absorbed from a sibling, effort
(often 1–3 hours), expected effect (fresher snippet, CTR change after 2–4 weeks).

**REFORMAT:** the specific structure problems, structured data to add, internal linking opportunities,
effort (often 1–2 hours).

**RETIRE:** similarity to the leader, Search Console figures confirming negligible traffic, backlink status,
implementation (410 or 301).

**REMAIN:** why it stays (leader, unique content, performance).

## Phase 6: Delivery and review

### Step 12: Deliver

1. The audit spreadsheet with tabs: main audit, summary, flagged items
2. A summary: pages analysed, clusters found, counts by strategy, high-confidence actions ready now,
   flagged items needing input, thresholds and assumptions used
3. Run `../data/verify_audit_output.py` on the main tab first; fix anything it reports

### Step 13: Support the decision

- The user reads the summary, reviews HIGH-confidence rows (usually actionable now), then decides the
  flagged rows from the research
- Suggest an order: high-confidence REDIRECT and RETIRE, then REPURPOSE, then REFRESH and REFORMAT
- Point out the gotchas: backlinks, consolidations above the consolidation threshold, strategically
  important pages
- Offer to track the targets in Search Console after implementation

## Implementation checklist

### Now (HIGH confidence, low effort)
- [ ] REDIRECT low-volume duplicates
- [ ] RETIRE pages with negligible impressions and no links
- [ ] REFRESH dated evergreen pages

### Next (HIGH or MEDIUM confidence, more effort)
- [ ] REPURPOSE pages with unique content
- [ ] REFORMAT poorly structured pages

### Review first
- [ ] Flagged REDIRECT and REPURPOSE decisions
- [ ] Pages with external backlinks (redirect planning)
- [ ] High-impression consolidations (merge planning)

## Monitoring after implementation

- Allow 1–2 weeks for recrawling; full effect often shows over 2–4 weeks
- Watch target pages for drops (there should be none if the merge kept the unique content)
- Make sure every redirect points straight at the final URL; update internal links to it
- Success: targets hold or gain position, target impressions approach the sum of the merged pages, CTR
  improves, no new 404s

## Common mistakes

1. **Redirecting without a backlink check.** If the source has external links, use a 301; deleting loses
   the equity.
2. **Merging high-volume pages without a scrape.** Above the consolidation threshold, scrape both pages
   and confirm unique content is kept.
3. **Shipping every redirect at once.** Batch them in groups of 5–10 and check before the next batch.
4. **Skipping REPURPOSE.** Pages in the 0.75–0.85 band with unique content often deliver more as rewrites
   than as redirects.
5. **Flagging too much.** If the criteria are clearly met, decide.
6. **Leaving internal links on redirected URLs.** They create chains; repoint them to the final URL.
