# Phase D: upload, swap into the post, verify

The PNG passed the gate and the family check. Now get it into the CMS and, if asked, into the live
post. **Changing live content needs the user's explicit approval: ask before any write to a published
page.**

## D1. Upload to the media library

**WordPress REST (the worked example):**

- `POST /wp-json/wp/v2/media`, multipart, with `Content-Disposition: attachment; filename="<name>.png"`
  and the PNG bytes. It needs an authenticated session (a logged-in REST nonce, or an application
  password the user sets up and supplies through an environment variable or their own session; never
  ask the user to paste their login password).
- **Two reliable ways to send the bytes from a browser session:**
  1. **A file-upload action** in your browser-automation tool: locate an `<input type=file>` on the
     media-upload screen and upload the PNG from your outputs folder. Simplest when such an input is on
     the page.
  2. **`fetch` with `FormData`** in page JavaScript: build a `File`/`Blob` and POST it to the media
     endpoint with the nonce header. To get the bytes into the page without pasting a huge string
     through the page, base64-encode the PNG locally and `atob()` it in page JS into a
     `Uint8Array`/`Blob`. Return only the resulting **media id and a boolean**, never the raw URL or
     body.
- **The timeout illusion.** WordPress generates many thumbnail sizes on upload, so a large PNG's POST can
  outlast the automation tool's script timeout and *look* like it failed. **Before assuming failure,
  confirm** with `GET /wp-json/wp/v2/media?per_page=5&orderby=date` (or `…/media/<id>`); the item is
  usually there. Don't re-POST blindly; you'll create duplicate orphaned media.

**Other CMSs:** use their media or asset API, or the DAM. The pattern is the same: upload, capture the
asset id/URL, verify it exists, then reference it in the content.

## D2. Swap the figure into the post

- `GET /wp-json/wp/v2/posts/<id>?context=edit&_fields=content` (the raw block content), replace the
  target `<figure>`/`<img>` `src` (and `width`/`height`/`alt`, plus the image block's attachment id if
  the editor stores one) with the new asset, and `POST` the updated content back. Set the descriptive
  **alt** from your `<desc>`.
- If there's no existing figure, insert a new `<figure>` at the right spot (usually under the "how it
  works" or overview heading), with margins matching the post's other figures, and **no figcaption**
  unless the brand's posts use them.

## D3. Verify: measured, not claimed

After the swap, re-fetch the post content and compute booleans/counts **in page JS, returning only the
booleans** (never raw HTML or URLs; some pages or extensions filter or choke on large returns, and
it keeps tokens out of the transcript):

- `newImg == 1` (the new filename or asset id appears exactly once)
- `oldImg == 0` (the replaced asset is fully gone)
- `hasFigure == true`, `altPresent == true`
- post status `publish`, HTTP 200

Example shape:
```js
const html = (await fetch('/wp-json/wp/v2/posts/<id>?_fields=content&_=' + Date.now(),
  {cache: 'no-store'}).then(r => r.json())).content.rendered;
const cnt = s => html.split(s).length - 1;
({ newImg: cnt('<new-filename>'), oldImg: cnt('<old-filename-or-id>'),
   hasFigure: /<figure/i.test(html), altPresent: /<your alt fragment>/i.test(html) });
```

If the site uses a page cache or CDN, also check the public page once the cache has cleared (or ask the
user to purge it); the REST response can be fresh while the cached page still shows the old figure.

## D4. Browser reliability notes

- **Use a fresh tab for the nonce and the write.** Don't reuse a stalled dashboard tab. In a fresh tab,
  WordPress's core `rest-nonce` AJAX action (the `admin-ajax.php` endpoint with that action name) returns
  a live nonce when the user is logged in (a short hex string) and `0` when logged out; if it's `0`, ask the user to log into wp-admin themselves.
  Never handle their credentials.
- **Themed pages can stall automation; raw endpoints usually don't.** Verify through `/wp-json/…` and
  raw image URLs, not the rendered themed post.
- **Never return raw HTML, URLs or the nonce** out of page JS: return booleans, counts and ids.

## D5. Deliver and clean up

- Share the PNG (and the SVG source) with the user so they see the result.
- If replacing an old figure left an **orphaned media item**, note its id and tell the user; **don't
  delete it yourself** (destructive). They can remove it from the media library.
