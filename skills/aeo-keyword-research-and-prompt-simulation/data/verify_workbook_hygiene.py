#!/usr/bin/env python3
"""WORKBOOK HYGIENE GATE: runs on every workbook this skill ships, keyword side or prompt side.
Python standard library only; runs offline.

Standing deliverable rules, checked on the saved file:
  1. SOURCE COLUMN. Every sheet carries a column whose header starts with "Source", filled on every data row. Prose
     sheets (README, Overview, Methodology, Method, Notes, Cover) are the method itself and are exempt.
  2. NO EM DASHES, in any cell or header.
  3. NO NARRATION OF HOW THE DATA WAS GATHERED inside a finding cell ("captured live", API, MCP, tool call, screenshot,
     scraped via, "our data pipeline"). Provenance belongs in the Source, Basis, anchor and evidence columns, which are
     exempt; the method belongs on the methodology tab. A tool name outside the provenance columns is a soft flag.
  4. NO AI VOCABULARY in client-facing cells (delve, leverage, seamless, robust, landscape, "in today's", "it's worth
     noting"): soft flag, read then fix or keep.
  5. CLOSED VOCABULARIES where the column exists: Content type, Tier, Scope, Stage, KPI. A FOLD row ("FOLD into <x>")
     and the context rows of a Prompt Map with a Row column are exempt.
  6. SHEET COUNT. With --asked N the workbook holds at most N + 1 sheets.
  7. SPELLING FOLLOWS THE MARKET. With --market us (or uk) the other market's spellings are flagged, except in columns
     whose header starts with Keyword (an observed string stays verbatim).
  8. REQUIRED SHEETS AND REASONS. --require-sheets "Scope Map,Exclusions" fails when one is missing; any column whose
     header starts with Reason, Why it is in the set, Why that KPI or Why a buyer must be filled on every row.

--skip-cols "Header prefix:reason" (repeatable) exempts a column from the narration and tool checks, for example a
column of verbatim excluded keywords that contain method words; the reason is printed.

Usage: python3 verify_workbook_hygiene.py deliverable.xlsx [--asked 3] [--market us] [--strict]
       [--require-sheets "Scope Map,Exclusions"] [--skip-cols "Excluded keyword:verbatim demand strings"]
Exit 1 on any hard flag. Soft flags are printed for the hand read and become hard with --strict.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsx_lite import Workbook, cell_str  # noqa: E402
from answer_types import CONTENT_TYPES, KPIS  # noqa: E402

EMDASH = chr(0x2014)
PROSE_SHEETS = {'readme', 'overview', 'methodology', 'method', 'notes', 'cover'}
PROVENANCE_COLS = ('source', 'basis', 'observed anchor', 'demand evidence', 'grounded in', 'why that kpi',
                   'flags and reasons', 'fan-out', 'placement evidence')
NARRATION_HARD = re.compile(r'\b(captured live|via the api|via api|via (the )?mcp\b|tool call|javascript|screenshot|'
                            r'(our|my|the|this) data pipeline|data pipeline (returned|pulled|ran|gathered|fetched)|'
                            r'extraction pipeline|scraped (from|via|with)|the tool (returned|gave|pulled))\b', re.I)
NARRATION_SOFT = re.compile(r'\b(scrap(e|ed|ing)|extract(ed|ion)? (from|via)|pulled (from|via)|we ran|i ran|fetched|'
                            r'pipeline)\b', re.I)
TOOLS = re.compile(r'\b(alsoasked|answer ?socrates|answerthepublic|semrush|ahrefs|keywords everywhere|search console|'
                   r'dataforseo|people also ask|paa|firecrawl|screaming frog)\b', re.I)
AI_VOCAB = re.compile(r"\b(delve|delving|leverag(e|es|ing)|seamless(ly)?|robust|landscape|in today'?s|"
                      r"it'?s worth noting|game[- ]changer|unlock(ing)? the|elevate)\b", re.I)
UK = re.compile(r'\b(optimis(e|ed|es|ing|ation)|programme|specialis(e|ed|es|ing)|analys(e|ed|es|ing)|organisation|'
                r'colour|behaviour|prioritis(e|ed|es|ing))\b', re.I)
US = re.compile(r'\b(optimiz(e|ed|es|ing|ation)|specializ(e|ed|es|ing)|analyz(e|ed|es|ing)|organization|color|'
                r'behavior|prioritiz(e|ed|es|ing))\b', re.I)
VOCAB = {
    'content type': set(CONTENT_TYPES),
    'tier': {'t1', 't2'},
    'scope': {'in segment', 'drift', 'adjacent-ask', 'adjacent - ask'},
    'stage': {'awareness', 'consideration', 'decision'},
    'kpi': set(KPIS),
}


def main():
    a = argparse.ArgumentParser()
    a.add_argument('xlsx')
    a.add_argument('--asked', type=int)
    a.add_argument('--market', choices=['us', 'uk'])
    a.add_argument('--strict', action='store_true')
    a.add_argument('--require-sheets', default='', help='comma-separated sheet names that must exist')
    a.add_argument('--skip-cols', action='append', default=[], help='"Header prefix:reason", repeatable')
    o = a.parse_args()
    skip_cols = {}
    for s in o.skip_cols:
        h, _, why = s.partition(':')
        if not why.strip():
            sys.exit('--skip-cols needs a reason: %s' % s)
        skip_cols[h.strip().lower()] = why.strip()
    wb = Workbook(o.xlsx)
    hard, soft = [], []
    for need in [x.strip() for x in o.require_sheets.split(',') if x.strip()]:
        if need.lower() not in [n.lower() for n in wb.sheetnames]:
            hard.append('required sheet missing: %s (have %s)' % (need, ', '.join(wb.sheetnames)))
    if o.asked is not None and len(wb.sheetnames) > o.asked + 1:
        hard.append('%d sheets for %d asked: a workbook holds what was asked for plus at most one extra sheet (%s)'
                    % (len(wb.sheetnames), o.asked, ', '.join(wb.sheetnames)))
    for name in wb.sheetnames:
        rows = wb.rows(name)
        if not rows:
            continue
        hdr = [cell_str(h) for h in rows[0]]
        low = [h.lower() for h in hdr]
        prose = name.strip().lower() in PROSE_SHEETS
        src = next((i for i, h in enumerate(low) if h.startswith('source')), None)
        if not prose and src is None:
            hard.append('%s: no Source column' % name)
        prov = {i for i, h in enumerate(low) if h.startswith(PROVENANCE_COLS)}
        skipped = {i for i, h in enumerate(low) for k in skip_cols if h.startswith(k)}
        vocab_cols = {i: VOCAB[k] for i, h in enumerate(low) for k in VOCAB if h.split(' (')[0] == k or h.startswith(k + ' (')}
        reason_cols = {i for i, h in enumerate(low) if h.startswith(('reason', 'why it is in the set', 'why that kpi', 'why a buyer'))}
        kw_cols = {i for i, h in enumerate(low) if h.startswith('keyword')}
        row_col = next((i for i, h in enumerate(low) if h == 'row'), None)
        data_rows = 0
        for rn, r in enumerate(rows, 1):
            if rn == 1:
                if not prose:
                    for h in hdr:
                        if EMDASH in h:
                            hard.append('%s: em dash in header "%s"' % (name, h))
                continue
            if not any(c not in (None, '') for c in r):
                continue
            first = cell_str(r[0]).upper() if r else ''
            if first in ('TOTAL', 'TOTALS'):
                continue
            data_rows += 1
            if not prose and src is not None and (src >= len(r) or r[src] in (None, '')):
                hard.append('%s row %d: Source cell empty (%s)' % (name, rn, cell_str(r[0])[:50]))
            context_row = row_col is not None and cell_str(r[row_col]).upper() not in ('', 'TRACKED')
            for rc in reason_cols:
                if not context_row and rc < len(r) and r[rc] in (None, ''):
                    hard.append('%s row %d: %s is empty (every decision carries its reason)' % (name, rn, hdr[rc]))
            rowkw = ' '.join(cell_str(r[k]).lower() for k in kw_cols if k < len(r) and r[k])
            for ci, c in enumerate(r):
                if c in (None, ''):
                    continue
                t = cell_str(c)
                col = hdr[ci] if ci < len(hdr) else str(ci)
                if EMDASH in t:
                    hard.append('%s row %d col %s: em dash: %s' % (name, rn, col, t[:80].replace('\n', ' ')))
                if ci in vocab_cols and t.strip().lower() not in vocab_cols[ci] and not (context_row or t.strip().lower().startswith('fold')):
                    hard.append('%s row %d: "%s" is not an allowed %s value (%s)' % (name, rn, t[:40], col, ', '.join(sorted(vocab_cols[ci]))))
                if ci in prov or prose or ci in kw_cols:
                    continue
                if ci in skipped:  # exempt from narration and tool checks only; spelling still follows the market
                    if o.market == 'us' and UK.search(t):
                        hard.append('%s row %d col %s: UK spelling for a US client: %s' % (name, rn, col, UK.search(t).group(0)))
                    if o.market == 'uk' and US.search(t):
                        hard.append('%s row %d col %s: US spelling for a UK client: %s' % (name, rn, col, US.search(t).group(0)))
                    continue
                m = NARRATION_HARD.search(t)
                if m and m.group(0).lower() in rowkw:
                    m = None  # the reason names the row's own keyword subject
                if m:
                    hard.append('%s row %d col %s: narrates the method ("%s"): %s' % (name, rn, col, m.group(0), t[:90].replace('\n', ' ')))
                m = NARRATION_SOFT.search(t)
                if m:
                    soft.append('%s row %d col %s: method wording ("%s"): %s' % (name, rn, col, m.group(0), t[:90].replace('\n', ' ')))
                m = TOOLS.search(t)
                if m:
                    soft.append('%s row %d col %s: tool name in a finding cell ("%s"): %s' % (name, rn, col, m.group(0), t[:90].replace('\n', ' ')))
                m = AI_VOCAB.search(t)
                if m:
                    soft.append('%s row %d col %s: AI vocabulary ("%s"): %s' % (name, rn, col, m.group(0), t[:90].replace('\n', ' ')))
                if o.market == 'us' and UK.search(t):
                    hard.append('%s row %d col %s: UK spelling for a US client: %s' % (name, rn, col, UK.search(t).group(0)))
                if o.market == 'uk' and US.search(t):
                    hard.append('%s row %d col %s: US spelling for a UK client: %s' % (name, rn, col, US.search(t).group(0)))
        print('%s: %d data rows, Source column %s' % (name, data_rows, 'exempt (prose sheet)' if prose else ('present' if src is not None else 'MISSING')))
    for h, why in skip_cols.items():
        print('  column check skipped for "%s": %s' % (h, why))
    if o.strict:
        hard, soft = hard + soft, []
    for f in hard:
        print('  FAIL ' + f)
    for f in soft[:60]:
        print('  read ' + f)
    if len(soft) > 60:
        print('  ... %d more soft flags' % (len(soft) - 60))
    print('WORKBOOK HYGIENE: %s (%d hard, %d soft)' % ('FAIL' if hard else 'PASS', len(hard), len(soft)))
    sys.exit(1 if hard else 0)


if __name__ == '__main__':
    main()
