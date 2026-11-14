# Scope: what the client actually sells, and what this engagement covers

Step 0, the category-split lens, scope-drift management and the product-fit gate. Read Step 0 before the first keyword
and the product-fit gate before scoring. One decides what may enter the set; the other throws out what should never have
been in it.

Examples use invented clients: **ClientV** (an online botanical-print shop), **ClientJ** (a bicycle-repair chain,
engaged for its e-bike servicing segment) and **ClientN** (a ceramics studio). Figures are illustrative.

## Step 0. Scope the product or service first (mandatory, before any keyword)

You cannot size demand for a thing you have not defined. A line name like "Platform" or "Managed Services" is a
container, not a scope. Build a **Scope Map** from the client's own surfaces and get it confirmed. Ship it as its own
tab.

**S1. The docs site is the fastest complete index.** Try `docs.<client domain>/llms.txt` (some docs platforms truncate
it: a capture that stops mid-URL is incomplete), then `/sitemap.md`, then `/llms-full.txt`. Many docs platforms serve
clean markdown when `.md` is appended to a page URL, and some answer questions on a page directly; use that to fill a
truncation gap instead of re-scraping blind.

**S1-fallback. No docs site? Walk the other first-party indexes, in order:** `help.` / `support.` / the help-centre
path; the blog's release-notes, changelog or product-updates category; app store listings; partner and integration
directories that list the product. Record each index in the Scope Map's Source column; an index that does not exist is
written as checked and absent, never skipped.

**S2. Find the launch post** ("introducing <line>", the product-updates category). It carries the capability list, the
workflow steps, any proprietary scored object and the timeline claim, none of which sit on the nav pages.

**S2-releases. Read the whole release-notes category as an inventory.** Product pages show what marketing leads with;
release notes show everything that shipped. Lines that exist only in release notes and partner posts are invisible from
the nav: ClientV's journal announces a licensing desk for stationery brands and a re-framing offer for past orders, and
neither has a product page. Page back to the first post, list every feature named in a title or H2, and fold them into lines.

**S3. Read the FAQ blocks, not the hero copy.** The delivery model (what is done for the client, by whom, how often)
often lives only in a launch-post or platform FAQ.

**S4. Harvest first-party evidence.** Reports and research posts give the statistics that later earn the
**Evidence mention** KPI. Record each stat verbatim with its number and source page; the briefs cite them.

**S5. Enumerate the integrations.** `/integrations/*` shows which platforms the product actually touches versus what the
pitch implies. Compare each listed partner with how the product is actually delivered: a partner that is not a delivery
channel changes the tier of the line that leans on it.

**S6. Reconcile PUBLIC scope against DELIVERED scope, then tier it.** Ask the reviewer what is delivered that the site
does not claim. **T1** = publicly supported, safe to build pages on. **T2** = needs messaging sign-off before a page
ships. T2 terms are still sized (the demand verdict is the finding); they never become a page target without sign-off.
Two sources feed T2, both needing sign-off: (a) delivered but unpublished (the reviewer names it); (b) published but
buried (only in release notes or a partner post, no product page). A page built on (b) carries the status `New (needs
messaging sign-off)`, with one line per item to the account team.

**S7. The two-vocabulary rule.** A product name, a marketing name and a buyer's word are three strings. Buyers type
`wedding bouquet preservation` and `press my wedding flowers`; ClientV's site calls the same service "ProductA" on the
order form and "forever florals" in its newsletters. Before naming any page, size all three, then check who writes the house word:
if it appears only in the client's and vendors' own copy and nowhere buyers write, buyers do not use it. Keep the
internal name internal; make the buyer's word the door.

## The category-split lens (run it on every emerging category)

Pull **Google Trends on the generic category terms** AND **volume and trend on the commercial vendor-selection terms**,
and compare direction. Divergence is the finding, and it is invisible if you run only one series: definitional terms
can flatten or fall while the terms that pick a provider climb. A single-series read of the definitional terms can hide
a commercial lane that is growing, so report both directions side by side.

Run the same contrast on the incumbent vocabulary of the adjacent legacy category. Do not build a lane on vocabulary
that is declining; compete on the contrast.

## Scope drift management (the engagement is a segment, not the whole category)

Most engagements cover a segment of the client's category. Research drifts outward on its own, because every lap of
the recirculation loop pulls in adjacent vocabulary and each adjacent term looks defensible alone.

**Write the boundary at Step 0 as one sentence:**
> This engagement is about **<segment>** within **<category>**. It is NOT about <category> as a whole, and it is NOT
> about <named adjacent segments>.

ClientJ example: *E-BIKE SERVICING is the subject, inside bicycle repair. Excluded: bicycle repair in general, bike
fitting, e-bike retail, and the courier-fleet contracts ClientJ runs as a separate line.*

**Run a drift check at the top of every lap**, before sizing anything:
- Re-read the boundary sentence.
- Mark each new cluster from the last lap **IN SEGMENT**, **DRIFT** or **ADJACENT-ASK**.
- Kill DRIFT clusters immediately: not sized, no pages, in the workbook only as a named exclusion with its reason.
- Take ADJACENT ones to the reviewer in one line each. They own the boundary.

**Mark scope per keyword where a group's buyer splits, and report the two totals apart.** When the same words serve two
buyers (`motor service` brings e-bike riders and also outboard-boat owners), mark the group ADJACENT-ASK and
override the in-segment keywords to IN SEGMENT on their own rows, with the reason. Give IN SEGMENT and ADJACENT-ASK
keyword counts and volumes as two figures; one blended total can present a market many times its real size.

**Worked drift (invented), four clusters, e-bike servicing segment:**

| Cluster | Verdict | Why |
|---|---|---|
| `ebike cuts out under load` / `e-bike battery check` | IN SEGMENT | one fault as riders describe it and one service as they name it; both are the segment's work |
| `e-bike conversion kit` | DRIFT | a part riders fit themselves; ClientJ fits nothing it does not service |
| `e-scooter puncture repair` | DRIFT | a different vehicle the workshops do not take in |
| `delivery bike fleet maintenance` | ADJACENT-ASK | ClientJ runs fleet contracts as another line; whether this engagement covers them is the reviewer's call |

Do not size a DRIFT cluster: every lap spent on it is a lap not spent on the segment.

**The tell: a cluster with great numbers that you are pleased to have found is the most likely to be drift.** A
high-volume, low-difficulty, high-CPC cluster outside the segment costs more than finding nothing, because it looks like
progress.

## 2c-fit. The product-fit gate (run the Scope Map as a filter, not a document)

The Scope Map is a qualification gate every cluster must pass before the shortlist. For each cluster: *does the client
actually deliver this?* If not, it is cut, however good its volume, difficulty and CPC. A gap export can surface a
cluster with textbook numbers (large combined volume, low difficulty, strong CPC) for a service the client does not sell
(for a repair chain, a cluster about buying and selling used e-bikes): worthless, and an easy way to build a list the reviewer
rejects on sight.

**Four passes:**
1. **Delivers / does not deliver.** Cut anything outside the confirmed service list, with the reason in the deliverable,
   so the reviewer sees the decision rather than wondering whether it was missed.
2. **Right noun, wrong noun.** A cluster can be right in shape and wrong in wording. ClientV sells fine-art **prints**, not
   **posters**: `botanical poster` carries the volume and leads to mass-market wall-decor sellers, so it is out; the
   print terms are pursued. When the
   client's category noun differs from the high-volume noun, pursue the client's noun and record the volume gap as a
   category-creation finding, not a reason to switch.
3. **Adjacent but not theirs.** Keep as Secondary only if the client could credibly answer the query today.
4. **Eligibility and liability: can the client serve this, and does it want to be found for it?** Delivering it and
   wanting to be found for it are different questions, and a regulated or restricted client fails the second on terms it
   passes the first on. Read the client's eligibility rules and compliance posture (FAQ, terms) before sizing a line,
   because this class is invisible in every volume tool. Two shapes (generic):
   - **Eligibility:** a theme the client's own terms rule out (a region it does not ship to, a customer type its terms
     exclude, a licence it does not hold) can carry large volume and soft difficulty and still be untrackable as an
     opportunity. Quote the rule from the client's terms on the Exclusions row.
   - **Liability:** terms that promise an outcome the client cannot or may not promise (a guaranteed result, a claim
     its regulator or its own policy forbids) have real demand and are wrong for the brand to be found for.
   Cut on eligibility or liability, say which of the two it was, and list it on the Exclusions tab like any other cut:
   the reviewer needs to see it was considered, not missed.

## Run the service-line test at page level too

The third relevance level (B3-scope in `prompt-universe.md`) runs over PAGES as well as prompts, and it is easier to
miss there because a page arrives with volume attached and volume reads as justification.

- **A page recovered for its volume is the page most likely to be out of scope.** Say so on the row and test it before
  scoring.
- **Approval or inclusion of a page is not scope clearance, in either direction.** A page from an earlier round, an
  earlier quarter or the client's own sheet has not been service-line tested by that fact. Test the page list when you
  test the prompts, with a verdict per page.

Cutting a page late is expensive: its keywords, prompts and score unwind, and because an opportunity score that is a
percentile within the set re-ranks every page, everything re-scores. That cost is the argument for testing the page
list before the keyword work, not after.

## Two provider nouns, one service: check the SERP before shipping two pages

A keyword set often hands you the same service under two provider nouns as separate groups (invented: `pottery
classes` and `ceramics workshop` for ClientN). Before building two pages, run both head terms, renumber to organic
position and count SHARED non-hub URLs in the top 10 (hubs are the encyclopedia, video and forum results that rank for
everything). At **2 or more** shared URLs they are one page (the same threshold the `prompt-to-page-serp-clustering`
skill uses). The test cuts both ways: groups that share nothing but a hub result are separate pages. Apply it to every
such pair in the set, not only the one that caught your eye.

**Pick the surviving noun on evidence**: the higher combined volume, the SERP more dominated by provider pages, and
the term with fewer competing meanings.

**Read the content type off those SERPs while you have them.** "Service Page" has to come from what ranks, not from a
page-type field inherited from an earlier quarter's clustering: inheriting a label looks identical to deriving it and is
not the same thing. Score each head term's top 10 rank-weighted by type (share of vendor service pages, share of
listicles). A family whose top 10 is mostly vendor service pages can be won by a page of the client's own; a mixed
family (a solid service share AND a solid listicle share) means the page is viable AND placement on the shortlists
matters.

## Slugs: a service page carries a provider noun

A page under a services path still needs the noun in its own slug (`/repairs/ebike-battery-checks` reads as a topic
page beside `/repairs/ebike-repair-shop`). Pick the noun from evidence: the page's own keywords and the convention
its closest siblings use. Where neither noun carries measured volume, say it is a naming call, not a demand call, and
name the tiebreak (for example the noun the client's own navigation already uses). A spelling variant is not
evidence for a noun.

**Ask the reviewer to confirm the service list before scoring.** "Which of these do you actually deliver?" costs a
minute and saves a rebuild.
