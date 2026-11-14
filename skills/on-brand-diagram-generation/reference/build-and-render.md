# Phase B: build to the spec, then render

You have `style_spec.json` from Phase A. Now author the SVG to it. SVG (not a raster paint tool)
because it is precise, diff-able, palette-checkable by the gate, and renders crisp at any size.

## B1. Set the frame

- **Match the brand's aspect ratio exactly** (from `target_ratio`). If their diagrams are 1600x900,
  author `width="1600" height="900" viewBox="0 0 1600 900"`. A mismatched ratio letterboxes inside
  their layout and instantly reads as foreign; the gate fails it.
- If the spec has an outer frame, replicate its colour, weight and corner radius (a `<rect>` with the
  frame's `rx`, stroked in the frame colour, inset by half the stroke width so it isn't clipped).
- Keep a consistent grid: align node centres to a few columns and rows; equal gaps between nodes do
  more for "designed" than any decoration.

## B2. Reusable `<defs>`: define the brand's parts once

Define once, reuse everywhere:

- **Arrow markers** (`<marker>`) in the connector colour, plus a second marker if dashed connectors
  use a different colour.
- **Gradients** only if the brand uses them (many don't; check the spec).
- **Logo groups** (`<g id="...">`). If you'll place the brand's logo more than once, or a partner mark,
  make it a reusable `<g>` and `<use href="#...">` it. Put the id in `required_ids` so the gate checks
  the logo is present. Example: the brand's mark as `<g id="brand-logo">`, ideally pasted from their
  official SVG rather than retraced by eye.

## B3. Draw to the palette, and only the palette

- Every `fill` / `stroke` / `stop-color` must be a colour from `approved_palette` (or an
  `allow_extra_accent_colors` partner colour). If you reach for a colour that isn't there, either you
  mis-sampled in Phase A (fix the spec, with evidence) or you're drifting off-brand (don't).
- Use the `palette_roles` map as your cheat sheet: box strokes get the box-stroke hex, labels the
  label hex, dividers the divider hex, and so on. Consistency across nodes is most of what makes a
  diagram look designed.
- Write colours as hex in `fill`/`stroke` attributes or inline `style`, or in one `<style>` block; the
  gate reads all three. Avoid `opacity` tricks to fake new tints: a 50%-opacity accent over white is a
  new visible colour the gate can't see. If the brand uses tints, sample them into the palette.
- Match **stroke weights and corner style** from the spec, not just colours: a sharp-cornered brand
  drawn with rounded rects still looks wrong in the right palette.
- Text: use the brand's font family with sensible fallbacks (`font-family="BrandFont, Arial,
  sans-serif"`). The renderer only uses fonts installed on the machine; if the brand font isn't
  available, install it (when its licence allows) or convert text to paths in a final copy, and say
  which you did.

## B4. Accessibility and search text (don't skip: the gate checks it)

- Add a `<title>` (short, the diagram's name) and a `<desc>` (a sentence or two naming each component
  and the relationships or flow between them) as the first children of `<svg>`.
- The `<desc>` is the natural source for the **`<img alt>`** you'll set when you place the image. Write
  it to name the components and their relationship and to work the page's target term in naturally;
  this is real search and answer-engine surface, not boilerplate. Avoid "image of…"; describe the flow.
- Keep label text at a size that stays readable when the image is shown at the post's content width
  (check it scaled down, not only at full size).

## B5. Render SVG → PNG at 2x

```bash
pip install cairosvg   # if not present
python3 -c "import cairosvg; cairosvg.svg2png(url='diagram.svg', \
  write_to='outputs/<brand>-<concept>-diagram.png', \
  output_width=3200, output_height=1800)"       # 2x the authored 1600x900
```

- **2x** so it stays crisp on high-DPI screens. Author at the brand's logical size, export at double.
- Write the PNG to an outputs folder you can both share with the user and upload from.
- Keep it **pure vector**: no `<image>` or `data:image` embeds. Raster embeds blur at 2x and the gate
  flags them.
- Name the PNG the way the CMS or post expects (if you're replacing an existing figure, follow its
  filename convention).
- Open the rendered PNG and look at it: renderers differ on fonts, markers and `<use>` handling, so
  confirm the PNG matches the SVG you designed.

## B6. Then gate it (Phase C)

Run `python3 data/diagram_style_probe.py --svg diagram.svg --spec style_spec.json`. Green on all
checks, then do the human-eye family check (side by side with a real reference). Only after both do you
go to Phase D.
