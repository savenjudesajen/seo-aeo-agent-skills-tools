# Data traps: when a volume belongs to someone else

A keyword-tool volume is a **hypothesis, not a finding**. Before targeting a high-volume term, confirm by reading the
live SERP that its intent and category match the client's service. Open this before writing any demand verdict and
again before a cut list ships: traps can account for a large share of a sized universe, and that share is itself a
finding.

The decisions traps produce are a closed list (`gates.md` section 4): **Excluded**, **Not a target**, **kept but
FLAGGED**, **one exemplar kept** (programmatic sets). Every trap stays VISIBLE on its own tab with the SERP evidence and
the decision, never silently dropped.

The families run 5a, 5b, 5e, 5c, 5d in this file: 5e sits after 5b because prompt-shaped strings are stripped in the
same pass as the programmatic ones.

Examples are invented, for **ClientJ** (a bicycle-repair chain with workshops, mobile vans and fleet contracts),
**ClientN** (a ceramics studio) and **ClientV** (an online botanical-print shop). Figures are illustrative.

## The basic shape

- For ClientJ, `chain repair` carries a big number, and its top 10 is jewellery menders and chainsaw sharpening:
  another trade's word. **Excluded**.
- `bike tools kit` is riders kitting out a home workbench to do the job themselves; ClientJ sells the job, not the
  kit. **Not a target**.
- `bicycle mechanic` mixes riders looking for one with people looking to become one (apprenticeships, wages, job
  boards share the SERP). Adjacent: **kept but FLAGGED**, never counted as exact-match demand.
- **Tool conflation**: a volume tool can return a huge number for a phrase by merging it with a near-identical phrase
  from another field (for example a phrase that is also a product name in another field). Store suspect numbers as text and verify on
  the SERP.

## 5a. Homonym traps: the same word, several markets

Examples for ClientN:
- **throwing**: on the wheel is ours; javelin coaching and party planning ("throwing a hen do") are not.
- **glaze**: ceramic glaze recipes are ours; doughnut icing and double-glazed windows take most of the volume.
- **firing**: a kiln firing service is ours; "fired from my job" and shooting ranges are not.
- A short stem that matches inside a longer word (`class` inside `classic`) is a trap and a lead at once: cut the rows
  from the other word, then read them for a cluster worth its own regex (`classic tea bowl shapes` and other
  form-reference questions can be in scope).

Run every ambiguous head term through the expansion tool and read the fallback suggestions: if the fallbacks come from
another field, the volume you are looking at belongs to that field.

## 5b. Templated or programmatic clusters: one entity's footprint posing as demand

Detect them mechanically: group keywords by their leading 5-gram; any group with 5 or more members is a programmatic page
set, not organic demand. Keep ONE exemplar on the sheet with the set size on its row and cut the rest as one block on the
Exclusions tab. A free-image library that publishes one templated page per plant (`<plant name> vintage illustration free download`)
can otherwise become the single largest "theme" at the top of the list. The collapse is the cleanup; the **observation** is
the finding for the competitive notes (a third party is capturing a query family with programmatic pages).

Also strip: URL-encoding artefacts (`framed%20fern%20print`), doubled words, competitor domains embedded in the phrase,
and named-competitor brand terms (flag those as a separate decision; do not silently target them).

## 5e. Prompt-shaped strings: the newest family, and growing

Keyword tools now index strings typed into an AI assistant rather than into Google. Examples (invented): `where to
find an e-bike mechanic who comes to the office`, `trusted shop for hydraulic brake bleeds`, `can we get our delivery
bikes serviced overnight`, `which repair chain covers cargo bikes for nurseries`. The tells: a leading verb phrase (where to find,
which, who offers, when should we), an evaluative adjective buyers rarely type (recommended, trusted, leading, most
effective), first person plural, a trailing "for <application>".

**These are not a cut. They are a lead, and Phase 2 is where they pay.** As keyword rows they inflate a page's apparent
demand and read as padding, so they leave the keyword sheet. They do not leave the engagement. Carry each into Phase 2 as
a named input and work it harder than an ordinary seed:

1. **Run each as a question-tool seed in its own right** (mid-specificity trade phrasings cache and return buyer-level
   questions).
2. **Test the phrasing's SERP before tracking it.** A SERP about a different industry is proof the wording is wrong.
3. **Tier them honestly when they survive**: tier 1b at best, never tier 1. A keyword tool showing the string is evidence
   of measured demand, not evidence a person typed it at an assistant. Report them on their own line in the grounding
   count.
4. **Read the family as a finding**: that this vocabulary is indexed at all is the first place the shift from typed
   queries to asked questions shows up in a paid tool.

Never drop one silently. A prompt-shaped string that goes nowhere still gets a row saying which of the four steps it
failed.

## 5c. When Search Console and the keyword tool disagree, Search Console wins for AEO

For an emerging category the keyword index lags and Search Console is ground truth. Example (invented): the tool
puts `kiln firing service` at close to zero, while ClientN's Search Console logs four-figure impressions for the
question form `where can i fire pottery if i dont own a kiln`. Rule: **Search Console impressions decide AEO targeting; the
keyword tool's volume decides SEO prioritisation.** Report both side by side and never let a tool zero delete a term
Search Console proves is asked. (Shape comes first: impressions decide targeting only among rows that pass the shape gate
in `seed-chain.md` C6.)

## 5d. Entity, direction and audience traps

5a catches a word that means something else. These three catch keywords where the WORDS are right and the demand still
belongs to someone else, which is why they survive a read of the string and die only on the SERP. Confirm each by
opening the live SERP; never infer it.

- **ENTITY trap: a named company or product owns the phrase.** A generic-sounding phrase that is also the name of a
  well-known consumer app, holding the Wikipedia result and most of the top 10, is not demand for the service. The tell
  is a brand, a Wikipedia entry or a set of location pages in the top 10. A trap verdict is re-run when the client's own
  brief names the term as a product it sells: the brief's word overrides the trap, with the reason on the row
  (`seed-chain.md` C6-coverage).
- **DIRECTION trap: right topic, opposite side of the transaction.** For ClientV, `custom botanical prints` ranks
  print-on-demand services where illustrators upload their own artwork to sell: the searchers make the item, they do
  not want to buy one. A shopper choosing a framed plant print for a gift shows up at the far smaller
  `botanical print gift`. High volume pointing exactly backwards is the most seductive version, because the string
  reads as a perfect match.
- **AUDIENCE trap: a real share of the volume is your competitors, not your buyers.** For ClientN, `pottery
  instructor` brings up teaching-certificate courses and instructor job listings: much of the number is potters who
  want to teach classes, the studio's own supply side, not adults looking to take one. Keep it if it fits the line,
  but discount it and say why.

Keep every trap visible on its own tab with the SERP evidence and the decision. "N% of this universe was unusable" is
itself a finding.
