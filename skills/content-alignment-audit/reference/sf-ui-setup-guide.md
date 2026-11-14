# Screaming Frog setup for semantic similarity

Source: Screaming Frog's tutorial on identifying semantically similar pages and outliers,
https://www.screamingfrog.co.uk/seo-spider/tutorials/how-to-identify-semantically-similar-pages-outliers/
(menus move between versions; read it before the first run). Checked against SEO Spider version 24.

Starting a crawl does not generate embeddings on its own. Embeddings need an AI provider connected in the
UI and the options below ticked before the crawl. Crawls started from the headless command line or an
automation wrapper use the same saved settings, so do this once in the UI and save the configuration.

## Steps
1. **Connect an AI provider.** Config > API Access > AI. The tutorial lists OpenAI, Gemini and Ollama for
   embeddings. Under Prompt Configuration choose Add from Library > "Extract Semantic Embeddings from
   Page". Under Account Information pick or enter the key and press Connect.
2. **Store HTML.** Config > Spider > Extraction: tick Store HTML and Store Rendered HTML.
3. **Turn embeddings on.** Config > Content > Embeddings: tick Enable Embedding functionality, then
   Semantic Similarity and Low Relevance.
4. **Set the content area.** Config > Content > Area: exclude navigation, footer and boilerplate. Without
   this, shared page chrome inflates every similarity score.
5. **Crawl.** Wait until the crawl bar and the API bar both read 100 percent.
6. **Crawl Analysis > Start** (or Crawl Analysis > Configure > Auto-Analyse at End of Crawl, which you need
   for headless runs). The similarity filters stay empty until this runs.
7. **Read.** Content tab > Semantically Similar (default threshold 0.95) and Low Relevance Content
   (default 0.4). Bulk Export > Content > Semantically Similar gives the pairs.
8. **Save the configuration** (File > Configuration > Save As) if you will crawl from the command line or a
   wrapper.

## Speed and cost
Reduce embedding dimensions (`outputDimensionality` for Gemini, `dimensions` for OpenAI) and tick Limit
Page Content (5,000 characters) for long pages. Free API tiers are heavily rate-limited; large sites need a
paid tier or the crawl waits on the API bar. Check your provider's current limits.

## Verify
After a test crawl, the Semantically Similar bulk export (from the UI, the headless command line or your
automation wrapper) should return records. The export lists only pages whose nearest neighbour passes the
threshold, so count pages that have an embedding vector (Internal export column "Extract semantic
embeddings from page") before reading a blank as "not similar". If the export is empty, check, in order:
provider Connected, embeddings ticked, Crawl Analysis run, Prompt Request Status on the AI tab.

## Cluster diagram
Visualisations > Content Cluster Diagram plots the embeddings in 2D. It exports as an SVG only and has no
per-URL cluster export; group pages from the vectors or the pairs export instead (`../data/run_audit.py`).
