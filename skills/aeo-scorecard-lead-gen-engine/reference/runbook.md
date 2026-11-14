# Runbook: one account, start to finish

Budget: about 1 to 2 hours for the first account, about 20 minutes once the generators are wired.

## 1. Positioning (5 min)
Read the homepage. Capture what they sell, who they serve, where they operate and how they name
themselves. Pull the title, H1 to H3, meta description and services list. Also capture, because they
matter later:
- **Brand-name variants** (e.g. "Acme", "Acme Group", "Acme Co."): variants fragment the entity
  in the engines' eyes.
- **Any second site** the brand runs (another domain or subdomain): it splits the entity too.

## 2. Generate buyer prompts (10 min)
Write 10 to 15 questions **from their own positioning**, in the buyer's words, for their market.
Cover: the generic category question, the region question, the most local one, each major service
line, and each niche they actually serve.

Rules:
- Generic category wins are the real test ("best [category] in [country]"). Branded wins
  ("[Company] reviews") are weak signal; don't count them as visibility.
- One very local prompt (their town or city) is a useful control: many small brands win only when
  the question names their location, and that contrast with the generic questions is often the
  clearest finding in the report.
- If the prompts feel wrong for the business, that's a finding: their site tells models the wrong
  story.

## 3. Map the site (5 min), before scoring
Get the URL inventory and folder structure from a sitemap or URL-discovery call, not a full crawl
(full crawls often time out). Look for:
- the real page count and content types (service pages, guides, blog, resources);
- funnel coverage;
- any split across domains or subdomains;
- content that engines can't use well (gated, image-only or document-only pages).

Skipping this produces a lazy diagnosis (see the gotchas in SKILL.md).

## 4. Probe the AI engines (15 min)
For each prompt, record whether the brand was named and **who was named instead**.
- Probe the brand and each competitor so you can build a real leaderboard. If your probe tool
  reports only whether one brand was named, run it once per brand.
- Note which engines answered. Some answer from memory with no sources; that's expected, not a bug.
  Never generalise one engine to all.
- Record the probe count (prompts × engines): the headline stat is "named in X of N." If an
  engine's probe fails (a deprecated model, a provider error), report the engines that ran and
  exclude the failures from the counts. Don't quietly average over a hole.

## 5. Layer SEO evidence (10 min)
- Organic footprint: keyword count and traffic estimate. This gives the strongest contrast: "ranks
  for N keywords in Google, appears in almost no AI answers."
- Authority and referring domains → off-site mentions pillar.
- On-page and schema on the homepage and top service pages → content structure, answer readiness,
  entity clarity.
- Freshness: last-modified dates, blog cadence.

## 6. Score, then write (20 min)
Score the 7 pillars per `scoring-rubric.md`. Then:
- **Pick the hook competitor:** the brand actually leading the leaderboard and recognisable enough to
  matter to the prospect. If those conflict, lead with the one that wins the highest-value query and
  say so.
- **Write the diagnosis as a causal chain, not a list:** what they have → why it isn't working →
  who's getting the answer → why it's fixable.
- **Write 3 plays**, ordered by impact, each mapped to the pillars it moves.

## 7. Quality gate, generate, write back
Run the quality gate in SKILL.md. Generate the assets and write the row to the master sheet
(`master-sheet-schema.md`). The row personalises the ad and the landing page; if it's wrong,
everything downstream is wrong.

## 8. Stand up continuous tracking
Load the account, its competitors and its prompts into a continuous prompt tracker (the client's
own, if they already use one) so scores re-run on a cadence and the "movement" story exists at the
next touch.
