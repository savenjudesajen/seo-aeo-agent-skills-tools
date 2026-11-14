#!/usr/bin/env python3
"""Compare original checkpoints vs fresh QA re-fetches: transcription fidelity + SERP stability.

Gate 5. Re-fetch a stratified sample into serps_qa/ with a FRESH agent in do-not-skip mode,
then run this from the working directory (it reads config.json like the other scripts).

Both checkpoints go through the engine's own rows_of / norm_url, so this gate compares exactly
what the clustering compared: organic position (not the provider's absolute rank), the top
cluster.topn window by RANK (not by list position), a lean provider's bare URL strings, and the
same URL normalization. Every serps_qa/*.json is read, whatever the prompt_id prefix.

Interpretation:
- Most of the top 10 usually persists; a few URLs moving is normal. Hour-scale SERP churn is
  real.
- A volatile SERP is NOT a problem if its page assignment rests on signal A or a recorded
  override. Cluster membership is ephemeral evidence; overrides are the durable layer.
- Google can return the SAME URL at two ranks — dedupe URL sets before counting (this does).

Exit 1 when any URL is malformed or a QA file has no original checkpoint; otherwise 0.
"""
import json, glob, os, statistics, sys

try:
    from cluster_engine import rows_of, norm_url, TOPN
except SystemExit:
    raise
except Exception as e:                      # e.g. no config.json in the working directory
    raise SystemExit(f"fidelity_check: cannot load cluster_engine's normalizer "
                     f"({e.__class__.__name__}: {e}). Run from the working directory that holds "
                     f"config.json, with cluster_engine.py next to this script.")


def window(d):
    """Normalized, de-duplicated top-TOPN urls in organic rank order."""
    seen, out = set(), []
    for x in rows_of(d):
        if x['r'] > TOPN or x.get('near_miss'):
            continue
        u = norm_url(x['url'])
        if u and u not in seen:
            seen.add(u)
            out.append(u)
    return out


def malformed_urls(d):
    """Raw urls that would not survive normalization as a real host (space, or no dot in host)."""
    return [x['url'] for x in rows_of(d)
            if x['r'] <= TOPN and (' ' in str(x['url']).strip()
                                   or '.' not in norm_url(x['url']).split('/')[0])]


res, no_original = [], []
for f in sorted(glob.glob('serps_qa/*.json')):
    new = json.load(open(f))
    pid = new.get('prompt_id') or os.path.basename(f)[:-5]
    orig = f'serps/{pid}.json'
    if not os.path.exists(orig):
        no_original.append(pid)
        continue
    old = json.load(open(orig))
    ou, nu_ = window(old), window(new)
    os_, ns = set(ou), set(nu_)
    od = {u.split('/')[0] for u in os_}
    nd = {u.split('/')[0] for u in ns}
    top3 = len(set(ou[:3]) & set(nu_[:3]))
    res.append((pid, len(os_ & ns), len(od & nd), len(od), top3, malformed_urls(old) + malformed_urls(new)))

if no_original:
    print(f"QA files with no original checkpoint in serps/: {no_original}")
if not res:
    print('fidelity_check: no serps_qa/ sample found')
    raise SystemExit(1 if no_original else 0)

w = max(11, max(len(r[0]) for r in res) + 2)
print(f"{'pid':{w}}{f'url_int/{TOPN}':12}{'dom_int':9}{'top3_int':9}malformed")
for pid, uo, do, nd_, t3, mal in res:
    print(f"{pid:{w}}{uo:<12}{do}/{nd_:<6}{t3:<9}{mal if mal else '-'}")

u = [r[1] for r in res]
d = [r[2] for r in res]
print(f"\nURL overlap: min {min(u)} / median {statistics.median(u)} / max {max(u)} (of {TOPN})")
print(f"domain overlap median: {statistics.median(d)}")
low = [(r[0], r[1]) for r in res if r[1] < TOPN / 2]
if low:
    print(f"\nVOLATILE (<{TOPN // 2}/{TOPN}): {low}")
    print("  -> verify each assignment rests on signal A or a recorded override, NOT on cluster membership.")
mal = sum(len(r[5]) for r in res)
print(f"malformed URLs: {mal} (must be 0)")
sys.exit(1 if mal or no_original else 0)
