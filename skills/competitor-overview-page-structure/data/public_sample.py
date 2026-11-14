# -*- coding: utf-8 -*-
"""Public benchmark sample for comparison hubs (competitor overview pages), coded by hand against the 45 section
types in reference/section-types.md.

Two groups ship with the skill:
  - SAAS: 10 well-known SaaS vendors in work-management, CRM, support, website and whiteboard software
    (6 readable hubs, 4 with comparison pages only)
  - CROSS: 5 comparison hubs from other industries (3 vendors and 2 software marketplaces)
Reuse these codings on any run and add the client's own set (named rivals plus category peers) in CLIENT_SET below.
Before reusing a public hub, check that it is not in the client's own category or competitor set; if it is, leave it
out of the run (delete its row locally) so the cross-industry benchmark never maps back to the client.
Navigation is industry-specific: count menus and footers on the client set; the SaaS navigation rows here are a
reference only. Pages change: re-read a page before you quote it, and update its row when it has moved.
Every membership below was decided by hand from the pages. Scripts only count these sets. Standard library only."""

# ---------------------------------------------------------------------------------------------------------------
# 1. Hubs and the section types each one carries (ids from reference/section-types.md)
# ---------------------------------------------------------------------------------------------------------------
# name: (group, kind, hub path as read, type ids carried)
HUBS = {
    'HubSpot': ('saas', 'vendor', 'hubspot.com/comparisons', {1, 17, 29, 30, 31}),
    'Zendesk': ('saas', 'vendor', 'zendesk.com/service/comparison/', {1, 4, 5, 13, 17, 18, 29, 38, 39, 42, 44, 45}),
    'monday.com': ('saas', 'vendor', 'monday.com/alternative', {1, 3, 7, 17, 29, 38, 42, 44, 45}),
    'Asana': ('saas', 'vendor', 'asana.com/compare', {1, 17, 18, 19, 27, 29, 38, 42, 45}),
    'ClickUp': ('saas', 'vendor', 'clickup.com/compare', {1, 4, 17, 18, 29, 36, 37, 38, 42, 45}),
    'Miro': ('saas', 'vendor', 'miro.com/compare/', {1, 17, 18, 29, 45}),
    'G2': ('cross', 'marketplace', 'g2.com/compare', {1, 7, 8, 29, 30, 32, 43, 45}),
    'Capterra': ('cross', 'marketplace', 'capterra.com/compare/', {1, 5, 7, 8, 15, 16, 22, 29, 32, 36, 43, 45}),
    'Shopify': ('cross', 'vendor', 'shopify.com/compare', {1, 18, 29, 30, 31, 33, 37, 40, 42, 43, 45}),
    'Ahrefs': ('cross', 'vendor', 'ahrefs.com/vs (serves the single vs-Semrush page)', {1, 4, 17, 18, 28, 42, 43, 45}),
    'Semrush': ('cross', 'vendor', 'semrush.com/vs/', {1, 17, 18, 29, 45}),
}
N_TYPES = 45
for _n, (_g, _k, _u, _t) in HUBS.items():
    assert _t <= set(range(1, N_TYPES + 1)), _n

# Signals read on each hub that are not section types (decided by hand)
SIGNALS = {
    # a button inside the hero itself (not the site header)
    'hero_cta': {'Zendesk', 'Asana', 'ClickUp', 'Miro', 'Shopify', 'Ahrefs', 'Semrush'},
    # the H1 is a question
    'question_h1': {'Zendesk'},
    # an offer at the end of the main content
    'closing_cta': {'Zendesk', 'monday.com', 'Asana', 'ClickUp', 'Miro', 'Shopify', 'Ahrefs', 'Semrush'},
    # a comparison table that names three or more products side by side
    'table_named_multi': {'Zendesk', 'ClickUp'},
    # sources numbered in the text (type 19 also counts asterisk footnotes and single source lines)
    'numbered_sources': set(),
    # a dated statement about the comparison data or the page
    'dated': {'Zendesk', 'Asana', 'Ahrefs'},
    # each rival gets a one-line description on its card
    'card_oneliner': {'monday.com', 'Semrush'},
    # plain text links, no card content
    'plain_links': {'Miro', 'Zendesk', 'Asana', 'ClickUp'},
    # customer stories grouped by the rival the customer left
    'switcher_grouped': {'Zendesk'},
    # an alternatives index linked from the hub
    'alternatives_linked': {'monday.com', 'Miro'},
    # content that exists only in the JavaScript-rendered page (missing from the server HTML)
    'js_only_blocks': {'Capterra', 'Shopify'},
    # under about 1,000 words of main content
    'under_1000_words': {'HubSpot', 'Miro', 'Semrush', 'Ahrefs', 'G2', 'Shopify'},
}
for _k, _v in SIGNALS.items():
    assert _v <= set(HUBS), (_k, _v - set(HUBS))

# ---------------------------------------------------------------------------------------------------------------
# 2. SaaS navigation reference (10 companies; menus and footers as read)
# ---------------------------------------------------------------------------------------------------------------
SAAS_COMPANIES = [
    # name, hub path or None, status, where the site links comparisons, comparisons listed or found (approx.)
    ('HubSpot', 'hubspot.com/comparisons', 'hub', 'footer, free-tools group', 24),
    ('Zendesk', 'zendesk.com/service/comparison/', 'hub', 'footer Compare group of three vs pages', 17),
    ('monday.com', 'monday.com/alternative', 'hub', 'footer Resources > Compare', 8),
    ('Asana', 'asana.com/compare', 'hub', 'not linked', 9),
    ('ClickUp', 'clickup.com/compare', 'hub', 'footer Compare group of eleven vs pages', 24),
    ('Notion', None, 'pages_only', 'not linked', 1),
    ('Airtable', None, 'pages_only', 'not linked', 5),
    ('Webflow', None, 'pages_only', 'footer Compare group of five vs pages', 14),
    ('Intercom', None, 'pages_only', 'footer why-choose page (names no rivals)', 10),
    ('Miro', 'miro.com/compare/', 'hub', 'not linked', 26),
]
SAAS = {c[0] for c in SAAS_COMPANIES}
NAV = {
    'footer': {'HubSpot', 'monday.com', 'Zendesk', 'ClickUp', 'Webflow'},
    'footer_names_rivals': {'Zendesk', 'ClickUp', 'Webflow'},
    'not_linked': {'Asana', 'Miro', 'Notion', 'Airtable', 'Intercom'},
    'unreadable': set(),
    'top_level_compare': set(),
    'header_menu_link': set(),
    'hub_at_compare': {'Asana', 'ClickUp', 'Miro'},
    'alternatives_pages': {'HubSpot', 'Zendesk', 'monday.com', 'ClickUp', 'Airtable', 'Webflow', 'Intercom', 'Miro'},
}
for _k, _v in NAV.items():
    assert _v <= SAAS, (_k, _v - SAAS)
NAV_READ = len(SAAS) - len(NAV['unreadable'])

# ---------------------------------------------------------------------------------------------------------------
# 3. SaaS head-to-head pages (8 "<Brand> vs <Rival>" pages on the vendors' own sites)
# ---------------------------------------------------------------------------------------------------------------
VS_PAGES = [
    # key, brand, rival, format
    ('Zendesk vs Freshdesk', 'Zendesk', 'Freshdesk', 'landing'),
    ('monday.com vs Asana', 'monday.com', 'Asana', 'article'),
    ('Asana vs monday.com', 'Asana', 'monday.com', 'landing'),
    ('ClickUp vs Asana', 'ClickUp', 'Asana', 'landing'),
    ('Notion vs Confluence', 'Notion', 'Confluence', 'landing'),
    ('Airtable vs Smartsheet', 'Airtable', 'Smartsheet', 'landing'),
    ('Intercom vs Zendesk', 'Intercom', 'Zendesk', 'landing'),
    ('Webflow vs WordPress', 'Webflow', 'WordPress', 'landing'),
]
VS_ALL = {p[0] for p in VS_PAGES}
VS = {
    # offers to run alongside the rival (integration or "works with any" line)
    'coexistence': {'Intercom vs Zendesk', 'monday.com vs Asana'},
    # own brand first in the URL path
    'url_brand_first': {'Zendesk vs Freshdesk', 'Asana vs monday.com', 'Notion vs Confluence', 'Airtable vs Smartsheet',
                        'Intercom vs Zendesk'},
    'table': VS_ALL - {'Notion vs Confluence'},
    'parity_rows': {'Asana vs monday.com', 'Webflow vs WordPress', 'monday.com vs Asana'},
    'rival_strength_named': {'monday.com vs Asana'},
    'choose_if_both': {'monday.com vs Asana'},
    'attack_framing': {'Zendesk vs Freshdesk', 'Notion vs Confluence', 'Intercom vs Zendesk'},
    'switcher_proof': {'Zendesk vs Freshdesk', 'Intercom vs Zendesk', 'Notion vs Confluence'},
    'migration_block': {'Webflow vs WordPress', 'Airtable vs Smartsheet', 'Notion vs Confluence'},
    'faq': VS_ALL - {'ClickUp vs Asana'},
    'faq_switch_question': {'monday.com vs Asana', 'Asana vs monday.com',
                            'Notion vs Confluence', 'Airtable vs Smartsheet', 'Intercom vs Zendesk',
                            'Webflow vs WordPress'},
    'updated_date': {'Zendesk vs Freshdesk', 'monday.com vs Asana'},
    'author': {'monday.com vs Asana'},
    'review_ratings': {'monday.com vs Asana', 'ClickUp vs Asana'},
}
for _k, _v in VS.items():
    assert _v <= VS_ALL, (_k, _v - VS_ALL)

# ---------------------------------------------------------------------------------------------------------------
# 4. The client's own set: fill this per run (named rivals first, then category peers)
# ---------------------------------------------------------------------------------------------------------------
# name: (kind, hub path or None, status, nav as read, type ids carried, signals carried)
# status: hub | hub_unreadable | pages_only | none. Leave empty to count the public sample alone.
CLIENT_SET = {
    # 'CompetitorB': ('vendor', 'competitorb.example/compare', 'hub', 'footer Compare group', {1, 29, 45},
    #                 {'hero_cta', 'closing_cta'}),
}
# Overrides: when a hand check on the live page disagrees with a coding, change the coding and record why here.
OVERRIDES = [
    # ('CompetitorB', 'type 4', 'added', 'the table renders only with JavaScript; seen in the browser read'),
]


def all_hubs():
    """Every readable hub: public sample plus the client set (status 'hub')."""
    out = {k: (v[0], v[1], v[2], set(v[3])) for k, v in HUBS.items()}
    for k, v in CLIENT_SET.items():
        if v[2] == 'hub':
            out[k] = ('client', v[0], v[1], set(v[4]))
    return out


def signal(key):
    s = set(SIGNALS.get(key, set()))
    for k, v in CLIENT_SET.items():
        if v[2] == 'hub' and key in v[5]:
            s.add(k)
    return s


if __name__ == '__main__':
    H = all_hubs()
    print('hubs', len(H), '(public %d, client %d)' % (len(HUBS), len(H) - len(HUBS)))
    for t in range(1, N_TYPES + 1):
        carry = sorted(k for k, v in H.items() if t in v[3])
        print('%2d  %2d  %s' % (t, len(carry), ', '.join(carry)))
    print('nav read', NAV_READ, {k: len(v) for k, v in NAV.items()})
    print('vs pages', len(VS_ALL), {k: len(v) for k, v in VS.items()})
