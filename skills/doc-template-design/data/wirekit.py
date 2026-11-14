# -*- coding: utf-8 -*-
"""Status-tagged page wireframes drawn in the document's own theme (doc-template-design).

Uses the theme's colours and the same font files the .docx embeds (Theme.font_files()), so a wireframe placed
in a themed document matches it. Nothing is hard-coded per client. Needs Pillow; without fontTools or network it
falls back to Pillow's default font (the layout still works, the type will not match the document).

    from wirekit import Wire
    w = Wire('themes/<slug>.json', width=1300, height=2400)        # or Wire() for the neutral default
    y = w.header('Recommended booking page (desktop)')               # title + legend, returns the next y
    y = w.navbar(y, 'Navigation: add a Support link')
    y = w.box(40, y + 20, 640, y + 140, 'Rework', 'Checkout button', ['One button, above the fold']) + 20
    w.save('wire.png', bottom=y + 40)

Statuses: Keep, Rework, New, Remove, Optional, Later (chip colours from the theme's status map). Later marks a
block that waits for content only the client can supply."""
import io
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doctemplate import STATUSES, Theme, docx_font   # saved alongside


def _rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _blend(c, base=(255, 255, 255), a=0.16):
    return tuple(int(round(base[i] * (1 - a) + c[i] * a)) for i in range(3))


class Wire:
    def __init__(self, theme=None, width=1300, height=2400):
        self.t = t = theme if isinstance(theme, Theme) else Theme(theme)
        self.W, self.H = width, height
        self.im = Image.new('RGB', (width, height), 'white')
        self.d = ImageDraw.Draw(self.im)
        self._fc = {}
        try:
            self._files = t.font_files()
        except Exception as e:                       # offline or no fontTools: default font
            print('wirekit: theme fonts unavailable (%s); using the default font' % e)
            self._files = {}
        self._roles = self._role_files()
        self.INK, self.MUTED = _rgb(t.ink), _rgb(t.muted)
        self.STRIPE, self.ALERT, self.PANEL = _rgb(t.stripe), _rgb(t.alert), _rgb(t.panel)
        self.BAR, self.BAR_TEXT, self.RULE = _rgb(t.accent), _rgb(t.accent_text), _rgb(t.rule)
        looks = {'New': (_blend(self.STRIPE), self.INK, False), 'Rework': (self.PANEL, self.INK, False),
                 'Keep': ((255, 255, 255), self.INK, False), 'Remove': ((255, 255, 255), self.ALERT, True),
                 'Optional': ((255, 255, 255), self.MUTED, True), 'Later': (_blend(self.MUTED, a=0.1), self.MUTED, False)}
        self.st = {}
        for s in STATUSES:
            fill, txt = (_rgb(x) for x in t.status[s])
            box, bout, dashed = looks[s]
            self.st[s] = dict(fill=fill, txt=txt, outline=fill if fill != (255, 255, 255) else txt, box=box,
                              bout=bout, dashed=dashed)

    # ------------------------------------------------------------------ fonts
    def _role_files(self):
        """role -> font file inside font_files(): body, bold, title, label."""
        f, t = self._files, self.t
        base = lambda role: docx_font(t.fonts[role])[0].replace(' ', '') if t.fonts.get(role) else None
        out = {'body': base('body') + '-regular.ttf',
               'bold': (base('strong') or base('body')) + ('-bold.ttf' if t.strong_bold else '-regular.ttf'),
               'title': (base('title') or base('body')) + ('-bold.ttf' if t.title_bold else '-regular.ttf')}
        sec = base('section')
        out['label'] = (sec + ('-bold.ttf' if t.section_bold else '-regular.ttf')) if sec else out['bold']
        return {k: v for k, v in out.items() if v in f}

    def font(self, size, role='body'):
        name = self._roles.get(role) or self._roles.get('body')
        key = (name, size)
        if key not in self._fc:
            if name:
                self._fc[key] = ImageFont.truetype(io.BytesIO(self._files[name]), size)
            else:
                try:
                    self._fc[key] = ImageFont.load_default(size)
                except TypeError:                     # Pillow < 10.1
                    self._fc[key] = ImageFont.load_default()
        return self._fc[key]

    def caps(self, s):
        return s.upper() if self.t.section_caps else s

    # ------------------------------------------------------------------ primitives
    def text(self, x, y, s, size=15, role='body', color=None):
        self.d.text((x, y), s, font=self.font(size, role), fill=color or self.INK)

    def tlen(self, s, size=15, role='body'):
        return self.d.textlength(s, font=self.font(size, role))

    def wrap(self, s, maxw, size=15, role='body'):
        lines, cur = [], ''
        for w in s.split():
            nxt = (cur + ' ' + w).strip()
            if self.tlen(nxt, size, role) <= maxw or not cur:
                cur = nxt
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def chip(self, x, y, status, size=13):
        s = self.st[status]
        label = status.upper()
        w = self.tlen(label, size, 'label') + 16
        self.d.rounded_rectangle([x, y, x + w, y + size + 9], radius=3, fill=s['fill'], outline=s['outline'], width=1)
        self.text(x + 8, y + 3, label, size, 'label', s['txt'])
        return w

    def dashed(self, x0, y0, x1, y1, col, step=14, dash=7, width=2):
        for xx in range(int(x0), int(x1), step):
            self.d.line([xx, y0, min(xx + dash, x1), y0], fill=col, width=width)
            self.d.line([xx, y1, min(xx + dash, x1), y1], fill=col, width=width)
        for yy in range(int(y0), int(y1), step):
            self.d.line([x0, yy, x0, min(yy + dash, y1)], fill=col, width=width)
            self.d.line([x1, yy, x1, min(yy + dash, y1)], fill=col, width=width)

    def box(self, x0, y0, x1, y1, status, title, lines=(), title_size=18, line_size=14, wrap=True):
        """A block with a stripe on the left, its status chip top right, a bold title and muted lines.
        Returns the y below the last line drawn."""
        s = self.st[status]
        if s['dashed']:
            self.dashed(x0, y0, x1, y1, s['bout'])
        else:
            self.d.rectangle([x0, y0, x1, y1], fill=s['box'], outline=self.RULE, width=1)
            self.d.rectangle([x0, y0, x0 + 4, y1], fill=s['bout'] if status != 'New' else self.STRIPE)
        cw = self.tlen(status.upper(), 13, 'label') + 16
        self.chip(x1 - 10 - cw, y0 + 9, status)
        ty = y0 + 10
        for tl in (self.wrap(title, x1 - x0 - 40 - cw, title_size, 'bold') if wrap else [title]):
            self.text(x0 + 16, ty, tl, title_size, 'bold')
            ty += title_size + 5
        yy = ty + 4
        for ln in lines:
            for sub in (self.wrap(ln, x1 - x0 - 30, line_size) if (wrap and ln) else [ln]):
                self.text(x0 + 16, yy, sub, line_size, 'body', self.MUTED)
                yy += line_size + 6
        return yy

    def navbar(self, y, label, x0=40, x1=None, h=36):
        x1 = x1 or self.W - 40
        self.d.rectangle([x0, y, x1, y + h], fill=self.BAR)
        self.text(x0 + 14, y + (h - 15) // 2 - 1, self.caps(label), 14, 'label', self.BAR_TEXT)
        return y + h

    def header(self, title, sub='Status against the current page', x=40, y=24, statuses=None):
        """Title plus a legend of the statuses the wireframe uses (all six when statuses is None)."""
        self.text(x, y, title, 28, 'title')
        ly, lx = y + 52, x
        for s in (statuses or STATUSES):
            lx += self.chip(lx, ly, s) + 10
        self.text(lx + 6, ly + 1, sub, 14, 'body', self.MUTED)
        self.d.line([x, ly + 34, self.W - 40, ly + 34], fill=self.RULE, width=1)
        return ly + 46

    def arrow_down(self, x, y0, y1, label_lines=(), col=None):
        col = col or self.MUTED
        for yy in range(int(y0), int(y1) - 6, 16):
            self.d.line([x, yy, x, min(yy + 8, y1 - 6)], fill=col, width=2)
        self.d.polygon([(x - 7, y1 - 14), (x + 7, y1 - 14), (x, y1 - 2)], fill=col)
        for i, t in enumerate(label_lines):
            self.text(x + 14, y0 + 8 + i * 19, t, 13, 'body', self.MUTED)

    def save(self, path, bottom=None):
        im = self.im.crop((0, 0, self.W, min(self.H, int(bottom or self.H))))
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        im.save(path)
        return im.size


if __name__ == '__main__':
    w = Wire(sys.argv[1] if len(sys.argv) > 1 else None, 1000, 900)
    y = w.header('Wireframe kit sample')
    y = w.navbar(y, 'Navigation') + 20
    for s in STATUSES:
        y = max(w.box(40, y, 960, y + 90, s, '%s block' % s, ['A body line in the muted colour']), y + 90) + 14
    print(w.save('wirekit_sample.png', bottom=y + 20))
