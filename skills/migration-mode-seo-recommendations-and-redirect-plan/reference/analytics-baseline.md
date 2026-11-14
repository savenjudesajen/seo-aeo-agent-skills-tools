# Analytics baseline: Search Console and GA4, what to pull and what to do with it

Contents: 1. Search Console: ask for THREE exports, not one · 2. GA4: three reports, and one check that matters more than the rest · 3. The denominator rule: pick the honest one, then pre-empt the challenge · 4. Corroborate before you write · 5. What reaches a slide, and what doesn't

The legacy site's own data is the strongest evidence in the deck, because the client cannot argue with
it. Two sources, roughly half a day of work, and it either corroborates or kills the thesis before you
write a slide.

Access is the critical path. Request it in week 1, chase it every session, and **build the provisional
crawl-based version straight away** so the engagement isn't blocked. Use your own Search Console / GA4
connector or export.

---
## 1. Search Console: ask for THREE exports, not one

The Search Console UI export is filtered, so the filter you set is the dataset you get. Ask the client
(or pull yourself) for the same window (the full 16 months), three times:

| # | Filter | What it is for |
|---|---|---|
| 1 | **No filter** | totals, the brand split, the daily series |
| 2 | **Query does not contain the brand** (add each brand variant) | the non-brand tail on its own, not drowned by brand volume |
| 3 | **Custom regex: queries of 4+ words** | the prompt mine (§1a) |

Regex for the third: `^\s*(\S+\s+){3,}\S+\s*$` (four or more whitespace-separated tokens).

### 1a. The 4+ word export is a prompt mine
Long queries are people typing questions, not keywords. That set is the closest thing to a free, real,
client-specific prompt universe, and it feeds three things:
- **AEO prompt set:** seed the tracked prompts with language real users already used. That beats
  anything a generator invents, because it is evidenced demand for this brand.
- **Content ideas:** a 4+ word query with impressions and no clicks is a page that doesn't exist yet.
- **The trust cluster** (below).

You may find queries that read like AI-assistant prompts arriving through Google at top positions.
They are usually thin (single-digit impressions), so keep them off the client slide, but note them for
the presenter: it is a real signal.

### 1b. Each Search Console export is a multi-sheet workbook
Don't stop at the Queries sheet. The **Dates / Chart** sheet holds the **daily series**. Roll it up by
month and compare year over year. Long-term declines in clicks and a slow drift in average position
show up there and are invisible in the query table.

### 1c. What to compute

1. **Branded vs non-branded split, on clicks AND on impressions.** Record both for yourself even if
   only one goes on the slide (see §3, the denominator rule).
2. **The trust cluster.** Group queries that pair the brand with words like reviews, complaints,
   legit, scam, refund or cancel. These are people checking whether the client can be trusted, and
   they often land on pages that don't answer them. On any site where trust drives the purchase, this
   can be one of the largest content gaps, and you only see it if you group for it.
3. **CTR failure where you already rank.** Any query at positions 1–3 with CTR well under expectation
   is a free win. Typical causes are titles and descriptions that don't match the query's intent,
   truncated titles, or a missing rich result; the rebuild fixes them for free if the spec says so.
4. **Demand from other markets and languages.** Use the country filter and search the query set for
   other languages. Real impressions there turn "the regional versions are dead weight" into an open
   scope question rather than a deletion.
5. **Third-party names in the query data.** Queries pairing the brand with another company (a
   retailer, a marketplace, an integration) show which third parties people associate with the
   brand. They belong on the list of places that must update to the new name.
6. **Orphaned products.** Product-line or product names with impressions but no ranking page are scope
   questions for the client.
7. **The new name, if the rebrand has leaked.** Check whether NewBrand already draws impressions. It
   sets the AEO baseline honestly.

---
## 2. GA4: three reports, and one check that matters more than the rest

GA4 usually needs the UI or your connector; the last 28 days is enough for a baseline.

| Report | Pull | Why |
|---|---|---|
| **Traffic acquisition** | sessions by default channel group | the traffic-model classification |
| **Landing pages** | top ~30 with engagement time | **exposes URLs the crawler cannot see** |
| **Key events / conversions** | by channel and by landing page | §2a |

### 2a. Check whether conversion is instrumented AT ALL. Do this first.
If key events are zero across every channel and landing page, the migration's actual KPI
(orders, enquiries, bookings, sign-ups) is not recorded anywhere, and promising to "prove the migration
preserved conversions" is empty.

**Make instrumentation a pre-cutover prerequisite in the checklist, not a post-launch nicety.** It is
also a cheap credibility win: you found something the client's analytics setup missed.

### 2b. Landing pages expose what the crawler can't reach
The crawler stops at login walls, form submissions and unlinked pages; GA4 does not. Landing-page
reports regularly reveal logged-in areas, checkout or booking steps, campaign landing pages and
orphaned pages that are absent from the crawl. A crawl-only redirect map would drop them silently.

**Redirect map = crawl ∪ Search Console ∪ GA4 ∪ backlink targets. Never crawl alone.**

Where conversions aren't tracked, engagement time on those paths is the best available proxy for
whether people actually use them.

### 2c. Referral doesn't capture offline influence
A channel mix dominated by Direct, with a small Organic share and a near-zero Referral line, is the
signature of a brand-navigational site: people learn the name offline (packaging, events, sales
conversations, third-party listings) and **type** it. Don't conclude "third parties send no traffic"
from a tiny referral line. It needs UTMs on every link you control plus offline attribution.

---
## 3. The denominator rule: pick the honest one, then pre-empt the challenge

The brand split often differs sharply between clicks and impressions: near-total brand share on clicks,
a much lower brand share on impressions, because non-brand terms surface the site at positions 40+
where nobody clicks.

"Traffic" means clicks, so the click split is the honest figure. A sharp client will ask why it isn't
the impressions split. **Put the answer in the presenter note before they ask**: impressions without
clicks are not traffic. Where two defensible numbers exist, show the honest one and arm the presenter
with why it isn't the other.

---
## 4. Corroborate before you write

The point of doing crawl, Search Console, GA4 and AEO **before** drafting is to see whether they
converge. Write each source's reading in one line, side by side, and check that they support the
same conclusion:

| Source | Question it answers for the thesis |
|---|---|
| Crawl | does the site have pages that could rank for non-brand demand? |
| Search Console | what share of clicks and impressions is branded? |
| GA4 | which channels bring the visits that convert? |
| AEO | does the brand appear in AI answers for category questions, or only for its own name? |

**A finding that survives four unrelated instruments is very hard to push back on.** Collect all four
before drafting the narrative, not after.

---
## 5. What reaches a slide, and what doesn't

Surface **every** finding to the reviewer; gate what reaches a client slide by whether it serves this
deck's argument.

A long-term traffic decline can be real and important and still belong off a migration deck: it
invites a "why is your traffic falling" tangent the deck isn't for, and it needs a cross-check first.
Send it to the reviewer for a separate analytics conversation. That is sequencing, not suppression.

A good default: **one slide on the brand/non-brand split** (a pie carries it better than a table),
**one on the query-cluster opportunity**, everything else in the workbook and the notes.
