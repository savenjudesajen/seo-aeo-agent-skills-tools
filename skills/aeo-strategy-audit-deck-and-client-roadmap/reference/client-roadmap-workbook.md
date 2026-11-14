# Client roadmap workbook

The roadmap is mostly mechanical: the thinking already happened in the deck. If the client or your team
has a roadmap template, use it: keep its structure and add the AEO items as their own workstreams.
Otherwise build the default below with openpyxl.

## Default workbook (when there is no template)

**1. Intake** - the first thing you need from the client; everything depends on it. One row per question:
Topic, Question, Answer, Who answers. Topics: goals and what a win looks like; products and the priority
product; buyers and personas; competitors (prefill your derived set for confirmation); data assets the
client owns (studies, benchmarks, outcomes); access (Search Console, analytics, CMS, Bing Webmaster
Tools); excluded vendors or channels; approvers.

**2. Plan** - one row per roadmap item, grouped by workstream:

| Column | Content |
|---|---|
| Workstream | Content and page map / Tracking and measurement / Earned presence / Structure and technical |
| Item | the action, written as an outcome |
| From the deck | the finding or slide it comes from |
| Start | "Month N" |
| End | "Month N" or "Ongoing" |
| Owner | Agency, Client, or both |
| Priority | High / Medium / Low |
| Status | Not started / In progress / Done / Blocked |
| Evidence link | the workbook tab, brief or page that proves it shipped |

To the right, a monthly timeline: one column per month headed "Month 1" ... "Month 12" (text, never
dates), each cell a formula that shows a bar when the month falls between Start and End, coloured with
conditional formatting. Months, not weeks: the plan is reviewed monthly.

**3. Tracker** - what actually shipped, one row per deliverable: Item (matching the Plan), Month, Status,
Blocker, Link. The Plan's Status column can read from it with a lookup.

**4. Experiments** (optional) - the experiment backlog scored Impact / Confidence / Effort / Speed (see
`what-wins-content.md`), with the result once measured.

## Build steps

1. Load any existing workbook with openpyxl **default** (not `data_only=True`, or you destroy formulas).
2. Set the client name in the title row of each sheet.
3. Write month labels as text ("Month 1" ...) with `number_format = '@'`. Never real dates: the workbook is
   reused per prospect.
4. In a client template, keep its existing SEO items (they apply to AEO) and add the AEO workstreams after
   them, styled by copying `cell._style` from existing rows (same workbook only; `gotchas.md` #7).
5. Fill the Plan from the deck's way-forward slides, content first (below), and seed the Tracker with the
   Month 1 items.
6. Recalculate (LibreOffice headless) and confirm zero formula errors.

## Mapping the deck to the plan, content first

- **Month 1 (decisions and setup):** sign off the keyword and prompt list; the page map (one owner page per
  keyword and prompt); the content calendar; data-access requests; prompt tracking live with the baseline
  recorded; same-week technical fixes such as a noindex on a money page or unmarked FAQ blocks.
- **Months 2-3 (first content and proof):** selling-page rewrites, the first pillar and its clusters,
  comparison and alternatives pages, author pages, the glossary, and the first visibility read against the
  baseline. Schema enrichment, entity work and canonical or redirect hygiene run alongside at Medium.
- **Ongoing:** the content calendar, proprietary data pages once access lands, earned presence
  (communities, video, editorial, review sites), and the monthly read of visibility and share of voice
  with a quarterly re-score of the readiness index.
