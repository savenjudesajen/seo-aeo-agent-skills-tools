# llms.txt: spec, evidence and examples

## The spec (llmstxt.org, proposed by Jeremy Howard in September 2024, since revised)
In order:
1. An H1 with the site or product name. The only required element.
2. A blockquote with a one or two sentence summary.
3. Optional plain paragraphs or bullets (positioning, important notes).
4. H2 sections, each a list of `- [Name](URL): description`.
5. `## Optional` last: secondary links an agent can skip when its context is short.

The file lives at the root (`/llms.txt`) or at a subpath (`/docs/llms.txt`, which covers
URLs under it). The spec also suggests a Markdown copy of each page at the same URL with
`.md` appended. `llms-full.txt` (all page content concatenated) is a community
convention, not in the core spec; it belongs beside llms.txt, never in place of it.

## The evidence (Semrush, "What is llms.txt?", 2026)
- No major platform (ChatGPT, Google AI Overviews, Claude) has confirmed using it. Google's
  John Mueller said in June 2025 that AI systems do not use it.
- Semrush put one on Search Engine Land in March 2025. Logs over the following two months
  showed zero visits from GPTBot, PerplexityBot and ClaudeBot; Googlebot and Bingbot
  fetched it a few times. No correlation with AI results.
- Adoption grew from under a thousand tracked domains in mid-2025 to well over ten thousand
  a year later (NerdyData figures cited in the article).
- Semrush Site Audit flags a missing llms.txt, and Google Lighthouse has an experimental
  agentic-browsing check for it. Both are checks, not evidence that any engine reads it.
- Their advice: treat it as a cheap experiment, keep it current, and spend the real effort
  on rendering, crawler access and content.

Client line to reuse: "There is no measured benefit yet, it takes about an hour, and it
gives assistants a clean map of the pages you most want quoted. Low priority."

## Public examples worth reading
Shapes and counts are approximate and change often; re-read a file before you cite it.

| File | Shape | Copy | Avoid |
|---|---|---|---|
| semrush.com/llms.txt | ~100 lines, about 9 H2s, ~40 links, descriptions on nearly all, Optional section | The best template for a commercial brand: summary plus positioning paragraphs, products, pricing, free tools, help | A section placed after Optional |
| cal.com/docs/llms.txt | ~50 links, a small root that points to nested index files | Hierarchy that scales to large doc sets | Only a third of links have descriptions; a duplicate link |
| platform.claude.com/llms.txt | Hundreds of `.md` links, an llms-full.txt linked | Advertises the MCP server and the language/SDK inventory | Repeated generic titles, no Optional section on a very large file |
| searchengineland.com/llms.txt | One H2 of a few hundred recent posts with dates and excerpts | Dates on each entry | An auto-generated news feed, no evergreen pages, `&amp;` left in the blockquote |
| Hugging Face Diffusers llms.txt | Over a million characters, tens of thousands of lines, hundreds of H1s and H2s of concatenated docs | | A full-content dump at the llms.txt URL, MDX components left in; the checker's multiple-H1 rule flags it |
| ai-sdk.dev/llms.txt | Over 100K characters of concatenated docs with front matter | Per-page front matter | Same dump problem; legacy API content ages fast |

Lessons from reading these: some files presented as "examples" in articles are not
llms.txt files under the spec at all, so read a file before you cite it as a model. A file
with text before the H1 fails the spec. The most spec-faithful documentation files open each
section with a one-line "use this when" note, link to `.md` copies of the pages, keep
`## Optional` last and point to llms-full.txt; avoid imperative instructions aimed at agents.

## Benchmark the client's competitors
On every audit, fetch llms.txt on 3 to 5 direct competitors and put the result in the
crawlability section of the audit. Record per competitor:

| Competitor | Status | Links | H2 sections | Passes spec? | Notable pattern |
|---|---|---|---|---|---|
| CompetitorA | 200 Markdown | N | N, Optional last | Yes | |
| CompetitorB | 200 Markdown | N | N, no Optional section | Yes | Long file an agent cannot trim |
| CompetitorC | 200 Markdown | N | Many H1s and H2s | No (full-content dump) | Belongs in llms-full.txt |
| CompetitorD | 404 | n/a | n/a | No file | |

(The rows are illustrative patterns, not real sites.) Run each through the checker's
llms.txt mode: an HTML body returned with status 200 is a soft 404, not a file.

## A glossary-style section
If the brand uses product or feature names an assistant could misread, a short plain
paragraph under the summary saying what each name refers to is allowed by the spec
(optional paragraphs before the H2s) and costs little.

## Choosing what goes in, for a services or B2B brand
1. Services and capability pages (the pages that should be named in a shortlist answer).
2. Proof: case studies, certifications, awards, leadership.
3. The evergreen guides that answer the category's research questions.
4. About, ownership, locations and contact (the facts assistants get wrong).
5. Optional: the blog index, news, webinars, careers.

Leave out thank-you, gated, campaign, legal and expiring pages. Use the canonical,
indexable, 200 URL of each page; the checker flags relative links.
