#!/usr/bin/env python3
"""Prompt-to-page SERP clustering engine - CONFIG-DRIVEN (portable across projects).

All client-specific values live in config.json (brand domain, competitors, hub hosts,
thresholds, tier names). No brand is hardcoded. Override the path with AEO_CONFIG.

JOIN RULE (thresholds need reviewer sign-off per project):
  shared >= T (default 2)                              -> join
  shared == 1 AND df(url) <= one_shared_max_df
                AND url is not a hub host
                AND prompt is not a brand-comparison   -> join   (genuine co-citation)
  otherwise                                            -> own cluster

  df(url) = document frequency: how many of the corpus SERPs contain that URL.
  Rationale: a URL present in many SERPs carries no information (IDF). The most shared URLs
  are usually category listicles, and cross-competitor bleed ("Brand vs RivalOne" fusing
  into "Brand vs RivalTwo") starts only a little above the df cap. A DOMAIN-based hub list
  is insufficient on its own: most promiscuous URLs are ordinary publishers, not hubs.

  WARNING: 1-shared joins are NEVER auto-accepted. On hand-read, a large share prove
  coincidental even at df <= 5. Every one must go to the QA gate.

ESCALATION (post-hoc, not at creation): any prompt whose FINAL cluster has size 1 could not
be mapped by SERP overlap. Those go to escalated.csv for demand adjudication (new page vs
map-to-existing-with-rationale). A centroid that gathered members is NOT escalated.

Outputs: clusters.csv, merge_candidates.csv, escalated.csv, drift_quarantine.csv,
         spell_watchlist.csv, thin_serps.csv
"""
import csv, json, os, re, sys, collections
from urllib.parse import urlsplit

DEFAULTS = {
    'cluster': {'T': 2, 'topn': 10, 'one_shared_max_df': 5, 'min_serp_urls': 3,
                # neutral backstop; tune per category in config.json (review sites, marketplaces)
                'hub_hosts': ['reddit.com', 'youtube.com', 'wikipedia.org', 'linkedin.com'],
                'never_one_shared_join': [r'\bvs\b', r'\bversus\b', 'which is better']},
    'signals': {'a_min_hits': 2, 'a_high_confidence_max_rank': 5,
                'a_max_rank_considered': 10, 'near_miss_rank_range': [11, 20]},
    # category terms are project-specific: build them from the client's own keyword set
    'meaning_tokens': [],
    'brand': {'domain': '', 'tokens': []}, 'competitors': [], 'page_inventory': '',
}


# When a config key is a dict but a hand-editor is most likely to type a bare scalar, name the
# sub-key that scalar means. Without this, "brand": "brand.example" type-errors far later at
# CFG['brand']['domain'] with a message naming neither config.json nor 'brand'.
SCALAR_ALIAS = {'brand': 'domain'}


def load_cfg(path=None):
    """Config over signed-off defaults. The portability contract is 'edit config.json, never the
    scripts' - so a half-edited config must degrade to the defaults, not KeyError at import.
    Shared with page_assign.py and integrity_gate.py so all three see the SAME effective
    config; a second copy of this merge drifts from this one silently, and the engine then
    accepts a config that a later step dies on - a half-run rather than a clean stop."""
    src = path or os.environ.get('AEO_CONFIG', 'config.json')
    raw = json.load(open(src))
    out = {k: (dict(v) if isinstance(v, dict) else list(v) if isinstance(v, list) else v)
           for k, v in DEFAULTS.items()}
    for k, v in raw.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k].update(v)
        elif isinstance(out.get(k), dict) and not isinstance(v, dict):
            sub = SCALAR_ALIAS.get(k)
            if sub and isinstance(v, (str, int, float)):
                out[k] = dict(out[k]); out[k][sub] = v      # "brand": "brand.example" -> brand.domain
            else:
                raise SystemExit(f"{src}: '{k}' must be an object like "
                                 f"{json.dumps(DEFAULTS[k])[:80]}, got {type(v).__name__} {v!r}")
        else:
            out[k] = v
    return out


CFG = load_cfg()
T = int(os.environ.get('CLUSTER_T', CFG['cluster']['T']))
TOPN = int(CFG['cluster']['topn'])
DF_MAX = int(os.environ.get('ONE_SHARED_MAX_DF', CFG['cluster']['one_shared_max_df']))
HUBS = tuple(CFG['cluster']['hub_hosts'])
NO_JOIN = [re.compile(p, re.I) for p in CFG['cluster']['never_one_shared_join']]
MEANING = set(CFG['meaning_tokens'])
BRAND = CFG['brand']['domain']
MIN_URLS = int(CFG['cluster'].get('min_serp_urls', 3))


def norm_url(u):
    txt = str(u or '').strip()
    s = urlsplit(txt)
    # A lean provider can return a URL WITHOUT its scheme ('www.site.example/path'). urlsplit
    # reads that as a bare path, so it would skip the www/tracking-token normalization below and
    # never match the same page written with a scheme. Re-parse it as a URL when its first
    # segment looks like a host (alphabetic TLD, no spaces).
    if not s.netloc and re.match(r'^([a-z0-9-]+\.)+[a-z]{2,}(/|\?|$)', txt.lower()):
        s = urlsplit('//' + txt)
    host = re.sub(r'^www\.', '', s.netloc.lower())
    if not host:          # bare or relative string - light normalization, never a bogus host
        raw = re.sub(r'^https?://', '', str(u or '').strip().lower())
        return raw.split('?')[0].rstrip('/')
    path = s.path.rstrip('/')
    # srsltid is a PER-REQUEST Google Shopping/organic tracking token: the same page returns a
    # different one on every fetch, so leaving it in makes one URL look like N distinct URLs and
    # silently UNDER-counts overlap between prompts.
    q = '&'.join(sorted(p for p in s.query.split('&')
                        if p and not p.lower().startswith(('utm_', 'ref=', 'gclid', 'fbclid',
                                                           'srsltid', 'mc_cid', 'mc_eid',
                                                           '_ga', 'igshid', 'msclkid')))) if s.query else ''
    return f"{host}{path}" + (f"?{q}" if q else '')


def is_brand_url(nurl):
    """Host-anchored brand test on a NORMALIZED url (host+path).

    A substring test ('brand.example' in url) passes 'notbrand.example/x' and
    'brand.example.evil.example/x'.
    """
    host = nurl.split('/')[0].split('?')[0]
    bd = re.sub(r'^www\.', '', BRAND.lower()).rstrip('/')
    return bool(bd) and (host == bd or host.endswith('.' + bd))


def is_hub(nurl):
    host = nurl.split('/')[0].split('?')[0]
    return any(host == h or host.endswith('.' + h) for h in HUBS)


def is_brand_comparison(text):
    return any(p.search(text) for p in NO_JOIN)


def spell_assess(prompt, spell, results):
    """showing_results_for + meaning-token swap -> quarantine. did_you_mean -> content check."""
    if not spell:
        return 'ok', ''
    sugg = spell.get('keyword', '') if isinstance(spell, dict) else str(spell)
    styp = spell.get('type', '') if isinstance(spell, dict) else ''
    a = set(re.findall(r"[a-z]+", prompt.lower()))
    b = set(re.findall(r"[a-z]+", sugg.lower()))
    lost, gained = a - b, b - a
    if not (lost & MEANING and gained & MEANING):
        return 'ok', f'benign spell ({styp}): {sugg}'
    tok = sorted(lost & MEANING)[0]
    hits = sum(1 for x in results if tok in (x.get('url', '') + ' ' + x.get('title', '')).lower())
    if styp == 'showing_results_for':
        return 'quarantine', f'results replaced with "{sugg}"; original-token hits={hits}'
    if hits == 0:
        return 'quarantine', f'did_you_mean "{sugg}" AND zero results mention "{tok}"'
    if hits <= 2:
        return 'watch', f'did_you_mean "{sugg}"; only {hits} results mention "{tok}"'
    return 'ok', f'did_you_mean "{sugg}" but {hits} results kept "{tok}" -> SERP intact'


def rows_of(d):
    """Normalize a checkpoint's `results` to [{'r':rank,'url':...,'title':...}].

    A lean SERP provider returns a BARE LIST OF URL STRINGS in rank order. Indexing that with
    x['url'] raises mid-run. Rank comes from the payload when present, else list position.
    """
    out = []
    for i, x in enumerate(d.get('results') or []):
        if isinstance(x, str):
            out.append({'r': i + 1, 'url': x, 'title': ''})
            continue
        if not isinstance(x, dict) or not x.get('url'):
            continue
        try:
            r = int(x.get('r'))
            r = r if r > 0 else i + 1
        except (TypeError, ValueError):
            r = i + 1
        out.append({'r': r, 'url': x['url'], 'title': x.get('title', ''),
                    'near_miss': bool(x.get('near_miss'))})
    # 'r' is ORGANIC POSITION, not the provider's rank_absolute. Providers number EVERY SERP
    # block - AI Overview, video, images, people-also-ask - so the 8th organic result can carry
    # rank_absolute 13. Windowing or rank-gating on that number silently drops real organic
    # results, and drops MORE of them on exactly the AI-feature-heavy SERPs an AEO project
    # cares most about, and the loss looks like low overlap rather than a bug. Position is
    # assigned over RANK order, never list order, so an out-of-order requery patch cannot shift
    # the window. The provider's raw value is kept as r_absolute for provenance.
    out.sort(key=lambda z: z['r'])
    for _n, _x in enumerate(out, 1):
        _x['r_absolute'] = _x['r']
        _x['r'] = _n
    return out


def main():
    if not MEANING:
        print("WARNING: meaning_tokens is empty in config.json - spell triage cannot tell a "
              "category-term swap from a benign correction, so no SERP will be quarantined for "
              "spell drift. Add the category terms from the client's own keyword set.", file=sys.stderr)
    master = {}
    malformed = []
    for r in csv.DictReader(open('prompts_master.csv')):
        if not (r.get('prompt_id') or '').strip() or not (r.get('prompt') or '').strip():
            malformed.append(r)
            continue
        master[r['prompt_id']] = r
    if malformed:
        print(f"WARNING: {len(malformed)} prompts_master rows dropped for a blank prompt_id or "
              f"prompt. A blank id collapses every such row onto one key and silently shrinks "
              f"the corpus.", file=sys.stderr)
    serps, missing = {}, []
    for pid, m in master.items():
        f = f'serps/{pid}.json'
        if not os.path.exists(f):
            missing.append(pid)
            continue
        d = json.load(open(f))
        rows = rows_of(d)
        # The clustering WINDOW is defined by RANK, not by list position. Checkpoints store 20
        # (fetch_depth) and a requery patch can append rows out of order, so slicing [:TOPN]
        # silently shifts the window and the run still completes clean.
        window = [x for x in rows if x['r'] <= TOPN and not x.get('near_miss')]
        # dedupe keeping the first (best-ranked) occurrence - Google can return the SAME url
        # at two ranks.
        _seen, urls = set(), []
        for x in sorted(window, key=lambda z: z['r']):
            nu = norm_url(x['url'])
            if not nu or nu in _seen:
                continue
            _seen.add(nu)
            urls.append(nu)
        serps[pid] = {'urls': urls, 'set': set(urls), 'spell': d.get('spell'),
                      'raw': window, 'prompt': d.get('prompt', m['prompt'])}
    print(f"loaded {len(serps)} serps, {len(missing)} missing", file=sys.stderr)

    # corpus document frequency - the guard that makes the 1-shared join safe
    df = collections.Counter()
    for s in serps.values():
        for u in s['set']:
            df[u] += 1

    assess = {pid: spell_assess(serps[pid]['prompt'], serps[pid]['spell'], serps[pid]['raw']) for pid in serps}
    drift = [p for p in serps if assess[p][0] == 'quarantine']
    watch = [p for p in serps if assess[p][0] == 'watch']
    ok = [p for p in serps if p not in set(drift) and len(serps[p]['set']) >= MIN_URLS]
    thin = [p for p in serps if p not in set(drift) and len(serps[p]['set']) < MIN_URLS]

    def prio(pid):
        try:
            imp = float(master[pid].get('impressions') or 0)
        except Exception:
            imp = 0
        return (-imp, len(master[pid]['prompt']))

    clusters, cand, reason = [], [], {}
    for pid in sorted(ok, key=prio):
        s = serps[pid]['set']
        best, share = None, 0
        for c in clusters:
            k = len(s & serps[c['centroid']]['set'])
            if k > share:
                best, share = c, k
        if best is not None and share >= T:
            best['members'].append(pid)
            reason[pid] = f'{share}-shared'
        elif best is not None and share == 1:
            u = sorted(s & serps[best['centroid']]['set'])[0]
            d = df[u]
            if is_brand_comparison(master[pid]['prompt']):
                v = 'NO-JOIN (brand comparison)'
            elif is_hub(u):
                v = f'NO-JOIN (hub host, df={d})'
            elif d > DF_MAX:
                v = f'NO-JOIN (df={d} > {DF_MAX}: promiscuous URL)'
            else:
                v = f'JOINED (df={d} <= {DF_MAX}: specific co-citation)'
            cand.append({'prompt_id': pid, 'candidate_centroid': best['centroid'],
                         'shared_urls': u, 'df': d, 'verdict': v})
            if v.startswith('JOINED'):
                best['members'].append(pid)
                reason[pid] = f'1-shared-specific(df={d})'
            else:
                clusters.append({'centroid': pid, 'members': [pid]})
                reason[pid] = 'centroid'
        else:
            clusters.append({'centroid': pid, 'members': [pid]})
            reason[pid] = 'centroid'

    with open('clusters.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cluster_id', 'prompt_id', 'prompt', 'tier', 'intent', 'impressions', 'is_centroid',
                    'shared_with_centroid', 'join_reason', 'brand_urls_in_serp'])
        for i, c in enumerate(clusters, 1):
            cs = serps[c['centroid']]['set']
            for pid in c['members']:
                # the centroid's own overlap is its DISTINCT URL COUNT, not the TOPN sentinel -
                # writing 10 for a centroid whose SERP held 6 urls reads as a real overlap count
                sh = len(serps[pid]['set'] & cs) if pid != c['centroid'] else len(cs)
                bu = ' | '.join(u for u in serps[pid]['urls'] if is_brand_url(u))
                # intent is carried THROUGH, not recomputed: page_map and cluster_summary declare
                # an intent column, and if clusters.csv drops it those ship silently empty - which
                # a reviewer reads as "intent was not collected", not "intent was lost in transit".
                w.writerow([f'c{i:03d}', pid, master[pid]['prompt'], master[pid]['tier'],
                            master[pid].get('intent', ''),
                            master[pid]['impressions'], int(pid == c['centroid']), sh,
                            reason.get(pid, ''), bu])

    with open('merge_candidates.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['prompt_id', 'prompt', 'candidate_centroid', 'centroid_prompt', 'shared_urls', 'df', 'verdict'])
        for x in cand:
            w.writerow([x['prompt_id'], master[x['prompt_id']]['prompt'], x['candidate_centroid'],
                        master[x['candidate_centroid']]['prompt'], x['shared_urls'], x['df'], x['verdict']])

    # ESCALATION = final singletons (could not be mapped by SERP overlap)
    singles = [c['centroid'] for c in clusters if len(c['members']) == 1]
    with open('escalated.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['prompt_id', 'prompt', 'tier', 'impressions', 'brand_url_in_own_serp', 'reason'])
        for pid in singles:
            bu = next((u for u in serps[pid]['urls'] if is_brand_url(u)), '')
            w.writerow([pid, master[pid]['prompt'], master[pid]['tier'], master[pid]['impressions'], bu,
                        'singleton: no qualifying SERP overlap with any centroid'])

    with open('drift_quarantine.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['prompt_id', 'prompt', 'spell_suggestion'])
        for pid in drift:
            w.writerow([pid, master[pid]['prompt'], assess[pid][1]])

    # thin SERPs are quarantined for a DIFFERENT reason than spell drift - page_assign reads
    # this so the review queue says which one, instead of blaming spell drift for everything.
    with open('thin_serps.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['prompt_id', 'prompt', 'distinct_urls', 'min_required'])
        for pid in thin:
            w.writerow([pid, master[pid]['prompt'], len(serps[pid]['set']), MIN_URLS])

    with open('spell_watchlist.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['prompt_id', 'prompt', 'note'])
        for pid in watch:
            w.writerow([pid, master[pid]['prompt'], assess[pid][1]])
        for pid in serps:
            if assess[pid][0] == 'ok' and serps[pid]['spell']:
                w.writerow([pid, master[pid]['prompt'], 'OK: ' + assess[pid][1]])

    # Record the config that ACTUALLY produced this run. CLUSTER_T / ONE_SHARED_MAX_DF are env
    # overrides, so without this a page_map built at swept thresholds is indistinguishable from
    # one built at the signed-off values.
    json.dump({'T': T, 'topn': TOPN, 'one_shared_max_df': DF_MAX, 'min_serp_urls': MIN_URLS,
               'brand': BRAND, 'hub_hosts': list(HUBS),
               'never_one_shared_join': CFG['cluster']['never_one_shared_join'],
               'meaning_tokens': sorted(MEANING), 'signals': CFG.get('signals', {}),
               'env_overrides': {k: v for k, v in os.environ.items()
                                 if k in ('CLUSTER_T', 'ONE_SHARED_MAX_DF', 'AEO_CONFIG')}},
              open('run_config.json', 'w'), indent=2)

    sizes = sorted((len(c['members']) for c in clusters), reverse=True)
    j1 = sum(1 for v in reason.values() if v.startswith('1-shared-specific'))
    vc = collections.Counter(x['verdict'].split(' (')[0] for x in cand)
    with_brand = sum(1 for pid in singles if any(is_brand_url(u) for u in serps[pid]['urls']))
    print(f"clusters={len(clusters)} multi={sum(1 for s in sizes if s > 1)} singletons={sum(1 for s in sizes if s == 1)}")
    print(f"largest={sizes[:10]}")
    print(f"1-shared reviewed={len(cand)} -> {dict(vc)}   (JOINED={j1})  <-- ALL must go to the QA gate")
    print(f"escalated(final singletons)={len(singles)} drift={len(drift)} watch={len(watch)} thin={len(thin)} missing={len(missing)}")
    print(f"  of escalated, {with_brand} have a brand URL in their own SERP (Signal A places them anyway)")


if __name__ == '__main__':
    main()
