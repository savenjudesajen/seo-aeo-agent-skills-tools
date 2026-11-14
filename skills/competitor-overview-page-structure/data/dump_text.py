# -*- coding: utf-8 -*-
"""Dump a .docx in reading order (paragraphs and tables interleaved) for the fresh-context reviewer.
Run: python3 dump_text.py file.docx > file.txt"""
import sys
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

d = Document(sys.argv[1])
body = d.element.body
for el in body.iterchildren():
    tag = el.tag.split('}')[1]
    if tag == 'p':
        t = Paragraph(el, d).text.strip()
        if t:
            print(t)
    elif tag == 'tbl':
        tb = Table(el, d)
        print('[TABLE]')
        for r in tb.rows:
            cells, seen = [], set()
            for c in r.cells:
                if id(c._tc) in seen:
                    continue
                seen.add(id(c._tc))
                cells.append(c.text.strip().replace('\n', ' / '))
            print(' | '.join(cells))
        print('[/TABLE]')
