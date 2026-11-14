# Building a pixel-faithful page mockup (optional Step 8)

Contents: Harness (in `data/`; edit the CONFIG blocks per site) · Pipeline · Definition of done (mockup)

When the user wants to *see* the recommendation, not just read the section list, build a mockup: one
self-contained HTML page rebuilt in the site's **own** design system (its fonts, colours, spacing and
real product imagery), delivered as a file and optionally published to a preview host (e.g. Vercel or
Netlify) where reviewers can leave comments. Two flavours:

- **Faithful current page:** a 1:1 rebuild of the live page. It proves the design system is right and
  serves as the "before".
- **Recommended redesign:** the Part 2 blueprint realised in the same design system. This is usually the
  deliverable: arrange the extracted components in the recommended order and design the new sections in
  the same visual language.

Why it works: **extract the real design system from the live DOM; don't eyeball it.** Everything
downstream (build, then gate) depends on a faithful token extraction.

## Harness (in `data/`; edit the CONFIG blocks per site)

- `probe.js`: one portable extractor that reads **computed** tokens off the DOM (font family, size,
  weight, line height, hex colours, padding, radius, geometry) and returns numbers and short tokens only.
  The **same** function runs on the live page (the browser extension's JavaScript tool) and on your mock
  (Playwright), so the two specs line up field for field. Set its CONFIG: the nav and button labels to
  find, and the hero background colour if auto-detection picks the wrong element.
- `render.js`: Playwright renders a mock HTML file to a full-page PNG at the live page's real CSS width,
  device scale factor 1, after fonts load.
- `mock_extract.js`: Playwright runs `probe.js` against the mock and writes `spec/mock.json`.
- `metrics_parity.py`: the metrics gate. Diffs the live spec against the mock spec field by field with
  per-field tolerances and prints a PASS/FAIL table (standard library only). `FONT_ALIASES` absorbs a
  site whose declared font name resolves to a different family at render.
- `visual_parity.py`: the visual gate. A region-aware pixel diff of the live screenshot against the mock
  render (Pillow and numpy). Pass the hero background colour and the site's container width as
  arguments.

Setup: copy the scripts into a working folder; `npm i playwright` and `npx playwright install chromium`
(or point `PW_CHROMIUM` at an existing Chromium binary); `pip install pillow numpy`. Folders: `spec/`
(JSON), `ref/` (live screenshots), `out/` (renders and comparisons), `img/` (cropped assets).

## Pipeline

### A. Extraction (get this right first)

1. On the live page, **hide what isn't part of the design**: CMS admin toolbars, promo or alert bars,
   cookie and chat widgets. Zero out any body offset they add (reuse `__clean()` from
   `capture-and-build.md`).
2. **Use the page's real viewport width.** Read `innerWidth`; the window often won't shrink below the
   page's minimum width, so adopt whatever it is and render the mock at the **same** width so containers
   and line wraps match.
3. Run `probe.js` through the JavaScript tool. Two hard constraints in browser extensions:
   - a **privacy filter** may block any return value containing a URL or base64 data, so return numbers,
     hex and short tokens only (no `url()`, no background images, no data URLs). Capture images by
     screenshot and crop, never by returning `src`;
   - tool results may be **truncated at about 1 KB**, so store the full spec on `window.__SPEC` and read
     it back in small groups, or the tail is cut without warning.
4. Save a **clean reference screenshot** to disk with the browser's screenshot tool. Don't rely on a
   server-side screenshot URL (see `capture-and-build.md`).

### B. Nail the font (a real trap)

The declared `font-family` is often not what renders. Measure it: with a `<canvas>`, `measureText` a known
phrase in the element's computed font **on the live page**, then compare candidate families. Two failure
modes:

- the declared family is self-hosted or misnamed and renders a **different cut** from the current Google
  Fonts version (an older cut can be a few percent wider, enough to change line wraps);
- the headless renderer **can't reach** the font host and silently falls back to a system font.

Fix (mandatory): **self-host** the matching font. Bundle the files (the `@fontsource/<font>` packages
carry older cuts too) and inline them as base64 `@font-face` rules in the HTML. That also makes the
deliverable self-contained. Check that the bundled font reproduces the live phrase width **and** the same
line breaks before you move on.

### C. Build and gate section 1 until both gates pass (before scaling)

Rebuild the first section (header and hero) purely from the extracted tokens. Run both gates and iterate:

- **Metrics gate:** `node mock_extract.js mock.html spec/mock.json <W>` then
  `python3 metrics_parity.py spec/live.json spec/mock.json`. Target: every field within tolerance. It
  catches what the eye misses: a line height a couple of pixels tight, a card radius that is rounder than
  the live one, a link colour one shade off, missing letter-spacing on small-caps labels, hero bottom
  padding that is short by a few pixels.
- **Visual gate:** `node render.js mock.html out/mock.png <W>` then
  `python3 visual_parity.py ref/live.jpg out/mock.png --band R,G,B --width <container>`. It scores the
  text column separately from photos (photos inflate pixel difference without meaning a layout miss).
  Look at the side-by-side image it writes.

Don't scale until section 1 passes both: the extraction logic and the shared token set are what every
later section inherits.

### D. Scale down the page

Work through the rest section by section. Lazy-loaded images and backgrounds paint only after they
scroll into view: scroll to each section, wait, then screenshot to disk; crop the real product
screenshots, diagrams and logos from those captures (use real imagery where you can, diagrams
especially). Move the section 1 tokens into a shared stylesheet so every section inherits the same
system. Screenshot timeouts recur on heavy pages: take shots one at a time, retry once, and open a fresh
tab if the renderer stays frozen.

### E. Assemble

- **Faithful current page:** sections in live order.
- **Recommended redesign:** components in the Part 2 order; design the new sections (for example a
  ratings strip, a three-step "how it works", an FAQ, a customer story with a quote, a pricing table, a
  jump-link bar, a closing CTA) in the same design system.
  Mark illustrative placeholder content (customer logos, metrics, case-study numbers, testimonials)
  clearly so the reader knows what to source.

### F. Deliver

Inline every image as a data URI so the result is **one** self-contained HTML file. Deliver the file;
publish it to a preview host if the user wants comments. Keep the current-page build next to the
redesign as the before and after.

## Definition of done (mockup)

- [ ] Section 1 passed the metrics gate (every field in tolerance) and the visual gate (both regions)
      before any scaling.
- [ ] The real font is self-hosted and reproduces the live line wraps (no headless fallback).
- [ ] Real product imagery is used where available, cropped from disk captures, not returned as URLs.
- [ ] The deliverable is a single self-contained HTML file (fonts and images inlined).
- [ ] For a redesign: sections follow the Part 2 order; new sections match the design system; placeholder
      content is marked illustrative.
