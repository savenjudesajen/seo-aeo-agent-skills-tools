#!/usr/bin/env python3
"""Gate for the URL pruning audit workbook, the merge candidates workbook and the Cannibalization workbook.

Usage: python verify_audit_workbook.py <workbook.xlsx> [--cms-list cms_urls_not_in_crawl.txt] [--master master.tsv]

On a workbook without the audit sheets (a merge candidates workbook, or a standalone cannibalization
workbook) it checks the "Merge candidates" sheet (reference/merge-execution.md section 5) and any sheet
whose name starts with "Cannibalization" (the flat one-row-per-pair layout in reference/sheet-columns.md).
A "Query evidence" sheet is allowed beside them. Either sheet is also checked inside an audit workbook.
Exits 1 on any FAIL. Reads the workbook as written (cached cell values); it never edits it.
Python standard library only; runs offline.
"""
import collections
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

M = '{*}'  # any namespace (ElementTree wildcard, Python 3.8+): the OOXML namespaces need not be spelled out
EM_DASH = '—'


def _local(tag):
    return tag.rsplit('}', 1)[-1]


def _rel_id(sheet):
    """The sheet element's r:id attribute, whatever its namespace prefix."""
    return next((v for k, v in sheet.attrib.items() if _local(k) == 'id' and k.startswith('{')), None)


# ---------------------------------------------------------------- xlsx reading (stdlib)

def _col_index(ref):
    n = 0
    for ch in re.match(r'[A-Z]+', ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def _text(node):
    """Text of a shared-string item or inline string, skipping phonetic runs."""
    out = []
    for child in node:
        if _local(child.tag) == 't':
            out.append(child.text or '')
        elif _local(child.tag) == 'r':
            t = child.find(M + 't')
            if t is not None:
                out.append(t.text or '')
    return ''.join(out)


def load_workbook(path):
    """Return an ordered dict {sheet name: list of rows (lists of values)}."""
    z = zipfile.ZipFile(path)
    names = set(z.namelist())
    shared = []
    if 'xl/sharedStrings.xml' in names:
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall(M + 'si'):
            shared.append(_text(si))
    rels = {}
    for rel in ET.fromstring(z.read('xl/_rels/workbook.xml.rels')).findall(M + 'Relationship'):
        target = rel.get('Target')
        target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        rels[rel.get('Id')] = target
    book = collections.OrderedDict()
    for sh in ET.fromstring(z.read('xl/workbook.xml')).find(M + 'sheets').findall(M + 'sheet'):
        target = rels.get(_rel_id(sh))
        if not target or target not in names:
            continue
        grid = {}
        width = 0
        for row in ET.fromstring(z.read(target)).iterfind('.//' + M + 'row'):
            ri = int(row.get('r')) - 1 if row.get('r') else len(grid)
            cells = {}
            for k, c in enumerate(row.findall(M + 'c')):
                ci = _col_index(c.get('r')) if c.get('r') else k
                t = c.get('t')
                v = c.find(M + 'v')
                if t == 's' and v is not None:
                    val = shared[int(v.text)]
                elif t == 'inlineStr':
                    is_ = c.find(M + 'is')
                    val = _text(is_) if is_ is not None else None
                elif v is None or v.text is None:
                    val = None
                elif t in ('str', 'e'):
                    val = v.text
                elif t == 'b':
                    val = v.text == '1'
                else:
                    try:
                        f = float(v.text)
                        val = int(f) if f.is_integer() else f
                    except ValueError:
                        val = v.text
                if val == '':
                    val = None
                cells[ci] = val
                width = max(width, ci + 1)
            grid[ri] = cells
        rows = []
        for ri in range(max(grid) + 1 if grid else 0):
            cells = grid.get(ri, {})
            rows.append([cells.get(ci) for ci in range(width)])
        book[sh.get('name')] = rows
    return book


# ---------------------------------------------------------------- checks

def path(u):
    if u is None:
        return ''
    u = str(u).strip()
    p = urlparse(u).path if u.startswith('http') else u.split('?')[0]
    return (p.rstrip('/') or '/').lower()


def records(rows):
    if not rows:
        return []
    h = rows[0]
    out = []
    for r in rows[1:]:
        if any(v is not None for v in r):
            out.append(dict(zip(h, r)))
    return out


def em_dash_check(book, fails):
    for name, rows in book.items():
        for row in rows:
            hit = next((v for v in row if isinstance(v, str) and EM_DASH in v), None)
            if hit:
                fails.append(f'em dash in {name}: {hit[:60]}')
                break


def is_cannibalization_sheet(name):
    return name.strip().lower().startswith('cannibalization')


def is_merge_sheet(name):
    return name.strip().lower() == 'merge candidates'


def check_merge_candidates(name, grid, livep, fails, warns):
    """Merge candidates sheet: header in row 1, one row per page and its survivor."""
    need = ('page', 'survivor', 'decision', 'similarity', 'query overlap %', 'reason', 'source')
    ok_outcome = {'stays separate', 'on hold', 'done'}
    if not grid:
        fails.append(f'{name}: empty sheet')
        return
    h = [str(v).strip().lower() if v is not None else '' for v in grid[0]]
    missing = [c for c in need if c not in h]
    if missing:
        fails.append(f'{name}: missing columns {missing}')
        return
    rows_n = 0
    for r in grid[1:]:
        if not any(v is not None for v in r):
            continue
        rows_n += 1
        row = dict(zip(h, r))
        page, surv = row.get('page'), row.get('survivor')
        tag = f'{page} -> {surv}'
        for c in need:
            if row.get(c) in (None, ''):
                fails.append(f'{name}: empty {c}: {tag}')
        if page and surv and path(page) == path(surv):
            fails.append(f'{name}: survivor equals page: {tag}')
        if surv and path(surv) == '/':
            fails.append(f'{name}: survivor is the homepage: {tag}')
        elif surv and livep is not None and path(surv) not in livep:
            warns.append(f'{name}: survivor not on live sheet: {tag}')
        out = str(row.get('outcome') or '').strip().lower()
        if out and out not in ok_outcome:
            fails.append(f'{name}: Outcome {row.get("outcome")!r} not allowed (Stays separate, On hold, Done): {tag}')
        if out in ('stays separate', 'on hold') and not row.get('outcome note'):
            fails.append(f'{name}: {row.get("outcome")} with no Outcome note: {tag}')
    if rows_n == 0:
        fails.append(f'{name}: sheet has no rows')
    print(f'{name}: rows {rows_n}')


def main():
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'):
        print(__doc__)
        sys.exit(2)
    wbp = a[0]
    cms = a[a.index('--cms-list') + 1] if '--cms-list' in a else None
    master = a[a.index('--master') + 1] if '--master' in a else None
    book = load_workbook(wbp)
    fails, warns = [], []
    can = [s for s in book if is_cannibalization_sheet(s)]
    mrg = [s for s in book if is_merge_sheet(s)]
    if 'Live pages (200)' not in book and (can or mrg):
        for s in mrg:
            check_merge_candidates(s, book[s], None, fails, warns)
        for s in can:
            check_cannibalization(s, book[s], None, fails, warns)
        em_dash_check(book, fails)
        return report(fails, warns)
    need = {'Live pages (200)': ['URL', 'Decision', 'Action', 'Target', 'Review', 'Reason', 'Source'],
            'Redirects and non-200': ['URL', 'Status', 'Remove from CMS?', 'Redirect rule',
                                      'Safe to remove the rule now?', 'Reason', 'Source'],
            'Dynamic URL patterns': ['Pattern', 'Recommendation', 'How to do it', 'Research basis', 'Source']}
    for s, cols in need.items():
        if s not in book:
            fails.append(f'missing sheet {s}')
            continue
        h = book[s][0] if book[s] else []
        for c in cols:
            if c not in h:
                fails.append(f'{s}: missing column {c}')
    if fails:
        return report(fails, warns)
    extra = [s for s in book if s not in need and not is_cannibalization_sheet(s) and not is_merge_sheet(s)
             and s.strip().lower() != 'query evidence']
    if len(extra) > 1:
        warns.append(f'more than one extra sheet: {extra}')
    live = records(book['Live pages (200)'])
    red = records(book['Redirects and non-200'])
    dyn = records(book['Dynamic URL patterns'])
    em_dash_check(book, fails)

    seen = collections.Counter(path(r['URL']) for r in live)
    dup = [u for u, n in seen.items() if n > 1]
    if dup:
        fails.append(f'{len(dup)} duplicate URLs on live sheet, e.g. {dup[:3]}')
    livep = set(seen)
    for r in live:
        u = r['URL']
        if r['Decision'] not in ('Remain', 'Redirect', 'Retire'):
            fails.append(f'bad Decision {r["Decision"]!r}: {u}')
        for c in ('Action', 'Reason', 'Source'):
            if not r.get(c):
                fails.append(f'empty {c}: {u}')
        if r.get('Reason') and len(str(r['Reason'])) < 25:
            fails.append(f'Reason too short: {u}')
        if r['Decision'] in ('Redirect', 'Retire') and 'Return 410' not in str(r['Action']) and not r.get('Target'):
            fails.append(f'{r["Decision"]} without Target: {u}')
        if r['Decision'] in ('Redirect', 'Retire') and r.get('Review') != 'Y':
            warns.append(f'{r["Decision"]} row not flagged Review Y: {u}')
        t = r.get('Target')
        if t and str(t).startswith('http'):
            tp = path(t)
            if tp == '/':
                fails.append(f'target is the homepage (soft 404 risk): {u}')
            elif tp not in livep and r.get('Review') != 'Y':
                warns.append(f'target not on live sheet and not flagged Review Y: {u} -> {tp}')
            if tp == path(u):
                fails.append(f'target equals source: {u}')
    rc = collections.Counter(str(r.get('Reason')) for r in live)
    top = rc.most_common(1)[0] if rc else ('', 0)
    if live and top[1] > 1 and top[1] / len(live) > 0.3:
        fails.append(f'{top[1]} of {len(live)} reasons are identical: looks scripted, decide row by row')
    if live and 'Group' in live[0]:
        grp = collections.defaultdict(list)
        for r in live:
            if r.get('Group') not in (None, '-'):
                grp[r['Group']].append(r)
        for g, members in grp.items():
            tops = sum(1 for r in members if r.get('Role in group') == 'Top performer')
            if tops != 1:
                fails.append(f'group {g} has {tops} top performers')
        order = []
        for g in [r.get('Group') for r in live]:
            if g in ('-', None):
                continue
            if order and order[-1] != g and g in order:
                fails.append(f'rows of group {g} are not contiguous')
                break
            if not order or order[-1] != g:
                order.append(g)
        for r in live:
            if r.get('Decision') == 'Redirect' and not r.get('Merge check'):
                warns.append(f'Redirect row has no carry-over check: {r["URL"]}')
            size = r.get('Group size')
            if r.get('Group type') == 'Near-duplicate' and isinstance(size, (int, float)) and size > 12:
                warns.append(f'large group labelled Near-duplicate: {r["Group"]}')
    for r in red:
        u = r['URL']
        for c in ('Remove from CMS?', 'Redirect rule', 'Reason', 'Source'):
            if not r.get(c):
                fails.append(f'redirects: empty {c}: {u}')
        if str(r.get('Safe to remove the rule now?') or '').lower().startswith('yes'):
            fails.append(f'redirects: marked safe to remove rule without a backlink check: {u}')
        tg = r.get('Currently redirects to') or ''
        if tg and path(tg) == '/' and r.get('Redirect rule') == 'Keep 301' and r.get('Review') != 'Y':
            warns.append(f'redirects: homepage target not flagged: {u}')
    for r in dyn:
        for c in ('Recommendation', 'How to do it', 'Research basis', 'Source'):
            if not r.get(c):
                fails.append(f'dynamic: empty {c}: {r.get("Pattern")}')
    if live and 'Cannibalization' in live[0]:
        for r in live:
            sev = str(r.get('Cannibalization') or '')
            if sev.startswith('High') and r.get('Action') == 'Keep as is' and 'quer' not in str(r.get('Reason') or '').lower():
                warns.append(f'High cannibalization kept as is with no query reasoning: {r["URL"]}')
    for s in mrg:
        check_merge_candidates(s, book[s], livep if live else None, fails, warns)
    for s in can:
        check_cannibalization(s, book[s], livep if live else None, fails, warns)
    if cms:
        want = {path(l) for l in open(cms, encoding='utf-8') if l.strip()}
        have = livep | {path(r['URL']) for r in red}
        miss = sorted(want - have)
        if miss:
            fails.append(f'{len(miss)} CMS URLs missing from live and redirect sheets, e.g. {miss[:3]}')
    if master:
        want = set()
        for i, l in enumerate(open(master, encoding='utf-8')):
            if i:
                want.add(path(l.split('\t')[0]))
        have = livep | {path(r['URL']) for r in red}
        miss = sorted(x for x in want if x and x not in have and '?' not in x)
        if miss:
            warns.append(f'{len(miss)} master URLs not on live or redirect sheet '
                         f'(parameter URLs belong on the dynamic sheet), e.g. {miss[:3]}')
    print(f'live {len(live)}  redirects {len(red)}  dynamic {len(dyn)}')
    print(collections.Counter((r['Decision'], r['Action']) for r in live).most_common(12))
    return report(fails, warns)


def check_cannibalization(name, grid, livep, fails, warns):
    """Default format (reference/sheet-columns.md): a flat table, header in row 1, one row per pair."""
    ok_resolution = {'merge into owner', 're-target', 'split anchors', 'wait'}
    ok_type = {'home', 'offer', 'campaign landing', 'article', 'guide', 'short answer', 'listing or hub',
               'profile', 'other'}
    buying = {'offer', 'campaign landing'}
    supporting = {'article', 'guide', 'short answer'}
    need = ('pair id', 'severity', 'owner url', 'owner type', 'other url', 'other type', 'top shared query',
            'query overlap %', 'resolution', 'reason', 'source')
    if not grid:
        fails.append(f'{name}: empty sheet')
        return
    h = [str(v).strip().lower() if v is not None else '' for v in grid[0]]
    missing = [c for c in need if c not in h]
    if missing:
        fails.append(f'{name}: missing columns {missing}')
        return
    rows_n = 0
    seen_ids = collections.Counter()
    for r in grid[1:]:
        row = dict(zip(h, r))
        if not any(v is not None for v in r):
            continue
        rows_n += 1
        owner, other = row.get('owner url'), row.get('other url')
        tag = f'{row.get("pair id")}: {other} vs owner {owner}'
        seen_ids[str(row.get('pair id'))] += 1
        for c in need:
            if row.get(c) in (None, ''):
                fails.append(f'{name}: empty {c}: {tag}')
        res = str(row.get('resolution') or '').strip().lower()
        otype = str(row.get('owner type') or '').strip().lower()
        xtype = str(row.get('other type') or '').strip().lower()
        if res and res not in ok_resolution:
            fails.append(f'{name}: Resolution {row.get("resolution")!r} not allowed: {tag}')
        for label, t in (('Owner type', otype), ('Other type', xtype)):
            if t and t not in ok_type:
                fails.append(f'{name}: {label} {t!r} not in the page-type list: {tag}')
        if str(row.get('severity') or '').strip() not in ('High', 'Medium', 'Low'):
            fails.append(f'{name}: Severity must be High, Medium or Low: {tag}')
        if owner and other and path(owner) == path(other):
            fails.append(f'{name}: other URL equals owner: {tag}')
        if res == 'merge into owner':
            t = row.get('redirect target')
            if not t:
                fails.append(f'{name}: Merge into owner with no Redirect target: {tag}')
            elif path(t) == path(other):
                fails.append(f'{name}: redirect target equals the merged page: {tag}')
            elif livep is not None and path(t) not in livep:
                warns.append(f'{name}: Redirect target not on live sheet: {tag}')
            if xtype in buying and otype in supporting:
                fails.append(f'{name}: buying page merged into supporting content: {tag}')
        if res in ('re-target', 'split anchors') and not row.get('anchor split'):
            fails.append(f'{name}: {row.get("resolution")} with no Anchor split: {tag}')
        if res == 'wait' and not row.get('recheck date') and 'recheck' not in str(row.get('reason') or '').lower():
            fails.append(f'{name}: Wait with no Recheck date: {tag}')
    dup = [k for k, n in seen_ids.items() if n > 1]
    if dup:
        fails.append(f'{name}: duplicate Pair IDs {dup[:3]}')
    if rows_n == 0:
        fails.append(f'{name}: sheet has no pair rows')
    print(f'{name}: pairs {rows_n}')


def report(fails, warns):
    for w in warns[:40]:
        print('WARN', w)
    if len(warns) > 40:
        print(f'WARN ... {len(warns) - 40} more')
    for f in fails[:40]:
        print('FAIL', f)
    if len(fails) > 40:
        print(f'FAIL ... {len(fails) - 40} more')
    print('RESULT', 'FAIL' if fails else 'PASS')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
