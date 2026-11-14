/* Run the SAME probe (probe.js) against the mock with Playwright and write the spec JSON:
   the mock side of the metrics gate (metrics_parity.py).
   usage: node mock_extract.js <htmlPath> <outJson> [width=1280]
   Uses PROBE_CONFIG from probe.js, so set the labels there once for both sides.
   Chromium: Playwright's bundled browser by default; set PW_CHROMIUM to use another binary. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const html = path.resolve(process.argv[2]);
  const out = process.argv[3];
  const W = parseInt(process.argv[4] || '1280', 10);
  const src = fs.readFileSync(path.join(__dirname, 'probe.js'), 'utf8')
    .replace(/if \(typeof module[\s\S]*$/, ''); // drop the Node export tail before injecting
  const launch = { args: ['--no-sandbox', '--font-render-hinting=none', '--force-color-profile=srgb'] };
  if (process.env.PW_CHROMIUM) launch.executablePath = process.env.PW_CHROMIUM;
  const browser = await chromium.launch(launch);
  const page = await browser.newPage({ viewport: { width: W, height: 1200 }, deviceScaleFactor: 1 });
  await page.goto('file://' + html, { waitUntil: 'networkidle' });
  await page.evaluate(() => (document.fonts ? document.fonts.ready : null));
  await page.waitForTimeout(1500);
  const spec = await page.evaluate(src + '\n; extractSpec();');
  fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
  fs.writeFileSync(out, JSON.stringify(spec, null, 2));
  await browser.close();
  console.log('mock spec ->', out);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
