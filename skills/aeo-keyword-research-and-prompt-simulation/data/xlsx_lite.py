#!/usr/bin/env python3
"""Minimal .xlsx reader for the gate scripts. Python standard library only; no network.

    from xlsx_lite import Workbook
    wb = Workbook('deliverable.xlsx')
    wb.sheetnames                 -> ['Prompt Map', 'Keyword Map', ...]
    wb.rows('Prompt Map')         -> [[cell, cell, ...], ...]   (row 1 first; None for empty cells)
    wb.cell_text('Prompt Map', 'D12') -> the text of one cell ('' when empty)
    wb.comments()                 -> [{'sheet', 'ref', 'messages': [{'author', 'time', 'text'}]}]

Values come back as str, int, float or bool. Formulas are read as their cached values (save the workbook from a
spreadsheet program, or compute values in code, if a formula cell shows None). Dates come back as serial numbers.
"""
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'pr': 'http://schemas.openxmlformats.org/package/2006/relationships',
      'tc': 'http://schemas.microsoft.com/office/spreadsheetml/2018/threadedcomments'}
RID = '{%s}id' % NS['r']
NL = chr(10)


def col_index(ref):
    """'C12' -> 2 (zero-based column)."""
    letters = re.match(r'[A-Z]+', ref.upper()).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def split_ref(ref):
    """'C12' -> (2, 12): zero-based column, one-based row."""
    m = re.match(r'([A-Z]+)(\d+)', ref.upper())
    return col_index(m.group(1)), int(m.group(2))


def _resolve(base, target):
    if target.startswith('/'):
        return target.lstrip('/')
    return posixpath.normpath(posixpath.join(posixpath.dirname(base), target))


def _text(node):
    return ''.join(t.text or '' for t in node.iter('{%s}t' % NS['m']))


def _number(s):
    try:
        f = float(s)
    except (TypeError, ValueError):
        return s
    return int(f) if f.is_integer() and 'e' not in s.lower() and '.' not in s else f


class Workbook:
    def __init__(self, path):
        self.path = path
        self.z = zipfile.ZipFile(path)
        names = set(self.z.namelist())
        self.shared = []
        if 'xl/sharedStrings.xml' in names:
            root = ET.fromstring(self.z.read('xl/sharedStrings.xml'))
            self.shared = [_text(si) for si in root.findall('m:si', NS)]
        wb = ET.fromstring(self.z.read('xl/workbook.xml'))
        rels = ET.fromstring(self.z.read('xl/_rels/workbook.xml.rels'))
        rid_to_target = {r.get('Id'): _resolve('xl/workbook.xml', r.get('Target', ''))
                         for r in rels.findall('pr:Relationship', NS)}
        self._parts = [(s.get('name'), rid_to_target.get(s.get(RID))) for s in wb.findall('m:sheets/m:sheet', NS)]
        self.sheetnames = [n for n, _ in self._parts]
        self._cache = {}

    def _part(self, sheet):
        for n, p in self._parts:
            if n == sheet:
                return p
        raise KeyError('no sheet named %r (have %s)' % (sheet, ', '.join(self.sheetnames)))

    def rows(self, sheet):
        """All rows of a sheet as lists, padded to the widest row; empty cells are None."""
        if sheet in self._cache:
            return self._cache[sheet]
        root = ET.fromstring(self.z.read(self._part(sheet)))
        by_row = {}
        width = 0
        for row in root.iter('{%s}row' % NS['m']):
            rn = int(row.get('r'))
            cells = {}
            pos = 0
            for c in row.findall('m:c', NS):
                ref = c.get('r')
                ci = col_index(ref) if ref else pos
                pos = ci + 1
                t = c.get('t', 'n')
                v = c.find('m:v', NS)
                if t == 's' and v is not None:
                    val = self.shared[int(v.text)]
                elif t == 'inlineStr':
                    is_ = c.find('m:is', NS)
                    val = _text(is_) if is_ is not None else ''
                elif t == 'b' and v is not None:
                    val = v.text == '1'
                elif t in ('str', 'e') and v is not None:
                    val = v.text
                elif v is not None and v.text is not None:
                    val = _number(v.text)
                else:
                    val = None
                if val == '':
                    val = None
                cells[ci] = val
                width = max(width, ci + 1)
            by_row[rn] = cells
        out = []
        for rn in range(1, (max(by_row) if by_row else 0) + 1):
            cells = by_row.get(rn, {})
            out.append([cells.get(i) for i in range(width)])
        self._cache[sheet] = out
        return out

    def cell_text(self, sheet, ref):
        ci, rn = split_ref(ref)
        rows = self.rows(sheet)
        if rn - 1 >= len(rows) or ci >= len(rows[rn - 1]):
            return ''
        return cell_str(rows[rn - 1][ci])

    def _rels(self, part):
        rp = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')
        if rp not in self.z.namelist():
            return []
        root = ET.fromstring(self.z.read(rp))
        return [(r.get('Type', ''), _resolve(part, r.get('Target', ''))) for r in root.findall('pr:Relationship', NS)]

    def comments(self):
        """Every cell comment: Excel notes, Excel threaded comments, and Google Sheets exports (one note per cell
        holding the whole thread: the root after a line of = signs, each reply after a line of - signs)."""
        names = set(self.z.namelist())
        persons = {}
        if 'xl/persons/person.xml' in names:
            for p in ET.fromstring(self.z.read('xl/persons/person.xml')):
                persons[p.get('id')] = p.get('displayName')
        out = []
        for name, part in self._parts:
            if not part:
                continue
            threaded = {}
            for typ, target in self._rels(part):
                if typ.endswith('/threadedComment') and target in names:
                    items = [c for c in ET.fromstring(self.z.read(target)) if c.tag.endswith('threadedComment')]
                    items.sort(key=lambda c: (c.get('parentId') is not None, c.get('dT') or ''))
                    for c in items:
                        t = c.find('{%s}text' % NS['tc'])
                        threaded.setdefault(c.get('ref'), []).append(
                            {'author': persons.get(c.get('personId'), c.get('personId')), 'time': c.get('dT'),
                             'text': (t.text if t is not None else '') or ''})
            for ref, msgs in threaded.items():
                out.append({'sheet': name, 'ref': ref, 'messages': msgs})
            for typ, target in self._rels(part):
                if not typ.endswith('/comments') or target not in names:
                    continue
                root = ET.fromstring(self.z.read(target))
                authors = [(a.text or '') for a in root.findall('m:authors/m:author', NS)]
                for c in root.findall('m:commentList/m:comment', NS):
                    text = _text(c)
                    ref = c.get('ref')
                    if text.startswith('[Threaded comment]') or ref in threaded:
                        continue
                    aid = int(c.get('authorId', 0))
                    who = authors[aid] if aid < len(authors) else ''
                    if re.match('^={3,}', text) or text.startswith('ID#'):
                        msgs = google_thread(text, who)
                    else:
                        body = text
                        if who and body.startswith(who + ':'):
                            body = body[len(who) + 1:]
                        msgs = [{'author': who, 'time': None, 'text': body.strip()}]
                    out.append({'sheet': name, 'ref': ref, 'messages': msgs})
        order = {n: i for i, n in enumerate(self.sheetnames)}

        def key(c):
            ci, rn = split_ref(c['ref'])
            return order.get(c['sheet'], 99), rn, ci
        return sorted(out, key=key)


def google_thread(text, fallback_author):
    msgs = []
    for block in re.split(r'^(?:={3,}|-{3,})[ ]*$', text, flags=re.M):
        lines = block.strip(NL).split(NL)
        if not ''.join(lines).strip():
            continue
        i = 1 if lines[0].startswith('ID#') else 0
        author, when = None, None
        if i < len(lines):
            m = re.match(r'^(.*?)[ ]{2,}[(]([0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9:]+)[)][ ]*$', lines[i])
            if m:
                author, when, i = m.group(1).strip(), m.group(2), i + 1
        msgs.append({'author': author or fallback_author, 'time': when, 'text': NL.join(lines[i:]).strip()})
    return msgs


def cell_str(v):
    """A cell value as text, the way a reader sees it."""
    if v is None:
        return ''
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    if isinstance(v, (int, float)):
        return str(int(v)) if float(v).is_integer() else str(round(float(v), 6))
    return str(v).replace('\r\n', NL).replace('\r', NL).strip()


def header_index(header, name):
    """Index of the first header that starts with name (or any of a tuple of names), case-insensitive; else None."""
    low = [cell_str(h).lower() for h in header]
    for n in (name if isinstance(name, tuple) else (name,)):
        for i, h in enumerate(low):
            if h.startswith(n):
                return i
    return None
