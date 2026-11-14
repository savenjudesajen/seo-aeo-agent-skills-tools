# Drupal implementation reference (Drupal 9/10/11 with the Metatag module)

Contents: Permissions and login · Finding a node ID from a page URL · The field names (Metatag module) · The safe save method (never blind-POST a node form) · Verify every row on the live page (cache-busted) · Multilingual · Track progress

How to apply on-page SEO fixes to Drupal nodes fast and without wiping content. Selectors below are
Drupal core and Metatag defaults; confirm them on the first edit of a new site, because field machine
names are chosen per site.

## Permissions and login

- The **user logs in themselves**. Never enter credentials.
- An editor role often **can edit nodes but cannot open `/admin/content`** (it returns 403). Don't
  treat that 403 as "no access": test the path you actually need.

```js
// logged-in check + node-edit access, same-origin, ends on a top-level await
async function can(nid){
  const r = await fetch('/node/' + nid + '/edit', {credentials: 'include', redirect: 'follow'});
  return 'status=' + r.status + ' final=' + r.url.replace(location.origin, '');
}
await can(101)   // 200 and final=/node/101/edit  => you can edit
```

On multilingual sites, prefix the language (`/<lang>/node/101/edit`) when editing a translation.

## Finding a node ID from a page URL

The shortlink `<link rel="shortlink">` is often absent from the server HTML. The reliable source is
`drupalSettings.path.currentPath` embedded in the page:

```js
async function nid(path){
  const html = await fetch(path, {credentials: 'include'}).then(r => r.text());
  const cp = (html.match(/"currentPath":"([^"]+)"/) || [])[1] || '';  // e.g. node\/101
  const m = cp.match(/node\\?\/(\d+)/);
  return m ? m[1] : 'NOT-FOUND';
}
await nid('/products/widget-pro')   // e.g. "101"
```

On a page already open in the tab you can also read
`document.querySelector('[data-history-node-id]')?.dataset.historyNodeId`.

## The field names (Metatag module)

| What | Typical form field name |
|---|---|
| Meta description | `field_metatags[0][basic][description]` (a `<textarea>`) |
| Meta title (the rendered `<title>`) | `field_metatags[0][basic][title]` |
| Meta keywords (if enabled) | `field_metatags[0][basic][keywords]` |
| Canonical URL | `field_metatags[0][advanced][canonical_url]` |
| Robots | `field_metatags[0][advanced][robots]...` (checkboxes) |
| Node title (admin label, often also the H1) | `title[0][value]` |

Replace `field_metatags` with the site's own field machine name if it differs (inspect the form once).

**Critical:** the rendered `<title>` and `<meta name="description">` come from the **Metatag fields**,
not from `title[0][value]`. The node title is the internal label (and, in most themes, the H1). To fix
a page's title tag, edit the Metatag title, not the node title. To fix the H1, edit the node title
(or the theme field that renders the headline, if the theme uses a separate one).

**"Missing" metas are usually a token that resolves to nothing.** Metatag's default description is
often a token such as `[node:summary]`. The field isn't blank; it resolves to an empty string when the
node has no summary, which is why the crawler reports "missing". Replacing the token with a static,
purpose-written description on that node is the correct fix. If hundreds of nodes share the problem,
also suggest the developer change the default pattern for that content type.

## The safe save method (never blind-POST a node form)

Node forms built with Paragraphs and CKEditor hold the body content in JS-managed widgets, not in the
raw `<textarea>` values. Fetching the form HTML and re-posting its fields **submits empty body fields
and wipes the page**. Use that shortcut only for simple admin forms (redirects, URL aliases), never for
content nodes.

Safe method: edit the real rendered form and click the real Save.

```js
// 1) navigate first to /node/<id>/edit, then run this on that page:
(function(){
  if (!location.pathname.endsWith('/node/<id>/edit')) return 'WRONG PAGE';
  const ta = document.querySelector('textarea[name="field_metatags[0][basic][description]"]');
  if (!ta) return 'NO FIELD';
  // readiness guard: the body editors must have rendered before you save
  if (!document.querySelector('.ck-editor, [data-drupal-selector*="paragraph"]')) return 'FORM NOT READY';
  const META = "<the exact meta text>";
  ta.value = META;
  ta.dispatchEvent(new Event('input', {bubbles: true}));
  ta.dispatchEvent(new Event('change', {bubbles: true}));
  if (ta.value !== META) return 'SET FAILED';
  document.querySelector('#edit-submit').click();   // the real Save; editors sync on submit
  return 'saved';
})()
```

The Save button is usually `#edit-submit` (check for a moderation-state select next to it: if the site
uses Content Moderation, set the state the user wants, e.g. Published, or the save creates a draft).
For the very first row of a run, split set and save into two calls (set, then save) to give the
editors a moment to initialise. Once verified, set and save in one call is fine, always behind the
readiness guard so you never save an unrendered form.

## Verify every row on the live page (cache-busted)

```js
async function verify(path, expectPrefix){
  const html = await fetch(path + '?cb=' + Date.now(), {credentials: 'include'}).then(r => r.text());
  const md = (html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)["']/i) || [])[1] || '(none)';
  const h1 = (html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i) || ['', ''])[1].replace(/<[^>]+>/g, '').trim();
  return {ok: md.startsWith(expectPrefix), meta: md.slice(0, 90), h1: h1.slice(0, 60), kb: Math.round(html.length / 1024)};
}
```

Record each page's `kb` **before** the first edit. `ok: true` means the field is set; a `kb` close to
the pre-edit size plus an intact `h1` means the body survived. If `kb` collapses, you wiped content:
stop and restore the previous revision from the node's Revisions tab.

Logged-in fetches can bypass the page cache while anonymous visitors still see the cached page. If the
user needs the change visible to everyone immediately, ask whether to clear the cache (or have the
developer purge the CDN) rather than doing it yourself.

## Multilingual

Default-language pages first. For other languages, the title and meta are a **localisation task**:
flag them for the localisation team or draft localised copy with sample approval; don't silently
machine-translate. Field names are the same in every language; each translation is edited at its own
language-prefixed `/<lang>/node/<id>/edit`.

## Track progress

Keep a sheet `URL | node ID | field | new value | status (DONE / FAILED + why)`. Update it per row. If
the session drops, resume from the sheet and don't re-edit rows already marked DONE.
