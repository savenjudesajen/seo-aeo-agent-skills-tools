# Filling missing image alt in bulk on WordPress: a four-stage pipeline

Contents: 1. Where the alt actually lives (decides who fixes it) · 2. Prioritise (content-aware vs tail) · 3. Extract context (deterministic, in-browser, read-only) · 4. Draft and apply in pipelined waves (output-limit safe) · 5. Tail fill (deterministic, no model needed) · 6. The safe write (idempotent) - assert before bulking · 7. Bulk throughput and tab freezes (same driver as any bulk browser job) · 8. Verify (measured, not claimed) · 9. Write back to the audit workbook

The stages are extract context, draft, apply, verify.

Alt text is not a one-field edit like meta or title. Read this before starting a "missing alt" item.
The pipeline is written for WordPress (the most common case); on Drupal the same logic applies to the
body field's HTML, edited through the real node form (see `reference/drupal-implementation.md`), or to
the image field's own alt sub-field when images are stored in a media/image field.

## 1. Where the alt actually lives (decides who fixes it)

- **Content images (in the post body):** the alt is written into `post_content` as `alt="..."` on each
  `<img>`. It is not pulled live from the media library, so **setting a media item's `alt_text` does not
  fix posts already published.** You must edit `post_content`. In-house: this pipeline.
- **Author/byline avatars and default placeholder images:** rendered by the theme template (no
  attachment ID in the content, very high reuse count across posts). They are not in any post's
  content, so the editor can't fix them. Developer item: one template edit (e.g. set `alt` to the
  author's display name in the avatar call).
- Check which case you're in on ONE image before promising an in-house pass: fetch the post's
  `content.raw` and look for the `<img ... wp-image-<ID> ... alt="">` tag. If the flagged image isn't in
  any post's content, it's theme-rendered and goes to the developer.

## 2. Prioritise (content-aware vs tail)

Join the flagged images to Search Console traffic (see `reference/prioritize-by-traffic.md`).
**Content-aware, keyword-optimised alt for the important tier; lighter content-derived alt is fine for
the long tail.** Confirm this split with the user before starting; some sites want every image
content-aware.

## 3. Extract context (deterministic, in-browser, read-only)

Alt should describe the image in context and carry the page's keywords. Without seeing pixels, the best
signals are the **post title and the image's nearest preceding H2/H3** (they carry the real keywords),
plus the filename. Sweep posts via REST and, for every empty-alt image under `/wp-content/uploads/`,
record `{post id, filename, post title, nearest heading}` into `localStorage` (e.g. `__exData`). This is
read-only, so it is fast; page through with the budgeted driver in section 7. If the user wants alt that
describes what the image actually shows, add a pass that looks at the image itself for the important
tier.

## 4. Draft and apply in pipelined waves (output-limit safe)

Many browser-automation tools truncate the return value (around 1.5 KB) and redact strings containing a
URL or query string. So you can't bulk-export the context and draft outside the browser. Keep the data
in the page and move tiny, URL-free slices:

1. `getWave(n)` returns ~10 compact, URL-free records: `idx | filename topic | post title | section`.
2. You **draft** alt for that wave: **primary keyword (from the title) + a secondary or related term
   (from the section heading)**, natural phrasing, under ~125 characters, and **varied across a post's
   images** (append "step N" / "figure N", or rotate the section angle) so repeated diagrams don't get
   identical alt. Purely decorative images get `alt=""` on purpose; say so in the sheet.
3. `applyWave(alts)` groups the wave by post, fetches each post's `content.raw`, replaces only the
   target `<img>`'s empty `alt=""` (or inserts `alt="..."` before the tag closes when the attribute is
   missing), PATCHes `content` back, advances a cursor in `localStorage`, and **returns the next wave**,
   so each turn does draft + apply + fetch-next in one call.

Escape `"`, `<`, `>` and `&` in drafted alt before inserting it into HTML.

## 5. Tail fill (deterministic, no model needed)

Humanise the filename: strip `-WxH` dimension suffixes, `-scaled`, and a trailing `image` / `img` /
`fig N`, replace separators with spaces, title-case it. But **detect junk filenames** (screenshot, img,
dsc / camera-number patterns, date-only, fewer than ~5 letters, hashes) and **fall back to the post
title** so tail alt is always content-relevant, never gibberish. Run this as one idempotent sweep over
all posts.

## 6. The safe write (idempotent) - assert before bulking

- Auth: header `X-WP-Nonce: window.wpApiSettings.nonce` (present on wp-admin pages that load the REST
  API settings; if it's missing, open the block editor or any admin page that enqueues it).
- Read: `GET /wp-json/wp/v2/posts/{id}?context=edit&_fields=content`.
- Mutate only the target tag's alt; leave everything else byte-identical.
- Write: `POST /wp-json/wp/v2/posts/{id}` with `{content: <new raw content>}`.
- **On the first test post, assert the byte delta equals the total length of the inserted alt text**:
  that proves nothing else changed. Changing alt never touches the slug or URL; it is a pure content
  edit (still confirm the user is happy for post content to be edited at all, and note that each save
  creates a revision).
- Idempotent by construction (only ever touches empty-alt uploads images), so any page or wave can be
  safely re-run.

## 7. Bulk throughput and tab freezes (same driver as any bulk browser job)

- Browser-automation calls time out after a fixed limit (often ~45 s); image-dense pages with many
  PATCHes can freeze the tab.
- Use a **time-budgeted driver** that persists `nextPage` to `localStorage` after every page, so a
  timeout never loses the cursor and you resume idempotently. Keep the per-call budget well under the
  timeout.
- **Tune `per_page` down where posts are image-dense (roughly 10-25) and up where they are sparse
  (50-100).** PATCH in parallel waves of about 5 with ~100 ms spacing.
- Don't change `per_page` mid-run without recomputing the page cursor (the page number depends on
  `per_page`). Safer: finish the run, then do one clean full re-scan from page 1. It's idempotent:
  filled images are skipped and gaps get caught.

## 8. Verify (measured, not claimed)

- Read-only counter sweep: page through all posts and count remaining empty-alt `/uploads/` images.
  It must be 0 (or equal only the images you deliberately marked decorative).
- Spot-check the live front end of a couple of important posts (read the `<img>` alt attributes from
  the cache-busted HTML).
- Multilingual plugin: `/wp/v2/posts` returns the default language only. Images in translated posts
  need a separate per-language pass with the plugin's language parameter; flag it as a follow-up.

## 9. Write back to the audit workbook

On the missing-alt tab add a **Status** column: content images get `Implemented (live <date>)`;
author/theme images get `Deferred - developer (template fix)`. Classify author/theme rows by filename
pattern (avatar, headshot, gravatar, square thumbnail sizes such as `-150x150`) **and** a high reuse
count across pages. Hand the developer a short note: which template renders the image and what the alt
should be (e.g. the author's display name).
