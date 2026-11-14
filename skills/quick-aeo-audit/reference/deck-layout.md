# Neutral default deck layout (path B: no client template)

Use the client's own template if they have one (Phase 6, path A). Otherwise
build this layout. It is deliberately plain: white slides, one accent colour, a
system font, no branding beyond the client's optional logo. Swap the palette
and font constants in `data/deck_helpers.py` and `data/sov_chart.py` if the
client gives you brand colours.

## Format

- 16:9, 13.333 x 7.5 in, white background, 0.6 in side margins.
- Font: Arial (or the client's brand font). Titles 24pt bold, body 12-14pt,
  table text 10-11pt, footer 8pt.
- Palette: near-black `#1F2933` (titles, labels), muted `#5F6B7A` (body),
  accent `#2563EB` (client highlight, title rule, takeaway border), light tint
  `#EAF1FD` (takeaway box, table header), greys `#B8BEC6` / `#DDE1E6`
  (competitors), rule grey `#D5DAE1`, semantic green `#166534`, red `#9B1C1C`,
  amber `#854D0E`.
- Chrome on every content slide (`add_chrome`): optional small uppercase
  section kicker in the accent colour, dark title at the left margin, a short
  accent rule under the title, optional client logo top-right, a thin grey rule
  above the footer, footer text left ("Confidential", optionally "Prepared for
  <Client>"), page number right.
- One message per slide. The title states the finding, not the topic
  ("AI names <Client> on 1 in N category questions", not "Share of voice").
- Content slides that carry a finding end with a takeaway box (`add_takeaway`):
  light tinted box, left accent border, a small bold label line and the
  one-sentence takeaway below it.

## Slide outline (about a dozen slides)

Core slides first; the optional ones go in only when the data supports them.

| # | Slide | Content | Source |
|---|---|---|---|
| 1 | Title | "<Client>: AI visibility audit", date, "Prepared for <Client>" | - |
| 2 | Executive summary | The thesis in one sentence (wins branded, invisible on category), three numbers (category share of voice, open goals, addressable gap), the three plays | Phases 4-5 |
| 3 | Method | Engines checked, prompt count by stage, brand set, "directional, single-run" label, date of the run | Phases 3-4 |
| 4 | AI visibility today | The client's branded-inclusive number next to the non-branded baseline, with the reason they differ | Phase 1 + 4 |
| 5 | Visibility by platform | Platform x Brand table (visibility % per engine per brand) | Phase 4 |
| 6 | Category share of voice | Signature horizontal bar chart | Phase 4, `sov_bar` |
| 7 | Prompt performance | Prompt / Stage / Who AI names today / Client? table, representative rows, gaps first | Phase 4 |
| 8 | Keyword gap by theme | Theme bar chart of untapped search volume, brand terms excluded | Phase 5, `theme_bar` |
| 9 | Open goals and plays | Prompts where AI names no vendor, grouped by play (Defend / Strengthen / Capture) | Phases 3-4 |
| 10 | Recommended next steps | 3-5 actions in priority order, each tied to a play and a slide above | All |
| opt | Head to head | Versus verdicts: for each "client vs competitor" prompt, who AI favours and why | Phase 4 |
| opt | Narrative alignment | What the client says about itself (owned) vs what AI repeats about it (earned), aligned / misaligned per claim | Phase 1 + 4 |
| opt | Competitor top pages | Top-5-pages Pareto with page-type labels | Phase 5, `pareto_bar` |
| opt | Appendix | Full prompt list with tags, method notes, data sources (described generically, no vendor names in body copy) | Phases 2-5 |

Place optional slides next to the core slide they extend (head to head and
narrative alignment after slide 7, competitor top pages after slide 8, the
appendix last). Never pad. Merge rather than append when two slides would make
the same point (the gate flags near-duplicates).

## Speaker notes format

```
What to say: <two to four sentences for the presenter>
Insight for the call: <one non-obvious, data-grounded line>
```
