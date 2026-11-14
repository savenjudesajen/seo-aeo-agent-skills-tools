# Slide-execution depth: how to do each analysis slide properly

Contents: Golden rule: show the GAP, not the win · Get the page data first · BLUF audit: top 25 pages (not 5) · Formatting and extractability: a content deep-dive, not an error list · Information gain: open each page before you classify it · Information gain: name the proprietary data opportunities · On-Page and Metadata: priority columns from the technical audit · Site Architecture: the navigation menu, audited against competitors · Internal Linking (pillar-cluster) slide: the hub model · Certifications and claims: check the footer and the PDFs before writing a trust finding · Open goals: split by KPI before writing the number · Roadmap slides: content first · Topical Authority Map: Own / Expand / Build / Deprioritize, reasoned from data · Expansion opportunities are Expand rows of the theme table · Share of voice / AI-visibility scoreboard: ranked, across the full set · Prompt-level detail: which prompts they win and lose · Where AI gets its answers: third-party sources by TYPE, not competitor sites · Earned channels (community / video): check across all prompts, verify live · AI accuracy check (hallucinations): real, tested · Owned vs earned message alignment: evidenced · Content velocity: client vs competitors' publishing cadence · Use a real browser for UI audits · The winning-page skeleton (cite on the What Wins slide) · Content freshness (recommend on the retrofit or on-page slide)

The failure mode is surface-level work: a table of placeholders, a five-page sample, a one-line finding,
or a competitor table where a third-party-source analysis belongs. Every slide below must be backed by
data you pulled and pages you actually opened. These are analysis standards, not a layout: they apply in
the client's template, a reference deck's format, or the neutral default.

## Golden rule: show the GAP, not the win

The client is paying for AEO because they have a gap. Choose the prompt, metric and framing that expose
where they LOSE. If you lead with a prompt where they are already number 1, they will ask why they need
this. Keep one proof-of-concept win to show the playbook works (a term the client coined returning them
first, say), but lead with the gap.

## Get the page data first

Use the client's organic-pages export (URL, traffic, number of keywords, primary intent, top keyword,
answer-engine flags and AI-prompt counts where the tool has them) as the master page list. It gives you
the top 25 by traffic for BLUF, the intent mix, and which pages already earn answer-engine visibility. If
you do not have it, crawl and pull it, or ask the client for it in chat.

## BLUF audit: top 25 pages (not 5)

Rank the top 25 organic pages by traffic. For each, OPEN the page and check whether the first 40-60 words
answer the page's core question. Score present or missing. Output: X of 25 have an answer-first block,
the priority retrofits (highest-traffic pages missing it), and two or three example rewrites. Never sample
five and call it done.

## Formatting and extractability: a content deep-dive, not an error list

Not a technical-error dump (that belongs on the technical slide). For the priority pages, assess the
actual content structure: heading hierarchy (is the H1 a question, are the H2s question-form),
answer-first blocks, lists and tables versus walls of prose, FAQ presence, and how extractable each chunk
is. Show, per page, what is structurally blocking AI extraction and the fix.

## Information gain: open each page before you classify it

Never blanket-label "AI will ignore this". For every page you call commodity: OPEN it and confirm it has
no original or proprietary data, no unique point of view or method, and content any competitor could have
written. Only then is it commodity, and say what you saw. For proprietary pages, name the actual asset (a
published index or benchmark the client runs, a client outcome with numbers, a coined term). The
classification must cite the page.

## Information gain: name the proprietary data opportunities

1. Inventory competitor data assets, direct and indirect: pages built on original data (indexes,
   surveys, benchmarks, calculators, annual reports), each with its traffic, AI prompts and referring
   domains.
2. Inventory the client's own data: published numbers (case-study outcomes, year-in-review stats, product
   stats) and data they hold but have not published.
3. Hand-write the opportunity rows: the data, the format, the question it answers, what competitors
   publish on it, and a priority. Each row is judged by hand; don't generate them in bulk.

The slide keeps the commodity vs proprietary contrast
in short boxes and adds a table of the top 5 opportunities (data, format, the question it answers, what
competitors publish, priority). The full rows ship on the Proprietary Data Opps sheet of the strategy
workbook, with the possible topics on its Content Plan sheet.

## On-Page and Metadata: priority columns from the technical audit

Build this slide from a triage of the crawl, not from raw crawler counts:
- **High:** missing H1, missing titles, titles under 30 characters on selling pages (too short to carry the
  keyword), multiple H1s on money pages, a meta description copied onto a different service page.
- **Low:** titles over 60 characters (truncation only), H1 over 70 characters, security headers,
  readability.
- **Never flag** meta descriptions over 155 characters.
Name the money page behind each High row, and point the Fixes line at the technical issue list, which
carries the affected URLs and the recommended fix.

## Site Architecture: the navigation menu, audited against competitors

This slide is about the nav bar and the information structure, not internal links. Read the client's
header and footer and each direct competitor's menu live. Draw two rows natively with shapes:
- **TODAY:** one column per top-level item, children listed, problems in the alarm colour (a menu item
  linking to `#`, a service that is only an on-page anchor, a mixed bucket, a buried blog, a misspelled
  URL).
- **RECOMMENDED:** one column per top-level item, each child coloured new / exists but move, fix or give it
  a page / keep, tagged with how many competitors carry that page type.
Additive first: existing URLs keep their address, no synonym renames. Check for menu items that link to
`#` where competitors give the same topic its own page. Add one band
for the footer and for buyer's-words menu labels with their search volumes.

## Internal Linking (pillar-cluster) slide: the hub model

Not a table of issues. Build the architecture natively with shapes: the homepage, one column per service
hub, and under each the money page, the pillar, the clusters and the proof pages (case studies, reports,
tools), coloured by action (new / exists, rebuild or relink / exists, keep). Add the link rules (cluster to
pillar first, pillar to money page on the service keyword, money pages and case studies receive links and
never send in-text ones, every post within 3 clicks) and one band of numbers from the crawl's inlink
export (menu links vs body links into service pages). The page-level link plan and a PageRank simulation
need Search Console data; say so in chat if it is missing, never on the slide.

## Certifications and claims: check the footer and the PDFs before writing a trust finding

Before calling a quality or compliance claim unproven, search the crawl's inlink and resource exports for
certificate, award and badge files. Proof often sits in a PDF behind an unlabelled badge, and "the
claim is unproven" becomes an embarrassing finding when the proof is linked sitewide.

## Open goals: split by KPI before writing the number

A prompt whose answer names no tracked brand is an open goal only when it asks for brands or providers.
Learning questions ("how does X work") name nobody by nature; count them separately and measure them on
citation, not mention. State both numbers wherever the open-goal total appears.

## Roadmap slides: content first

Rank the recommendations so the first rows are content: the signed-off keyword and prompt list (with any
new prompts added to tracking), the page map (one owner page per keyword and prompt, titles and H1s
rewritten to carry it), the content calendar led by the biggest-demand pillar, the proprietary data
assets, the pillar and cluster builds, answer-first rewrites. Then the work that makes content findable
(crawlable archive, new service pages and menu) and earned inclusion. Schema, entity markup, Wikidata and
speed go last at Medium. Quick wins open with the content decisions; the 90-day plan puts the CONTENT row
first, Month 1 is decisions (list, page map, calendar) and writing starts in Month 2; Measurement carries
a "Content shipped" card against the calendar.

## Topical Authority Map: Own / Expand / Build / Deprioritize, reasoned from data

The most important slide in the deck; reviewers read it first. Build:
1. A theme table, one row per theme (typically 8-15 themes): demand per month, client pages in the theme
   and how many are unlinked from the rest of the theme, best non-branded top-20 term, AI answers naming
   the client (x of y), brands AI names instead, search leader, verdict, next move.
2. A second slide plotting each theme by demand (x) against the share of AI answers naming the client (y),
   coloured by verdict, so the biggest gaps read at a glance.
3. A Deprioritize line for the themes cut in the keyword review, and a one-line legend.
4. The per-theme evidence as a Topic Summary sheet with live formulas.

A three-box version with one-line bullets is not deep enough and gets sent back.

Arrive at themes from data (the prompt clusters, the pages-export intent mix, the competitor gap), not
guesses. OWN: themes where the client already gets cited or ranks; name the prompts. EXPAND: the growth
plays (glossary, vs and comparison pages, alternatives pages, listicles, client stories, webinar
repurposing), but only after you VERIFY on the live site that the client lacks them or they are weak.
BUILD: demand with no client presence. DEPRIORITIZE / EXIT: themes a competitor owns where the client has
no right to win. Show the tiered competitor models to study.

## Expansion opportunities are Expand rows of the theme table

Glossary, listicles, client stories, vs pages, webinar repurposing: check the live site first. If absent
or weak, add each as an Expand-verdict row of the theme table, or put it in the next-move column of the
theme it serves (do not spin up a new slide). Verify; do not invent.

## Share of voice / AI-visibility scoreboard: ranked, across the full set

Build a ranked brand table across ALL relevant non-branded prompts (exclude branded prompts, where the
client obviously wins): rank, brand, visibility, share of voice, sentiment, average position. Aim for the
full tracked non-branded set (20 or more; about 50 is a good target). Lead with the gap (the incumbents own
the answers, the client registers but rarely), then present any strength honestly (when mentioned, the
client's position beats the incumbents; the problem is frequency). One prompt is never a scoreboard.

## Prompt-level detail: which prompts they win and lose

Not four hand-picked comparisons. Show prompt-level visibility across the tracked set: the handful the
client wins (with share of voice and position) and a clear note on the rest they lose. Include the top
retrieved source domains.

## Where AI gets its answers: third-party sources by TYPE, not competitor sites

This slide answers WHERE the engines pull answers from. Build a table of source domains by type
(competitor, UGC video, UGC community, editorial, analyst) with retrieved percentage and cite rate. The
usual insight is that earned, community and analyst sources get cited at a markedly higher rate than
competitor sites when retrieved. Competitor listicles are ONE row, labelled listicle, low priority, not the
focus. Then give follow-up slides to the highest-leverage channels.

## Earned channels (community / video): check across all prompts, verify live

Base the finding on the retrieved-source data across ALL tracked prompts, not a subset. For video and
community: state retrieval percentage, cite rate and whether the client has any presence (verify live).
Check whether the client runs webinars or has video BEFORE recommending repurposing; if not, it is a
create-from-scratch motion, and say so plainly.

## AI accuracy check (hallucinations): real, tested

Not a thin placeholder. Test the brand across factual prompts (pricing, integrations, founding,
capabilities, ideal customer) and capture where an engine states something wrong. If the engines are
accurate, say so and pivot to the bigger risk (absence). Ground each row in an actual model response.

## Owned vs earned message alignment: evidenced

For each brand topic: what the site says (owned, from a scrape) versus what AI and third parties say
(earned, from prompt tests and search results), the alignment, and the risk. Ground both sides. Surface the
sharpest gap.

## Content velocity: client vs competitors' publishing cadence

Compare recent publishing cadence: the client's last-published date and posts per month against the top
competitors. Pull the dates from the blog and news feeds. Some CMS platforms hide publishing dates from the
blog listing, the post markup AND the sitemap (no lastmod). If you cannot get real dates, raise it with the
reviewer in chat and get cadence from the client's CMS. Do not invent a cadence comparison; if dates are
unavailable, skip the slide.

## Use a real browser for UI audits

When a check needs the rendered page (schema in raw HTML, UI and UX, what a page actually shows, whether a
glossary, resources or events section exists), load it in a browser: navigate, then read the page or run
JavaScript for the raw HTML. Do not guess a page's content or existence. This is required for the BLUF,
information-gain, formatting, expansion and accuracy slides.

## The winning-page skeleton (cite on the What Wins slide)

1. Eyebrow or breadcrumb naming the hub. 2. H1 as a question or a numbered promise. 3. A 40-60 word
answer-first definition directly under the H1 (the biggest single citation lever). 4. H2s phrased as real
questions (what / why / how / vs / types). 5. H3s for every enumerable item. 6. An FAQ block that powers
FAQPage schema. 7. A related-terms internal-link mesh. 8. A branded closing call to action.

## Content freshness (recommend on the retrofit or on-page slide)

Show a visible last-updated date on every blog and money page, and refresh key pages on a regular cycle
(monthly for the most important). Recently updated pages are cited more often by answer engines; if you
quote a figure for that, cite the study on the slide's source line. Put it as a high-priority quick win on
the content-retrofit or on-page slide.
