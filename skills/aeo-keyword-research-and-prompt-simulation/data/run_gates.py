#!/usr/bin/env python3
"""RUN EVERY GATE, from the deliverable alone. Python standard library only; runs offline.

    python3 data/run_gates.py --workbook <deliverable.xlsx> --corpus <corpus.json> --asked <N> --market us
    -> ALL GATES: PASS

Gates invoked one by one, each with its own input files, get skipped. Here every input except the corpus is derived from
the workbook itself (the Prompt Map and the Keyword Map), so "no input file" is never a reason, and a gate that cannot
run is a FAIL unless skipped with a written reason (--skip gate:reason), printed in the report.

Gates, in order:
  hygiene     verify_workbook_hygiene.py  every sheet: Source column, no em dashes, no method narration, closed
                                          vocabularies, sheet count, market spelling
  tracked     verify_tracked_set.py       the prompt sheet contract and set-level rules (checks 1 to 13)
  audit       prompt_audit.py             does each prompt belong on its page (A1 to A7, KPI, stage)
  grounding   ground_check.py             verbatim, anchored and keyword-verbatim grounding against the corpus
  review      review_round.py             a pass after a reviewer round (--returned): every comment quoted with what was
                                          done in a 'Reviewer decision' column; returned sheets still exist. Without
                                          --returned it is SKIPPED (a first pass has no comments).

Required when the workbook has a prompt sheet: --brands <json list of the client's brand and product names
plus every tracked competitor's>; the run stops with a message when it is missing or empty.

Optional: --returned <workbook sent back> [--previous <last workbook sent>], --evidence <placement json>,
--qualifiers <file, one qualifier word per line, replacing the default
list>, --acronyms <file of abbr=expansion lines>, --report <path.json>, --floor / --floor-reason / --min-seeds for the
grounding gate, --strict and --require-sheets and --skip-cols for the hygiene gate.
Exit 1 if any gate FAILS.
"""
import argparse
import collections
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from xlsx_lite import Workbook, cell_str, header_index  # noqa: E402
from answer_types import parse_check, primary_type  # noqa: E402
from prompt_audit import load_brands  # noqa: E402  (exits with the --brands message)

STOP = {'which', 'what', 'are', 'the', 'a', 'an', 'for', 'to', 'of', 'in', 'and', 'is', 'do', 'i', 'my', 'with', 'that',
        'should', 'can', 'how', 'does', 'on', 'or', 'it', 'you', 'some', 'best', 'top'}
# Words that qualify a page's audience or market. Neutral default; replace per client with --qualifiers.
QUALIFIERS = {'b2b', 'b2c', 'saas', 'enterprise', 'ecommerce', 'startup', 'startups', 'smb', 'small', 'local',
              'nonprofit', 'agency', 'agencies', 'education', 'retail', 'manufacturing', 'us', 'usa', 'uk', 'canada',
              'australia'}


def derive(wb, sheet, qualifiers):
    """Prompts and pages for prompt_audit and ground_check, read off the Prompt Map and the Keyword Map."""
    if sheet not in wb.sheetnames:
        return None, None, 'no sheet named %s (have %s)' % (sheet, ', '.join(wb.sheetnames))
    rows = wb.rows(sheet)
    hdr = rows[0]
    c = {k: header_index(hdr, k) for k in ['page', 'content type', 'answer shape', 'cluster core page',
                                            'answer type', 'kpi', 'stage', 'prompt', 'family', 'keywords mapped',
                                            'basis', 'observed anchor']}
    c['row'] = next((i for i, h in enumerate(hdr) if cell_str(h).lower() == 'row'), None)
    if c['page'] is None or c['prompt'] is None:
        return None, None, 'the prompt sheet has no Page or Prompt column'

    def v(r, k):
        i = c[k]
        return cell_str(r[i]) if i is not None and i < len(r) else ''
    prompts, pages = [], {}
    for r in rows[1:]:
        if not v(r, 'prompt'):
            continue
        if c['row'] is not None and v(r, 'row') != 'TRACKED':
            continue
        page = v(r, 'page')
        kws = [ln for ln in v(r, 'keywords mapped').split('\n') if ln.strip() and not ln.strip().startswith('(no keyword')]
        prompts.append({'prompt': v(r, 'prompt'), 'page': page, 'answer_type': primary_type(v(r, 'answer type')),
                        'stage': v(r, 'stage'), 'kpi': v(r, 'kpi'), 'family': v(r, 'family'), 'kws': len(kws),
                        'basis': v(r, 'basis'), 'anchor': v(r, 'observed anchor')})
        if page not in pages:
            pages[page] = {'ctype': v(r, 'content type'), 'core': [], 'quals': [], 'nkw': 0, 'vol': 0,
                           'core_page': v(r, 'cluster core page').lower() == 'yes',
                           'format_check': parse_check(v(r, 'answer shape')) or ''}
        if parse_check(v(r, 'answer shape')) == 'mismatch':
            # the page check is page level: any tracked row whose trailing check is MISMATCH marks the page
            pages[page]['format_check'] = 'mismatch'
    if 'Keyword Map' in wb.sheetnames:
        km = wb.rows('Keyword Map')
        kh = km[0]
        kc = header_index(kh, 'keyword')
        vc = next((i for i, h in enumerate(kh) if 'volume' in cell_str(h).lower()), None)
        pc = header_index(kh, ('page (final)', 'page'))
        per = collections.defaultdict(list)
        for r in km[1:]:
            if kc is None or pc is None or kc >= len(r) or not r[kc]:
                continue
            pg = cell_str(r[pc])
            vol = r[vc] if vc is not None and vc < len(r) and isinstance(r[vc], (int, float)) else 0
            if pg in pages:
                per[pg].append((cell_str(r[kc]).lower(), vol or 0))
        for pg, lst in per.items():
            lst.sort(key=lambda x: -x[1])
            pages[pg]['nkw'] = len(lst)
            pages[pg]['vol'] = sum(x[1] for x in lst)
            core = []
            for k, _ in lst[:3]:
                for t in re.findall(r'[a-z0-9]+', k):
                    if t not in STOP and t not in core:
                        core.append(t)
            pages[pg]['core'] = core
            if len(lst) >= 2:
                common = set.intersection(*[set(re.findall(r'[a-z0-9]+', k)) for k, _ in lst])
                pages[pg]['quals'] = sorted(t for t in common if t in qualifiers)
    return prompts, pages, None


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--workbook', required=True)
    a.add_argument('--sheet', default='Prompt Map')
    a.add_argument('--corpus')
    a.add_argument('--asked', type=int)
    a.add_argument('--market', choices=['us', 'uk'])
    a.add_argument('--strict', action='store_true')
    a.add_argument('--require-sheets', default='')
    a.add_argument('--skip-cols', action='append', default=[])
    a.add_argument('--evidence')
    a.add_argument('--brands')
    a.add_argument('--qualifiers')
    a.add_argument('--acronyms')
    a.add_argument('--report')
    a.add_argument('--own-budget', type=int, default=1,
                   help='simulated OWN rows allowed per topic cluster (observed OWN rows never count)')
    a.add_argument('--returned', help='the workbook the reviewer sent back: runs the review gate')
    a.add_argument('--previous', help='the last workbook sent to the reviewer: lists direct edits')
    a.add_argument('--floor', type=float, default=0.50)
    a.add_argument('--floor-reason', default='')
    a.add_argument('--min-seeds', type=int, default=20)
    a.add_argument('--skip', action='append', default=[], help='gate:reason')
    o = a.parse_args()
    skips = {}
    for s in o.skip:
        g, _, why = s.partition(':')
        if not why.strip():
            sys.exit('--skip needs a reason: %s' % s)
        skips[g.strip()] = why.strip()
    qualifiers = QUALIFIERS
    if o.qualifiers:
        qualifiers = {ln.strip().lower() for ln in open(o.qualifiers, encoding='utf-8') if ln.strip()}
    results = {}

    def record(gate, status, out):
        results[gate] = {'status': status, 'output': out}
        print('\n=== %s: %s\n%s' % (gate, status, out))

    py = sys.executable
    if 'hygiene' in skips:
        record('hygiene', 'SKIPPED', skips['hygiene'])
    else:
        cmd = [py, os.path.join(HERE, 'verify_workbook_hygiene.py'), o.workbook]
        if o.asked is not None:
            cmd += ['--asked', str(o.asked)]
        if o.market:
            cmd += ['--market', o.market]
        if o.strict:
            cmd += ['--strict']
        if o.require_sheets:
            cmd += ['--require-sheets', o.require_sheets]
        for sc in o.skip_cols:
            cmd += ['--skip-cols', sc]
        rc, out = run(cmd)
        record('hygiene', 'PASS' if rc == 0 else 'FAIL', out)
    wb = Workbook(o.workbook)
    sheet = o.sheet if o.sheet in wb.sheetnames else ('Tracked Prompts' if 'Tracked Prompts' in wb.sheetnames else None)
    if sheet is None:
        for g in ('tracked', 'audit', 'grounding'):
            record(g, 'SKIPPED', 'no prompt sheet in the workbook (keyword-side deliverable)')
    else:
        if 'tracked' in skips:
            record('tracked', 'SKIPPED', skips['tracked'])
        else:
            cmd = [py, os.path.join(HERE, 'verify_tracked_set.py'), o.workbook, '--sheet', sheet, '--own-budget', str(o.own_budget)]
            if o.acronyms:
                cmd += ['--acronyms', o.acronyms]
            rc, out = run(cmd)
            record('tracked', 'PASS' if rc == 0 else 'FAIL', out)
        prompts, pages, err = derive(wb, sheet, qualifiers)
        if err:
            record('audit', 'FAIL', err)
            record('grounding', 'FAIL', err)
        else:
            tmp = tempfile.mkdtemp()
            pj, gj = os.path.join(tmp, 'prompts.json'), os.path.join(tmp, 'pages.json')
            json.dump(prompts, open(pj, 'w', encoding='utf-8'))
            json.dump(pages, open(gj, 'w', encoding='utf-8'))
            if 'audit' in skips:
                record('audit', 'SKIPPED', skips['audit'])
            else:
                cmd = [py, os.path.join(HERE, 'prompt_audit.py'), '--prompts', pj, '--pages', gj]
                if o.evidence:
                    cmd += ['--evidence', o.evidence]
                bj = os.path.join(tmp, 'brands.json')
                json.dump(load_brands(o.brands), open(bj, 'w', encoding='utf-8'))
                cmd += ['--brands', bj]
                rc, out = run(cmd)
                record('audit', 'PASS' if rc == 0 else 'FAIL', out)
            if 'grounding' in skips:
                record('grounding', 'SKIPPED', skips['grounding'])
            elif not o.corpus:
                record('grounding', 'FAIL', 'no --corpus given: the grounding gate needs the observed-question corpus. Pass it, or --skip grounding:"<reason>"')
            else:
                rc, out = run([py, os.path.join(HERE, 'ground_check.py'), '--prompts', pj, '--corpus', o.corpus,
                               '--floor', str(o.floor), '--floor-reason', o.floor_reason, '--min-seeds', str(o.min_seeds)])
                record('grounding', 'PASS' if rc == 0 else 'FAIL', out)
    if 'review' in skips:
        record('review', 'SKIPPED', skips['review'])
    elif not o.returned:
        record('review', 'SKIPPED', 'no --returned workbook: a first pass has no reviewer comments. A pass after a review must be given --returned.')
    else:
        cmd = [py, os.path.join(HERE, 'review_round.py'), '--returned', o.returned, '--workbook', o.workbook]
        if o.previous:
            cmd += ['--previous', o.previous]
        rc, out = run(cmd)
        record('review', 'PASS' if rc == 0 else 'FAIL', out)
    print('\n' + '=' * 72)
    for g, r in results.items():
        print('  %-10s %s%s' % (g, r['status'], ('  (' + skips[g] + ')') if r['status'] == 'SKIPPED' and g in skips else ''))
    failed = [g for g, r in results.items() if r['status'] == 'FAIL']
    verdict = 'ALL GATES: PASS' if not failed else 'GATES FAILED: ' + ', '.join(failed)
    print('  ' + verdict)
    if o.report:
        json.dump({'workbook': o.workbook, 'verdict': verdict, 'gates': results, 'skips': skips, 'floor': o.floor,
                   'floor_reason': o.floor_reason}, open(o.report, 'w', encoding='utf-8'), indent=1)
        print('  report written to', o.report)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
