# Reconciling the CMS with the crawl

A crawl finds only linked pages. The CMS knows every item, including orphans, drafts that are still live
and programmatic collections nobody links to. Use the CMS API, an export, or the CMS's MCP server if one
is connected (read its guide tool first, if it has one).

## Steps (any CMS)

1. List every content type or collection, and every static page.
2. Page through every collection's items: id, slug, title, state (published, draft, archived or
   trashed), created date, last-published date. Save to a CSV outside the chat (results are large) and
   parse the saved file with Python.
3. Check that each collection has a public template or route. A collection whose template is unpublished
   has no public pages, and its items return 404 even when published.
4. Build each item's public URL from the collection's real URL prefix (it can differ from the collection
   name) and the item slug.
5. Diff against the crawl. For each item record: crawl status, CMS state, and whether the crawl reached
   it.
6. Write the missing published URLs to a list file and crawl them in List mode with all APIs connected.

## What to expect

- Items flagged Draft that are still live, published items that now 301, and published pages the crawl
  never reached (programmatic collections are the usual gap). Report each count in the Method sheet.
- Collections with unpublished templates have no live pages; their item URLs return 404.
- Very large collections outside the crawl: say they were not checked rather than assuming.

## Limits to state in the Method sheet (any CMS)

- Where the redirect rules live (hosting settings, a plugin, the web server or CDN) and whether the API
  can read them. If it cannot, ask the human to confirm a rule exists before any CMS item is deleted.
- Deleting a CMS item with no rule returns 404. The item deletion and the rule are separate actions.
- The CMS state seen at crawl time. Record it per row.

## Platform notes: Webflow

- On most plans the API cannot read or edit 301 redirect rules or robots.txt; redirects live in the
  site's hosting settings, and importing a redirect file replaces the whole list (import base rules plus
  changes).
- A redirect is rejected when its source path still has a published static page: set that page to
  draft and publish first.
- An item can show as Draft while its page is still live until the next publish, and an updated item
  stays staged until a separate publish. Check for someone else's staged edits before publishing a merge
  survivor, and diff the stored body against the intended one.
- Ages: the item's created date (the collection's own created date when the whole collection is new).

## Platform notes: WordPress

- The REST API lists posts, pages and public custom post types (`/wp-json/wp/v2/<type>?per_page=100&page=N`,
  with `status`, `date` and `modified`). Drafts and private items need an authenticated request.
- Redirects usually live in a plugin or the server config, not in core. Find out which before deleting
  anything, and export its rule list.
- noindex and canonical settings usually come from an SEO plugin; read them from the rendered page, not
  from the post record.
- Trashed posts return 404 unless a rule exists.

## Other platforms

Use the platform's export or API for the item list, find where redirect rules live, and record the same
limits in Method. When no item list is available, use the XML sitemap and say the reconciliation is
partial.
