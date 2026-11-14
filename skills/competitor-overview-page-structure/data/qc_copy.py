#!/usr/bin/env python3
"""qc_copy.py - copy gate for client-facing .docx / .pptx / .txt / .md deliverables. Standard library only, offline.

Scans every paragraph, table cell and slide text frame for a fixed set of copy bans and exits 1 when any hit
remains. Usage:
    python3 qc_copy.py file.docx|file.pptx|file.txt|file.md [--allow "phrase" ...] [--client "Client Name"]
                       [--cover-blocks 3] [--names "Benchmark Co" ...]
--client flags third-person mentions of the client name outside the first --cover-blocks text blocks (use it only
when the document is addressed TO the client).
--names exempts companies that are benchmark subjects from the tool-name rule only (a vendor whose page is an example
and whose name is also a tool name). Every other rule still applies to their lines.
Rules: em/en dash, spaced hyphen used as a dash, rather-than cadence, not-X-Y cadence, if-then construction, hollow
affirmations, hedging, formal transitions, trailing lists, AI vocabulary, doomsday framing, tool names in body copy,
process narration, data-availability admissions, reading instructions, uncertainty language, meta-commentary,
semicolons (review), questions in body copy (review). Lines starting with 'Source:' may name tools and sites."""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

BANNED_VOCAB = [
    'leverage', 'leverages', 'leveraging', 'robust', 'holistic', 'seamless', 'seamlessly', 'delve', 'tapestry',
    'testament', 'underscore', 'underscores', 'pivotal', 'standout', 'actionable insights', 'utilize', 'utilise',
    'comprehensive', 'unlock', 'unlocks', 'elevate', 'elevates', 'supercharge', 'deep dive', 'low-hanging fruit',
    'double down', 'game-changer', 'game changer', 'move the needle', "it's worth noting", 'it is worth noting',
    "it's important to note", 'it is important to note', 'realm', "in today's landscape",
    'at the end of the day', 'untapped potential', 'harness', 'genuine', 'genuinely', 'world-class', 'best-in-class',
    'cutting-edge', 'state-of-the-art', 'empower', 'synergy',
]
HEDGES = ['often considered', 'arguably', 'it could be said', 'generally speaking', 'may or may not',
          'some would argue', 'perhaps', 'potentially', 'seems to', 'appears to', 'might ', 'could be ']
TRANSITIONS = ['furthermore', 'moreover', 'additionally']
TRAILING = ['and more', 'etc.', 'and beyond', 'and so on']
AFFIRM = ['great question', 'absolutely!', 'certainly!', "you're right to ask"]
DOOM = ['left behind', 'obsolete', 'replaced by machines']
TOOLS = ['screaming frog', 'semrush', 'keywords everywhere', 'ga4', 'gsc', 'search console', 'pagespeed',
         'ahrefs', 'moz ', 'sitebulb', 'dataforseo', 'firecrawl', 'webfetch', 'playwright']
NARRATION = ['captured live', 'screenshot-validated', 'extraction', 'fetched', 'page fetch', 'scraped', 'crawled',
             'pulled through', 'api pull', 'we ran', 'we pulled', 'we captured', 'was captured', 'tool pull',
             're-run the', 'screenshot taken', 'captured on']
ADMISSIONS = ['n/a', "couldn't get", 'could not get', 'credits unavailable', 'pending a', 'unverified']
READING = ['worth reading', 'note that', 'as mentioned', 'keep in mind', 'as noted above']
UNCERTAIN = ['unclear', 'seems to be', 'we think', 'not sure', 'do not agree']
META = ['to be blunt', "won't sugar-coat", 'should not be softened', 'worth repeating']

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'


def _ptext(p, tag_t):
    return ''.join(t.text or '' for t in p.iter(tag_t))


def docx_lines(path):
    """Paragraphs outside tables, then table cells (one entry per cell), from word/document.xml."""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    body = root.find(W + 'body')
    out = []
    ti = 0
    for el in body:
        if el.tag == W + 'p':
            t = _ptext(el, W + 't')
            if t.strip():
                out.append(('p', t))
        elif el.tag == W + 'tbl':
            for tc in el.iter(W + 'tc'):
                t = '\n'.join(_ptext(p, W + 't') for p in tc.iter(W + 'p')).strip()
                if t:
                    out.append(('t%d' % ti, t))
            ti += 1
    return out


def pptx_lines(path):
    """Text of every paragraph on every slide (speaker notes are not client-facing copy)."""
    out = []
    with zipfile.ZipFile(path) as z:
        slides = sorted((n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)),
                        key=lambda n: int(re.findall(r'\d+', n)[-1]))
        for n in slides:
            si = int(re.findall(r'\d+', n)[-1])
            root = ET.fromstring(z.read(n))
            for p in root.iter(A + 'p'):
                t = _ptext(p, A + 't')
                if t.strip():
                    out.append(('s%d' % si, t))
    return out


def scan(lines, allow=(), client=None, cover_blocks=3, names=()):
    names = [n.lower() for n in names]
    hits = []
    for idx, (where, text) in enumerate(lines):
        low = text.lower()
        src = low.lstrip().startswith('source:')
        body = re.sub(r'"[^"]*"', '""', text)          # quoted material is the source's words
        blow = body.lower()

        def add(rule, frag):
            if any(a.lower() in low for a in allow):
                return
            hits.append((rule, where, frag, text[:140]))
        if '—' in text:
            add('em dash', '—')
        if '–' in text:
            add('en dash', '–')
        if re.search(r'\s-\s', body):
            add('spaced hyphen as dash', ' - ')
        if 'rather than' in blow:
            add('rather-than cadence', 'rather than')
        if re.search(r"\b(it's|it is|this is|that's) not\b[^.]*,", blow) or re.search(r'\bnot just\b', blow):
            add('not-X-Y cadence', 'not X, Y')
        if re.search(r'\bif\b[^.]{0,80}\bthen\b', blow):
            add('if-then construction', 'if ... then')
        for w in AFFIRM:
            if w in blow:
                add('hollow affirmation', w)
        for w in HEDGES:
            if w in blow:
                add('hedging', w.strip())
        for w in TRANSITIONS:
            if re.search(r'\b' + w + r'\b', blow):
                add('formal transition', w)
        for w in TRAILING:
            if w in blow:
                add('trailing list', w)
        for w in BANNED_VOCAB:
            if re.search(r'\b' + re.escape(w) + r'\b', blow):
                add('AI vocabulary', w)
        for w in DOOM:
            if w in blow:
                add('doomsday framing', w)
        if not src:
            for w in TOOLS:
                if w in blow and w.strip() not in names:
                    add('tool name in body', w.strip())
        for w in NARRATION:
            if w in blow:
                add('process narration', w)
        for w in ADMISSIONS:
            if re.search(r'(?<![a-z])' + re.escape(w) + r'(?![a-z])', blow):
                add('data-availability admission', w)
        for w in READING:
            if w in blow:
                add('reading instruction', w)
        for w in UNCERTAIN:
            if w in blow:
                add('uncertainty language', w)
        for w in META:
            if w in blow:
                add('meta-commentary', w)
        if client and idx >= cover_blocks and re.search(r'\b' + re.escape(client.lower()) + r'\b', blow) and not src:
            add('third-person client name (review)', client)
        if ';' in body and not src:
            add('semicolon (review)', ';')
        if re.search(r'\?(\s|$)', body) and not src:
            add('question in body (review)', '?')
    return hits


def main():
    import argparse
    ap = argparse.ArgumentParser(description='Copy gate for client-facing documents.')
    ap.add_argument('path')
    ap.add_argument('--allow', nargs='*', default=[], help='phrases whose lines are exempt')
    ap.add_argument('--client', default=None, help='client name to flag in third person')
    ap.add_argument('--cover-blocks', type=int, default=3, help='leading text blocks treated as the cover')
    ap.add_argument('--names', nargs='*', default=[],
                    help='benchmark companies that are also tool names (exempt from the tool-name rule only)')
    a = ap.parse_args()
    if a.path.endswith('.docx'):
        lines = docx_lines(a.path)
    elif a.path.endswith('.pptx'):
        lines = pptx_lines(a.path)
    else:
        # plain text or markdown: drop list markers and blockquote marks so '- item' is not read as a dash
        raw = open(a.path, encoding='utf-8').read().splitlines()
        lines = [('p', re.sub(r'^\s*(>\s*)*([-*+]|\d+[.)])?\s*', '', l)) for l in raw if l.strip()]
    hits = scan(lines, a.allow, a.client, a.cover_blocks, a.names)
    for rule, where, frag, text in hits:
        print('[%s] (%s) %r :: %s' % (rule, where, frag, text))
    print('\n%d hit(s) across %d text blocks' % (len(hits), len(lines)))
    sys.exit(1 if hits else 0)


if __name__ == '__main__':
    main()
