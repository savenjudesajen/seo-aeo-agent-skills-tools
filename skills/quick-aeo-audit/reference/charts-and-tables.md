# Charts, tables and extra insight slides

Build charts as native PowerPoint charts with `add_bar_chart`
(`data/deck_helpers.py`), on native slides with matching chrome. Native charts
keep brand names and values as text in the deck and in its PDF, so they stay
searchable and the gate (`data/deck_qc.py`) checks their categories for dashes,
stale names and tool names. `voice_sweep` doesn't reach chart text, so pass clean
category names. Use the matplotlib PNGs in
`data/sov_chart.py` only to fill a picture frame in a client's template
(path A). Both files share one neutral palette. If the client's template has its
own brand colours and font, change the constants at the top of both files to
match; otherwise keep the defaults.

## Default chart style (neutral)

- accent (client / opportunity highlight): `#2563EB`
- grey (competitors / neutral): `#B8BEC6`; faint grey (zero values): `#DDE1E6`
- dark text: `#1F2933`; muted text: `#5F6B7A`; positive value label: `#166534`
- grid: `#EEF0F3`; white background; title left-aligned, bold, ~16pt
- charts at the content width, about 3.5-4.5 in tall (PNGs for path A at 150
  dpi, at the frame's aspect ratio); client bar in the accent colour,
  competitors grey; value labels bold at the bar end

## The four slides worth adding

Each chart below is `add_bar_chart` on path B; the name after it is the matching
`data/sov_chart.py` function for a template's picture frame on path A.

1. Category share of voice (the signature chart): horizontal bar, one bar per
   brand, client in the accent colour. A caption under the chart states the
   denominator ("across N non-branded category prompts, single-run baseline").
   Path A: `sov_bar`.
2. Keyword gap by theme: horizontal bar of untapped monthly search volume per
   non-brand theme (the category's sub-topics), `number_format='#,##0'`. All bars
   in the accent colour: they are all opportunities. The caption notes that
   brand terms are excluded. Path A: `theme_bar`.
3. Competitor Pareto: columns (`horizontal=False`) of the incumbent's top-5
   pages' share of organic traffic, all grey to signal "navigational, not
   category content". The title states the punchline with the real figure ("Top
   5 pages = N% of traffic, all navigational"). Path A: `pareto_bar`.
4. Prompt-performance TABLE: Prompt | Stage | Who AI names today | Client?, with
   the Client? column coloured red / amber / green. This is the strategy on one
   slide.

## Adding a native slide with chrome (do NOT clone)

Cloning breaks image relationships (`gotchas.md` #12). Instead:
1. `add_blank_slide(prs)` adds a slide on the blankest layout (fewest
   placeholders, `blank_layout(prs)`) and removes any placeholders.
2. Path B: `add_chrome(prs, slide, title, logo_path=None, footer_text=...,
   kicker=None)` draws the default chrome from `deck-layout.md`: an optional
   accent kicker, the dark title at the left margin, a short accent rule, an
   optional logo top-right (the client's logo), a thin rule above the footer, a
   footer bottom-left ("Confidential" by default) and a page-number placeholder
   bottom-right. Path A: redraw the template's own chrome elements instead
   (the logo already in their template, its header and footer style).
3. Below `CONTENT_TOP`, at the content width (slide width minus both margins):
   a native chart with `add_bar_chart(slide, left, top, width, height,
   categories, values, colors, number_format=...)` (one colour per bar: the
   client in `ACCENT`, competitors in `GRAY`; `'0.0"%"'` for shares, `'#,##0'`
   for volumes), OR a native table with `add_table`, then
   `set_row_heights(table, header=..., body=...)` so rows fit their text instead
   of splitting the frame height evenly. On path A, a chart PNG goes into the
   template's picture frame with `add_picture`, height by aspect.
4. `add_takeaway(prs, slide, body)` adds the takeaway box: light tint, left
   accent border, a bold label line and the one-sentence takeaway below it,
   both left-aligned.
5. Reorder into the analysis section with `reorder_after_add` (snapshot the
   slide id list before adding; it moves the new ids to the target index).
6. Re-run `renumber_footers(prs)` over ALL slides.
7. Add speaker notes with `set_notes`.

## Table styling

`add_table` does this by default: header row in the light accent tint with dark
bold text; body rows alternate white and `#F7F8FA`; first column dark text,
middle columns muted, the verdict or status column coloured by meaning and bold
(`verdict_colors`, e.g. Yes = green, No = red, Partial = amber). On a template
table (path A), set explicit cell fills and per-run colours yourself: colours
inherited from a template are unreliable (`gotchas.md` #7).
