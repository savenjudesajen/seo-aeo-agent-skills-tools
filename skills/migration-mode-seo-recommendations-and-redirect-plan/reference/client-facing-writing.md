# Client-facing writing rules

The most common failure is not the analysis. It is writing the deck **to the reviewer** instead of
**to the client**, and then having to rewrite it wholesale.

## The rule
**The deck is not the conversation.** A slide may contain only what the client should read. Mechanics,
methodology caveats, why a placeholder exists, what to chase, what to say out loud: **presenter notes,
or a message to the reviewer. Never the slide.**

## Disqualifying on a client slide
- **Process talk about the deliverable itself:** "We've structured this as a spec because of where the
  build is." The client cares about the spec, not its genre.
- **Lines addressed to your reviewer or project lead:** "As discussed, hreflang is in scope." The
  audience in the room didn't have that discussion.
- **Dramatic framing:** "a ticking time bomb in the sitemap", "the hidden cost of doing nothing".
- **Internal to-dos:** "pull crawl again after dev pushes the fix", "confirm with the dev team".

## Register: a board-ready consulting deck
Declarative and unhurried. No rhetorical questions, no em-dash punchlines, no superlatives, no italics
for drama. **Severity is carried by placement and by the recommendation column, not by adjectives.** The
finding may be alarming; the prose is not.

| Default instinct | Target register |
|---|---|
| "Your redirects go round in circles before anyone lands anywhere" | "Legacy product URLs pass through up to three hops before resolving. Each should point directly to its final address on the new domain." |
| "Google has no idea which country page to show" | "The regional versions carry no hreflang annotations. The new build should publish a reciprocal hreflang set for each language and region pair." |
| "Half your catalogue is basically invisible" | "A group of product pages receives no internal links from category or navigation templates. The new templates should link to each of them." |
| "The product template is painfully slow" | "The product template's largest content element loads after the recommended threshold on mobile. The specification sets image sizing and script loading rules for the new template." |

## The test
**Would this sentence survive being read aloud, verbatim, to the client's CMO?**
If it explains your process, argues with your own framing, or addresses the reviewer, cut it.

## Supporting rules
1. **Placeholders: keep them and make them deliberate.** Never silently drop an item you can't measure
   yet; the placeholder is the reminder, and losing it loses the follow-up. But it must look like a
   field awaiting data (`[DATE]`, `N of M URLs mapped`, `[key events: yes/no]`), never an unfinished
   sentence explaining itself. Put the rationale in the presenter note: that the placeholder is
   intentional and what must happen before the meeting (fill it from the data, or remove that
   scorecard row for that session).
2. **Relevance test.** Every slide states a decision, an action, or an input to one. True but inert
   context gets cut or demoted to a note. Insight that isn't actionable is trivia, and trivia in a
   client deck costs credibility. An interesting observation often earns its slide only when reframed
   as a choice the client must make (for example, whether an old microsite is migrated, merged or
   retired).
3. **Choose the honest denominator, and pre-empt the challenge.** Where two defensible numbers exist
   (for example the brand split on clicks vs on impressions), show the honest one and arm the presenter
   with why it isn't the other, in the notes, before anyone asks.
4. **Headline tense carries the argument.** Present tense keeps a finding live and actionable; past
   tense implies it has been handled. If the client accepts either, take the one that keeps it live and
   record the nuance in the note.
5. **Surface every finding to the reviewer; gate what reaches a slide** by whether it serves this
   deck's argument.

## Where everything else goes
Presenter notes, generously. Expect most content slides to carry a note: the mechanics, the verbal
framing to use, what to chase, and the caveats that would be wrong on screen but essential in the room.
