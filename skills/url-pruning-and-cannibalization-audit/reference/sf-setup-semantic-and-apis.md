# Crawler setup: APIs, embeddings, crawl analysis, exports (Screaming Frog)

Read Screaming Frog's own tutorial on identifying semantically similar pages before the first run
(screamingfrog.co.uk, SEO Spider tutorials); menus move between versions. API keys and Google accounts
are often saved in the app already: select them and press Connect. Check the saved accounts before
asking the user for keys.

## Order of operations (every crawl)

1. **Google APIs.** Config > API Access > Google Search Console > Account Information: pick the saved
   account, Connect, choose the property. Repeat under Google Analytics 4 (wait for the data stream list
   to load; choose Account, Property and "All Data Streams"). URL Inspection is a tab inside the Search
   Console config and must be enabled. OK. The right-hand API tab must show Connected for each; verify it
   on screen.
2. **AI provider.** Config > API Access > AI. Embeddings can come from OpenAI, Gemini or a local model
   (the tutorial lists the current options). Prompt Configuration > Add from Library > the "extract
   semantic embeddings from page" prompt. Account Information: pick the saved key, Connect.
3. **Store HTML.** Config > Spider > Extraction: Store HTML and Store Rendered HTML.
4. **Embeddings on.** Config > Content > Embeddings: enable embeddings, Semantic Similarity and Low
   Relevance.
5. **Content area.** Config > Content > Area: exclude navigation, footer and boilerplate, or shared chrome
   dominates the text and templated pages look identical.
6. **Speed.** Reduce embedding dimensions (`outputDimensionality` for Gemini, `dimensions` for OpenAI).
   Free tiers are slow; check your provider's current rate limits. For long pages limit the page content
   sent for embedding (a few thousand characters is enough).
7. **Crawl.** Full site: URL and Start. List: Mode > List, Upload > From a File. Wait until crawl
   progress and API progress both read 100 percent.
8. **Crawl Analysis > Start** (or Configure > Auto-Analyse at End of Crawl). Similarity filters stay empty
   until it runs.
9. **Read.** Content tab: Semantically Similar (default threshold 0.95) and Low Relevance Content
   (default 0.4); Duplicate Details lists similar pages.
10. **Export.** Bulk Export > Content > Semantically Similar for pairs. Export the Internal table (with the
    embeddings column), page visible text and raw HTML. If you drive the crawler through an automation
    wrapper (MCP server or command line), check its parameter names: wrappers often want a path relative
    to an allowed base folder, refuse absolute paths, and return results inline (writing nothing) when a
    parameter name is wrong. Check the file exists after every export.

## Cluster diagram

Visualisations > Content Cluster Diagram plots the embeddings in 2D (sampling, dimension reduction,
cluster count and colour settings; right-click a node for its inlinks). It exports as an SVG of the
viewport only, with no per-URL cluster ID. For grouped rows, cluster the exported vectors or the page
text yourself (`data/similarity_groups.py`), and use the diagram to eyeball the result.

## If the AI columns are empty

Check the AI tab for the embedding value and the prompt request status, and test the prompt on one URL to
separate a key or quota problem from a settings problem. If the cause is not found quickly, stop and flag
it, then use the text method in `similarity-grouping-and-merge-check.md` and say so in the Method sheet.

## Request API Data on an existing crawl

Connect the API, then click Request API Data (bottom of the API tab). It fills the columns for
already-crawled URLs without a recrawl. Progress text can read "0 of 0" while data arrives, so count the
cells.

## Verify before using the data

Count non-empty cells per column: Clicks, Impressions, GA4 Sessions, Indexability Status, Closest
Semantically Similar Address, Semantic Similarity Score, and the embeddings vector. An empty column means
the source was not connected or the step was skipped. Stop and fix it. Never substitute another source
and carry on.
