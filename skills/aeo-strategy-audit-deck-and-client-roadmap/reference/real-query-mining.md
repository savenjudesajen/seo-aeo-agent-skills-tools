# Grounding the prompt universe in real user language

A prompt generator invents plausible prompts. Plausible is not evidenced. Before you generate, spend an
hour mining the questions people **already asked**, in the brand's own data. Generated prompts are a fine
second pass and a poor first one, and a client can always tell which is which.

This also gives the deck something the client cannot dispute: their own numbers.

## 1. Search Console: pull THREE exports, not one

The Search Console UI export is filtered, so the filter you set **is** the dataset. Same date window, three
pulls (or the same three queries through the API with your own connector):

| # | Filter | What it gives you |
|---|---|---|
| 1 | no filter | totals, the brand split, the daily series |
| 2 | query does not contain `<brand>` | the non-brand tail, not drowned by brand volume |
| 3 | **custom regex, queries of 4+ words** | the prompt mine (section 2) |

Regex for the third: `^\s*(\S+\s+){3,}\S+\s*$`

## 2. The 4+ word export is the prompt mine

Long queries are people typing questions rather than keywords. That set is the closest thing to a free,
real, client-specific prompt universe, and it does three jobs at once:

- **Prompt seeds.** Feed the real phrasings into your prompt generator as existing prompts so it expands
  around evidenced language instead of inventing its own. Keep the user's wording; people do not phrase
  questions the way marketers do.
- **Content gaps.** A 4+ word query with impressions and no clicks points at a page that does not exist.
- **The trust cluster** (section 3).

Check every time for literal AI-style prompts (full conversational questions) arriving through Google at
top positions. Volumes are usually thin, so they belong in a presenter note rather than on the slide, but
they are a real sign that the two surfaces are converging.

## 3. The trust cluster: group for it, or you will miss it

Group the queries that pair the brand with doubt: `<brand> complaints`, `is <brand> legit`,
`<brand> reviews`, `how does <brand> make money`, `<brand> scam`. When this cluster carries real
impressions, it means people are actively checking whether the client can be trusted and landing on pages
that do not answer them.

This matters more in AEO than in SEO. These are exactly the questions people now ask an assistant instead
of a search box, and the assistant answers from whatever third-party material exists when the brand has
published nothing. **A trust cluster with impressions and no owned answer is the strongest argument for
the defend plays**, and it turns an abstract AEO pitch into a specific, urgent gap. Track those prompts and
lead the visibility section with them.

## 4. Also worth computing while you are in there

- **Branded vs non-branded, on clicks AND impressions.** They can diverge sharply. Report clicks, and
  handle the second number as `writing-and-voice.md` describes under "Pick the honest denominator".
- **CTR failure where the brand already ranks.** A query at position 1-3 with CTR far under expectation is
  a free win, usually a title or answer-format problem rather than a ranking one.
- **The daily series.** Do not stop at the Queries sheet; the Dates sheet holds the day-level history. Roll
  it up monthly and check year on year before quoting any trend.
- **Third-party names appearing beside the brand:** partners, resellers, plans, integrations. That is the
  off-site map for `citation-sources-and-offsite.md`, drawn from data rather than guessed.

## 5. Sibling skills that do this faster

- **`gsc-url-queries`**: URL-level Search Console queries. Use it when the question is "what does this
  specific page already get asked", which is the right input for prompt-to-page mapping.
- **`bing-wmt-ai-queries`**: the AI grounding queries that cited a page, from Bing Webmaster Tools' AI
  Performance report, with citation counts. It is the only source that tells you what an assistant
  actually asked before citing the site. Pull it whenever the property is verified in Bing Webmaster
  Tools; it is the best single complement to tracked prompts.

## 6. Boundary

First-party Search Console and analytics data come from the client's own property: use your own Search
Console / GA4 connector or an export the client shares. Do not spend turns looking for a third-party tool
that serves it.
