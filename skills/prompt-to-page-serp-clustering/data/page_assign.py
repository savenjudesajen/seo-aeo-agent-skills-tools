#!/usr/bin/env python3
"""Page assignment - CONFIG-DRIVEN, RANK-WEIGHTED, EVIDENCE-EXPOSING. Portable across projects.

Signals, first match wins (per cluster):

  A: brand-URL consensus across member SERPs.
       Only hits at rank <= signals.a_max_rank_considered (10) count toward A.
       hits >= a_min_hits AND best_rank <= a_high_confidence_max_rank -> HIGH
       hits >= a_min_hits AND best_rank >  a_high_confidence_max_rank -> MEDIUM (rank-demoted)
       hits == 1 in a <=2-prompt cluster                              -> MEDIUM/LOW by rank
     Counting a rank-10 hit exactly like a rank-1 hit labels many rows 'high' on weak
     visibility and lets whole clusters rest on low-ranked evidence.

  NEAR-MISS: a brand URL at rank 11-20 (near_miss_rank_range) does NOT fire Signal A.
     It sets near_miss=true on that row. These are the strongest refresh candidates on the
     site, and they are invisible when only the top 10 is stored.

  B: authored-intent prior (the page inventory's mapped_pages majority).
     NOT independent evidence. For prompts authored FROM a page's keywords this merely
     re-asserts the author's intent. Always confidence=low; EVERY B row is hand-read.
     (See reference/signal-provenance.md.)

  A-weak: single brand hit in a larger cluster -> LOW

  C: NET-NEW - only via the escalation adjudication (demand + seed-ownership + inventory
     reasoning). NEVER from absence of evidence alone.

Overrides (exact prompt text) beat all signals. The engine is never hand-edited.

ROW-LEVEL EVIDENCE (why these columns exist): confidence is inherited from the CLUSTER, not
the row. A prompt can sit on a 'high confidence' page while its OWN SERP contains no brand URL,
and a large share of hand-read corrections are exactly that. page_map.csv therefore carries, per row:
  shared_with_centroid, join_reason, brand_url_in_own_serp, brand_rank_in_own_serp, near_miss

Outputs: page_map.csv, page_summary.csv, cluster_summary.csv, run_caveat.txt
"""
import csv, json, glob, collections, re, os
from urllib.parse import urlsplit

# ONE config merge for the whole pipeline, owned by cluster_engine. A second copy drifts (for
# example in scalar-alias handling, "brand": "brand.example" -> brand.domain), and the engine then
# accepts a config that this script dies on - a half-run, not a clean stop.
try:
    from cluster_engine import load_cfg, DEFAULTS
except Exception:                                   # engine not importable: stand alone, same rules
    DEFAULTS = {'signals': {'a_min_hits': 2, 'a_high_confidence_max_rank': 5,
                            'a_max_rank_considered': 10, 'near_miss_rank_range': [11, 20]},
                'brand': {'domain': '', 'tokens': []}, 'competitors': [], 'page_inventory': ''}
    SCALAR_ALIAS = {'brand': 'domain'}

    def load_cfg(path=None):
        """Config over signed-off defaults - a half-edited config degrades, it does not KeyError."""
        src = path or os.environ.get('AEO_CONFIG', 'config.json')
        raw = json.load(open(src))
        out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULTS.items()}
        for k, v in raw.items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k].update(v)
            elif isinstance(out.get(k), dict) and not isinstance(v, dict):
                sub = SCALAR_ALIAS.get(k)
                if sub and isinstance(v, (str, int, float)):
                    out[k] = dict(out[k]); out[k][sub] = v
                else:
                    raise SystemExit(f"{src}: '{k}' must be an object, got {type(v).__name__} {v!r}")
            else:
                out[k] = v
        return out


CAVEAT = ('Clusters are formed from Google organic SERP overlap as a PROXY for what answer '
          'engines cite. Citations, where available, are a SEPARATE signal and are never '
          'pooled into the join decision.')

CFG = load_cfg()
BRAND = CFG['brand']['domain']
A_MIN = CFG['signals'].get('a_min_hits', 2)
A_RANK = CFG['signals'].get('a_high_confidence_max_rank', 5)
A_MAX = CFG['signals'].get('a_max_rank_considered', 10)
NM_LO, NM_HI = CFG['signals'].get('near_miss_rank_range', [11, 20])


def is_brand_url(u):
    """Host-anchored brand test on a RAW url.

    A substring test (BRAND in url) passes 'notbrand.example/x' and
    'brand.example.evil.example/x', which silently inflates Signal A.
    """
    host = re.sub(r'^https?://', '', (u or '').strip().lower()).split('/')[0].split('?')[0]
    host = re.sub(r'^www\.', '', host)
    bd = re.sub(r'^www\.', '', BRAND.lower()).rstrip('/')
    return bool(bd) and (host == bd or host.endswith('.' + bd))


def rows_of(d):
    """Normalize a checkpoint's `results` to [{'r':rank,'url':...,'title':...}].

    ⛔ A lean SERP provider returns a BARE LIST OF URL STRINGS in rank order. Every read loop
    must go through here - indexing a raw payload item with x['url'] raises TypeError mid-run
    and takes the whole assignment step down.
    """
    out = []
    for i, x in enumerate(d.get('results') or []):
        if isinstance(x, str):
            out.append({'r': i + 1, 'url': x, 'title': ''})
            continue
        if not isinstance(x, dict) or not x.get('url'):
            continue
        out.append({'r': rank_of(x, i), 'url': x['url'], 'title': x.get('title', '')})
    # 'r' is ORGANIC POSITION, not the provider's rank_absolute - see the same note in
    # cluster_engine.rows_of. It matters twice here: the A_MAX gate drops brand URLs whose
    # rank_absolute exceeds the cap even when they are genuinely top-10 organic, and every
    # rationale string says "best rank #N", which a reader takes as the organic position.
    out.sort(key=lambda z: z['r'])
    for _n, _x in enumerate(out, 1):
        _x['r_absolute'] = _x['r']
        _x['r'] = _n
    return out


def rank_of(x, i):
    """Rank from the payload, else the 1-based list position.

    ⚠️ A lean SERP provider returns a bare URL list IN RANK ORDER with no rank field. Reading a
    missing rank as 99 pushes every hit past a_max_rank_considered, which silently disables
    Signal A for that entire provider - the run completes and every cluster looks net-new.
    """
    try:
        r = int(x.get('r'))
        return r if r > 0 else i + 1
    except (TypeError, ValueError):
        return i + 1


def npath(u):
    """Brand URL -> page key. A SUBDOMAIN keeps its host, because it is a different page.

    Parsed with urlsplit, never by slicing the raw string. String slicing fails two ways:
    matching the bare domain anywhere in the URL collapses www.brand.example/guide and
    docs.brand.example/guide onto '/guide'; and searching a LOWERCASED host inside the ORIGINAL
    mixed-case url returns -1, so the slice cuts at an arbitrary offset and fabricates a
    plausible-looking page key that can ship at confidence=high.
    """
    s = urlsplit(str(u or '').strip())
    host = re.sub(r'^www\.', '', (s.netloc or '').lower())
    if not host:
        return str(u or '')
    path = (s.path or '').rstrip('/') or '/'
    bd = re.sub(r'^www\.', '', BRAND.lower()).rstrip('/')
    if host == bd:
        return path
    return f"{host}{path}" if host.endswith('.' + bd) else str(u or '')


clusters = collections.defaultdict(list)
for r in csv.DictReader(open('clusters.csv')):
    clusters[r['cluster_id']].append(r)
# Glob EVERY checkpoint, not serps/p*.json. The prompt_id prefix is the caller's choice - a
# keyword corpus may use p0001, a prompt corpus q<hash>, a client's own ids anything at all.
# A prefix-filtered glob returns nothing for those, Signal A never fires, and every row falls
# through to C:net-new while the clustering step upstream looks perfectly healthy.
serp = {json.load(open(f))['prompt_id']: json.load(open(f)) for f in glob.glob('serps/*.json')}
_inv = CFG.get('page_inventory') or ''
audit = json.load(open(_inv)) if _inv and os.path.exists(_inv) else {}
if not audit:
    print(f"NOTE: no page inventory at '{_inv or '(unset)'}' - Signal B (authored-intent) is "
          f"unavailable this run; clusters with no brand URL fall to A-weak or NET-NEW.")
# overrides.csv is HAND-WRITTEN by the reviewer, so validate its header here. Without this a
# missing column takes the whole assignment step down much later with a bare
# KeyError: 'confidence' that names neither the file nor the row - and because the crash leaves
# the PREVIOUS page_map.csv in place, the QA and gate steps then run clean on stale artifacts.
_ovr_rows = list(csv.DictReader(open('overrides.csv')))
_need = {'prompt_text', 'target_page', 'confidence', 'rationale'}
if _ovr_rows:
    _missing = _need - set(_ovr_rows[0])
    if _missing:
        raise SystemExit(f"overrides.csv is missing required column(s): {sorted(_missing)}. "
                         f"Header must be exactly: prompt_text,target_page,confidence,rationale")
    for _i, _r in enumerate(_ovr_rows, 2):
        _blank = [c for c in ('prompt_text', 'target_page') if not (_r.get(c) or '').strip()]
        if _blank:
            raise SystemExit(f"overrides.csv line {_i}: empty {_blank}. An override with no "
                             f"prompt_text silently matches nothing and the row it was meant to "
                             f"fix ships unchanged.")
ovr = {r['prompt_text'].strip(): r for r in _ovr_rows}
master = {r['prompt_id']: r for r in csv.DictReader(open('prompts_master.csv'))}


def _reasons(path, col, fmt):
    if not os.path.exists(path):
        return {}
    return {r['prompt_id']: fmt(r) for r in csv.DictReader(open(path))}


# why a prompt is unclustered: spell drift and a thin SERP are different problems
Q_REASON = {}
Q_REASON.update(_reasons('drift_quarantine.csv', 'spell_suggestion',
                         lambda r: f"spell drift: {r.get('spell_suggestion', '')}"))
Q_REASON.update(_reasons('thin_serps.csv', 'distinct_urls',
                         lambda r: f"thin SERP ({r.get('distinct_urls')} distinct urls < "
                                   f"{r.get('min_required')} required) - too little signal to join"))

KNOWN = set()
for v in audit.values():
    for p in str(v.get('mapped_pages') or '').split('|'):
        p = p.strip()
        if p.startswith('/'):
            KNOWN.add(p)


def own_brand_evidence(pid):
    """Best brand URL in THIS prompt's own SERP, at any stored depth. Returns (path, rank)."""
    best = (None, 99)
    for x in rows_of(serp.get(pid, {})):
        if is_brand_url(x['url']):
            r = x['r']
            if r < best[1]:
                best = (x['url'], r)   # keep the FULL url: docs.brand.example/x and www.brand.example/x
                                       # must not render identically in the evidence column
    return best


rows_out, page_rows = [], collections.defaultdict(list)
for cid, members in clusters.items():
    pids = [m['prompt_id'] for m in members]
    hits = collections.Counter()
    best_rank = {}
    for pid in pids:
        # ⛔ Signal A counts DISTINCT MEMBER SERPs, not occurrences. Google can list the same
        # brand URL at two ranks in ONE SERP; counting occurrences let a single SERP satisfy
        # a_min_hits by itself and ship a false 'high confidence, 2 member SERPs' rationale.
        seen_here = set()
        for x in rows_of(serp.get(pid, {})):
            if is_brand_url(x['url']):
                r = x['r']
                if r > A_MAX:
                    continue                 # rank 11-20 is near-miss, not consensus evidence
                p = npath(x['url'])
                best_rank[p] = min(best_rank.get(p, 99), r)
                if p in seen_here:
                    continue
                seen_here.add(p)
                hits[p] += 1
    bcnt = collections.Counter()
    for pid in pids:
        mp = [p.strip() for p in audit.get(pid, {}).get('mapped_pages', '').split('|') if p.strip().startswith('/')]
        for i, p in enumerate(mp):
            bcnt[p] += (2 if i == 0 else 1)

    a_page, a_hits = (hits.most_common(1)[0] if hits else (None, 0))
    a_rank = best_rank.get(a_page, 99) if a_page else 99
    b_page, b_score = (bcnt.most_common(1)[0] if bcnt else (None, 0))

    # cluster_review: does THIS CLUSTER's signal require a hand-read, regardless of any one row?
    # Only a high-confidence A consensus is exempt. Every other branch goes to the queue - that is
    # what the b_signal_rows_hand_read and one_shared_joins_hand_read gates are asserting.
    if a_hits >= A_MIN:
        conf = 'high' if a_rank <= A_RANK else 'medium'
        page, sig = a_page, 'A:brand-ranks'
        cluster_review = conf != 'high'            # rank-demoted consensus still needs a read
        why = f"{BRAND}{a_page} appears in {a_hits} member SERP(s), best rank #{a_rank}" + \
              ('' if conf == 'high' else f" - rank-demoted: best rank #{a_rank} > {A_RANK}, weak visibility")
    elif a_hits == 1 and len(pids) <= 2:
        conf = 'medium' if a_rank <= A_RANK else 'low'
        page, sig, cluster_review = a_page, 'A:brand-ranks', True
        why = f"{BRAND}{a_page} appears in 1 of {len(pids)} member SERP(s), rank #{a_rank}"
    elif b_page:
        page, sig, conf, cluster_review = b_page, 'B:authored-intent', 'low', True
        why = (f"authored-intent prior (mapped-pages score {b_score}); no {BRAND} URL ranks in cluster SERPs. "
               f"This is the page the prompt was authored FROM, not independent evidence - hand-read required.")
    elif a_hits == 1:
        page, sig, conf, cluster_review = a_page, 'A:brand-weak', 'low', True
        why = f"single {BRAND} hit (rank #{a_rank}) in a {len(pids)}-prompt cluster"
        if len(hits) > 1:
            # the page is whichever key most_common() returned first; say so rather than
            # reporting 'a single hit' when the cluster is actually split across brand pages
            why += (f"; NOTE this cluster holds {len(hits)} DIFFERENT brand pages seen once each "
                    f"({', '.join(sorted(hits))}) - it may need splitting across pages")
    else:
        cen = next((m for m in members if m['is_centroid'] == '1'), members[0])
        # ⛔ An empty or all-punctuation centroid yields the slug '', and 'NET-NEW:' (or any fixed
        # fallback) is non-empty and identical for every such cluster - silently fusing unrelated
        # net-new clusters onto one page with one primary. So the cluster id is appended, but
        # ONLY when the slug is empty: appending it always would rename every net-new key whenever
        # clusters renumber. Two DIFFERENT clusters colliding on one slug are caught by the
        # integrity gate.
        slug = re.sub(r'[^a-z0-9]+', '-', str(cen.get('prompt') or '').lower())[:60].strip('-')
        page = f"NET-NEW:{slug}" if slug else f"NET-NEW:unnamed-{cid}"
        sig, conf, cluster_review = 'C:net-new', 'medium', True
        why = f"no {BRAND} URL in any member SERP + no authored-intent prior -> new page CANDIDATE (verify demand)"

    for m in members:
        own_path, own_rank = own_brand_evidence(m['prompt_id'])
        near_miss = bool(own_path) and NM_LO <= own_rank <= NM_HI
        base = {**m,
                'brand_url_in_own_serp': own_path or '',
                'brand_rank_in_own_serp': own_rank if own_path else '',
                'near_miss': 'yes' if near_miss else ''}
        o = ovr.get(m['prompt'].strip())
        if o:
            rows_out.append({**base, 'page': o['target_page'], 'signal': 'OVERRIDE',
                             'confidence': o['confidence'], 'rationale': o['rationale'],
                             'cluster_id': cid, 'needs_review': ''})
        else:
            # An A-signal row whose OWN serp holds no brand URL inherited its confidence from the
            # cluster and has none of its own. It is the commonest hand-read correction, so it is
            # flagged automatically rather than left for the hand-read to notice.
            rows_out.append({**base, 'page': page, 'signal': sig, 'confidence': conf,
                             'rationale': why, 'cluster_id': cid,
                             # UNION of the cluster's review flag and this row's own-evidence
                             # test. Dropping the cluster term ships every B / C / weak-A row
                             # unflagged, which is exactly what the hand-read gates forbid.
                             'needs_review': 'yes' if (cluster_review or
                                                       (sig.startswith('A') and not own_path)) else ''})

# quarantined / unclustered prompts: resolved via overrides, else flagged REVIEW
clustered = {r['prompt_id'] for r in rows_out}
_no_checkpoint = [p for p in master if p not in clustered and p not in serp]
if _no_checkpoint:
    print(f"WARNING: {len(_no_checkpoint)} prompt(s) have no SERP checkpoint and are NOT in the "
          f"map: {_no_checkpoint[:5]}. The integrity gate will fail on coverage.")
for pid, m in master.items():
    if pid in clustered or pid not in serp:
        continue
    o = ovr.get(m['prompt'].strip())
    own_path, own_rank = own_brand_evidence(pid)
    rows_out.append({'prompt_id': pid, 'prompt': m['prompt'], 'tier': m['tier'], 'impressions': m['impressions'],
                     'is_centroid': '0', 'cluster_id': 'quarantine', 'shared_with_centroid': '',
                     'join_reason': '', 'brand_urls_in_serp': '',
                     'brand_url_in_own_serp': own_path or '', 'brand_rank_in_own_serp': own_rank if own_path else '',
                     'near_miss': 'yes' if own_path and NM_LO <= own_rank <= NM_HI else '',
                     'page': o['target_page'] if o else 'REVIEW',
                     'signal': 'OVERRIDE' if o else 'QUARANTINE-UNRESOLVED',
                     'confidence': o['confidence'] if o else 'low',
                     'needs_review': '' if o else 'yes',
                     'rationale': o['rationale'] if o else
                         (Q_REASON.get(pid, 'held out of clustering') + '; no override resolves it')})

# Backfill intent from prompts_master for EVERY row, whatever path built it (normal, OVERRIDE,
# quarantine). page_map declares an 'intent' column and cluster_summary computes intent_mix from
# it; without this they ship empty and a reviewer reads "no intent data" as "intent not collected".
for r in rows_out:
    if not r.get('intent'):
        r['intent'] = (master.get(r['prompt_id'], {}) or {}).get('intent', '') or ''

for r in rows_out:
    page_rows[r['page']].append(r)


def imp(r):
    try:
        return float(r['impressions'] or 0)
    except Exception:
        return 0


with open('page_map.csv', 'w', newline='') as f:
    cols = ['page', 'page_status', 'cluster_id', 'role', 'prompt_id', 'prompt', 'tier',
            'impressions', 'intent', 'signal', 'confidence', 'needs_review',
            'shared_with_centroid', 'join_reason', 'brand_url_in_own_serp', 'brand_rank_in_own_serp',
            'near_miss', 'rationale']
    w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
    w.writeheader()
    for page, rs in sorted(page_rows.items(), key=lambda x: -len(x[1])):
        status = 'REVIEW' if page == 'REVIEW' else (
            'net-new' if page.startswith('NET-NEW') else (
                'existing' if page in KNOWN or any(r['signal'].startswith('A') for r in rs) else 'existing(audit)'))
        prim = max((r for r in rs if r['is_centroid'] == '1'), key=imp, default=max(rs, key=imp))
        for r in sorted(rs, key=lambda r: (-int(r['is_centroid']), -imp(r))):
            w.writerow({**r, 'page': page, 'page_status': status,
                        'role': 'primary' if r is prim else 'secondary'})

with open('page_summary.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['page', 'status', 'prompts', 'clusters', 'total_impressions', 'near_miss_rows',
                'needs_review_rows', 'tier_mix', 'signals'])
    for page, rs in sorted(page_rows.items(), key=lambda x: -len(x[1])):
        status = 'REVIEW' if page == 'REVIEW' else ('net-new' if page.startswith('NET-NEW') else 'existing')
        tiers = collections.Counter(r.get('tier', '') for r in rs if r.get('tier'))
        mix = ', '.join(f'{t} {round(100.0 * n / max(len(rs), 1))}%'
                        for t, n in tiers.most_common(4))
        w.writerow([page, status, len(rs), len(set(r['cluster_id'] for r in rs)),
                    int(sum(imp(r) for r in rs)),
                    sum(1 for r in rs if r.get('near_miss') == 'yes'),
                    sum(1 for r in rs if r.get('needs_review') == 'yes'),
                    mix,
                    '+'.join(sorted(set(r['signal'] for r in rs)))])

# CLUSTER-level roll-up. The judgment pass is told to "read every multi-cluster", which needs a
# row per cluster with a readable name and a size - page_summary is page-level, not cluster-level.
by_cluster = collections.defaultdict(list)
for r in rows_out:
    by_cluster[r.get('cluster_id', '')].append(r)
with open('cluster_summary.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['cluster_id', 'cluster_name', 'size', 'page', 'signal', 'confidence',
                'needs_review_rows', 'intent_mix', 'tier_mix', 'rationale'])
    for cidx, rs in sorted(by_cluster.items(), key=lambda x: -len(x[1])):
        cen = next((r for r in rs if r.get('is_centroid') == '1'), rs[0])
        nm_ = str(cen.get('prompt') or '')
        name = nm_ if len(nm_) <= 70 else nm_[:67] + '...'
        def _mix(key):
            c = collections.Counter(r.get(key, '') for r in rs if r.get(key))
            return ', '.join(f'{k} {round(100.0 * v / max(len(rs), 1))}%' for k, v in c.most_common(4))
        w.writerow([cidx, name, len(rs), cen.get('page', ''), cen.get('signal', ''),
                    cen.get('confidence', ''),
                    sum(1 for r in rs if r.get('needs_review') == 'yes'),
                    _mix('intent'), _mix('tier'), cen.get('rationale', '')])

# The caveat travels WITH the run. As prose in a doc it can be forgotten out of a deliverable.
with open('run_caveat.txt', 'w') as f:
    f.write(CAVEAT + '\n')

nm = sum(1 for r in rows_out if r.get('near_miss') == 'yes')
nr = sum(1 for r in rows_out if r.get('needs_review') == 'yes')
print(f"pages: {len(page_rows)} | prompts mapped: {len(rows_out)} | "
      f"near-miss refresh candidates (rank {NM_LO}-{NM_HI}): {nm} | needs_review: {nr}")
