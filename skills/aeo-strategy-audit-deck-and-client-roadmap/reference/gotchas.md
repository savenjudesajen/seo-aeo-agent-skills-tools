# Gotchas (read before analysis)

Contents: 1. Verify schema from RAW HTML, never from a tool flag (the expensive one) · 2. Never fabricate a number · 3. Decks: condensed is 15 slides or fewer (aim for about 10) · 4. Roadmap months are "Month 1..N", never real dates · 5. Competitors: use the review site's category grid, not its "alternatives" list · 6. python-pptx · 7. openpyxl · 8. Editing a deck the client has already commented on (Google Slides) · 9. Prompt-tracker import shape · 10. Additive editing creates duplicate slides. Run the de-dup gate. · 11. Keyword-tool UI exports

These are the failure modes that cost the most when they reach a client.

## 1. Verify schema from RAW HTML, never from a tool flag (the expensive one)

Telling a client their schema "renders client-side, AI crawlers can't see it" because an SEO tool said so,
and then having to walk it back in the room, is the most expensive mistake in this skill.
- Flags like `has_micromarkup` (DataForSEO and similar APIs) track **Microdata** (itemscope / itemprop),
  NOT JSON-LD. Modern sites use JSON-LD, so the flag is false even when schema is present and
  server-rendered.
- A crawl with structured-data extraction switched off (or a headless crawl setup that does not store it)
  reports zero JSON-LD sitewide. That is a config state, not a finding.
- Correct method: fetch the raw HTML and look for `<script type="application/ld+json">`. Run
  `data/check_schema_raw_html.js` in the browser console on the page (or through a browser-automation
  tool's JavaScript execution). For sitewide coverage, fetch every sitemap URL and count.
- Check for a service worker first (`navigator.serviceWorker.getRegistrations()`): a browser fetch can
  return an intercepted, hydrated response and mislead you. Confirm with View Source when in doubt.
- Report what IS present before what is missing. Many sites already ship Organization + WebSite +
  Product/Service + FAQPage. The real (smaller) win is usually missing **AggregateRating / Review /
  BreadcrumbList / WebPage**. Pitch enrichment, not "blocked for AI".
- Nuance for the room: Google renders JavaScript, so client-side-only schema hurts AI answer engines more
  than classic search.
- **Pick the type for what the client actually is.** Use the industry subtype rather than bare
  `Organization` where schema.org has one (a law firm is `LegalService`, a dental practice `Dentist`; see
  schema.org's `LocalBusiness` subtypes). Ask whether the offering is a **service or a product** and type it by what is sold, not by how it
  is accessed (a browser-based service is still a `Service`). Add only types that describe something on
  the page. Mark up people only when they are actually named on the site.

## 2. Never fabricate a number

Every figure traces to a source. If you don't have it, say so (in chat). Label fresh AI-visibility reads
"directional". A confident wrong number is worse than an honest gap.

## 3. Decks: condensed is 15 slides or fewer (aim for about 10)

Clients reject long decks. Build the long form for the argument and the appendix, but the deliverable they
approve is the condensed cut. Consolidate aggressively.

## 4. Roadmap months are "Month 1..N", never real dates

The workbook is reused per prospect. Real months force a manual update every time.

## 5. Competitors: use the review site's category grid, not its "alternatives" list

An "alternatives" page is co-occurrence noise: it can lead with a brand from a different category
altogether. The category grid gives real positions (leader, contender and so on) and ratings. Validate
every auto-suggested competitor DOMAIN before adding it: suggestion engines sometimes propose a personal
blog or a reseller as a competitor's domain.

The "who the review site says competes" set and the "who AI co-mentions" set diverge. That divergence is
an insight, not an error; put it on a slide.

## 6. python-pptx

- Deleting a slide via `sldIdLst` must ALSO drop its relationship (`prs.part.drop_rel(...)`) or the file
  corrupts in some viewers. Deleting and then ADDING in the same run is worse: part names get reused and
  you get duplicate-relationship warnings plus duplicated slides. If you need idempotency, rebuild the deck
  from the template instead of dropping and re-adding.
- Card / autoshape text defaults to a MIDDLE vertical anchor; set `vertical_anchor = MSO_ANCHOR.TOP` or the
  content floats.
- A title that wraps to two lines collides with the subtitle. Shorten it or move text down.
- Bottom one-liners clip at the slide edge past about 110 characters.
- Build in ONE script run with ONE `prs.save()` when you start from a stripped template: re-opening and
  re-saving a stripped template duplicates parts. (An engagement that edits an intact template can safely
  run an ordered chain of scripts that each re-open and re-save.)
- Some file-writing tools truncate or mangle long files at em dashes and other multibyte characters. Use
  plain hyphens in source, write long files in one pass, and parse the file (`python3 -c "import ast;
  ast.parse(open('build.py').read())"`) before trusting it. A build that RUNS is not proof the source is
  complete: a stale `.pyc` can mask a truncated file.
- **Template tables have a FIXED row count and silently DROP extra rows.** Read `len(table.rows)` before
  writing and assert your data fits. Nothing errors; the rows just vanish.
- **python-pptx reports meaningless table heights**, so overflow is invisible until rendered. Keep cells
  under about 50 characters, set explicit `row.height`, and prove it with a render.
- **Empty template cells can carry NO run formatting** (`font.size is None`). Text written into them
  inherits PowerPoint's 18pt black default, invisible on a dark header. After filling a table, clone the
  `rPr` XML from a formatted donor run in the same row.
- **Check every table for an unused trailing column.** A 4-column table filled with 3 columns of data reads
  as a mistake.
- Rendering to PDF then PNG and actually LOOKING at the slides is the only real layout proof:
  `soffice --headless --convert-to pdf deck.pptx`, then `pdftoppm -png -r 110 deck.pdf slide`.
- **Charts: use a native chart, not drawn shapes or an image.** `shapes.add_chart(...)` with
  `CategoryChartData` stays editable, takes per-point colours, and lets the client adjust it without coming
  back to you. Turn the chart title off (the slide has one), put the legend at the bottom, and set the
  legend font explicitly (charts do not reliably inherit theme fonts). Note in the presenter notes that the
  chart is editable.
- **When the reviewer sends a list of fixes, add them to the build script and re-run from clean.** Never
  hand-patch the delivered file: patching is how slides get dropped and re-added, which is the corruption
  path above. If a fix deletes a slide, make that the **last** operation before save.

## 7. openpyxl

- Load with the default (NOT `data_only=True`) or you permanently replace formulas with values on save.
- Copying a sheet ACROSS workbooks: copy the style OBJECTS (`font`, `fill`, `border`, `alignment`,
  `number_format`), NOT `cell._style`, which is an index into the source workbook's style table and means
  something else in the target.
- Within the SAME workbook, `copy(cell._style)` is fine and is the cheap way to make appended rows look
  native.
- Always recalculate formulas (LibreOffice headless) and confirm zero `#REF!` / `#DIV/0!` before
  delivering.

## 8. Editing a deck the client has already commented on (Google Slides)

Use Find and Replace for partial text edits (it preserves run formatting). Always check the match count
before "Replace all": a generic phrase like "90 days" appears in many places and you will corrupt slides
you never looked at. The editor can freeze; reload the tab to recover. Don't reply to or resolve comment
threads unless asked.

## 9. Prompt-tracker import shape

Trackers and tracking APIs expect a fixed object shape per prompt (at minimum the prompt text; often
optional topic, tags and a brand vs category type). When importing from a sheet, map the columns to that
shape BEFORE the call, or the import fails or silently drops fields.

## 10. Additive editing creates duplicate slides. Run the de-dup gate.

The failure mode: you build a deck, then a later pass adds slides (competitor, content, a new analysis)
and never reconciles them against what is already there. Each new slide is individually fine, so nothing
looks wrong while you write it. The result is duplicate pairs, e.g. the same table in two sections or an
actions slide that repeats the closing slide. Typically the reviewer finds them, not the builder.

This bites hardest in the long-form to condensed cut, where slides are merged and re-ordered.

**Adding a slide is a merge, not an append.** Before adding, ask what already covers this material:
extend the existing slide, replace it, or make the new one genuinely distinct.

Run `python3 data/dedupe_audit.py <deck.pptx>` before delivery. It checks repeated substantive strings,
near-duplicate slides (over 45% distinctive-token overlap), and stale status text ("early data", TBC,
TODO left in after the data landed).

Resolving a duplicate, in order of preference: delete the weaker slide; repurpose the weaker slide into
the distinct point it was reaching for; or split by altitude, one slide for the concept and one for the
instance, never both.

## 11. Keyword-tool UI exports

- Some export buttons **ignore the first click**: the dropdown does not open. Hover the button, wait
  about a second, then click, then pick the format.
- Browser downloads may land in a folder you cannot read (a save dialog the automation cannot operate).
  Do not burn turns debugging it. Either read the on-screen report directly (the page text holds the full
  table) or ask the user to hand the files back. Ask; do not guess.
- Exports are row-capped (tens of thousands of rows). That is fine for analysis on large estates, but say
  so rather than implying you have everything.
