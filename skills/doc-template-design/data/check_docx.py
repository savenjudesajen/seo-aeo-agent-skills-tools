# -*- coding: utf-8 -*-
"""check_docx.py (doc-template-design): offline gate for a finished .docx. Python standard library only.

    python3 check_docx.py <file.docx> [theme.json|slug] [--adopted]

Checks, from the file's XML (no rendering):
  - every XML part parses; header, footer and a page-number field are present
  - every font a run names is one of the theme's fonts; every text, fill and border colour is in its palette
  - every theme text/fill pair reads at 4.5:1 or better (WCAG AA)
  - no name from the theme's never_mention list appears in the body, headers or footers
  - structure: one title, numbered sections in order (1, 2, 3 ... then A, B ...), subsections numbered under
    their section, no empty heading, no short all-bold paragraph posing as a heading outside the block set
  - fonts are embedded (warning only when the file was built with embed_fonts=False)
  - no image wider than the text column; no leftover placeholder text (TODO, lorem ipsum, XX, [brackets],
    {braces}, "Client Name")
--adopted skips the palette, font and structure checks (a client's own template has its own rules) and keeps
the parse, never_mention, placeholder and image checks.
Prints "DOCX CHECK PASS" or "DOCX CHECK FAIL" with one line per finding.
"""
import os
import re
import sys
import zipfile
from xml.dom import minidom

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doctemplate import Theme, contrast, docx_font   # stdlib-only at import time

PLACEHOLDERS = re.compile(r'\bTODO\b|\blorem ipsum\b|\bXX+\b|\[[^\]]{1,40}\]|\{[^}]{1,40}\}|\bClient Name\b|'
                          r'\bTBD\b', re.I)


def texts(xml):
    return ''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)</w:t>', xml))


def paragraphs(xml):
    return re.findall(r'<w:p(?: [^>]*)?>(.*?)</w:p>', xml, re.S)


def main(argv):
    path = argv[0]
    adopted = '--adopted' in argv
    rest = [a for a in argv[1:] if not a.startswith('--')]
    t = Theme(rest[0] if rest else None)
    fails, warns = [], []
    z = zipfile.ZipFile(path)
    names = z.namelist()
    parts = {}
    for n in names:
        if n.endswith('.xml') or n.endswith('.rels'):
            data = z.read(n)
            try:
                minidom.parseString(data)
            except Exception as e:
                fails.append('%s does not parse: %s' % (n, e))
            parts[n] = data.decode('utf-8', 'replace')
    doc = parts.get('word/document.xml', '')
    heads = [v for k, v in parts.items() if re.match(r'word/header\d*\.xml$', k)]
    foots = [v for k, v in parts.items() if re.match(r'word/footer\d*\.xml$', k)]
    if not doc:
        fails.append('no word/document.xml')
    if not heads:
        warns.append('no header part')
    if not foots:
        fails.append('no footer part')
    elif not any(re.search(r'PAGE\b', f) for f in foots):
        fails.append('no page-number field in the footers')

    all_text = ' '.join(texts(x) for x in [doc] + heads + foots)
    low = all_text.lower()
    for w in t.never_mention:
        if w.lower() in low:
            fails.append('mentions "%s", which documents for %s must never carry' % (w, t.client))
    for m in sorted(set(PLACEHOLDERS.findall(all_text))):
        fails.append('placeholder text left in: "%s"' % m)

    # images no wider than the text column
    w_tw = re.search(r'<w:pgSz [^>]*w:w="(\d+)"', doc)
    ml = re.search(r'<w:pgMar [^>]*w:left="(\d+)"', doc)
    mr = re.search(r'<w:pgMar [^>]*w:right="(\d+)"', doc)
    if w_tw and ml and mr:
        col_emu = (int(w_tw.group(1)) - int(ml.group(1)) - int(mr.group(1))) * 635
        for cx in re.findall(r'<wp:extent cx="(\d+)"', doc):
            if int(cx) > col_emu + 6350:
                fails.append('image %.2fin wide in a %.2fin column' % (int(cx) / 914400.0, col_emu / 914400.0))

    if not adopted:
        # contrast of every theme pair
        for name, fill, col in t.contrast_pairs():
            r = contrast(fill, col)
            if r < 4.5:
                fails.append('%s: %s on %s reads at %.1f:1 (needs 4.5)' % (name, col, fill, r))
        # fonts named by runs and styles
        allowed = {docx_font(r)[0] for r in t.fonts.values() if r}
        for x in [doc, parts.get('word/styles.xml', ''), parts.get('word/numbering.xml', '')] + heads + foots:
            for f in set(re.findall(r'<w:rFonts [^>]*w:ascii="([^"]+)"', x)):
                f = f.replace('&quot;', '"').replace('&amp;', '&')
                if f not in allowed:
                    fails.append('font "%s" is not one of the theme fonts %s' % (f, sorted(allowed)))
        # colours
        palette = {c.upper() for c in t.colors.values()} | {c for pair in t.status.values() for c in pair} | {
            'FFFFFF', 'AUTO'}
        for x in [doc] + heads + foots:
            for c in set(re.findall(r'<w:color w:val="([0-9A-Fa-f]{6}|auto)"', x)) | set(
                    re.findall(r'w:fill="([0-9A-Fa-f]{6}|auto)"', x)) | set(
                    re.findall(r'<w:(?:top|left|bottom|right|insideH|insideV|bdr) [^>]*w:color="([0-9A-Fa-f]{6})"', x)):
                if c.upper() not in palette:
                    fails.append('colour %s is outside the theme palette' % c.upper())
        # structure
        ps = paragraphs(re.sub(r'<w:tbl>.*?</w:tbl>', '', doc, flags=re.S))     # paragraphs outside tables
        styles = [(re.search(r'<w:pStyle w:val="([^"]+)"', p), texts(p).strip(), p) for p in ps]
        titles = [s for s in styles if s[0] and s[0].group(1) == 'Title']
        if len(titles) != 1:
            fails.append('%d title paragraphs (expected exactly one)' % len(titles))
        expect_num, expect_letter, parent, sub = 1, 0, None, 0
        for m, tx, p in styles:
            st = m.group(1) if m else None
            if st in ('Heading1', 'Heading2') and not tx:
                fails.append('empty %s' % st)
                continue
            if st == 'Heading1':
                lead = tx.split()[0]
                if lead.isdigit():
                    if int(lead) != expect_num or expect_letter:
                        fails.append('section "%s" out of order (expected %d)' % (tx[:50], expect_num))
                    expect_num = int(lead) + 1
                elif len(lead) == 1 and lead.isalpha():
                    if ord(lead.upper()) - 64 != expect_letter + 1:
                        fails.append('appendix "%s" out of order' % tx[:50])
                    expect_letter = ord(lead.upper()) - 64
                else:
                    fails.append('section without a number: "%s"' % tx[:50])
                parent, sub = lead, 0
            elif st == 'Heading2':
                sub += 1
                want = '%s.%d' % (parent, sub)
                if not tx.startswith(want):
                    fails.append('subsection "%s" should be numbered %s' % (tx[:50], want))
            elif not st and tx and len(tx) < 70 and '<w:numPr>' not in p:
                runs = re.findall(r'<w:r>(.*?)</w:r>', p, re.S)
                if runs and all(re.search(r'<w:b/>', r) for r in runs if texts(r).strip()) and '<w:tbl' not in p:
                    warns.append('short all-bold paragraph looks like a heading outside the block set: "%s"' % tx)
        if not any(s[0] and s[0].group(1) == 'Heading1' for s in styles):
            warns.append('no numbered sections')
    # fonts embedded?
    ft = parts.get('word/fontTable.xml', '')
    if '<w:embedRegular' not in ft:
        warns.append('no embedded fonts: the reader\'s machine will substitute (built with embed_fonts=False?)')
    else:
        rels = parts.get('word/_rels/fontTable.xml.rels', '')
        for target in re.findall(r'Target="([^"]+)"', rels):
            if 'word/' + target not in names:
                fails.append('embedded font part missing: ' + target)

    for f in fails:
        print('FAIL ' + f)
    for w in warns:
        print('WARN ' + w)
    print('DOCX CHECK %s  (%d failures, %d warnings)' % ('FAIL' if fails else 'PASS', len(fails), len(warns)))
    return 1 if fails else 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
