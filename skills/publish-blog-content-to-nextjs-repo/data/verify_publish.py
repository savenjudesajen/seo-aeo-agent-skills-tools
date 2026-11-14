#!/usr/bin/env python3
"""Runnable gates for publishing blog content to a site with a hand-rolled Markdown renderer.

Gate 1  renderer   every content block maps to a node the site's parser supports; prints the per-post
                   counts it predicts for the live page (save them with --json)
Gate 2  literals   body text is safe inside a JS/TS template literal
        untouched  every post you did not target is byte-identical before and after the apply
Gate 4  live       each published URL returns 200 with no Markdown leaking through (needs network)
        html       the same checks on pages saved from the browser (offline)
        compare    live (or html) counts against gate 1's prediction

Gate 3 (typecheck) is `tsc --noEmit`, run separately. Python standard library only.

Usage:
    python3 verify_publish.py renderer [--json predicted.json] payload/*.md
    python3 verify_publish.py literals payload/*.md
    python3 verify_publish.py untouched --manifest manifest.json --before before/
    python3 verify_publish.py live [--scope article] [--json live.json] https://example.com/blog/a ...
    python3 verify_publish.py html [--scope article] [--json live.json] saved/a.html saved/b.html
    python3 verify_publish.py compare predicted.json live.json

Posts are keyed by slug: a payload file's stem, a saved page's stem, or a URL's last path segment.
Exit code is non-zero if any gate fails, so it can be used as a hard gate.
"""
import argparse
import json
import os
import pathlib
import re
import sys
import urllib.request

# ---------------------------------------------------------------------------------------------------
# The supported subset. EDIT THIS to match the site's renderer before trusting the result;
# reference/renderer-subset.md explains how to read it off the code. Rules are tried in order; the
# first match wins. Each rule: (name, html tag it renders as, predicate(block_text, non_empty_lines)).
SUPPORTED = [
    ('h2', 'h2', lambda t, L: t.startswith('## ')),
    ('h3', 'h3', lambda t, L: t.startswith('### ')),
    # Uncomment if the renderer promotes a block that is one bold-only line to a heading (set its tag).
    # ('bold-line', 'h3', lambda t, L: len(L) == 1 and re.fullmatch(r'\*\*[^*]+\*\*', L[0].strip()) is not None),
    ('ul', 'ul', lambda t, L: all(l.strip().startswith('- ') for l in L)),
    ('table', 'table', lambda t, L: L[0].strip().startswith('|')),
]
FALLBACK = ('p', 'p')

# Markdown the parser does NOT support: if any of these survive into a paragraph block, they render
# as literal text on the live page. Remove a row if the renderer does support that form.
LEAKS = [
    (r'(?m)^#',                         'heading marker in a paragraph'),
    (r'(?m)^\s*\d+[.)]\s',              'ordered list'),
    (r'(?m)^\s*>',                      'blockquote'),
    (r'!\[',                            'image'),
    (r'```|~~~',                        'code fence'),
    (r'(?m)^\s*(---|\*\*\*|___)\s*$',   'horizontal rule'),
    (r'(?m)^\s*[\*\+]\s',               'non-dash bullet'),
    (r'<[a-zA-Z/][^>]*>',               'raw html tag'),
    (r'\|',                             'stray pipe in a paragraph'),
    (r'(?m)^\s{4,}\S',                  'indented code block'),
    (r'\[[^\]]*\]\[[^\]]*\]',           'reference-style link'),
]
# Tags compared between the prediction and the live page.
COMPARED_TAGS = ('h2', 'h3', 'ul', 'table')
# ---------------------------------------------------------------------------------------------------

UNSAFE = [('`', 'backtick'), ('${', 'template interpolation'), ('\\', 'backslash')]


def classify(block):
    t = block.strip()
    if not t:
        return 'empty', None
    lines = [l for l in t.split('\n') if l.strip()]
    for name, tag, pred in SUPPORTED:
        if pred(t, lines):
            return name, tag
    return FALLBACK


def slug_of(label):
    label = label.rstrip('/')
    if '://' in label:
        label = label.split('?', 1)[0].split('#', 1)[0]
        return label.rsplit('/', 1)[-1]
    return pathlib.Path(label).stem


def write_json(path, data):
    if path:
        pathlib.Path(path).write_text(json.dumps(data, indent=2, sort_keys=True), encoding='utf-8')
        print('wrote ' + path)


# --- gate 1 ------------------------------------------------------------------------------------------
def gate_renderer(a):
    failures, predicted = 0, {}
    for p in a.paths:
        md = open(p, encoding='utf-8').read().replace('\r\n', '\n')
        blocks = re.split(r'\n\s*\n', md)
        counts, tags, problems = {}, {t: 0 for t in COMPARED_TAGS}, []
        for n, b in enumerate(blocks):
            name, tag = classify(b)
            counts[name] = counts.get(name, 0) + 1
            if tag in tags:
                tags[tag] += 1
            if name == 'p':
                for rx, label in LEAKS:
                    if re.search(rx, b):
                        problems.append('block %d: %s :: %s' % (n, label, b.strip()[:80]))
        if md.count('**') % 2:
            problems.append('odd ** count (an unclosed bold)')
        supported = sum(v for k, v in counts.items() if k not in ('p', 'empty'))
        print('%s\n   blocks=%d  %s\n   predicted %s' % (
            p, len(blocks), '  '.join('%s=%d' % kv for kv in sorted(counts.items())),
            ' '.join('%s=%d' % (t, tags[t]) for t in COMPARED_TAGS)))
        predicted[slug_of(p)] = tags
        if problems:
            failures += 1
            for q in problems[:10]:
                print('   FAIL ' + q)
        else:
            print('   ok - every block maps to a supported node (%d structured, %d paragraphs)'
                  % (supported, counts.get('p', 0)))
    write_json(a.json, predicted)
    return failures


# --- gate 2 ------------------------------------------------------------------------------------------
def gate_literals(a):
    failures = 0
    for p in a.paths:
        md = open(p, encoding='utf-8').read()
        bad = [name for seq, name in UNSAFE if seq in md]
        if bad:
            failures += 1
            print('%s  FAIL unsafe in a template literal: %s' % (p, ', '.join(bad)))
        else:
            print('%s  ok - safe inside a template literal' % p)
    return failures


def gate_untouched(a):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import apply_content as ac  # same folder: the one object-locating rule

    man = json.loads(pathlib.Path(a.manifest).read_text(encoding='utf-8'))
    lay = ac.layout_from(man)
    root = pathlib.Path(man.get('content_root', '.'))
    by_file = {}
    for slug, spec in man['posts'].items():
        by_file.setdefault(spec['file'], []).append(slug)

    failures = 0
    for rel, slugs in sorted(by_file.items()):
        before = (pathlib.Path(a.before) / rel).read_text(encoding='utf-8')
        after = (root / rel).read_text(encoding='utf-8')

        def strip_targets(src):
            spans = sorted(ac.locate_object(src, s, lay)[:2] for s in slugs)
            out, pos = [], 0
            for start, end in spans:
                out.append(src[pos:start])
                pos = end
            out.append(src[pos:])
            return '\x00'.join(out)

        try:
            same = strip_targets(before) == strip_targets(after)
        except SystemExit as e:
            failures += 1
            print('%s  FAIL %s' % (rel, e))
            continue
        tok = re.compile(r'\b%s: ' % re.escape(lay['slug_key']))
        n_before, n_after = len(tok.findall(before)), len(tok.findall(after))
        if same and n_before == n_after:
            print('%s  ok - %d target post(s) changed, the other %d byte-identical'
                  % (rel, len(slugs), n_before - len(slugs)))
        else:
            failures += 1
            print('%s  FAIL text outside the target posts changed (posts before=%d after=%d)'
                  % (rel, n_before, n_after))
    return failures


# --- gate 4 ------------------------------------------------------------------------------------------
def scoped(html, scope):
    if not scope:
        return html, False
    m = re.search(r'(?is)<%s[\s>].*?</%s>' % (scope, scope), html)
    return (m.group(0), True) if m else (html, False)


def inspect_page(label, status, html, scope):
    part, found = scoped(html, scope)
    body = re.sub(r'(?is)<script.*?</script>|<style.*?</style>', ' ', part)
    text = re.sub(r'(?s)<[^>]+>', '\n', body)
    leaks = []
    if '**' in text:
        leaks.append('literal **')
    if re.search(r'(?m)^\s*\|.*\|', text):
        leaks.append('literal pipe row')
    if re.search(r'\]\((?:https?:|/)', text):
        leaks.append('literal link syntax')
    if re.search(r'(?m)^\s*#{2,6}\s', text):
        leaks.append('literal heading marker')
    if re.search(r'&lt;/?[a-zA-Z]', part):
        leaks.append('escaped html tag shown as text')

    counts = {t: len(re.findall(r'<%s[\s>]' % t, body, re.I)) for t in COMPARED_TAGS}
    title = re.search(r'(?is)<title[^>]*>(.*?)</title>', html)
    ld = re.findall(r'(?is)<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html)
    faq_q = sum(len(re.findall(r'"@type"\s*:\s*"Question"', b)) for b in ld)
    ok = status == 200 and not leaks
    print('%s\n   status=%s  %s  ld_json=%d faq_q=%d%s\n   title: %s\n   %s' % (
        label, status, ' '.join('%s=%d' % (t, counts[t]) for t in COMPARED_TAGS), len(ld), faq_q,
        '' if not scope or found else '  (no <%s> found: counted the whole page)' % scope,
        re.sub(r'\s+', ' ', title.group(1)).strip()[:100] if title else '(none)',
        'ok' if ok else 'FAIL ' + (', '.join(leaks) or 'status %s' % status)))
    return ok, counts


def gate_live(a):
    failures, seen = 0, {}
    for u in a.paths:
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'publish-verify/1.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                status, html = r.status, r.read().decode('utf-8', 'replace')
        except Exception as e:  # a proxy 403 lands here: re-run with `html` on pages saved from a browser
            failures += 1
            print('%s\n   FAIL %s (if this is a sandbox proxy error, use the html mode)' % (u, e))
            continue
        ok, counts = inspect_page(u, status, html, a.scope)
        failures += 0 if ok else 1
        seen[slug_of(u)] = counts
    write_json(a.json, seen)
    return failures


def gate_html(a):
    failures, seen = 0, {}
    for p in a.paths:
        html = open(p, encoding='utf-8', errors='replace').read()
        ok, counts = inspect_page(p, 200, html, a.scope)
        failures += 0 if ok else 1
        seen[slug_of(p)] = counts
    write_json(a.json, seen)
    return failures


def gate_compare(a):
    pred = json.loads(pathlib.Path(a.predicted).read_text(encoding='utf-8'))
    live = json.loads(pathlib.Path(a.live).read_text(encoding='utf-8'))
    failures = 0
    for slug in sorted(set(pred) | set(live)):
        if slug not in pred or slug not in live:
            failures += 1
            print('%-40s FAIL only in %s' % (slug, 'prediction' if slug in pred else 'live'))
            continue
        diff = {t: live[slug].get(t, 0) - pred[slug].get(t, 0) for t in COMPARED_TAGS}
        bad = {t: d for t, d in diff.items() if d}
        if bad:
            failures += 1
            print('%-40s FAIL live minus predicted: %s' % (slug, ' '.join('%s=%+d' % kv for kv in bad.items())))
        else:
            print('%-40s ok - live matches the prediction' % slug)
    return failures


def main(argv=None):
    ap = argparse.ArgumentParser(description='Publish gates', usage=__doc__)
    sub = ap.add_subparsers(dest='mode', required=True)
    for mode in ('renderer', 'literals', 'live', 'html'):
        sp = sub.add_parser(mode)
        sp.add_argument('paths', nargs='+')
        if mode != 'literals':
            sp.add_argument('--json', help='write the per-post counts to this file')
        if mode in ('live', 'html'):
            sp.add_argument('--scope', help='count only inside the first <TAG>...</TAG> (e.g. article, main)')
    sp = sub.add_parser('untouched')
    sp.add_argument('--manifest', required=True)
    sp.add_argument('--before', required=True, help='folder holding the content files as they were before the apply')
    sp = sub.add_parser('compare')
    sp.add_argument('predicted')
    sp.add_argument('live')
    a = ap.parse_args(argv)

    fn = {'renderer': gate_renderer, 'literals': gate_literals, 'untouched': gate_untouched,
          'live': gate_live, 'html': gate_html, 'compare': gate_compare}[a.mode]
    failures = fn(a)
    print('\n%s gate: %s (%d failing)' % (a.mode, 'PASS' if failures == 0 else 'FAIL', failures))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
