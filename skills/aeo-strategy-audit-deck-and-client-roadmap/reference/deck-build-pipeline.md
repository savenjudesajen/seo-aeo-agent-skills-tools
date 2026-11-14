# Deck build pipeline (python-pptx)

Use the client's own template if they have one, or your team's template. The defaults below are a
neutral fallback; swap every token for the template's own.

## Default design tokens (neutral fallback)

- Background `#FFFFFF`, text `#1F2933`, muted text `#5F6B7A`, accent `#2563EB`, alarm `#C2410C`,
  positive `#15803D`
- Card fills `#F4F6F8` / `#EEF0F3` (alternate rows)
- One sans-serif font for everything (the template's, or a widely available one such as Arial or
  Calibri). Pass it to `data/verify_deck.py --font` so mixed fonts are caught.
- 16:9, 0.5 in margins, title 26-28 pt bold, subtitle 12-13 pt in the accent colour, body 11-14 pt,
  table text 10-11 pt.

## Method

1. Start from the template: keep its master, layouts and theme. If you strip its sample slides, drop each
   slide's relationship as well (`prs.part.drop_rel(...)`; see `gotchas.md` #6), or start from a copy
   that already has no slides.
2. Build content slides natively with a few helpers: `set_bg`, an optional client logo, `title()` (title
   plus subtitle), `card()` (autoshape with `vertical_anchor` TOP), a key-finding bar, and a generic
   `mktable()` (header row in the accent colour with bold text, alternating card-fill rows, the client's
   own row highlighted).
3. Reuse the template's designed **cover** and **closing / Q&A** slides rather than rebuilding them; edit
   only their text. This is what makes the deck look designed.
4. One `prs.save()` per script run.
5. Render and READ: `soffice --headless --convert-to pdf deck.pptx`, then `pdftoppm -png -r 110 deck.pdf
   slide`, then look at every slide image.

## QA (assume there are problems)

- Titles that wrap to two lines and collide with the subtitle.
- Text overflowing a card, or floating mid-card (missing TOP anchor).
- Bottom one-liners clipping past the slide edge (over about 110 characters).
- Table headers wrapping mid-word ("Impressions" breaking across lines): shorten to "Impr.".
- Placeholder or incomplete-status text anywhere, including table cells and notes.
- **Gates:** `python3 data/verify_deck.py deck.pptx --font "<font>"` and
  `python3 data/dedupe_audit.py deck.pptx`.

## The deliverables and phases slide

A deliverables slide listing each file and recurring task with its phase. Treat prompts as the AEO
equivalent of keywords and never state a fixed count (the set grows). Group the technical items into one
row so they don't crowd out the content work. Leave pricing off unless the client provided it.
