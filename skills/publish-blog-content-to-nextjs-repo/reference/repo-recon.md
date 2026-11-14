# Repo recon without cloning

A clone is slow, needs credentials, and on Windows can introduce a CRLF problem. Do the reconnaissance
in the browser first. Clone only when you need a real build or typecheck.

## Reading a file from a private repo in the browser

GitHub's raw-file host is frequently blocked by browser-extension site permissions, and GitHub's
embedded page data no longer contains the file's raw lines. A reliable channel is the blob page's
read-only textarea, read by running JavaScript in the page:

```js
const src = document.querySelector('#read-only-cursor-text-area').value;
```

Sanity-check `src.length` against the byte size GitHub displays for the file. If it is short, the page
had not finished loading: wait and re-read. GitHub changes its markup from time to time; if the selector
finds nothing, look for the read-only code textarea on the blob page and use that.

If the `gh` CLI or a GitHub connector with access to the client's org is available, reading the file
through it is simpler still.

## Structural probe before you edit anything

Run a small script against each content file (in the page, or on the working copy) and confirm every
assumption your apply script depends on. Return a small JSON summary to keep the cost low; never pull
whole files into context just to inspect their shape.

For each target slug, assert:

- the slug token appears **exactly once** (a second occurrence means find-first logic would silently
  edit the wrong object);
- no longer slug starts with it (`pricing-guide` vs `pricing-guide-2`): prefix collisions break naive
  matching, so match the slug together with its closing quote;
- the object does not already carry the structured-data field;
- the metadata fields you intend to rewrite are present;
- the object's last field ends on a comma (or handle the case where it does not);
- whether the OLD body contains the token your end-of-object scan looks for.

That last one is the trap: if the end-of-object scan starts before the body literal ends, a body that
happens to contain the closing-brace pattern (a code sample, say) truncates the object. See the comment
in `data/apply_content.py`.

## Copy existing conventions

Before inventing a field or a format, search the content files for it. If some posts already carry FAQ
structured data, match their field name, their `JSON.stringify({...})` shape and their exact
indentation, and set `data/apply_content.py`'s manifest `layout` block to match. A diff that looks like
the team's own code gets reviewed; one that looks foreign gets questioned.

## Check the build config

Read `package.json`. Note the framework version, the package manager, and whether the build pulls in
outside services that will want environment variables. That tells you in advance
whether a local `next build` can succeed or whether you should typecheck the data layer instead.
