#!/usr/bin/env python3
"""Standing final gate: run after every page_assign; ZERO failures required before any deliverable.

Scope = ALL prompts in prompts_master.csv. Never scope it to a single tier: a tier constant
silently 'passes' a partial run.

Its most common catch: an override keyed on a RECONSTRUCTED prompt text (from a truncated
display) that silently matched nothing. NEVER hand-type override keys — copy exact text from
prompts_master, or key on prompt_id and resolve the text programmatically.

Thin-checkpoint threshold is 5, because a lean provider legitimately returns 6-9 URLs.
"""
import csv, json, glob, collections, sys, os


def results_of(d):
    """Checkpoint results as dicts. A lean provider returns a bare list of URL strings."""
    out = []
    for i, x in enumerate(d.get('results') or []):
        if isinstance(x, str):
            out.append({'r': i + 1, 'url': x})
        elif isinstance(x, dict) and x.get('url'):
            out.append(x)
    return out

fail = []
master = {r['prompt_id']: r for r in csv.DictReader(open('prompts_master.csv'))}
target = set(master)                       # ALL tiers
pm = list(csv.DictReader(open('page_map.csv')))
ids = [r['prompt_id'] for r in pm]

if set(ids) != target:
    fail.append(f"coverage: map has {len(ids)} vs target {len(target)}; "
                f"missing={sorted(target - set(ids))[:5]} extra={sorted(set(ids) - target)[:5]}")
if len(ids) != len(set(ids)):
    fail.append('duplicate prompt_ids in page_map')

pages = collections.defaultdict(list)
for r in pm:
    pages[r['page']].append(r)
for page, rs in pages.items():
    if page == 'REVIEW':
        continue
    prims = [r for r in rs if r['role'] == 'primary']
    if len(prims) != 1:
        fail.append(f"page {page}: {len(prims)} primaries")
    # Two different clusters sharing ONE net-new page key means unrelated clusters were fused
    # (an empty or colliding centroid slug). The key is non-empty, so no other check sees it.
    if page.startswith('NET-NEW'):
        cids = {r.get('cluster_id') for r in rs if r.get('cluster_id')}
        if len(cids) > 1:
            fail.append(f"{page}: fuses {len(cids)} different clusters ({sorted(cids)}) onto one "
                        f"net-new page key")

for r in pm:
    if not r['rationale'].strip():
        fail.append(f"empty rationale: {r['prompt_id']}")
    if not r['page'].strip():
        fail.append(f"empty page: {r['prompt_id']}")

ovr = list(csv.DictReader(open('overrides.csv')))
bytext = {r['prompt'].strip(): r for r in pm}
for o in ovr:
    row = bytext.get(o['prompt_text'].strip())
    if row is None:
        fail.append(f"override target prompt not in map: {o['prompt_text'][:50]}")
    elif row['page'] != o['target_page']:
        fail.append(f"override not applied: {o['prompt_text'][:40]} -> {row['page']} != {o['target_page']}")

# page_summary is written by page_assign; qa_grain_check writes flags back to page_map AFTER
# that, so the two artifacts can disagree about how many rows need review. Catch it here.
if os.path.exists('page_summary.csv'):
    _pm_nr = collections.Counter()
    for r in pm:
        if r.get('needs_review') == 'yes':
            _pm_nr[r['page']] += 1
    for s in csv.DictReader(open('page_summary.csv')):
        if 'needs_review_rows' not in s:
            break
        want, got = _pm_nr.get(s['page'], 0), int(s.get('needs_review_rows') or 0)
        if want != got:
            fail.append(f"page_summary disagrees with page_map on needs_review for "
                        f"{s['page']}: summary={got} map={want} (re-run page_assign after "
                        f"qa_grain_check writes flags back)")

if not os.path.exists('run_caveat.txt'):
    fail.append('run_caveat.txt missing - the SERP-overlap-as-proxy-for-citations caveat must '
                'travel with the run and be stated in the deliverable')

# a run_config is the only record of which thresholds actually produced this map
if not os.path.exists('run_config.json'):
    fail.append('run_config.json missing - cannot prove which thresholds produced this map')
else:
    # Compare against the EFFECTIVE config (defaults merged), via the engine's own load_cfg -
    # reading config.json raw KeyErrors on any partial config, and the GATE crashing is worse
    # than the engine crashing: it is the thing that certifies the run.
    _rc = json.load(open('run_config.json'))
    try:
        from cluster_engine import load_cfg as _load_cfg
        _cfg = _load_cfg()
    except SystemExit:
        raise
    except Exception as e:
        _cfg = None
        fail.append(f'cannot load effective config to verify thresholds ({e.__class__.__name__}: {e})')
    if _cfg is not None:
        for k in ('T', 'one_shared_max_df'):
            if _rc.get(k) != _cfg['cluster'].get(k):
                fail.append(f"run_config {k}={_rc.get(k)} != config.json {k}={_cfg['cluster'].get(k)} "
                            f"- this map was built at a swept threshold, not the signed-off one")

mc = list(csv.DictReader(open('merge_candidates.csv')))
spells = 0
for f in glob.glob('serps/*.json'):            # NOT serps/p*.json - see page_assign
    d = json.load(open(f))
    pid = d['prompt_id']
    if pid not in target:
        continue
    _res = results_of(d)
    if len(_res) < 5:
        fail.append(f"thin checkpoint {pid}: {len(_res)} results")
    if any(not str(x.get('url', '')).startswith('http') for x in _res):
        fail.append(f"malformed url in {pid}")
    if d.get('spell') or d.get('original_spell_issue'):
        spells += 1

n_ck = sum(1 for f in glob.glob('serps/*.json') if json.load(open(f))['prompt_id'] in target)
if n_ck != len(target):
    fail.append(f"checkpoints {n_ck} != target {len(target)}")

print(f"checks: coverage={len(ids)}/{len(target)} pages={len(pages)} overrides={len(ovr)} "
      f"merge_candidates={len(mc)} spell_cases={spells}")
if fail:
    print('FAILURES:')
    for x in fail:
        print('  -', x)
    sys.exit(1)
print('INTEGRITY GATE: PASS (0 failures)')
