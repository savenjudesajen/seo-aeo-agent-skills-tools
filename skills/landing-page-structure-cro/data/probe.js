/* Portable design-token probe for the mockup harness.
   Reads COMPUTED tokens off the DOM and returns numbers, hex colours and short tokens ONLY
   (no URLs or base64: browser-extension privacy filters block those).
   The SAME function runs on the live page (the extension's JavaScript tool) and on the mock
   (Playwright page.evaluate), so both specs line up field for field for metrics_parity.py.

   Edit CONFIG per site: the visible labels of the primary CTA and a few nav items, and
   optionally the hero background colour. The extraction logic is reusable; the labels are not.
   Tool results may be truncated (~1 KB): on the live page, run
     window.__SPEC = extractSpec(); JSON.stringify(Object.keys(window.__SPEC))
   then read window.__SPEC back one key at a time. */
var PROBE_CONFIG = {
  ctaLabel: 'Get started',              // exact visible text of the primary CTA
  navLabels: ['Product', 'Pricing'],    // exact visible text of two or three nav items
  secondaryLabel: 'Contact sales',      // exact visible text of a secondary button or link
  heroBg: null                          // e.g. 'rgb(240, 244, 248)'; null = first non-transparent ancestor of the h1
};

function extractSpec(cfg) {
  cfg = cfg || PROBE_CONFIG;
  const hex = c => {
    c = c || '';
    const a = c.match(/rgba?\(([^)]+)\)/);
    if (a) { const p = a[1].split(',').map(s => parseFloat(s)); if (p.length >= 4 && p[3] === 0) return 'transparent'; }
    const m = c.match(/(\d+),\s*(\d+),\s*(\d+)/);
    if (!m) return c;
    return '#' + [1, 2, 3].map(i => (+m[i]).toString(16).padStart(2, '0')).join('').toUpperCase();
  };
  const rd = v => { const n = parseFloat(v); return isNaN(n) ? v : Math.round(n * 10) / 10; };
  const cs = el => getComputedStyle(el);
  const rect = el => el.getBoundingClientRect();
  const vis = el => { const r = rect(el); return r.width > 0 && r.height > 0; };
  const byText = (txt, sel) => {
    const arr = [];
    document.querySelectorAll(sel || '*').forEach(e => { if ((e.textContent || '').trim() === txt && vis(e)) arr.push(e); });
    const inner = arr.filter(e => !arr.some(o => o !== e && e.contains(o)));
    const pool = inner.length ? inner : arr;
    pool.sort((a, b) => { const ra = rect(a), rb = rect(b); return ra.width * ra.height - rb.width * rb.height; });
    return pool[0] || null;
  };
  const box = el => {
    const s = cs(el), r = rect(el);
    return { fs: rd(s.fontSize), fw: +s.fontWeight, lh: rd(s.lineHeight), color: hex(s.color), bg: hex(s.backgroundColor),
             pt: rd(s.paddingTop), pr: rd(s.paddingRight), pb: rd(s.paddingBottom), pl: rd(s.paddingLeft),
             rad: rd(s.borderTopLeftRadius), w: Math.round(r.width), h: Math.round(r.height),
             ff: (s.fontFamily.split(',')[0] || '').replace(/"/g, '').trim() };
  };
  const o = {};
  const h1 = document.querySelector('h1');
  if (h1) o.h1 = box(h1);
  let lede = h1 && h1.parentElement ? h1.parentElement.querySelector('p') : null;
  if (lede) o.lede = box(lede);
  const cta = byText(cfg.ctaLabel, 'a,button,span');
  if (cta) o.cta = box(cta);
  const sec2 = byText(cfg.secondaryLabel, 'a,button,span');
  if (sec2) o.secondary = box(sec2);
  (cfg.navLabels || []).forEach((label, i) => {
    const el = byText(label, 'a,span,button');
    if (el) { o['nav' + i] = box(el); o['nav' + i].td = cs(el).textDecorationLine; }
  });
  const navEl = o.nav0 ? byText(cfg.navLabels[0], 'a,span,button') : null;
  const header = navEl && navEl.closest ? navEl.closest('nav,header') : document.querySelector('nav,header');
  let logo = null;
  (header || document).querySelectorAll('img,svg').forEach(im => {
    if (logo) return;
    const r = im.getBoundingClientRect();
    if (r.top < 230 && r.width > 40 && r.width < 260) logo = im;
  });
  if (logo) o.logo = { w: Math.round(rect(logo).width), h: Math.round(rect(logo).height) };
  // Hero band: the h1 ancestor with the configured background, else the first non-transparent one.
  let band = null;
  if (h1) {
    let a = h1;
    for (let i = 0; i < 14 && a; i++) {
      const b = cs(a).backgroundColor;
      const transparent = b === 'transparent' || /rgba\([^)]*,\s*0\)$/.test(b);
      if (cfg.heroBg ? b === cfg.heroBg : !transparent) { band = a; break; }
      a = a.parentElement;
    }
  }
  if (band) { const s = cs(band); o.band = { bg: hex(s.backgroundColor), pt: rd(s.paddingTop), pb: rd(s.paddingBottom) }; }
  const scope = band || document;
  let hi = null, area = 0;
  scope.querySelectorAll('img').forEach(im => {
    const r = im.getBoundingClientRect();
    if (r.width > 300 && r.width * r.height > area) { area = r.width * r.height; hi = im; }
  });
  if (hi) o.img = { w: Math.round(rect(hi).width), h: Math.round(rect(hi).height), nw: hi.naturalWidth, nh: hi.naturalHeight,
                    rad: rd(cs(hi).borderTopLeftRadius) };
  let row = null;
  if (h1 && hi) {
    let a = h1.parentElement;
    for (let i = 0; i < 12 && a; i++) {
      const d = cs(a).display;
      if ((d === 'flex' || d === 'grid') && a.contains(hi)) { row = a; break; }
      a = a.parentElement;
    }
  }
  if (row) {
    const s = cs(row);
    const kids = [...row.children].map(c => Math.round(c.getBoundingClientRect().width)).filter(w => w > 100);
    o.row = { disp: s.display, gap: rd(s.columnGap === 'normal' ? s.gap : s.columnGap), ai: s.alignItems,
              cols: kids.slice(0, 2), w: Math.round(rect(row).width) };
  }
  return o;
}
if (typeof module !== 'undefined' && module.exports) { module.exports = { extractSpec, PROBE_CONFIG }; }
