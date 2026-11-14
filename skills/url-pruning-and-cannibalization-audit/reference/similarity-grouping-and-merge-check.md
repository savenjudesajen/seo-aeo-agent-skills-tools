# Similarity, grouping and the carry-over check

Contents: 1. Coverage before anything else · 2. Page text similarity (for pages without vectors, and as a cross-check) · 3. Grouping · 4. Confirm on the live pages · 5. Carry-over check (flag only) · 6. Redirect direction · 7. Cluster map (visual, delivered as an HTML file) · 8. Merge decision framework (absorber test)

## 1. Coverage before anything else

Count, for the live pages: pages with an embedding vector (the embeddings column in the crawler's
Internal export), pages with page text (the visible-text export), and pages with a Semantic Similarity
Score filled. The score column is filled only for pages whose nearest neighbour passes the threshold, so
a blank is not evidence of "no similar page". Pages added from a list crawl often have no vectors.
Gate: every live page has similarity from vectors or from text, and the sheet says which.

## 2. Page text similarity (for pages without vectors, and as a cross-check)

- Strip boilerplate: lines that appear on 4 percent or more of pages (menus, footers, banners).
- TF-IDF with sublinear tf, English stop words, unigrams and bigrams, `min_df=2`, `max_df=0.5`; cosine on
  the matrix (`data/similarity_groups.py`).
- Validate on pages that have both scores: Pearson/Spearman correlation, top-5 neighbour overlap against
  chance, and the share of text pairs at 0.30+ that the embedding model also scores high. Report the
  numbers in the Method sheet. A lexical score misses topical links that share no wording, so say so.
- **Matching the crawler's numbers.** Export the embedding vectors, then take plain cosine similarity
  between two pages' vectors (dot product divided by the product of the lengths). On pages that have
  both a vector and a Semantic Similarity Score this should reproduce the crawler's score to rounding;
  check it on your own pages and report the mean and maximum difference. Then use it to score any pair
  locally, including pairs the crawler does not list.
- **Known gap.** The nearest neighbour the crawler lists for a page does not always equal the nearest
  vector by plain cosine; on some sites they disagree on a sizeable minority of pages, for reasons the
  crawler does not document. Report the agreement rate in Method and treat the listed neighbour as a
  hint, not as the ranking.
- Vectors cover only the pages the AI provider embedded; the rest use the text method above. Say which
  method scored each row.

## 3. Grouping

- Average-linkage agglomerative clustering on 1 minus text cosine, cut at similarity 0.30 (this tends to
  give groups of real topics and template families; around 0.25 chains unrelated pages, around 0.40
  splits true twins). Tune on a sample and record the cut in Method.
- Merge clusters that contain pages with the same task name when a library repeats one task across
  variants (one page per platform, city or integration whose titles differ only in that word): strip the
  variant and filler words from the slug and union equal keys.
- Group type: Near-duplicate when the mean pairwise similarity in the group is 0.70 or more; Same-topic
  overlap (reviewed) when a reviewed redirect sits inside it; Same-topic overlap (variants) for repeated
  tasks; otherwise Template family. A maximum-pair test labels a whole template family a duplicate: use
  the mean.
- Top performer: most clicks, then impressions, then sessions. It is a display field. The redirect target
  is the same-topic twin, which can differ from the top performer in a cluster spanning several topics.
- Order the sheet by group (groups by total impressions), top performer first, then ungrouped rows.

## 4. Confirm on the live pages

For every proposed Redirect pair read both pages (title, H1, H2 list). Same task passes. A different
angle (a news item against an evergreen guide, a review against a sales page) does not: keep the page or retire it to the
hub. Check a sample of Template family and Near-duplicate groups and of ungrouped pages with a
same-folder near-title.

## 5. Carry-over check (flag only)

For every row that redirects to a live page, compare sections, not lines (page text arrives
hard-wrapped):
- Extract H2/H3 sections with their body text from the stored raw HTML. Drop headings that appear on 8 or
  more pages (template blocks).
- Strip variant and filler words, TF-IDF the section text, and for each section of 60+ words take its
  best cosine to the target's sections. Below 0.30 is a section with no close match.
- Write the result in the Merge check column: how many sections have no match and the three largest by
  name. Set Review = Y when any exist. A person decides what moves before the 301.
- Expect false positives when the same advice is worded differently; the list is for review, not for
  deletion.

## 6. Redirect direction

Send the weaker page to the stronger one on the same topic. Where sessions on the source far exceed the
target (several times as many), say so in the Reason with both counts: it signals a traffic source
(internal links, ads, email) that needs checking before the 301.

## 7. Cluster map (visual, delivered as an HTML file)

The workbook stays at three sheets plus Method, so the map ships as a separate self-contained HTML file
the user opens in a browser. The crawler's own cluster diagram exports only as a viewport SVG with no
per-URL data, so this map is built from the audit table.
- Build: `python data/cluster_map.py pages.ndjson table.tsv out.html --title "Site" --note "..."` (needs
  numpy and scikit-learn). Inputs: page text (visible-text export as NDJSON with Address and content) and
  a TSV of the live-sheet columns listed in the script docstring.
- Layout: boilerplate-stripped TF-IDF, SVD to 50 dimensions, t-SNE to 2D. This is a text-based layout of
  the same family as the crawler's diagram (which runs t-SNE on embeddings), so cluster shapes will not
  match its picture. Say so in the hand-off.
- Encoding: colour is the decision, capped at three categorical series; dot size follows impressions.
  Hover shows decision, target, group, clicks, impressions, sessions. Click pins a page, rings its group
  and lists the members. Filters: search, folder, group type, decision.
- Test it before sending: open it in a headless browser, hover a dot, confirm the tooltip fills and the
  legend checkboxes render at normal size.

## 8. Merge decision framework (absorber test)

Inputs per page: first-published date (a CMS custom date field, then the created date), similarity to the
survivor, 12-month clicks, impressions, CTR, average position, inlinks, and the cannibalization metrics
against the survivor (shared queries, query overlap %, rotation, severity) from
`keyword-cannibalization.md`.
- Survivor: most clicks, then impressions, best position, most inlinks; equal or broader scope. A hub or
  pillar page in another folder can be the survivor.
- Survivor intent check: search the merged page's head term and see which page format Google shows. If it
  shows a sibling's format (for example a checklist page where you planned to merge into a long-form
  explainer), the sibling is the better survivor; otherwise Google can move the head term to that sibling
  after the merge. After every merge, recheck the head term after four weeks.
- Merge (Redirect, Review = Y): live 6 months or more, similarity 0.90 or higher, same intent confirmed
  on the live page, and cannibalization severity Medium or High against the survivor (query overlap 10
  percent or more, or a contested query with 100+ impressions). With no query x page data, stop and flag
  it; do not merge on clicks alone.
- Review band 0.80 to 0.89: an intent read decides.
- Keep separate: different intent, a top-3 position on queries the survivor lacks, or sections worth
  carrying that the survivor lacks. Similarity 0.90 or higher with Low cannibalization leans Keep
  separate: Google already treats the pages as different jobs.
- Below 0.80 similarity with High or Medium cannibalization is not a merge. Re-target the other
  page, unless 80 percent or more of its impressions sit on shared queries and the live read
  shows no job of its own.
- Wait: under 6 months old. Decision = Remain with a recheck date. Twins published within days of each
  other on one topic skip the wait.
- Click yield alone does not separate pages: near-identical posts usually show similarly low CTR.
  Similarity, query overlap and a clear survivor decide.
- Excluded by rule: families with one page per place, person, product line or release (location pages,
  author pages, category pages, release notes) are template families by default.
- Delivery: a Merge candidates list with Page, Survivor, Decision, Live since, Age, Similarity, Shared
  queries, Query overlap %, Cannibalization, page and survivor metrics side by side, Reason, Source, then
  Outcome and Outcome note after the intent read. Format and the merge steps: `merge-execution.md`.
