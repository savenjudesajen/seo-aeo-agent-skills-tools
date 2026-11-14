# Generators to write

Six small Python generators produce the assets. This skill describes them; write them for your run
from these specs and the other reference files. Each is a **template, not a framework**: one account
data block sits at the top of the file. Swap that block per account and re-run. Keeping the account
data in one dict at the top makes the swap obvious and diffable.

| Script | Produces | Swap per account |
|---|---|---|
| `build_master_sheet.py` | The master tracking `.xlsx`: rows plus a Legend/schema tab, the auto composite and the auto ad headline (`master-sheet-schema.md`) | the account list and the column list |
| `build_scorecard.py` | The full scorecard: the external 9 sections (gated brief, proof block) and the internal call-prep view (`report-structure.md`) | pillars, probes, leaderboard, brief, plays, recommendations, funnel and folder data |
| `build_landing_plain.py` | A plain-English prospect landing page as static HTML: the design and copy spec that maps onto the production Next.js repo | pillars, stat cards, leaderboard, probes, brief, plays |
| `build_ads.py` | LinkedIn creatives: single image (1200×627, 1200×1200) and a 5-card carousel (1080×1080), as SVG and PNG via `cairosvg` (`ads-guide.md`) | company, competitor, score, and the copy in each builder |
| `build_board.py` | The ad review board: creatives, copy and specs on one HTML page | the copy and the landing destination URL |
| `build_sequences.py` | Cold and nurture sequences: a review board, a cold-email campaign JSON, a leads CSV and a plain-text spec (`sequences-guide.md`) | the cold and nurture copy, the live landing URL, the booking link |

## Dependencies
`pip install openpyxl cairosvg weasyprint` (add `--break-system-packages` only where the sandbox's
Python requires it).
- `cairosvg`: SVG to PNG at exact ad dimensions, reliable and needs no browser.
- `weasyprint`: HTML to PDF for QA only. It renders pessimistically (flexbox stacks, blur degrades);
  judge layout in a real browser.
- `openpyxl`: the sheet. Formulas need a recalc before preview tools show values; see the build
  gotcha in `master-sheet-schema.md`.

## Conventions worth keeping
- **Build HTML from a plain-string template with `.replace()`**, not f-strings: the f-string parser
  breaks on brace-heavy CSS.
- Render and look at every asset before it ships (the quality gate in SKILL.md). A quick visual:
  `weasyprint` to PDF, then read the PDF. For exact pixels, use the `cairosvg` PNGs.
- After deploy, put the live landing URL into `build_board.py` (the ad destination) and
  `build_sequences.py`, then re-run and re-package.
- The landing generator is the static spec. The production landing page is the client's Next.js repo
  (`deployment-and-launch.md`): port the copy and structure into its components rather than shipping
  the static HTML as the live page.
