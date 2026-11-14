# AI crawler tokens (checked against vendor docs at time of writing)

Re-check the vendor pages on every audit; new tokens appear every few months. If you find a
token that is not in this table or in the checker's `AI_TOKENS`, add it to both.

| Vendor | Token | Role | Keep allowed for AEO? | Notes from the vendor docs |
|---|---|---|---|---|
| OpenAI | OAI-SearchBot | ChatGPT search index | Yes | Sites that opt out are not shown in ChatGPT search answers |
| OpenAI | ChatGPT-User | User-triggered fetch | Yes | robots.txt "may not apply"; not used for search inclusion |
| OpenAI | GPTBot | Training | Client's choice | Disallow means content should not be used in training |
| OpenAI | OAI-AdsBot | Ad landing-page checks | Yes | |
| Anthropic | Claude-SearchBot | Search indexing | Yes | Blocking reduces visibility in Claude's search answers |
| Anthropic | Claude-User | User-triggered fetch | Yes | |
| Anthropic | ClaudeBot | Training | Client's choice | Anthropic supports Crawl-delay |
| Anthropic | anthropic-ai | Legacy | n/a | No longer in Anthropic's current article; harmless to keep |
| Perplexity | PerplexityBot | Search index | Yes | Not used to train foundation models |
| Perplexity | Perplexity-User | User-triggered fetch | Yes | Generally ignores robots.txt |
| Google | Googlebot | Search, AI Overviews, AI Mode | Yes | AI features are controlled with Googlebot plus nosnippet, data-nosnippet, max-snippet, noindex |
| Google | Google-Extended | Control token (no crawler) | Client's choice | Gemini training and grounding in other Google systems; does not affect Search or AI Overviews |
| Microsoft | Bingbot | Bing search, Copilot grounding | Yes | |
| Apple | Applebot | Siri, Spotlight, Safari search | Yes | |
| Apple | Applebot-Extended | Control token (no crawler) | Client's choice | Training opt-out; blocking does not remove pages from Apple search |
| Common Crawl | CCBot | Open crawl dataset | Client's choice | The dataset most training sets start from |
| Meta | meta-webindexer | Meta AI search | Yes | Allowing it lets Meta AI cite and link the site |
| Meta | meta-externalagent | Training and indexing | Client's choice | |
| Meta | meta-externalfetcher | User-triggered fetch | Yes | May bypass robots.txt |
| Meta | facebookexternalhit | Link previews | Yes | |
| Amazon | Amzn-SearchBot | Alexa and search | Yes | Not used for generative AI training |
| Amazon | Amazonbot | General, may train | Client's choice | Does not support Crawl-delay; robots.txt cached up to 30 days |
| ByteDance | Bytespider | Search and training | Client's choice | Compliance disputed in press reports; spoofing common |

Sources (vendor documentation): developers.openai.com/api/docs/bots;
support.claude.com (Anthropic's article on its crawlers); docs.perplexity.ai/guides/bots;
developers.google.com/search/docs/crawling-indexing/google-common-crawlers;
developers.google.com/search/docs/appearance/ai-features; support.apple.com/en-us/119829;
commoncrawl.org/ccbot; developers.facebook.com/docs/sharing/webmasters/web-crawlers;
developer.amazon.com/amazonbot.

## How to use the table
- A training token and a search token from the same vendor are separate decisions. Blocking
  GPTBot does not remove a site from ChatGPT search; blocking OAI-SearchBot does.
- "Client's choice" rows go in the deliverable as a decision for the client to make, with the
  trade-off stated in one line (training reach versus content reuse). Record their answer.
- User-triggered fetchers may ignore robots.txt by design. If a client wants them stopped,
  that is a firewall or bot-management job, not a robots.txt rule.
- Control tokens (Google-Extended, Applebot-Extended) never appear in server logs: there is
  no crawler behind them. Do not report "no Google-Extended hits" as evidence of anything.
