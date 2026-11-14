#!/usr/bin/env python3
"""READ EVERYTHING THE REVIEWER DID TO A WORKBOOK, AND CHECK EACH COMMENT WAS ANSWERED.
Python standard library only; runs offline.

A workbook comes back from review. Before anything is changed:

    python3 data/review_round.py --returned <returned.xlsx> [--previous <the last workbook sent>]

lists every cell comment (sheet, cell, author, time, the text of the cell it sits on, that row's page and prompt, every
message of a thread) and, with --previous, every cell edited directly and every column added, dropped or moved.
Comments are not the only way a reviewer instructs: a find-and-replace across a column, or a column order rearranged,
carries no comment. Say what you found in the reply, count included, before acting on any of it.

After the new workbook is built (or through data/run_gates.py --returned):

    python3 data/review_round.py --returned <returned.xlsx> --workbook <new.xlsx>
    -> REVIEW ROUND: PASS

checks that
  1. every sheet of the returned workbook still exists in the new one (a returned column that has gone is a WARN for the
     hand read; a column whose header starts with "Change" is re-dated every round and exempt);
  2. the new workbook has a column whose header starts with "Reviewer" (Reviewer decision (<date>)), and
  3. every message of every comment is quoted in a cell of such a column, with what was done. A message counts as quoted
     when at least 90% of its words of four letters or more sit in one cell, so a light edit passes and an unanswered
     comment does not.

Comment formats read: Google Sheets exports (one note per cell holding the whole thread), Excel notes, Excel threaded
comments. The listing is sorted by sheet and cell, because the order inside the file is not the order on the sheet.
Exit 1 if a returned sheet is missing, the decision column is missing while comments exist, or a message is unanswered.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsx_lite import Workbook, cell_str, split_ref  # noqa: E402

NL = chr(10)
APOS, QUOT = chr(39), chr(34)
WS_SPLIT = r'(\s+)'
SMART = ((chr(0x2018), APOS), (chr(0x2019), APOS), (chr(0x201c), QUOT), (chr(0x201d), QUOT), (chr(0x2013), '-'), (chr(0x2014), '-'))


def norm(s):
    s = str(s or '').lower()
    for a, b in SMART:
        s = s.replace(a, b)
    return ' '.join(s.split())


def toks(s):
    return [t for t in re.findall('[a-z0-9' + APOS + ']+', norm(s)) if len(t.replace(APOS, '')) >= 4]


def anchor(wb, sheet, ref):
    """The text of the cell a comment sits on, and the page and prompt of its row."""
    if sheet not in wb.sheetnames:
        return '', {}
    rows = wb.rows(sheet)
    ci, rn = split_ref(ref)
    ctx = {}
    if rows:
        for j, h in enumerate(rows[0]):
            h = cell_str(h).lower()
            for key in ('page', 'prompt'):
                if key not in ctx and (h == key or h.startswith(key + ' (')) and rn - 1 < len(rows) and j < len(rows[rn - 1]):
                    ctx[key] = cell_str(rows[rn - 1][j])
    return wb.cell_text(sheet, ref), ctx


def find_replace(pairs):
    """If every differing cell is the same find-and-replace, return (old, new); else None."""
    reps = set()
    for x, y in pairs:  # x = returned, y = previous
        tx, ty = re.split(WS_SPLIT, x), re.split(WS_SPLIT, y)
        if len(tx) != len(ty):
            return None
        for p, q in zip(tx, ty):
            if p == q:
                continue
            i = 0
            while i < min(len(p), len(q)) and p[i] == q[i]:
                i += 1
            j = 0
            while j < min(len(p), len(q)) - i and p[-1 - j] == q[-1 - j]:
                j += 1
            reps.add((q[i:len(q) - j], p[i:len(p) - j]))
    return next(iter(reps)) if len(reps) == 1 else None


def diff_previous(ret, prev):
    rep = {'sheets_only_returned': [s for s in ret.sheetnames if s not in prev.sheetnames],
           'sheets_only_previous': [s for s in prev.sheetnames if s not in ret.sheetnames], 'sheets': {}}
    for name in ret.sheetnames:
        if name not in prev.sheetnames:
            continue
        a, b = ret.rows(name), prev.rows(name)
        if not a or not b:
            continue
        ha = [cell_str(c) for c in a[0]]
        hb = [cell_str(c) for c in b[0]]
        common = [h for h in ha if h and h in hb]
        info = {'added': [h for h in ha if h and h not in hb], 'dropped': [h for h in hb if h and h not in ha],
                'order_changed': common != [h for h in hb if h in ha], 'rows': (len(a), len(b)), 'edits': {}}
        for r in range(1, min(len(a), len(b))):
            for h in common:
                ia, ib = ha.index(h), hb.index(h)
                x = cell_str(a[r][ia]) if ia < len(a[r]) else ''
                y = cell_str(b[r][ib]) if ib < len(b[r]) else ''
                if x != y:
                    info['edits'].setdefault(h, []).append((r + 1, x, y))
        rep['sheets'][name] = info
    return rep


def decision_cells(wb):
    cells, has_col = [], False
    for name in wb.sheetnames:
        rows = wb.rows(name)
        if not rows:
            continue
        cols = [i for i, h in enumerate(rows[0]) if cell_str(h).lower().startswith('reviewer')]
        if not cols:
            continue
        has_col = True
        for rn, r in enumerate(rows[1:], 2):
            for i in cols:
                if i < len(r) and cell_str(r[i]):
                    cells.append((name, '%s%d' % (col_letter(i), rn), cell_str(r[i])))
    return has_col, cells


def col_letter(i):
    s = ''
    i += 1
    while i:
        i, rem = divmod(i - 1, 26)
        s = chr(65 + rem) + s
    return s


def quoted(msg, cell_text):
    if norm(msg) and norm(msg) in norm(cell_text):
        return 1.0
    t = toks(msg)
    if len(t) < 2:
        return 0.0
    have = set(toks(cell_text))
    return sum(1 for x in t if x in have) / len(t)


def header_warnings(ret, new):
    warns = []
    for name in ret.sheetnames:
        if name not in new.sheetnames or not ret.rows(name) or not new.rows(name):
            continue
        hn = {cell_str(c).lower() for c in new.rows(name)[0] if c}
        for c in ret.rows(name)[0]:
            h = cell_str(c)
            if not h or h.lower() in hn or h.lower().startswith('change'):
                continue
            warns.append('%s: the returned column %s is not in the new workbook (dropped or renamed; check it is on purpose)' % (name, h))
    return warns


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--returned', required=True)
    ap.add_argument('--previous')
    ap.add_argument('--workbook')
    ap.add_argument('--json')
    o = ap.parse_args()
    ret = Workbook(o.returned)
    comments = ret.comments()
    nmsg = sum(len(c['messages']) for c in comments)
    print('COMMENTS IN THE RETURNED WORKBOOK: %d cells, %d messages' % (len(comments), nmsg))
    for c in comments:
        val, ctx = anchor(ret, c['sheet'], c['ref'])
        print(NL + '  %s!%s   on: %s' % (c['sheet'], c['ref'], (val[:110] + ('...' if len(val) > 110 else '')) or '(empty cell)'))
        if ctx.get('page') and ctx['page'] != val:
            print('    page:   %s' % ctx['page'])
        if ctx.get('prompt') and ctx['prompt'] != val:
            print('    prompt: %s' % ctx['prompt'][:140])
        for m in c['messages']:
            print('    %s%s: %s' % (m['author'] or '?', ' (%s)' % m['time'] if m['time'] else '', m['text'].replace(NL, ' / ')))
    report = {'returned': o.returned, 'comments': comments, 'edits': None, 'answered': None}
    if o.previous:
        d = diff_previous(ret, Workbook(o.previous))
        report['edits'] = d
        print(NL + 'DIRECT EDITS, returned against previous (%s)' % o.previous)
        anything = bool(d['sheets_only_returned'] or d['sheets_only_previous'])
        for s in d['sheets_only_returned']:
            print('  sheet added by the reviewer: %s' % s)
        for s in d['sheets_only_previous']:
            print('  sheet dropped by the reviewer: %s' % s)
        for name, i in d['sheets'].items():
            if i['rows'][0] != i['rows'][1]:
                print('  %s: row count differs (returned %d, previous %d); row-by-row edits below may be misaligned' % (name, i['rows'][0], i['rows'][1]))
                anything = True
            if i['added']:
                print('  %s: columns added: %s' % (name, ', '.join(i['added'])))
                anything = True
            if i['dropped']:
                print('  %s: columns dropped: %s' % (name, ', '.join(i['dropped'])))
                anything = True
            if i['order_changed']:
                print('  %s: column order changed' % name)
                anything = True
            for h, e in i['edits'].items():
                fr = find_replace([(x, y) for _, x, y in e])
                anything = True
                print('  %s / %s: %d cells edited%s' % (name, h, len(e), ('; one find-and-replace: %s -> %s' % fr) if fr else ''))
                if not fr:
                    for r, x, y in e[:4]:
                        print('      row %d: was %r, now %r' % (r, y[:90], x[:90]))
        if not anything:
            print('  none: the reviewer changed nothing but the comments')
    if not o.workbook:
        if o.json:
            json.dump(report, open(o.json, 'w', encoding='utf-8'), indent=1, default=str)
        return
    print(NL + 'ANSWERS IN THE NEW WORKBOOK (%s)' % o.workbook)
    new = Workbook(o.workbook)
    has_col, cells = decision_cells(new)
    fails, answered = [], []
    for n in ret.sheetnames:
        if n not in new.sheetnames:
            fails.append('the returned sheet %s is missing from the new workbook' % n)
    if comments and not has_col:
        fails.append('the new workbook has no column headed Reviewer decision to answer %d comments in' % len(comments))
    for c in comments:
        for k, m in enumerate(c['messages']):
            best = max(((quoted(m['text'], t), s, r) for s, r, t in cells), default=(0.0, '', ''))
            ok = best[0] >= 0.9
            answered.append({'sheet': c['sheet'], 'ref': c['ref'], 'message': m['text'],
                             'answered_in': '%s!%s' % (best[1], best[2]) if ok else None, 'score': round(best[0], 2)})
            print('  %s %s!%s message %d: %s' % ('OK     ' if ok else 'MISSING', c['sheet'], c['ref'], k + 1,
                  ('quoted in %s!%s' % (best[1], best[2])) if ok else 'no Reviewer decision cell quotes it (best match %.0f%%)' % (best[0] * 100)))
            if not ok:
                fails.append('%s!%s message %d is not answered: %s' % (c['sheet'], c['ref'], k + 1, m['text'][:80].replace(NL, ' ')))
    for w in header_warnings(ret, new):
        print('  WARN    ' + w)
    report['answered'] = answered
    verdict = 'REVIEW ROUND: PASS' if not fails else 'REVIEW ROUND: FAIL'
    print(NL + verdict)
    for f in fails:
        print('  - ' + f)
    report['verdict'] = verdict
    report['fails'] = fails
    if o.json:
        json.dump(report, open(o.json, 'w', encoding='utf-8'), indent=1, default=str)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
