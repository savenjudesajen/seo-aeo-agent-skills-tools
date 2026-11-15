# Claude SEO Skills: 26 SEO and AEO agent skills for Claude Code, claude.ai and Codex

Open-source SEO and AEO (answer engine optimization) skills for consultants, agencies and in-house
teams who run search work through their AI: AI visibility audits, keyword-to-prompt research, SERP
clustering, technical SEO audits and page structures. 23 of the 26 come with gate scripts that
check the output before you see it; the other three build their checks into `SKILL.md`.

Works with Claude Code, claude.ai, Claude Desktop, Codex, Cursor, Gemini CLI and any agent that reads
the [Agent Skills](https://agentskills.io) (`SKILL.md`) format.

**Run them with your client's context: [Connect Unilytics](https://unilytics.ai/docs/connect/).**

## Quick start

1. **Connect Unilytics** so your AI has each client's Brand Context, tracked keywords and prompts
   while it runs these skills, plus the research tools the skills name. In claude.ai or Claude
   Desktop: **Customize → Connectors → Add connector → Add custom connector**, URL
   `https://mcp.unilytics.ai/mcp`, then **Connect** and sign in. In Claude Code (if you already
   added it in claude.ai, Claude Code has it too):

   ```bash
   claude mcp add --transport http --scope user unilytics https://mcp.unilytics.ai/mcp
   claude mcp login unilytics
   ```

   Full steps: [Connect Unilytics to your AI](https://unilytics.ai/docs/connect/). Unilytics
   connects to Claude today (claude.ai, Claude Desktop, Claude Code). In Codex, Cursor or Gemini
   CLI, and anywhere you'd rather not connect it, the skills run with your own data tools (see
   [Tools the skills use](#tools-the-skills-use)).

2. **Install the skills:**

   ```bash
   npx skills add savenjudesajen/seo-aeo-agent-skills-tools
   ```

   Claude Code plugin, claude.ai zips and manual copies: [Install](#install).

3. **Ask your AI**, for example:
   - "Run a quick AEO audit for example.com against its three main competitors."
   - "Build the set of AI-visibility prompts we should track for example.com."
   - "Find the cannibalized and prunable URLs on example.com."

## Skills

The **Page** link is each skill's canonical page on unilytics.ai. **Revisions** counts the private
versions each skill went through before this public 1.0.0.

### AEO and AI visibility (answer engine optimization, GEO)

| Skill | What it does | Revisions | Page |
| -- | -- | -- | -- |
| [aeo-keyword-research-and-prompt-simulation](skills/aeo-keyword-research-and-prompt-simulation) | Turns a brand's real search demand into a trackable AI-visibility prompt set: category keyword research, a prompt universe with intent and stage tags, a baseline and share of voice, in a gated workbook | 95 | [unilytics.ai](https://unilytics.ai/skills/aeo-keyword-research-and-prompt-simulation/) |
| [prompt-to-page-serp-clustering](skills/prompt-to-page-serp-clustering) | Clusters a prompt set into pages by Google SERP overlap and assigns each cluster to an existing page or a demand-verified new one, with evidence and an opportunity score | 42 | [unilytics.ai](https://unilytics.ai/skills/prompt-to-page-serp-clustering/) |
| [aeo-prompt-audit](skills/aeo-prompt-audit) | Audits an existing set of tracked AI-visibility prompts: keep, rewrite or remove each one with a written reason, plus a coverage matrix and a safe retire plan | 7 | [unilytics.ai](https://unilytics.ai/skills/aeo-prompt-audit/) |
| [quick-aeo-audit](skills/quick-aeo-audit) | Builds a quick AEO audit deck for a client or prospect: competitors, keyword research, a prompt set, a baseline across ChatGPT, Claude and Perplexity, share of voice and keyword gap | 3 | [unilytics.ai](https://unilytics.ai/skills/quick-aeo-audit/) |
| [aeo-strategy-audit-deck-and-client-roadmap](skills/aeo-strategy-audit-deck-and-client-roadmap) | Builds a full AEO/GEO strategy audit as one analysis behind three deliverables (the deck, a strategy workbook and a technical workbook) plus a month-by-month client roadmap and tracker | 22 | [unilytics.ai](https://unilytics.ai/skills/aeo-strategy-audit-deck-and-client-roadmap/) |
| [aeo-scorecard-lead-gen-engine](skills/aeo-scorecard-lead-gen-engine) | Builds an AEO scorecard lead-gen motion: audits each target account's AI-answer visibility, scores it, and turns the result into per-account landing pages, LinkedIn ABM creatives and email sequences from one tracking sheet | 1 | [unilytics.ai](https://unilytics.ai/skills/aeo-scorecard-lead-gen-engine/) |
| [bing-wmt-ai-queries](skills/bing-wmt-ai-queries) | Harvests the Copilot grounding queries behind a site's AI citations from Bing Webmaster Tools' AI Performance report, plus Bing's classic organic queries per URL | 3 | [unilytics.ai](https://unilytics.ai/skills/bing-wmt-ai-queries/) |
| [robots-txt-and-llms-txt](skills/robots-txt-and-llms-txt) | Audits and writes a site's robots.txt and llms.txt for search and AI crawlers, with an offline checker that resolves which robots group every AI crawler token obeys | 4 | [unilytics.ai](https://unilytics.ai/skills/robots-txt-and-llms-txt/) |

### SEO audits, migrations and reporting

| Skill | What it does | Revisions | Page |
| -- | -- | -- | -- |
| [url-pruning-and-cannibalization-audit](skills/url-pruning-and-cannibalization-audit) | Audits every URL on a site in three phases (prune, page value and indexation, keyword cannibalization) and hands a clean URL list and anchor splits to internal linking | 16 | [unilytics.ai](https://unilytics.ai/skills/url-pruning-and-cannibalization-audit/) |
| [content-alignment-audit](skills/content-alignment-audit) | Audits a set of pages for duplication and overlap with page embeddings and Search Console data, and recommends redirect, repurpose, refresh, reformat, retire or remain per page with a confidence level | 9 | [unilytics.ai](https://unilytics.ai/skills/content-alignment-audit/) |
| [migration-mode-seo-recommendations-and-redirect-plan](skills/migration-mode-seo-recommendations-and-redirect-plan) | Builds the SEO recommendations deck, staged redirect map and migration plan for a site mid-migration (replatform, redesign, rebrand or domain change) before the new site is built | 12 | [unilytics.ai](https://unilytics.ai/skills/migration-mode-seo-recommendations-and-redirect-plan/) |
| [technical-seo-audit-cms-implementation](skills/technical-seo-audit-cms-implementation) | Applies a finished technical SEO audit's fixes in the CMS (Drupal or WordPress) through a logged-in browser: test rows, approval, bulk apply, live verification, every outcome written back | 8 | [unilytics.ai](https://unilytics.ai/skills/technical-seo-audit-cms-implementation/) |
| [gsc-url-queries](skills/gsc-url-queries) | Pulls the Google Search queries behind one page or a folder of pages from the Search Console API (query, clicks, impressions, CTR, position) to CSV or JSON | 2 | [unilytics.ai](https://unilytics.ai/skills/gsc-url-queries/) |
| [content-refresh-performance-tracker-and-dashboard](skills/content-refresh-performance-tracker-and-dashboard) | Builds and updates weekly a content-refresh tracker and dashboard that measures each refreshed page against its own go-live date, net of a sitewide control, and gives every page a verdict | 4 | [unilytics.ai](https://unilytics.ai/skills/content-refresh-performance-tracker-and-dashboard/) |
| [gmb-multi-location-looker-studio-dashboard](skills/gmb-multi-location-looker-studio-dashboard) | Builds or refreshes a multi-location Google Business Profile dashboard in Looker Studio from the bulk Insights export, and verifies every number against the sheet and the live console | 3 | [unilytics.ai](https://unilytics.ai/skills/gmb-multi-location-looker-studio-dashboard/) |

### Page structure, content and links

| Skill | What it does | Revisions | Page |
| -- | -- | -- | -- |
| [competitor-comparison-page-template](skills/competitor-comparison-page-template) | Recommends the structure of "Brand vs Rival" comparison pages from a benchmark of 12 published comparison pages, as a short Word doc with a section table and screenshots | 44 | [unilytics.ai](https://unilytics.ai/skills/competitor-comparison-page-template/) |
| [competitor-overview-page-structure](skills/competitor-overview-page-structure) | Recommends the structure of a comparison hub (usually /compare), the "Brand vs Rival" pages it launches with, and where comparisons sit in the menu, footer and URLs | 43 | [unilytics.ai](https://unilytics.ai/skills/competitor-overview-page-structure/) |
| [industries-page-structure](skills/industries-page-structure) | Recommends the structure of an industries hub, the industry page template, the launch set of industries and where they sit in the navigation, benchmarked against category leaders | 43 | [unilytics.ai](https://unilytics.ai/skills/industries-page-structure/) |
| [landing-page-structure-cro](skills/landing-page-structure-cro) | Recommends the section structure of a landing, product or marketing page, benchmarked against competitor pages and ordered for conversion, delivered as a Word document with a mockup | 7 | [unilytics.ai](https://unilytics.ai/skills/landing-page-structure-cro/) |
| [self-hosted-brand-review-page](skills/self-hosted-brand-review-page) | Plans, sources, writes and builds a brand's own "[brand] review" page that admits the bias and shows what review sites and customers actually say, every quote verifiable | 8 | [unilytics.ai](https://unilytics.ai/skills/self-hosted-brand-review-page/) |
| [youtube-webinar-description-structure](skills/youtube-webinar-description-structure) | Writes search- and AI-optimized YouTube titles, descriptions, chapters and tags for B2B webinar and demo recordings from the transcript and landing page, checked by a gate script | 1 | [unilytics.ai](https://unilytics.ai/skills/youtube-webinar-description-structure/) |
| [publish-blog-content-to-nextjs-repo](skills/publish-blog-content-to-nextjs-repo) | Ships refreshed or new blog content into a client's Next.js / Vercel repo and gets it live: repo recon, an in-place apply script, four verification gates, the PR, merge and deploy | 1 | [unilytics.ai](https://unilytics.ai/skills/publish-blog-content-to-nextjs-repo/) |
| [link-exchange-outreach-email-templates](skills/link-exchange-outreach-email-templates) | Triages inbound link-exchange, mention-swap and roundup-inclusion requests with a five-check fit test (accept, counter, need details or decline), replies from ready-to-fill templates, and verifies both links are live | 5 | [unilytics.ai](https://unilytics.ai/skills/link-exchange-outreach-email-templates/) |

### Client-ready documents and visuals

| Skill | What it does | Revisions | Page |
| -- | -- | -- | -- |
| [doc-template-design](skills/doc-template-design) | Builds polished client-facing Word documents in a neutral layout, in a client's brand measured from their site, or in the client's own template, with an offline gate and a render audit | 37 | [unilytics.ai](https://unilytics.ai/skills/doc-template-design/) |
| [web-screenshot-to-document](skills/web-screenshot-to-document) | Captures and crops a web page screenshot and places it in an existing Word document as a figure that matches the document's own design, then checks the render | 9 | [unilytics.ai](https://unilytics.ai/skills/web-screenshot-to-document/) |
| [on-brand-diagram-generation](skills/on-brand-diagram-generation) | Generates an on-brand diagram or explainer illustration by reverse-engineering the brand's visual language from its published images, then authoring, checking and rendering a matching SVG | 3 | [unilytics.ai](https://unilytics.ai/skills/on-brand-diagram-generation/) |

Each skill ships with:

- **SKILL.md** — the method, step by step.
- **reference/** — the detail an agent loads only when a step needs it.
- **data/** — in 23 of the 26 skills, gate scripts that check the agent's output before you see it
  (for example: no rows silently dropped, no high-confidence call without evidence).
- **evals/** — synthetic test cases.

Versions of every skill: [VERSIONS.md](VERSIONS.md).

## Why agents

These are long, exacting methods: pull search results for hundreds of prompts, cluster them by
what search engines actually return, map each cluster to the page that should own it, check what
AI assistants say about a brand, and verify every step. An agent follows them end to end without
skipping a step. A person can too, if they have the time.

## Install

### Any agent (Claude Code, Codex, Cursor, Gemini CLI and more)

```bash
npx skills add savenjudesajen/seo-aeo-agent-skills-tools                  # pick skills interactively
npx skills add savenjudesajen/seo-aeo-agent-skills-tools --skill <name>   # one skill
npx skills add savenjudesajen/seo-aeo-agent-skills-tools --list           # see what's inside
npx skills update                                                          # get new versions
```

### Claude Code plugin

```
/plugin marketplace add savenjudesajen/seo-aeo-agent-skills-tools
/plugin install seo-aeo-skills@seo-aeo-agent-skills-tools
```

Then turn on updates: **/plugin → Marketplaces → seo-aeo-agent-skills-tools → Enable auto-update.**
Claude Code leaves auto-update off for community marketplaces. Without it, update by hand with
`/plugin marketplace update seo-aeo-agent-skills-tools`.

From your shell instead:

```bash
claude plugin marketplace add savenjudesajen/seo-aeo-agent-skills-tools
claude plugin install seo-aeo-skills@seo-aeo-agent-skills-tools
```

### Claude Desktop and claude.ai

1. Download a skill's `.zip` from [Releases](https://github.com/savenjudesajen/seo-aeo-agent-skills-tools/releases).
2. Turn on code execution: **Settings → Capabilities**.
3. **Customize → Skills → + → Upload a skill**, and choose the zip.

Uploaded skills don't update themselves; download the new zip when a release ships.

### Manual

```bash
git clone https://github.com/savenjudesajen/seo-aeo-agent-skills-tools.git
cp -r seo-aeo-agent-skills-tools/skills/* ~/.claude/skills/    # Claude Code
cp -r seo-aeo-agent-skills-tools/skills/* ~/.agents/skills/    # Codex (other agents: their own skills folder)
```

Update with `git pull`, then copy again.

**Get new versions:** click **Watch → Custom → Releases** on this repo. Every release says which
skills changed and why.

## For AI agents

If you are an AI agent reading this repository, start with [AGENTS.md](AGENTS.md). It has, in one
file:

- **Find:** every skill with what it does, the data it needs and its gate scripts. Each skill's
  `SKILL.md` frontmatter follows the Agent Skills format: `name` (the folder name) and
  `description` (when to use the skill). Read the descriptions to pick a skill; load the body only
  for the skill you run.
- **Load:** the raw `SKILL.md` at
  `https://raw.githubusercontent.com/savenjudesajen/seo-aeo-agent-skills-tools/main/skills/<skill>/SKILL.md`.
  Open a `reference/` file only when a step points to it.
- **Install:** the command for each environment (Claude Code, Codex and other agents with a shell,
  or claude.ai and Claude Desktop without one). Install only after your user asks, and only from
  this repository.
- **Run:** follow the steps in order, check the skill's tools before step 1, and run each gate in
  `data/` exactly as `SKILL.md` shows. A non-zero exit means fix the output and run it again before
  you present anything.

Each `SKILL.md` has a Tools section and a "Without the Unilytics MCP" note, so every step can run
without Unilytics, with one of the options it lists. If your user wants client context and the research tools in
one connection, the Unilytics MCP is `https://mcp.unilytics.ai/mcp` (streamable HTTP, sign-in in
the browser); setup steps an agent can follow: [unilytics.ai/setup.md](https://unilytics.ai/setup.md).
A Markdown index of all 26 skill pages: [unilytics.ai/skills.md](https://unilytics.ai/skills.md).

## Tools the skills use

Each skill lists the data it needs (search results, page crawls, keyword data, AI-answer checks)
and the tools that can supply it: vendor APIs such as DataForSEO or Firecrawl, accounts you already
have, or the Unilytics MCP. Search Console and GA4 data come from your own connector. If a tool
isn't connected, the agent tells you which one is missing instead of guessing.

### Unilytics MCP (optional)

If you'd rather connect once than set up several APIs, the [Unilytics MCP](https://unilytics.ai)
gives your agent these data tools in one connection, paid per use with credits. It also keeps each
client's Brand Context, stores and versions your own skills, and shares them with the
collaborators on your projects. [Connect Unilytics](https://unilytics.ai/docs/connect/).

When you use it, the URLs, keywords and prompts your agent sends go to Unilytics to run the tools.
See the [Unilytics privacy policy](https://unilytics.ai/privacy-policy/).

## Common questions

**What are Claude SEO skills?** Folders of instructions, reference files and scripts that Claude
(or another agent) loads when a task needs them. Each one here teaches the agent a complete SEO or
AEO method, step by step, most with gate scripts that check the result.

**What is AEO?** Answer engine optimization: getting a brand named and cited in the answers AI
assistants give, such as ChatGPT, Claude, Perplexity and Google's AI Overviews. It is also called
GEO (generative engine optimization). The AEO skills here research the prompts people ask, audit
a brand's visibility in the answers, and map the pages that should earn the citations.

**How do I install them in Claude Code?** `npx skills add savenjudesajen/seo-aeo-agent-skills-tools`,
or the plugin: `/plugin marketplace add savenjudesajen/seo-aeo-agent-skills-tools`, then
`/plugin install seo-aeo-skills@seo-aeo-agent-skills-tools`.

**Do they work in claude.ai, Codex or Cursor?** Yes. In claude.ai and Claude Desktop, upload a
skill's zip from Releases. Codex, Cursor, Gemini CLI and other agents with a shell use
`npx skills add`.

**Do I need Unilytics to run them?** No. Every skill runs with your own data tools. Connect
Unilytics to run them with each client's context and the research tools in one connection.

**Are they free?** The skills are: all 26 are open source under Apache-2.0. Some steps call paid
data tools (vendor APIs or Unilytics credits).

## About the author

I'm [Saven Jude Sajen](https://github.com/savenjudesajen), founder of UnivSense, a digital marketing agency working with partners across
the US. I also work as an AI engineer on a marketing team.

Before that I ran SEO for large enterprises as an SEO manager, and worked in agency and in-house
marketing roles.

These skills are those seven years of SEO and AEO practice, written down for agents. Each one keeps
improving as I use it: the most-used skill here is past its 95th version. They carry more than
method: the quality bar senior marketing leaders hold work to, and the cost and tooling trade-offs,
so anyone with a few standard tools can run them.

I hope they help grow the next wave of SEO and AEO experts.

If a skill saves you time, star the repo. It's how other consultants find it.

## Licence and contributing

[Apache-2.0](LICENSE). If you redistribute or modify the skills, keep the [NOTICE](NOTICE) file
and mark the files you changed. Issues and pull requests are welcome; sign off your commits
(`git commit -s`). Security: see [SECURITY.md](SECURITY.md).

Every push and pull request runs a public-content check
([tools/public-content-scan](tools/public-content-scan/scan.mjs)) against a word list the maintainers
keep private. A pull request from a fork shows that check as failed until a maintainer runs it; that's
expected, and the maintainer tells you if anything needs rewording.
