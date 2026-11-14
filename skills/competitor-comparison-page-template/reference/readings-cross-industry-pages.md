# Readings: 3 vendor comparison pages from other industries, plus review-site patterns

Vendor head-to-head pages outside the SaaS-leader set, chosen because they show what a vendor can adopt without
reading as biased. Coded in `data/section_library.py` (type ids in brackets). Notes are paraphrased descriptions of
structure and claim patterns. Re-read the live page before you capture or describe it; never quote from these notes.

## Shopify: Shopify vs WooCommerce
- shopify.com/compare/shopify-vs-woocommerce. Switch and enterprise landing page in a /compare library. No page
  date; dated proof cards only.
- Order: hero with a thesis line and two buttons > switcher logo strip > four numbered reasons, each a one-line
  proof and a jump link > four pillars (security with the rival's vulnerabilities cited from a public database,
  total cost split into setup, platform and operating cost with a calculator and a white paper, usability with a
  plugin to start selling on the rival's platform before migrating, capabilities and roadmap) > analyst and press
  validation as dated, linked cards > migration partners named for this exact switch > a four-question FAQ that
  discloses the cost study as commissioned > closing band.
- Stands out: reasons as jump links [8, 9]; a cost argument broken into components [23]; rival risk cited from a
  public source rather than asserted [27, 33]; named migration partners [41]; a coexistence path.
- Caution: the proof cards were dated two to three years before the read and there is no page date.

## Ahrefs: Ahrefs vs Semrush
- ahrefs.com/vs/semrush. No page date; one third-party table carries an as-of month.
- Order: hero with the buyer's question and one button > a logo wall with a customer-share figure > a numeric data
  face-off that shows the one metric where the rival is larger and explains why it is not like for like > a third-
  party ranking table (the rival appears in it), dated and linked > a numbered list of things only it can do, one
  screenshot each > a short checkmark recap that mixes facts and jokes > an industry-context block on the rival's
  change of ownership > a closing band with a live sign-up counter and a downloadable brochure.
- Stands out: dated, linked third-party evidence [6, 33]; an honest qualifier on the rival's bigger number [18]; a
  numbered exclusives list [19]; company context [38]; a take-away brochure [47].
- Caution: the face-off numbers carry no source or date; no pricing or FAQ.

## Semrush: Semrush vs Ahrefs
- semrush.com/vs/semrush-vs-ahrefs (breadcrumb to a vs hub). The body renders only with JavaScript. A data-as-of
  note on the table that was more than a year old at the read.
- Order: breadcrumb to the comparison library > hero with a two-sentence scope contrast that describes the rival
  fairly enough to be quoted > logos > a grouped table covering many categories, with numeric rows, both products'
  entry prices, the as-of note and a report-an-error link > named testimonials > review-site ratings by source >
  capability blocks with buttons > closing band.
- Stands out: a correction channel under the data [6]; a fair scope contrast in the hero [2].
- Caution: its database totals contradict the rival's page for the same metrics, and the date was stale. Dated,
  sourced numbers matter because the other side publishes its own.

## Trust patterns from independent review sites (no example carried)
Vendor pages in this set never show these, so the block model takes them from the review-site format in general.
If you want a capture, pick an independent review page in a category unrelated to the client and its rivals.
- A one-line disclosure of how the page is funded or who wrote it, above the H1 [1].
- A byline with the writer's role and a named second checker, plus a visible updated date [3, 5].
- A short how-we-compared section: what was checked on each product, when, and by whom [39].
- A dated change log that says what changed in each revision, and a way to report an error [7].
- Choose-if lists for both products and a Best for row in the table [11, 17].
- Measured tests with the conditions stated, including the rows the runner-up wins [18, 20].
- Scorecards, winner cards and weights are common there too, but a vendor that scores both products reads as
  biased: this model lists them as "Not used" [10, 13, 40].

## Cross-cutting notes
- Rendering: some tables appear only with JavaScript. A table you want quoted must ship in the server-rendered HTML.
- One source of truth: when the summary, table, sections and FAQ are written separately they drift apart. Feed every
  number from one data source.
- Freshness: proof cards dated years back, or a data-as-of note more than a year old, read as neglect.
- Concessions are rare on vendor pages: 2 of the 12 give the rival a row or a point.

## What vendor comparison pages usually lack (counted on all 12 vendor pages)
Each item: the gap, how many of the 12 had it, and the honest vendor version.

1. Choose-if guidance per use case. 1 of 12. Vendor version: "Choose {Company} if" and "Choose <Rival> if", with at
   least one real condition where the rival is the better fit.
2. Sections with the result in the heading. 1 of 12. Vendor version: one section per buying question labelled
   {Company} leads, Parity or <Rival> leads, each with a one-line wrap-up and an evidence link.
3. Category scorecard. 0 of 12. Vendor version: never self-score; show both products' third-party category ratings
   with review counts and an as-of date.
4. Method. 0 of 12. Vendor version: sources, dates, who ran the comparison, what was checked on the rival, and what
   could not be verified.
5. Hands-on test data. 0 of 12. Vendor version: repeatable tests with date and method, including rows the rival
   wins.
6. Pricing with total cost. 5 of 12 compare prices; 1 explains the cost model. Vendor version: where pricing is
   quote-based, compare the pricing model (unit billed, what is included, add-ons) and cite the rival's public
   pricing page with a date.
7. Pros and cons for both. 0 of 12. Vendor version: both sides from third-party reviews with counts and a date,
   including your own cons.
8. Third-party ratings for both. 1 of 12 shows ratings for both products. Vendor version: both products' review-site
   scores side by side, with review counts, date and links.
9. Certifications compared with dates and scope. 3 of 12 mention certifications. Vendor version: a certification
   table for both (standard, scope, date) linking each company's trust page.
10. Support compared with published service levels. 3 of 12 touch support. Vendor version: support model (hours,
    channels, service levels) from published terms plus both products' third-party support scores.
11. Ease of setup with screenshots. 3 of 12. Vendor version: onboarding steps, screenshots and time to first value,
    described against the rival's public onboarding documentation.
12. Neutral key takeaways. 1 of 12 includes a rival strength. Vendor version: four to six bullets that include at
    least one rival strength; reuse the first as the meta description.
13. Author and expert reviewer. 1 of 12 has a byline, 0 a reviewer. Vendor version: a named author and a named
    technical reviewer with credentials, plus a link to the editorial policy for comparison pages.
14. Visible date, as-of stamps and an update log. 2 of 12 show a page date, 5 date some figures, 0 keep a log. Vendor
    version: last reviewed date, per-table as-of stamps, a public change log and a report-an-error link.
15. Alternatives to both. 0 of 12. Vendor version: a short other-options block with category context, linking your
    other comparison pages.
