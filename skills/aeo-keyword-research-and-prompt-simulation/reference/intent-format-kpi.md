# Answer type, page check and KPI: what a prompt can win, and what its page must supply

Open this at B2 (tagging the tracked rows), at B2-format (the page check), and before the KPI split of a set is
stated. The same labelling runs on keywords at A7, where it proposes the page each keyword needs.

## 1. Why this file exists

Two decisions made per prompt drive everything downstream: **what the answer has to contain** (which decides whether an
engine will name a provider at all, and so which KPI the row can move) and **whether the page it sits on can supply that
answer** (which decides whether the page can be cited or mentioned for it). Both are hand decisions, and both are
columns on the Prompt Map so the verifier can hold them. A label that lives only in a sentence never reaches the
deliverable.

## 2. Two labels on every prompt: the need and the answer type

**The need** follows the user-intent categories in Google's public Search Quality Rater Guidelines: **Know** (the asker
wants information), **Do** (the asker wants to accomplish something), **Website** (the asker wants a specific site or
page) and **Visit** (the asker wants a physical place). It is the coarse label, kept so a set can be read against the
same categories search quality work already uses.

**The answer type** splits the need by what the answer must contain. Nine values, one primary per row, an optional
secondary. Solutions and Shortlist follow the public problem-aware and solution-aware stages of the copywriting
awareness ladder: the first asker knows the problem, the second already knows the kind of answer.

| Need | Answer type | The answer has to contain |
|---|---|---|
| Website / Visit | **Destination** | the specific site, account, page or place the asker names or is trying to reach |
| Do | **Transact** | a path to complete an action now: buy, sign up, book, request a quote, download |
| Know | **Contrast** | two or more named options set against each other |
| Know | **Specifics** | a checkable fact about a named provider or product: what it costs, covers, works with, or has done |
| Know | **Shortlist** | providers in a category the asker names (or replacements for a provider the asker names), listed, ranked or filtered |
| Know | **Solutions** | named products, services or providers that solve a problem or reach a goal the asker states without naming a category or provider |
| Do | **Steps** | a procedure the asker carries out themselves |
| Know | **Fit** | a judgement for the asker's situation: whether or when it applies, whether it is worth it, its risks, trade-offs or common mistakes |
| Know | **Concept** | an explanation: what something is, how it works, why it matters |

The table reads in the order the questions in section 3 decide.

**Provider-naming types** are Destination, Transact, Contrast, Specifics, Shortlist and Solutions: an answer to them
names somebody, and their KPI default is Mention. **Explaining types** are Steps, Fit and Concept: an answer to them
usually names nobody, and their KPI default is Citation. Evidence mention (section 4) is a KPI, not an answer type.

## 3. Deciding the answer type

Read the prompt for what a useful answer must contain, not for its opening words. Three questions, in this order:

1. **Does the asker want to go somewhere or complete something right now?** A named site, login, official page,
   opening hours or a place near them is **Destination**; a purchase, sign-up, booking, quote or download is
   **Transact**.
2. **Is the answer useless unless it names providers or products?** If yes: two or more options named in the prompt
   is **Contrast**; a fact about what a provider charges, includes, supports or has proven is **Specifics**; the
   category or a provider to replace is named (who offers it, which are good, what replaces a named one) is
   **Shortlist**; otherwise (a problem or goal, no category or provider named) is **Solutions**.
3. **If the answer can be useful naming nobody:** the asker will carry out a procedure (**Steps**); the asker is
   deciding whether, when or how much (**Fit**); otherwise the asker wants to understand (**Concept**).

A script may propose a first label from the obvious tokens each question looks for: a site or place the asker names
(question 1), a verb that completes a purchase or booking (question 1), two named options joined by "vs" or "or"
(question 2), a plural provider noun such as "workshops", "studios" or "framers" (question 2; a named category points to Shortlist), "how do I" or "how to"
(question 3). Everything else is read by hand. The proposal never decides the label.

Where a first reading goes wrong, the three questions settle it:
- **A brand name that is also an ordinary word.** "Does Kickstand take carbon frames?" (Kickstand being an invented repair
  chain) reads like a parts-fit question about a bike stand; the asker wants a fact about a named provider checked, so it is
  Specifics, not Concept. Check the name against the client's competitor list before labelling.
- **A "fastest way" phrasing that only providers can answer.** "Buckled rear wheel, race on Saturday, fastest fix?"
  looks like a request for a procedure, but a useful answer names shops with same-day wheel service and their turnaround,
  and the asker names a problem, not a category: Solutions, not Steps.
- **An "or" between two methods, not two providers.** "Should a hotel breakfast set be wheel-thrown or slip-cast?" sets
  two making methods against each other and names nobody: Fit, not Contrast. Contrast needs named options.

**The label is the decision; the script transcribes it.** Every row carries its reason.

**Mixed prompts.** Record a primary and, where it helps, a secondary ("which framers seal a pressed wedding bouquet
behind UV glass, and what do they charge?" names the category and asks a price fact about the providers, so it is
Shortlist with Specifics secondary, written `Shortlist / Specifics` in the cell: space, slash, space, primary first). The page is built and judged against the primary.

**On keywords (A7).** Run the same three questions on each keyword. A keyword whose answer must name providers needs a
page that can be named (a service, product or list page); one whose answer names nobody needs a page that can be
cited (a guide or glossary entry). The SERP still decides whether such a page of the client's own can win
(`keyword-research.md` A7-placement).

## 4. The KPI a prompt can move

The KPI follows **what the answer will name**, not the topic and not the funnel stage:

- **Mention**: the answer is expected to name providers or products. Provider-naming types are Mention rows by default.
  The question for the set is whether the client is named, how it is described, and who is named beside it.
- **Citation**: the answer explains and names nobody, so the realistic win is the client's page being a source the
  answer rests on. Explaining types are Citation rows by default.
- **Evidence mention**: an explaining row (Concept, Fit or Steps) whose prompt asks for proof or real examples the
  client holds first-hand ("what does handmade stoneware actually look like on a hotel breakfast table? show me real
  examples", Concept, for a studio whose hotel commissions are published). The client is named as evidence, not as a
  recommendation.

Three refinements:
- **A list prompt is not automatically a Mention row.** "Which winter habits stop a road bike's chain from rusting?"
  lists habits, not vendors, so the three questions (section 3) decide it: the answer names nobody and the asker carries
  the habits out, so it is Steps, KPI Citation. The list shape belongs in the page check and `Page must carry` ("a list
  of habits, each with its reason"), not in the answer type.
- **A tools list is a Mention row only if the client is a tool.** For a repair chain, a request for the kit a home
  mechanic needs to bleed hydraulic brakes is Citation unless the chain sells a kit of its own; the reason says so, and answers the hand-read finding the verifier
  prints for a row whose KPI is not its answer type's default.
- **Criteria prompts** ("how can I tell if a mechanic really knows e-bike motors?") are Citation: the answer is a
  checklist, and a name in it is upside.

**With the four gates.** G4 (worth winning) fails an answer that names nobody on a page that sells. On a guide or
glossary entry the same explaining row is a Citation row and passes when the page can be the source. A strong set mixes
answer types on purpose; each row is read against its own KPI, and **the KPI split is stated in the deliverable** so a
mostly-citation set is never read against mention rate.

## 5. The page check

**Page types, as the gates read them.** A **selling page** is a Service Page or Product Page. A **list page** is a Listicle; a Listicle is not a selling page. A **guide** is a Guide or Research
Post. A **glossary** is a Glossary entry.

Each page has a SERP-derived content type and a primary answer type: the most common primary type among its tracked
rows (on a tie, the tied type that appears first in the page's tracked rows). The page check is one value per page, judged against that
primary type. The check asks one thing: **can this page supply what the answer needs, in the form an engine lifts?** Four outcomes:

- **match**: the page can supply that answer as it stands.
- **partial**: one added section makes it answerable. A list page carrying an explaining row needs a short explainer
  above the list; a guide carrying a provider-cost row needs the client's own range stated.
- **mention route**: a selling page whose primary type is Solutions, Shortlist or Contrast (Contrast on a Service Page
  only): rows it will not be cited for. The list an engine cites
  will be someone else's (reached by placement), so the page's work is to make the client's mention likely and
  accurate: what it is, who it is for, proof, price. For those rows this is the normal outcome, provided they stay
  Mention rows.
- **MISMATCH**: a selling page carrying explaining rows (on a kiln-firing service page: "why does glaze crawl off a pot
  in the kiln?", "what should I check on a piece before it goes in for a bisque firing?"), or a Contrast row on a
  Product Page (one product cannot be its own side-by-side). Engines take explanations from pages built to explain:
  restructure the page so the explanation leads and the offer follows it, or record on the page row that it tracks
  nothing citable.

**Default page check by primary answer type and page type** (the verifier compares the page's check with its primary
type's default; any other value is allowed with a reason on the rows and prints one hand-read finding for the page,
never a silent pass). The check is read only from the trailing `(<check>)` of the cell, never from words elsewhere in
it. Destination has no scripted default: every page whose primary type is Destination prints a hand-read finding to
confirm it is the destination the prompt names (then match; otherwise partial):

| Answer type | List page | Guide | Glossary | Selling page |
|---|---|---|---|---|
| Concept, Fit, Steps | partial | match | match | MISMATCH |
| Solutions | match | match | partial | mention route |
| Shortlist | match | partial | partial | mention route |
| Contrast | match | partial | partial | mention route on a Service Page; MISMATCH on a Product Page |
| Specifics | partial | partial | partial | match (facts about the client itself) |
| Transact | partial | partial | partial | match |
| Destination | match only when the row's page is the destination itself; otherwise partial | | | |

Record the check as `<answer shape> (<check>)` in the `Answer shape and page check` column, repeated on every tracked row
of the page (a PAGE row, where the sheet has one, may carry it too; the scripts read it from the tracked rows), where the answer shape is what the engine has to lift:
an explanation, a judgement, ordered steps, providers or products that solve the stated problem, named options with the criteria that separate them, a side-by-side,
checkable facts, an action path, or the destination itself. The page summary of a set states how many pages land in
each check.

**What the page owes.** The `Page must carry` cell on every row says what the page needs for that row to be winnable:
for an explaining row, the answer in plain words near the top of the section that carries it; for a list or contrast
row, the options with the same few attributes for each; for a Solutions row, the stated problem with the ways to solve
it and who offers each; for a Specifics row, the fact itself, stated and dated. The
brief is built from these cells and the fan-out blocks. Write it from what the answer needs; markup and schema are a
separate audit and never stand in for the content.

## 6. Phrasing versus noise

- **Reruns move answers more than wording does.** The same prompt asked twice repeats only part of its cited sources,
  so most of the variation people put down to wording is the model's own randomness.
- **Never track spelling or abbreviation variants of one prompt.** They measure the same thing twice.
- **The exception is an ambiguous shorthand** (a short form with two plausible meanings in the category). When one is
  judged ambiguous, every row spells it out, and each head page carries exactly one short-form row beside its
  spelled-out twin, with the reason on the row. That pair is the only variant tracked twice. One obvious expansion,
  one row.
- **A stable number comes from sampling.** A visibility read aggregates several runs of each prompt (a daily tracker
  does this); a one-off baseline is one sample and is labelled single-run / directional.
- **Fan-out strings vary most of all.** A fan-out block covers the retrieval nouns the engine reaches for, not exact
  strings. Call a string observed (`O-ui`) only after it has appeared in three or more runs and only when it is used
  verbatim at 10 words or fewer; a trimmed engine string is `S-compress`.

## 7. Where the labels live, so they bind

- **Prompt Map**: `Answer type (primary / secondary)`, `Need`, `KPI this prompt can move`, `Why that KPI`, and the
  page-level `Answer shape and page check`.
- **Delta** (second pass): a page-check column (answer shape | check | what the page must add) and the KPI split per
  row.
- **The content plan's page notes** (whatever field the writers read): one segment each for the page check, the KPI
  split and what the page owes, so the writer and the tracker read the same thing.
- **The verifier** (`data/verify_tracked_set.py`, checks 10 and 11): every row carries one of the nine answer types and
  one of the three KPIs; a missing column (including Cluster or Topic, which the OWN budget needs) or an unknown answer type fails the
  build; a page whose page check differs
  across its tracked rows fails; two rows that are one prompt with an abbreviation expanded fail unless the reason
  says the shorthand is ambiguous. It prints these for the hand read: a Concept row on a selling page; a citation row
  on a MISMATCH page; a row whose KPI is not its answer type's default (section 2; Evidence mention on an explaining
  row is allowed silently); a page whose check is not its primary type's default (one finding per page, section 5);
  every page whose primary type is Destination, to confirm. The answer type cell is `Primary` or `Primary / Secondary`;
  the primary is the text before ` / `.
- **The tracked-set file** saved as next run's `--tracked` file carries the answer type, need and KPI, so the platform
  load can tag by them.

## 8. Labelling precedents (so the next set is labelled the same way)

A precedent is a default, not a veto: when a row departs from it, the reason goes on the row.

- **Qualified provider lists are Shortlist, Mention, Decision**, whatever the qualifier (an industry, a team size, a
  budget band or a proof requirement: "for a courier fleet of about 30 cargo bikes, who does servicing on site?").
- **Replacing a named provider** ("alternatives to CompetitorA") is Shortlist, Mention, Decision: one option is
  named, so there is no Contrast. **Replacing an approach** ("who could look after my bike so I don't have to fix it every weekend?") is
  Solutions, Mention, Consideration: the answer must name providers, and the asker names no category.
- **What a provider costs or includes** is Specifics, Mention, Decision. A generic budget benchmark ("roughly how much
  should a full e-bike service set me back?") or a choice between payment models (a yearly service plan against paying
  per visit) is Fit, Citation, Consideration.
- **How a service is measured or how long it takes** ("is a week normal for a hand-built wheel?") is Fit or Concept,
  Citation. On the service page that owns the keyword the default check is MISMATCH; if the page carries a
  what-to-expect section, record partial with the reason on the rows (the verifier prints the off-default finding),
  or rewrite the row provider-shaped, or place it on the guide. When the asker learns
  to do the measuring themselves, it is Steps, Awareness.
- **OWN rows** ("Besides framed prints, what does ClientV make?") are Specifics, Mention, Decision: the asker wants a
  fact about one named provider (a secondary only where a second named option is present). The metric is whether the offer is described accurately; the set line says how many Mention rows are OWN
  baselines so the split is not read as mention rate.
- **Process rows on a selling page (switching rows included) are written provider-shaped.** "How is a wedding bouquet
  pressed and framed?" is Concept (the asker wants to understand a process, not carry it out) and names nobody; "Which studios press and frame a bouquet sent to them by post?" names the
  category, so it is the Shortlist version a mention can be won on.
- **Ambiguous shorthand on a head page**: every row spells it out and the head page carries one short-form row, each
  with the keywords of its own form. An observed short-form query is the short-form row; do not construct a bare twin
  beside it. Abbreviations with one obvious expansion in context (DIY, UV, GPS, FAQ, ROI) are never tracked
  twice. Write the verdicts on the sheet so the reviewer can overrule one.
- **Guide pages carrying provider-cost rows** are kept when the guide is where the generic question is answered in
  full; the check is partial and the page note says to state the client's own range.
- **A Research Post** (a case study page is written as a Research Post) carrying an explaining prompt that asks for
  real examples is Concept or Fit with KPI Evidence mention; its default check is match.
- **Explaining rows on term pages** (a glossary or a set of definition pages) are Citation rows: the answers name no
  provider, so a term page can be the source and not the recommendation. Where many pages carry rows of the same kind,
  decide the label once per kind and apply it, with the reason written once on the set line.
