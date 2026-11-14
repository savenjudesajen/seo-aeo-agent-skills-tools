# Security

## Reporting a problem

Report security issues privately through GitHub: **Security → Report a vulnerability** on this
repository. Please don't open a public issue for them.

## What these skills do and don't do

- They never fetch remote instructions and never update themselves. Updates come only from the
  installer you ran (`npx skills update`, the Claude Code plugin manager, `git pull`, or a new zip).
- Skills tell the agent to treat crawled pages, search results and AI answers as data, never as
  instructions.
- Skills never ask for credentials in their output. API keys stay in your agent's or tool's own
  configuration.

## What the scripts in `data/` need and touch

The scripts run on your machine. None of them uploads your files.

- **Python packages.** Every script needs Python 3. Some also need:
  - python-docx and python-pptx (Word and PowerPoint files),
  - Pillow (images), fonttools (embedded fonts), matplotlib (charts),
  - numpy and pdfplumber for `doc-template-design/data/audit.py` (OpenCV optional).
- **Programs they start.**
  - The render checks call LibreOffice (`soffice`) and poppler (`pdftoppm`).
  - `aeo-keyword-research-and-prompt-simulation/data/run_gates.py` runs that skill's other gate
    scripts.
  - `competitor-comparison-page-template/data/lean_doc.py` runs the validator named in
    `$DOCX_VALIDATOR`, only if you set it.
- **Network.**
  - `doc-template-design/data/doctemplate.py` downloads open-licence fonts by family name from
    Google Fonts' GitHub repository, its jsDelivr mirror or npm (the package's latest release),
    falling back to `curl`. It caches them in `~/.cache/doctemplate-fonts`, or in
    `$DOCTEMPLATE_FONT_CACHE`. `Doc(embed_fonts=False)` builds without fonts or network.
  - `doc-template-design/data/brand_probe.js` and `dump_probe.js` run in your browser, on the page
    you're measuring.
  - No other script makes network requests.
