# Phase A: analyse the brand's design patterns

Contents: A1. Find the brand's own published diagrams (2-4 of them) · A2. View them (and get past pages that hang automation) · A3. Extract the design vocabulary (the catalogue) · A4. Sample colours, never invent them · A5. Patterns to expect (but always verify) · A6. Third-party and partner marks · A7. Output: write the style-spec · A8. Extracting a whole website's design system (pages, not just diagrams)

The whole skill lives or dies here. A diagram built from a good spec practically draws itself; a
diagram built from your imagination gets rejected. Spend the time here.

## A1. Find the brand's own published diagrams (2-4 of them)

You want real, first-party diagrams the brand's design team actually shipped: not stock, not photos,
not a competitor's. In priority order:

1. **CMS media library.** WordPress: `GET /wp-json/wp/v2/media?per_page=100&media_type=image&search=diagram`
   (also try `search=architecture`, `how-it-works`, `overview`, `process`, `flow`). Look for landscape
   line-art or flat illustrations, not hero photography.
2. **Other posts in the same category or product line.** Diagrams inside existing articles are the
   truest signal of house style for *this* content type. Pull a few post bodies and collect their
   `<figure>` / `<img>` URLs.
3. **Product, solution or "how it works" pages** on the main site: these often carry the canonical
   overview diagram.
4. **Brand or press kit, or a DAM**, if the brand has one (logos, colour tokens, icon sets, a brand
   guideline PDF). A brand guide gives you exact hex tokens and logo geometry, which beats sampling.

One reference is enough to start; two or three let you separate "house style" from "one designer's
one-off". If references disagree, follow the most recent ones in the same content type and note the
disagreement for the user.

## A2. View them (and get past pages that hang automation)

You must actually see the pixels; you cannot infer a palette from a filename.

- **The reliable trick:** point a browser tab at the **raw image URL** (the uploaded `.png`/`.svg`/`.webp`
  file itself, not the post that embeds it) and take a screenshot, zooming into regions. Raw images
  and REST/JSON endpoints render even when a themed page doesn't.
- **Why pages hang:** heavy themes, page-injected scripts or browser extensions can stall the browser
  automation channel on rendered pages, so in-page scripts or screenshots hang or error there.
  Unthemed endpoints (raw images, `/wp-json/…`) are usually unaffected. If a themed page hangs, don't
  fight it: go to the raw asset.
- Zoom into regions to read edge treatments, corner radii and stroke weights, and to eyedrop colours.

## A3. Extract the design vocabulary (the catalogue)

Walk this checklist against the reference images and write each answer into the style-spec. These are
the dimensions that make a diagram read as "theirs":

| Dimension | Questions to answer |
|---|---|
| **Canvas** | Background colour (sample it). Full-bleed or inset? Is there an outer frame or border? Its colour, weight, corner radius? |
| **Box geometry** | Sharp or rounded corners (what radius)? **Filled or outline-only?** Stroke colour and weight. Any shadow (many brands use none)? |
| **Palette** | **Sample the exact hexes.** Monochrome plus one or two accents, or genuinely colourful? Which colour is load-bearing vs decorative? What are the accent rules (only on the hero element? only on their own logo? only on a highlighted step)? |
| **Typography** | Font family (serif or sans; which one?), heading weight vs label weight, sizes, case (title case, sentence case, all caps), alignment (centred vs left) |
| **Iconography** | How do they draw **their own logo** in diagrams? How do they show **third-party products** (a cloud provider, a CRM, a payment processor)? Simple line glyphs, filled icons, or brand-coloured tiles? |
| **Connectors** | Arrow style (thin or thick, arrowhead shape), straight vs elbowed vs curved, solid vs dashed, and what dashed *means* in their legend (often optional/asynchronous vs the primary flow) |
| **Labelling** | Numbered steps? Circles vs pills vs plain numerals? Captions inside or outside boxes? Divider lines under headings? A legend? |
| **Density** | Airy or packed? Roughly how many nodes per canvas? Generous whitespace or edge-to-edge? |

## A4. Sample colours, never invent them

- Zoom the raster and eyedrop; or, if you found an **SVG source** (an inline SVG in the page source, or
  an `.svg` in the media library), read the exact `fill` / `stroke` / `stop-color` values straight out
  of it. That is the ground truth.
- JPEG and resized WebP images shift colours slightly around edges; sample flat interior areas, not
  anti-aliased edges, and prefer PNG/SVG references when you have a choice.
- Put every sampled hex into `approved_palette`. If you're unsure whether a near-duplicate is real,
  include both; the gate's tolerance will collapse them.
- **Don't add a colour because it "would look nice."** The gate will flag it, and so will the brand.

## A5. Patterns to expect (but always verify)

Brand diagram systems tend to fall into a few families. None of them is the default; identify which
one the references belong to, then read the details off the images:

| Family | Typical traits |
|---|---|
| **Outline line-art** | Light canvas, outline boxes, thin connectors, one type family, few accents |
| **Flat colourful illustration** | Filled shapes in several brand colours, rounded geometry, icons or characters, thicker strokes |
| **Dark-canvas technical** | Dark background, light or glowing strokes, monospace or condensed labels, bright accent for active paths |
| **Hand-drawn / sketch** | Uneven strokes, handwritten-style labels, paper-like canvas, loose arrows |

Whatever the family, your own defaults (whatever style you would pick without references) are the thing
to suppress. The point is never "make it minimal" or "make it lively"; it is "match what they actually
do." Let the sampled palette and the reference images decide.

## A6. Third-party and partner marks

When the diagram includes another vendor's product (a cloud provider, a SaaS the brand integrates
with), draw that mark **true to the partner's brand** (recognisable wordmark, official accent colour)
but **subordinate** to the brand's own visual system: a small brand-coloured tile or wordmark inside an
otherwise house-style box. Add the partner's accent colour to `allow_extra_accent_colors` in the spec
if it isn't in the brand's own palette, so the gate permits it without opening the palette to
arbitrary colours. Check the partner's published brand guidelines for how their mark may be used.

## A7. Output: write the style-spec

Copy `data/style_spec.example.json` to `style_spec.json` (keep it next to your working SVG or in a
per-brand folder) and fill in:

- `client`: the brand and its host, for the report header
- `approved_palette`: the sampled hexes
- `palette_tolerance`: RGB distance treated as "the same colour" (6 is a good default; raise it a
  little only for colours sampled from lossy JPEGs)
- `target_ratio`: from their image dimensions (`"16:9"`, a number, or `[w, h]`)
- `required_ids`: ids that must appear in the SVG, e.g. the reusable logo `<g id="brand-logo">`
- `allow_extra_accent_colors`: partner colours exempt from the palette check
- `palette_roles`: which hex does what (your build cheat sheet)
- `derivation_evidence`: the reference image URLs you sampled

That file now drives both the build and the gate. Delete the `_README` key or leave it; the gate
ignores it.

## A8. Extracting a whole website's design system (pages, not just diagrams)

When the job is to make pages look like a reference site, or to make a site consistent with itself, the
same rule holds: measure, don't eyeball.

1. **Measure computed styles across several pages.** Load each page in a hidden same-origin iframe at
   your target desktop width (e.g. 1280px) and read `getComputedStyle` for h1-h4, p, li, buttons, section
   padding, container max-width and left offset, and section backgrounds. Batch several pages per
   script call. A screenshot tells you something looks off; the numbers tell you which token is wrong
   and on which page.
2. **Write the tokens down before building:** colours by role (primary, accent/CTA and its hover,
   highlight, neutral band, body and muted text), font pairing with weights, a type scale (H2 on
   desktop and phone, body size and line-height, eyebrow), section padding (desktop and phone), content
   max-width and side padding, and any accent device (e.g. a short bar under headings). Build every
   later section from this table.
3. **Common dimensions to check** (no fixed order): (a) spacing between sections: one band padding
   everywhere, no stray spacers or divider lines doubling up; (b) edges: every section's content starts
   at the same x, and nothing runs to the screen edge unless it is meant to be
   full-bleed; (c) heading scale: all section headings one size, one colour, one alignment; (d) band
   backgrounds: a small, repeated set, used the same way on every page; (e) button styles: one
   primary and one secondary style site-wide; (f) image aspect ratios: one ratio per image role.
4. **Decoration must not compete with content.** Use brand patterns and textures where they don't sit
   behind dense imagery or small text; keep image-heavy sections on a plain background.
5. **Logos and images must be legible.** Keep logo sizes
   consistent within a group, label unfamiliar ones, and write alt text that says what the image means
   for the reader ("Logo of CompanyA, one of our customers"), not just the brand name.
6. **One CTA per job.** Remove duplicate buttons that do the same thing in the same viewport.
7. **Verify uniformity after building:** rerun the computed-style audit and compare it with the token
   table at your target desktop, tablet and phone widths (e.g. 1280 / 768 / 375). When the user is
   unsure between design options, show them side by side rather than guessing.
8. **Keep content in the HTML.** Ship content as server-rendered or static markup rather than building
   it from JavaScript strings at run time, so search engines and AI crawlers can read it; add
   Organization structured data (JSON-LD).
9. **Store the result for reuse:** keep the token table and the final live code with the brand's other
   working notes, so the next request starts from what is live instead of a rebuild from memory.
