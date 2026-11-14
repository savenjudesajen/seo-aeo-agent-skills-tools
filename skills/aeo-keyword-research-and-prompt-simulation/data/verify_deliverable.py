#!/usr/bin/env python3
"""verify_deliverable.py: the mechanical gate for a cleaned keyword workbook in the seed-chain C6 layout.
Python standard library only; runs offline.

Run it against the SAVED workbook, not the build script's variables. It re-derives every checkable claim from the source
JSON and fails loudly. It never imports the build script.

Usage:  python3 verify_deliverable.py <workbook.xlsx> <rows.json> <gsc_norm.json> [--exempt exempt.txt]

Layout expected (positional columns; adapt the constants below if your layout differs, or say in the run notes that the
layout does not match and run the hygiene gate instead):
  Keywords       col B term, col E volume, col H impressions total
  Group Summary  col A group, col C head term, col D count, col E volume total, col F impressions total,
                 col H top CPC, col I prose
  Exclusions     col A class, col D examples separated by ';'
  README         prose containing the volume, impressions and clicks totals (formatted 1,234)
rows.json:     [{term, vol, kd, cpc, imp_total, clk_total, variants, variant_list, group}, ...]
gsc_norm.json: [{q, imp, clicks}, ...] AFTER apostrophe and case normalisation.
Near duplicates are found after compound spellings are folded: a hyphen inside a word is dropped ("e-bike" ->
"ebike"), a one-letter token is joined to the next ("e bike" -> "ebike"), and terms that differ only in spacing
("wood working tools" / "woodworking tools") share a second key. Word order and plurals are ignored as before.
exempt.txt:    optional; one pair per line, "term one | term two": two real head terms that normalise together and are
               kept apart on purpose (say why in the deliverable).

Exit 1 on any failure. A passing run prints the surviving superlatives so a human still reads them: a machine cannot
judge "the clearest case in this file".
"""
import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsx_lite import Workbook, cell_str  # noqa: E402

KW_TERM, KW_VOL, KW_IMP = 1, 4, 7
GS_GROUP, GS_HEAD, GS_COUNT, GS_VOL, GS_IMP, GS_CPC, GS_PROSE = 0, 2, 3, 4, 5, 7, 8
EX_CLASS, EX_EXAMPLES = 0, 3
STOP = {'for', 'and', 'in', 'of', 'to', 'the', 'a', 'on', 'with'}


def n(x):
    return str(x).replace(chr(0x2019), "'").replace(chr(0x2018), "'").strip().lower()


def sing(w):
    if len(w) <= 3:
        return w
    if w.endswith('ies'):
        return w[:-3] + 'y'
    if w.endswith('ss'):
        return w
    if w.endswith('s'):
        return w[:-1]
    return w


def fold_compounds(t):
    """Fold compound spellings: drop a hyphen between word characters, join a one-letter token to the next one."""
    t = re.sub(r'(?<=\w)-(?=\w)', '', t)
    toks = [w for w in re.split(r'[\s\-]+', t) if w]
    out, i = [], 0
    while i < len(toks):
        if len(toks[i]) == 1 and toks[i] not in STOP and i + 1 < len(toks):
            out.append(toks[i] + toks[i + 1])
            i += 2
        else:
            out.append(toks[i])
            i += 1
    return out


def key(t):
    """Order- and plural-insensitive key after compound folding."""
    return tuple(sorted(sing(w) for w in fold_compounds(n(t).replace('?', '')) if w not in STOP))


def space_key(t):
    """Spacing-insensitive key: the folded words in order, joined with nothing ('wood working' = 'woodworking')."""
    return ''.join(sing(w) for w in fold_compounds(n(t).replace('?', '')) if w not in STOP)


def near_duplicates(terms, exempt=frozenset()):
    """Groups of two or more distinct terms that share either key, minus the exempt pairs."""
    groups = []
    for keyfn in (key, space_key):
        col = collections.defaultdict(list)
        for t in terms:
            col[keyfn(t)].append(t)
        for v in col.values():
            distinct = sorted(set(v))
            if len(distinct) > 1 and frozenset(x.lower() for x in distinct) not in exempt and distinct not in groups:
                groups.append(distinct)
    return groups


def g(row, i):
    return row[i] if i < len(row) else None


def num(x):
    return x if isinstance(x, (int, float)) else 0


def main():
    a = argparse.ArgumentParser()
    a.add_argument('workbook')
    a.add_argument('rows')
    a.add_argument('gsc')
    a.add_argument('--exempt')
    o = a.parse_args()
    exempt = set()
    if o.exempt:
        for line in open(o.exempt, encoding='utf-8'):
            parts = [p.strip().lower() for p in line.split('|') if p.strip()]
            if len(parts) == 2:
                exempt.add(frozenset(parts))
    wb = Workbook(o.workbook)
    f = json.load(open(o.rows, encoding='utf-8'))
    gq = {n(q['q']): (q['imp'], q['clicks']) for q in json.load(open(o.gsc, encoding='utf-8'))}
    byg = collections.defaultdict(list)
    for r in f:
        byg[r['group']].append(r)
    for k in byg:
        byg[k].sort(key=lambda r: (-(r['vol'] or 0), -(r['imp_total'] or 0)))
    fails = []

    # 1. the Keywords tab is the source, cell for cell
    kw = [r for r in wb.rows('Keywords')[1:] if g(r, KW_TERM)]
    if len(kw) != len(f):
        fails.append('Keywords tab has %d rows, source has %d' % (len(kw), len(f)))
    BY = {r['term']: r for r in f}
    for r in kw:
        term = cell_str(g(r, KW_TERM))
        s = BY.get(term)
        if not s:
            fails.append('row not in source: %s' % term)
            continue
        if num(g(r, KW_VOL)) != (s['vol'] or 0):
            fails.append('%s: volume %s vs %s' % (term, g(r, KW_VOL), s['vol']))
        if num(g(r, KW_IMP)) != (s['imp_total'] or 0):
            fails.append('%s: impressions %s vs %s' % (term, g(r, KW_IMP), s['imp_total']))

    # 2. no duplicate and no near-duplicate rows survive
    terms_list = [cell_str(g(r, KW_TERM)) for r in kw]
    dup = [t for t, c in collections.Counter(terms_list).items() if c > 1]
    if dup:
        fails.append('duplicate terms: %s' % dup)
    nd = near_duplicates(terms_list, exempt)
    if nd:
        fails.append('near-duplicate rows still present: %s' % nd)

    # 3. every row clears the stated evidence floor (a volume with difficulty, a CPC above zero, or impressions)
    floor = [r['term'] for r in f if r['kd'] is None and not (r['cpc'] or 0) and not r['imp_total']]
    if floor:
        fails.append('rows clearing none of the evidence floor: %s' % floor)

    # 4. Search Console totals equal head + variants, recomputed from the normalised export
    for r in f:
        terms = [r['term']] + list(r['variant_list'])
        wi = sum(gq.get(n(t), (0, 0))[0] for t in terms)
        wc = sum(gq.get(n(t), (0, 0))[1] for t in terms)
        if int(wi) != r['imp_total'] or int(wc) != r['clk_total']:
            fails.append('%s: Search Console %s/%s vs export %d/%d' % (r['term'], r['imp_total'], r['clk_total'], wi, wc))

    # 5. Group Summary aggregates, and the head really is the top row
    gs = wb.rows('Group Summary')[1:]
    for r in gs:
        grp = cell_str(g(r, GS_GROUP))
        if not grp or grp == 'TOTAL':
            continue
        if grp not in byg:
            fails.append('Group Summary has unknown group %s' % grp)
            continue
        rows = byg[grp]
        if cell_str(g(r, GS_HEAD)) != rows[0]['term']:
            fails.append('%s: head "%s" is not the top row "%s"' % (grp, g(r, GS_HEAD), rows[0]['term']))
        if num(g(r, GS_COUNT)) != len(rows):
            fails.append('%s: count %s vs %d' % (grp, g(r, GS_COUNT), len(rows)))
        if num(g(r, GS_VOL)) != sum(x['vol'] or 0 for x in rows):
            fails.append('%s: volume total wrong' % grp)
        if num(g(r, GS_IMP)) != sum(x['imp_total'] for x in rows):
            fails.append('%s: impression total wrong' % grp)
        if abs(num(g(r, GS_CPC)) - max((x['cpc'] or 0) for x in rows)) > 0.001:
            fails.append('%s: top CPC wrong' % grp)
        kds = {x['kd'] for x in rows if x['kd'] is not None}
        for m in re.findall(r'KD (\d+)', cell_str(g(r, GS_PROSE))):
            if int(m) not in kds:
                fails.append('%s: prose says KD %s, group has %s' % (grp, m, sorted(kds)))

    # 6. only ONE group may hold each global superlative
    allkd = [x['kd'] for x in f if x['kd'] is not None] or [0]
    GMIN, GMAXV = min(allkd), max((x['vol'] or 0) for x in f)
    GMAXC = max((x['cpc'] or 0) for x in f)
    GMAXI = max(sum(x['imp_total'] for x in byg[k]) for k in byg)
    GMAXCLK = max(sum(x['clk_total'] for x in byg[k]) for k in byg)
    tests = [('lowest difficulty', 'lowest KD', lambda k: min([x['kd'] for x in byg[k] if x['kd'] is not None] or [999]) == GMIN),
             ('most expensive click', 'max CPC', lambda k: abs(max((x['cpc'] or 0) for x in byg[k]) - GMAXC) < 0.001),
             ('largest single term', 'max volume', lambda k: max((x['vol'] or 0) for x in byg[k]) == GMAXV),
             ('largest search console signal', 'max impressions', lambda k: sum(x['imp_total'] for x in byg[k]) == GMAXI),
             ('largest gsc signal', 'max impressions', lambda k: sum(x['imp_total'] for x in byg[k]) == GMAXI),
             ('most clicks', 'max clicks', lambda k: sum(x['clk_total'] for x in byg[k]) == GMAXCLK)]
    claims = collections.defaultdict(list)
    for r in gs:
        grp = cell_str(g(r, GS_GROUP))
        if grp not in byg:
            continue
        t = cell_str(g(r, GS_PROSE)).lower()
        for phrase, label, holds in tests:
            if phrase in t:
                claims[label].append(grp)
                if not holds(grp):
                    fails.append('%s claims "%s" but does not hold it' % (grp, phrase))
    for k, v in claims.items():
        if len(v) > 1:
            fails.append('%d groups claim "%s": %s' % (len(v), k, v))

    # 7. nothing is both kept and excluded, and no exclusion example is double-booked
    seen, kept = {}, {t.lower() for t in terms_list}
    for row in wb.rows('Exclusions')[1:]:
        cls = cell_str(g(row, EX_CLASS))
        if not cls or cls == 'TOTAL':
            continue
        for part in cell_str(g(row, EX_EXAMPLES)).split(';'):
            p = re.sub(r'\(.*?\)', '', part).strip().lower()
            if not p:
                continue
            if p in kept:
                fails.append('"%s" is both kept and listed as excluded' % p)
            if p in seen:
                fails.append('exclusion example "%s" booked under both "%s" and "%s"' % (p, seen[p][:40], cls[:40]))
            seen[p] = cls

    # 8. README totals
    txt = ' '.join(cell_str(c) for row in wb.rows('README') for c in row)
    for label, val in (('volume', sum(r['vol'] or 0 for r in f)), ('impressions', sum(r['imp_total'] for r in f)),
                       ('clicks', sum(r['clk_total'] for r in f))):
        if '{:,}'.format(val) not in txt:
            fails.append('README does not state the true %s total %s' % (label, '{:,}'.format(val)))

    # 9. surviving superlatives, for a human to read
    for r in gs:
        t = cell_str(g(r, GS_PROSE))
        for sup in ('the only', 'the clearest', 'the most', 'the largest', 'the softest', 'the lowest', 'the highest',
                    'nobody', 'every'):
            if sup in t:
                i = t.find(sup)
                print('  READ AND CONFIRM -> %s: ...%s...' % (cell_str(g(r, GS_GROUP)), t[max(0, i - 60):i + 90]))
    print()
    if fails:
        print('FAILURES:')
        for x in fails:
            print('  x', x)
        sys.exit(1)
    print('ALL MECHANICAL CHECKS PASS')


if __name__ == '__main__':
    main()
