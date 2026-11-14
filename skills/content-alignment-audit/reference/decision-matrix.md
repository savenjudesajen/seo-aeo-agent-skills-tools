# Decision Matrix: Content Alignment Strategies

Contents: Overview · Strategy 1: RETIRE (remove) · Strategy 2: REDIRECT (consolidate) · Strategy 3: REFRESH (update in place, absorbing overlap) · Strategy 4: REFORMAT (restructure, same URL) · Strategy 5: REPURPOSE (rewrite for a different angle) · Strategy 6: REMAIN (no action) · Confidence scoring · Decision tree (quick reference, first match wins)

## Overview

Each page gets one strategy. For a page in a cluster, compare it with the cluster leader (or with its
closest neighbour if it is standalone). Check the strategies in the order of the decision tree at the end;
the first one whose conditions all hold wins. All thresholds are defaults: scale impression thresholds to
the site and calibrate similarity bands on a few pairs read by eye.

**Inputs per page:** similarity to the compared page (0–1), value-add ratio (below), impressions per month,
average position, external backlinks, internal inlinks, and the scrape findings.

**Value-add ratio:** the share of a page's main content that the compared page does not have, 0–1, counted
from the two scrapes:

1. Split the page's main content (navigation, footer and boilerplate removed) into its H2/H3 sections. A
   page without subheadings is split into paragraphs.
2. Mark a section unique when its topic, examples, table, data points or tool has no counterpart anywhere
   on the compared page. A section that covers the same topic in other words is not unique.
3. Value-add = words in unique sections / words in all sections, rounded to two decimals.
4. Put the figure in the Value_Add column and the count behind it in Research_Notes (for example
   "Value-add: 2 of 6 H2 sections unique (milk steaming); 700 of 2000 words"), so a reviewer can re-check it.

0.10 means "almost everything here is also on the other page"; 0.60 means "most of this page is its own".
For a REFRESH or REFORMAT pair, measure both directions (each page against the other). A page with no
neighbour above 0.70 has no value-add comparison: write N/A.

The examples below use a fictional coffee-equipment blog on example.com with invented, round figures.
Impressions in the examples are 90-day totals, the same figures as `../data/audit_output_template.csv`;
divide by 3 for the per-month thresholds.

---

## Strategy 1: RETIRE (remove)

**When to use:**
- Similarity ≥ 0.92 (nearly identical)
- Value-add < 0.10
- Under 50 impressions a month
- No external backlinks (or very few), no internal links that matter
- No unique keyword target

**Example:**
- Source: `/blog/grinder-list-old` (30 impressions, about 10 a month, position 40)
- Compared page: `/guides/choosing-a-burr-grinder` (1,200 impressions, position 5)
- Similarity: 0.94; scrape finds nothing on the source that the guide lacks; no external backlinks
- Decision: RETIRE with a 410 (a 301 to the guide instead if a backlink turns up)

**Implementation:**
1. Return 410 Gone, or 301 to the closest page if there are any backlinks
2. Remove the URL from the sitemap
3. Remove or repoint internal links to it
4. Watch for new 404s for a week

**Risk factors:** losing ranking history (mitigated by a 301), breaking internal links if they were not
checked, external backlinks missed because only domain-level link data was used.

---

## Strategy 2: REDIRECT (consolidate)

**When to use:**
- Similarity ≥ 0.90
- Value-add of the source < 0.20
- The target performs better: more impressions and at least 2 positions better
- The target covers the same or a broader topic
- The source has no distinct point of view the site wants to keep

**Example:**
- Source: `/blog/cold-brew-ratio-tips` (200 impressions, position 12)
- Target: `/guides/cold-brew-ratio` (1,500 impressions, position 4)
- Similarity: 0.93
- Decision: REDIRECT the source to the target

**Implementation:**
1. 301 the source directly to the final target (no chains)
2. Repoint internal links to the target
3. Confirm the redirect is crawled within a few days and watch the target in Search Console for a few
   weeks
4. Check that no redirect chains or 404s appear

**Caveat:** if either page is above the consolidation threshold (default 10,000 impressions over the
export window), scrape both and move anything unique into the target before redirecting.

**Risk factors:** backlinks on the source (plan them), a temporary position dip during the transition,
302 used by mistake instead of 301.

---

## Strategy 3: REFRESH (update in place, absorbing overlap)

**When to use, case A (two overlapping pages, both useful):**
- Similarity ≥ 0.85
- Value-add 0.30–0.70 on both pages
- Combined traffic is meaningful (default > 100 impressions a month together)
- The same or equivalent queries, so one stronger page would serve them better than two
- The stronger page gets REFRESH; the weaker one gets REDIRECT to it

**When to use, case B (one dated page):**
- An evergreen page that ranks well but has outdated statistics, examples or screenshots
- The structure is fine; only the facts need updating

**Example (case A):**
- `/blog/espresso-basics` (1,000 impressions, position 11) and `/guides/espresso-at-home` (3,000
  impressions, position 6)
- Similarity: 0.87; each has a section the other lacks
- Decision: REFRESH `/guides/espresso-at-home` with the unique section from the blog post, then REDIRECT
  the blog post to it

**Implementation:**
1. Merge the unique content into the stronger page without diluting its focus
2. Update dated facts and examples, and the visible updated date
3. 301 the absorbed page (case A)
4. Watch position and CTR for 2–4 weeks

**Risk factors:** losing a niche angle in the merge, a muddled page if two intents are forced together.

---

## Strategy 4: REFORMAT (restructure, same URL)

**When to use, case A (one page):**
- On topic but poorly structured: broken heading hierarchy, thin sections, wall-of-text, missing
  structured data

**When to use, case B (two similar pages that should both stay):**
- Similarity 0.80–0.88 (same topic, different treatment)
- Value-add 0.40–0.70 on both
- Both get traffic (default > 50 impressions a month each)
- They can serve complementary needs, so users benefit from both

**Example (case B):**
- `/compare/burr-grinders-table` (450 impressions, position 9, quick reference)
- `/guides/choosing-a-burr-grinder` (1,200 impressions, position 5, long-form guide)
- Similarity: 0.83
- Decision: REFORMAT. Make the first a sortable comparison table, keep the second as the narrative guide,
  interlink them

**Implementation:**
1. Fix the heading hierarchy and expand or cut thin sections
2. Give each page of a pair a distinct format, depth or audience
3. Add structured data that matches the visible content
4. Interlink complementary pages

**Risk factors:** the pair keeps competing if the differentiation is weak; watch positions after the
change.

---

## Strategy 5: REPURPOSE (rewrite for a different angle)

**When to use:**
- Similarity 0.70–0.89 (similar, not identical)
- Value-add 0.20–0.60, or a clearly different intent (awareness vs decision, beginner vs advanced)
- The page has its own angle, framework or examples worth building on
- Query overlap with the compared page under about 30% in Search Console

**Example:**
- Source: `/blog/what-is-pour-over` (2,000 impressions, position 11, explainer)
- Compared page: `/guides/pour-over-step-by-step` (5,000 impressions, position 4, how-to)
- Similarity: 0.76
- Decision: REPURPOSE the source as a "pour-over for beginners: what you need and why" page, linking to the
  step-by-step guide

**Implementation:**
1. Rewrite for the new angle at the same URL (keeps its history)
2. Add a new introduction and examples specific to the new audience
3. Interlink the two pages
4. Give the writer specific guidance: what to keep, what to cut, the new target intent

**Risk factors:** cannibalization if the differentiation is weak; needs a writer's time; check query
overlap first.

---

## Strategy 6: REMAIN (no action)

**When to use (any of):**
- The page leads its cluster and performs well
- Similarity < 0.70 to every other page
- Value-add > 0.60
- Strong performance: solid impressions for the site (default > 500 a month) and position 1–5
- It serves a distinct purpose in the user journey

**Example:**
- `/guides/coffee-for-offices` (4,000 impressions, position 6)
- Unique: buying advice and maintenance schedules for shared machines
- Decision: REMAIN, a distinct segment

**Implementation:** none. Re-check at the next audit.

---

## Confidence scoring

### HIGH
- Every condition clearly met, supporting data strong, few risk factors
- Safe to implement now

Examples: REDIRECT at 0.92 similarity, value-add under 0.15 and a 3x traffic gap; RETIRE at 0.93 with
under 50 impressions and no backlinks; REMAIN under 0.70 similarity or above 0.60 value-add.

### MEDIUM
- Most conditions met, some uncertainty in execution
- Review before implementing; may need the content team

Examples: REPURPOSE at 0.81 with 0.45 value-add, pending a differentiation check; REFRESH at 0.86 where
the merge needs editing; REFORMAT at 0.82 where format differentiation is possible but not certain.

### LOW
- Marginal fit, conflicting signals, or two strategies equally valid
- Flag for manual review with the full research; the user decides

Examples: REDIRECT at 0.88 (below the 0.90 threshold); REFRESH with borderline traffic; any strategy
where the value-add is unclear.

Write the label (HIGH, MEDIUM, LOW) in the sheet. Confidence is a judgement on how clearly the conditions
hold, not a computed score.

---

## Decision tree (quick reference, first match wins)

```
Similarity >= 0.92 AND value-add < 0.10 AND < 50 impressions/month AND no backlinks
  -> RETIRE

Similarity >= 0.90 AND value-add < 0.20 AND target better (more impressions, >= 2 positions better)
  -> REDIRECT

Similarity >= 0.85 AND value-add 0.30-0.70 on both AND combined traffic meaningful
  -> stronger page: REFRESH, weaker page: REDIRECT to it

Similarity 0.80-0.88 AND both get traffic AND a different format is possible
  -> REFORMAT

Similarity 0.70-0.89 AND (value-add 0.20-0.60 OR different intent) AND query overlap < 30%
  -> REPURPOSE

Standalone page, dated facts, good rank          -> REFRESH
Standalone page, poor structure                  -> REFORMAT
Similarity < 0.70 OR value-add > 0.60 OR leader OR strong performer
  -> REMAIN
```
