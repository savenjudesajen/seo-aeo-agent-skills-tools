# -*- coding: utf-8 -*-
"""The packed block model for a competitor overview page (comparison hub), in page order, with the count behind each
block computed from the coded hubs in public_sample.py (plus the client set once it is filled in).

Edit CLIENT, the block names (keep one name per block everywhere) and STATUS for each run: status compares each block
with the client's site today (New, Rework = the content exists on the site in another form, Optional, Later = waits for
content only the client can supply). Every example named in a block must carry the section it illustrates; the
asserts at the bottom check that. Scripts only count. Standard library only.
Run: python3 block_model.py   (prints the order table and the status tally; exits non-zero on a failed assert)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import public_sample as S   # noqa: E402

CLIENT = {'name': '<Client>', 'product': '<Product>', 'offer': '<main offer label>'}

H = S.all_hubs()
N = len(H)
VENDORS = {k for k, v in H.items() if v[1] == 'vendor'}


def hubs(*ids):
    """Hubs that carry any of the given section types."""
    return {k for k, v in H.items() if v[3] & set(ids)}


def of(s, base=None):
    return '%d of %d' % (len(s), N if base is None else base)


# derived sets (hand decisions live in public_sample.SIGNALS; these only combine them)
HERO_CTA = S.signal('hero_cta')
QUESTION_H1 = S.signal('question_h1')
TABLE_MULTI = S.signal('table_named_multi')
NUMBERED = S.signal('numbered_sources')
BYLINE = hubs(10, 11)
DISCLOSE = hubs(15)
METHOD = hubs(7, 9, 14, 16)
PROOF = hubs(17, 18)
BALANCE = hubs(21, 26)
NEED = hubs(30, 31)

C, P, O = CLIENT['name'], CLIENT['product'], CLIENT['offer']

# key, stage, block name, status, count cell, best public examples (comma-separated; asserted below)
HUB = [
    ('nav', 'Capture', 'Menu link: "Compare %s" under the product or Why menu' % P, 'New',
     'No top-level Compare item in the SaaS reference set (0 of %d menus); %d of %d footers link comparisons'
     % (S.NAV_READ, len(S.NAV['footer']), S.NAV_READ), ''),
    ('hero', 'Capture', 'Breadcrumb, question H1 and a 40 to 60 word answer', 'New',
     '%s open with a hero, %d ask a question in the H1' % (of(hubs(1)), len(QUESTION_H1)), 'Zendesk'),
    ('byline', 'Capture', 'Byline: written by, reviewed by, last reviewed date', 'New',
     '%s name an author, %s show a date' % (of(BYLINE), of(hubs(13))), ''),
    ('disclose', 'Capture', 'Disclosure: %s wrote this page and sells %s' % (C, P), 'New',
     '%s, no vendor hub' % of(DISCLOSE) if not (DISCLOSE & VENDORS) else of(DISCLOSE), 'Capterra'),
    ('button', 'Capture', 'Button: %s' % O, 'Rework', '%s put a button in the hero' % of(HERO_CTA),
     'Shopify, Semrush'),
    ('proof', 'Capture', 'Proof strip: <n> proof items, each with its source and date', 'Rework',
     '%s show ratings, logos or customer proof' % of(PROOF), 'Semrush, Ahrefs'),
    ('verdict', 'Capture', 'The short answer: which tool fits which job', 'New', of(hubs(2)), ''),
    ('effort', 'Capture', 'Evaluation strip: what was compared, from how many sources, when', 'Optional',
     of(hubs(8)), 'G2, Capterra'),
    ('toc', 'Capture', 'On this page: jump links to each section', 'New', of(hubs(39)), 'Zendesk'),
    ('need', 'Orient', 'Compare by need: start from the tool a buyer runs today', 'New', of(NEED),
     'Shopify, G2'),
    ('cards', 'Orient', 'Competitor cards: category, best for, where %s differs, link' % C, 'New',
     '%s link a list of comparisons, %d give each a best-for line' % (of(hubs(29)), len(hubs(3))),
     'monday.com, Capterra'),
    ('table', 'Evaluate', 'Comparison table in text: dated, sourced, with a row each rival leads', 'New',
     '%s carry a comparison table, %d name three or more products' % (of(hubs(4)), len(TABLE_MULTI)),
     'Zendesk, ClickUp'),
    ('balance', 'Evaluate', 'Where each platform leads, %s included' % C, 'New', of(BALANCE), ''),
    ('fit', 'Evaluate', 'Where %s fits beside the tools a buyer runs' % P, 'New',
     '%d of the %d SaaS comparison pages offer to run beside the rival' % (len(S.VS['coexistence']),
                                                                         len(S.VS_ALL)),
     'Intercom, monday.com'),
    ('explainer', 'Evaluate', 'What each type of tool does', 'New', of(hubs(35)), ''),
    ('considered', 'Evaluate', 'Also considered: tools buyers confuse with %s, and why' % C, 'Optional',
     of(hubs(25)), ''),
    ('market', 'Evaluate', 'How the category is changing, with dates and sources', 'Optional', of(hubs(28)),
     'Ahrefs'),
    ('objections', 'De-risk', 'Doubts answered: the objections buyers raise', 'New', of(hubs(27)),
     'Asana'),
    ('stories', 'De-risk', 'Customer stories from teams that switched to or added %s' % P, 'Later',
     of(hubs(18)), 'Zendesk, Shopify'),
    ('checklist', 'De-risk', 'Buyer\'s checklist: questions to ask any vendor, %s included' % C, 'New',
     of(hubs(36)), 'Capterra, ClickUp'),
    ('faq', 'De-risk', 'FAQ: questions in the words buyers type into AI assistants', 'Rework', of(hubs(38)),
     'Zendesk, ClickUp'),
    ('method', 'De-risk', 'How we compare: criteria, sources, change log, corrections', 'New',
     '%s show a method, criteria, trust box or change log' % of(METHOD), 'Capterra, G2'),
    ('sources', 'De-risk', 'Numbered sources for every claim', 'New',
     '%s footnote or cite sources, %d number them' % (of(hubs(19)), len(NUMBERED)), ''),
    ('builder', 'De-risk', 'Side-by-side builder: pick two vendors', 'Later', of(hubs(32)), 'Capterra, G2'),
    ('related', 'Convert', 'Related reading: <two or three resource links by intent>', 'New', of(hubs(44)),
     'Zendesk, monday.com'),
    ('closing', 'Convert', 'Closing band: %s, then <secondary links>' % O, 'New',
     '%s close with a call to action' % of(S.signal('closing_cta')), 'Shopify, Miro'),
    ('footer', 'Convert', 'Footer: a Compare group naming the main rivals, then All comparisons', 'New',
     '%d of %d SaaS footers name each main rival' % (len(S.NAV['footer_names_rivals']), S.NAV_READ),
     'Zendesk, ClickUp'),
]
KEYS = [r[0] for r in HUB]
NUM = {k: i + 1 for i, k in enumerate(KEYS)}
assert len(set(KEYS)) == len(KEYS)
STATUSES = ('New', 'Rework', 'Optional', 'Later')
STAGES = ('Capture', 'Orient', 'Evaluate', 'De-risk', 'Convert')
TALLY = {s: sum(1 for r in HUB if r[3] == s) for s in STATUSES}
assert all(r[3] in STATUSES and r[1] in STAGES for r in HUB)
assert sum(TALLY.values()) == len(HUB)
LAUNCH = [r for r in HUB if r[3] in ('New', 'Rework')]

# each block's examples must sit in the set the block is counted by
EXAMPLE_SETS = {
    'hero': QUESTION_H1, 'disclose': DISCLOSE, 'button': HERO_CTA, 'proof': PROOF, 'effort': hubs(8),
    'toc': hubs(39), 'need': NEED, 'cards': hubs(3, 29), 'table': hubs(4) & TABLE_MULTI, 'balance': BALANCE,
    'explainer': hubs(35), 'market': hubs(28), 'objections': hubs(27), 'stories': hubs(18),
    'checklist': hubs(36), 'faq': hubs(38), 'method': METHOD, 'sources': NUMBERED, 'builder': hubs(32),
    'related': hubs(44), 'closing': S.signal('closing_cta'), 'footer': S.NAV['footer_names_rivals'],
    'fit': {p[1] for p in S.VS_PAGES if p[0] in S.VS['coexistence']},
}
for r in HUB:
    for ex in [e for e in r[5].split(', ') if e]:
        assert r[0] in EXAMPLE_SETS, ('no example set for', r[0])
        assert ex in EXAMPLE_SETS[r[0]], (r[0], ex)

# where each of the 45 section types lands on the recommended hub (Appendix B): a block or a "Not used" reason
LANDS = {
    1: 'Hero', 2: 'The short answer', 3: 'Competitor cards: Best for line', 4: 'Comparison table',
    5: 'Not used: rival scores set by a vendor read as biased, so the table shows third-party ratings',
    6: 'Not used: How we compare lists the criteria instead', 7: 'How we compare',
    8: 'Evaluation strip (optional)', 9: 'How we compare: which vendors are included and why', 10: 'Byline',
    11: 'Byline: reviewed by', 12: 'Byline names link to bios', 13: 'Byline: last reviewed date',
    14: 'How we compare: change log', 15: 'Disclosure line', 16: 'How we compare, with the disclosure line',
    17: 'Proof strip and the table\'s ratings row', 18: 'Proof strip, customer stories (later)',
    19: 'Numbered sources', 20: 'Competitor cards', 21: 'Where each platform leads',
    22: 'Not used: rivals\' screens', 23: 'Not used at launch: no comparison video',
    24: 'Not used: no lab benchmark', 25: 'Also considered (optional)', 26: 'Where each platform leads',
    27: 'Doubts answered', 28: 'How the category is changing (optional)', 29: 'Competitor cards',
    30: 'Compare by need', 31: 'Compare by need', 32: 'Side-by-side builder (later)',
    33: 'Not used unless the product has something to calculate',
    34: 'Not used: a vendor-drawn market map reads as biased', 35: 'What each type of tool does',
    36: 'Buyer\'s checklist', 37: 'Comparison pages carry the switch path', 38: 'FAQ', 39: 'On this page',
    40: 'Comparison table: pricing model row', 41: 'Not used: a vendor naming itself winner reads as biased',
    42: 'Where %s fits' % P, 43: 'Checklist download and the main offer', 44: 'Related reading',
    45: 'Button and closing band',
}
assert set(LANDS) == set(range(1, S.N_TYPES + 1))

if __name__ == '__main__':
    print('hubs counted:', N)
    for i, r in enumerate(HUB, 1):
        print('%2d %-8s %-8s %-70s | %s | %s' % (i, r[1], r[3], r[2][:70], r[4], r[5] or '-'))
    print('tally', TALLY, '| launch blocks', len(LAUNCH))
