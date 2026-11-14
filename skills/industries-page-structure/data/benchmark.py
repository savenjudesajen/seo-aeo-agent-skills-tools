# -*- coding: utf-8 -*-
"""Section-type library and block models for an industries overview page and the industry page template.

Standard library only, runs offline. Two sets, one taxonomy:

  * CROSS: the starter cross-industry set, 12 well-known companies in cloud, enterprise software, consulting and
    IT services. For each, one overview page (the industries hub, or the section of a page that lists the
    industries) and one industry page (the same industry for every company; financial services in the starter set
    because nearly every company covers it). Every membership below was decided by hand from one reading of the
    pages. Pages change: re-check any example before you cite it.
  * CLIENT: the client's own set (direct competitors plus a few leaders from the client's category). Empty in this
    file. Code it per run in CLIENT_HUBS, CLIENT_IND and CLIENT_NAV, using the same type ids, and set each block's
    status against the client's site in CLIENT_STATUS (no status is preset).

Every count the deliverable prints comes from here ("n of N", with the base named). A script never decides set
membership, it only counts. Run it to print every count with its names and to run the gate checks:

    python3 benchmark.py            # counts, block models, checks; exit code 1 on any failed check
"""
import sys

# ------------------------------------------------------------------ the starter cross-industry set ------------
CROSS = ['AWS', 'Microsoft', 'IBM', 'Oracle', 'SAP', 'Adobe', 'Deloitte', 'Accenture', 'McKinsey', 'PwC',
         'Capgemini', 'Cognizant']
GROUP = {
    'AWS': 'cloud',
    'Microsoft': 'software',
    'IBM': 'software',
    'Oracle': 'software',
    'SAP': 'software',
    'Adobe': 'software',
    'Deloitte': 'consulting',
    'Accenture': 'consulting',
    'McKinsey': 'consulting',
    'PwC': 'consulting',
    'Capgemini': 'consulting',
    'Cognizant': 'IT services',
}
# where the pages were found (host and path; check for redirects before reuse)
HUB_PAGE = {
    'AWS': 'aws.amazon.com/industries',
    'Microsoft': 'microsoft.com/en-us/ai (an industry carousel on a broader page)',
    'IBM': 'ibm.com/industries',
    'Oracle': 'oracle.com/industries',
    'SAP': 'sap.com/industries.html',
    'Adobe': 'business.adobe.com/industries/adobe-industries.html',
    'Deloitte': 'deloitte.com/us/en/industries.html',
    'Accenture': 'accenture.com/en/services (an industries section on a services page)',
    'McKinsey': 'mckinsey.com/industries',
    'PwC': 'pwc.com/us/en/industries.html',
    'Capgemini': 'capgemini.com/industries',
    'Cognizant': 'cognizant.com/us/en/industries',
}
IND_PAGE = {
    'AWS': 'aws.amazon.com/financial-services',
    'Microsoft': 'microsoft.com/en-us/ai/financial-services',
    'IBM': 'ibm.com/industries/banking-financial-markets',
    'Oracle': 'oracle.com/financial-services',
    'SAP': 'sap.com/industries/financial-services.html',
    'Adobe': 'business.adobe.com/industries/financial-services.html',
    'Deloitte': 'deloitte.com/us/en/industries/financial-services/about.html',
    'Accenture': 'accenture.com/en/industries/banking',
    'McKinsey': 'mckinsey.com/industries/financial-services/how-we-help-clients',
    'PwC': 'pwc.com/us/en/industries/financial-services.html',
    'Capgemini': 'capgemini.com/industries/banking-and-capital-markets',
    'Cognizant': 'cognizant.com/us/en/industries/banking-technology-solutions',
}
ALL12 = frozenset(CROSS)

# ------------------------------------------------------------------ the taxonomy (45 section types) ------------
# id: (name, overview pages with it, industry pages with it, best example (company, page, what it does),
#      what it gives buyers, what it gives AI answers, where it lands in the default block model)
# Types 36 and 41 are kept as ids so client codings stay comparable, but no page in the starter set carries them:
# their best example is None and they count as open ground.
# Best-example notes are paraphrases of what the page does, never its copy.
TYPES = {
    1: ('Hero (H1, one-line promise, button)', ALL12, ALL12,
        ('SAP', 'industry page', 'the line under the H1 names the four buyer types the page serves'),
        'confirmation they are in the right place', 'a one-line scope statement, best when it names the buyer types',
        'Hero (both pages)'),
    2: ('Announcement banner (event, report, news)', {'Microsoft', 'IBM'}, {'Microsoft', 'IBM', 'SAP'},
        ('IBM', 'overview page', 'runs its newest flagship report as a site banner with one headline figure'),
        'the newest report or event', 'a dated report name with a headline figure', 'Announcement banner (site-wide)'),
    3: ('In-page navigation (jump links, sticky local menu, index, breadcrumb, filters, tabs)',
        {'Microsoft', 'IBM', 'Oracle', 'SAP', 'Accenture', 'PwC', 'Capgemini', 'Cognizant'},
        {'AWS', 'IBM', 'Oracle', 'SAP', 'Adobe', 'Accenture', 'PwC', 'Capgemini', 'Cognizant'},
        ('PwC', 'industry page', 'puts an index of six anchor links beside the H1'),
        'a jump to what they need on a long page', 'explicit page structure and clean anchors to cite',
        'Jump navigation (both pages)'),
    4: ('Industry list without descriptions', {'Oracle', 'SAP', 'Capgemini'}, set(),
        ('Oracle', 'overview page', 'an A to Z list of about twenty industry links, nothing else per item'),
        'a fast A to Z pick', 'a list of industries only', 'Industry directory (each entry carries a line instead)'),
    5: ('Industry cards with a one-line value, scope or challenge statement',
        {'AWS', 'Microsoft', 'IBM', 'Adobe', 'Deloitte', 'Accenture', 'McKinsey', 'PwC', 'Cognizant'}, set(),
        ('Accenture', 'overview page', 'opens every industry entry with a challenge line in that industry\'s terms'),
        'each industry framed in its own terms before the click', 'a quotable one-sentence description per industry',
        'Industry directory'),
    6: ('Coverage statement with a number', {'Oracle', 'Deloitte'}, set(),
        ('Deloitte', 'overview page', 'states how many industries and sectors it covers, then names the sectors on '
                                      'each card'),
        'the size of the taxonomy at a glance', 'a countable, citable scope fact',
        'Industry directory (coverage count)'),
    7: ('Sub-industry or segment navigation', {'Microsoft'},
        {'AWS', 'Microsoft', 'Oracle', 'Deloitte', 'Accenture', 'McKinsey', 'PwC', 'Capgemini', 'Cognizant'},
        ('AWS', 'industry page', 'a segments row with one page per segment'),
        'a route straight to their segment', 'the segments served, each with its own address to cite',
        'Segment links (industry page)'),
    8: ('Second way in on the overview (capabilities, cross-industry processes, products by job)',
        {'Microsoft', 'SAP', 'Accenture'}, set(),
        ('SAP', 'overview page', 'cross-industry process pages, each with a one-line outcome, beside the vertical '
                                 'list'),
        'a way to browse by problem instead of vertical', 'process names with one-line definitions',
        'Second route in (overview)'),
    9: ('Why us, value pillars, differentiators', {'AWS', 'IBM', 'Oracle'}, {'AWS', 'Microsoft', 'SAP'},
        ('AWS', 'industry page', 'four benefit statements in the body of the page, each a short paragraph'),
        'the case for the vendor in a few lines', 'a named list of differentiators', 'Why the company (overview)'),
    10: ('Industry challenge statement or sector point of view', set(),
         {'IBM', 'Adobe', 'Deloitte', 'Accenture', 'PwC', 'Capgemini', 'Cognizant'},
         ('Deloitte', 'industry page', 'names the forces reshaping the industry before it says what it does'),
         'their own problem named first', 'a list of forces reshaping the industry, a quotable thesis',
         'Answers per industry (overview), point of view (industry page)'),
    11: ('Use cases or business priorities (tabs or cards, each with its answer)', set(),
         {'IBM', 'SAP', 'Adobe', 'Accenture'},
         ('IBM', 'industry page', 'each business priority pairs a problem paragraph with the one asset that answers '
                                  'it (webinar, guide or report)'),
         'the priority that matches their project', 'problem-to-solution pairs',
         'Priorities and capabilities (industry page)'),
    12: ('Solution and product mapping for the industry', set(),
         {'AWS', 'Microsoft', 'IBM', 'Oracle', 'SAP', 'Deloitte', 'Capgemini', 'Cognizant'},
         ('Oracle', 'industry page', 'line-of-business tabs, each listing sub-solutions in two or three plain '
                                     'sentences'),
         'which product fits which job', 'definitional product descriptions per need',
         'Priorities and capabilities (industry page)'),
    13: ('Full product index for the industry (A to Z)', set(), {'Oracle'},
         ('Oracle', 'industry page', 'a product directory grouped by solution and sector'),
         'a complete finder', 'complete named coverage of the portfolio',
         'Not used unless the portfolio has many products per industry'),
    14: ('Partner ecosystem by industry (named partners, marketplace listings)', {'Accenture'},
         {'AWS', 'Microsoft', 'SAP', 'Capgemini'},
         ('Microsoft', 'industry page', 'named partners, each mapped to one job in the industry'),
         'the vendors they already use', 'partner-to-use-case pairs', 'Partners (industry page)'),
    15: ('Customer logo strip (logos only)', {'Oracle'}, {'Oracle', 'SAP'},
         ('Oracle', 'industry page', 'a logo carousel with no quote or number'),
         'recognisable peer names', 'names only, weak evidence', 'Not used: logos alone are weak evidence'),
    16: ('Case study cards (headline and teaser)', {'Microsoft', 'IBM', 'PwC'},
         {'AWS', 'Microsoft', 'IBM', 'Adobe', 'Deloitte', 'Accenture', 'McKinsey', 'PwC', 'Capgemini', 'Cognizant'},
         ('AWS', 'industry page', 'story cards with the outcome in each headline'),
         'peers and what they achieved', 'named customer and outcome pairs',
         'Stories (overview), proof (industry page)'),
    17: ('Customer outcome metrics shown as numbers', {'Microsoft', 'IBM'},
         {'Microsoft', 'IBM', 'Adobe', 'Deloitte', 'PwC', 'Capgemini', 'Cognizant'},
         ('Adobe', 'industry page', 'one bold metric under each of six customer logos, across the industry\'s '
                                    'segments'),
         'proof they can repeat internally', 'numeric outcomes tied to named firms',
         'Proof beside the answer (overview), proof (industry page)'),
    18: ('Named customer quote (name and title)', set(), {'Microsoft', 'Adobe'},
         ('Microsoft', 'industry page', 'each story card carries a quote, the speaker\'s title, one or two results '
                                        'and the products used'),
         'a peer\'s voice', 'attributable quotes', 'Stories (overview), proof (industry page)'),
    19: ('Video (overview, customer or executive spotlight)', {'AWS', 'SAP'}, {'AWS', 'Microsoft', 'IBM', 'SAP'},
         ('AWS', 'industry page', 'an executive customer spotlight video from a large customer in the industry'),
         'a customer in their own words', 'little text; the heading and caption carry the citable part',
         'Optional: only when an industry video exists'),
    20: ('Industry-firsts proof narrative', {'AWS'}, set(),
         ('AWS', 'overview page', 'one paragraph of named firsts across industries, with no logo wall'),
         'cross-industry credibility in one paragraph', 'named, dated milestones', 'Why the company (overview)'),
    21: ('Vendor scale statistics (solutions, partners, years, regions)', {'AWS', 'SAP', 'Accenture'},
         {'AWS', 'Oracle', 'Capgemini'},
         ('AWS', 'overview page', 'two scale numbers (solutions and industry partners) in the first body section'),
         'a sense of depth', 'countable facts about the vendor', 'Proof beside the answer (overview)'),
    22: ('State-of-the-industry statistic strip', set(), {'Oracle', 'Accenture'},
         ('Accenture', 'industry page', 'four industry figures at the top of the page'),
         'the industry in numbers', 'quotable figures, citable only when sourced and current',
         'Answers per industry (overview), point of view (industry page)'),
    23: ('Third-party-sourced statistics (source named per figure)', set(), {'Adobe'},
         ('Adobe', 'industry page', 'three adoption figures, each with a named external source, one of them dated'),
         'trust in the numbers', 'figures with a named source and date, the most citable format seen',
         'Answers per industry (overview), point of view (industry page)'),
    24: ('Analyst recognition and awards', {'IBM', 'Accenture'}, {'Oracle', 'Accenture', 'Capgemini', 'Cognizant'},
         ('Accenture', 'industry page', 'recognition specific to the industry\'s sub-markets, each with firm, '
                                        'report, year, placement and field size'),
         'third-party validation', 'firm, report, year and placement in one line',
         'Recognition (overview), proof (industry page)'),
    25: ('Resource library cards (typed: report, guide, e-book, webinar, blog)', {'AWS', 'Microsoft', 'IBM', 'PwC'},
         ALL12,
         ('Capgemini', 'industry page', 'research cards labelled by kind (point of view, research, report) with a '
                                        'link to all insights for the industry'),
         'self-education by format', 'report titles; open PDFs are citable, gated ones are not',
         'Research, outlooks and events'),
    26: ('Year-labelled industry outlook or trends report', {'Microsoft', 'IBM', 'PwC'},
         {'AWS', 'IBM', 'Deloitte', 'Accenture', 'PwC', 'Capgemini'},
         ('Deloitte', 'industry page', 'a year-labelled outlook for every sector, plus annual predictions'),
         'current, sector-specific thinking', 'dated research answer engines cite for trend questions',
         'Research, outlooks and events'),
    27: ('Research with stated sample size or method', set(), {'PwC'},
         ('PwC', 'industry page', 'a survey card that states both of its sample sizes in the description'),
         'a way to judge the evidence', 'a figure with its sample, which raises citation confidence',
         'Research, outlooks and events (sample and method line)'),
    28: ('Industry events (conference, forum, webinar, dated)', {'Microsoft', 'IBM', 'Oracle'},
         {'IBM', 'SAP', 'Accenture'},
         ('Accenture', 'industry page', 'an event card that gives the event\'s dates and venue'),
         'where to meet the team', 'event name, dates and place', 'Research, outlooks and events'),
    29: ('Named experts (leader cards with titles and contacts, bylined series, interviews)', set(),
         {'Deloitte', 'Accenture', 'McKinsey', 'PwC', 'Capgemini', 'Cognizant'},
         ('Deloitte', 'industry page', 'sector leaders with title, legal entity and direct contact routes'),
         'a real person to talk to', 'named experts with titles, strong authorship signals', 'People'),
    30: ('Visible publication dates on content cards', set(), {'McKinsey', 'Capgemini'},
         ('McKinsey', 'industry page', 'dates on its featured insight and case study cards'),
         'proof the content is current', 'a freshness signal on each cited item',
         'Research, outlooks and events (every card dated)'),
    31: ('Named regulations, standards or certifications', set(), {'Microsoft', 'Oracle', 'SAP'},
         ('Microsoft', 'industry page', 'a full-width band on one named regulation'),
         'a direct answer to "do you support X"', 'exact regulation and certification names', 'Trust and standards'),
    32: ('Security, compliance and trust block', {'Microsoft'}, {'Microsoft', 'IBM', 'SAP'},
         ('Microsoft', 'industry page', 'a security and compliance block on the industry page'),
         'reassurance plus links to evidence', 'trust claims with links to compliance evidence', 'Trust and standards'),
    33: ('FAQ', {'Microsoft'}, {'SAP'},
         ('SAP', 'industry page', 'seven questions, one or two sentence answers, links to trust evidence'),
         'quick answers to standard objections', 'extractable question and answer pairs in buyer phrasing', 'FAQ'),
    34: ('On-page AI assistant with suggested questions', {'Microsoft'}, set(),
         ('Microsoft', 'overview page', 'an ask box with two suggested questions'),
         'ask instead of browse', 'little (answers live in the widget); the suggested questions show intended queries',
         'Optional: suggested questions for an AI assistant'),
    35: ('Interactive tool (calculator, explorer, lookup)', set(), {'IBM'},
         ('IBM', 'industry page', 'an ROI calculator offered as a card in the research row'),
         'a personalised number or answer', 'little on the page; the tool page itself may be cited',
         'Not used at launch unless a tool exists'),
    36: ('Reference architectures or deployable templates', set(), set(),
         None,
         'a technical map of how it fits', 'use-case names and architecture layers on the tool page',
         'Not used: not seen on the starter set (add it only when technical buyers expect architectures)'),
    37: ('Named methodology or playbook', {'Oracle'}, {'Deloitte'},
         ('Oracle', 'overview page', 'industry playbooks framed as planning standards and tools'),
         'a structured way to plan', 'a named method to reference', 'Not used unless the client has a named method'),
    38: ('Innovation labs or studios', {'IBM', 'Oracle'}, set(),
         ('Oracle', 'overview page', 'physical industry lab sites where customers test solutions'),
         'a place to test before buying', 'that physical labs exist', 'Not used unless the client runs labs'),
    39: ('Proprietary benchmarks and data products', set(), {'McKinsey'},
         ('McKinsey', 'industry page', 'named benchmarking and data products with plain one-line definitions'),
         'a way to compare themselves to peers', 'named benchmark products with definitions',
         'Not used unless the client sells benchmark or data products'),
    40: ('Product road map by industry', set(), {'SAP'},
         ('SAP', 'industry page', 'public product road maps, one per segment, in the get-started block'),
         'what is coming', 'links that answer road map questions', 'Not used unless a public road map exists'),
    41: ('Free trials and offers', set(), set(),
         None,
         'a way to try before buying', 'little',
         'Not used: not seen on the starter set (the offer belongs in the closing band)'),
    42: ('Newsletter subscription (industry intelligence)', {'IBM', 'PwC'}, {'Deloitte', 'PwC'},
         ('PwC', 'overview page', 'an industry-intelligence subscription framed around what is coming for the '
                                  'reader\'s industry'),
         'ongoing updates for their sector', 'none', 'Closing band (newsletter option)'),
    43: ('Contact and next steps (closing button, multi-path next steps, phone or RFP shortcuts)',
         {'AWS', 'Microsoft', 'IBM', 'Adobe', 'McKinsey', 'Capgemini', 'Cognizant'},
         {'AWS', 'Microsoft', 'IBM', 'SAP', 'Adobe', 'Deloitte', 'McKinsey', 'PwC', 'Capgemini', 'Cognizant'},
         ('Microsoft', 'industry page', 'next steps that route to responsible-use principles, a trust portal and '
                                        'documentation, not only to sales'),
         'a next step matched to their stage', 'little', 'Closing band'),
    44: ('Cross-links to other site sections (services, alliances, governance, careers)',
         {'IBM', 'Deloitte', 'Accenture', 'McKinsey'}, {'Accenture'},
         ('McKinsey', 'overview page', 'links to the firm\'s history and its client service policies'),
         'related routes, governance transparency', 'little', 'Closing band (related links)'),
    45: ('Page feedback widget', {'SAP'}, {'SAP'},
         ('SAP', 'industry page', 'a page feedback prompt at the foot of the page'),
         'a voice of customer channel', 'none', 'Not used: a site-wide feature, not a page section'),
}
# widgets are site features, not sections: an assistant launcher was seen on these pages (not counted)
ASSISTANT_WIDGET = {'hub': {'AWS', 'IBM', 'McKinsey'}, 'ind': {'AWS', 'IBM', 'McKinsey'}}

# ------------------------------------------------------------------ derived sets, decided by hand ---------------
# a button in the overview hero (a jump link or no button does not count)
HERO_BUTTON = {'AWS', 'Microsoft', 'IBM'}
# no page in the starter set shows a page date, a named reviewer or an author line (McKinsey dates content cards)
BYLINE = (set(), set())

# ------------------------------------------------------------------ the client set (fill per run) ---------------
# company -> set of type ids seen on its overview page / its industry page (same taxonomy, coded by hand)
CLIENT_HUBS = {}
CLIENT_IND = {}
# company -> navigation facts read on its live site (menus and footers are counted on the client set only)
#   menu: 'under_solutions' | 'top_level' | 'under_product' | 'other_parent' | 'not_in_menu' | 'unreadable'
#   footer_group: True when industries have their own footer group
#   all_link: True when the menu links an all-industries page
#   lists_differ: True when the menu and the overview page list different industries
#   parent: 'live' | 'broken' (404, empty shell, placeholder template or redirect to another page) | 'none'
#   presentation: 'hub' | 'section' (part of another page) | 'menu_only' | 'pages_no_hub' | 'orphan' | 'none'
CLIENT_NAV = {}
# derived sets for the client set, decided by hand like HERO_BUTTON
CLIENT_HERO_BUTTON = set()
CLIENT_BYLINE = (set(), set())
# block key -> status against the client's live site today. Empty on purpose: never preset a status, set each one
# per client (Keep, New, Rework, Optional, Later). Keys are the block keys in OVERVIEW, SITE and TEMPLATE.
CLIENT_STATUS = {}


# ------------------------------------------------------------------ helpers ---------------------------------------
def hubs(*ids):
    """(client set, cross set) of overview pages that carry any of the types."""
    c, x = set(), set()
    for i in ids:
        x |= set(TYPES[i][1])
        c |= {k for k, v in CLIENT_HUBS.items() if i in v}
    return c, x


def inds(*ids):
    """(client set, cross set) of industry pages that carry any of the types."""
    c, x = set(), set()
    for i in ids:
        x |= set(TYPES[i][2])
        c |= {k for k, v in CLIENT_IND.items() if i in v}
    return c, x


def cnt(pair):
    return len(pair[0]) + len(pair[1])


N_HUB = len(CROSS) + len(CLIENT_HUBS)
N_IND = len(CROSS) + len(CLIENT_IND)


def of_hub(pair):
    return '%d of %d' % (cnt(pair), N_HUB)


def of_ind(pair):
    return '%d of %d' % (cnt(pair), N_IND)


def names(pair):
    order = list(CLIENT_HUBS) + list(CLIENT_IND) + CROSS
    s = pair[0] | pair[1]
    seen, out = set(), []
    for x in order:
        if x in s and x not in seen:
            out.append(x)
            seen.add(x)
    return out


# derived pairs used by the block models
HERO_CTA = (set(CLIENT_HERO_BUTTON), set(HERO_BUTTON))
PROOF_TYPES = (15, 16, 17, 18, 20, 21, 24)            # proof of any kind on an overview page
PROOF_ANY = hubs(*PROOF_TYPES)


def nav_count(key, value=True):
    """Companies in the client set whose CLIENT_NAV[key] equals value, and the readable base."""
    base = [k for k, v in CLIENT_NAV.items() if v.get('menu') != 'unreadable' or key != 'menu']
    hit = [k for k in base if CLIENT_NAV[k].get(key) == value]
    return hit, len(base)


# ------------------------------------------------------------------ block models ----------------------------------
# A starting grouping, not a template to copy: merge, split or reorder blocks for the client and say why.
STATUSES = ['Keep', 'New', 'Rework', 'Optional', 'Later']
ZONES = ['Top of page', 'Find your industry', 'Answers per industry', 'Evidence', 'Questions and trust', 'Next step']

# Overview page: key, zone, block, counted on overview pages, counted on industry pages (or None), best examples,
# notes. "Counted" is a tuple of type ids or a derived pair name ('HERO_CTA', 'PROOF_ANY', 'BYLINE'). An example
# marked "(industry page)" is checked against the industry page set. Notes: (label, counted, 'hub' | 'ind').
OVERVIEW = [
    ('o_answer', 'Top of page', 'Hero: H1, a 40 to 60 word answer naming the industries served, one button',
     (1,), None, ['SAP (industry page)', 'IBM'], [('with a button', 'HERO_CTA', 'hub')]),
    ('o_proof', 'Top of page', 'Proof beside the answer: scale figures, results or a recognition, each sourced',
     'PROOF_ANY', None, ['AWS', 'IBM'], []),
    ('o_directory', 'Find your industry', 'Industry directory: a coverage count, then one entry per industry with a '
     'line in its own vocabulary', (4, 5, 6), None, ['Deloitte', 'AWS', 'Accenture'],
     [('give each industry a line', (5,), 'hub'), ('state a coverage number', (6,), 'hub')]),
    ('o_route', 'Find your industry', 'A second route in, by problem, process or job', (8,), None,
     ['SAP', 'Microsoft'], []),
    ('o_jump', 'Find your industry', 'Jump navigation: breadcrumb and a sticky bar of anchors', (3,), None,
     ['PwC', 'Microsoft'], []),
    ('o_answers', 'Answers per industry', 'One open, anchored block per industry: challenge, question-shaped H2, '
     'answer, a sourced figure, standards, proof, link', (10, 22, 23), (10, 22, 23),
     ['Deloitte (industry page)', 'Adobe (industry page)'], []),
    ('o_why', 'Answers per industry', 'Why the company: differentiators or a paragraph of named firsts', (9, 20), None,
     ['AWS', 'Oracle'], []),
    ('o_stories', 'Evidence', 'Stories and results tagged by industry', (16, 18), None, ['Microsoft', 'IBM'], []),
    ('o_research', 'Evidence', 'Research, outlooks and events: typed, dated cards per industry', (25, 26, 27, 28, 30),
     None, ['PwC', 'IBM'], []),
    ('o_recognition', 'Evidence', 'Recognition: firm, report, year and placement', (24,), (24,),
     ['IBM', 'Accenture'], []),
    ('o_faq', 'Questions and trust', 'FAQ in the buyer\'s words, answers in the HTML', (33,), (33,),
     ['Microsoft', 'SAP (industry page)'], []),
    ('o_trust', 'Questions and trust', 'Trust and standards: a line with links to the evidence', (31, 32), (31, 32),
     ['Microsoft', 'SAP (industry page)'], []),
    ('o_people', 'Questions and trust', 'People: named industry leads, and a Reviewed by line with date and sources',
     (29,), (29,), ['Deloitte (industry page)'], [('show a reviewer or page date', 'BYLINE', 'ind')]),
    ('o_ask', 'Questions and trust', 'Suggested questions for an AI assistant', (34,), None, ['Microsoft'], []),
    ('o_close', 'Next step', 'Closing band: the one offer, a newsletter option, related links', (41, 42, 43, 44),
     None, ['AWS', 'McKinsey'], []),
]

# Site-wide elements, specified with the navigation: key, element, counted, best examples
SITE = [
    ('s_banner', 'Announcement banner pointed at the newest research or event', (2,), ['IBM']),
    ('s_menu', 'Menu: a By industry group (under Solutions unless the launch list is long), ending with All '
     'industries', 'nav:menu', []),
    ('s_footer', 'Footer: an Industries group with the same pages in the same order', 'nav:footer_group', []),
]

# Industry page template: key, block, counted on industry pages, best examples, notes
TEMPLATE = [
    ('t_hero', 'Hero: industry H1, a 30 to 40 word answer naming the buyer types, button', (1,), ['SAP'], []),
    ('t_jump', 'Jump navigation', (3,), ['PwC', 'Adobe'], []),
    ('t_segments', 'Segment links, a page per segment', (7,), ['AWS', 'Microsoft'], []),
    ('t_pov', 'Point of view: the industry\'s challenge, with sourced figures', (10, 22, 23), ['Deloitte', 'Adobe'],
     [('with a named source for every figure', (23,), 'ind')]),
    ('t_jobs', 'Priorities mapped to capabilities, each with a matching resource', (11, 12), ['IBM', 'Oracle'], []),
    ('t_standards', 'Standards, regulations and trust evidence', (31, 32), ['Microsoft', 'SAP'], []),
    ('t_partners', 'Partners mapped to industry jobs', (14,), ['Microsoft'], []),
    ('t_proof', 'Proof: stories, results, quotes and recognition', (16, 17, 18, 24), ['Microsoft', 'Adobe'], []),
    ('t_research', 'Research, outlooks and events for the industry, dated', (25, 26, 27, 28, 30),
     ['McKinsey', 'Deloitte'], []),
    ('t_people', 'People: the industry lead, and a Reviewed by line with sources', (29,), ['Deloitte'],
     [('show a reviewer', 'BYLINE', 'ind')]),
    ('t_faq', 'FAQ for the industry', (33,), ['SAP'], []),
    ('t_close', 'Closing band with two sibling industries', (41, 42, 43), ['Microsoft', 'AWS'], []),
]


def pair_for(counted, page):
    """The (client, cross) pair behind a count. page is 'hub' or 'ind'."""
    if isinstance(counted, tuple):
        return hubs(*counted) if page == 'hub' else inds(*counted)
    if counted == 'HERO_CTA':
        return HERO_CTA
    if counted == 'PROOF_ANY':
        return PROOF_ANY
    if counted == 'BYLINE':
        return (set(CLIENT_BYLINE[0]), set(BYLINE[0])) if page == 'hub' else (set(CLIENT_BYLINE[1]), set(BYLINE[1]))
    return None


def count_cell(counted, page):
    """'n of N' for one base; nav counts read the client set."""
    if isinstance(counted, str) and counted.startswith('nav:'):
        key = counted[4:]
        if not CLIENT_NAV:
            return 'counted on the client set'
        if key == 'menu':
            hit, base = nav_count('menu', 'under_solutions')
            return '%d of %d menus put industries under Solutions' % (len(hit), base)
        hit, base = nav_count(key, True)
        return '%d of %d menus' % (len(hit), base)
    pair = pair_for(counted, page)
    if cnt(pair) == 0:
        return 'None of %d' % (N_HUB if page == 'hub' else N_IND)
    return of_hub(pair) if page == 'hub' else of_ind(pair)


def _notes(notes):
    parts = []
    for label, counted, page in notes:
        n = cnt(pair_for(counted, page))
        parts.append('%s %s' % ('none' if n == 0 else n, label))
    return ' (%s)' % ', '.join(parts) if parts else ''


def overview_cell(r):
    """The 'pages with it' cell of an overview block: overview pages, plus industry pages when counted."""
    out = count_cell(r[3], 'hub') + ' overview pages'
    if r[4] is not None:
        out += ', ' + count_cell(r[4], 'ind').replace('None of', 'none of') + ' industry pages'
    return out + _notes(r[6])


def template_cell(r):
    """The 'industry pages with it' cell of a template block."""
    return count_cell(r[2], 'ind') + _notes(r[4])


def _label(n):
    return 'Common' if n >= 6 else 'Less common' if n >= 2 else 'Rare' if n == 1 else 'Not seen'


def prevalence(r):
    """Prevalence label from the public sample only: Common 6+ of 12, Less common 2 to 5, Rare 1, Not seen 0."""
    if r in TEMPLATE:
        return _label(len(pair_for(r[2], 'ind')[1]))
    h = len(pair_for(r[3], 'hub')[1])
    if h == 0:
        return 'Not seen on overview pages'
    i = len(pair_for(r[4], 'ind')[1]) if r[4] is not None else 0
    return _label(max(h, i))


def tally(keys):
    """Status counts for the given block keys, from CLIENT_STATUS (blocks with no status yet are left out)."""
    out = {}
    for k in keys:
        s = CLIENT_STATUS.get(k)
        if s:
            out[s] = out.get(s, 0) + 1
    return out


# ------------------------------------------------------------------ gate checks -----------------------------------
def _pool(counted, page):
    if counted is None or (isinstance(counted, str) and counted.startswith('nav:')):
        return set()
    pair = pair_for(counted, page)
    return pair[0] | pair[1]


def _bad_examples(examples, hub_counted, ind_counted):
    bad = []
    for ex in examples:
        if ex.endswith(' (industry page)'):
            co = ex[:-len(' (industry page)')]
            spec = ind_counted if ind_counted is not None else hub_counted
            if co not in _pool(spec, 'ind'):
                bad.append(ex)
        elif ex not in _pool(hub_counted, 'hub'):
            bad.append(ex)
    return bad


def check():
    errs = []
    if set(TYPES) != set(range(1, 46)):
        errs.append('type ids must run 1 to 45')
    for tid, t in TYPES.items():
        for s in (t[1], t[2]):
            bad = set(s) - ALL12
            if bad:
                errs.append('type %d: not in the cross set: %s' % (tid, sorted(bad)))
        if t[3] is None:                            # a type no page in the starter set carries
            if t[1] or t[2] or not t[6].startswith('Not used'):
                errs.append('type %d: no best example, so it must be on no page and be "Not used"' % tid)
            continue
        co, page = t[3][0], t[3][1]
        pool = t[1] if page == 'overview page' else t[2]
        if co not in pool:
            errs.append('type %d: best example %s is not in its %s set' % (tid, co, page))
        if not t[6]:
            errs.append('type %d: lands nowhere and has no "Not used" reason' % tid)
    for co, v in list(CLIENT_HUBS.items()) + list(CLIENT_IND.items()):
        bad = set(v) - set(TYPES)
        if bad:
            errs.append('client coding %s: unknown type ids %s' % (co, sorted(bad)))
    keys = [r[0] for r in OVERVIEW] + [r[0] for r in SITE] + [r[0] for r in TEMPLATE]
    if len(set(keys)) != len(keys):
        errs.append('duplicate block keys')
    for k, s in CLIENT_STATUS.items():
        if k not in keys:
            errs.append('CLIENT_STATUS: unknown block key %s' % k)
        if s not in STATUSES:
            errs.append('CLIENT_STATUS: unknown status %s for %s' % (s, k))
    # every type is counted by a block, or its Lands says Not used / Optional
    counted = set(PROOF_TYPES)
    for r in OVERVIEW:
        for c in (r[3], r[4]):
            if isinstance(c, tuple):
                counted |= set(c)
    for r in SITE:
        if isinstance(r[2], tuple):
            counted |= set(r[2])
    for r in TEMPLATE:
        if isinstance(r[2], tuple):
            counted |= set(r[2])
    for tid, t in TYPES.items():
        if tid not in counted and not t[6].startswith(('Not used', 'Optional')):
            errs.append('type %d lands in "%s" but no block counts it' % (tid, t[6]))
    # every best example named in a block is in that block's set
    for r in OVERVIEW:
        if r[1] not in ZONES:
            errs.append('overview block %s: unknown zone %s' % (r[0], r[1]))
        bad = _bad_examples(r[5], r[3], r[4])
        if bad:
            errs.append('overview block %s: %s not in its set' % (r[0], bad))
    for r in SITE:
        bad = _bad_examples(r[3], r[2], None)
        if bad:
            errs.append('site element %s: %s not in its set' % (r[0], bad))
    for r in TEMPLATE:
        bad = [x for x in r[3] if x not in _pool(r[2], 'ind')]
        if bad:
            errs.append('template block %s: %s not in its set' % (r[0], bad))
    return errs


def leaderboard():
    """Companies ranked by how many types they are the named best example for, then types carried."""
    best = {}
    for t in TYPES.values():
        if t[3] is not None:
            best[t[3][0]] = best.get(t[3][0], 0) + 1
    rows = []
    for co in CROSS:
        nh = sum(1 for t in TYPES.values() if co in t[1])
        ni = sum(1 for t in TYPES.values() if co in t[2])
        rows.append((co, GROUP[co], best.get(co, 0), nh, ni))
    return sorted(rows, key=lambda r: (-r[2], -(r[3] + r[4]), r[0]))


if __name__ == '__main__':
    print('Base: %d overview pages and %d industry pages (cross-industry %d + client %d / %d)'
          % (N_HUB, N_IND, len(CROSS), len(CLIENT_HUBS), len(CLIENT_IND)))
    print('\nSECTION TYPES')
    for tid, t in TYPES.items():
        h, i = hubs(tid), inds(tid)
        print('%2d %-62s overview %-9s industry %-9s | %s' % (tid, t[0][:62], of_hub(h), of_ind(i), t[6]))
    print('\nOVERVIEW BLOCKS (status from CLIENT_STATUS; - = not set yet)')
    for n, r in enumerate(OVERVIEW, 1):
        print('%2d %-20s %-8s %-60s | %s | %s | %s' % (n, r[1], CLIENT_STATUS.get(r[0], '-'), r[2][:60],
                                                     overview_cell(r), prevalence(r), ', '.join(r[5])))
    print(tally([r[0] for r in OVERVIEW]))
    print('\nSITE-WIDE')
    for r in SITE:
        print('   %-8s %-60s | %s | %s' % (CLIENT_STATUS.get(r[0], '-'), r[1][:60],
                                         count_cell(r[2], 'hub'), ', '.join(r[3])))
    print('\nTEMPLATE BLOCKS')
    for n, r in enumerate(TEMPLATE, 1):
        print('%2d %-8s %-60s | %s | %s | %s' % (n, CLIENT_STATUS.get(r[0], '-'), r[1][:60], template_cell(r),
                                                prevalence(r), ', '.join(r[3])))
    print(tally([r[0] for r in TEMPLATE]))
    print('\nDERIVED: hero button %s, proof of any kind %s, industry figures on industry pages %s'
          % (of_hub(HERO_CTA), of_hub(PROOF_ANY), of_ind(inds(22, 23))))
    print('\nLEADERBOARD (best example for n types; types carried overview / industry page)')
    for r in leaderboard():
        print('  %-13s %-11s best for %d | %2d / %2d' % r)
    errs = check()
    print('\nCHECKS: %s' % ('PASS' if not errs else 'FAIL'))
    for e in errs:
        print('  - ' + e)
    sys.exit(1 if errs else 0)
