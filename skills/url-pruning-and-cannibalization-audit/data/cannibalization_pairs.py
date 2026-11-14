#!/usr/bin/env python3
"""Query cannibalization metrics from a Search Console query x page export.

Usage:
  python cannibalization_pairs.py gsc.csv out_prefix [--brand REGEX] [--max-words 8]
         [--min-impr 10] [--max-pos 20] [--share 0.2] [--sim-high 0.30]
         [--rotation rot.csv] [--live live.txt] [--redirects rules.csv]
         [--page-types types.tsv] [--article-prefix /blog/]
         [--similarity sim.tsv] [--primary map.tsv]

gsc.csv     query, page, clicks, impressions, position (header names, any order).
            Optional date column (YYYY-MM-DD): weekly rotation is then computed here.
            position is the average position (1-based). For the BigQuery bulk export
            use sum_position / impressions + 1 (see data/sql/query_by_page.sql).
rot.csv     query, weeks, rotations, double_weeks, tops (pipe-separated URLs), from
            data/sql/weekly_rotation_summary.sql. Use it when the weekly rows are too
            large to download.
live.txt    one URL or path per line: the cleaned URL list. Pages outside it are dropped.
rules.csv   Old Path, New Path. Query data on an old path moves to its final target.
types.tsv   url<TAB>page type, using the labels in reference/sheet-columns.md: Home, Offer,
            Campaign landing, Article, Guide, Short answer, Listing or hub, Profile, Other.
            Only pages typed Offer or Campaign landing get the buying-page preference.
            Untyped pages: '/' is Home, paths under an --article-prefix are Article
            (default /blog/), everything else is Other.
sim.tsv     url_a<TAB>url_b<TAB>similarity (text cosine with menus and footers removed).
map.tsv     query<TAB>intended url (page map). Overrides the owner pick.

Query filter (noise): drops brand queries, queries longer than --max-words words (AI-prompt
style queries from rank trackers) and queries with search operators or quotes.

For each contested query one page is the owner; every other ranking page forms a pair with it.
A query counts as shared for a pair when both URLs have --min-impr impressions or more,
both average --max-pos or better, and the other page holds --share or more of the site's
impressions on it. Severity:
  High    overlap 30%+ with 2+ shared queries and a contested query of 100+ impressions
          or a rotating query
  Medium  overlap 10 to 29% on the same terms, or rotation on 3+ shared queries
  Low     the rest
Rotation: the site's top URL for the query changed 3+ times across the weeks.
These thresholds are starting defaults; calibrate them per site and record them in Method.

Writes <out>_pairs.tsv and <out>_queries.tsv. It computes metrics only. The Resolution
(Merge into owner, Re-target, Split anchors, Wait), the anchor split and the Reason are
written by hand per pair after a live read and a results-page check. The Hint column only
says which resolution the numbers point to.
"""
import sys, csv, re, collections, datetime
from urllib.parse import urlparse

PAGE_TYPES = ('Home', 'Offer', 'Campaign landing', 'Article', 'Guide', 'Short answer',
              'Listing or hub', 'Profile', 'Other')
BUYING = {'offer', 'campaign landing'}
OPS = re.compile(r'["%:]|(^|\s)-site|site:')


def norm(u):
    u = str(u).strip()
    p = urlparse(u)
    path = p.path if p.netloc else u.split('?')[0].split('#')[0]
    return (path.rstrip('/') or '/').lower()


def arg(a, k, d=None):
    return a[a.index(k) + 1] if k in a else d


def read_tsv(path, n):
    out = []
    if not path:
        return out
    for line in open(path, encoding='utf-8'):
        parts = line.rstrip('\n').split('\t')
        if len(parts) >= n and parts[0]:
            out.append(parts[:n])
    return out


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__); sys.exit(2)
    src, out = a[0], a[1]
    brand = re.compile(arg(a, '--brand'), re.I) if arg(a, '--brand') else None
    max_words = int(arg(a, '--max-words', 8))
    min_impr = float(arg(a, '--min-impr', 10))
    max_pos = float(arg(a, '--max-pos', 20))
    share_min = float(arg(a, '--share', 0.2))
    sim_high = float(arg(a, '--sim-high', 0.30))
    article_prefixes = [p.strip().lower() for p in arg(a, '--article-prefix', '/blog/').split(',') if p.strip()]
    types = {norm(u): t.strip() for u, t in read_tsv(arg(a, '--page-types'), 2)}
    known = {t.lower() for t in PAGE_TYPES}
    unknown = sorted({t for t in types.values() if t.lower() not in known})
    if unknown:
        print(f'note: page types not in the default list (no buying-page preference): {unknown[:5]}')
    sim = {}
    for x, y, s in read_tsv(arg(a, '--similarity'), 3):
        try:
            sim[frozenset((norm(x), norm(y)))] = float(s)
        except ValueError:
            pass
    intended = {q.lower().strip(): norm(u) for q, u in read_tsv(arg(a, '--primary'), 2)}
    live = None
    if arg(a, '--live'):
        live = {norm(l) for l in open(arg(a, '--live'), encoding='utf-8') if l.strip()}
    red = {}
    if arg(a, '--redirects'):
        for r in csv.DictReader(open(arg(a, '--redirects'), encoding='utf-8-sig')):
            o, n = norm(r.get('Old Path') or r.get('old') or ''), norm(r.get('New Path') or r.get('new') or '')
            if o and n and o != n:
                red[o] = n

    def final(p):
        for _ in range(10):
            if p not in red:
                break
            p = red[p]
        return p

    def keep_query(q):
        if not q or (brand and brand.search(q)) or OPS.search(q):
            return False
        return len(q.split()) <= max_words

    agg = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
    weekly = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0])))
    dropped = kept = 0.0
    with open(src, newline='', encoding='utf-8-sig') as f:
        rd = csv.DictReader(f)
        cols = {c.lower().strip(): c for c in rd.fieldnames}
        for need in ('query', 'page', 'clicks', 'impressions', 'position'):
            if need not in cols:
                sys.exit(f'missing column {need} in {src}')
        has_date = 'date' in cols
        for r in rd:
            q = r[cols['query']].strip().lower()
            i = float(r[cols['impressions']] or 0)
            if not keep_query(q):
                dropped += i
                continue
            u = final(norm(r[cols['page']]))
            if live is not None and u not in live:
                continue
            kept += i
            c = float(r[cols['clicks']] or 0); p = float(r[cols['position']] or 0)
            s = agg[(q, u)]; s[0] += c; s[1] += i; s[2] += p * i
            if has_date and r[cols['date']]:
                y, m, d = map(int, r[cols['date']][:10].split('-'))
                wk = datetime.date(y, m, d).isocalendar()[:2]
                w = weekly[q][wk][u]; w[0] += p * max(i, 1); w[1] += max(i, 1)

    rot = {}
    if arg(a, '--rotation'):
        for r in csv.DictReader(open(arg(a, '--rotation'), encoding='utf-8-sig')):
            tops = {norm(t) for t in (r.get('tops') or '').split('|') if t.strip()}
            rot[r['query'].strip().lower()] = (int(r.get('rotations') or 0), tops)

    qp, page_total = {}, collections.Counter()
    for (q, u), (c, i, pi) in agg.items():
        pos = pi / i if i else 0
        page_total[u] += i
        if i >= min_impr and 0 < pos <= 30:
            qp.setdefault(q, {})[u] = (c, i, pos)

    def ptype(u):
        if u in types:
            return types[u]
        if u == '/':
            return 'Home'
        return 'Article' if any(u.startswith(p.rstrip('/') + '/') for p in article_prefixes) else 'Other'

    def pick_owner(q, pages):
        if q in intended and intended[q] in pages:
            return intended[q], 'page map'
        best = sorted(pages, key=lambda u: (-pages[u][0], -pages[u][1], pages[u][2]))[0]
        buying = [u for u in pages if ptype(u).lower() in BUYING]
        if buying and best not in buying:
            return sorted(buying, key=lambda u: (-pages[u][1], pages[u][2]))[0], 'buying page over supporting content'
        return best, 'most clicks, then impressions, then position'

    def rotation(q, pages):
        weeks = weekly.get(q)
        if weeks:
            tops = []
            for wk in sorted(weeks):
                ranked = sorted(((u2, v[0] / v[1]) for u2, v in weeks[wk].items() if u2 in pages), key=lambda kv: kv[1])
                if ranked:
                    tops.append(ranked[0][0])
            return sum(1 for x, y in zip(tops, tops[1:]) if x != y), set(tops)
        return rot.get(q, (0, set()))

    pairs = collections.defaultdict(lambda: {'q': [], 'sh': 0.0, 'n': 0, 'big': 0, 'rot': 0})
    qrows = []
    for q, pages in qp.items():
        if len(pages) < 2:
            continue
        T = sum(v[1] for v in pages.values())
        owner, why = pick_owner(q, pages)
        r_n, r_tops = rotation(q, pages)
        qrows.append([q, len(pages), int(T), owner, why, r_n,
                      ' | '.join(f'{u} ({int(v[1])} impr, pos {v[2]:.1f})' for u, v in sorted(pages.items(), key=lambda kv: -kv[1][1]))])
        for u, (c, i, pos) in pages.items():
            if u == owner:
                continue
            real = i / T >= share_min and pos <= max_pos and pages[owner][2] <= max_pos
            pr = pairs[(owner, u)]
            pr['q'].append((q, int(i), round(pos, 1), round(pages[owner][2], 1), real))
            if real:
                pr['sh'] += i; pr['n'] += 1
                if T >= 100:
                    pr['big'] += 1
                if r_n >= 3 and (not r_tops or (u in r_tops and owner in r_tops)):
                    pr['rot'] += 1

    prow = []
    for (owner, u), pr in pairs.items():
        ov = pr['sh'] / page_total[u] if page_total[u] else 0
        strong = pr['n'] >= 2 and (pr['big'] or pr['rot'])
        sev = 'High' if ov >= 0.30 and strong else 'Medium' if ov >= 0.10 and strong else 'Low'
        if sev == 'Low' and pr['rot'] >= 3:
            sev = 'Medium'
        s = sim.get(frozenset((owner, u)))
        hi = s is not None and s >= sim_high
        if sev == 'Low':
            hint = 'similar text, few shared queries: intent read, lean Split anchors' if hi else 'low overlap: no action'
        elif s is None:
            hint = 'similarity missing: score the pair'
        elif hi:
            hint = 'similar and sharing queries: Merge into owner candidate (live read first)'
        else:
            hint = 'sharing queries with different text: Re-target the other page'
        if ptype(u).lower() in BUYING and ptype(owner).lower() not in BUYING and sev != 'Low':
            hint += '; other page is a buying page: never merge it into supporting content'
        top = sorted([x for x in pr['q'] if x[4]] or pr['q'], key=lambda x: -x[1])[:3]
        prow.append([owner, ptype(owner), u, ptype(u), pr['n'], len(pr['q']), f'{ov:.0%}', int(pr['sh']),
                     int(page_total[u]), pr['big'], pr['rot'], '' if s is None else f'{s:.2f}', sev, hint,
                     '; '.join(f'{q} ({i} impr, pos {op} vs {xp})' for q, i, xp, op, _ in top)])
    order = {'High': 0, 'Medium': 1, 'Low': 2}
    prow.sort(key=lambda r: (order[r[12]], -r[7]))
    qrows.sort(key=lambda r: -r[2])
    with open(out + '_pairs.tsv', 'w', encoding='utf-8') as f:
        f.write('\t'.join(['Owner URL', 'Owner type', 'Other URL', 'Other type', 'Shared queries',
                           'All common queries', 'Query overlap %', 'Shared impressions', 'Other impressions',
                           'Contested queries 100+', 'Weekly swaps', 'Text similarity', 'Severity', 'Hint',
                           'Top shared queries (owner pos vs other pos)']) + '\n')
        for r in prow:
            f.write('\t'.join(map(str, r)) + '\n')
    with open(out + '_queries.tsv', 'w', encoding='utf-8') as f:
        f.write('\t'.join(['Query', 'Ranking URLs', 'Impressions', 'Owner', 'Owner picked by', 'Rotations',
                           'Pages']) + '\n')
        for r in qrows:
            f.write('\t'.join(map(str, r)) + '\n')
    tot = dropped + kept
    print(f'noise filter set aside {dropped / tot:.0%} of impressions' if tot else 'no rows')
    print(f'queries kept {len(qp)}  contested {len(qrows)}  pairs {len(prow)}  '
          + str(collections.Counter(r[12] for r in prow)))


if __name__ == '__main__':
    main()
