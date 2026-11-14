# Adopting a client's own template

When the client (or the agency you deliver through) has a document template, use it. Rebuilding it by eye with
this generator always drifts from the original. Three routes, cheapest first.

## Route 1: fill the template file in place (one-off documents)
For one document, or when the template changes often.
1. Copy the template; never edit the original.
2. Unpack the .docx and read `word/document.xml`, `styles.xml`, headers and footers. List the styles the template
   defines (title, headings, body, table style, caption) and the blocks it repeats (a cover, a summary box, a
   section opener, a table pattern).
3. Fill it with python-docx (`pip install python-docx`) or by editing the XML: use the template's own styles by
   name, duplicate its own example tables and paragraphs for repeated blocks, and delete its sample text.
   Never introduce a colour, font or block the template does not have. The docx skill covers XML-level editing.
4. Gates: `python3 check_docx.py out.docx --adopted` (parse, never-mention, placeholders, image widths), then
   `audit.py layout` if LibreOffice is available, and look at every page against the original.

## Route 2: theme the default layout to the template (recurring documents, simple templates)
When the template is mostly colours and fonts on a conventional layout: read its theme colours, heading colours,
table header fill and fonts from `styles.xml` and `theme1.xml`. Run `theme_from_probe.py` on a probe of the
client's site and override every value the template defines (`--accent`, `--ink`, `--panel`, `--muted`,
`--body-font`, `--title-font`). With no site to probe, copy the default theme's fields into `themes/<slug>.json`
and fill them by hand; `check_docx.py` on the preview then proves the contrast. Preview and confirm as for any
theme, and say clearly that this is the default layout in the client's colours, not their template.

## Route 3: capture the template as a generator (recurring documents, templates worth matching exactly)
The method for rebuilding a template from nothing, so documents come out identical to it without shipping the file
each time. Budget a working session.
1. **Unpack and inventory.** List every part: document, styles, settings, numbering, theme, fontTable (and its
   rels), headers and footers (and rels), media, embedded fonts. Read `sectPr`: page size, margins, header and
   footer distances, `titlePg`, which header and footer is first and which default.
2. **Outline the body.** Dump every block in order with its paragraph and run properties and table geometry
   (grid, indent, borders, cell margins, fills, row heights, vertical alignment). The repeated patterns are the
   components: name each one and note its exact values. Keep the original's render beside you
   (`audit.py render original.docx r/`).
3. **Strip, do not rewrite.** Carry styles, settings, numbering, theme, headers and footers as constants with the
   noise removed (rsids, paraIds, bookmarks, unused table styles). Replace only the variable text (titles) and the
   logo runs with placeholders. Keep the namespaces as the export wrote them.
4. **Fonts from public sources, proven by fingerprint.** Record each embedded file's name table, OS/2 weight and
   fsSelection, vertical metrics and a signature (`font_signature` in `doctemplate.py`). Find the same version
   publicly (Google Fonts statics on npm pin exact versions; Google Docs embeds the same files, minus some
   unencoded glyphs; google/fonts variable fonts can be instanced as a fallback and usually match to within outline
   rounding), rewrite the name table to the embedded one, and gate on the signatures. If a template font is
   licensed and not public, ask the client for a licence to embed it or agree a substitute.
5. **Write the generator** with one method per component, emitting the same XML pattern (same property order, same
   explicit off-values such as `<w:b w:val="0"/>`). Build the template's own sample content as a fixture script,
   with the client's sample text replaced by invented content if the generator will be shared.
6. **Golden.** Remove anything the user wants gone from the original (usually the logo) with
   `python3 make_golden.py original.docx golden.docx --image-name <part of the logo's name>`, render it and
   `audit.py snapshot golden.docx golden.json`.
7. **Audit until identical.** Render the fixture and the golden in separate `soffice` calls, pixel-compare at 100
   and 200 dpi, read the heat map, fix the component, repeat until 0 px. Then diff the normalised XML (drop
   rsids, compare leaves) so Word sees the same thing too; the only differences left should be deliberate.
8. **Stress the layout.** Build filler documents that push each block across a page foot and a showcase of every
   component; fix keep-with-next behaviour and add a layout gate.
9. **Package it**: generator, audit, fixture, golden, showcase, a components reference with the measured values,
   a document-patterns reference from the template's own content, and the gotchas below. Keep it with the
   client's files, not in a shared skill: it is their design.

## Checklist: what to look for in any template
Go through this list for every template you adopt; most templates hit only a few items.
- **Page setup**: page size, margins, header and footer distances, a different first-page header (`titlePg`),
  page-number fields (with or without a result run; without one some renderers draw the number in the default
  font).
- **Table geometry**: tables at, wider or narrower than the text column (a negative or positive indent). Keep the
  template's indent and widths exactly and set the layout gate's column limits to match.
- **Section openers drawn as tables**: LibreOffice keeps a table with a following table but not with a following
  paragraph, so a table-based heading followed by text can strand at a page foot. Render once, find those headings
  with nothing below them on their page, insert a page break before each on a separate empty 1pt paragraph (page
  breaks inside table cells are ignored), and repeat until none is left.
- **Fonts**: exports from online editors (Google Docs and similar) can store embedded fonts as plain TTF with a
  zero key, which Word ignores; re-package them the Word way (`audit-and-gotchas.md`).
- **Schema hygiene**: exports from online editors can omit `w:gutter` in `pgMar` (add `w:gutter="0"`), write
  numeric attributes as decimals (round them to integers) and carry unused styles (drop them). Run an OOXML
  validator once on the rebuilt output.
- **Images and shapes**: check how the logo and decorative shapes are anchored (inline or floating, and whether
  any is duplicated) and what fallback picture a shape carries; a pixel compare against the original shows any
  difference.
- **Lists**: the numbering definitions behind bullets and numbered lists.
