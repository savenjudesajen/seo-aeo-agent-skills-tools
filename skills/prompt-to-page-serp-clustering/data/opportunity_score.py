#!/usr/bin/env python3
"""OPPORTUNITY SCORE - page-level build-order ranking, 0-100.

BASE   Siege Media's KOB (Keyword Opposition to Benefit): traffic value divided by difficulty,
       higher is better, traffic value = volume x CPC. Aggregated from keyword to page.
       https://www.siegemedia.com/strategy/kob-analysis
SHAPE  Minuttia's weighted-variable method: weights sum to 100, plotted 0-100, KD inversely
       proportional.  https://minuttia.com/keyword-selection/

THE RULE THAT MATTERS: a component is scored ONLY where its input was observed. An unobserved
input is never scored as zero. Where a page has no keyword carrying a CPC, the KOB weight is
redistributed across the components that were observed. Scoring absent CPC as zero lets a
tiny page outrank a large one whenever many keywords carry no CPC - the ad market has not
priced them, which is common for new or niche demand and is not the same as no value.

Impressions are an UPLIFT, never a weighted component: every net-new page has zero impressions
by definition and that is the reason to build it, not a reason to rank it last.

Percentile rank, not log or min-max scaling. Log scaling compresses the top of the set until a
trend difference outweighs a many-fold difference in value, so a mid-size page can outrank the
head page.

Input: rows of {page, volume, kd, cpc, impressions, trend} where trend is a keyword tool's
12-point monthly series as a comma-separated string (take it from the export or API; on-screen
tables often show only a sparkline).
"""
import json, math, argparse
from collections import defaultdict

W = {'kob': 60, 'vol': 25, 'trend': 15}   # sums to 100
IMP_UPLIFT = 15.0
KD_FLOOR = 5.0                            # stops near-zero-difficulty pages dividing to infinity
TREND_LO, TREND_HI = 0.5, 2.0             # clamp so one spiky term cannot dominate


def trend_ratio(series):
    """Second half over first half of the 12-point series, clamped. None when unusable."""
    if not series:
        return None
    try:
        v = [float(x) for x in str(series).split(',') if str(x).strip()]
    except ValueError:
        return None
    if len(v) < 6:
        return None
    h = len(v) // 2
    a = sum(v[:h]) / h
    b = sum(v[h:]) / len(v[h:])
    if a <= 0:
        return None
    return max(TREND_LO, min(TREND_HI, b / a))


def pct_ranker(values):
    """Percentile rank 0-100 over the observed values; ties share the midrank."""
    s = sorted(v for v in values if v is not None)
    n = len(s)
    def f(x):
        if x is None:
            return None
        if n <= 1:
            return 50.0
        lo = sum(1 for y in s if y < x)
        eq = sum(1 for y in s if y == x)
        return 100.0 * (lo + (eq - 1) / 2) / (n - 1)
    return f


def trend_points(t):
    if t is None:
        return None
    if t <= 1.0:                                   # flat maps to 50
        return 50 * (t - TREND_LO) / (1.0 - TREND_LO)
    return 50 + 50 * (t - 1.0) / (TREND_HI - 1.0)


def score(rows):
    agg = defaultdict(lambda: {'vol': 0, 'tv': 0.0, 'kdn': 0.0, 'kdd': 0,
                               'imp': 0, 'trn': 0.0, 'trd': 0, 'n': 0, 'cpcvol': 0})
    for r in rows:
        p = r.get('page')
        if not p:
            continue
        v = r.get('volume') or 0
        kd = r.get('kd')
        cpc = r.get('cpc') or 0
        t = trend_ratio(r.get('trend'))
        d = agg[p]
        d['n'] += 1
        d['vol'] += v
        d['tv'] += v * cpc
        d['imp'] += r.get('impressions') or 0
        if cpc > 0:
            d['cpcvol'] += v
        if kd is not None and v > 0:
            d['kdn'] += kd * v
            d['kdd'] += v
        if t is not None and v > 0:
            d['trn'] += t * v
            d['trd'] += v

    raw = {}
    for p, d in agg.items():
        kd = d['kdn'] / d['kdd'] if d['kdd'] else None
        kde = max(KD_FLOOR, kd) if kd is not None else None
        observed_cpc = d['cpcvol'] > 0 and d['tv'] > 0 and kde is not None
        raw[p] = {'kob': (d['tv'] / kde) if observed_cpc else None,
                  'vol': d['vol'],
                  'imp': d['imp'],
                  'trend': (d['trn'] / d['trd']) if d['trd'] else None,
                  'kd': kd, 'tv': d['tv'], 'keywords': d['n'],
                  'cpc_coverage': (d['cpcvol'] / d['vol']) if d['vol'] else 0.0}

    f_kob = pct_ranker([v['kob'] for v in raw.values()])
    f_vol = pct_ranker([v['vol'] for v in raw.values()])
    max_imp = max((v['imp'] for v in raw.values()), default=0) or 1

    out = {}
    for p, v in raw.items():
        comps = {'kob': f_kob(v['kob']), 'vol': f_vol(v['vol']), 'trend': trend_points(v['trend'])}
        live = {k: W[k] for k, s in comps.items() if s is not None}
        total = sum(live.values())
        core = sum(comps[k] * (w / total) for k, w in live.items()) if total else 0.0
        uplift = IMP_UPLIFT * math.log1p(v['imp']) / math.log1p(max_imp) if v['imp'] > 0 else 0.0
        out[p] = {'score': round(min(100.0, core + uplift), 1),
                  'core': round(core, 1), 'impressions_uplift': round(uplift, 1),
                  'components': {k: (round(s, 1) if s is not None else None)
                                 for k, s in comps.items()},
                  'weights_applied': sorted(live), **v}
    return out


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--rows', required=True,
                   help='JSON: [{page, volume, kd, cpc, impressions, trend}, ...]')
    a.add_argument('--out', default='opportunity_score.json')
    args = a.parse_args()
    res = score(json.load(open(args.rows)))
    json.dump(res, open(args.out, 'w'), indent=1)

    scores = sorted(v['score'] for v in res.values())
    no_kob = [p for p, v in res.items() if v['components']['kob'] is None]
    print(f"pages scored      : {len(res)}")
    print(f"range             : {scores[0]} - {scores[-1]}  median {scores[len(scores)//2]}")
    print(f"KOB applied       : {len(res)-len(no_kob)} of {len(res)}  "
          f"({len(no_kob)} pages had no observed CPC - weight redistributed, not zeroed)")
    print(f"impressions uplift: {sum(1 for v in res.values() if v['impressions_uplift']>0)} pages")
    print("\nSTATE IN THE DELIVERABLE: the score ranks build order WITHIN this set. It is not a "
          "forecast and does not carry to another keyword set, because percentile rank is "
          "relative to the pages in it. Pages with no keywords carry no score and must say so "
          "in words, never a blank or a zero.")


if __name__ == '__main__':
    main()
