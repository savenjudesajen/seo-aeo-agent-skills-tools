# Sharp, zoomed captures of a web app's UI (cards, tables, charts)

Contents: Rules before you start · The clone method · Charts (recharts and similar SVG libraries) · Tables and virtualized lists · Adding margin to a finished capture · Wide captures for a 16:9 canvas · Menus and popovers · Neutral avatars and sample text · Hold the exports in memory · Browser tool quirks

The main pipeline in `SKILL.md` captures a page or a section for a document. This file covers the harder
case: product UI (dashboards, tables, charts) that has to read large and sharp in a finished image, for an
image or design tool or a page slot. A full-viewport screenshot of a dashboard shrinks every label. The
method is to capture one card at a time, at 1.5 to 2.3 times zoom, from a clone you can edit. Expect
sources of roughly 1000 px wide per card, and a wider source for a 16:9 canvas.

## Rules before you start

- **The user signs in.** If the app shows a sign-in page, stop and ask the user to sign in. Never type or
  submit credentials, even when the browser autofills them.
- **Use a fresh tab** for the capture work and keep the image tool's tab separate.
- **Frame pixels are not physical pixels.** The browser tool's click coordinates and its zoom regions are
  in the screenshot frame. The saved PNG is native: the frame times the device scale (a 1400 px frame at
  a device scale of 1.25 saves 1750 px). Recompute after any viewport change from `innerWidth` and
  `innerHeight`.
- **Region zoom with save-to-disk** writes the native PNG to a local temp folder. Don't combine it with a
  scale option, which shrinks the saved file. Copy the file into your working folder under its final
  name, then upload it to the image tool.
- **Don't change the account.** Keyboard shortcuts on panels can trigger actions. Close panels with their
  own close control, navigate by URL (list, then item, then tab), and never click accept, decline, apply
  or any other button that changes the account.
- **Scan before you capture.** Keep a regex of every name that must not appear (competitors, people,
  internal project names) as `window.__BLOCK_RE`, and test the card's `textContent`, every `alt`, `title`
  and `aria-label`, and each image `src` against it. Zero hits to proceed. Replace what hits (see Neutral
  avatars and sample text).

## The clone method

Edit a copy, never the live page. Framework re-renders reset live DOM edits, and charting libraries
measure text under zoom and inflate their axis widths.

1. Find the card's root element: often the header's parent, with an inline width and height in px and
   `overflow: hidden`.
2. If the card's text wraps badly at full width, give the card's wrapper a width in CSS px that lays it
   out compactly (roughly 500 to 700 px) and let the layout settle.
3. `cloneNode(true)` the card into a fixed overlay `#__cap` with its own width and height in CSS px and a
   white background. Strip the clone's border, radius and shadow, and hide the body's other children.
4. Edit the clone (sections below), then set `document.documentElement.style.zoom` to 1.5 to 2.3. The
   overlay's size times the zoom (times the device scale) is the native size of the capture; aim for
   about 1000 px wide.
5. Capture with a region zoom over the overlay in frame coordinates, with save-to-disk on. Read the saved
   file's size rather than trusting the arithmetic.

## Charts (recharts and similar SVG libraries)

- **Don't zoom or transform the live chart.** Wait until its entry animation ends. Animations run on
  `requestAnimationFrame`, so take a few small screenshots to make the browser produce frames; value
  labels often appear only afterwards. Then clone.
- **To add a marker**, compute its x from the data point you want: parse the `d` attribute of the area or
  line path (`path.recharts-area-curve` in recharts) and read that point's x. Set the marker's `left` to
  it, move or remove the vertical guide to match, and replace the label text.
- **Existing markers may mean something else.** Chart badges can be annotations, not data points. Don't
  present them as something they are not. If you replace or add a marker, say so in your report to the
  user.
- **A window the live chart doesn't show** (a shorter range, a cut-off day) can be rebuilt from the
  chart's own values. Check at least one point against the live tooltip, and tell the user the view was
  reconstructed.

## Tables and virtualized lists

A virtualized table positions rows with `transform` and absolute positions, so a clone collapses. In the
clone:

- Set `table` and `tbody` to `display: block` with `height: auto`, and `thead` to `position: static`.
- Set each `tr` to `position: static; transform: none; display: flex`.
- Set cell widths inline in px so the columns line up (they must sum to the card width).
- Remove any rows or columns the user doesn't want shown (for example prices, counts, competitor rows or
  rows naming people), keep the first N rows that fit the card, un-truncate titles (remove `truncate`
  and `text-overflow`), and hide row icons and hover chrome.
- Container queries can hide labels in a narrow clone (a stacked bar loses its percentages). Force the
  label's `display` back on for segments wide enough to hold it.
- Leave room on the right. A table that runs to the clone's edge reads as cut off in a square image. Give
  the clone about 40 px of free width after its last column, or pad the finished PNG (next section).

## Adding margin to a finished capture

When a capture sits too close to an edge, pad the PNG instead of recapturing it.

1. Pad the side that needs it with the card's background colour.
2. Carry every border or separator that reached the old edge across the new margin by repeating the last
   pixel column of those rows (edge replication), so the lines run to the new edge as they ran to the
   old one.
3. If a right-aligned control should stay right-aligned, move it: cut its non-background pixels out of a
   region you name and paste them back shifted.
4. If the image tool fades the bottom edge, pad the bottom too.
5. View the result at full size and confirm the lines reach the new edge and nothing else changed. Keep
   the original beside it and give the new file its own name.

```python
from PIL import Image, ImageChops

BG = (255, 255, 255)           # the card's background colour


def pad_right(src, pad):
    w, h = src.size
    out = Image.new("RGB", (w + pad, h), BG)
    out.paste(src, (0, 0))
    for y in range(h):
        px = src.getpixel((w - 1, y))
        if px != BG:                         # a separator reaches the old edge
            out.paste(px, (w, y, w + pad, y + 1))
    return out


def nudge(img, region, dx):
    """Shift the non-background content inside region (x0, y0, x1, y1) right by dx px."""
    blank = Image.new("RGB", (region[2] - region[0], region[3] - region[1]), BG)
    box = ImageChops.difference(img.crop(region), blank).getbbox()
    if box is None:
        return img
    x0, y0, x1, y1 = (region[0] + box[0], region[1] + box[1], region[0] + box[2], region[1] + box[3])
    piece = img.crop((x0, y0, x1, y1))
    img.paste(BG, (x0, y0, x1, y1))
    img.paste(piece, (x0 + dx, y0))
    return img


def pad_bottom(img, pad):
    out = Image.new("RGB", (img.width, img.height + pad), BG)
    out.paste(img, (0, 0))
    return out


PAD_RIGHT = 40                   # px of new margin on the right
CONTROL_REGION = (0, 0, 0, 0)    # set to a box around the right-aligned control, or leave as-is to skip
PAD_BOTTOM = 50                  # only if the image tool fades the bottom edge

img = Image.open("capture.png").convert("RGB")
img = pad_right(img, PAD_RIGHT)
if CONTROL_REGION[2] > CONTROL_REGION[0]:
    img = nudge(img, CONTROL_REGION, PAD_RIGHT // 2)
img = pad_bottom(img, PAD_BOTTOM)
img.save("capture_padded.png")
```

## Wide captures for a 16:9 canvas

A square capture sits small on a 1920x1080 canvas, so a layout that shows the image wide (for example an
intro with the image centred above the text) needs a source with a wide shape.

1. **Choose a view that is wide by nature** (a table with many columns) and let the app show its widest
   layout. Before editing the DOM, check whether a filter or view parameter in the page URL adds columns
   without any clicks.
2. **Give the clone a wide card**, around 1100 CSS px at a root zoom of about 1.4. The capture region is
   in frame coordinates, so the native width is the region times the device scale, not CSS px times zoom:
   read the saved file's size instead of computing it.
3. **Pad the bottom** with the card's background (`pad_bottom` above) if the image tool fades the bottom
   edge.
4. **Set the canvas size per canvas.** Import the source into its own canvas, set the tool's 16:9 option
   on that canvas only, and leave the other canvases on their own sizes. Export through the in-memory hook
   below, take the export that matches the canvas order, and confirm it is 1920 by 1080.
5. **Save it under its own name** with the size in it (`..._1920x1080.png`) and its own alt text. Keep the
   square version for the same slot as a fallback.

## Menus and popovers

A menu that opens at body level is often `position: absolute` with an inline `transform: translate(x,
y)`, and root zoom multiplies that transform. Place it by hand: `translate(btn.left / z, (btn.top - 10 -
menu.height) / z)`, with visual px and the zoom `z`.

## Neutral avatars and sample text

- Replace a competitor's logo or avatar with a neutral letter circle (A, B, C, assigned by first
  appearance of each image `src`). Keep it replaced with a `MutationObserver` stored as `window.__mo`,
  because the app re-renders and puts the logo back.
- Where real rows name a client or a competitor (row titles, item names), swap in neutral sample titles
  and keep the real counts and shares. Tell the user you did.

## Hold the exports in memory

When an image tool exports by creating a Blob and clicking a download link, intercept it in the page so
nothing is written to the user's disk (downloading a file needs the user's explicit yes), and keep the
Blob for the upload:

```js
window.__exports = [];
const _toBlob = HTMLCanvasElement.prototype.toBlob;
HTMLCanvasElement.prototype.toBlob = function (cb, type, q) {
  return _toBlob.call(this, b => { window.__exports.push({ blob: b, w: this.width, h: this.height }); cb(b); }, type, q);
};
const _click = HTMLAnchorElement.prototype.click;
HTMLAnchorElement.prototype.click = function () { if (this.download) return; return _click.call(this); };
```

An "export all" button typically calls `toBlob` once per canvas, in canvas order, then builds a zip. The
hook records the blobs in that order, and the zip's own download is swallowed too. Check how the specific
tool triggers the download before relying on `click()`: a tool that dispatches a click event needs that
hooked instead.

## Browser tool quirks

- A JavaScript evaluation tool may behave like a REPL: top-level `await` works and `return` does not.
- Some browser tools block results containing `=`, `&` or `?`. Return counts, booleans and short ids, or
  sanitize with `.replace(/[=&?]/g, '~')`.
- A batch tool that chains navigate, click and script calls saves round trips.
- A still page produces no frames, so take small screenshots while an animation runs.
- A screenshot timeout usually passes on one retry.
- A hidden or frozen tab returns no screenshots. Recreate the tab, then refresh the tab context to get the
  new id.
- A window resize can report success while `innerWidth` stays the same, so read `innerWidth` after it.
  For a narrow-width check of a same-origin page, load it in a fixed-width iframe and zoom a screenshot on
  that region (frame coordinates, not CSS px).
