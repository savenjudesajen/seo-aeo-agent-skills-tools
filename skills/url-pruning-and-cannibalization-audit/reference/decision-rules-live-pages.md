# Decision rules for live 200 pages

Write each reason from the row's own evidence: impressions, clicks, position, sessions, inlinks, words,
indexability, Google's index state, group and top performer. Impressions weigh as much as clicks. One to
three sentences, numbers first, no em dashes, no "X, not Y" constructions.

## Order of judgement

1. Performance (Search Console and GA4): good results stay, poor results go.
2. Similarity: group by topic; the best performer for that exact topic is the target for weaker twins.
3. Live confirmation of the same topic before a Redirect.
4. Carry-over flag (Merge check) before any 301.
5. Page value (phase 2): an indexable page live 6 months or more with under 100 impressions and under 10
   organic sessions is decided by its other channels (`page-value-and-indexation.md`).
6. Query cannibalization (phase 3): shared queries with a stronger page decide between merge, re-target
   and keep (`keyword-cannibalization.md`).

Sessions count as demand only when split by channel: organic search, AI assistants, campaigns (paid,
email) and key events count; Direct and Unassigned do not.
A standing owner rule (for example "keep only pages with 1 click or 100 impressions") sits in step 1 for
that collection and is recorded in the Method sheet.

## Remain

- Keep as is: has a distinct job. Demand alone is not enough when a stronger page covers the same intent
  at 0.90 or higher similarity; the Reason then names the distinct job and the survivor's numbers.
  Template overlap across different subjects is not duplication.
- Wait (recheck date): the page is under 6 months old and passes the other merge tests. Decision =
  Remain, Reason gives the recheck date.
- Keep noindex: already noindex and useful for navigation. If Google still lists it, say it should drop
  out and recheck.
- Add noindex: useful to users, no search value, indexable today.
- Keep as campaign page (noindex): no search value but paid, email or sales traffic, or conversions.
  Remove it from the sitemap and link to it only from CTAs and navigation, never with search-term anchors.
- Fix canonical: indexable duplicate or variant with a wrong or missing canonical.
- Fix content (named): the page earns demand but holds placeholder or cloned copy.
- Re-target: the page shares queries with a stronger page (the owner) at below 0.80 similarity. Name
  the shared query to remove from its title, H1 and leading H2s, and the anchor link to add to the
  owner. A blog post that outranks a product or service page on a commercial query gets this action,
  never a redirect of the money page.

## Redirect

- Merge then 301: two pages on one task where each holds something the other lacks. Name it.
- Absorber test: live 6 months or more, similarity 0.90 or higher to a stronger same-intent page, same
  intent confirmed on the live page, and cannibalization severity Medium or High against the survivor
  (query overlap 10 percent or more, or a contested query with 100+ impressions). Never merge on clicks
  alone. The survivor can be a hub or pillar page in another folder.
- Duplicate body: a page whose body duplicates a stronger page is a Redirect to it. Fix duplicate body
  applies only when no stronger page exists.
- 301 to sibling or target: duplicates a stronger same-topic page. The target is a live 200 indexable
  page, never the homepage or a generic hub when a same-topic page exists.

## Retire

- 301 to the closest live page, or the collection hub when none shares the task.
- Return 410 when no match exists and the page has no demand, inlinks or backlinks.
- Never retire a page with real impressions without Review = Y and a named target.

## Review flag

Review = Y on every Redirect and Retire row, on rows whose target is outside the crawl, where evidence
conflicts (traffic with zero impressions), where the Merge check finds an unmatched section, and on every
High cannibalization row.

## Libraries of repeated pages

Decide by task. Keep the performing page for each task, send non-performing variants to it, and flag a
whole library with no impressions for an owner decision after checking the Search Console page indexing
report (Google may never have indexed it).
