/* dump_probe.js (doc-template-design): read-back helper for brand_probe.js.
   Browser tools cut a script's return value off near 1,000 characters, so brand_probe.js keeps its full JSON
   on the page (window.__brandProbe). Run this in the same tab afterwards: it replaces the tab's copy of the
   page with that JSON as plain text between two markers. Then use your browser tool's page-text read and save
   the text between BRAND_PROBE_JSON and END_BRAND_PROBE_JSON as probes/<slug>_<page>.json.
   Nothing on the site changes; reload the tab to get the page back. */
(() => {
  const json = window.__brandProbe;
  if (!json) return 'nothing to dump: run brand_probe.js on this page first';
  document.head.innerHTML = '';
  for (const attr of ['class', 'style']) document.body.removeAttribute(attr);
  document.body.innerHTML = '';
  const block = document.createElement('pre');
  Object.assign(block.style, {whiteSpace: 'pre-wrap', wordBreak: 'break-all'});
  block.textContent = 'BRAND_PROBE_JSON ' + json + ' END_BRAND_PROBE_JSON';
  document.body.appendChild(block);
  return 'dumped ' + json.length + ' characters; now read the page text';
})()
