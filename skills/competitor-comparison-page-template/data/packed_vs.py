# -*- coding: utf-8 -*-
"""Packed block order for a "{Company} vs <Rival>" comparison page template.

Counts come from section_library.py: 12 published comparison pages on vendors' own sites (9 by SaaS leaders, 3 by
vendors in other industries), each coded against the same 50 section types. Every block names the type ids it is
counted by; derived sets are decided by hand from the reads. Scripts only count.

Default statuses assume a company with no comparison pages yet: every block is New except three depth blocks
(company context, take-away, AI prompt) that are Optional because they never block a launch. Re-decide every status
against the company's live site in each run (New, Rework, Optional, Later) and set them in STATUS_OVERRIDES.

Run: python3 packed_vs.py   (prints the block list with its counts). Standard library only.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import section_library as L   # noqa: E402

T = L.TYPES
N = L.N
NONE = 'none in this set'


def pages(*ids):
    return L.pages(*ids)


def of(s):
    return '%d of %d' % (len(s), N)


# ---- derived sets, decided by hand from the reads -----------------------------------------------------------------
BYLINE = pages(3)
assert BYLINE == {'monday.com vs Asana'}
DATED = pages(5)
DISCLOSE = pages(1, 49)            # a statement of interest or a non-endorsement line: not on any vendor page here
assert not DISCLOSE
TABLE = pages(11, 12)
CONCEDE = pages(18)
ONE_SIDED = pages(19)
ROUNDS = pages(15)
BOUGHT = pages(22, 23, 24)
SECURITY = pages(26, 28)
CONTEXT = pages(38)
EVIDENCE = pages(32, 33, 34)
START = pages(41)
METHOD = pages(39, 4, 7, 40)       # a method, trust box, change log or weights: a review-site pattern, none here
assert not METHOD
SOURCES = pages(6)
SCREENS = pages(21)
ASSET = pages(47)
RELATED = pages(45)
CLOSING = pages(48)
PROOF = pages(35)
HERO_CTA = L.S['hero_cta'] | L.HERO_CTA_CROSS
TOGETHER = L.S['coexistence'] | L.COEXIST_CROSS
AI_PROMPT = set(L.S['ai_device'])

# ---- the comparison page, in page order ----------------------------------------------------------------------------
# key, stage, block, default status, count cell, best examples (owners of pages in the set the block is counted by)
VS = [
    ('hero', 'Capture', 'Breadcrumb, H1 "{Company} vs <Rival>" and the difference in one line', 'New',
     '%s state a verdict or thesis in the first screen' % of(pages(2)), 'Semrush, Ahrefs, Airtable'),
    ('byline', 'Capture', 'Byline: written by, reviewed by, last reviewed', 'New',
     '%s name an author, %s show a date' % (of(BYLINE), of(DATED)), 'monday.com'),
    ('disclose', 'Capture', 'Disclosure: {Company} wrote this page and sells {Product}', 'New',
     '%s (a review-site pattern a vendor can adopt)' % of(DISCLOSE), NONE),
    ('button', 'Capture', 'Button: the one call to action the site uses for this audience', 'New',
     'all 9 SaaS pages, and Shopify and Ahrefs', 'Shopify, Ahrefs, Airtable'),
    ('proof', 'Capture', 'Proof strip: a few sourced proof points', 'New',
     '%s show logos or customer-scale numbers' % of(PROOF), 'Ahrefs, Shopify, Asana'),
    ('answer', 'Orient', 'Key takeaways: the short answer, one point a rival strength', 'New',
     '%s open with takeaways or a short answer' % of(pages(8)), 'monday.com, Shopify, HubSpot'),
    ('choose', 'Orient', 'Choose {Company} if, Choose <Rival> if', 'New', of(pages(17)), 'monday.com'),
    ('toc', 'Orient', 'On this page: jump links that carry each section\'s answer', 'New', of(pages(9)),
     'Shopify, monday.com'),
    ('table', 'Evaluate', 'At-a-glance table: the same rows in text on every page, dated, a Leads tag on each row',
     'New', '%s carry a table, %d name a winner per row' % (of(TABLE), len(pages(14))),
     'monday.com, Webflow, Zendesk'),
    ('leads', 'Evaluate', 'Where each one leads, <Rival> first', 'New',
     '%s concede a row or a point to the rival, %d list one-sided strengths' % (of(CONCEDE), len(ONE_SIDED)),
     'monday.com, Ahrefs'),
    ('shared', 'Evaluate', 'What both do: the ground they share', 'New', of(pages(16)), 'Asana, Webflow'),
    ('rounds', 'Evaluate', 'Sections by buying question, the answer in each heading', 'New',
     '%s run one section per dimension' % of(ROUNDS), 'monday.com, Zendesk'),
    ('together', 'Evaluate', 'Where they work together: keep <Rival>, add {Product}', 'New',
     '3 of the 9 SaaS pages, and Shopify', 'Intercom, HubSpot, Shopify'),
    ('bought', 'Evaluate', 'How each one is bought: pricing model, trial, contract', 'New',
     '%s compare pricing, %d explain the cost model' % (of(pages(22)), len(pages(23))),
     'Zendesk, Shopify, monday.com'),
    ('security', 'Evaluate', 'Security and data handling: certifications for both', 'New',
     '%s compare security or certifications' % of(pages(26)), 'Webflow, monday.com'),
    ('context', 'Evaluate', 'Company context: ownership and acquisitions, dated and sourced', 'Optional', of(CONTEXT),
     'Ahrefs, Notion'),
    ('evidence', 'De-risk', 'Proof measured against this rival: quotes, ratings and research, each dated', 'New',
     '%s quote customers, %d name the source of review-site ratings, %d cite analysts or public data'
     % (of(pages(34)), len(pages(32)), len(pages(33))), 'Ahrefs, Shopify, monday.com'),
    ('start', 'De-risk', 'Getting started beside <Rival>: what a <Rival> customer needs', 'New', of(START),
     'Airtable, Shopify, Notion'),
    ('faq', 'De-risk', 'FAQ: the questions <Rival> customers ask', 'New', of(pages(43)), 'Airtable, Intercom, Webflow'),
    ('method', 'De-risk', 'How we compared: writer, reviewer, pages checked, change log, corrections', 'New',
     '%s (a review-site pattern a vendor can adopt)' % of(METHOD), NONE),
    ('sources', 'De-risk', 'Numbered sources, each with the date it was read', 'New',
     '%s stamp figures with an as-of date' % of(SOURCES), 'Ahrefs, Semrush, HubSpot'),
    ('screens', 'De-risk', '{Product} in action: one annotated screenshot', 'New', of(SCREENS), NONE),
    ('asset', 'Convert', 'Take-away: the comparison as a one-page PDF', 'Optional', of(ASSET), 'Notion, Ahrefs'),
    ('related', 'Convert', 'Related comparisons, then All comparisons', 'New', of(RELATED),
     'monday.com, ClickUp, Zendesk'),
    ('ai', 'Convert', 'Ask an AI assistant: a neutral prefilled prompt', 'Optional', '0 of %d' % N, NONE),
    ('closing', 'Convert', 'Closing band: one line on the offer, then the button', 'New', of(CLOSING),
     'Ahrefs, Shopify, Webflow'),
]
KEYS = [r[0] for r in VS]
assert len(set(KEYS)) == len(KEYS)

# Per-run statuses: set {key: status} after auditing the live site. Allowed: New, Rework, Optional, Later.
STATUS_OVERRIDES = {}
VS = [(k, st, name, STATUS_OVERRIDES.get(k, s), c, ex) for (k, st, name, s, c, ex) in VS]
STATUS = {}
for r in VS:
    STATUS[r[3]] = STATUS.get(r[3], 0) + 1
assert set(STATUS) <= {'New', 'Rework', 'Optional', 'Later'}, STATUS
STAGES = ['Capture', 'Orient', 'Evaluate', 'De-risk', 'Convert']
LAUNCH = [r for r in VS if r[3] in ('New', 'Rework')]

# examples named in the best-example column must carry the section (checked against the set it is counted by)
EXAMPLE_SETS = {
    'hero': pages(2), 'byline': BYLINE, 'disclose': DISCLOSE, 'button': HERO_CTA, 'proof': PROOF, 'answer': pages(8),
    'choose': pages(17), 'toc': pages(9), 'table': TABLE, 'leads': CONCEDE, 'shared': pages(16), 'rounds': ROUNDS,
    'together': TOGETHER, 'bought': BOUGHT, 'security': SECURITY, 'context': CONTEXT, 'evidence': EVIDENCE,
    'start': START, 'faq': pages(43), 'method': METHOD, 'sources': SOURCES, 'screens': SCREENS, 'asset': ASSET,
    'related': RELATED, 'ai': AI_PROMPT, 'closing': CLOSING,
}
assert set(EXAMPLE_SETS) == set(KEYS)
for r in VS:
    if r[5] == NONE:
        assert not EXAMPLE_SETS[r[0]], r[0]
        continue
    have = L.owners(EXAMPLE_SETS[r[0]])
    for ex in r[5].split(', '):
        assert ex in have, (r[0], ex)

# where each of the 50 types lands on the company's comparison pages: a block, or the reason it is not used
LANDS = {
    1: 'Disclosure line', 2: 'Difference line and key takeaways', 3: 'Byline', 4: 'How we compared',
    5: 'Byline: last reviewed', 6: 'Numbered sources with the date read', 7: 'How we compared: change log',
    8: 'Key takeaways', 9: 'On this page', 10: 'Not used: a vendor rating both products reads as biased',
    11: 'At-a-glance table', 12: 'Not used: ticks hide the difference, so the table uses sentences',
    13: 'Not used: scores a vendor sets read as biased', 14: 'Table: the Leads tag on each row',
    15: 'Sections by buying question', 16: 'What both do', 17: 'Choose-if lists',
    18: 'Where each one leads: Where <Rival> leads', 19: 'Where each one leads: Where {Company} leads',
    20: 'Proof measured against this rival', 21: '{Product} in action', 22: 'How each one is bought',
    23: 'How each one is bought: the cost model', 24: 'How each one is bought: trial or first step',
    25: 'Not used unless the product has something to calculate', 26: 'Security and data handling',
    27: 'Not used: a vendor listing a rival\'s incidents reads as an attack', 28: 'Security and data handling',
    29: 'Sections by buying question: support', 30: 'Getting started beside <Rival>',
    31: 'Where they work together: how they connect', 32: 'Proof: review-site ratings for both, dated',
    33: 'Proof: analyst research and public data', 34: 'Proof strip, and proof measured against this rival',
    35: 'Proof strip', 36: 'Not used unless {Company} has review-site data of its own', 37: 'Where each one leads',
    38: 'Company context (optional)', 39: 'How we compared',
    40: 'Not used: How we compared lists the rows, not weights', 41: 'Getting started beside <Rival>',
    42: 'Sections by buying question: a tip line where it helps', 43: 'FAQ',
    44: 'Not used: the answer sits at the top', 45: 'Related comparisons',
    46: 'Related comparisons: All comparisons on the hub', 47: 'Take-away PDF (optional)', 48: 'Closing band',
    49: 'Disclosure line and the trademark line', 50: 'Not used: no reader comments',
}
assert set(LANDS) == set(T)

if __name__ == '__main__':
    for i, r in enumerate(VS, 1):
        print('%2d %-8s %-8s %-70s | %s | %s' % (i, r[1], r[3], r[2][:70], r[4], r[5]))
    print(STATUS, 'launch', len(LAUNCH))
