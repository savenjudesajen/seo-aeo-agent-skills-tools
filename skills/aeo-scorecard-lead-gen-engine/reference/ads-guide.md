# LinkedIn ABM ad creatives

Paired with the landing page: the click-through has to feel like one thing (same design system,
same hook).

## Formats to produce
- **Single image:** landscape **1200×627** (1.91:1, desktop feed) and square **1200×1200** (1:1,
  where mobile feed weight sits). JPG or PNG under 5 MB.
- **Carousel:** **1080×1080** per card, 2 to 10 cards. Tell the story card by card: hook → receipt →
  who's winning (leaderboard) → why (it's not a content problem) → call to action.

## Build
- Author each creative as an **SVG** (parametric, design tokens at the top) and render it to PNG with
  **`cairosvg`** at exact dimensions. The brand's webfont usually falls back to a system face in the
  PNG; note that on handoff.
- Also produce a **review board** (one HTML page) that inlines the SVGs, so they render with the real
  webfont in a browser, plus all copy and specs, and an `ad-copy.txt` for pasting into Campaign
  Manager.

## Copy
- **Intro text** shows about 150 characters before "…see more" (600 max). **Headline** 70 characters
  or fewer (200 max). Carousel intro about 255 characters.
- **Rotate hooks** two at a time (A/B):
  - curiosity: "Where does [Company] come up when buyers ask AI?";
  - competitive: name the competitor AI recommends in the account's place, e.g. "Ask AI about
    [category]. It recommends [Competitor].";
  - the receipt: one real result as a template, e.g. "[Company] appeared in [N] of [M] AI answers,
    and only when the question named [a place or the brand]";
  - the contrast: "N keywords in Google. Almost no answers in AI."

  Curiosity tends to win cold click-through; the competitive hook lands hardest.
- **Destination** = the live per-account landing URL (propagate it once the page is deployed).

## Competitor logos are a legal question, not a design one
"X is beating you" with X's logo is comparative advertising. Ship **names only** until the client
signs off. If the design has logo placeholders that never got assets (empty circles), removing them
is cleaner and sidesteps the legal question.

## LinkedIn audience minimums: what breaks a small target list
**LinkedIn won't serve an ad to an audience under about 300 members.** Matched audiences (uploaded
company or contact lists) also need about 300 matched members to activate.
- **A short list of named companies is often too small for paid LinkedIn ads**, especially small
  firms: a few decision-makers at each of a handful of companies rarely clears 300. The campaign
  simply won't run.
- **Options:**
  1. broaden the persona, seniority or title filters at those companies to reach 300+;
  2. expand the account list substantially;
  3. skip paid LinkedIn ads for a handful of named accounts and run the **1:1 outbound sequences**
     (cold email plus a manual LinkedIn connection and message), which have no minimum.

  For a truly small named-account list, outbound is the right channel; paid ads suit a larger list,
  retargeting or awareness.
- Always confirm the live audience size in Campaign Manager before promising a paid launch.

## Upload is manual (platform limit)
No common connector creates or uploads LinkedIn campaigns. Third-party LinkedIn connectors are
typically read-only analytics: they pull performance, they don't push campaigns. LinkedIn's
ad-creation API needs Marketing Developer Platform approval. So deliver upload-ready PNGs, copy and a
targeting/campaign spec; a person (or a browser-automation tool, as a draft, see
`linkedin-abm-campaign-build.md`) builds it in Campaign Manager.
