# Audit loop and gotchas

## The checks
| Check | Command | Pass | What it proves |
|---|---|---|---|
| Fonts | `python3 doctemplate.py --fonts [themes/<slug>.json]` | `FONT GATE PASS` | Every embedded face has nameID 1 equal to the font name the runs use, the right weight and italic flags, covers the ASCII set (warns on missing typographic characters), and matches the signatures pinned when the theme was confirmed |
| Docx check (offline, stdlib) | `python3 check_docx.py out.docx [theme]` | `DOCX CHECK PASS` | XML parses; fonts and colours inside the theme; contrast 4.5:1; no never-mention name; one title; sections and subsections numbered in order; header, footer and page number present; images inside the column; no placeholder text |
| Layout | `python3 audit.py layout out.docx --out lay/` | `LAYOUT PASS` | No heading or caption alone at a page foot, no stub page before the last, nothing outside the text column; writes a colour contact sheet to look at |
| Theme | `python3 audit.py theme out.docx themes/<slug>.json` | `THEME PASS` | Every font drawn in the render is the theme's (no fallback), every fill and text colour is in the palette, contrast, never-mention |
| Geometry | `python3 audit.py verify sample.docx golden.json` | `GEOMETRY PASS (0 differences)` | The fixture still renders where your approved build did, to 0.5pt, with the same font, size and colour |
| XML | `python3 audit.py xmlcheck sample.docx golden.json` | `XML PASS` | The generator still writes the fixture's parts byte for byte (fonts and media excluded) |
| Pixel | `audit.py render a.docx ra/`, `render b.docx rb/`, `compare ra/ rb/ --out d/` | `PASS` (0 px) or `NEAR` | Two builds look identical; read the heat map (red = only in A, blue = only in B) |
| Schema (optional) | an OOXML validator, e.g. the docx skill's validate script | passes | Word will not complain about the file |

`check_docx.py` needs nothing but Python. The render checks need LibreOffice (`soffice`), poppler (`pdftoppm`)
and the Python packages `pdfplumber`, `numpy` and `Pillow`. When LibreOffice is not available, run the docx check,
say the render checks were skipped, and ask the user to open the file once before sending it on.

## Your own golden (regression for the generator)
The skill ships no golden: renders differ between LibreOffice versions, so a golden is only meaningful on the
machine that made it.
1. Build the fixture: `python3 doctemplate.py --sample sample.docx`.
2. Render and look at every page (`audit.py layout sample.docx --out lay/`). When it is right:
   `python3 audit.py snapshot sample.docx golden.json` (geometry of the render plus XML hashes; the LibreOffice
   version is recorded in `about`).
3. After any change to `doctemplate.py`, rebuild the fixture and run `verify` and `xmlcheck`. A change meant to
   alter the layout fails both on purpose: look at the new render, then snapshot again.

## Reading a failure
- `GEOMETRY FAIL` with every line "moved +0.0pt x, -2.0pt y" below some point: a spacing value changed in the block
  just above the first moved line.
- "text restyled [...] -> [...]": colour, size or font of that block changed. A font such as `DejaVuSans` or
  `LiberationSans` means an embedded font was not picked up: run the font gate.
- "text missing or reflowed": a line broke differently. Usually a font (advances or kerning), sometimes a width.
- Many small differences on another machine, all under 1pt, with the font gate passing: a different LibreOffice
  version (`soffice --version`, compare with `about` in the golden). Judge the pages by eye and make a new
  golden on that machine. The XML check still has to pass.
- `XML FAIL` after you edited `doctemplate.py`: you changed a part. Revert, or if the change was meant, snapshot.
- `LAYOUT FAIL stranded`: a heading or caption ended a page. Headings keep with the next paragraph, so this
  usually means a block that cannot split (a large figure, a long unsplittable row) follows it: shrink the
  figure's `max_h`, or `page_break()` before the heading.
- `stub page`: a keep chain pushed a block over. Shrink the figure on the page before or drop a forced `new_page`.
- `WARN thin page` (under 35% full): usually the last rows of a table or a small figure spilled over. Look at it;
  starting that section with `new_page=True`, or letting the next short section flow onto the page, fixes it.
- `THEME FAIL` "fonts outside the theme (fallback?)": rerun `--fonts`; "reads at 3.9:1": a colour was edited by
  hand, rerun `theme_from_probe.py` with an override; "mentions ...": remove the name (`save()` already refuses).
- `DOCX CHECK FAIL` "placeholder text left in": a TODO, lorem ipsum, XX, a bracketed placeholder or "Client Name"
  survived. Fill it or cut it.

## Gotchas
- **Word ignores fonts packaged the Google Docs way.** Google Docs exports store embedded fonts as plain TTF with an
  all-zero key; LibreOffice and previewers accept that, Word does not and sets the whole document in Times New
  Roman. Embed fonts the way Word writes them (obfuscated `.odttf`, a real key per font, PANOSE and code-page data
  in the font table), as `doctemplate.py` does. LibreOffice and previewers read that too.
- **Adjacent tables merge.** Two tables with no paragraph between them render as one table in Word and in most
  previewers (and Word joins them when edited). The builder always puts a small gap paragraph between them.
- **The page number needs a result run.** A PAGE field with no result run is drawn in the document default font
  and size by LibreOffice. The footer field carries a run in the footer's style.
- **Font names matter more than files.** Renderers resolve a font through the embedded file's nameID 1. If it does
  not equal the name in the runs ("Source Sans 3 SemiBold" for a 600 weight), the renderer falls back to another
  face and every line reflows. Both font gates check it.
- **One file per LibreOffice call.** Fonts embedded in one document stay active for every later document converted
  in the same `soffice` call: a file without embedded fonts, converted after one with them, still renders in the
  embedded fonts. `audit.py` converts one file per call in a fresh profile, so a missing embed shows up as a
  fallback font.
- **Page breaks inside table cells are ignored** by LibreOffice. `page_break()` uses a separate empty 1pt paragraph.
- **Heading text in the PDF does not match the XML exactly**: the PDF text layer may escape apostrophes, curly
  quotes differ, chips render in capitals. The layout gate normalises escapes, quotes, no-break spaces and case
  before matching.
- **The pixel compare renders in greyscale**; the layout contact sheet is in colour so themes can be checked by eye.
- **Determinism.** Zip entries carry a fixed timestamp, so the same script gives the same bytes: diff two builds
  to see what changed.
