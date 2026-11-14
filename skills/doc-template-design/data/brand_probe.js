/* brand_probe.js (doc-template-design): measure the rendered brand styles of a live page for a client theme.
   Run it in a browser tool that can execute JavaScript on the page (a browser-automation extension or MCP
   server, Playwright or Puppeteer, or paste it into the DevTools console). Read-only: nothing on the page
   changes. It measures text styles weighted by characters, h1-h4 styles, buttons and calls to action, link
   colours, background/text/border colours weighted by area, header/hero/footer colours, :root custom
   properties, declared and loaded font faces and font files, logo candidates (the best inline SVG returned
   standalone) and page meta. The full JSON stays on the page as window.__brandProbe and the call returns a
   short summary; read the JSON back with dump_probe.js. theme_from_probe.py turns one or more probes into a
   theme proposal. Consent banners and chat widgets are skipped. */
await (async () => {
  const SKIP = /cookie|consent|gdpr|cmp-|cky-|osano|truste|didomi|hs-banner|cybot|usercentrics|termly|iubenda|klaro|qc-cmp|intercom|drift-|hubspot-messages|chat-widget/i;
  const out = {probe: 1, url: location.href, host: location.hostname, title: document.title,
               at: new Date().toISOString(), viewport: [innerWidth, innerHeight], lang: document.documentElement.lang};
  try { await document.fonts.ready; } catch (e) {}
  // reveal-on-scroll sites (Webflow, GSAP) keep sections at opacity 0 until they enter the viewport: scroll
  // through the page once so they render, then measure from the top
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  for (let y = 0, i = 0; y < document.documentElement.scrollHeight && i < 40; y += Math.round(innerHeight * 0.8), i++) {
    scrollTo(0, y); await sleep(120);
  }
  scrollTo(0, 0); await sleep(500);
  // any CSS colour -> 'RRGGBB' through a 1x1 canvas (handles rgb, hsl, oklch, color(), names); null if mostly transparent
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', {willReadFrequently: true});
  const hex = (c) => {
    if (!c || c === 'transparent' || c === 'none' || /^url|gradient/.test(c)) return null;
    cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#010203'; cx.fillStyle = c;
    if (cx.fillStyle === '#010203') return null;
    cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data;
    if (d[3] < 200) return null;
    return [d[0], d[1], d[2]].map(v => v.toString(16).padStart(2, '0')).join('').toUpperCase();
  };
  const cls = (e) => typeof e.className === 'string' ? e.className : (e.className && e.className.baseVal) || '';
  const skipRoots = [...document.querySelectorAll('[id],[class]')].filter(e => SKIP.test((e.id || '') + ' ' + cls(e)));
  const skipped = (e) => skipRoots.some(r => r.contains(e));
  const vis = (cs) => cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0.05;
  const tally = (m, k, w) => { if (k) m.set(k, (m.get(k) || 0) + w); };
  const top = (m, n) => [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, n).map(([k, w]) => [k, Math.round(w)]);
  const grad = (cs) => /gradient/.test(cs.backgroundImage) ? cs.backgroundImage.slice(0, 240) : null;
  const lum = (h) => {
    const v = [0, 2, 4].map(i => parseInt(h.substr(i, 2), 16) / 255)
      .map(c => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
  };
  // background a text element sits on: first opaque background up the tree (white when none)
  const bgCache = new Map();
  const bgOf = (e) => {
    const chain = []; let x = e, found = null;
    while (x && x.nodeType === 1) {
      if (bgCache.has(x)) { found = bgCache.get(x); break; }
      chain.push(x);
      const h = hex(getComputedStyle(x).backgroundColor);
      if (h) { found = h; break; }
      x = x.parentElement;
    }
    found = found || 'FFFFFF';
    for (const c of chain) bgCache.set(c, found);
    return found;
  };

  // 1. every visible element: backgrounds by area, borders by length, text colour and text style by characters
  const bg = new Map(), fg = new Map(), bd = new Map(), styles = new Map();
  for (const e of [...document.body.querySelectorAll('*')].slice(0, 9000)) {
    if (e.closest('script,style,noscript,template') || skipped(e)) continue;
    const cs = getComputedStyle(e);
    if (!vis(cs)) continue;
    const r = e.getBoundingClientRect();
    const area = Math.max(0, Math.min(r.width, innerWidth)) * Math.max(0, r.height);
    if (area < 4) continue;
    tally(bg, hex(cs.backgroundColor), area);
    const bw = ['Top', 'Right', 'Bottom', 'Left'].reduce((s, k) => s + (parseFloat(cs['border' + k + 'Width']) || 0), 0);
    if (bw > 0 && cs.borderTopStyle !== 'none') tally(bd, hex(cs.borderTopColor), bw * Math.max(r.width, r.height));
    let chars = 0;
    for (const n of e.childNodes) if (n.nodeType === 3) chars += n.textContent.trim().length;
    if (chars) {
      const col = hex(cs.color), under = bgOf(e);
      // context: L = dark text on a light background, D = on a dark background, I = light text over a light
      // colour, which means over an image or video
      const ctx = lum(under) > 0.5 ? (col && lum(col) > 0.6 ? 'I' : 'L') : 'D';
      tally(fg, col, chars);
      tally(styles, JSON.stringify([cs.fontFamily, cs.fontWeight, Math.round(parseFloat(cs.fontSize)), col,
                                    cs.textTransform, cs.fontStyle, ctx, under]), chars);
    }
  }
  out.bg = top(bg, 20); out.text = top(fg, 15); out.border = top(bd, 10);
  out.textStyles = top(styles, 24).map(([k, w]) => {
    const [family, weight, size, color, transform, style, ctx, under] = JSON.parse(k);
    return {family, weight, size, color, transform, style, ctx, under, chars: w};
  });

  // 2. headings
  out.headings = [];
  for (const tag of ['h1', 'h2', 'h3', 'h4']) {
    let k = 0;
    for (const e of document.querySelectorAll(tag)) {
      if (k >= 3 || skipped(e)) continue;
      const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
      const text = (e.innerText || e.textContent || '').trim().replace(/\s+/g, ' ');
      if (!vis(cs) || r.width * r.height < 4 || !text) continue;
      const inner = [...e.querySelectorAll('*')].find(x => [...x.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()));
      const ics = inner ? getComputedStyle(inner) : null;
      out.headings.push({tag, text: text.slice(0, 70), family: cs.fontFamily, weight: cs.fontWeight,
                         size: parseFloat(cs.fontSize), color: hex(cs.color), innerColor: ics ? hex(ics.color) : null,
                         transform: cs.textTransform, spacing: cs.letterSpacing, lineHeight: cs.lineHeight,
                         gradient: grad(cs) || (ics && grad(ics))});
      k++;
    }
  }

  // 3. buttons and calls to action
  out.buttons = []; const seen = new Set();
  for (const e of document.querySelectorAll('button, [role=button], input[type=submit], a[class*=btn], a[class*=Btn], ' +
                                            'a[class*=button], a[class*=Button], a[class*=cta], a[class*=CTA], .btn, .button')) {
    if (out.buttons.length >= 20 || skipped(e)) continue;
    const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
    const text = (e.innerText || e.value || '').trim().replace(/\s+/g, ' ').slice(0, 40);
    if (!vis(cs) || r.width < 30 || r.height < 16 || !text) continue;
    const b = hex(cs.backgroundColor), before = hex(getComputedStyle(e, '::before').backgroundColor);
    const key = [b, before, hex(cs.color)].join('|') + text;
    if (seen.has(key)) continue; seen.add(key);
    out.buttons.push({text, bg: b, before, color: hex(cs.color),
                      border: parseFloat(cs.borderTopWidth) && cs.borderTopStyle !== 'none' ? hex(cs.borderTopColor) : null,
                      family: cs.fontFamily, weight: cs.fontWeight, size: parseFloat(cs.fontSize),
                      radius: cs.borderTopLeftRadius, transform: cs.textTransform, gradient: grad(cs),
                      top: Math.round(r.top + scrollY)});
  }

  // 4. link colours in running text
  const links = new Map();
  for (const e of document.querySelectorAll('main a, article a, p a, li a')) {
    if (skipped(e) || e.closest('nav, header, footer')) continue;
    const cs = getComputedStyle(e);
    if (vis(cs) && (e.innerText || '').trim()) tally(links, hex(cs.color), 1);
  }
  out.links = top(links, 6);

  // 5. regions: effective background under points of the first screen, header and footer subtrees
  const effBg = (x, y) => {
    let image = false;
    for (const e of document.elementsFromPoint(x, y)) {
      if (skipped(e)) continue;
      const cs = getComputedStyle(e);
      if (/url\(/.test(cs.backgroundImage) || e.tagName === 'IMG' || e.tagName === 'VIDEO') image = true;
      const h = hex(cs.backgroundColor);
      if (h) return {color: h, overImage: image, gradient: grad(cs)};
    }
    return {color: null, overImage: image};
  };
  const subtree = (sel) => {
    const root = document.querySelector(sel);
    if (!root) return null;
    const m = new Map(), t = new Map();
    for (const e of [root, ...root.querySelectorAll('*')].slice(0, 2000)) {
      const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
      if (!vis(cs)) continue;
      tally(m, hex(cs.backgroundColor), r.width * r.height);
      if ([...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) tally(t, hex(cs.color), 1);
    }
    return {bg: top(m, 4), text: top(t, 4)};
  };
  out.regions = {top: effBg(innerWidth * 0.5, 10), topLeft: effBg(30, 10),
                 hero: effBg(innerWidth * 0.5, innerHeight * 0.55), heroLeft: effBg(innerWidth * 0.12, innerHeight * 0.45),
                 header: subtree('header, [role=banner], .navbar, #header'),
                 footer: subtree('footer, [role=contentinfo], #footer, .footer')};

  // 6. custom properties on :root (colour and font tokens)
  const vars = {}; const rs = getComputedStyle(document.documentElement);
  const keepVar = (p, v) => v && v.length <= 140 && (/font|family|typeface/i.test(p) ||
      /colou?r|brand|primary|secondary|accent|bg|background|text|neutral|gr[ae]y|swatch|dark|light/i.test(p) ||
      /^(#|rgb|hsl|oklch|lab|color\()/i.test(v));
  for (let i = 0; i < rs.length && Object.keys(vars).length < 250; i++) {
    const p = rs[i];
    if (p.startsWith('--')) { const v = rs.getPropertyValue(p).trim(); if (keepVar(p, v)) vars[p] = v; }
  }
  if (!Object.keys(vars).length) {
    for (const s of document.styleSheets) {
      try {
        for (const r of s.cssRules) {
          if (!r.style || !/^(:root|html|body)\b/.test(r.selectorText || '')) continue;
          for (const p of r.style) if (p.startsWith('--') && Object.keys(vars).length < 250) {
            const v = rs.getPropertyValue(p).trim() || r.style.getPropertyValue(p).trim();
            if (keepVar(p, v)) vars[p] = v;
          }
        }
      } catch (e) {}
    }
  }
  out.vars = vars;

  // 7. fonts: faces the page declared (and whether they loaded), @font-face sources, font files fetched
  const faces = new Map();
  for (const f of document.fonts) {
    const k = [f.family.replace(/["']/g, ''), f.weight, f.style].join('|');
    if (!faces.has(k) || f.status === 'loaded') faces.set(k, f.status);
  }
  out.fontFaces = [...faces.entries()].slice(0, 100).map(([k, status]) => {
    const [family, weight, style] = k.split('|'); return {family, weight, style, status};
  });
  out.fontCss = [...document.querySelectorAll('link[href]')].map(l => l.href)
    .filter(h => /fonts\.googleapis|typekit|fonts\.bunny|fast\.fonts|cloud\.typography|fontshare|fonts\.adobe/i.test(h)).slice(0, 10);
  out.fontFiles = performance.getEntriesByType('resource').map(e => e.name)
    .filter(n => /\.(woff2?|ttf|otf)(\?|$)/i.test(n)).slice(0, 40);

  // 8. logo candidates; the best inline SVG is returned standalone (computed fills written into the markup)
  const home = location.origin.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const homeRe = new RegExp('^' + home + '/?([a-z]{2}(-[a-z]{2})?/?)?(#.*)?$', 'i');
  const cands = [];
  for (const e of document.querySelectorAll('img, svg, [class*=logo], [id*=logo], [class*=Logo], [class*=brand]')) {
    const tag = e.tagName.toLowerCase();
    if (skipped(e) || (tag === 'svg' && e.parentElement && e.parentElement.closest('svg'))) continue;
    const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
    if (!vis(cs) || r.width < 16 || r.height < 8) continue;
    let src = null;
    if (tag === 'img') src = e.currentSrc || e.src;
    else if (tag !== 'svg') { const m = cs.backgroundImage.match(/url\(["']?([^"')]+)/); if (!m) continue; src = m[1]; }
    const label = [e.id, cls(e), e.getAttribute('alt'), e.getAttribute('aria-label'), e.getAttribute('title'), src || '',
                   (e.closest('a') || {}).className || ''].join(' ');
    const a = e.closest('a');
    let score = 0;
    if (e.closest('header, [role=banner], nav, [class*=header], [class*=navbar], [class*=nav_]')) score += 3;
    if (/logo|brand|wordmark/i.test(label)) score += 3;
    if (r.top + scrollY < 160) score += 2;
    if (a && homeRe.test(a.href)) score += 2;
    if (r.left < innerWidth * 0.3) score += 1;
    if (r.width > 420 || r.height > 160) score -= 3;
    const fills = new Map();
    if (tag === 'svg') for (const s of e.querySelectorAll('path,rect,circle,polygon,ellipse,polyline,line,text')) {
      const scs = getComputedStyle(s); tally(fills, hex(scs.fill), 1); if (scs.stroke !== 'none') tally(fills, hex(scs.stroke), 1);
    }
    cands.push({el: e, info: {score, tag, src, w: Math.round(r.width), h: Math.round(r.height), top: Math.round(r.top + scrollY),
                              left: Math.round(r.left), alt: (e.getAttribute('alt') || e.getAttribute('aria-label') || '').slice(0, 60),
                              fills: top(fills, 6)}});
  }
  cands.sort((a, b) => b.info.score - a.info.score);
  out.logos = cands.slice(0, 6).map(c => c.info);
  const bestSvg = cands.find(c => c.info.tag === 'svg' && c.info.score >= 5);
  if (bestSvg) {
    const src = bestSvg.el, clone = src.cloneNode(true);
    const a = src.querySelectorAll('*'), b = clone.querySelectorAll('*');
    for (let i = 0; i < a.length; i++) {
      if (!/^(path|rect|circle|polygon|ellipse|polyline|line|text|tspan|use)$/i.test(a[i].tagName)) continue;
      const scs = getComputedStyle(a[i]);
      b[i].setAttribute('fill', scs.fill.startsWith('url') ? scs.fill.replace(/^url\("?|"?\)$/g, '').replace(/^.*#/, 'url(#') + ')' : scs.fill);
      if (scs.stroke && scs.stroke !== 'none') { b[i].setAttribute('stroke', scs.stroke); b[i].setAttribute('stroke-width', scs.strokeWidth); }
      if (scs.opacity !== '1') b[i].setAttribute('opacity', scs.opacity);
    }
    const r = src.getBoundingClientRect();
    clone.setAttribute('width', Math.round(r.width)); clone.setAttribute('height', Math.round(r.height));
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    const svg = clone.outerHTML;
    out.logoSvg = svg.length <= 60000 ? svg : null; out.logoSvgLength = svg.length;
  }

  // 9. meta
  const meta = (s) => { const m = document.querySelector(s); return m ? (m.content || m.href || null) : null; };
  out.meta = {themeColor: meta('meta[name=theme-color]'), siteName: meta('meta[property="og:site_name"]'),
              ogImage: meta('meta[property="og:image"]'), generator: meta('meta[name=generator]'),
              maskIconColor: (document.querySelector('link[rel=mask-icon]') || {getAttribute: () => null}).getAttribute('color'),
              icons: [...document.querySelectorAll('link[rel*=icon]')].map(l => l.href).slice(0, 6)};

  // the full JSON stays on the page (window.__brandProbe); browser tools cut results off near 1,000
  // characters, so the call returns a compact summary. Next: dump_probe.js, then read the page text.
  const json = JSON.stringify(out);
  window.__brandProbe = json;
  const fam = (s) => (s || '').split(',')[0].replace(/["']/g, '').trim();
  const totalChars = out.textStyles.reduce((s, t) => s + t.chars, 0) || 1;
  const totalBg = out.bg.reduce((s, x) => s + x[1], 0) || 1;
  const share = new Map();
  for (const t of out.textStyles) tally(share, fam(t.family) + ' ' + t.weight, t.chars);
  const L = out.logos[0];
  return JSON.stringify({n: json.length,
    fonts: top(share, 5).map(([k, w]) => k + ' ' + Math.round(100 * w / totalChars) + '%'),
    h: out.headings.filter((h, i, a) => a.findIndex(x => x.tag === h.tag) === i).slice(0, 3)
      .map(h => [h.tag, fam(h.family), h.weight, Math.round(h.size), h.innerColor || h.color].join(' ')),
    btn: out.buttons.slice(0, 4).map(b => [b.bg || b.before || '-', b.color, b.border || '-', fam(b.family), b.weight].join('/')),
    bg: out.bg.slice(0, 6).map(([c, a]) => c + ':' + Math.round(100 * a / totalBg)),
    text: out.text.slice(0, 4).map(x => x[0]),
    onLight: top(out.textStyles.filter(t => t.ctx === 'L').reduce((m, t) => (tally(m, t.color, t.chars), m), new Map()), 3)
      .map(x => x[0]),
    link: out.links.slice(0, 2).map(x => x[0]),
    border: out.border.slice(0, 3).map(x => x[0]),
    logo: L ? [L.tag, L.w + 'x' + L.h, (L.src || (out.logoSvg ? 'svg ' + out.logoSvgLength : '')).slice(-70),
               (L.fills || []).map(f => f[0]).join(',')].join(' ') : null,
    theme: out.meta.themeColor});
})();
