# Redirect and error URLs: should they come out of the CMS?

The action on this sheet is a flag for removal from the CMS. A human decides. Each row says: remove the
CMS item or not, keep or drop the 301 rule, the correct target, and whether dropping the rule is safe.

## Rules

- **R1.** Many CMSs keep redirect rules separate from CMS items (hosting settings, a redirect plugin, the
  server config). Deleting an item with no rule returns 404. Removing the item and keeping the rule are
  two decisions. Platform specifics: `cms-reconciliation.md`.
- **R2.** Keep a 301 in place for at least a year so Google processes the change several times
  (Google Search Central, "site moves with URL changes": keep redirects as long as possible, generally
  at least a year). Redirect age is unknown from a crawl, so any rule with demand or index presence stays.
- **R3.** A rule is a drop candidate only when impressions, clicks, sessions and internal inlinks are all
  zero, Google does not show the source as indexed, and the target is sound. Check per-URL backlinks in a
  backlink tool's per-page export first. Until that is done no row is marked safe.
- **R4.** Repoint internal links to the final target before anything is removed.
- **R5.** If Google still shows the source as indexed, it has not processed the redirect. Keep the rule.
- **R6.** A redirect with demand and a weak target (blog index, homepage, unrelated page, chain, noindex
  page) gets a better target. Action: Fix target.
- **R7.** 404 or 401 sources with demand and a relevant live page get a new 301. Without demand they stay
  404 or return 410.
- **R8.** No blanket redirects to the homepage. Google treats irrelevant redirects as soft 404s. The gate
  script warns on any Keep 301 row that lands on the homepage.

## Action vocabulary

Keep 301, Fix target, Set up 301, Leave 404, Return 410, Candidate to drop (only after the backlink
check), Leave as is.

## Check each target

Target status, target indexability, and whether the target itself redirects (chain). A list-mode crawl of
all targets settles this in minutes.

## Removal column

"Yes: delete the CMS item", "Yes: delete the CMS item (already Draft)", "Nothing to delete (no CMS item)",
or a note when the item is published but its public URL 404s because no collection page is live.

## Sanity check on the result

Most rows should be Keep 301 or Fix target. Candidate to drop should be rare and only after the backlink
check. A sheet where most rows are "drop" has skipped R2 or R3.
