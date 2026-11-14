"""Answer types, content types, page kinds, KPIs, defaults and the page-check parser: the one place the gate scripts read
them from. Python standard library only. Imported by verify_tracked_set.py, prompt_audit.py, ground_check.py,
run_gates.py and verify_workbook_hygiene.py; their messages are built from these names.

reference/intent-format-kpi.md states the same rules in prose; when one changes, the other changes with it.
"""
import collections
import re

# The nine answer types, in the order the three decision questions reach them (display names).
ANSWER_TYPE_NAMES = ('Destination', 'Transact', 'Contrast', 'Specifics', 'Shortlist', 'Solutions', 'Steps', 'Fit', 'Concept')
ANSWER_TYPES = tuple(n.lower() for n in ANSWER_TYPE_NAMES)
EXPLAINING = frozenset({'concept', 'fit', 'steps'})
PROVIDER_NAMING = frozenset(ANSWER_TYPES) - EXPLAINING

# KPIs. The default per answer type; Evidence mention is allowed silently on an explaining row (its prompt asks for proof
# or real examples the client holds first-hand) and is never a default.
KPI_NAMES = ('Mention', 'Citation', 'Evidence mention')
KPIS = frozenset(k.lower() for k in KPI_NAMES)
KPI_DEFAULT = {t: ('citation' if t in EXPLAINING else 'mention') for t in ANSWER_TYPES}
CITATION_KPIS = KPIS - {'mention'}

# Stage, decided by who does the work.
STAGE_NAMES = ('Awareness', 'Consideration', 'Decision')
STAGES = frozenset(s.lower() for s in STAGE_NAMES)

# The six content types and the page kinds they fall into. A Listicle is a list page, never a selling page.
CONTENT_TYPE_NAMES = ('Guide', 'Glossary', 'Research Post', 'Listicle', 'Service Page', 'Product Page')
CONTENT_TYPES = frozenset(c.lower() for c in CONTENT_TYPE_NAMES)
SELLING = frozenset({'service page', 'product page'})
LIST_PAGE = frozenset({'listicle'})
GUIDE = frozenset({'guide', 'research post'})
GLOSSARY = frozenset({'glossary'})
INFORMS = GUIDE | GLOSSARY

# Rows a provider-shortlist set simulates by design (the grounding floor waiver may apply).
FLOOR_WAIVER_NAMES = ('Shortlist', 'Contrast', 'Destination')   # the order the docs state it in
FLOOR_WAIVER = frozenset(n.lower() for n in FLOOR_WAIVER_NAMES)

# The page check: the trailing "(<check>)" of the 'Answer shape and page check' cell, nothing else.
PAGE_CHECK_NAMES = ('match', 'partial', 'mention route', 'MISMATCH')
_PAGE_CHECK_RE = re.compile(r'\((match|partial|mention route|mismatch)\)\s*$', re.I)

# Default page check: answer type -> page kind -> check. Destination has none (see DESTINATION_FINDING).
_DEFAULTS = {
    'concept':   {'list': 'partial', 'guide': 'match',   'glossary': 'match',   'selling': 'mismatch'},
    'fit':       {'list': 'partial', 'guide': 'match',   'glossary': 'match',   'selling': 'mismatch'},
    'steps':     {'list': 'partial', 'guide': 'match',   'glossary': 'match',   'selling': 'mismatch'},
    'solutions': {'list': 'match',   'guide': 'match',   'glossary': 'partial', 'selling': 'mention route'},
    'shortlist': {'list': 'match',   'guide': 'partial', 'glossary': 'partial', 'selling': 'mention route'},
    'contrast':  {'list': 'match',   'guide': 'partial', 'glossary': 'partial', 'selling': 'mention route'},
    'specifics': {'list': 'partial', 'guide': 'partial', 'glossary': 'partial', 'selling': 'match'},
    'transact':  {'list': 'partial', 'guide': 'partial', 'glossary': 'partial', 'selling': 'match'},
}
DESTINATION_FINDING = 'confirm this page is the destination the prompt names'


def parse_check(cell):
    """The page check from the trailing '(<check>)' of an 'Answer shape and page check' cell, lower-cased, or None."""
    m = _PAGE_CHECK_RE.search(str(cell or ''))
    return m.group(1).lower() if m else None


def primary_type(cell):
    """The primary answer type: the text before ' / ' (space, slash, space), lower-cased."""
    return str(cell or '').split(' / ')[0].strip().lower()


def page_primary(types):
    """The page's primary answer type: the most common primary type among its tracked rows (in sheet order);
    on a tie, the tied type that appears first among the page's tracked rows."""
    types = [t for t in types if t]
    if not types:
        return None
    counts = collections.Counter(types)
    top = max(counts.values())
    tied = {t for t, c in counts.items() if c == top}
    return next(t for t in types if t in tied)


def page_kind(content_type):
    ct = (content_type or '').strip().lower()
    if ct in SELLING:
        return 'selling'
    if ct in LIST_PAGE:
        return 'list'
    if ct in GUIDE:
        return 'guide'
    if ct in GLOSSARY:
        return 'glossary'
    return None


def default_check(answer_type, content_type):
    """The page check a page of this primary answer type expects on this content type, or None when there is no
    scripted default (Destination: a hand decision; unknown types or content types)."""
    t = (answer_type or '').strip().lower()
    ct = (content_type or '').strip().lower()
    if t == 'contrast' and ct == 'product page':
        return 'mismatch'   # a single-product page cannot carry a side-by-side
    kind = page_kind(ct)
    if t not in _DEFAULTS or kind is None:
        return None
    return _DEFAULTS[t][kind]
