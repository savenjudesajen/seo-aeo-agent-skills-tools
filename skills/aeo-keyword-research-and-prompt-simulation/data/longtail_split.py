#!/usr/bin/env python3
"""Split a 6+ word Search Console query export by WHO WROTE THE QUERY, before any of it is cited as evidence of what
buyers ask. Python standard library only; runs offline. It LABELS; it does not decide relevance.

Why: at the top of a long-tail export much of the impression volume is often not people. Review-site tool strings hit
the site by collision; other trackers' prompts are executed through AI search modes ("acting as a <role>, list the
leading <category> providers and order them from best to worst"); and inside the question-shaped remainder a few exact
long phrasings can carry impressions every day for months. A person does not type the same long question several times
a day; a tracker does. A client's own tracked prompts, run daily, come back out of Search Console as "demand".

Labels, and what each population is FOR:
  HUMAN     question opener, flat impression distribution. A person asking: the SHAPES a tracked prompt should take,
            and the only population whose volume is demand.
  REPEAT    human-shaped, but one exact phrasing of --min-repeat-words or more repeated >= --per-day times a day over the
            window. An instrument. Read flagged rows as SETS (same brand or same template = one instrument).
  OWN-TRACK exact match to the client's own tracked-prompt export (--tracked): their instrument reflected back. Run it
            whenever an export exists; REPEAT is the fallback.
  TRACKER   persona framing, a ranking instruction ("forced ranking", "order them from best to worst"), an instruction
            addressed to the model ("you must ...", "you are a ...", "search the web for", "do not invent"), a leading
            <tag> wrapper, or a string over --max-human-words words. Another tool's prompt set. A trailing clause stating
            the asker's location or market is stripped before matching.
  TEMPLATE  a noun-phrase prompt iterated over a slot. With no extra flags it matches a query that STARTS with:
              "evaluate the "                                        (anything may follow)
              "best " + a provider noun as the very next word       (required; "best kayak companies" is not TEMPLATE)
              "top " + a provider noun as the very next word        (required)
              "tool to ", "tools to ", "tool for ", "tools for "    (anything may follow)
              "leading ", "highest-rated " (or "highest rated "), "most reliable ", "most affordable "
                                                                     (anything may follow; no noun needed)
            Provider nouns: tool(s), platform(s), software, solution(s), service(s), agency/agencies,
            company/companies, provider(s), app(s), vendor(s), as whole words; --template-noun adds the category's own
            head nouns to that list (for "best" and "top" only). --template-pattern adds whole regex alternatives (no
            default). Checked after TRACKER, PERSONA_SHORT and STACK. The category's measurement surface, not buyer
            demand and not the engine's own fan-out.
  NOISE     third-party product strings hitting the site by collision. Per client: pass with --noise.
  PREFIX    a string whose first character is + or % (often ending in a year): a tool's operator prefix. Instrument.
  AGENT     search operators and crawl or watch instructions ("site:", "inurl:", "list every page on <domain>", "watch
            <domain> for changes"). Not demand.
  PERSONA_SHORT  a short persona plus a request ("as a <role>, suggest a <category> service for my team"), typically one
            phrasing per product noun at similar impressions each. A tracker.
  STACK     three or more vendor names in one string, usually "... comparison <year>": a tracker's or review tool's
            comparison string. Runs only when you pass the category's vendor names with --vendors (no default list).
  REPEAT-SET  8+ word human-shaped phrasings that are one template with a slot swapped (same first 5 and last 2 words,
            same length, --set-min or more variants, together at or above the REPEAT rate). Slips under the REPEAT length
            floor one phrasing at a time. An instrument.
  other     non-English questions, bare noun phrases people do type, templates not seen before. Read the samples and the
            template table before trusting any share.

The engine's own FAN-OUT is NOT a Search Console population: observe it in Bing Webmaster Tools' AI performance report
and in the assistant UI, or simulate it by compressing the tracked prompt. Never label a Search Console row "fan-out".

HUMAN detection is English-only by default: non-English questions land in "other". If the client sells into other
languages, pass their question openers with --opener.

Usage:
  python3 longtail_split.py --csv gsc_export.csv [--query-col query] [--imp-col impressions] [--clicks-col clicks]
        [--days 90] [--per-day 3] [--min-repeat-words 10] [--noise '<substring>' ...] [--tracked tracked.csv]
        [--template-noun '<noun>' ...] [--template-pattern '<regex>' ...] [--opener '<word>' ...]
        [--vendors 'name1,name2,...'] [--set-min 3] [--max-human-words 40] [--json out.json]

The same split runs inside BigQuery on the full Search Console bulk export (no row cap): longtail_split_bigquery.sql.
"""
import argparse
import csv
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tracker_tells import LOCATION_CLAUSE, LONG_PERSONA_TELLS, TRACKER_TELLS  # noqa: E402

# Tracker tells from tracker_tells.py (shared with verify_tracked_set.py; the SQL carries the same text). A location or
# market clause is stripped before matching here (LOC), not treated as a tell.
TRACK = re.compile('(%s|%s)' % (TRACKER_TELLS, LONG_PERSONA_TELLS), re.I)
# other languages' output instructions: pass them as --noise substrings or read them in "other"
PREFIX = re.compile(r'^[+%]')
AGENT = re.compile(r'(\b(?:site|inurl|intitle):|^(?:list|crawl|scan) every |^watch \S+ for )', re.I)
PSHORT = re.compile(r"^(i'm|i am|as) an? [a-z ,\-]{3,60}[.,] ", re.I)
BASE_TEMPLATE_NOUNS = ['tools?', 'platforms?', 'software', 'solutions?', 'services?', 'agenc(?:y|ies)', 'compan(?:y|ies)',
                       'providers?', 'apps?', 'vendors?']
OPENERS = ['what', 'how', 'which', 'who', 'why', 'is', 'are', 'can', 'do', 'does', 'should', 'will', 'where', 'when']
LOC = re.compile(r'(\.?\s*' + LOCATION_CLAUSE + r' [a-z ]+\.?$)', re.I)


def build_template(extra_nouns, extra_patterns=()):
    nouns = '|'.join(BASE_TEMPLATE_NOUNS + [re.escape(n) for n in extra_nouns])
    extra = ''.join('|' + p for p in extra_patterns)
    return re.compile(r'^(evaluate the |best (%s)\b|top (%s)\b|tools? (to|for) |'
                      r'(leading|highest.rated|most reliable|most affordable) %s)' % (nouns, nouns, extra), re.I)


def norm(q):
    q = q.lower().replace(chr(0x2019), "'").replace(chr(0x2014), '-').replace(chr(0x2013), '-')
    q = LOC.sub('', q)
    q = re.sub(r'[^\w\s]', '', q)
    return re.sub(r'\s+', ' ', q).strip()


def classify(q, noise, tracked, templ, humanq, vendors=(), max_human=40):
    ql = q.lower()
    if any(n in ql for n in noise):
        return 'NOISE'
    if PREFIX.match(q):
        return 'PREFIX'
    if AGENT.search(q):
        return 'AGENT'
    if tracked and norm(q) in tracked:
        return 'OWN-TRACK'
    if TRACK.search(q) or len(q.split()) > max_human:
        return 'TRACKER'
    if PSHORT.match(q):
        return 'PERSONA_SHORT'
    if vendors and sum(1 for v in vendors if re.search(r'\b' + re.escape(v) + r'\b', ql)) >= 3:
        return 'STACK'
    if templ.search(q):
        return 'TEMPLATE'
    if humanq.match(q):
        return 'HUMAN'
    return 'other'


ORDER = ('HUMAN', 'REPEAT', 'REPEAT-SET', 'OWN-TRACK', 'TRACKER', 'PERSONA_SHORT', 'STACK', 'TEMPLATE', 'PREFIX', 'AGENT',
         'NOISE', 'other')


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--csv', required=True)
    a.add_argument('--query-col', default='query')
    a.add_argument('--imp-col', default='impressions')
    a.add_argument('--clicks-col', default='clicks')
    a.add_argument('--noise', action='append', default=[], help='per-client noise substring, repeatable')
    a.add_argument('--tracked', help="CSV of the client's tracked prompts (a 'prompt' column, or the first column)")
    a.add_argument('--template-noun', action='append', default=[], help='category head noun for the TEMPLATE pattern')
    a.add_argument('--template-pattern', action='append', default=[],
                   help='extra TEMPLATE regex alternative matched at the start of the query, repeatable; no default')
    a.add_argument('--max-human-words', type=int, default=40, help='longer strings are labelled TRACKER')
    a.add_argument('--opener', action='append', default=[], help='extra question opener (other languages)')
    a.add_argument('--vendors', default='', help='comma-separated vendor names in the category (STACK label); no default')
    a.add_argument('--vendor', action='append', default=[], help='one vendor name, repeatable (same as --vendors)')
    a.add_argument('--set-min', type=int, default=3, help='REPEAT-SET: minimum variants of one slot-swapped template')
    a.add_argument('--days', type=int, default=90, help='length of the export window in days')
    a.add_argument('--per-day', type=float, default=3.0, help='impressions per day that mark an exact phrasing as repeated')
    a.add_argument('--min-repeat-words', type=int, default=10, help='REPEAT applies only at or above this length')
    a.add_argument('--min-words', type=int, default=6)
    a.add_argument('--json')
    o = a.parse_args()
    noise = [n.lower() for n in o.noise]
    templ = build_template(o.template_noun, o.template_pattern)
    vendors = tuple(v.strip().lower() for v in o.vendors.split(',') + o.vendor if v.strip())
    humanq = re.compile(r'^(%s)\b' % '|'.join(re.escape(w) for w in OPENERS + o.opener), re.I)
    tracked = set()
    if o.tracked:
        with open(o.tracked, newline='', encoding='utf-8-sig') as f:
            rd = csv.reader(f)
            hdr = next(rd, None)
            col = 0
            if hdr:
                low = [h.strip().lower() for h in hdr]
                col = low.index('prompt') if 'prompt' in low else 0
                if low[col] not in ('prompt', 'query', 'text'):
                    tracked.add(norm(hdr[col]))
            for r in rd:
                if r and len(r) > col and r[col].strip():
                    tracked.add(norm(r[col]))
    tracked = frozenset(tracked)
    rows = []
    with open(o.csv, newline='', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            q = (r.get(o.query_col) or '').strip()
            if len(q.split()) < o.min_words:
                continue
            try:
                imp = float(r.get(o.imp_col) or 0)
                clk = float(r.get(o.clicks_col) or 0)
            except ValueError:
                continue
            rows.append({'q': q, 'imp': imp, 'clk': clk, 'pop': classify(q, noise, tracked, templ, humanq, vendors, o.max_human_words)})
    if not rows:
        sys.exit('no rows read; check the column names')
    thresh = o.per_day * o.days
    for r in rows:
        if r['pop'] == 'HUMAN' and r['imp'] >= thresh and len(r['q'].split()) >= o.min_repeat_words:
            r['pop'] = 'REPEAT'
    # REPEAT-SET: group 8+ word HUMAN rows by first 5 words, last 2 words and length; a group of --set-min or more whose
    # swapped words all differ, together at or above the REPEAT rate, is one instrument.
    sets = defaultdict(list)
    for r in rows:
        if r['pop'] == 'HUMAN' and len(r['q'].split()) >= 8:
            w = norm(r['q']).split()
            sets[(' '.join(w[:5]), ' '.join(w[-2:]), len(w))].append(r)
    for v in sets.values():
        if len(v) >= o.set_min and sum(r['imp'] for r in v) >= thresh:
            mids = [norm(r['q']).split()[5:-2] for r in v]
            common = set.intersection(*(set(m) for m in mids))
            stems = [' '.join(w for w in m if w not in common)[:4] for m in mids]
            if len(set(stems)) == len(stems):  # a swapped slot, not a spelling variant
                for r in v:
                    r['pop'] = 'REPEAT-SET'
    N = len(rows)
    T = sum(r['imp'] for r in rows) or 1
    by = defaultdict(list)
    for r in rows:
        by[r['pop']].append(r)
    print('LONG-TAIL POPULATION SPLIT   %d queries, %.0f impressions, %d clicks   (window %d days, REPEAT >= %.0f imp at %d+ words%s)'
          % (N, T, sum(r['clk'] for r in rows), o.days, thresh, o.min_repeat_words,
             ', tracked export matched' if tracked else ', NO tracked export: OWN-TRACK could not run'))
    if not vendors:
        print('  no --vendors given: STACK could not run')
    print('  %-13s %7s %6s %10s %6s %6s %6s' % ('pop', 'queries', 'share', 'imp', 'share', 'clicks', 'words'))
    for k in ORDER:
        v = by.get(k, [])
        if not v:
            continue
        print('  %-13s %7d %5.1f%% %10.0f %5.1f%% %6.0f %6.1f' % (k, len(v), 100 * len(v) / N, sum(r['imp'] for r in v),
              100 * sum(r['imp'] for r in v) / T, sum(r['clk'] for r in v), statistics.mean(len(r['q'].split()) for r in v)))
    H = by.get('HUMAN', [])
    if H:
        im = sorted(r['imp'] for r in H)
        print('  HUMAN impressions per phrasing: median %.0f, p90 %.0f, p99 %.0f. A flat tail is the signature of people.'
              % (statistics.median(im), im[min(len(im) - 1, int(.9 * len(im)))], im[min(len(im) - 1, int(.99 * len(im)))]))
    print('\nSAMPLES, top by impressions. READ THESE before trusting the split.')
    for k in ORDER:
        v = sorted(by.get(k, []), key=lambda r: -r['imp'])[:4]
        if not v:
            continue
        print('  [%s]' % k)
        for r in v:
            print('     %6.0f | %s' % (r['imp'], r['q'][:120]))
    R = by.get('REPEAT', [])
    if R:
        words = Counter()
        for r in R:
            for w in re.findall(r'\b[a-z][a-z0-9.\-]{2,}\b', r['q'].lower()):
                words[w] += 1
        print('\nREPEAT SETS: most frequent tokens across the repeated phrasings (a brand or a template noun at the top = one instrument)')
        print('  ' + ', '.join('%s (%d)' % (w, c) for w, c in words.most_common(12)))
    grp = defaultdict(list)
    for r in rows:
        grp[' '.join(r['q'].lower().split()[:3])].append(r)
    print('\nTEMPLATE CHECK: openings shared by 60+ queries. A high same-5-word share with zero clicks = a tool or the engine, not people.')
    print('  %-30s %6s %8s %5s %7s %6s  %s' % ('opening', 'n', 'imp', 'clk', 'same5w', 'words', 'labelled as'))
    out = []
    for k, v in sorted(grp.items(), key=lambda kv: -len(kv[1])):
        if len(v) < 60:
            continue
        five = Counter(' '.join(r['q'].lower().split()[:5]) for r in v)
        t5 = five.most_common(1)[0][1] / len(v)
        pops = Counter(r['pop'] for r in v).most_common(1)[0][0]
        print('  %-30s %6d %8.0f %5.0f %6.0f%% %6.1f  %s' % (k, len(v), sum(r['imp'] for r in v), sum(r['clk'] for r in v),
              100 * t5, statistics.mean(len(r['q'].split()) for r in v), pops))
        out.append({'opening': k, 'n': len(v), 'same5w': round(t5, 2), 'labelled': pops})
        if len(out) >= 25:
            break
    if o.json:
        json.dump({'rows': rows, 'templates': out, 'threshold': thresh,
                   'shares': {k: {'queries': len(v), 'impressions': sum(r['imp'] for r in v)} for k, v in by.items()}},
                  open(o.json, 'w', encoding='utf-8'), indent=1)
        print('\nwrote', o.json)


if __name__ == '__main__':
    main()
