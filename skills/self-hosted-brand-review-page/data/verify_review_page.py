#!/usr/bin/env python3
'''Gate for a self-hosted '<brand> review' page.

Checks the page AS A NON-JS CRAWLER SEES IT (raw HTML, no script execution)
against the quote ledger. Run it on the raw HTML of the draft or live page:

    python -I verify_review_page.py --ledger ledger.csv --html page.html
        [--min-negatives 2] [--disclosure 'Published by <Brand>']
        [--today YYYY-MM-DD] [--warn-char X ...]

page.html is a plain HTTP GET of the URL (curl, fetch, or view-source text),
never the rendered DOM: the point is to prove the quotes are in the server HTML
that AI crawlers which do not run JavaScript read.

Ledger columns (CSV with header; extra columns ignored):
    id, platform, quote, source_url, reviewer, date, sentiment, licence_ok,
    expires_on, Source
  sentiment: positive | negative | mixed
  licence_ok: yes | no  (cleared under the client's recorded quoting policy)
  expires_on: YYYY-MM-DD or blank (Capterra / GetApp / Software Advice: date + 12 months)

Python standard library only; runs offline.
Exit code 1 on any FAIL. WARN lines need a decision, not necessarily a fix.
'''
import argparse
import csv
import datetime as dt
import html
import json
import re
import sys
import unicodedata

# curly quotes, nbsp, ellipsis, en and em dash -> plain equivalents
QUOTE_CHARS = {
    chr(0x2018): chr(39), chr(0x2019): chr(39), chr(0x201C): chr(34), chr(0x201D): chr(34),
    chr(0x00A0): ' ', chr(0x2026): '...', chr(0x2013): '-', chr(0x2014): '-',
}


def norm(text):
    text = html.unescape(text)
    text = unicodedata.normalize('NFKC', text)
    for k, v in QUOTE_CHARS.items():
        text = text.replace(k, v)
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()


def visible_text(raw):
    raw = re.sub(r'(?is)<(script|style|noscript|template)\b.*?</\1>', ' ', raw)
    raw = re.sub(r'(?is)<iframe\b.*?</iframe>', ' ', raw)
    raw = re.sub(r'(?s)<[^>]+>', ' ', raw)
    return norm(raw)


def jsonld_blocks(raw):
    for m in re.finditer(r'(?is)<script[^>]+application/ld\+json[^>]*>(.*?)</script>', raw):
        body = m.group(1).strip()
        try:
            yield json.loads(body)
        except Exception:
            yield {'__unparsed__': body[:200]}


def walk_types(node, found):
    if isinstance(node, dict):
        t = node.get('@type')
        if isinstance(t, list):
            found.update(t)
        elif t:
            found.add(t)
        for k, v in node.items():
            if k in ('review', 'aggregateRating'):
                found.add(k)
            walk_types(v, found)
    elif isinstance(node, list):
        for v in node:
            walk_types(v, found)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ledger', required=True)
    ap.add_argument('--html', required=True)
    ap.add_argument('--min-negatives', type=int, default=2)
    ap.add_argument('--disclosure', default='', help='phrase that must appear, e.g. Published by <Brand>')
    ap.add_argument('--today', default=dt.date.today().isoformat())
    ap.add_argument('--warn-char', action='append', default=[],
                    help='a character the style guide bans in copy (repeatable); warns if present in the HTML')
    a = ap.parse_args()

    with open(a.html, encoding='utf-8', errors='replace') as fh:
        raw = fh.read()
    text = visible_text(raw)
    hrefs = {norm(h) for h in re.findall(r'(?i)href\s*=\s*[\x22\x27]([^\x22\x27]+)', raw)}
    today = dt.date.fromisoformat(a.today)

    fails, warns = [], []
    with open(a.ledger, encoding='utf-8-sig') as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        fails.append('ledger is empty')
    on_page = 0
    negatives = 0
    for r in rows:
        rid = r.get('id') or '?'
        q = norm(r.get('quote', ''))
        if not q:
            fails.append(rid + ': empty quote')
            continue
        present = q in text
        if not present:
            # excerpts cut with an ellipsis: every fragment must be on the page
            frags = [f.strip() for f in re.split(r'\.\.\.|\[\.\.\.\]', q) if len(f.strip()) > 20]
            present = bool(frags) and all(f in text for f in frags)
        if not present:
            warns.append(rid + ': quote not found in server HTML (not placed, edited, or JS/iframe-only)')
            continue
        on_page += 1
        url = norm(r.get('source_url', ''))
        if not url:
            fails.append(rid + ': no source_url in ledger')
        elif url not in hrefs:
            fails.append(rid + ': quote is on the page but its source link is not (' + r.get('source_url', '') + ')')
        if not (r.get('date') or '').strip():
            fails.append(rid + ': no date in ledger')
        if (r.get('licence_ok') or '').strip().lower() != 'yes':
            fails.append(rid + ': on page without licence or permission cleared (' + (r.get('platform') or '') + ')')
        exp = (r.get('expires_on') or '').strip()
        if exp:
            try:
                exp_d = dt.date.fromisoformat(exp)
                if exp_d <= today:
                    fails.append(rid + ': expired on ' + exp + ' (platform age rule)')
                elif (exp_d - today).days < 45:
                    warns.append(rid + ': expires ' + exp + ', rotate soon')
            except ValueError:
                fails.append(rid + ': bad expires_on ' + exp)
        if not (r.get('Source') or '').strip():
            fails.append(rid + ': Source column empty')
        if (r.get('sentiment') or '').strip().lower() in ('negative', 'mixed'):
            negatives += 1

    if on_page == 0:
        fails.append('no ledger quote is present in the server HTML')
    if negatives < a.min_negatives:
        fails.append('only %d negative or mixed quotes on the page (min %d); a page with no pushback reads as a testimonial wall'
                     % (negatives, a.min_negatives))

    types = set()
    for block in jsonld_blocks(raw):
        walk_types(block, types)
    banned = {'Review', 'AggregateRating', 'review', 'aggregateRating'} & types
    if banned:
        fails.append('self-serving review markup present: ' + ', '.join(sorted(banned)))
    if not ({'Article', 'BlogPosting', 'WebPage'} & types):
        warns.append('no Article, BlogPosting or WebPage JSON-LD found')

    if a.disclosure and norm(a.disclosure) not in text:
        fails.append('disclosure phrase missing: ' + a.disclosure)
    for ch in a.warn_char:
        if ch and ch in raw:
            warns.append('banned character %r present in page HTML (style guide)' % ch)
    for m in re.finditer(r'(?is)<iframe[^>]+src=[\x22\x27]([^\x22\x27]+)', raw):
        if 'linkedin.com/embed' in m.group(1):
            warns.append('LinkedIn iframe present: fine for readers, invisible to crawlers; the quote must also be in HTML')
            break

    print('quotes in ledger: %d | on page (server HTML): %d | negative or mixed on page: %d'
          % (len(rows), on_page, negatives))
    for w in warns:
        print('WARN', w)
    for f in fails:
        print('FAIL', f)
    print('RESULT', 'FAIL' if fails else 'PASS')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
