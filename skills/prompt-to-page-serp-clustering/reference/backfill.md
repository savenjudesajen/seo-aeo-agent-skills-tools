# Backfill: step 8c (the last step, and the one that gets skipped)

After the unified page universe exists, most of its pages typically carry one or two keywords, and pages
that exist only because a prompt landed there carry none. A page with one keyword is not a page, it is
a row. Backfill is what turns it into something a writer can brief.

Examples use the fictional espresso-equipment retailer from SKILL.md.

## Where the keywords come from: the pages that ALREADY RANK

Do NOT expand from the seed keyword with a generic idea tool. Two reasons:

1. **Idea tools go down and drift.** If one is unavailable, flag the blocked source; do not silently
   substitute another.
2. **Slug and title mining produces phrases that are not queries.** Candidates harvested from ranking
   URLs' slugs and sized in a volume tool mostly come back with zero volume. Title fragments read like
   keywords and are not.

The method that works: **read what the already-ranking pages rank for.** For each thin page, take the
top non-hub URLs from its own SERP (already fetched for clustering, so no new SERP calls) and run each
through a keyword tool's **organic keywords for a single URL** report (Semrush Organic Research in URL
mode, Ahrefs Organic keywords for a URL, or the equivalent API). Those keywords are anchored to a page
Google already decided is about this subject, so they cannot drift the way an idea-tool expansion does.

### If you read the report from the browser instead of an export or API

Exports and APIs avoid all of this. If you must parse the on-screen table:

- **Virtualised tables** often expose cell roles only on the header row, with data rows empty. Parse the
  page's visible text line by line instead.
- **Never index columns positionally from the left.** Optional columns (position, for instance) are
  sometimes absent, and a left-indexed parse silently reads traffic as volume. Anchor on a column that
  is always present and distinctive, usually the **URL line**, and read volume and KD at fixed offsets
  from it. Expand abbreviated numbers (`1.5K`).
- ⛔ **A URL rendered without its scheme** (`www.site.example/path`) tempts a naive domain regex, which
  also matches a decimal figure such as a traffic percentage (`12.34`). Every row after the first false
  match is misaligned by one and the output is plausible nonsense rather than an error. **Require an
  alphabetic TLD**: `^(https?:\/\/)?([a-z0-9-]+\.)+[a-z]{2,}(\/|$)`.
- **Anchor the loop on the header line and seed the first keyword from the line after it**, or row one
  is dropped and the whole table shifts.
- **Verify one KNOWN row against what you can see on screen before trusting the parse.** Both faults
  above produce a full, well-formed-looking result set.
- **Accumulate results in `localStorage`**, not a page variable (dies on navigation) and not
  `sessionStorage` (dies when the driver recycles the tab), and confirm the store's key count after
  every batch.
- **Download the accumulated JSON as a file** at the end (console output truncates) and confirm the file
  landed before closing the tab; downloads can take a few seconds to appear, so re-list once before
  concluding it failed. Re-running a harvest you already have is the expensive mistake.
- **Small batches with a settle wait.** Long batches time out and lose their tail SILENTLY: the calls
  that ran return normally. Check the stored-key count after every batch.
- ⛔ **Tables paginate (often at 100 rows) and a single-page parse truncates without saying so.** A source
  returning exactly the page size is the tell. Click through and append, de-duplicating on
  keyword + URL + volume, because the next page can repeat part of the previous one.
- ⚠ **The keyword slot can misalign even when volume and KD are right.** Screen for keywords that are
  numeric-only or a single letter, drop those rows, and report the count.

## ⛔ A ranking URL with NO keyword data is a finding, not a failure

In a young or niche category, many ranking URLs return nothing at all from the keyword index ("no data in
the top 100"). Re-check each at a longer wait to rule out a timeout. A genuine empty result means those
pages rank on Google today and the keyword index has not caught up. Read it as evidence and report it.

The consequence reaches the deliverable: **a page whose every ranking URL is unindexed cannot be
backfilled**. It stays on one keyword and the row says so in words. Do not go and find candidates
somewhere else to fill the gap: a generic idea tool is exactly what this step avoids, and a page with no
measurable demand is something the client needs to know.

Log the two empty states separately: "the index has nothing for this URL" versus "the tool looked and
found zero rows". They mean different things.

## How many: 2 to 10 per page, and zero is a valid answer

⛔ **Backfill is a top-up, not a harvest.** The target is **2 to 10 additional keywords** for a page that
has one or two. A page where nothing clears the tests below **gets nothing**; leaving it thin is correct
and better than padding it.

The usual first-cut failure: dozens of keywords kept on a single page because every row was individually
defensible and the volume looked good. A reviewer will reject that as a keyword dump, and they are
right. The re-cut from the same harvest keeps a fraction of the rows.

**Why the cap is not arbitrary.** Keyword rows are not free. Every row becomes a line in the writer's
brief and a seed for the prompt set. Dozens of rows on one page does not make the page bigger; it makes the
brief unreadable and propagates junk into the prompts derived from it. The damage is downstream and
invisible when you add the row.

## The tests every candidate must pass

Run them by hand on every candidate. Volume is a tie-breaker between rows that pass, never a reason to
pass one.

**1. SEED CONTAINMENT.** The keyword carries the page's core term or a direct variation: plural or
singular, `machine`/`maker`, `grinder`/`mill`, the spelled-out form of an acronym. Topical adjacency is
NOT containment. On an `espresso grinder` page this test throws out `coffee grinder`, usually the
biggest number in the candidate set, because dropping the `espresso` qualifier changes the buyer. A high
number that fails the test is the most dangerous row in the file, not the most valuable.

**2. DISTINCT FACET.** It adds an angle the page does not already hold. `cheap burr grinder` next to
`affordable burr grinder` next to `budget burr grinder` is one purchase written three ways; keep the one
that earns the slot. Same for definitional near-dupes: `what is a portafilter`, `whats a portafilter`,
`portafilter meaning` and `portafilter definition` are one intent in four spellings.

Name the seed explicitly per page in the deliverable, so the reviewer can check the test rather than
trust it.

**3. NOT ALREADY SOMEWHERE ELSE.** ⛔ Check the candidate against the WHOLE keyword sheet before you assign
it, not just the page you are filling. A candidate already carried by another page from an earlier
round looks right for the page in front of you, and the collision is invisible at the moment of
decision. No two pages may track the same row (8c-remap), so run the duplicate check as a gate before
the sheet is written. Resolve a clash by which page OWNS the term, not by which round found it first:

- the unqualified term goes to the unqualified page; a qualified page owns its qualified version;
- a bare product or service term belongs on the product or service page, not on a listicle;
- a page's own seed keyword stays on that page; it is the easiest one to misassign, because it arrives
  as a fresh candidate and looks new.

A collision is also a signal: two pages competing for one body of demand is a grain question for the
reviewer and belongs on both page rows.

## Relevance is still the whole job

The harvest is generous and most of it does not belong. Expect to reject the large majority of
candidates; a rejection rate below about 70% usually means the tests are not being applied.

## ⛔ The source-URL trap: check what the ranking URL's OWNER sells

The single biggest source of rubbish, invisible until you read the candidates. The URL ranks for your
subject; the **site** it sits on ranks for everything its owner sells. Four shapes:

- **Tool or manufacturer documentation.** A support page that ranks for your subject pulls in the
  owner's product support queries (`<brand> machine error code`, `<brand> app login`, `how to reset
  <brand> grinder`). Those searchers are troubleshooting one product, not shopping. Rows pairing the
  subject WITH that brand go too.
- **A broad retailer or service line.** A general kitchen retailer's category page ranks for every
  appliance it stocks, so a grinder page sourced from it pulls `stand mixer`, `toaster deals` and local
  store queries.
- **The head term instead of the page.** A narrow checklist page's URL can rank for the category head
  term, which is the pillar's demand, not the checklist's. Pulling it in makes a narrow page look like
  the hub.
- **Domain-name noise.** A vendor homepage ranks for whatever its domain string matches.

**Before writing a page's rule, look at the ranking URL's domain and ask what else that company
sells.** That one question predicts most of the drop pile.

## ⛔ The highest-volume candidate is the one most likely to be wrong

It holds on almost every page. The biggest number in a candidate set is usually the head term, an
adjacent category, or a word-sense collision, never the row you want. Illustrative rejects:

| candidate | why it is wrong |
|---|---|
| `coffee` | the category head term, not a grinder page's demand |
| `coffee grinder` | a different buyer from `espresso grinder` |
| `<brand> grinder manual` | product support, not shopping |
| `shot glasses` | word-sense collision with espresso "shots" |
| `crema` (skin-care sense) | a homonym from another industry |
| any adult or offensive string | substring match on an innocent word |

That last row is why backfill cannot be run by script: a substring match can put an offensive string
with real volume into a client file.

## ⚠ PROMPT-SHAPED STRINGS: they will grow

Keyword tools now return strings at real volume that read like something typed into an AI assistant
rather than into Google, for example `where to find best espresso machine for small kitchens`,
`recommended grinder for home baristas`, `which espresso machine is best for beginners on a budget`,
`when should we upgrade our office espresso machine`.

The tells: a leading verb phrase (where to find, which, when should we), an evaluative adjective a
searcher would not type (recommended, trusted, leading, most effective), first person plural, and a
"for <application>" tail.

**They leave the KEYWORD sheet. They do not leave the engagement.** As keyword rows they inflate a page's
apparent demand and read as padding. But they are the closest thing to observed prompt phrasing a
keyword tool produces, so they go into the prompt phase as a named input and get worked harder than an
ordinary seed: run each as its own question-research seed, SERP-test the phrasing, and tier it as
grounded-but-unverified rather than fully observed. The `aeo-keyword-research-and-prompt-simulation`
skill covers that phase.

Hand them over explicitly: record the family with its examples, say which page each came from, and
carry the list into the prompt phase rather than leaving it in the exclusions tab where it reads as
rubbish. An exclusion from the keyword set is not an exclusion from the research.

## Word-sense and operator traps

- **Search operators are not queries.** `inurl:forum espresso`, `site:reddit.com grinder`. Real strings
  with real volume, typed by researchers. Useless as page targets.
- **Acronym collisions.** A category acronym that also names an unrelated standard or product.
- **Same word, different discipline.** "Shot" (espresso, photography, sports, vaccines); "dosing"
  (coffee, medicine); "tamper" (coffee tool, tamper-evident packaging).
- **Unrelated how-tos.** Queries about doing something with a different product that shares your
  vocabulary.
- **Navigational rows.** Forum or subreddit names typed to go there, not to research.

The single worst shape: the page ranking for a cheap-product query belongs to a vendor selling cheap
everything, so its URL also ranks for broad bargain queries with far more volume than your whole
subject. That source can produce dozens of candidates and keep **zero**. A ranking URL is about your
subject; the vendor behind it usually sells more than your subject.

**Write one relevance rule per page, by hand, after reading its candidates, and a reason for each row
you keep.** A script may transcribe the decisions; it may not make them. Ship the rule, the kept rows
with their reasons (at 2–10 per page the full list fits) and what was thrown out and why: a reviewer
needs to see what you discarded to trust what you kept.

Traps to check for on any client:

- **Vendor-suite drift**: the ranking page sells more than the one product or service.
- **Adjacent-concept drift**: `espresso machine` pulls `drip coffee maker` and `pod machine`, which
  belong to different pages.
- **Word-sense drift**: see above.
- **Branded navigational**: the client's own URL pulls `<client> login` or `<client> order status`. Real
  volume, zero intent for the page.
- **Modifier restacking**: cheap/affordable/budget/premium/quality/professional, each in singular and
  plural. Many ways to say one purchase.
- **Segment and geo fanout**: `espresso machine for` offices, cafés, RVs, students, and a list of
  cities. One page cannot rank for all of them; keep only the qualifiers that match the real customer.
- **Tool-brand queries on a how-to page**: `<app> brew timer`. Those searchers want the tool.
- **Competitor-branded comparisons**: `RivalOne grinder review`. Someone else's branded demand.
- **Outright junk**: a foreign-language row, an indexed typo, a malformed query string with `+`
  separators, an offensive string. Indefensible in a client file, and a sign the cut ran by pattern.

## ⛔ The bandwidth rule: fold before you propose a page

There are TWO reasons to fold, and they are independent: retrieval and capacity.

### Leg 1: an AI engine retrieves by SUBJECT, not by keyword variant

The SEO rule was: if a keyword group has volume, give it a page, because Google matches a query to one
best URL and the tailored page wins the slot. That still holds on Google. It does not transfer to AI
retrieval:

- **The engine rewrites the question before it retrieves anything.** Grounding queries an engine
  issues are short, keyword-dense noun phrases with the persona and framing stripped, and mostly not
  questions. The page is never matched against the user's phrasing.
- **Many phrasings collapse into few subjects.** Grouped by topic, grounding queries concentrate in a
  handful of subjects that carry most citations; the variation is in the WORDING, not the subject.
- **Citations spread across many pages, and growth comes from breadth.** As citation volume rises, much
  of the growth tends to be MORE pages being cited rather than the same pages cited harder.
- **Google stays concentrated.** On the same site and queries, a few pages take most impressions; one
  page still wins the query.

If you have the data, check this on your own client before relying on it: Bing Webmaster Tools AI
grounding queries (see the `bing-wmt-ai-queries` skill) for query length, question share and topic
concentration, and daily cited-page counts against citation volume for breadth.

Put together: many phrasings, few subjects, many cited pages. A page built for a keyword VARIANT
(`espresso maker` beside `espresso machine`, `burr grinder` beside `burr mill`) buys no AI retrieval
surface, because the engine's query will not be that variant; it will be a compressed noun phrase about
the subject both pages share. What it does buy is a split: passages that could have made one page the
strongest candidate are divided across two weaker URLs.

⚠ **This is not an argument for folding everything.** Google still distinguishes: two head terms whose
SERPs share zero top-10 URLs are a real split, and both pages stay. What has changed is the THRESHOLD:

> Split when the head-term SERPs genuinely diverge AND the sub-topic has enough distinct substance to
> fill a page with passages of its own. Otherwise fold, and carry the variant as a section.

A variant that fails either half is a section, not a page. Say both halves on the row so the reviewer
sees which one decided it.

### Leg 2: capacity

A page map is a build order for a team with finite capacity, not an inventory of every keyword group.
Few teams will create hundreds of pages for small groups, and an approved list longer than the team
can build is a list that stalls. A map that ignores capacity does not get built.

So after the backfill, run a FOLD pass over the page list before anything is proposed.

**Fold a page when its demand does not support one.** The signals are low total volume, very few
keywords and few or no prompts, usually together. Segment pages at a few dozen to a few hundred
searches each are the classic case: a single shortlist page carries them as sections.

**Three conditions, all required:**

1. **A seed page has to exist.** Fold into the page that already owns the parent term. Where there is no
   seed page, the group either earns its own page or gets cut; folding it somewhere loosely related is
   worse than either.
2. **The keyword has to earn its place on the target.** Would a reader of the target page be served by
   that section? `espresso machine for small kitchens` folds into a compact-machines page; it would NOT
   fold into a coffee-bean subscription page just because both are thin.
3. **If you are sure the keyword has no value on the target, do not fold it.** Leave it as its own thin
   page with the reason written, or cut it. A fold that dilutes the target has moved the problem.

**Fold properly, the same way as a reviewer-directed fold:** retarget the absorbed page's keywords AND
prompts onto the survivor, zero the absorbed page's rollups, recompute the score, and put the absorbed
page on the exclusions tab with its reason. Nothing is deleted: a fold is reversible and that is the
point of preferring it to a cut.

**Record every fold on BOTH rows.** The survivor says what it absorbed and why; the absorbed page says
where it went. A reviewer who disagrees must be able to reverse it without re-deriving it.

⛔ **When a method rule changes, re-check maps already delivered under the old rule.** A rule is not
scoped to the map where it was adopted. List the earlier maps for the same client and say which of them
the new rule would change; a rule applied only going forward leaves the client holding a build order
nobody believes. Group the old map into families
by hand first: fold candidates are obvious within a family and invisible across the whole list.

**Where the call is genuinely arguable, flag it rather than acting.** A page thin on demand but doing a
distinct job in the funnel (a case-study page, a shortlist beside its product page) is a funnel
judgement, not a volume one. Mark it FOLD CANDIDATE, say what you would fold it into, and let the
reviewer decide.

## Then update the keyword sheet

Backfilled keywords go into the SAME keyword sheet as the original research, tagged `Backfill`, with a
Source naming the ranking URL they came from; never a second sheet. Rebuild the unified page universe's
counts and volumes **from the keyword sheet** rather than incrementing them, so the two cannot disagree.
Re-run the reconciliation gate: the unified map's keyword count must equal original research plus
backfill, and the volume must reconcile to the sum.
