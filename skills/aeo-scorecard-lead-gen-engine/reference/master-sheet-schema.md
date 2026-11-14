# Master tracking sheet: schema

One row per account. **The single source of truth.** Each finished audit writes its score,
competitor and gap back to the row; the row drives the ad copy and the landing page. A wrong row
means every downstream asset is wrong.

## Columns
| Group | Fields | Filled by |
|---|---|---|
| Identity | company_name, website_domain, country, market_language, segment | Pre-filled |
| Competitors | primary_competitor (the ad hook), competitor_set (3 to 6) | Audit |
| Score | composite (auto), plus the 7 pillars: citation_share, content_structure, answer_readiness, competitor_gaps, freshness, entity_clarity, offsite_mentions | Audit |
| Diagnosis | biggest_gap, top_play | Audit |
| Creative | ad_intro, ad_headline (auto), ad_description | Auto / audit |
| Delivery | landing_url, internal_report_url | Build |
| Ops | campaign_stage, last_run, run_status, qa_passed | Ops |
| CRM | contact_name, contact_title, contact_linkedin, crm_id | Ops |
| Notes | notes (also keep deliverable file references here) | Anyone |

## Two mechanics to build in
1. **The composite rolls up automatically** from the 7 pillars:
   `=IFERROR(ROUND(AVERAGE(<pillar range>),0),"")`. `IFERROR` keeps the sheet clean before scores
   land.
2. **The ad headline builds itself** from identity and competitor:
   `=IF(OR(<company>="",<competitor>=""),"",<hook template with both cells>)`, e.g.
   `"AI recommends "&<competitor>&". Where is "&<company>&"?"`. Write the template once per
   campaign, in the brand's voice and the account's language.

Together these mean a finished audit produces the ad copy for free. That's the mechanism worth
showing a client: it turns an audit into a motion.

## Controlled values
- campaign_stage: Not started | Queued | Report ready | Ad live | Engaged | Booked | Handed off | Excluded
- run_status: OK | Broken - re-run | Pending
- qa_passed: Yes | No

## Rules
- **Exclude accounts with no real domain.** If the "website" is a social profile, there's nothing to
  audit: mark it Excluded.
- **Flag the too-clean accounts.** Very large brands are often already visible in AI answers; they
  make weak demos with no gap to show.
- Keep `market_language` even in an English-only first version: it makes localisation a later switch,
  not a rebuild.
- Set `qa_passed` = Yes only after a human has read the report. Never automate that flag.

## Build gotcha: formulas and cached values
`openpyxl` writes formulas but clears their cached values on save, and a headless LibreOffice recalc
often times out in a locked-down sandbox. Excel and Google Sheets recompute on open, so the formulas
are fine there, but quick-preview tools show blank cells. For a single scored pilot row, write the
composite and headline as values (not formulas) so they display everywhere; leave formulas on the
unscored rows.
