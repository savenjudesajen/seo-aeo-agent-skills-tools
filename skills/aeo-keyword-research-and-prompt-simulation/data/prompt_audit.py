#!/usr/bin/env python3
"""PROMPT QUALITY AUDIT: run on every prompt set, grounded or simulated, before it ships.
Python standard library only; runs offline.

The grounding gate answers "was this phrasing observed?". It cannot answer "does this prompt belong on this page?". A
set can be almost entirely grounded and still be rejected, because the failure modes are about placement, not phrasing:
a grounded prompt placed on a page that cannot answer it; informational prompts on a selling page, where the answer
names no provider; placements that no results page supports.

Seven checks. Each FLAGS for a hand read; a BLOCKER fails the build (exit 1).

  A1 PROVIDER INTENT vs PAGE TYPE. On a page that sells: a MENTION row with no provider noun, no buying signal and no
     brand name is a BLOCKER (the engine will explain, not name anyone); a DIY how-to tagged Mention is a BLOCKER; a
     CITATION row is a FLAG (the page owes the explainer section named in Page must carry, or the keyword moves to the
     guide). A selling page whose rows are ALL citation rows is a BLOCKER unless its page check (in Answer shape and page check) already says MISMATCH
     (then a FLAG for the owner's decision). On a page that informs: a provider question with a buying word tagged
     Mention is a FLAG (it may belong on the service page). Provider signals include "solution(s)" and analyst report
     names, because answers to those name vendors. A row whose page check is its answer type's default (match or
     mention route, from answer_types.py) is never blocked for lacking provider words: a Transact or Specifics row at
     its default on a selling page names the client by being there. A1 still blocks rows off their default.
  A2 CORE-TERM CONTAINMENT. A row with no mapped keyword (an intent row: proof, cost, OWN, switching, persona) that
     carries none of the page's core terms is a BLOCKER unless it is family C or I (vendor names are the nouns) or names
     a client brand. A row WITH a mapped keyword is contained by construction and only FLAGS.
  A3 QUALIFIER MATCH. A row that drops every qualifier the page owns is a FLAG.
  A4 AI-ERA SHAPE. A short bare question is a FLAG, never a blocker (observed questions are short by construction and
     grounding beats length). The set-level mean is reported.
  A5 COVERAGE. A page with keywords and NO prompt is a BLOCKER. A high keyword-to-prompt ratio is a FLAG to check that
     each row's keywords are one intent, never a reason to pad.
  A6 PLACEMENT EVIDENCE. With --evidence ({page: [prompts the SERP cross-check placed here]}): a prompt not placed on
     its page is a FLAG. Without it, the report says placements rest on the keyword partition and A2.
  A7 STAGE MIX. Stage is required on every row (Awareness / Consideration / Decision). More than 60% Awareness on a page
     that sells is a BLOCKER.
  KPI is required on every row (Mention / Citation / Evidence mention); a row without one is a BLOCKER.

Input: --prompts  [{prompt, page, stage, kpi, family, kws (mapped keyword count), basis, ...}]
       --pages    {page: {ctype, core[], quals[], nkw, vol, core_page (bool), format_check (str)}}
       --evidence optional {page: [prompts]}
       --brands   REQUIRED [brand names]: the client's brand and product names plus every tracked competitor's.
                  Without them an OWN or competitor-named row has no provider signal and blocks, so a missing or
                  empty list stops the audit with a message instead.
data/run_gates.py derives all of these from the deliverable workbook, so the audit cannot be skipped for want of input.
"""
import argparse
import collections
import json
import os
import re
import sys

PROVIDER = re.compile(r'\b(agency|agencies|service|services|company|companies|firm|firms|consultant|consultants|'
                      r'consultancy|consultancies|consulting|provider|providers|partner|partners|vendor|vendors|'
                      r'platform|platforms|tool|tools|software|app|apps|freelancer|freelancers|contractor|contractors|'
                      r'team|teams|specialist|specialists|studio|studios|shop|shops|practice|option|options|'
                      r'marketplace|marketplaces|package|packages|solution|solutions|magic quadrant|forrester wave|'
                      r'peer insights)\b', re.I)
BUYING = re.compile(r'\b(how much|cost|costs|price|pricing|charge|fee|worth it|worth the|worth paying|budget|best|top|'
                    r'leading|choose|choosing|select|selecting|hire|hiring|vet|vetting|evaluate|evaluating|evaluation|'
                    r'criteria|compare|comparison|vs|versus|alternative|alternatives|look for|looking for|shortlist|'
                    r'recommend|recommendation|recommendations|consider|considering|rank|ranked|ranking|switch|'
                    r'switching|migrate|migrating|outsource|outsourcing|suitable|reviews|rated|proven|track record|'
                    r'case stud|include|included|offer|offers|specialize|specialise|book|booking|buy|order|sign up|signup|quote|'
                    r'download|subscribe|trial)\b', re.I)
DIY = re.compile(r'^(how (do|can) (i|you|we)\b|how to\b)', re.I)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from answer_types import (CITATION_KPIS, INFORMS, KPI_NAMES, KPIS, SELLING as SELLS, STAGE_NAMES, STAGES,  # noqa: E402
                          default_check, parse_check, primary_type)  # a Listicle is a list page, not a selling page


BRANDS_MESSAGE = ("--brands is required: the path to a JSON file holding one list of strings, the client's brand and "
                  "product names plus every tracked competitor's name, e.g. [\"ClientA\", \"ProductA\", \"CompetitorB\"]. "
                  "Without it OWN and competitor-named rows have no provider signal and the audit would block them.")


def load_brands(path):
    """The --brands list, or exit with BRANDS_MESSAGE when it is missing, unreadable or empty."""
    try:
        brands = json.load(open(path, encoding='utf-8')) if path else None
    except (OSError, ValueError):
        brands = None
    brands = [str(b).strip() for b in brands if str(b).strip()] if isinstance(brands, list) else []
    if not brands:
        sys.exit(BRANDS_MESSAGE)
    return brands


def lc(x):
    return str(x or '').strip().lower()


def page_check_of(value):
    """The page check from a full 'Answer shape and page check' cell or from the bare check run_gates passes."""
    return parse_check(value) or parse_check('(%s)' % (value or ''))
WHO = re.compile(r'^\s*who\b(\s+(is|are|can|will|does|do))?\s+(offers?|delivers?|provides?|sells?|builds?|makes?|'
                 r'supplies|supply|best|the best|leading|top)\b', re.I)


def named_entity(q, brands):
    return any(re.search(r'\b' + re.escape(b) + r'\b', q, re.I) for b in brands) if brands else False


def norm(s):
    return re.sub(r'[^a-z0-9 ]', ' ', str(s).lower())


def sing(t):
    return t[:-1] if len(t) > 4 and t.endswith('s') and not t.endswith('ss') else t


def toks(s):
    return {sing(t) for t in norm(s).split()}


def audit(P, PAGES, EV, BRANDS=None):
    BRANDS = BRANDS or []
    issues = []

    def add(sev, code, page, prompt, msg):
        issues.append({'severity': sev, 'check': code, 'page': page, 'prompt': prompt, 'issue': msg})
    byp = collections.defaultdict(list)
    for r in P:
        byp[r['page']].append(r)
    for r in P:
        if lc(r.get('stage')) not in STAGES:
            add('BLOCKER', 'A7-stage', r['page'], r['prompt'], 'no stage label (%s, by who does the work)' % ' / '.join(STAGE_NAMES))
        if lc(r.get('kpi')) not in KPIS:
            add('BLOCKER', 'KPI', r['page'], r['prompt'], 'no KPI label (%s)' % ' / '.join(KPI_NAMES))
    for page, meta in PAGES.items():
        rows = byp.get(page, [])
        ct = (meta.get('ctype') or '').strip().lower()
        core = [c.lower() for c in meta.get('core', [])]
        quals = [q.lower() for q in meta.get('quals', [])]
        fmt_check = page_check_of(meta.get('format_check'))
        nkw = meta.get('nkw', 0)
        if not rows and nkw:
            add('BLOCKER', 'A5-coverage', page, '', '%d keywords and NO prompt.' % nkw)
        elif rows and nkw / len(rows) >= 8:
            add('FLAG', 'A5-coverage', page, '', '%d keywords carrying %d prompt(s): check that the keywords on each row are one intent; do not pad.' % (nkw, len(rows)))
        if rows and ct in SELLS:
            aw = sum(1 for r in rows if lc(r.get('stage')) == 'awareness')
            if aw / len(rows) > 0.6:
                add('BLOCKER', 'A7-stage', page, '', '%d of %d prompts are Awareness on a %s: a selling page is measured on whether an engine names a provider, and Awareness prompts get a how-to answer.' % (aw, len(rows), ct))
            cit = sum(1 for r in rows if lc(r.get('kpi')) in CITATION_KPIS)
            if cit == len(rows):
                if fmt_check == 'mismatch':
                    add('FLAG', 'A1-intent', page, '', 'every tracked row is a citation row on a %s marked MISMATCH: the owner decides, rebuild guide-shaped or accept that it tracks nothing citable.' % ct)
                else:
                    add('BLOCKER', 'A1-intent', page, '', 'every tracked row is a citation row on a %s: the page is mis-typed for its prompts. Retype it or mark the page check in Answer shape and page check MISMATCH with the decision.' % ct)
        for r in rows:
            q = r['prompt']
            qt = toks(q)
            kpi = lc(r.get('kpi'))
            want = default_check(primary_type(r.get('answer_type')), ct)
            at_default = fmt_check is not None and fmt_check == want and want in ('match', 'mention route')
            fam = (r.get('family') or '').upper()
            kws = int(r.get('kws') or 0)
            if fam == 'L':
                if len(q.split()) > 10:
                    add('FLAG', 'A4-shape', page, q, '%d words for an engine-grounding string (5 to 8 expected).' % len(q.split()))
                continue
            signal = PROVIDER.search(q) or BUYING.search(q) or named_entity(q, BRANDS) or WHO.match(q)
            if ct in SELLS:
                if at_default:
                    pass   # at its type's default check: never blocked for lacking provider words
                elif kpi == 'mention' and not signal:
                    add('BLOCKER', 'A1-intent', page, q, 'a Mention row with no provider noun, buying word or brand on a %s: the engine will explain, not name a provider.' % ct)
                elif kpi == 'mention' and DIY.match(q) and not (PROVIDER.search(q) or named_entity(q, BRANDS)):
                    add('BLOCKER', 'A1-intent', page, q, 'DIY how-to tagged Mention on a %s: the asker does the work, nobody is named.' % ct)
                if kpi in CITATION_KPIS:
                    add('FLAG', 'A1-intent', page, q, 'citation row on a %s: the page owes the explainer section in Page must carry, or the keyword moves to the guide.' % ct)
            elif ct in INFORMS and PROVIDER.search(q) and BUYING.search(q) and kpi == 'mention':
                add('FLAG', 'A1-intent', page, q, 'commercial provider question on a %s; it may belong on the service page.' % ct)
            if core and not any(all(sing(t) in qt for t in c.split()) for c in core):
                if kws == 0 and fam not in ('C', 'I') and not named_entity(q, BRANDS):
                    add('BLOCKER', 'A2-core', page, q, "no mapped keyword and none of the page's core terms (%s): nothing ties this row to the page." % ', '.join(core))
                else:
                    add('FLAG', 'A2-core', page, q, "none of the page's core terms (%s); the mapped keyword is the tie, read it." % ', '.join(core))
            miss = [x for x in quals if sing(x) not in qt]
            if quals and len(miss) == len(quals):
                add('FLAG', 'A3-qualifier', page, q, 'drops every qualifier the page owns (%s): it reads as the parent term.' % ', '.join(quals))
            if len(q.split()) <= 4 and not (PROVIDER.search(q) or named_entity(q, BRANDS)):
                add('FLAG', 'A4-shape', page, q, '%d words and no provider noun: fine when observed verbatim, a PAA-shaped invention otherwise.' % len(q.split()))
            if EV is not None and q not in EV.get(page, []):
                add('FLAG', 'A6-evidence', page, q, 'not placed on this page by the SERP cross-check: placed by the partition or by wording.')
    if EV is None:
        add('INFO', 'A6-evidence', '(set)', '', 'no SERP evidence file: placements rest on the keyword partition and on core-term containment for keyword-less rows. If the cross-check was meant to run, the run is not done.')
    conv = [r for r in P if (r.get('family') or '').upper() != 'L']
    if conv:
        mw = sum(len(r['prompt'].split()) for r in conv) / len(conv)
        add('INFO', 'A4-shape', '(set)', '', 'mean prompt length %.1f words (AI-era long tail runs longer than PAA; a grounded set sits between).' % mw)
    return issues


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--prompts', required=True)
    a.add_argument('--pages', required=True)
    a.add_argument('--evidence')
    a.add_argument('--brands')
    a.add_argument('--json')
    o = a.parse_args()
    P = json.load(open(o.prompts, encoding='utf-8'))
    PAGES = json.load(open(o.pages, encoding='utf-8'))
    EV = json.load(open(o.evidence, encoding='utf-8')) if o.evidence else None
    BR = load_brands(o.brands)
    issues = audit(P, PAGES, EV, BR)
    if o.json:
        json.dump(issues, open(o.json, 'w', encoding='utf-8'), indent=1)
    bl = [i for i in issues if i['severity'] == 'BLOCKER']
    fl = [i for i in issues if i['severity'] == 'FLAG']
    print('PROMPT QUALITY AUDIT\n  prompts %d over %d pages' % (len(P), len(PAGES)))
    print('  BLOCKERS %d   FLAGS %d\n' % (len(bl), len(fl)))
    for code, n in collections.Counter(i['check'] for i in issues if i['severity'] != 'INFO').most_common():
        b = sum(1 for i in issues if i['check'] == code and i['severity'] == 'BLOCKER')
        print('    %-14s %4d  (%d blocking)' % (code, n, b))
    for i in issues:
        if i['severity'] in ('BLOCKER', 'INFO'):
            print('  %s %s | %s | %s: %s' % (i['severity'], i['check'], i['page'], i['prompt'][:60], i['issue']))
    if bl:
        print('\nPROMPT QUALITY AUDIT: FAIL - %d blockers' % len(bl))
        sys.exit(1)
    print('\nPROMPT QUALITY AUDIT: PASS')


if __name__ == '__main__':
    main()
