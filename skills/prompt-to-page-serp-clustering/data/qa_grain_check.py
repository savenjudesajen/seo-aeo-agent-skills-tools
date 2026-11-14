#!/usr/bin/env python3
"""Deterministic grain guard (run after page_assign, before deliverable).

CONFIG-DRIVEN: the competitor list and page inventory come from config.json.

Rule: a prompt naming <competitor> together with alternatives/competitor/tools-like intent
must land on that competitor's alternatives/compare page when one exists.

KNOWN FALSE POSITIVE: attributive uses such as "competitor price match" describe a feature or
a comparison, not alternatives intent - the pattern requires plural/top-anchored forms.

KNOWN BLIND SPOT: this regex CANNOT see the "X vs Y" shape (it catches only a small share of
them). Competitor-vs-competitor head-to-heads are enforced by reviewer rule, not by script.
The blind spot is printed on the PASS path too, so nobody reads a pass as correctness.

Flags are ADVISORY: they are written back onto page_map.csv as grain_flag + needs_review=yes
so the deliverable carries the record, and the gate exits non-zero so a human adjudicates.
A flag never auto-reassigns a row.

Extend this script whenever a hand-read finds a systematic class.
"""
import csv, json, re, sys, os, collections

CFG = json.load(open(os.environ.get('AEO_CONFIG', 'config.json')))
def squash(s):
    """Lowercase and strip every non-alphanumeric, on BOTH sides of a comparison.

    Squashing the two sides differently (say '.' and ' ' from the competitor but '-' and '.'
    from the page) means a hyphenated competitor name (the config.json template uses one) can
    never match its own page: the row is flagged even when correctly assigned, and the
    candidate list always comes back empty.
    """
    return re.sub(r'[^a-z0-9]', '', str(s or '').lower())


# ⛔ Usability is decided by the SQUASHED base, not the raw string. A config of ['.', '  ']
# leaves a non-empty COMP, skips the guard, then skips every comparison - and reports PASS.
COMP = [str(c).lower() for c in (CFG.get('competitors') or []) if squash(c)]
BRAND_TOKENS = [str(t).lower() for t in ((CFG.get('brand') or {}).get('tokens') or []) if str(t).strip()]

BLIND_SPOT = ("BLIND SPOT: this check cannot see the 'X vs Y' shape (it catches only a small "
              "share of them); that class is a reviewer rule, not a script check. A pass means "
              "'no DETECTABLE grain violation', not 'the grain is right'.")

# ⛔ A gate that never ran must never report as a gate that passed.
if not COMP:
    print("GRAIN CHECK: SKIPPED (no competitors configured in config.json) - the gate did NOT run")
    print(BLIND_SPOT)
    sys.exit(2)


KNOWN = set()
_inv = CFG.get('page_inventory') or ''
if _inv and os.path.exists(_inv):
    for v in json.load(open(_inv)).values():
        for p in str(v.get('mapped_pages') or '').split('|'):
            p = p.strip()
            if p.startswith('/'):
                KNOWN.add(p)

ALT = re.compile(r'\balternatives?\b|\bcompetitors\b|tools like|similar to|top [a-z .]*competitor\b')

rows = list(csv.DictReader(open('page_map.csv')))
flags, flagged_ids = [], {}
for r in rows:
    pl, page = r['prompt'].lower(), r['page']
    if page == 'REVIEW':
        continue
    if any(t in pl for t in BRAND_TOKENS):
        continue          # brand-anchored prompts are handled by the brand-anchor rule
    for c in COMP:
        base = squash(c)
        if not base:
            continue      # a junk config entry ('.', ' ') would otherwise match everything
        if base in squash(pl) and ALT.search(pl):
            if base not in squash(page):
                cand = sorted(k for k in KNOWN
                              if base in squash(k) and 'alternativ' in k.lower())
                flags.append((r['prompt_id'], r['prompt'][:60], page, c, cand))
                flagged_ids[r['prompt_id']] = c
            break

# Write the flags back onto the artifact - terminal output is not a deliverable.
if flagged_ids:
    cols = list(rows[0].keys())
    for extra in ('grain_flag', 'needs_review'):
        if extra not in cols:
            cols.append(extra)
    for r in rows:
        if r['prompt_id'] in flagged_ids:
            r['grain_flag'] = f"competitor-alternatives grain ({flagged_ids[r['prompt_id']]})"
            r['needs_review'] = 'yes'
        else:
            r.setdefault('grain_flag', '')
            r.setdefault('needs_review', r.get('needs_review', ''))
    with open('page_map.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)

    # page_summary was written by page_assign BEFORE these flags existed. Re-sync its
    # needs_review_rows column so the two shipped artifacts cannot contradict each other.
    if os.path.exists('page_summary.csv'):
        nr = collections.Counter(r['page'] for r in rows if r.get('needs_review') == 'yes')
        srows = list(csv.DictReader(open('page_summary.csv')))
        if srows and 'needs_review_rows' in srows[0]:
            for s in srows:
                s['needs_review_rows'] = nr.get(s['page'], 0)
            with open('page_summary.csv', 'w', newline='') as f:
                w = csv.DictWriter(f, fieldnames=list(srows[0].keys()), extrasaction='ignore')
                w.writeheader()
                w.writerows(srows)

if flags:
    print(f"GRAIN CHECK: {len(flags)} flags (written back to page_map.csv as grain_flag)")
    for pid, prompt, page, comp, cand in flags:
        print(f"  {pid} '{prompt}' -> {page} | competitor={comp} | candidates: {cand}")
    print(BLIND_SPOT)
    sys.exit(1)

print("GRAIN CHECK: PASS (0 flags)")
print(BLIND_SPOT)
