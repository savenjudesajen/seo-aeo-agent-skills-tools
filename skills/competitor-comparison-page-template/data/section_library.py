# -*- coding: utf-8 -*-
"""Section-type library for "<Brand> vs <Rival>" comparison pages: one taxonomy, one public benchmark set.

The set (12 public head-to-head pages on the vendors' own sites; re-read anything you reuse, pages change):
  saas   9 pages by SaaS leaders (CRM, customer support, work management, docs, website builder)
  cross  3 pages by vendors in other industries (ecommerce, SEO software)

Every page is coded against the same 50 section types. A page counts for a type only where the page itself
showed the section. Some types are not seen on any vendor page in this set: they are patterns common on
independent review sites, described without a named example (best example starts with "Not in this set").
Set membership was decided by hand from the reads; scripts only count. Page notes:
reference/readings-saas-pages.md and reference/readings-cross-industry-pages.md.

Run: python3 section_library.py   (prints every type with its counts, and the signal tallies)
Standard library only.
"""

# id: (section type, best example (paraphrased), what it gives buyers, what it gives AI answers)
TYPES = {
    1: ('Commercial disclosure (affiliate, advertiser, independence)',
        'Not in this set: review sites put a one-line note on how they are funded above the H1',
        'Knows how the page is funded before reading claims', 'Little directly; a trust signal around the verdict'),
    2: ('Verdict or thesis in the first screen',
        'Semrush: a two-sentence scope contrast in the hero that describes the rival fairly enough to be quoted',
        'The answer before the detail', 'The most quotable sentence for "X or Y?" prompts'),
    3: ('Byline with author credentials',
        'monday.com: a named author with photo, an updated date and a read time on a blog-format comparison',
        'Who is accountable and why they are qualified', 'A named expert and credential attached to the claim'),
    4: ('Why-trust-us box with testing-scale stats',
        'Not in this set: review sites add a box saying how many products they tested and how',
        'Scale of testing behind the verdict', 'Publisher-credibility numbers'),
    5: ('Visible updated or published date',
        'Zendesk: a last-updated date directly under the hero image',
        'Freshness check', 'Recency signal; dated pages are easier to trust and cite'),
    6: ('As-of stamps on figures and evidence (with a correction channel on one vendor)',
        'Ahrefs: an as-of month under a sourced third-party table; Semrush adds a report-an-error link under its data',
        'How current each number is', 'Dated facts that can be quoted with their date'),
    7: ('Update log (dated changelog)',
        'Not in this set: review sites keep a short dated list of what changed in each revision',
        'Proof of maintenance', 'Revision history as a freshness signal'),
    8: ('Key takeaways or short summary (reasons-to-switch list on vendor pages)',
        'monday.com: a takeaways list near the top in which one bullet is a rival strength',
        'The findings in 30 seconds', 'List-shaped findings engines lift as a summary'),
    9: ('Jump links, table of contents or section cards',
        'Shopify: a numbered list of reasons, each a one-line proof and a jump link to its section',
        'Skip to the criterion they care about', 'A section map; with verdict-bearing labels the outline is itself an answer'),
    10: ('Winner or product cards / overall house rating',
         'Not in this set: review sites show a card per product with a house score and a winner label',
         'Winner, score and reasons at a glance', 'Overall score and label per product'),
    11: ('At-a-glance spec or key-differences table',
         'monday.com: an at-a-glance table in text whose first row is Best for',
         'Core facts side by side', 'Row-level facts, easy to extract as a table'),
    12: ('Checkmark or yes/no feature grid',
         'Webflow: a three-way table with an icon plus a one-sentence reason in every cell',
         'Feature parity and gaps', 'Yes/no facts per feature; a sentence per cell stops over-claiming'),
    13: ('Per-category numeric scorecard for both products',
         'Not in this set: review sites score both products per testing category in one table',
         'Where each product is stronger, in one table', 'Scores per category that answer "which is better for X"'),
    14: ('Winner per category (scoreboard, verdict in the heading, per-row winner label)',
         'monday.com: every dimension heading states its verdict, parity verdicts included',
         'A scorecard of who wins what', 'A winner per criterion, the shape engines most often restate'),
    15: ('Head-to-head rounds per dimension',
         'monday.com: one section per buying dimension with a short per-vendor comparison inside',
         'Depth per criterion', 'Paragraph evidence per criterion with a closing verdict line'),
    16: ('Similarities or shared ground',
         'Asana: a grid that marks the rival as equal on half its rows',
         'Removes non-differentiators from the decision', 'Parity facts'),
    17: ('Best-for or choose-if guidance',
         'monday.com: paired go-with-us-if and go-with-the-rival-if lists',
         'Self-selection by need', 'Conditional recommendations for "best for [use case]" prompts'),
    18: ('Concessions: rows or rounds the rival wins',
         'Ahrefs: shows the one metric where the rival is larger and explains why it is not like for like',
         'Makes the rest of the page believable', 'Balanced statements, which engines prefer to one-sided claims'),
    19: ('Differentiator blocks (one-sided strengths)',
         'Ahrefs: a numbered list of things only it can do, one screenshot per item',
         'Jobs only this product does', 'A numbered list of exclusive capabilities'),
    20: ('Hands-on test results with numbers',
         'Not in this set: review sites publish measured tests with the conditions stated',
         'Measured evidence instead of adjectives', 'Specific figures with conditions, highly citable'),
    21: ('Visual evidence (screenshots of both, side-by-side video)',
         'Not in this set: review sites film the same task in both products side by side',
         'Sees the difference', 'Little directly (captions and alt text only)'),
    22: ('Pricing compared for both',
         'Zendesk: a two-column price table that states each side\'s billing basis',
         'Cost at each tier', 'Price rows per tier or term, a top prompt topic'),
    23: ('Total cost, renewal or billing model explained',
         'Shopify: total cost split into setup, platform and operating components, with a calculator',
         'Real cost, not sticker price', 'Cost-model facts and worked examples'),
    24: ('Free trial and refund terms compared',
         'Not in this set: review sites compare trial length and refund terms for both products',
         'Risk of trying each', 'Trial length and refund terms per product'),
    25: ('Interactive tool or live data (calculator, live quote, deal widget, comparison builder)',
         'Asana: an ROI calculator framed as making the case for a switch',
         'Their own numbers', 'A current numeric outcome, if rendered server-side'),
    26: ('Security, audits and certifications compared',
         'Webflow: certifications as a row of its comparison table, crediting the rival\'s enterprise tier where equal',
         'Evidence for the trust decision', 'Auditor names, dates and certification lists'),
    27: ('Incident or track-record section',
         'Shopify: risk on the rival\'s side cited from a public database rather than asserted',
         'How each vendor handles failure', 'Dated incident facts with sources'),
    28: ('Data-handling table (what each collects)',
         'Not in this set: review sites tabulate what each product collects, read from both privacy policies',
         'Exactly what data each touches', 'Row-level facts plus a countable summary'),
    29: ('Customer support compared',
         'monday.com: a support section with a heading per vendor',
         'What help looks like in practice', 'Channel lists and response times'),
    30: ('Ease of use, setup or implementation compared',
         'monday.com: an ease-of-use section with a heading per vendor and user quotes',
         'Time-to-value', 'Setup-time figures and ease scores'),
    31: ('Platform or integration coverage compared',
         'monday.com: an integrations section with a parity verdict',
         'Fit with their stack', 'Counts and named integrations'),
    32: ('Third-party user ratings with the source named',
         'monday.com: review-site scores for both products, each with its review count',
         'Independent satisfaction evidence', 'Scores with source and sample size'),
    33: ('Independent third-party evidence (labs, analysts, public datasets, press awards, legal cases)',
         'Ahrefs: a third-party ranking table, dated and linked to the full report, in which the rival also appears',
         'Proof they can check', 'Outside sources engines trust over vendor claims'),
    34: ('Customer testimonials',
         'Zendesk: story cards from customers who switched from the rival, each with a metric',
         'Peer voices', 'Attributed quotes; provenance labels add weight'),
    35: ('Logo wall and customer-scale stats',
         'Ahrefs: a logo wall with one customer-scale share figure',
         'Social proof', 'Customer counts and share figures'),
    36: ('Reviewer demographics (segment, industry)',
         'Not in this set: review marketplaces show which company sizes and industries review each product',
         '"Is it used by companies like mine?"', 'Segment evidence for "best for enterprise / SMB" prompts'),
    37: ('Pros and cons for both (incl. AI review summary)',
         'Not in this set: review sites list pros and cons for both products, often as counted review themes',
         'Balanced strengths and complaints', 'Counted pro and con themes per product'),
    38: ('Company and market context (ownership, acquisition, roadmap)',
         'Ahrefs: an industry-context section on the rival\'s change of ownership, answered with its own independence',
         'Vendor risk and momentum', 'Ownership and roadmap facts'),
    39: ('Methodology section',
         'Not in this set: review sites explain how they compared, criterion by criterion',
         'Can judge the basis of the verdict', 'Method description that makes claims citable'),
    40: ('Weighted scoring criteria',
         'Not in this set: review sites list the criteria with a weight each',
         'Can reweight for their own priorities', 'Explicit weights behind the verdict'),
    41: ('Migration or getting-started path',
         'Shopify: named migration partners for this exact switch',
         'How to switch and who helps', 'Answers "how to migrate from X to Y"'),
    42: ('Buyer education or tip callouts',
         'Not in this set: a short block that teaches how to judge any product in the category',
         'How to judge any provider', 'Evaluation criteria in checklist form'),
    43: ('FAQ',
         'Airtable: question-led sections, one answering a current rival user with a module-by-module equivalence map',
         'Direct answers to objections', 'Question-shaped pairs in prompt phrasing'),
    44: ('Final verdict section',
         'monday.com: a closing conclusion that restates when each product fits, with a button',
         'Closure', 'A closing verdict with the deciding reason'),
    45: ('Related comparisons or vs-hub links',
         'monday.com: an alternatives link and a run of further comparisons near the end',
         'Next matchups', 'Topical depth across a comparison library'),
    46: ('Alternatives to both products',
         'Not in this set: review marketplaces list alternatives to each product with ratings',
         'Options if neither fits', 'An alternatives list with ratings'),
    47: ('Take-away asset (CSV export, brochure, white paper, emailed comparison)',
         'Notion: the detailed comparison as a downloadable guide',
         'Something to share internally', 'Little (a PDF can be cited on its own)'),
    48: ('Closing CTA band',
         'Ahrefs: a closing band with a live sign-up counter, a sign-up button and a downloadable brochure',
         'Next step', 'Little'),
    49: ('Legal or non-endorsement disclaimer',
         'Not in this set: a footnote saying the rival has not reviewed or approved the comparison',
         'Clarity on what the rival did not approve', 'Little'),
    50: ('Reader feedback or community Q and A',
         'Not in this set: review marketplaces show community questions per product',
         'Real buyer questions', 'Little'),
}

# key: (owner, rival, set, kind, address, format, section type ids)
PAGES = {
    # ---- SaaS leaders, on their own sites
    'HubSpot vs Salesforce': ('HubSpot', 'Salesforce', 'saas', 'vendor', 'hubspot.com/comparisons/salesforce-vs-hubspot',
                              'landing', {2, 6, 8, 12, 19, 33, 34, 35, 41, 43}),
    'Zendesk vs Freshdesk': ('Zendesk', 'Freshdesk', 'saas', 'vendor', 'zendesk.com/why-zendesk/zendesk-vs-freshdesk/',
                             'landing', {2, 5, 8, 11, 15, 19, 22, 33, 34, 43, 45, 48}),
    'monday.com vs Asana': ('monday.com', 'Asana', 'saas', 'vendor',
                            'monday.com/blog/project-management/asana-vs-monday-com-which-to-choose/', 'article',
                            {2, 3, 5, 8, 9, 11, 14, 15, 16, 17, 18, 22, 26, 29, 30, 31, 32, 34, 41, 43, 44, 45, 48}),
    'Asana vs monday.com': ('Asana', 'monday.com', 'saas', 'vendor', 'asana.com/compare/asana-vs-monday-com', 'landing',
                            {2, 6, 12, 16, 19, 25, 30, 31, 33, 34, 35, 43, 48}),
    'ClickUp vs Asana': ('ClickUp', 'Asana', 'saas', 'vendor', 'clickup.com/compare/asana-vs-clickup', 'landing',
                         {2, 12, 29, 32, 35, 45}),
    'Notion vs Confluence': ('Notion', 'Confluence', 'saas', 'vendor', 'notion.com/product/notion-vs-confluence',
                             'landing', {2, 19, 33, 34, 35, 38, 41, 43, 47, 48}),
    'Airtable vs Smartsheet': ('Airtable', 'Smartsheet', 'saas', 'vendor', 'airtable.com/airtable-vs-smartsheet', 'landing',
                               {2, 8, 11, 19, 22, 31, 34, 35, 41, 43, 48}),
    'Intercom vs Zendesk': ('Intercom', 'Zendesk', 'saas', 'vendor', 'intercom.com/compare-intercom-vs-zendesk', 'landing',
                            {2, 8, 12, 19, 30, 31, 34, 35, 41, 43, 48}),
    'Webflow vs WordPress': ('Webflow', 'WordPress', 'saas', 'vendor', 'webflow.com/vs/wordpress', 'landing',
                             {2, 11, 12, 16, 19, 22, 25, 26, 29, 31, 34, 35, 41, 43, 45, 47, 48}),
    # ---- vendors in other industries
    'Shopify': ('Shopify', 'Shopify vs WooCommerce', 'cross', 'vendor', 'shopify.com/compare/shopify-vs-woocommerce',
                'landing', {2, 6, 8, 9, 19, 23, 25, 26, 27, 33, 34, 35, 38, 41, 43, 47, 48}),
    'Ahrefs': ('Ahrefs', 'Ahrefs vs Semrush', 'cross', 'vendor', 'ahrefs.com/vs/semrush', 'landing',
               {2, 6, 12, 18, 19, 33, 35, 38, 47, 48}),
    'Semrush': ('Semrush', 'Semrush vs Ahrefs', 'cross', 'vendor', 'semrush.com/vs/semrush-vs-ahrefs', 'landing',
                {2, 6, 12, 19, 22, 32, 34, 35, 45, 48}),
}

SAAS = {k for k, v in PAGES.items() if v[2] == 'saas'}
CROSS = {k for k, v in PAGES.items() if v[2] == 'cross'}
ALL = SAAS | CROSS
N = len(ALL)
KIND = {k: v[3] for k, v in PAGES.items()}
OWNER = {k: v[0] for k, v in PAGES.items()}
URL = {k: v[4] for k, v in PAGES.items()}
ARTICLES = {k for k, v in PAGES.items() if v[5] == 'article'}
assert len(SAAS) == 9 and len(CROSS) == 3 and N == 12
assert all(v == 'vendor' for v in KIND.values())
for _k, _v in PAGES.items():
    assert _v[6] <= set(TYPES), _k
UNSEEN = {t for t in TYPES if not any(t in v[6] for v in PAGES.values())}
assert all(TYPES[t][1].startswith('Not in this set') for t in UNSEEN)

# Signals read by hand on the 9 SaaS pages (page keys). Not part of the taxonomy; used for "n of the 9" cells.
S = {
    'brand_first_h1': SAAS - {'monday.com vs Asana', 'Notion vs Confluence', 'Webflow vs WordPress'},
    'year_in_title': {'monday.com vs Asana'},
    'table_text_cells': {'Zendesk vs Freshdesk', 'monday.com vs Asana', 'Airtable vs Smartsheet', 'Webflow vs WordPress'},
    'table_top_third': {'HubSpot vs Salesforce', 'Asana vs monday.com', 'ClickUp vs Asana', 'monday.com vs Asana',
                        'Zendesk vs Freshdesk'},
    'parity_rows': {'Asana vs monday.com', 'Webflow vs WordPress', 'monday.com vs Asana'},
    'summary_top': {'HubSpot vs Salesforce', 'monday.com vs Asana', 'Airtable vs Smartsheet', 'Intercom vs Zendesk'},
    'rival_strength_named': {'monday.com vs Asana'},
    'verdict_headings': {'monday.com vs Asana'},
    'switcher_proof': {'Zendesk vs Freshdesk', 'Intercom vs Zendesk', 'HubSpot vs Salesforce', 'Notion vs Confluence'},
    'migration_block': {'Webflow vs WordPress', 'Airtable vs Smartsheet', 'Notion vs Confluence'},
    # offers to run alongside the rival (an integration or a works-with-any answer)
    'coexistence': {'Intercom vs Zendesk', 'HubSpot vs Salesforce', 'monday.com vs Asana'},
    'faq_switch_question': {'HubSpot vs Salesforce', 'monday.com vs Asana', 'Asana vs monday.com',
                            'Notion vs Confluence', 'Airtable vs Smartsheet', 'Intercom vs Zendesk',
                            'Webflow vs WordPress'},
    'sourced_claims': {'HubSpot vs Salesforce'},
    'ai_device': set(),
    # a button in the hero itself (not the site header)
    'hero_cta': set(SAAS),
    # an offer at the end of the page (closing band or final block)
    'closing_cta': SAAS - {'HubSpot vs Salesforce', 'ClickUp vs Asana'},
    'gated_asset': {'Webflow vs WordPress', 'Notion vs Confluence'},
    'calculator': {'Asana vs monday.com', 'Webflow vs WordPress'},
    'reviewer_or_method': set(),
}
for _k, _v in S.items():
    assert _v <= SAAS, _k
# hand checks on the other-industry vendor pages
HERO_CTA_CROSS = {'Shopify', 'Ahrefs'}      # the Semrush hero was not checked for a button
COEXIST_CROSS = {'Shopify'}                 # a plugin to start on the rival's platform before migrating


def pages(*ids):
    """Pages that carry any of the type ids."""
    return {k for k, v in PAGES.items() if v[6] & set(ids)}


def cnt(*ids):
    return len(pages(*ids))


def of(*ids):
    return '%d of %d' % (cnt(*ids), N)


def owners(keys):
    return {OWNER[k] for k in keys}


if __name__ == '__main__':
    print('pages: %d (saas %d, other industries %d)' % (N, len(SAAS), len(CROSS)))
    for tid, t in TYPES.items():
        p = pages(tid)
        print('%2d %-62s saas %d + other %d = %2d' % (tid, t[0][:62], len(p & SAAS), len(p & CROSS), len(p)))
    print('\nsignals on the 9 SaaS pages:')
    for k, v in S.items():
        print('  %-22s %d' % (k, len(v)))
