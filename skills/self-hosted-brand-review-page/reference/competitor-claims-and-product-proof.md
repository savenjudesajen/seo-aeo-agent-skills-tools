# Competitor claims register and product proof

Contents: 1. The claims register (start it in Phase 1, before any writing) · 2. Use the product (Phase 1b, before writing) · 3. Serve it to the writer: the claims-to-answer brief · 4. Checks the QA agent runs on this part

Two inputs the writer cannot do without. The claims register says what other people tell buyers
about the brand. The product notes say what is true, read from inside the product. The page
answers the first with the second.

Examples in this file use a fictional brand: TimeTrellis, a time-tracking app for agencies
(timetrellis.example). All counts are invented for illustration.

## 1. The claims register (start it in Phase 1, before any writing)

### What to read

Every page that ranks in the top 20 for "<brand> review", "<brand> reviews", "<brand>
alternatives", "<brand> pricing" and "is <brand> worth it", plus the brand's own listings on
review platforms (they often carry an old product description). Expect a mix of pages written by
competing vendors or their affiliates and pages by independents (bloggers, agencies, review
sites, review platform listings). Count the split; the page will say it.

Scrape competitors freely. A no-competitor-names rule governs what the page says, never what you
read.

### How to capture it

Run it as one sub-agent per batch of pages (it keeps a large volume of competitor prose out of
the main context). Bulk scrapers often cap the characters returned per page, so re-read long pages
with single-page scrapes and note in `read_notes` which pages were still cut off.

One JSON file, `claims_register.json`:

```json
{
  "generated": "YYYY-MM-DD",
  "scope_note": "Claims third-party and competitor-written pages make about <brand>. Snippets are short excerpts for internal use only.",
  "narrative_to_change": "<the one outdated narrative the brand most needs to change>",
  "pages": [
    {
      "url": "...", "owner": "competitor vendor (<name>) | affiliate | independent | review platform",
      "author": "...", "date": "as printed, or 'from SERP'",
      "narrative_flag": {"level": "explicit | implied | none", "snippets": ["..."], "note": ""},
      "claims": [
        {"claim_paraphrase": "...", "snippet": "exact words, under 25", "topic": "positioning/category | pricing/cost | UX | core features | integrations | scale/enterprise fit | support | other",
         "polarity": "con | pro | neutral", "type": "OUTDATED_POSITIONING | FEATURE_GAP_CLAIM | PRICING | UX | OTHER",
         "recurring_group": "R_<SHORT_ID>"}
      ]
    }
  ],
  "recurring": [
    {"id": "R_<SHORT_ID>", "claim": "one-line normalised claim", "topic": "...", "type": "...", "count": 0, "urls": ["..."]}
  ],
  "single_page_claims_of_note": [],
  "narrative_flags": [],
  "pages_not_found_or_failed": [],
  "read_notes": []
}
```

Rules for the sub-agent:
- `count` is the number of distinct pages making the claim, never the number of mentions.
- The `narrative_flag` field tracks the one narrative the brand most needs to change (for example
  "an old category label", "desktop only", "no API"). Name it in the prompt for each client.
- Keep the owner type on every page. "Most reviews are by competitors" is a claim the page makes,
  so it needs the number.
- Snippets stay internal. The page never quotes or links a competitor-written review.

Illustrative shape of a finished rollup (fictional, 15 pages read): desktop only 9, per-seat price
jump 8, reports hard to customise 6, no invoicing 4, slow support 3. A typical register has a
handful of claims on many pages and a long tail on one or two.

## 2. Use the product (Phase 1b, before writing)

Reviews and competitor pages describe the product as it was when they were written. The answer to
each claim has to come from the product as it is today, and the only reliable place to see that is
the product.

Walk the client's product UI with the client's own login (a browser, read only: open and read;
never create, change or delete anything in the account). Capture:

1. **Navigation map.** Every top-level area and what it is called in the product.
2. **One proof per recurring claim.** For each `recurring` row, find the screen that confirms or
   disproves it and write one line of fact (what the product shows, in its own words). Fictional
   examples: the download and sign-in screens listing web, desktop and mobile apps disprove
   "desktop only"; the billing page showing per-seat price bands answers "the price jumps when the
   team grows" (partly true); the report builder offering only fixed templates confirms "reports
   are hard to customise".
3. **What must not be published.** The client's own account data, customer names that appear
   in the UI, unreleased features. Write them down as banned.
4. **What you could not verify.** Plan gating, regional coverage, prices. Mark each "not
   verified, do not state". The page says "confirm on a call" instead of a plan limit.

Save it as `product_notes.md` with those four headings. Every product sentence on the page must
trace to a line in it; the QA agent checks this.

## 3. Serve it to the writer: the claims-to-answer brief

Before drafting, turn the register and the notes into one table the writer works from (fictional
example):

| Claim (recurring id) | Pages | Type | True today? | Proof line from product_notes | Where the page answers it |
|---|---|---|---|---|---|
| Desktop app only (R_DESKTOP_ONLY) | 9 | OUTDATED_POSITIONING | No | Web, desktop and mobile apps listed on the sign-in screen | H2 "Is <brand> only a desktop app?" |
| Per-seat price jumps (R_SEAT_JUMP) | 8 | PRICING | Partly | Per-seat bands on the billing page; annual discount shown | H2 cost section, bullet list |
| Reports hard to customise (R_REPORTS) | 6 | UX | Yes | Report builder offers fixed templates plus CSV export | H3 under pushback, with a reviewer quote saying it |

Rules:
- Claims that are true get admitted, quoted from a real reviewer, and answered with what helps
  ("export to CSV for custom views"). Do not argue with a true claim.
- Claims that are out of date get the current fact and no date-based implication you cannot prove
  ("since then we added..." needs a release date).
- Every recurring claim with a count of 5 or more gets an H2, an H3 or a table row.
- The register itself becomes a section: "What do other <brand> reviews say?", a table of claim,
  number of pages out of N, and the section that answers it. It is information no competitor page
  has, and it lets the page address competitor reviews without naming one.
- Outdated-positioning claims (old category label, old prices) also feed a third-party
  correction request, if the client wants one: URL, owner, the outdated words, the current
  wording.

## 4. Checks the QA agent runs on this part

- Every product sentence has a matching line in `product_notes.md`; quote any that overstates it
  (for example, "every report is fully customisable" when the product only offers templates plus
  export).
- Every count in the claims table matches `recurring`; no recurring claim with a count above the
  lowest row shown is left out.
- The owner split stated on the page matches the register.
- Customer result figures match the story body, not only the CMS headline-stat field.
