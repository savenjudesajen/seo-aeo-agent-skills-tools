# Grounding a prompt phrasing when the research tool is down

Prompt phrasings rest on something observed, never on invention. When the usual question-research path
is unavailable (a quota exhausted for the run, or every call failing auth), this substitute still
yields verbatim buyer questions with no invention.

## The substitute path

1. Run a SERP fetch on the QUESTION-FORM query rather than on the keyword.
2. Read the ranking URL SLUGS. Forum and Q&A slugs (Reddit, Quora) carry the asker's exact phrasing
   verbatim, which is the whole point of grounding.
3. Supplement by fetching vendor FAQ pages, which are written to mirror the questions buyers ask. Treat
   them as a hint about commercial angles, not as evidence of demand.

## Its limits, which belong on the row

- Forum comment bodies are often unreachable (site-blocked fetches, failing JSON endpoints); you may
  get titles only.
- Forums truncate long slugs. Flag a truncated title as truncated and never guess the missing words.
- Flag a blocked source in the deliverable instead of silently substituting for it, so the reviewer can
  see which grounding tier each prompt rests on.

## A SERP can disprove a phrasing

Test a phrasing's SERP before tracking it as a prompt. A SERP that returns a different subject is
tool-grounded proof the phrasing is wrong, not a weak-demand result. For example, `best shot timing`
might return sports coaching and photography pages with no coffee intent, while `espresso shot time`
and `how long to pull an espresso shot` carry the real intent. Record the disproof as a finding: it
tells the client which vocabulary their market does not use.
