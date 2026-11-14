#!/usr/bin/env python3
"""Gate a finished TRACKED PROMPT SET before it leaves. Python standard library only; runs offline.

Reads the prompt sheet of the deliverable workbook and checks what a hand read misses at 80 to 150 rows. It flags; it
does not decide. Every flag is fixed or kept with a written reason on the sheet.

The sheet may be prompt-first ('Tracked Prompts', one row per prompt) or the one-sheet map ('Prompt Map'; if it has a
'Row' column, TRACKED rows are the prompts and PAGE / FOLD / other rows are context).

Checks:
  1. instrument signatures in a tracked prompt (TRACKER_TELLS in tracker_tells.py): a ranking instruction ("forced
     ranking", "rank/order them from best to worst"), an instruction addressed to the model ("you must provide / rank /
     list / give / answer", a prompt opening "you are a ...", "search the web for", "do not invent"), a leading <tag>
     wrapper, or a clause stating the asker's location or market ("my/our location/country/market/region is"). A
     first-person persona row is not a tell here: check 5 counts it. A prompt written like a tracking tool's measures the category's
     dashboards, not its buyers
  2. length 5 to 25 words; a 4-word row passes only when its Basis says observed
  3. dangling pronouns ("is it free", "does it work"): a follow-up turn, not a prompt (observed rows exempt)
  4. rows per page: floor 2; SIMULATED rows cap at 12 (observed rows are uncapped)
  5. one simulated cost row per selling page (Service Page, Product Page); one simulated persona row per page and per
     set; simulated OWN rows within --own-budget PER CLUSTER (default 1: OWN positioning is a shared intent tracked once
     per topic cluster, on its core page). Budgets and caps bind SIMULATED rows only: an observed row never counts toward
     them and is never dropped for them. A sheet with no Cluster (or Topic) column fails: the OWN budget cannot run.
  6. exact duplicates, and near duplicates across pages (token Jaccard >= 0.6): a service page and its listicle may
     share a subject by design; two pages of the same type carrying the same question is one answer measured twice
  7. every row has a fan-out block of 2 to 5 strings, each 10 words or fewer, no question mark (or "Not built: ...");
     an O-ui string is an engine string used verbatim, so one over 10 words is named: trim it and label it S-compress
  8. spelling consistency: a set should not mix optimise/optimize, programme/program
  9. the KEYWORD PARTITION, when a 'Keyword Map' sheet exists: every keyword appears once and every prompt it names is
     tracked on that page (pages written EXISTING:<url> are exempt)
 10. ANSWER TYPE, KPI AND PAGE CHECK. Every row's primary answer type (the text before ' / ') is one of the nine
     in answer_types.py (any other value fails as an unknown answer type) and its KPI one of the three. The page check is
     read only from the trailing '(<check>)' of 'Answer shape and page check'; the cell is identical on every tracked
     row of a page (rows that disagree are a hard flag), and any row whose check is MISMATCH makes the page MISMATCH.
     Printed for the hand read, never failing the build:
       - a Concept row on a selling page; a citation row on a MISMATCH page;
       - a row whose KPI differs from its answer type's default (Evidence mention on Concept, Fit or Steps is allowed
         silently; any other departure needs its reason on the row);
       - one finding per page whose check differs from the default for the page's PRIMARY answer type (the most common
         primary type on the page; on a tie, the tied type that appears first among its tracked rows) and content type (an off-default check
         is allowed with a reason on the row);
       - every page whose primary type is Destination: confirm the page is the destination the prompt names.
     Page kinds, the default table and the waiver set: answer_types.py and intent-format-kpi.md section 5. The KPI split
     is printed.
 11. ABBREVIATION VARIANTS: two rows on one page that are the same prompt with an abbreviation expanded are one prompt
     tracked twice, unless the 'Why that KPI' reason says the shorthand is ambiguous.
 12. THE CONTRACT: every required Prompt Map and Keyword Map column is present (header prefix, case-insensitive).
 13. CLOSED VOCABULARIES on every tracked row: Stage; Play starts Defend / Strengthen / Capture; Wave 1 to 9 and
     following Stage; Family A to L and never D or L; Form NB / OWN / COMP; Basis starts observed / simulated; observed
     rows carry an anchor; fan-out labels from the closed list (the bracket holds the bare label; any evidence count goes
     after the arrow); Page must carry and Source filled; Content type from the six; Need is Know / Do / Website /
     Visit; the page check in 'Answer shape and page check' ends in (match), (partial), (mention route) or (MISMATCH);
     Cluster core page Yes / No; a page of 4+ rows all in one family is printed for the hand read.

Usage: python3 verify_tracked_set.py deliverable.xlsx [--sheet 'Prompt Map'] [--own-budget 1]
       [--acronyms acronyms.txt]   (one "abbr=expansion" per line, added to the default map)
Exit 1 when anything hard is flagged. Near duplicates and the five answer-type findings of check 10 (Concept row on a selling page,
citation row on a MISMATCH page, KPI off its default, page check off its default, Destination to confirm) are printed for
the hand read.
"""
import argparse
import collections
import itertools
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsx_lite import Workbook, cell_str  # noqa: E402
from answer_types import (ANSWER_TYPES, CITATION_KPIS, CONTENT_TYPE_NAMES, CONTENT_TYPES, DESTINATION_FINDING,  # noqa: E402
                          EXPLAINING, KPI_DEFAULT, KPI_NAMES, KPIS, PAGE_CHECK_NAMES, SELLING, STAGE_NAMES, STAGES,
                          default_check, page_primary, parse_check, primary_type)
from tracker_tells import LOCATION_CLAUSE, TRACKER_TELLS  # noqa: E402

# Tracker tells from tracker_tells.py; on a tracked prompt a location or market clause is a tell too.
INSTRUMENT = re.compile('(%s|%s)' % (TRACKER_TELLS, LOCATION_CLAUSE), re.I)
# Findings printed for the hand read, never hard flags. Emitted and filtered through these constants only.
FINDING_CONCEPT_SELLING = 'Concept row on a selling page'
FINDING_CITATION_MISMATCH = 'citation row on a page whose page check says MISMATCH'
FINDING_KPI_DEFAULT = "row whose KPI differs from its answer type's default"
FINDING_CHECK_DEFAULT = "page whose check differs from the default for its primary answer type"
FINDING_DESTINATION = DESTINATION_FINDING
SOFT_FINDINGS = (' | ' + FINDING_CONCEPT_SELLING, ' | ' + FINDING_CITATION_MISMATCH, ' | ' + FINDING_KPI_DEFAULT,
                 ' | ' + FINDING_CHECK_DEFAULT, ' | ' + FINDING_DESTINATION)
PERSONA = re.compile(r"^(as an? |i'?m an? |i am an? |we('re| are) )", re.I)
DANGLING = re.compile(r'^(is|does|can|will|do) (it|they|this|that)\b', re.I)
COST = re.compile(r'\b(cost|charge|pric|budget|fee)', re.I)
STOP = {'which', 'what', 'are', 'the', 'a', 'an', 'for', 'to', 'of', 'in', 'and', 'is', 'do', 'i', 'my', 'with',
        'that', 'should', 'can', 'how', 'does', 'on', 'or', 'it', 'you', 'some'}
UK = re.compile(r'\b(optimis(e|ed|es|ing|ation)|programme|specialis(e|ed|es|ing)|analys(e|ing)|organisation)\b', re.I)
US = re.compile(r'\b(optimiz(e|ed|es|ing|ation)|program\b|specializ(e|ed|es|ing)|analyz(e|ed|es|ing)|organization)\b', re.I)
NEEDS = {'know', 'do', 'website', 'visit'}
ACRONYM = {'seo': 'search engine optimization', 'b2b': 'business to business', 'b2c': 'business to consumer',
           'saas': 'software as a service', 'ai': 'artificial intelligence',
           'roi': 'return on investment', 'kpi': 'key performance indicator', 'crm': 'customer relationship management',
           'erp': 'enterprise resource planning', 'api': 'application programming interface', 'faq': 'frequently asked questions',
           'smb': 'small and medium business'}   # cross-category only; add the client's own shorthand with --acronyms
PROMPT_MAP_REQUIRED = ['page', 'content type', 'answer shape', ('cluster', 'topic'), 'cluster core page',
                       'answer type', 'need', 'kpi', 'why that kpi', 'stage', 'play', 'wave', 'prompt', 'form',
                       'family', 'keywords mapped', 'why a buyer asks', 'page must carry', 'fan-out', 'basis',
                       'observed anchor', 'source']
KEYWORD_MAP_REQUIRED = ['keyword', 'volume', 'page', 'mapped to prompt', 'source']
FANOUT_LABELS = {'o-ui', 'o-bing', 'o-as', 'o-gsc', 's-compress', 's-axis'}


CONTRACT_NAMES = {n for e in PROMPT_MAP_REQUIRED for n in (e if isinstance(e, tuple) else (e,))}


def header_is(h, n):
    """A header is the column n when it is n exactly or n followed by ' ', ' (' or ':' (a word boundary)."""
    if n == 'need':   # a short header: match "Need" or "Need (...)" only, never "Need review" and the like
        return h == 'need' or h.startswith(('need (', 'need:'))
    return h == n or h.startswith((n + ' ', n + ':'))


def contract_name(h):
    """The longest contract column name this header is, or None ('cluster core page' is never 'cluster')."""
    hits = [n for n in CONTRACT_NAMES if header_is(h, n)]
    return max(hits, key=len) if hits else None


def find_col(low, name):
    for n in (name if isinstance(name, tuple) else (name,)):
        for i, h in enumerate(low):
            if header_is(h, n) and (n not in CONTRACT_NAMES or contract_name(h) == n):
                return i
    return None


def toks(s):
    return set(re.findall(r'[a-z0-9]+', s.lower())) - STOP


def main():
    a = argparse.ArgumentParser()
    a.add_argument('xlsx')
    a.add_argument('--own-budget', type=int, default=1, help='OWN rows allowed per topic cluster')
    a.add_argument('--sheet', default=None)
    a.add_argument('--acronyms', help='file of abbr=expansion lines, added to the default map')
    o = a.parse_args()
    acr = dict(ACRONYM)
    if o.acronyms:
        for line in open(o.acronyms, encoding='utf-8'):
            k, _, v = line.strip().partition('=')
            if k and v:
                acr[k.strip().lower()] = v.strip().lower()

    def expanded(s):
        return ' '.join(acr.get(t, t) for t in re.findall(r'[a-z0-9]+', s.lower()))

    wb = Workbook(o.xlsx)
    sheet = o.sheet if o.sheet in wb.sheetnames else ('Prompt Map' if 'Prompt Map' in wb.sheetnames else 'Tracked Prompts')
    if sheet not in wb.sheetnames:
        sys.exit('no prompt sheet (have %s)' % ', '.join(wb.sheetnames))
    allrows = wb.rows(sheet)
    hdr = [cell_str(h) for h in allrows[0]]
    low = [h.lower() for h in hdr]
    col = {h.split(' (')[0]: i for i, h in enumerate(low)}
    miss = [n for n in ('page', 'content type', 'prompt', 'form') if n not in col]
    if miss:
        sys.exit('missing columns: %s (have %s)' % (miss, hdr))
    missing_cols = [n if isinstance(n, str) else ' or '.join(n) for n in PROMPT_MAP_REQUIRED if find_col(low, n) is None]
    fo_col = find_col(low, 'fan-out')
    basis_col = find_col(low, 'basis')
    si_col = find_col(low, 'answer type')
    need_col = find_col(low, 'need')
    kpi_col = find_col(low, 'kpi')
    kpi_why_col = find_col(low, 'why that kpi')
    fmt_col = find_col(low, 'answer shape')
    stage_col, play_col, wave_col, fam_col, carry_col, src_col, core_col, anchor_col = (
        find_col(low, n) for n in ('stage', 'play', 'wave', 'family', 'page must carry', 'source', 'cluster core page', 'observed anchor'))
    row_col = col.get('row')
    P = col['prompt']
    PG = col['page']
    CT = col['content type']
    FM = col['form']

    def v(r, i):
        return cell_str(r[i]) if i is not None and i < len(r) else ''

    rows = [r for r in allrows[1:] if v(r, P) and (row_col is None or v(r, row_col) == 'TRACKED')]
    flags = []
    per_page = collections.defaultdict(list)
    for r in rows:
        per_page[v(r, PG)].append(r)
    if missing_cols:
        flags.append('CONTRACT: the prompt sheet is missing required columns: %s' % ', '.join(missing_cols))

    def observed(r):
        return v(r, basis_col).lower().startswith('observed')

    # 13. closed vocabularies per tracked row
    for r in rows:
        page, p = v(r, PG), v(r, P)
        ct = v(r, CT).lower()
        if ct not in CONTENT_TYPES:
            flags.append('%s | content type "%s" is not one of the six (%s)' % (page, ct, ', '.join(CONTENT_TYPE_NAMES)))
        if stage_col is not None and v(r, stage_col).lower() not in STAGES:
            flags.append('%s | stage missing or not %s: "%s" on %s' % (page, ' / '.join(STAGE_NAMES), v(r, stage_col), p))
        if play_col is not None and not v(r, play_col).lower().startswith(('defend', 'strengthen', 'capture')):
            flags.append('%s | play missing or not Defend / Strengthen / Capture: "%s" on %s' % (page, v(r, play_col), p))
        wv = v(r, wave_col)
        if wave_col is not None and not (wv.isdigit() and 1 <= int(wv) <= 9):
            flags.append('%s | wave missing or not 1-9: "%s" on %s' % (page, wv, p))
        if fam_col is not None:
            fam = v(r, fam_col).upper()
            if fam not in set('ABCDEFGHIJKL') or len(fam) != 1:
                flags.append('%s | family "%s" is not A to L on %s' % (page, fam, p))
            elif fam in ('D', 'L'):
                flags.append('%s | family %s row is tracked: D and L are brief inputs, never tracked: %s' % (page, fam, p))
        form = v(r, FM).upper()
        if form not in ('NB', 'OWN', 'COMP'):
            flags.append('%s | form "%s" is not NB / OWN / COMP on %s' % (page, form, p))
        b = v(r, basis_col).lower()
        if not b.startswith(('observed', 'simulated')):
            flags.append('%s | basis must start with observed or simulated: "%s" on %s' % (page, b[:40], p))
        if anchor_col is not None and b.startswith('observed') and not v(r, anchor_col):
            flags.append('%s | observed row with no verbatim anchor string: %s' % (page, p))
        if carry_col is not None and not v(r, carry_col):
            flags.append('%s | Page must carry is empty on %s' % (page, p))
        if src_col is not None and not v(r, src_col):
            flags.append('%s | Source is empty on %s' % (page, p))
        if need_col is not None and v(r, need_col).lower() not in NEEDS:
            flags.append('%s | Need missing or not Know / Do / Website / Visit: "%s" on %s' % (page, v(r, need_col), p))
        if fmt_col is not None and parse_check(v(r, fmt_col)) is None:
            flags.append('%s | Answer shape and page check must end in %s: "%s"' % (page, ', '.join('(%s)' % c for c in PAGE_CHECK_NAMES), v(r, fmt_col)[:60]))
        if core_col is not None and v(r, core_col).lower() not in ('yes', 'no'):
            flags.append('%s | Cluster core page must be Yes or No: "%s"' % (page, v(r, core_col)))
        if stage_col is not None and wave_col is not None and wv.isdigit():
            st, w = v(r, stage_col).lower(), int(wv)
            if (st in ('consideration', 'decision') and w != 1) or (st == 'awareness' and w == 1):
                flags.append('%s | wave %d does not follow the stage (%s): wave 1 is every Consideration and Decision row, Awareness fills after: %s' % (page, w, st, p))
        if fo_col is not None and not v(r, fo_col).lower().startswith('not built:'):
            for line in [x for x in v(r, fo_col).split('\n') if x.strip()]:
                m = re.search(r'\[([^\]]+)\]', line)
                if not m or m.group(1).strip().lower() not in FANOUT_LABELS:
                    flags.append('%s | fan-out string without a label from O-ui / O-bing / O-as / O-gsc / S-compress / S-axis: %s' % (page, line[:80]))
    if fam_col is not None:
        for page, rs in per_page.items():
            fams = {v(r, fam_col).upper() for r in rs}
            if len(rs) >= 4 and len(fams) == 1:
                flags.append('near duplicate family: %s carries %d rows all in family %s (a page written from habit; read it)' % (page, len(rs), fams.pop()))
    # 10 and 11. intent and KPI per row, abbreviation variants
    if si_col is None or kpi_col is None:
        flags.append('no Answer type / KPI column on the prompt sheet: every tracked prompt carries its answer type and the KPI it can realistically move')
    else:
        kpi_split = collections.Counter()
        for page, rs in per_page.items():
            ctype = v(rs[0], CT).lower()
            checks_seen = {v(r, fmt_col).strip() for r in rs} if fmt_col is not None else set()
            if len(checks_seen) > 1:
                flags.append('%s | Answer shape and page check differs across the page\'s tracked rows (it repeats on every row): %s'
                             % (page, ' / '.join(sorted(x[:40] for x in checks_seen))))
            parsed = [parse_check(v(r, fmt_col)) for r in rs] if fmt_col is not None else []
            # page level: one row whose trailing check is MISMATCH marks the page, whatever the first row says
            page_mismatch = any(c == 'mismatch' for c in parsed)
            page_check = next((c for c in parsed if c), None)
            primary = page_primary([primary_type(v(r, si_col)) for r in rs if primary_type(v(r, si_col)) in ANSWER_TYPES])
            if primary == 'destination':
                flags.append('%s | %s (primary answer type Destination; the page check says %s)' % (page, FINDING_DESTINATION, page_check))
            elif primary:
                want = default_check(primary, ctype)
                shown = 'mismatch' if page_mismatch else page_check
                if want and shown and shown != want:
                    flags.append('%s | %s (primary %s on a %s defaults to %s, the page says %s; allowed with a reason on the row)'
                                 % (page, FINDING_CHECK_DEFAULT, primary.title(), ctype, want, shown))
            by_expansion = {}
            for r in rs:
                p = v(r, P)
                si = primary_type(v(r, si_col))
                kpi = v(r, kpi_col).lower()
                why = v(r, kpi_why_col).lower()
                if si not in ANSWER_TYPES:
                    flags.append('%s | unknown answer type "%s" (not one of the nine): %s' % (page, si, p))
                else:
                    kpi_ok = kpi == KPI_DEFAULT[si] or (si in EXPLAINING and kpi == 'evidence mention')
                    if kpi in KPIS and not kpi_ok:
                        flags.append('%s | %s (%s defaults to %s; Evidence mention is allowed on Concept, Fit and Steps; any other departure needs its reason on the row): %s'
                                     % (page, FINDING_KPI_DEFAULT, si.title(), KPI_DEFAULT[si].title(), p))
                if kpi not in KPIS:
                    flags.append('%s | KPI missing or not %s: "%s" on %s' % (page, ' / '.join(KPI_NAMES), kpi, p))
                kpi_split[kpi] += 1
                if si == 'concept' and ctype in SELLING:
                    flags.append('%s | %s (the ledger: none on a page that sells unless two sources place it there): %s' % (page, FINDING_CONCEPT_SELLING, p))
                if kpi in CITATION_KPIS and page_mismatch:
                    flags.append('%s | %s (a selling page will not be cited for an explanation): %s' % (page, FINDING_CITATION_MISMATCH, p))
                e = expanded(p)
                if e in by_expansion and 'ambiguous' not in why:
                    flags.append('%s | abbreviation variant tracked twice (shorthand moves citations less than a rerun does): "%s" / "%s"' % (page, by_expansion[e], p))
                by_expansion.setdefault(e, p)
        print('KPI split: ' + ', '.join('%s %d' % (k, n) for k, n in sorted(kpi_split.items())))
    own = sum(1 for r in rows if v(r, FM).upper() == 'OWN')
    # OWN budget: simulated OWN rows per topic cluster (the Cluster or Topic column, never 'Cluster core page')
    clu_col = find_col(low, ('cluster', 'topic'))
    if clu_col is None:
        flags.append('no Cluster (or Topic) column: the OWN budget is counted per topic cluster and cannot run')
    else:
        own_by_cluster = collections.Counter(v(r, clu_col) for r in rows if v(r, FM).upper() == 'OWN' and not observed(r))
        for clu, n in sorted(own_by_cluster.items()):
            if n > o.own_budget:
                flags.append('cluster %s: %d simulated OWN rows, budget %d per cluster (observed OWN rows do not count)'
                             % (clu or '(blank)', n, o.own_budget))
    uk = sum(1 for r in rows if UK.search(v(r, P)))
    us = sum(1 for r in rows if US.search(v(r, P)))
    if uk and us:
        flags.append('spelling mixed across the set: %d UK-form, %d US-form prompts' % (uk, us))
    personas_total = 0
    fo_scoped = 0
    for page, rs in per_page.items():
        ctype = v(rs[0], CT).lower()
        sim_rows = [r for r in rs if not observed(r)]
        if len(rs) < 2:
            flags.append('%s: %d rows, the floor is 2' % (page, len(rs)))
        if len(sim_rows) > 12:
            flags.append('%s: %d simulated rows; simulated rows cap at 12 per page (observed rows are uncapped)' % (page, len(sim_rows)))
        cost = personas = 0
        for r in rs:
            p = v(r, P)
            w = len(p.split())
            obs = observed(r)
            if INSTRUMENT.search(p):
                flags.append('%s | instrument signature: %s' % (page, p))
            floor = 4 if obs else 5
            if not floor <= w <= 25:
                flags.append('%s | %d words: %s' % (page, w, p))
            if DANGLING.match(p) and not obs:
                flags.append('%s | dangling pronoun, a follow-up turn not a prompt: %s' % (page, p))
            if PERSONA.match(p) and not obs:
                personas += 1
                personas_total += 1
            if COST.search(p) and ctype in SELLING and not obs:
                cost += 1
            fo_text = v(r, fo_col)
            if fo_col is not None and fo_text.lower().startswith('not built:'):
                fo_scoped += 1
            elif fo_col is not None:
                fo = [x for x in fo_text.split('\n') if x.strip()]
                if not 2 <= len(fo) <= 5:
                    flags.append('%s | %d fan-out strings: %s' % (page, len(fo), p))
                for line in fo:
                    s = line.split('[')[0].strip()
                    m = re.search(r'\[([^\]]+)\]', line)
                    lab = m.group(1).strip().lower() if m else ''
                    if lab == 'o-ui' and len(s.split()) > 10:
                        flags.append('%s | O-ui string over 10 words: an observed engine string is O-ui only when used verbatim at 10 words or fewer; trim it and label it S-compress: %s' % (page, s))
                    elif len(s.split()) > 10 or '?' in s:
                        flags.append('%s | fan-out fails R2 (10 words or fewer, no question mark): %s' % (page, s))
        if cost > 1:
            flags.append('%s: %d simulated cost rows (one intent, one prompt; observed cost rows are exempt)' % (page, cost))
        if personas > 1:
            flags.append('%s: %d simulated persona rows (observed persona rows do not count)' % (page, personas))
    if personas_total > 1:
        flags.append('%d simulated persona rows across the set; the rule is one (observed rows do not count)' % personas_total)
    if fo_scoped:
        print('fan-out: %d rows scoped out with a written decision ("Not built: ..."); R1/R2 not checked on them' % fo_scoped)
    seen = {}
    for r in rows:
        k = re.sub(r'[^a-z0-9 ]', '', v(r, P).lower())
        if k in seen:
            flags.append('exact duplicate: %s (%s and %s)' % (v(r, P), seen[k], v(r, PG)))
        seen[k] = v(r, PG)
    for ra, rb in itertools.combinations(rows, 2):
        pa, pb = v(ra, P), v(rb, P)
        ta, tb = toks(pa), toks(pb)
        if ta and tb and len(ta & tb) / len(ta | tb) >= 0.6 and v(ra, PG) != v(rb, PG):
            same_type = v(ra, CT).lower() == v(rb, CT).lower()
            tag = 'near duplicate, SAME page type, keep only with a written reason' if same_type else 'near duplicate across page types, allowed by design if the reason is written'
            flags.append('%s: %s [%s] / %s [%s]' % (tag, pa, v(ra, PG), pb, v(rb, PG)))
    # 9. keyword partition
    if 'Keyword Map' in wb.sheetnames:
        km = wb.rows('Keyword Map')
        kh = [cell_str(h).lower() for h in km[0]]
        km_missing = [n for n in KEYWORD_MAP_REQUIRED if not any(n in h for h in kh)]
        if km_missing:
            flags.append('CONTRACT: the Keyword Map is missing required columns: %s' % ', '.join(km_missing))
        kc = find_col(kh, 'keyword')
        pc = find_col(kh, ('page (final)', 'page'))
        mc = find_col(kh, 'mapped to prompt')
        prompts_by_page = collections.defaultdict(set)
        for r in rows:
            prompts_by_page[v(r, PG)].add(v(r, P))
        seen_k = collections.Counter()
        nk = 0
        if None not in (kc, pc, mc):
            for r in km[1:]:
                if not v(r, kc):
                    continue
                nk += 1
                k = v(r, kc).lower()
                seen_k[k] += 1
                pg, mapped = v(r, pc), v(r, mc)
                if pg.startswith('EXISTING:'):
                    continue
                if not mapped.startswith('KEYWORD ONLY') and mapped not in prompts_by_page.get(pg, set()):
                    flags.append('keyword map: "%s" is mapped to a prompt not tracked on %s: %s' % (k, pg, mapped))
        twice = [k for k, c in seen_k.items() if c > 1]
        if twice:
            flags.append('keyword map: keywords listed more than once: %s' % twice)
        print('keyword map: %d keywords%s' % (nk, ', each mapped once' if not twice else ', some listed twice (flagged)'))
    print('%d rows, %d pages, OWN %d, %d flags' % (len(rows), len(per_page), own, len(flags)))
    for f in flags:
        print('  ' + f)
    hard = [f for f in flags if not f.startswith('near duplicate')
            and not any(s in f for s in SOFT_FINDINGS)]
    print('TRACKED SET: %s (%d hard flags)' % ('FAIL' if hard else 'PASS', len(hard)))
    sys.exit(1 if hard else 0)


if __name__ == '__main__':
    main()
