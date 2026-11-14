#!/usr/bin/env python3
r"""In-place apply of blog bodies into TypeScript / JavaScript object-literal content files.

Reads a manifest, replaces each post's body template literal, rewrites metadata fields, and appends a
structured-data field. Guards refuse rather than corrupt. Python standard library only.

Manifest (JSON):
{
  "content_root": ".",
  "structured_field": "structuredData",
  "layout": {                      # the repo's own conventions; read them off existing posts
    "slug_key": "slug",            # posts are found by  <slug_key>: <quote><slug><quote>
    "body_key": "body",            # the body is the template literal  <body_key>: `...`
    "quote": "\"",                 # quote style of string fields (' or ")
    "object_indent": 2,            # spaces before the { and } that open and close one post object
    "field_indent": 4,             # spaces before each field inside a post object
    "json_indent": 2               # indent inside the JSON.stringify({...}) block
  },
  "posts": {
    "<slug>": {
      "file": "src/content/<file>.ts",
      "body": "payload/<slug>.md",
      "structured": "payload/<slug>.jsonld.json",          # optional
      "meta": {"title": "New title or null", "description": "..."}
    }
  }
}
(Comments above are for the reader; the real manifest is plain JSON.)

Run from the repo root:
    python3 apply_content.py --manifest ./manifest.json          # dry run: report only
    python3 apply_content.py --manifest ./manifest.json --apply  # write the files
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

UNSAFE = ('`', '${', '\\')

DEFAULT_LAYOUT = {
    'slug_key': 'slug',
    'body_key': 'body',
    'quote': '"',
    'object_indent': 2,
    'field_indent': 4,
    'json_indent': 2,
}


def fail(msg):
    raise SystemExit('REFUSED: ' + msg)


def layout_from(manifest):
    lay = dict(DEFAULT_LAYOUT)
    lay.update(manifest.get('layout') or {})
    if lay['quote'] not in ("'", '"'):
        fail('layout.quote must be \' or "')
    return lay


def slug_token(slug, lay):
    return '%s: %s%s%s' % (lay['slug_key'], lay['quote'], slug, lay['quote'])


def locate_object(src, slug, lay):
    """Return (start, end, body_start, body_end) of one post object, or raise SystemExit.

    start/end bound the object's text from the line holding its opening brace up to (not including)
    the newline before its closing brace. body_start/body_end bound the body literal's content.
    """
    tok = slug_token(slug, lay)
    i = src.find(tok)
    if i < 0:
        fail('slug not found: ' + slug)
    if src.find(tok, i + 1) >= 0:
        fail('slug appears more than once: ' + slug)

    opener = '\n' + ' ' * lay['object_indent'] + '{'
    start = src.rfind(opener, 0, i) + 1
    if start <= 0:
        fail('object start not found: ' + slug)

    # Locate the body literal FIRST. The end-of-object scan must begin AFTER it; otherwise a body
    # that contains the closing-brace pattern (a code sample, say) truncates the object and
    # corrupts the file.
    marker = '%s: `' % lay['body_key']
    o = src.find(marker, i)
    if o < 0:
        fail('body literal not found: ' + slug)
    cs = o + len(marker)
    ce = src.find('`', cs)
    if ce < 0:
        fail('unterminated body literal: ' + slug)

    closer = re.compile(r'\n {%d}\},?' % lay['object_indent'])
    m = closer.search(src, ce)
    if not m:
        fail('object end not found: ' + slug)
    # The next post's slug must not sit between this body and the closer we found.
    nxt = re.compile(r'\b%s: ' % re.escape(lay['slug_key'])).search(src, ce, m.start())
    if nxt:
        fail('object end scan ran into another post after: ' + slug)
    return start, m.start(), cs, ce


def quote_value(v, quote):
    return v.replace('\\', '\\\\').replace(quote, '\\' + quote)


def format_json(obj, lay):
    """Pretty-print JSON the way a hand-written literal would look: every line after the first is
    shifted to the field indent."""
    lines = json.dumps(obj, indent=lay['json_indent'], ensure_ascii=False).split('\n')
    pad = ' ' * lay['field_indent']
    return '\n'.join(l if n == 0 else pad + l for n, l in enumerate(lines))


def patch_object(src, slug, body, structured, meta, field, lay):
    start, end, cs, ce = locate_object(src, slug, lay)
    obj = src[start:end]
    cs -= start
    ce -= start
    old_len = ce - cs

    if structured is not None and re.search(r'\b%s\s*:' % re.escape(field), obj):
        fail('object already has %s: %s' % (field, slug))

    # Metadata is rewritten outside the body only, so text inside the body can never match a field.
    head, tail = obj[:cs], obj[ce:]
    q = re.escape(lay['quote'])
    for key, val in (meta or {}).items():
        if val is None:
            continue
        rx = re.compile(r'(\b%s: %s)((?:[^%s\\]|\\.)*)(%s)' % (re.escape(key), q, q, q))
        sub = lambda mm: mm.group(1) + quote_value(val, lay['quote']) + mm.group(3)
        if rx.search(head):
            head = rx.sub(sub, head, count=1)
        elif rx.search(tail):
            tail = rx.sub(sub, tail, count=1)
        else:
            fail('field not found: %s on %s' % (key, slug))
    obj = head + body + tail

    if structured is not None:
        obj = obj.rstrip()
        if not obj.endswith(','):
            obj += ','
        obj += '\n%s%s: JSON.stringify(%s),' % (' ' * lay['field_indent'], field, format_json(structured, lay))

    return src[:start] + obj + src[end:], old_len, len(body)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--apply', action='store_true', help='write the files (default: dry run)')
    a = ap.parse_args()

    man = json.loads(pathlib.Path(a.manifest).read_text(encoding='utf-8'))
    lay = layout_from(man)
    root = pathlib.Path(man.get('content_root', '.'))
    field = man.get('structured_field', 'structuredData')

    edits, report = {}, []
    for slug, spec in man['posts'].items():
        rel = spec['file']
        src = edits.get(rel)
        if src is None:
            src = (root / rel).read_text(encoding='utf-8')
            if '\r\n' in src:
                fail('%s has CRLF line endings; normalize the working copy first' % rel)
        body = pathlib.Path(spec['body']).read_text(encoding='utf-8')
        structured = None
        if spec.get('structured'):
            structured = json.loads(pathlib.Path(spec['structured']).read_text(encoding='utf-8'))

        for bad in UNSAFE:
            if bad in body:
                fail('unsafe sequence %r in the body of %s' % (bad, slug))
        if '`' in json.dumps(structured or {}):
            fail('backtick in the structured data of %s' % slug)

        src, old_len, new_len = patch_object(src, slug, body, structured, spec.get('meta'), field, lay)
        edits[rel] = src
        report.append(dict(slug=slug, file=rel, old_body=old_len, new_body=new_len,
                           structured=structured is not None,
                           body_sha=hashlib.sha256(body.encode('utf-8')).hexdigest()[:16]))

    for rel, src in edits.items():
        if src.count('`') % 2:
            fail('odd backtick count in ' + rel)
    if a.apply:
        for rel, src in edits.items():
            (root / rel).write_text(src, encoding='utf-8')

    print(json.dumps(dict(applied=a.apply, files=sorted(edits), posts=report), indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
