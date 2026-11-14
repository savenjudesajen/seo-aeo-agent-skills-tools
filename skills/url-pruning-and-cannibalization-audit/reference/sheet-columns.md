# Sheet columns

## Live pages (200), one row per URL

URL, Group, Group size, Group type, Role in group, Folder, CMS state, Decision, Action, Target, Review,
Reason, Merge check, Indexable, Words, Inlinks, Clicks, Impressions, Avg Position, Sessions, Key Events,
Group top performer, Text similarity to top performer, Embedding similarity to top performer, Closest
Similar URL, Similarity, Live since, Age (months), Survivor URL, Survivor clicks, Survivor impressions,
Survivor position, Other URL (the page `data/cannibalization_pairs.py` pairs with this one), Shared
queries, Query overlap %, Cannibalization (High, Medium, Low, blank when no shared query), Source.

Decision: Remain, Redirect, Retire. Action: Keep as is, Keep noindex, Add noindex, Fix canonical, 301 to
sibling, 301 to target, Merge then 301, Return 410, Re-target, or a content fix named in plain words. Redirect and
Retire rows carry Review = Y. Role in group: Top performer for exactly one row per group.

## Redirects and non-200

URL, Status, Currently redirects to, Target status, Remove from CMS?, Redirect rule, Correct target, Safe
to remove the rule now?, Review, Reason, Internal inlinks, Impressions, Clicks, Sessions, Google index
state, CMS item, Source. Rules R1 to R8 are in `redirect-removal-rules.md`.

## Dynamic URL patterns, one row per pattern

Pattern, Example, URLs in crawl, What it is, Current state, Google and traffic evidence, Options and
their impact, Recommendation, How to do it, Review, Research basis, Source. Method in
`dynamic-url-patterns.md`.

## Phase 2 columns (added to the live sheet)

Search impressions (6 mo), Organic sessions, AI Assistant sessions, Campaign sessions, Index check (URL
Inspection and `site:` result), Value decision. The age gate reads Live since and Age (months), which
are already on the live sheet; fill any blanks there rather than adding new columns. Detail:
`page-value-and-indexation.md`.

## Cannibalization pairs workbook (phase 3)

If the client already tracks cannibalization in their own format, fill that and map these fields onto
it. Otherwise use this default, which the gate script reads. It is a flat table, one row per pair, so it
sorts and filters like any other sheet.

Sheets: Cannibalization pairs, Query evidence, Method. (The merge candidates workbook may carry the
Cannibalization pairs sheet too; the gate reads any sheet whose name starts with "Cannibalization" and
a sheet named Merge candidates, laid out as in `merge-execution.md` section 5.)

**Cannibalization pairs: one row per pair, header in row 1.**

| Column | What goes in it |
|---|---|
| Pair ID | P1, P2, ... (Query evidence rows point back to it) |
| Severity | High, Medium or Low, from the pair metrics |
| Owner URL, Owner type | The page that should own the shared queries, and its page type |
| Other URL, Other type | The competing page, and its page type |
| Top shared query | The shared query with the most impressions, with both positions |
| Shared queries, Query overlap %, Weekly swaps, Text similarity | From `data/cannibalization_pairs.py` and the similarity step |
| Owner clicks, Owner impressions, Other clicks, Other impressions | Search Console, same window |
| Results page shows | The page format Google ranks for the top shared query today (guide, list, vendor page, ...) |
| Resolution | Merge into owner, Re-target, Split anchors, Wait |
| Redirect target | Required for Merge into owner |
| Anchor split | Which wording links to which page; required for Re-target and Split anchors |
| Recheck date | Required for Wait |
| Reason | Top shared query, both positions, overlap, swaps, then the resolution |
| Source | Where each number came from |

**Page types** (labels you assign; the same list feeds `--page-types` in `data/cannibalization_pairs.py`):
Home, Offer (product, service, pricing), Campaign landing, Article, Guide, Short answer (FAQ or help),
Listing or hub, Profile, Other. Offer and Campaign landing are the buying types.

Example row (all values invented):

| Pair ID | Severity | Owner URL | Owner type | Other URL | Other type | Top shared query | Query overlap % | Weekly swaps | Resolution | Anchor split |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 | High | https://www.example.com/product/photo-editor | Offer | https://www.example.com/blog/what-is-a-photo-editor | Article | photo editor app (pos 7 vs 12) | 30% | 4 | Re-target | "photo editor app" links to the product page; "what a photo editor does" links to the article |

**Query evidence.** Every query behind a pair, one row per query and ranking URL, sorted by the query's
total impressions. Columns: Pair ID, Query, Ranking URL, Avg position, Impressions, Clicks, Source.

**Method.** Scope, window, query filter and brand pattern, the shared-query and severity definitions,
owner rule, page-type labels used, and related fixes found along the way (redirects pointing at hubs,
off-site copies).

Detail: `keyword-cannibalization.md`.

## Method (the only extra sheet in the audit workbook)

Scope, decision rules, similarity method and its validation numbers, live checks done, platform limits,
owner decisions for this site. Keep it short. Source column on every row of every sheet.
