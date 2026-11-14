/* Render a mock HTML file to a full-page PNG at the live page's real CSS width, so it is 1:1
   comparable with the reference screenshot from the browser.
   usage: node render.js <htmlPath> <outPng> [width=1280] [height=1200]
   Chromium: Playwright's bundled browser by default; set PW_CHROMIUM to use another binary. */
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const html = path.resolve(process.argv[2]);
  const out = process.argv[3];
  const W = parseInt(process.argv[4] || '1280', 10);
  const H = parseInt(process.argv[5] || '1200', 10);
  const launch = { args: ['--no-sandbox', '--font-render-hinting=none', '--force-color-profile=srgb'] };
  if (process.env.PW_CHROMIUM) launch.executablePath = process.env.PW_CHROMIUM;
  const browser = await chromium.launch(launch);
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto('file://' + html, { waitUntil: 'networkidle' });
  await page.evaluate(() => (document.fonts ? document.fonts.ready : null));
  await page.waitForTimeout(2000);
  await page.screenshot({ path: out, fullPage: true });
  await browser.close();
  console.log('rendered ->', out, W + 'x' + H);
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
