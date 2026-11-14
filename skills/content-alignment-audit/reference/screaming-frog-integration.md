# Screaming Frog: crawl, embeddings and similarity exports

Contents: The one thing to know first · Running the crawl · Exports you need · Cosine similarity · Similarity for pages without a vector · Joining with Search Console · Timing · End-to-end outline · Rules that apply to any crawler-based skill

How to get the crawl and similarity data this audit needs out of Screaming Frog SEO Spider. There are
three ways to drive it:

- **The UI:** menu actions, the Content tab and Bulk Export.
- **Its documented headless command line:** crawl, save and export without the UI. Check the vendor's
  command-line documentation for the exact flags and export names in your version.
- **An automation wrapper** (an MCP server or your own script around the command line): check its
  parameter names and what it reports while a crawl runs.

Whichever route you use, the settings saved in the UI (embeddings, content area, stored HTML) are what the
crawl uses, so set them up first (`sf-ui-setup-guide.md`).

## The one thing to know first

Semantic similarity only appears when an AI embeddings provider is connected in the UI, the embedding
options are on before the crawl, and Crawl Analysis runs after it.

If the Semantically Similar export is empty, the cause is one of:
- embeddings not set up (no provider connected, or options not ticked before the crawl);
- Crawl Analysis not run;
- no page scored above the similarity threshold.

The export lists only pages whose nearest neighbour passes the threshold (0.95 by default), so a blank is
not "no similar page". Count pages that have an embedding vector before reading blanks. To see the
0.70–0.95 band, lower the threshold if your version allows it, or compute pairwise cosine similarity from
the exported vectors (`../data/similarity_pairs.py --vectors`).

## Running the crawl

**UI:** enter the site URL (or switch to List mode and paste the URL list) and press Start. Wait until the
crawl bar and the API bar both reach 100%, then run Crawl Analysis > Start (or turn on Crawl Analysis >
Configure > Auto-Analyse at End of Crawl before the crawl).

**Headless command line:** run the crawler with its headless and crawl options, a saved configuration file
that has embeddings and the content area set, an output folder, and the exports you need, for example:

```
<seo-spider-cli> --headless --crawl https://example.com \
  --config audit.seospiderconfig --save-crawl --output-folder ./crawl-output \
  --export-tabs "Internal:All" --bulk-export "<Semantically Similar export name>"
```

There is no button to press for Crawl Analysis in headless mode, so turn on Auto-Analyse at End of Crawl
in the configuration you pass. The executable name and export names differ by operating system and
version: take them from the vendor's documentation.

**Automation wrapper:** start the crawl with the site URL, the saved configuration, and an output location.
Name the crawl after the audit and the date so you can reopen it later.

**Wait for everything to finish before exporting.** Export only after the crawl, the embeddings API queue
and Crawl Analysis have all finished; an export started early can fail or come back incomplete. If you use
a wrapper, wait until it reports the crawl as finished and idle.

## Exports you need

**Internal (all HTML pages):** `Address`, `Status Code`, `Indexability`, `Title 1`, `H1-1`, `Word Count`,
`Inlinks`, and the embedding column ("Extract semantic embeddings from page") when embeddings are on.
Use it for the page set, the vector coverage count and, if you compute similarity yourself, the vectors.

**Content > Semantically Similar (bulk export):** `Address` (the page), `Closest Semantically Similar
Address` (its nearest neighbour), `Semantic Similarity Score` (0–1 cosine similarity). This is the input
`../data/run_audit.py --pairs` reads directly.

**Also useful:** exact duplicates, near duplicates (needs its own threshold set before the crawl), 404
response codes and canonical chains.

Column names can change between versions; check the header row before joining.

## Cosine similarity

cos(θ) = (A · B) / (‖A‖ × ‖B‖), where A and B are two pages' embedding vectors. For text embeddings the
useful range is 0 to 1.

Working bands (calibrate per model and site):
- **1.0**: identical main content
- **0.90–1.0**: very similar (redirect or retire candidates)
- **0.75–0.90**: similar (repurpose, refresh or reformat candidates)
- **0.60–0.75**: related (usually keep both)
- **< 0.60**: distinct

Different embedding models produce different score distributions. Check a few pairs at each band by eye
before applying the decision matrix.

## Similarity for pages without a vector

If some pages have no embedding (blocked rendering, API errors, pages added from another list), compare
their visible main text instead: strip navigation and footer, build a TF-IDF vector per page (word
unigrams and bigrams, English stop words removed) and take the cosine similarity between pages. Mark these
scores as text-based in Research_Notes; they run lower than embedding scores for the same pair, so read
them against their own bands. `../data/similarity_pairs.py --texts page_texts.csv` does this; combine it
with `--vectors` to score only the pages that lack a vector. The text file must hold the main text of
every page in scope, including pages that have a vector, because the TF-IDF weights are fitted over the
whole file and a page without a vector can only be compared with pages whose text is there. Under 20
pages of text the script skips its frequent-term cut (`--max-df`) and warns that the scores are rough.

## Joining with Search Console

### URL encoding and slashes

**Problem:** Search Console shows `/blog/cold-brew-guide/` and the crawl shows an encoded or differently
slashed form of the same URL, so a join on raw strings silently drops rows.

**Fix:** normalise both sides before joining.

```python
from urllib.parse import unquote

def norm(u):
    u = unquote(u.strip())
    return u[:-1] if u.endswith("/") and u.count("/") > 3 else u
```

### URL × query exports

**Problem:** the same URL appears on many rows, one per query.

**Fix:** aggregate to one row per URL before joining: sum impressions and clicks, impression-weighted mean
position.

```python
rows = {}
for r in gsc_rows:
    u = norm(r["URL"])
    a = rows.setdefault(u, {"imp": 0, "clk": 0, "pos_x_imp": 0.0})
    imp = float(r["Impressions"])
    a["imp"] += imp
    a["clk"] += float(r["Clicks"])
    a["pos_x_imp"] += float(r["Position"]) * imp
# position = pos_x_imp / imp for each URL with imp > 0
```

## Timing

Crawl time depends on site size, server speed and crawl-speed settings. Embedding time depends on the
provider's rate limit: free tiers are slow enough that a large site waits on the API, so use a paid tier
or reduce the page set. Exports themselves are quick. Test on a small crawl first to estimate the full run.

## End-to-end outline

1. Load and aggregate the Search Console data, normalising URLs.
2. Start the crawl with embeddings on (UI, command line or wrapper).
3. Wait until the crawl, the embeddings queue and Crawl Analysis have all finished.
4. Export Internal (with the embedding column) and Content > Semantically Similar.
5. Join crawl and Search Console data on the normalised URL (left join from the crawl).
6. Check vector coverage; compute missing pairs from vectors or page text with
   `../data/similarity_pairs.py --vectors internal.csv --texts page_texts.csv`.
7. Run `../data/run_audit.py --gsc gsc.csv --pairs similarity.csv` for draft clusters, then continue with
   the scrape and the decision matrix.

## Rules that apply to any crawler-based skill

1. Settings saved in the UI apply to every later crawl, including crawls started from the command line or
   a wrapper. Configure once, then verify on a small crawl.
2. Crawl Analysis fills the similarity filters; without it they stay empty.
3. Export only after everything has finished.
4. Normalise URLs on both sides of every join.
5. Aggregate Search Console URL × query data to one row per URL before joining.
