# Components: tokens, roles, page furniture and every block

The neutral default layout that `data/doctemplate.py` builds. Twips in the XML (1pt = 20 twips, 1in = 1440),
points in the render, `sz` in half-points. A theme changes the colour roles and the fonts below and nothing
else: every size, spacing and measurement on this page holds in every theme.

## Design principles of the default
- Quiet and printable: white page, one accent, hairline rules, no filled bars across the page.
- Hierarchy through type and a stripe, not through boxes: numbered sections are shaded paragraphs with a 3pt
  stripe on the left; tables carry horizontal hairlines only.
- Real Word styles (Title, Heading 1 to 3, Caption) so the navigation pane, a table of contents and screen
  readers see the structure.
- Everything aligns to the text column: tables are exactly the text width, images never exceed it.

## Layout tokens
| Token | Value |
|---|---|
| Page | US Letter 12240 x 15840 (default) or A4 11906 x 16838: `Doc(page='a4')` |
| Margins | top 1440, bottom 1296, left 1440, right 1440; header 600, footer 560 |
| Text column | page width minus 2880 (9360 twips on Letter, 9026 on A4) |
| First page | its own header (logo only, or empty) via titlePg; page numbers start at 1 |
| Tables | exactly the text width, indent 0, fixed layout; cell margins 70 top and bottom, 115 left and right |
| Rules | 0.5pt (`sz` 4) in `rule`, above, below and between rows; no vertical rules |
| Body | 11pt (`sz` 22), line 1.15 (276 auto), 7pt after |
| Table text | 10pt (`sz` 20), single line spacing |
| Type scale | title 24pt, lead 12pt, section 14pt, subsection 12pt, minor heading 11pt, caption 10pt, meta 9pt, notes and sources 8.5pt, header and footer 8.5pt, chips 7.5pt caps |
| Default fonts | Source Sans 3 400 (body), Source Sans 3 700 (strong), Source Serif 4 700 (title) |

## Colour roles
| Role | Default | Drawn on |
|---|---|---|
| `ink` | 1D2630 | Body, lead, table text, section and subsection labels |
| `title` | 1D2630 | The document title |
| `muted` | 59636E | Meta line, notes, source lines, sub-captions, header and footer text |
| `panel` | EEF1F4 | Section heading shading, fact-table label column, zebra rows, Keep chip |
| `rule` | BFC6CE | Table hairlines, subsection underline, header and footer rules, image edges |
| `accent` | 2B5F8A | Table header rows, New chip |
| `accent_text` | FFFFFF | Text on `accent` |
| `stripe` | 2B5F8A | The section stripe and the lead's left rule |
| `number` | 2B5F8A | Section and subsection numbers, figure numbers, first-level bullets (must read on `panel`) |
| `alert` | A4262C | Remove chip only |

Status chips (`status` map, fill / text): Keep EEF1F4 / ink, Rework F4E2B8 / ink, New accent / white, Remove
A4262C / white, Optional white / muted with a muted outline, Later DDE2E7 / ink. Later marks a block that waits
for content only the client can supply. Every pair reads at 4.5:1 or better; `check_docx.py` and `audit.py theme`
prove it for any theme.

## Fonts
Font roles: `title`, `body`, `strong`, optional `section` (a brand's label face for section headings, with
`"caps": true` for capitals). Weight 400 and 700 are the family itself (700 as its bold); any other weight
becomes a family of its own, the convention Word and Google Docs exports share ("Source Sans 3 SemiBold"), with
the family's 700 as its bold face. The body font is embedded with italics; the others regular and bold.

Fonts come from Google Fonts: the static TTFs published on npm (`@expo-google-fonts/<family>`, exact versions
pinnable), with the google/fonts variable font instanced at the weight as a fallback. Each face's name table is
rewritten so nameID 1 equals the font name the runs use (renderers find faces by that name; a mismatch falls
back to another face and every line reflows). They are embedded the way Word writes them: obfuscated `.odttf`
parts with a key per font (ECMA-376 17.8.1), and each `w:font` entry carries PANOSE, family class, pitch and
code-page data, so a viewer that cannot use embedded fonts substitutes a sans for a sans and a serif for a serif.

## Page furniture (built for you)
- **Running header** (page 2 on): the short title on the left, the client on a right tab, 8.5pt muted, with a
  hairline rule under it. `Doc(short_title=..., client=...)`.
- **First-page header**: empty, or the logo top left, scaled to fit a 1.5 x 0.6in box (`Doc(logo='mark.png')`;
  `logo_box=(w, h)` in inches sets another box).
- **Footer** (every page): "<client> · <short title>" on the left (`footer_text=` overrides), "Page N" on a
  right tab, hairline rule above. The PAGE field carries a result run in the footer's style so every renderer
  draws the number in the footer font.

## Blocks (Doc API)
Construct: `d = Doc(short_title, client='', theme=None, page='letter', logo=None, img_dir=None,
embed_fonts=True, font_cache=None, jpeg_over=250000, footer_text=None, logo_box=(1.5, 0.6))`.
Inside a build script `d.t` is the theme (`d.t.client`, `d.t.meta_by()`, colours and fonts).
Markup in every text argument: `**bold**`. In table and fact cells, `\n` starts a new paragraph and a line
starting with `~` becomes a muted 8.5pt note.

| Call | Look | Spacing (twips) | Use for |
|---|---|---|---|
| `title(text)` | Title font 24pt, `title` colour, Title style | after 100 | The outcome or the ask, one line |
| `meta(parts)` | 9pt muted, parts joined by " / " (empty parts dropped) | after 280 | kind, client, prepared by/for, date |
| `lead(text)` | 12pt ink behind a 2.25pt `stripe` rule, indented 11pt | after 320 | The ask or the answer in 2 or 3 sentences |
| `section(label, new_page=False)` | Heading 1: `panel` shading, 3pt `stripe` on the left, number in `number`, label 14pt strong (or the section font) | before 400 (200 on a new page), after 160 | Every section; numbered 1, 2, 3 automatically |
| `appendix(label, new_page=True)` | As a section, lettered A, B, C | as section | Appendices after the numbered sections |
| `subsection(label, status=None)` | Heading 2: "2.1  Label" 12pt strong over a hairline, optional status chip on a right tab | before 280, after 120 | Second level, one per item reviewed |
| `minor(text)` | Heading 3: strong 11pt, kept with next | before 200, after 80 | A caption over a second table or list in one section |
| `facts(pairs, label_w=0.3)` | Two columns: label in `panel`, bold; value beside it | rows hairline-ruled | Facts, specs, "What it is / Verdict", problem and fix |
| `table(header, rows, widths=None, status_col=None, label_col=False, bold_first=False, sz=None, zebra=False)` | Header row in `accent` with `accent_text`, repeats on each page; body rows hairline-ruled; widths are relative weights | rows cantSplit | Steps, comparisons, recommendations, any grid |
| `body(text, before=None, after=140)` | 11pt ink; 6pt above automatically right after a table or figure | after 100 between paragraphs of one section, 0 on the last line | Prose between blocks, short |
| `bullets(items, level=0)` / `numbered(items)` | Bullet in `number`, text at 0.25in | 60 between items, 160 after the last | Short lists inside a section |
| `note(text)` | 8.5pt muted | after 140 | Caveats, asides |
| `figure(path, finding, source=None, max_h=4.0, width=None, frame=True)` | "Figure N.  finding" 10pt strong above (number in `number`), image centred with a 0.5pt `rule` edge, "Source: ..." 8.5pt muted below | caption before 240 after 100; source before 80 after 200 | Screenshots, wireframes, charts |
| `figure_pair(left, right, finding, source=None, max_h=3.0)` | Two images side by side in a borderless table, bottom-aligned, muted sub-captions | as figure | Before/after, two exemplars |
| `gap(pt=6)` | Empty exact-height line | | Air where a block needs it |
| `page_break()` | Empty 1pt paragraph with a page break before | | Force the next block to a new page |

Notes:
- Two tables in a row are always separated by a 6pt gap paragraph (the builder inserts it): Word and most
  previewers join adjacent tables into one, which reads as a merged table.
- A figure's image paragraph keeps with its source line, so a source never opens the next page alone.
- Screenshots over 250 KB with more than 1,000 colours are stored as JPEG quality 86; diagrams stay PNG.
- Column widths: task lists `[1, 9, 3, 4]`, two-way comparisons `[3, 7, 7]`, recommendation tables
  `[1, 6, 2, 7]` with `status_col=2`. Fact label share: 0.3 for sentence labels, 0.22 for one or two words.
- Bold sparingly inside a table: at most the one value per row the reader has to act on.
- Output is byte-deterministic (fixed zip timestamps): the same script gives the same file, so two builds
  can be diffed.

## Wireframes and diagrams in the document's look
`data/wirekit.py`: `Wire(theme, width, height)` loads the theme's colours and the same font files the document
embeds, and gives `header(title, statuses=[...])` (title plus a legend of the statuses used), `navbar(y, label)`,
`box(x0, y0, x1, y1, status, title, lines)` (left stripe, status chip, wrapped title, muted lines; Remove and
Optional dashed, New tinted with the stripe), `chip()`, `dashed()`, `text()`, `wrap()`, `arrow_down()` and
`save(path, bottom)`. For other diagrams, draw with Pillow using `d.t.font_files()` and only the theme's roles.
The `on-brand-diagram-generation` skill covers diagrams in depth.

## Low-level helpers (for a block that is not in the set)
`run(text, font, bold, color, sz, italic, caps, bdr, shd)`, `rich(text, **kw)`, `para(runs, style, before,
after, line, keep_next, keep_lines, page_break, num, pbdr, shd, tabs, ind, jc)`, `border(side, color, sz,
space)`, `cell(width, paras, fill, valign, span)`, `row(cells, header)`, `table_xml(widths, rows, rule,
borders)`, then `d._add(kind, xml, text)` (pass the plain text so the never-mention check sees it). Property
order follows the OOXML schema (`rPr`: fonts, bold, italic, caps, colour, size, border, shading; `pPr`: style,
keeps, page break, numbering, borders, shading, tabs, spacing, indent, alignment). Add a new block to
`doctemplate.py` and to this table rather than writing XML in a build script, then rebuild `showcase.py` and
re-run the gates.
