# Deck build mechanics: template editing that survives contact

Scripts: `data/dump_pptx.py`, `data/tpl_edit.py`, `data/slide_ops.py` (need `python-pptx`). Use the
client's own template if they have one; otherwise start from a neutral template (cover, contents,
executive summary, scorecard, section openers, content slides, glossary, next steps).

## The rule
**Edit the client's template file. Don't rebuild it.**
A rebuild reproduces the design *approximately*, inherits none of the theme, masters, layouts or
embedded fonts, and reproduces the template's own bugs while losing its good decisions. A rebuild from
screenshots or memory can also introduce changes the real template never needed. Work from the real
file: copy the template, open it, **replace text only**, and map each template slide to its new
purpose 1:1. Text replacement must preserve run formatting: replace run text in place when the
paragraph count matches, and clone the first paragraph's XML when it doesn't (`set_text()` in
`tpl_edit.py` does both).

## Run order that works
1. `python3 data/dump_pptx.py Template.pptx` → slide size, layouts, shape indices, table row counts,
   notes.
2. Copy the template to your output filename. Open it. Replace **text only**.
3. Map each template slide to a new purpose **1:1**. An existing audit template usually maps cleanly
   onto a migration deck (cover, contents, executive summary, scorecard, parts, chapter openers,
   glossary, close).
4. Build in **ordered scripts** (`edit_a.py`, `edit_b.py`, … `add_final_slides.py`), each re-opening
   the output and saving it. The deck is then **regenerable from source in one loop**.
5. Render to PDF, then PNG, and **look at it**. This is the only real layout proof.

```bash
libreoffice --headless --convert-to pdf "Deck.pptx"
pdftoppm -png -r 60 -f 8 -l 12 "Deck.pdf" out/s
# then tile the PNGs into a contact sheet (e.g. with Pillow) and actually view it
```

## Build through an ordered, re-runnable script chain
Because you are editing an intact template, each script can re-open the saved output and save it
again. (A deck built on a *stripped* template must instead be built in one run with one save, because
re-saving a stripped file duplicates parts.) One script per pass, named for what it does, always run in
a fixed order from the pristine template:
`edit_a → edit_b → fix_tables → fix_headers → add_*_slides → apply_review_fixes`. Never hand-edit the
output. This makes the deck idempotent and cheap to revise: a reviewer's change list becomes a fix in
the last script and a re-run. **Deletions go in the final script, as the last operation before save.**

## The traps

| Trap | Fix |
|---|---|
| Template tables have **fixed row counts**; extra rows are **silently dropped** | read `len(table.rows)` before writing; assert your data fits (`set_table()` in `tpl_edit.py` warns) |
| python-pptx reports **meaningless table heights** (every table returns the same value) | keep cells under ~50 characters; set explicit `row.height`; prove by render |
| **Empty template cells carry no run formatting**, so text falls back to the default size and colour and can be invisible on a dark header row | `fix_invisible_cells()` in `slide_ops.py` |
| Inherited styling can **contradict your meaning** (a neutral figure placed in the template's "bad" coloured card) | read the template's colour semantics, then match content to it |
| A cloned slide's **header bar can have an empty text frame**; a naive "strip shapes without text" removes it and leaves light title text on a light background | `is_header_bar()`: identify by fill + geometry |
| Removing slides from the slide list leaves **orphan parts** → duplicate-relationship corruption, ghost slides | never drop-and-re-add; rebuild from the template |
| python-pptx **cannot measure text**; overflow is invisible until rendered | render and view |
| Inserting a slide **shifts later indices** | duplicate ALL first, then move |
| Index anchors rot between runs | anchor by **title text** (`find_slide()`) |

## Keeping the build reproducible
- **Check build scripts on disk after large edits.** Parse each one (`python3 -m py_compile file.py`)
  before trusting a run: a build that runs is not proof the source is the version you meant.
- **Design builds to overwrite their output** rather than delete and recreate it.
- **Keep every build script, the source template and assets in a persistent project folder**, not a
  temp directory a restart can wipe. Treat the deck as **regenerable from source, not a precious
  binary**.
- Re-verify any number in the deck that is **derived from another artifact** after that artifact changes.

## Charts: use a native pptx chart, not drawn shapes
When a slide needs a chart, `shapes.add_chart(XL_CHART_TYPE.PIE, ...)` with `CategoryChartData` beats
drawing arcs or pasting an image. It stays **editable in PowerPoint**, takes the template's colours per
data point, and the client can adjust it without coming back to you. Turn the chart title off (the slide
already has one), put the legend at the bottom, and set the legend font to the template's body font
explicitly, because charts don't inherit theme fonts reliably.

Build the chart slide by **cloning a content slide** so it keeps the header bar, footer, logo and type,
then stripping the body shapes, watching for the empty-text-frame header bar. Say in the presenter note
that the chart is native and editable; otherwise someone will ask for a new version to change a colour.

## Presenter notes carry everything non-client-facing
Every mechanic, caveat, placeholder rationale, thing to chase and "say this out loud" goes in
`note(slide, ...)`. Expect most content slides to carry a note.
