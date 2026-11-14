# Brand themes: the layout in a client's colours and fonts

A theme is a skin over the layout. It changes the colour roles (`ink`, `title`, `muted`, `panel`, `rule`,
`accent`, `accent_text`, `stripe`, `number`, `alert`), the status chips and the fonts (`title`, `body`, `strong`,
optional `section`). It never changes page geometry, spacing, sizes, the block set or the header and footer
layout. With no theme, the neutral default (`components.md`) is used.

## The theme file: `themes/<slug>.json`
| Field | What it holds |
|---|---|
| `client`, `slug`, `domains`, `aliases` | How a request is matched to the theme (case-insensitive) |
| `relationship` | How you work with the client (in-house, your agency, through another agency): decides the meta line and voice |
| `prepared_by` | Meta line "Prepared by ..." (null leaves it out) |
| `prepared_for` | Meta line "Prepared for ..." for work delivered to an agency about its client; wins over `prepared_by` |
| `never_mention` | Names this client's documents must never carry: other clients, your other employers or partners, internal tool or vendor names. `save()` refuses to write a document that contains one |
| `colors` | The roles above |
| `status` | Fill and text for Keep, Rework, New, Remove, Optional, Later |
| `fonts` | `title`, `body`, `strong`: `{family, weight}`, Google Fonts families only; optional `section` `{family, weight, caps}` |
| `font_versions`, `font_sigs` | npm package versions and font signatures pinned at confirmation |
| `substitutes` | Licensed site fonts and the open family used instead |
| `logo` | The site's logo URL (used only if the user asks for a logo; `Doc(logo=)` takes a PNG) |
| `provenance` | Pages probed and the evidence behind every value |
| `confirmed` | `{on, note}` once the user approved the preview; null means proposal only |

Keep confirmed themes where your agent persists files between sessions (a `themes/` folder in the project or next
to `doctemplate.py`), so the next document for that client needs no probe. Re-probe when the client rebrands or
the user says the colours look off.

## 1. Who is the document for
Signals, strongest first: the client named in the request; a domain or URL in it; the project, folder or file
name; the content skill in play; earlier documents in the conversation. Match them against `client`,
`aliases` and `domains` of every saved theme.

| Situation | Do |
|---|---|
| One theme matches | Use it and say so in one line ("Using the <client> theme: navy header rows, Lora body") |
| A client is named with no theme | Build one (steps 2 to 5), get a yes on the preview, then write the document |
| Nothing matches, or two candidates (an agency and its client) | Ask: the candidates plus "neutral default". Never guess |
| Work delivered under your agency's name | The client's brand with `prepared_by` naming your agency; the neutral default if the user wants the agency look |
| Work delivered to an agency about its client | The end client's brand, with `prepared_for` naming the agency |
| The user supplies the client's own template file | Use that file (`adopt-a-client-template.md`); do not rebuild it with this generator |
| The client has brand guidelines (PDF, hex codes, font names) | Build the theme from them with the overrides in step 3, still preview and confirm |

## 2. Probe the live site
Use a browser tool that runs JavaScript on the page and can read page text. Probe the homepage and one content
page (a blog post or a product page: documents look like content pages, not like heroes).
1. Open the page.
2. Run `data/brand_probe.js` (paste the file's text into the tool). It scrolls the page once so fade-in sections
   render, measures everything, keeps the full JSON on the page (`window.__brandProbe`) and returns a short
   summary, because browser tools cut results off near 1,000 characters.
3. Run `data/dump_probe.js`, then read the page text. Save the text between `BRAND_PROBE_JSON` and
   `END_BRAND_PROBE_JSON` as `probes/<slug>_<page>.json`. Reload the page to restore the tab.
4. When you keep a probe, trim what is not brand evidence: framework variables (`--bs-*`), deleted CMS
   variables, size tokens, a chat or feedback widget's own palette, and customer-logo candidates. A content-page
   probe can leave out the `:root` tokens the homepage probe already holds (they are site-wide). Note what you
   left out in a `note` field.

**If the site cannot be read** (no browser connected, a bot wall, a login): stop and tell the user which step
failed. Never fill colours in from memory, a screenshot or a guess. Offer the ways forward: connect a browser,
or send brand guidelines, hex codes or a sample document.

## 3. Build the proposal
```
python3 theme_from_probe.py probes/<slug>_home.json probes/<slug>_page.json --client "Name" \
    --domain site.example [--alias ...] [--prepared-by "Team"] [--prepared-for "Agency"] \
    [--relationship "..."] [--never-mention "Name" ...] --out themes/<slug>.json
```
It prints every value with its evidence. How the brand maps onto the layout:
- **Accent**: the most used saturated colour, scored by filled buttons (x4), border length (x2), filled area
  (capped), links, the logo's fills and brand tokens (`--primary`, `--brand`, `--accent`). Framework default
  palettes (Bootstrap 4 on `:root`, `--bs-*`) and deleted variables are ignored.
- **Light accent** (luminance 0.4 and up: pale yellows, light corals): it cannot carry white text, so table header rows
  take the darkest text colour with the accent as their text (when it reads at 4.5:1), and the accent becomes
  the stripe. The Rework chip uses the accent itself with dark text.
- **Mid accent** (most reds and blues): header rows in the accent with white or dark text, whichever reads; the
  accent is also the stripe.
- **Dark accent** (navy, aubergine, dark slate): header rows in the accent; their text is the brand's bright
  highlight when one reads at 4.5:1 on it, else white.
- **No saturated colour** (a monochrome brand): header rows and stripe in the darkest text colour, white text.
- **Section numbers** take the brand colour when it reads at 4.5:1 on the panel, else the header-row colour,
  else the ink.
- **Ink**: the colour of most running text on light backgrounds. **Title**: the heading colour on light
  backgrounds, else the darkest text colour.
- **Dark sites** (half or more of the page area dark and no dark text on a light background anywhere): documents
  are white pages, so the site's main page colour becomes the ink; its light greys, which only work on black,
  give way to the darkest neutral grey that reads at 4.5 to 7.5:1 on white. Printed as "dark site".
- **Muted**: the site's secondary grey when it reads at 4.5 to 7.5:1 on white; a lighter grey is darkened along
  its hue to 5:1 (reported).
- **Panel**: a neutral panel colour between 1.12 and 1.45:1 against white (visibly grey, still light), first from
  measured backgrounds covering at least 1% of the page (a sliver of border colour does not count), then from
  `card`, `canvas` or `surface` tokens.
- **Rule**: the site's light neutral border colour (1.3 to 2.2:1 on white), else the panel darkened to 1.6:1.
- **Chips**: Keep on the panel, Rework a tint of the accent (or a second brand colour when the accent is red, so
  Rework never reads as Remove), New in the header-row style, Remove in the alert red, Optional white with muted
  text, Later a light tint of the muted grey.
- **Contrast**: every text and fill pair is checked at 4.5:1; a failing pair takes white or the dark text.
- **Fonts**: body = the family carrying most running text (13 to 20px) at its weight; title = the largest h1 to
  h3 family and weight; strong = the body family bold (600 when the site declares no 700). A family that is not on
  Google Fonts is licensed: documents use the closest open family from `SUBSTITUTES`, and the user is told.
  Never embed a client's web font files: their licence covers the website, not documents.
- **Section label face**: when 60% or more of the styled calls to action (filled or outlined buttons, at least
  three) share a family other than the body's, it goes on section headings only, in capitals when most of those
  buttons are. Tables, chips and body keep the strong font. `--section-font "Family:400:caps"` sets it,
  `--no-section-font` turns it off.

Overrides when the user corrects something (rerun with them rather than editing the JSON, so the contrast rules
still apply): `--accent`, `--highlight`, `--accent-text`, `--panel`, `--muted`, `--ink`, `--body-font
"Family:400"`, `--title-font`, `--strong-font`, `--section-font`, `--no-section-font`. `--offline` skips the
Google Fonts lookups (font availability is then unchecked; say so).

## 4. Preview, gates, confirmation
```
python3 doctemplate.py --fonts themes/<slug>.json               # FONT GATE PASS
python3 showcase.py preview.docx --theme themes/<slug>.json      # every block + a Theme appendix
python3 check_docx.py preview.docx themes/<slug>.json            # DOCX CHECK PASS
python3 audit.py theme preview.docx themes/<slug>.json           # THEME PASS (when LibreOffice is available)
python3 audit.py layout preview.docx --out lay/                  # LAYOUT PASS, then look at lay/contact.png
```
Send the preview and ask for a clear yes ("Use this theme" / "Change something"). Name every substituted font
in the message. Changes go back through step 3 as overrides. On yes:
`python3 theme_from_probe.py --confirm themes/<slug>.json --note "approved on the preview, <date>"`
builds and gates the fonts, pins their versions and signatures and stamps `confirmed`.

## 5. Build documents in the theme
`Doc(short_title, client, theme='<slug>')` (themes are found in `themes/` next to `doctemplate.py`, or pass a
path). Meta line: `d.t.meta_by()`. Gates for every themed document: `DOCX CHECK PASS` with the theme, and with
LibreOffice `THEME PASS` and `LAYOUT PASS` with the contact sheet looked at.

## Gotchas
- **Browser results are cut near 1,000 characters.** The probe returns a summary; the full JSON comes back through
  `dump_probe.js` and the page-text tool (tens of kilobytes come through whole that way).
- **Fade-in sections.** Many sites (Webflow and GSAP builds especially) hold sections at opacity 0 until they
  scroll into view. The probe scrolls first; without that it only sees the hero.
- **Hero text is not body text.** Light text over a dark hero image is often the most common text colour on a
  homepage. The probe tags each text style with the background under it, and the builder takes the ink from text
  on light backgrounds.
- **Dark sites have no ink to take.** Without the dark-site rule, the only dark text on such a site is a small meta
  grey, and the whole document comes out grey.
- **Tokens lie sometimes.** Frameworks publish default palettes on `:root`, templates leave old variables behind,
  and third-party widgets (feedback, chat) publish their own palette, often with a loud `--primary`. Measured use
  outranks tokens; check `accent_runners_up` when a widget colour comes close.
- **A contrast failure after a hand edit.** "reads at 3.9:1" means a colour was overridden in the JSON. Rerun the
  builder with the override instead.
- **Fonts drawn as DejaVuSans or LiberationSans** in `audit.py theme` mean an embed was not picked up, usually a
  name that does not match the file's nameID 1: rerun `doctemplate.py --fonts`.
