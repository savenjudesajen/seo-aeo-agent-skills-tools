# Page value and indexation check (phase 2, after pruning, before cannibalization)

Pruning compares pages with each other. This check asks a different question of each page on its own:
has it earned anything in search, and if not, what is it for? It catches pages that are old, indexable
and linked, but that Google never indexed or never shows.

Why it exists: sessions protect a page only after they are split by channel, because a total can be made
of direct, paid or unassigned visits with no search behind it. Index state needs its own check for the
same reason: a page can be live, linked and visited and still be absent from Google. Internal linking
should not aim search-term anchors at a page until this check has run.

## 1. Age gate

- Live 6 months or more decides. Younger pages are Wait with a recheck date.
- Age comes from the CMS item created date (or the collection's created date when the whole collection
  is new) and from the page list for static pages. Platform field names: `cms-reconciliation.md`.
- A collection that is itself new (recently launched as a whole) is too new to judge, even when most of
  its pages show under 100 impressions.

## 2. Search value

- Pull page-level impressions and clicks for the window from the Search Console bulk export
  (`data/sql/page_search_totals.sql`, anonymized queries included). A crawl's blank Search Console cell
  is missing data until this pull says it is zero.
- No search value: under 100 impressions and under 10 organic sessions in 6 months.
- Confirm index state with two checks together: URL Inspection and a `site:` search for the exact path.
  Neither is reliable alone. URL Inspection can call a page with many impressions "unknown to Google"
  when a trailing-slash or other variant was inspected.

## 3. Other value, by channel

Pull GA4 sessions per landing page split by default channel group
(`data/sql/ga4_sessions_by_channel.sql`).
- Counts as value: Organic Search, AI Assistant (or sessions whose source is chatgpt, perplexity, claude,
  gemini or copilot), key events, paid and email traffic (campaign use), referring domains to the exact
  URL, and a defined role (author profile, legal, careers, navigation).
- Does not count: Direct and Unassigned. They hold bots, untagged campaigns and internal visits, and on
  many sites Unassigned is a large share of all sessions.
- Check AI Assistant numbers before trusting them. Near-identical counts across unrelated low-traffic
  pages, paired with similar paid counts and nothing else, point to automated visits. Look at engagement
  time or engaged sessions before counting them.

## 4. Decide (by hand, row by row)

| What the page has | Decision |
|---|---|
| Campaign use (paid, email, sales links) or conversions, no search value | Keep live as a campaign page: noindex, remove from the sitemap, link to it only from CTAs and navigation, never with search-term anchors |
| AI Assistant visits or backlinks, no search value | Keep. Find why Google ignores it (thin page, shared template with a stronger page) and differentiate it or merge it |
| Repeats a stronger page's sections | Merge the unique parts into the stronger page and 301 (`merge-execution.md`) |
| Nothing on any channel | Return 410, or 301 to the closest live page when it has inlinks or backlinks |
| A defined role (author profile, legal) | Exempt from the search test. Decide index or noindex on the page's role |

Every row gets a Reason with the age, the 6-month impressions, the sessions by channel and the index
checks.

## 5. Output

Fill Live since and Age (months), which are already on the live sheet, and add these columns: Search
impressions (6 mo), Organic sessions, AI Assistant sessions, Campaign sessions, Index check, Value
decision. The rows this check
changes go into the merge candidates workbook only when the decision is a merge.

## 6. Run order

1. Run after pruning decisions are final and the redirect file is imported, on the cleaned URL list.
2. Pull page totals and GA4 channels for the same window.
3. Apply the age gate, then the search value test, then the channel test.
4. Run the `site:` check and read the live page for every page that fails search value.
5. Decide by hand, then hand the cleaned list to the cannibalization check.
