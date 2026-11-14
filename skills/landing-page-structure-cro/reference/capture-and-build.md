# Capture and build: the reliable path

Contents: Capturing screenshots (they must be files on disk) · Building the .docx · Verify before delivery (required)

## Capturing screenshots (they must be files on disk)

Screenshots embedded in a `.docx` must be real files the build script can open. Many agent sandboxes
cannot download a server-side screenshot URL (a signed storage link returns 403 through the sandbox's
proxy), and full-page capture modes often error. So capture for embedding goes through a browser that
writes image files locally: a browser-automation extension on the user's machine (it saves captures to a
temp folder the agent can read), or Playwright where the sandbox has network access. The base mechanic is
in the `web-screenshot-to-document` skill; the additions below make a run with many sections and many
competitors fast and clean.

### Browser setup

- Load every browser tool you will need in one go (tab context, navigate, screenshot/computer, run
  JavaScript, batch, create and close tab) rather than one at a time.
- If more than one browser is connected, ask the user which to use (list each one, plus an option to
  confirm in the extension) and select it before navigating.

### Two page helpers, injected once per page

Re-inject after every navigation: the page's `window` resets.

```js
// __clean(): hide sticky headers/footers, cookie and consent banners, and corner chat widgets
window.__clean = () => {
  const sel = ['[id*=cookie i]', '[class*=cookie i]', '[id*=consent i]', '[class*=consent i]',
               '[id*=chat i]', '[class*=chat i]', '[id*=widget i]', '[aria-label*=chat i]',
               'iframe[title*=chat i]'];
  sel.forEach(s => { try { document.querySelectorAll(s).forEach(el =>
      el.style.setProperty('display', 'none', 'important')); } catch (e) {} });
  document.querySelectorAll('body *').forEach(el => {
    const c = getComputedStyle(el);
    if (c.position !== 'fixed' && c.position !== 'sticky') return;
    const r = el.getBoundingClientRect();
    const edge = r.top <= 5 || r.bottom >= innerHeight - 5;
    const corner = r.right > innerWidth - 60 && r.bottom > innerHeight - 60;
    if (r.height < 340 && r.width > 380 && (edge || corner))
      el.style.setProperty('display', 'none', 'important');
  });
};
// __go(pattern): scroll to the first visible heading matching the regex (fallback: strong/p/blockquote);
// returns the matched text, or NOTFOUND
window.__go = (pat) => {
  const re = new RegExp(pat, 'i');
  const pick = (q, max) => [...document.querySelectorAll(q)].find(e => {
    const t = (e.innerText || '').trim();
    return t && t.length < max && re.test(t) && e.getBoundingClientRect().height > 0;
  });
  const m = pick('h1,h2,h3,h4', 130) || pick('h5,h6,strong,p,blockquote', 170);
  if (!m) return 'NOTFOUND:' + pat;
  scrollTo(0, Math.max(0, m.getBoundingClientRect().top + scrollY - 90));
  return 'ok:' + (m.innerText || '').trim().slice(0, 60);
};
```

Then one batch captures many sections without knowing pixel offsets:
`[navigate, wait, {js: inject + __clean()}, {js: __clean(); __go('How it works')}, wait,
{screenshot, save to disk}, {js: __clean(); __go('FAQ|Questions')}, wait, {screenshot}, …]`.
JavaScript calls work inside a batch. For a page whose structure you already know (usually the target
page), measure each heading's Y position once with JavaScript and scroll to exact positions instead.

### Gotchas

- **Chat widgets re-render** after load and after scrolling, and branded assistant panels are often
  taller than the size cap in `__clean()`. Re-run `__clean()` before every shot; crop out large side
  panels afterwards.
- **Screenshot timeouts** ("capture timed out" / "renderer frozen") recur on heavy single-page apps.
  Retry once; if it persists, open a **fresh tab**, which is the reliable recovery. Closing a tab can
  change the tab group's id: re-read the tab context to get a valid tab id.
- **Viewport sizes vary** between machines and sessions, and resize requests aren't always honoured.
  Always crop afterwards; never rely on one fixed pixel box across sites.
- **Lazy sections** don't render until scrolled into view; `__go()` plus a one-second wait usually fixes
  it. If a section still won't render, use a nearby section on the same site that proves the same point
  and say so in the caption.
- For heavy pages take shots one at a time instead of in a long batch.

### Crop, then check every crop (Pillow)

```python
from PIL import Image
im = Image.open(src)            # print(im.size) first
im.crop((left, top, right, bottom)).save(out)   # trim nav bars, chat panels, whitespace
```

Build a labelled contact sheet of all crops and look at it before you embed anything.

## Building the .docx

Use `data/build_doc_template.py`: it has helpers for headings, an image with a thin border and an italic
grey caption, and shaded tables. `add_image()` caps by width **and** height so near-square shots don't
take over a page. Embed at about 6.5" wide. Every image gets a caption naming what it shows and its source
URL. Default styling is neutral (Calibri, dark grey text, one navy accent); if the client has a document
template, set its font and accent colour in CONFIG instead.

## Verify before delivery (required)

```bash
python3 data/check_deliverable.py deliverable.docx      # must print PASS
soffice --headless --convert-to pdf deliverable.docx
pdftoppm -jpeg -r 80 deliverable.pdf pg                 # then look at every pg-*.jpg
```

Confirm: no chat widgets or nav bars in any image, nothing cut off, no table overflowing, every caption
present. Then deliver the `.docx`.
