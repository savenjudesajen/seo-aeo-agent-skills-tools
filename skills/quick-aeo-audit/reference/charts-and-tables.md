# Charts, tables and extra insight slides

Build charts as PNGs with matplotlib (`data/sov_chart.py`) and place them on
native slides with matching chrome (`data/deck_helpers.py`). Both files share
one neutral palette. If the client's template has its own brand colours and
font, change the constants at the top of both files to match; otherwise keep
the defaults.

## Default chart style (neutral)

- accent (client / opportunity highlight): `#2563EB`
- grey (competitors / neutral): `#B8BEC6`; faint grey (zero values): `#DDE1E6`
- dark text: `#1F2933`; muted text: `#5F6B7A`; positive value label: `#166534`
- grid: `#EEF0F3`; white background; title left-aligned, bold, ~16pt
- wide charts ~13.0 x 3.7-4.6 in at 150 dpi; client bar in the accent colour,
  competitors grey; value labels bold at the bar end

## The four slides worth adding

1. Category share of voice (the signature chart): horizontal bar, one bar per
   brand, client in the accent colour. The axis label states the denominator
   ("across N non-branded category prompts, single-run baseline"). `sov_bar`.
2. Keyword gap by theme: horizontal bar of untapped monthly search volume per
   non-brand theme (the category's sub-topics). All bars in the accent colour:
   they are all opportunities. The caption notes that brand terms are excluded.
   `theme_bar`.
3. Competitor Pareto: vertical bar of the incumbent's top-5 pages' share of
   organic traffic, all grey to signal "navigational, not category content".
   The title states the punchline with the real figure ("Top 5 pages = N% of
   traffic, all navigational"). `pareto_bar`.
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
3. Add the chart with `add_picture` below `CONTENT_TOP`, at the content width
   (slide width minus both margins, height by aspect), OR a native table with
   `add_table`.
4. `add_takeaway(prs, slide, body)` adds the takeaway box: light tint, left
   accent border, a bold label line and the one-sentence takeaway below it.
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
