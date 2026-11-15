# Gotchas: read before the deck build

Ordered roughly by how much damage each one does if missed. Items marked
"path A" apply when you edit a client's existing template; check which of them
your template actually has.

## 1. Tool connections drop mid-run

Remote tool connections (MCP servers, device bridges, browser extensions) can
disconnect without warning and reconnect on their own. Therefore:
- Run the AI-visibility checks in WAVES of ~20-24 parallel calls, never one
  giant batch.
- Treat a dropped call as a retry, not a data point. Definitional or awareness
  prompts that do return are almost always zero for every brand, so a dropped
  awareness call can be provisionally treated as zero and re-run later.
- When the connection is up, do any account-modifying steps (creating a
  tracking project, adding tracked prompts) promptly.
- If it stays down, keep going: the deck build runs locally and needs no remote
  tools. Finish the missing data later.
- After a reconnect, reload the tool list before calling the tools again.

## 2. SEO-suite APIs with no units: use the UI

Agency sub-accounts frequently have zero API units even though the UI works.
Every report call then returns a "not enough API units" notice. Do not keep
retrying the API. Tell the user their account owner must allocate units, then
get the data from the UI export (`keyword-gap-and-top-pages.md`).

## 3. Unstable shape names (path A)

Some templates, for example ones exported from Google Slides, name shapes with
a numeric id plus a suffix that changes per file and per slide
(`Google Shape;<n>;<suffix>`). Never hardcode full shape names. Match on the
stable part: `find(slide, n)` in `data/deck_helpers.py` matches the
`Google Shape;<n>;` prefix; adapt it to your template's pattern. Run
`dump_structure(prs)` on each new deck to get the ids.

## 4. Invisible text (path A)

Some templates contain a text box whose colour matches the background behind
it, so it does not show in the render. If it holds content you need, recolour
it to the body colour, check its size, and move it clear of tables and charts.
Always render and LOOK to confirm every text block shows.

## 5. Page numbers that are plain text

Some templates type page numbers as plain text instead of a slide-number field,
so they go wrong as soon as slides move. Renumber every pure-digit (2
characters or fewer) text shape to its real 1-based slide position
(`renumber_footers`), and re-run it AFTER inserting any new slides. The gate
(`data/deck_qc.py`) fails on mismatches.

## 6. Stale screenshots

A screenshot supplied for the audit can show another account's data (for
example a share-of-voice chart listing brands that are not this client's
competitors). You cannot edit a raster screenshot. Flag it to the reviewer in
chat and rebuild that slide as a NATIVE chart from your baseline. Always check
that the brands in every screenshot match the client's real competitor set.

## 7. Semantic cell colours inherited from the template (path A)

Table cells can carry inherited run colours (a "No" can render green). Always
set `run.font.color.rgb` explicitly on every semantic cell:
- Yes / Aligned / Owns it = green `166534`
- No / Misaligned / Competitor = red `9B1C1C`
- Rarely / Partial / Open goal / Medium = amber `854D0E`
- body text = muted `5F6B7A`
- header text = whatever contrasts with the header fill, set explicitly
- stage or platform label = near-black `1F2933`

## 8. Callouts with a styled label run (path A)

Some templates build a callout as one paragraph whose first run is a styled
label and whose second run is the body. Replace only the body run and keep the
label run (`set_callout_body`). Clearing the paragraph loses the styling.

## 9. Dash sweep and stale-name sweep

After all edits, sweep every run (`voice_sweep`): replace spaced em or en dashes
with ": ", bare em or en dashes with "-", and any leftover previous-client name
with the new client's name. Write build scripts in pure ASCII (hyphens only):
some editors and pipelines truncate a file at a multibyte em dash.

## 10. Visibility tools that return no answer text

Some AI-visibility tools return, per engine, whether the brands you pass are
named and their positions, but no answer text and no list of every brand named.
Read how the tool takes brands before you plan the call count:
- If it takes the client plus a list of competitors and reports each one in the
  same answer (the Unilytics MCP `brand_visibility`: `brand` plus up to 20
  `competitors`), share of voice is ONE call per prompt with the whole set. A set
  over 21 brands takes a second call on the same prompt, and the two calls are
  two different answers: count each brand from one call only.
- If it takes one brand per call, share of voice needs one call per (prompt,
  brand), and each call is a separate answer. That costs N brands times more,
  and brands are never compared within one answer; say so in the method slide.
Position (where the brand comes among the brands named; earlier is better)
supports the "good position, low frequency" insight: the client is named early
when named at all, but named rarely.

## 11. Keyword-gap top rows are a data trap

The highest-volume "untapped" gap keywords are usually competitor brand names
and navigational terms (a brand plus "sign in", "app", "account"). Never present
these as opportunities. Bucket the untapped set by non-brand THEME and present
theme totals as the addressable content gap.

## 12. Cloning slides breaks image relationships

Do not deep-copy a slide to duplicate it: image relationship ids (logo,
screenshots) break. Add a slide on the blankest layout (`add_blank_slide`) and
draw the chrome fresh. On path B use `add_chrome`; on path A redraw the
template's own chrome elements. Then reorder via the slide id list
(`reorder_after_add`) and renumber footers.

## 13. The render is the only truth

Render with LibreOffice and read every slide image. python-pptx will not catch
text overflow, invisible text, collisions or a stretched replacement image.
Generate replacement chart PNGs at the target frame's aspect ratio so they do not
stretch. A title too long for one line wraps upward into the kicker: shorten it.

## 14. Count cited domains after normalising them

Answer engines that cite sources (Perplexity) cite the same site under several
hosts (`example.com`, `www.example.com`, `blog.example.com`). Lower-case each
host and strip `www.` and content subdomains such as `blog.` before counting
"questions where the engine cited this domain", and count a domain once per
question. Counted raw, one site shows up as two rows and its count can double.
