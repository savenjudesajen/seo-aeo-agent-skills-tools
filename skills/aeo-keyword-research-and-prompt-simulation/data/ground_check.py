#!/usr/bin/env python3
"""GROUNDING GATE: run before any prompt set ships. Python standard library only; runs offline.

A shape test cannot catch the failure this gate exists for: a prompt set rewritten to match the observed corpus on
length, clause rate and first-person rate can still be mostly ungrounded, because the phrasings were written to LOOK
like the harvested ones rather than taken from them. Only a verbatim (or anchored) match rate catches it.

What counts:
  VERBATIM  the prompt itself is in the tier-1 corpus (question tools, Google PAA, Search Console human rows, the
            signed-off keyword set, each under its own source label).
  ANCHORED  the prompt is a rewrite of an observed string that IS in the corpus, named in the row's Observed anchor
            column. A made-up anchor does not count.
  1b        a keyword-verbatim row: the anchor is a keyword from the client's signed-off set (source label contains
            "keyword"). Grounded, and reported on its own line, never merged into the question tools.
  SIMULATED the row says so, names its matrix family and what was checked and found empty. Counted, never grounded.
  UNFOUND   the row claims observed and neither it nor its anchor is in the corpus: a shape-borrow, and a failure.

The gate fails when: grounded (verbatim + anchored + 1b) is under the floor; a row rests on tier-2 evidence only (FAQ
blocks are authored content, never proof anyone asked); an observed row is UNFOUND; a simulated row has no family or no
reason; or the corpus is thin (fewer distinct seeds than --min-seeds).

The floor and its waiver. The default 50% floor fits an informational set, where question tools hold most of what buyers
ask. A provider-shortlist set (Shortlist, Contrast and Destination rows: qualified shortlists, alternatives, head-to-heads,
destination prompts) cannot
clear it honestly: no question tool records those prompts. Such a set runs with a lower --floor AND a written
--floor-reason; a lowered floor with no reason fails. When rows carry an answer type, the report prints the
rows simulated by design (the FLOOR_WAIVER set in answer_types.py) apart from the harvestable rest. Solutions rows state a
problem, the shape question tools hold most often, so they count as harvestable.

Possible anchors. Before a row stays simulated, the corpus is searched for observed strings sharing most of its words
(token Jaccard >= 0.45, plurals folded, stop words dropped) and the hits are printed for a hand read: an observed
phrasing beats a constructed one. A hit that changes the subject is not an anchor; the label is a hand decision.

Inputs:
  --prompts   [{"prompt", "basis" (starts with observed|simulated; "grounded_in" is read when basis is absent), "anchor", "family", "page", "answer_type"}, ...]
  --corpus    {"t1": {normalised: [text, source, seed]}, "t2": {...}}  or a plain list [{q|text, src|source, seed}]
  --floor     minimum grounded share (default 0.50)
  --floor-reason  required when --floor is below 0.50
  --min-seeds minimum distinct seeds in the corpus (default 20)
Exit 0 only when every check passes. Shape figures are reported and never gated.
"""
import argparse
import collections
import json
import os
import re
import sys


def norm(s):
    return re.sub(r'[^a-z0-9 ]', '', str(s).lower()).strip()


STOPW = {'which', 'what', 'are', 'the', 'a', 'an', 'for', 'to', 'of', 'in', 'and', 'is', 'do', 'i', 'my', 'with', 'that',
         'should', 'can', 'how', 'does', 'on', 'or', 'it', 'you', 'some'}
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from answer_types import FLOOR_WAIVER as SHORTLIST, FLOOR_WAIVER_NAMES, primary_type  # noqa: E402


def _sing(t):
    return t[:-1] if len(t) > 3 and t.endswith('s') and not t.endswith('ss') else t


def _toks(s):
    return {_sing(t) for t in re.findall(r'[a-z0-9]+', str(s).lower()) if t not in STOPW}


def possible_anchors(prompt, T1, min_overlap=0.45, limit=2):
    a = _toks(prompt)
    out = []
    for v in T1.values():
        b = _toks(v[0])
        if a and b:
            j = len(a & b) / len(a | b)
            if j >= min_overlap:
                out.append((j, v[0], v[1]))
    return sorted(out, reverse=True)[:limit]


def classify(row, T1, T2):
    q = row.get('prompt', '')
    basis = str(row.get('basis') or row.get('grounded_in') or '').strip().lower()
    anchor = str(row.get('anchor') or '').strip()
    n, na = norm(q), norm(anchor)
    observed = basis.startswith('observed')
    if n in T1:
        return 'verbatim', T1[n][1]
    if observed and na and na in T1:
        return ('1b' if 'keyword' in str(T1[na][1] or '').lower() else 'anchored'), T1[na][1]
    if observed:
        return ('tier2', 'tier-2 only') if (n in T2 or (na and na in T2)) else ('unfound', '')
    return 'simulated', ''


def shape(lst):
    if not lst:
        return 0, 0, 0
    L = [len(x.split()) for x in lst]
    cl = 100 * sum(1 for x in lst if re.search(r'\b(and|but|when|while|without|before|after|if)\b', x, re.I)) / len(lst)
    fp = 100 * sum(1 for x in lst if re.search(r"\b(i|my|me|we|our)\b", x, re.I)) / len(lst)
    return sum(L) / len(L), cl, fp


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--prompts', required=True)
    a.add_argument('--corpus', required=True)
    a.add_argument('--floor', type=float, default=0.50)
    a.add_argument('--floor-reason', default='')
    a.add_argument('--min-seeds', type=int, default=20)
    o = a.parse_args()
    fail = []
    P = json.load(open(o.prompts, encoding='utf-8'))
    C = json.load(open(o.corpus, encoding='utf-8'))
    if isinstance(C, list):
        C = {'t1': {norm(r.get('q') or r.get('text') or ''): [r.get('q') or r.get('text'), r.get('src') or r.get('source') or '', r.get('seed') or ''] for r in C}, 't2': {}}
    T1, T2 = C.get('t1', {}), C.get('t2', {})
    if not P:
        print('GROUNDING GATE: FAIL - empty prompt set')
        sys.exit(1)
    seeds = {v[2] for v in T1.values() if len(v) > 2}
    if len(seeds) < o.min_seeds:
        fail.append('corpus covers only %d seeds, below the %d minimum: a grounding rate against a thin corpus is not evidence' % (len(seeds), o.min_seeds))
    kinds = collections.Counter()
    by_source = collections.Counter()
    unfound, tier2, bad_sim, sim_rows = [], [], [], []
    for row in P:
        kind, src = classify(row, T1, T2)
        kinds[kind] += 1
        if kind in ('verbatim', 'anchored', '1b'):
            by_source[src] += 1
        elif kind == 'unfound':
            unfound.append(row.get('prompt', ''))
        elif kind == 'tier2':
            tier2.append(row.get('prompt', ''))
        else:
            sim_rows.append(row)
            if not str(row.get('family') or '').strip() or len(str(row.get('basis') or row.get('grounded_in') or '').split(None, 1)) < 2:
                bad_sim.append(row.get('prompt', ''))
    grounded = kinds['verbatim'] + kinds['anchored'] + kinds['1b']
    rate = grounded / len(P)
    if o.floor < 0.50 and not o.floor_reason.strip():
        fail.append('the floor was lowered to %.0f%% with no --floor-reason: a lower bar needs the reason written down' % (100 * o.floor))
    if rate < o.floor:
        fail.append('grounded %.0f%% is below the %.0f%% floor: %d rows were written rather than harvested' % (100 * rate, 100 * o.floor, kinds['simulated'] + kinds['unfound']))
    if unfound:
        fail.append('%d rows claim observed but neither the prompt nor its anchor is in the corpus: %s' % (len(unfound), unfound[:4]))
    if tier2:
        fail.append('%d rows rest on tier-2 evidence only (FAQ blocks are authored content, not observed demand): %s' % (len(tier2), tier2[:3]))
    if bad_sim:
        fail.append('%d simulated rows carry no family or no reason: %s' % (len(bad_sim), bad_sim[:3]))
    hits = [(r, possible_anchors(r.get('prompt', ''), T1)) for r in sim_rows]
    hits = [(r, h) for r, h in hits if h]
    print('GROUNDING')
    print('  corpus                : %d tier-1 strings over %d seeds (%d tier-2, never counted as grounding)' % (len(T1), len(seeds), len(T2)))
    print('  prompts               : %d' % len(P))
    print('  grounded              : %d  (%.0f%%, floor %.0f%%) = verbatim %d + anchored rewrite %d + keyword-verbatim (1b) %d' % (grounded, 100 * rate, 100 * o.floor, kinds['verbatim'], kinds['anchored'], kinds['1b']))
    for s, n in by_source.most_common():
        print('      %4d  %s' % (n, s))
    if o.floor < 0.50 and o.floor_reason.strip():
        print('  floor                 : lowered from 50%% to %.0f%%: %s' % (100 * o.floor, o.floor_reason.strip()))
    if any(r.get('answer_type') for r in P):
        sl = [r for r in P if primary_type(r.get('answer_type')) in SHORTLIST]
        rest = [r for r in P if r not in sl]
        g_rest = sum(1 for r in rest if classify(r, T1, T2)[0] in ('verbatim', 'anchored', '1b'))
        g_sl = sum(1 for r in sl if classify(r, T1, T2)[0] in ('verbatim', 'anchored', '1b'))
        print('  shortlist-shaped rows : %d of %d (%s), grounded %d: qualified shortlists, alternatives, head-to-heads and destination prompts are simulated by design' % (len(sl), len(P), ', '.join(FLOOR_WAIVER_NAMES), g_sl))
        print('  harvestable rows      : %d, grounded %d (%.0f%%)' % (len(rest), g_rest, (100 * g_rest / len(rest)) if rest else 0))
    print('  simulated, labelled   : %d' % kinds['simulated'])
    print('  observed but unfound  : %d' % kinds['unfound'])
    print('  possible anchors      : %d of %d simulated rows share most of their words with an observed string (read each)' % (len(hits), len(sim_rows)))
    for r, h in hits[:40]:
        print('      %s\n          <- [%s] %s (overlap %.2f)' % (r.get('prompt', ''), h[0][2], h[0][1], h[0][0]))
    if len(hits) > 40:
        print('      ... and %d more' % (len(hits) - 40))
    print('  resting on tier-2 only: %d' % kinds['tier2'])
    print('  shape  prompts        : %.1f words | clause %.1f%% | first-person %.1f%%' % shape([r.get('prompt', '') for r in P]))
    print('         corpus         : %.1f words | clause %.1f%% | first-person %.1f%%' % shape([v[0] for v in T1.values()]))
    print('         (shape is reported, never gated: matching it is exactly what a written set does)')
    if fail:
        print('\nFAILURES:')
        for f in fail:
            print('  -', f)
        sys.exit(1)
    print('\nGROUNDING GATE: PASS')


if __name__ == '__main__':
    main()
