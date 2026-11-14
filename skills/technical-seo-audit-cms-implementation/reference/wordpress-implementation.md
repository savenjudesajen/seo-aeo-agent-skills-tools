# WordPress implementation reference (Yoast SEO, optional multilingual plugin)

Contents: Split first · Where Yoast stores it · What is not writable the way you'd expect · The safe UI write (title, meta, H1) - classic editor · Alt text - its own pipeline · Verify live (never trust the save alone) · Multilingual plugins (WPML, Polylang) · Bulk throughput and tab freezes (any large browser job)

The mechanics below assume WordPress with Yoast SEO. Selectors are plugin defaults; confirm them on the
first edit of a new site, since themes and page builders can move things. If the site uses another SEO
plugin (Rank Math, All in One SEO, SEOPress), find its equivalent fields on the first post and keep the
same workflow.

## Split first

Developer items (redirects, image compression, hreflang output from the multilingual plugin,
HTTPS/HSTS, security headers, pagination markup, anything theme-rendered) go to a developer ticket.
In-house CMS items: Yoast title and meta, H1 (`post_title`), image alt in post content, per-post
noindex and canonical.

## Where Yoast stores it

| What | Classic-editor selector | Post meta key (DB) |
|---|---|---|
| SEO title (rendered `<title>`) | `#yoast_wpseo_title` | `_yoast_wpseo_title` |
| Meta description | `#yoast_wpseo_metadesc` | `_yoast_wpseo_metadesc` |
| **H1** (visible headline, in most themes) | `#title` (the post title field) | `post_title` |
| Canonical | Yoast box, Advanced tab, Canonical URL | `_yoast_wpseo_canonical` |
| Robots noindex | Yoast box, Advanced tab, "Allow search engines to show this in search results?" | `_yoast_wpseo_meta-robots-noindex` |

Most themes render `post_title` as the on-page H1. Changing the post title changes the H1 (and
anywhere the title shows: related-posts widgets, menus that use the title) but not the slug or URL.
Category and tag archive "pages" are **terms** (`term.php`), articles are **posts** (`post.php`).
Term-level Yoast fields are the hidden inputs `#hidden_wpseo_title` and `#hidden_wpseo_desc`,
submitted with the `#edittag` form.

On the **block editor**, the Yoast fields live in a React sidebar panel and the classic selectors
don't exist. Either edit through that panel and click the real **Update** button, or ask whether the
developer can run WP-CLI (below). Don't try to reconstruct the block editor's save request.

## What is not writable the way you'd expect

- **Yoast title and meta are not REST-writable via `{meta: {...}}` by default**: Yoast doesn't register
  its post meta for REST updates, so the request "succeeds" and changes nothing. Use the editor UI
  write below, or WP-CLI server-side
  (`wp post meta update <id> _yoast_wpseo_title '<new title>'`).
- **Content-image alt is not the media library's `alt_text`.** The alt is written into `post_content`
  as `alt="..."` when the image is inserted; changing the media item's alt later does nothing to posts
  already published. Edit `post_content` instead, which **is** REST-writable with a nonce. Full method:
  `reference/image-alt-at-scale.md`.

## The safe UI write (title, meta, H1) - classic editor

1. Navigate to `/wp-admin/post.php?post=<id>&action=edit`.
2. In the page, poll up to ~40 x 250 ms for `#yoast_wpseo_title` to exist (Yoast loads late). Set each
   field through the **native value setter**
   (`Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set`, and the
   `HTMLTextAreaElement` one for the description), then dispatch `input` and `change`. Click the real
   **`#publish`** (Update) button: the editor syncs its content on a genuine submit. Do not blind-POST
   the form; that wipes the body.
3. Wait ~1.5 s after the click before the next navigation, so the form POST finishes transmitting. The
   server persists it even if the next navigation interrupts the response.

```js
async function save3(id, t, d, h){
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 40 && !document.querySelector('#yoast_wpseo_title'); i++) await sleep(250);
  const ti = document.querySelector('#yoast_wpseo_title');
  const de = document.querySelector('#yoast_wpseo_metadesc');
  const h1 = document.querySelector('#title');
  if (!ti || !de || !h1) return 'FIELDS NOT FOUND';
  if (!location.search.includes('post=' + id)) return 'WRONG POST';
  const setIn = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  const setTa = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
  const put = (el, v) => {
    (el.tagName === 'TEXTAREA' ? setTa : setIn).call(el, v);
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
  };
  if (t) put(ti, t);
  if (d) put(de, d);
  if (h) put(h1, h);
  document.querySelector('#publish').click();
  await sleep(1500);
  return 'saved ' + id;
}
await save3(123, '<title>', '<meta description>', '<H1>');
```

### Bulk pattern (the 3-field "title same as H1" fix, and title/meta generally)

- Inject the full `{id: {t: title, d: meta, h: H1}}` map once into `localStorage` (it persists per
  origin across navigations), so each save call only needs the post ID.
- Per post: navigate to the edit URL, then run the save snippet reading `localStorage` for that ID.
- If the tool supports batching actions, **batch 3-4 posts per call** (6-8 actions). Larger batches
  tend to hit the tool's timeout. On a timeout, check which tab and URL it landed on and resume from
  there; earlier saves have usually persisted (verify them).

## Alt text - its own pipeline

Content-image alt means editing `post_content` (an idempotent PATCH of the exact `<img>` tag).
Prioritisation, content-aware drafting, output limits, the budgeted driver and verification are in
`reference/image-alt-at-scale.md`. Author and byline avatars are theme-rendered: developer item.

## Verify live (never trust the save alone)

Fetch `/wp-json/wp/v2/posts/<id>?_fields=title,link` to confirm `post_title` (the H1) and get the URL.
Then fetch the front-end `link` cache-busted and read `<title>`, `<meta name="description">` and the
first `<h1>`: confirm all three are live and distinct. **Verify the title tag and meta from the
front-end HTML, not from REST**: `yoast_head_json` can come back empty or stale over REST even when
the page is correct. Space verification fetches ~200 ms apart and run them in chunks of 12 or fewer to
avoid freezing the tab.

## Multilingual plugins (WPML, Polylang)

`/wp-json/wp/v2/posts` returns the default language only. Translations need the plugin's language
parameter (e.g. `&lang=<code>` with WPML). Title, meta and alt live per translation: run a separate pass
per language, as a localisation task, and don't machine-translate silently.

## Bulk throughput and tab freezes (any large browser job)

Browser-automation calls typically time out after a fixed limit (often around 45 s), and dense admin
pages can freeze the tab. Use a time-budgeted driver that writes its cursor (`nextPage`) to
`localStorage` after every page so a timeout resumes idempotently; keep each call's budget well under
the timeout; tune `per_page` to page density; send PATCHes in parallel waves of about 5. Keep data in
the page and return only small, URL-free slices (see the `getWave` / `applyWave` pattern in
`reference/image-alt-at-scale.md`).
