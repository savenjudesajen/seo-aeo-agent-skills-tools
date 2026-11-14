# On-template figure design

Contents: The rule · The three figure patterns · Placement · Caption and source wording · Neutral default tokens · Token file

How a screenshot becomes a figure that belongs in the target document. Load this at step 3, after the
crop and before any placement.

## The rule

A figure inherits the document's grid. If the document's tables are 9360 dxa wide, not indented, with
0.5pt grey borders and 115 dxa cell margins, then the figure frame is 9360 dxa wide, not indented, with
0.5pt grey borders and 115 dxa cell margins. Nothing is chosen; everything is measured.

Measure first, every time:

```bash
python3 <skill>/data/extract_docx_design.py client-brief.docx
python3 <skill>/data/extract_docx_design.py client-brief.docx --json > figure-tokens.json
```

The three tokens that decide whether the figure looks commissioned or pasted:

| Token | Where it comes from | Why it matters |
|---|---|---|
| grid width + indent | the dominant `tblW` / `tblInd` in the body | a figure even a few tenths of an inch narrower than the tables above it is visible at a glance |
| border weight + colour | the dominant table border `w:sz` / `w:color` | a heavy grey frame next to hairline black tables reads as a foreign object |
| caption font | the run properties on the existing `Table N.` / `Figure N.` captions | the figure caption and the table caption must look like the same object |

Units: `dxa` = twentieths of a point; 1440 dxa = 1 inch. `w:sz` on a border = eighths of a point, so
`sz=4` is 0.5pt and `sz=8` is 1pt. `w:sz` on a run = half-points, so `sz=20` is 10pt.

## The three figure patterns

### A. Single figure (default)

```
Figure 3. What the reader should notice          <- caption, document's caption formatting
+---------------------------------------------+
|                                             |  <- one-cell table on the document's grid,
|              [ screenshot ]                 |     document's border weight and colour,
|                                             |     image centred, width = grid - 2x cell margin
+---------------------------------------------+
Source: domain/path, Month YYYY                  <- body font, small, muted colour
```

Use for: one competitor section, one SERP feature, one page state.

### B. Two-up comparison

Same frame, two cells. Each image gets a sub-caption inside its own cell naming the domain. The caption
states the comparison, not the contents. Use when the point is a difference: ours vs theirs, before vs
after, desktop vs mobile.

Images render at roughly half width, so each crop must be legible small; crop tighter than you would for
a single figure.

### C. Banded figure

Pattern A or B with a full-width header row above the image(s). Use when a run of figures needs its own
labelled block ("Competitor reference", "Sections we are missing") so a designer can find them without
reading the prose.

If the document already has a section band (a full-width shaded row it uses for its own labels), copy it:
same fill, same run font, size and colour, same row height, same vertical alignment. If it has none, use
the neutral band below, or skip the band. Don't invent a decorative band a template doesn't have.

Some templates put a heading style (for example Heading 1) on their band rows. Copy the band's look, not
its style: a heading style on a figure band puts the band text into the document's table of contents.
The inserter writes band text as direct formatting for this reason.

## Placement

- The figure goes **with the section it proves**, not in an appendix. A designer reading the section
  should not have to scroll to find the reference.
- Caption, frame and source are kept together: `keepNext` on the paragraphs that lead into the frame and
  `cantSplit` on the frame's rows, so the block never breaks across a page.
- Caption position follows the document: if its table captions sit above, put figure captions above; if
  it puts captions below images, do the same. With no precedent, above is the inserter's default.
- For a page or section recommendation: one figure per missing section, showing where a competitor runs
  it.
- Number figures in reading order. The inserter counts the figure captions before the anchor and warns
  if figures after it now need renumbering. For long documents, Word `SEQ Figure` fields renumber
  automatically; if the template already uses them, keep using them.

## Caption and source wording

- Caption: `Figure N. <what the reader should notice>`. It carries the finding.
  - Good: `Figure 3. The competitor shows the price in the first screen.`
  - Bad: `Figure 3. Competitor pricing page.`
- Source: `Source: <domain/path>, <Month YYYY>`.
- No capture narration anywhere: no "captured live", no "screenshot taken via", no tool names. State the
  finding and the date it was checked.

## Neutral default tokens

These are the defaults in `data/insert_figure.py`. They suit a plain Letter document with 1in margins and
are meant to be overridden. Use the client's own template if they have one: measure it and pass its
tokens.

| Token key | Default | Meaning |
|---|---|---|
| `grid_width` | 9360 | frame width in dxa (6.5in: Letter 8.5in minus two 1in margins) |
| `grid_indent` | 0 | frame indent in dxa (negative values bleed left of the text column) |
| `cell_margin` | 115 | cell padding in dxa, all four sides |
| `border_size` | 4 | border weight in eighths of a point (0.5pt) |
| `border_color` | `BFBFBF` | light grey |
| `caption_font` | null | null = inherit the document's font |
| `caption_size` | 20 | half-points (10pt) |
| `caption_color` | `262626` | near-black |
| `caption_bold` | true | |
| `caption_style` | null | a paragraph style to apply first, e.g. `Caption`, so Word's table of figures picks it up |
| `body_font` | null | font for the source line and sub-captions; null = inherit |
| `source_size` | 16 | half-points (8pt) |
| `muted_color` | `595959` | source line and sub-caption colour |
| `band_fill` | `F2F2F2` | band row fill |
| `band_color` | `262626` | band text colour |
| `band_size` | 20 | band text size in half-points |
| `band_height` | 400 | band row minimum height in dxa |
| `max_image_height_in` | 8.0 | caps tall images so caption, frame and source fit on one page |

The image width is derived, not set: `(grid_width - 2 x cell_margin) / 1440` inches for a single figure,
split across the cells for a two-up.

## Token file

`extract_docx_design.py --json` writes a file with the keys above, filled from what it measured, and
leaves anything it couldn't measure out, so the default applies. If the document has no table width to
copy, `grid_width` falls back to the text column (page width minus the left and right margins). Edit
the file by hand where the extractor guessed wrong, then pass it with `--tokens`. Any single key can
also be overridden on the command line (`--grid-width`, `--border-color`, ...). Precedence: command-line flag > token file > default.

Keep one token file per client template, stored with that client's project files, not in this skill.
When a template changes, re-measure; don't patch the old file from memory.
