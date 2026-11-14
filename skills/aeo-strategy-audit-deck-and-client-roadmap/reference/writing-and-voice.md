# Writing and voice: client-facing AEO decks and reports

Contents: The one test · Banned: em dashes · Banned: the "not X, it is Y" cadence · Banned stock vocabulary · Banned: tool and platform names in client copy · Other tells to strip · The relevance test: does this change a decision? · Never address the reviewer through the deck · Presenter notes are where internal material lives · Pick the honest denominator, then pre-empt the challenge · Headline tense carries the argument · Proportion and themes · Recommendations · Ground content claims in the live page · Data-availability problems go to the reviewer in chat, not into the deck · Tone about the client's own business · QC sweep before every handoff

These are the rules that get work sent back when broken. The deck goes straight to the client, so write
it that way. Run the QC sweep at the bottom before every handoff.

## The one test

Could this sentence have been written WITHOUT opening the site or pulling the data? If yes, it is not
done. Every figure needs the reason behind it, tied to revenue, visibility, authority or a decision. Do not
restate data as sentences. Interpret; do not describe.

## Banned: em dashes

Zero em dashes anywhere: headings, table cells, footnotes, parentheticals. A hyphen in a compound word is
fine. A spaced dash used as a sentence break is not. Use a colon or split the sentence.

## Banned: the "not X, it is Y" cadence

No "X rather than Y", no "not just X but Y", no "this is a traffic problem, not a ranking problem". This
comparative construction is the most recognisable machine-writing tell. Rewrite as plain statements. After
drafting, reread every line for it.

## Banned stock vocabulary

delve, seamless, game-changer, utilize, robust, unlock, holistic, elevate, leverage, supercharge,
furthermore, moreover, it is worth noting, in today's landscape, navigate the complexities, cutting-edge,
best-in-class, synergy, empower. Keep a per-client list too: whenever a client flags a word, add it and
sweep for it on every later deliverable.

## Banned: tool and platform names in client copy

No analytics, search-console, crawler, keyword-tool, audience-tool, CMS or prompt-tracker product names in
the body. Describe them instead: the crawl, the site audit, AI-visibility tracking, the dashboard, the
audience data. Attribution goes only in a small source line or the presenter notes.

## Other tells to strip

No clause-splicing semicolons. No adverb sentence openers. No over-bolding. No flowery, grand or
over-polished language. If a claim is not backed by a number you pulled, cut it or soften it.

## The relevance test: does this change a decision?

Every slide states a decision, an action, or an input to one. Something can be true, interesting and
useless at the same time, and that is the hardest kind to cut because the research behind it was real. A
reviewer who cannot see how a slide is useful is right more often than not. Cut it, or demote it to a
presenter note framed as an ask. Insight that does not change what anyone does is trivia, and trivia in a
client deck costs credibility.

The rescue move, when the underlying material is good: reframe it from an observation into a decision the
client has to make. Material that fails as "here is an interesting pattern" often survives as "here is a
scope question only you can settle".

## Never address the reviewer through the deck

The deck is not the conversation. No meta-commentary on how the deliverable is categorised, no second
person aimed at whoever commissioned the work ("as you asked..."), no narrative drama, no working notes on
the slide face. Mechanics, method caveats and what to chase go to the reviewer in
chat or into the presenter notes.

The test before any slide ships: would this sentence survive being read aloud, verbatim, to the client's
CMO?

## Presenter notes are where internal material lives

Internal content does not have to be deleted; it has to be **moved**. Put every mechanic, caveat, source
note, "say this out loud" line and pre-empted objection into the slide's notes. In a long deck, most
slides should carry notes; that is what lets the slide face stay clean without losing anything. A slide
with nothing in its notes usually means something internal is still on its face.

## Pick the honest denominator, then pre-empt the challenge

Where two defensible numbers exist, show the honest one and arm the presenter with why it is not the
other. A brand vs non-brand split measured on clicks can look far more brand-heavy than the same split
measured on impressions, because non-brand terms surface on deep result pages where nobody clicks.
Traffic means clicks, so the click split is the one to show, and the note should explain the impressions
figure before a sharp client asks.

## Headline tense carries the argument

Present tense keeps a finding live and actionable; past tense implies it is already handled. When a
reviewer offers both framings of a finding, take the one that keeps it open, and record the nuance in the
note so it is not lost.

## Proportion and themes

Moves under about 3% are essentially flat; frame them that way. Report search by query theme or cluster,
never as a raw keyword list.

## Recommendations

Overarching guidance, not prescriptive do-X-on-page-Y directives (those live in the workbooks). Never
forceful or scolding (no "still not done after N months"). State the opportunity plainly. Tie each to a
real, verified page, search result or finding.

## Ground content claims in the live page

Before you say a page is commodity, missing a term, or needs a change: OPEN THE PAGE (scrape or browser).
For local or contextual needs, the fix is usually making sure the engine can pull context from existing
copy, not keyword stuffing.

## Data-availability problems go to the reviewer in chat, not into the deck

If a tool or data source is unavailable, raise it with the reviewer in chat and follow up. Never write "X
was not available this pass" into a client-ready deck. If uncertainty must appear, label it plainly as
needing client confirmation and state what was observed, the likely causes and the next action.

## Tone about the client's own business

Never write anything that reads as insulting the client's site. Instead of a dismissive line about the
revenue pages being empty, write the neutral, constructive fact ("the revenue pages have no structured
markup yet"). Read every line as if the client's CMO is reading it about their own company.

## QC sweep before every handoff

Run these passes on the rendered deck:
1. Em-dash sweep.
2. "Rather than" / "not just X but Y" sweep.
3. Stock-vocabulary sweep (the list above plus the client's own list).
4. Tool names in body copy.
5. Grounding: every number has a source; every claim ties to a real page.
6. Layout: nothing clipped or overflowing.
7. Address every reviewer comment one by one; do not regenerate and relabel.
8. A required pre-ship search of the rendered deck for: pending, not available, not assessed, not checked,
   this pass, scoped into, blocked, TBD, "requires ... pull", and every internal tool name you used. Any
   hit means the deck is NOT client-ready. Pull the real data (read the review or analyst site in the
   browser if the API is missing) or raise the gap with the reviewer in chat, then remove the line. A
   client deck ships with real data only, never a placeholder.

`data/verify_deck.py` automates the placeholder and incomplete-status part of pass 8; pass it your tool
names with `--ban` so it catches those too.
