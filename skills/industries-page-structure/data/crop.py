# -*- coding: utf-8 -*-
"""Crop map for the benchmark and client-site captures (Pillow).

Copy the raw full-scale browser captures into $WORK/raw, then list one entry per figure:

    'out.png': ('raw file', (left, top, right, bottom), [blur boxes])

Boxes are in raw pixels. Blur boxes cover personal contact details (people blocks). A block that spans two scroll
positions goes in STITCH as (raw file, box) pieces stacked top to bottom; put the seam at a row or block boundary.
POINTER lists, per raw file, the boxes where the browser drew its pointer on a flat background: each is painted with
the median colour of the pixels around it.

The entries below are round placeholders for the worked example. Measure your own: open the raw image, read the
pixel corners of the block the caption talks about, and crop to that block only.

Run: WORK=/path/to/workdir python3 crop.py [name.png ...]
"""
import os
import sys

from PIL import Image, ImageFilter

WORK = os.environ.get('WORK', os.path.join(os.getcwd(), 'ind'))
RAW = os.path.join(WORK, 'raw')
OUT = os.path.join(WORK, 'img')

MAP = {
    # client site today (one capture per existing page you audit)
    'client_today.png': ('client-industry-page.png', (0, 0, 1400, 600), []),
    # benchmark proof, one per New or Rework block (the worked example's figure set)
    'aws_segments.png': ('bench-aws-industry-segments.png', (150, 60, 1350, 460), []),
    'accenture_lines.png': ('bench-accenture-overview-list.png', (200, 80, 1300, 600), []),
    'ibm_priorities.png': ('bench-ibm-industry-priorities.png', (200, 100, 1300, 640), []),
    'adobe_sourced.png': ('bench-adobe-industry-figures.png', (200, 150, 1350, 520), []),
    'microsoft_story.png': ('bench-microsoft-industry-story.png', (150, 80, 1350, 620), []),
    'mckinsey_dated.png': ('bench-mckinsey-industry-cards.png', (200, 100, 1300, 520), []),
    'pwc_contacts.png': ('bench-pwc-industry-leaders.png', (200, 100, 1350, 460),
                         [(300, 380, 700, 430), (800, 380, 1200, 430)]),
}

STITCH = {
    # a block split across two scroll positions: bottom of the first, top of the second
    'cognizant_jump.png': [('bench-cognizant-industry-top-1.png', (150, 300, 1350, 660)),
                           ('bench-cognizant-industry-top-2.png', (150, 60, 1350, 260))],
}

POINTER = {
    # 'bench-aws-industry-segments.png': [(780, 330, 802, 361)],
}


def _fill(im, box):
    x0, y0, x1, y1 = box
    ring = [im.getpixel((x, y0 - 2)) for x in range(x0, x1)] + [im.getpixel((x, y1 + 1)) for x in range(x0, x1)]
    ring += [im.getpixel((x0 - 2, y)) for y in range(y0, y1)] + [im.getpixel((x1 + 1, y)) for y in range(y0, y1)]
    med = tuple(sorted(c[i] for c in ring)[len(ring) // 2] for i in range(3))
    im.paste(med, box)


def _load(name):
    path = os.path.join(RAW, name)
    if not os.path.exists(path):
        return None
    im = Image.open(path).convert('RGB')
    for b in POINTER.get(name, []):
        _fill(im, b)
    return im


def run(only=None):
    os.makedirs(OUT, exist_ok=True)
    done = 0
    for out, (src, box, blur) in MAP.items():
        if only and out not in only:
            continue
        im = _load(src)
        if im is None:
            print('skip (no raw file):', src)
            continue
        for b in blur:
            im.paste(im.crop(b).filter(ImageFilter.GaussianBlur(9)), b[:2])
        im.crop(box).save(os.path.join(OUT, out), optimize=True)
        done += 1
    for out, parts in STITCH.items():
        if only and out not in only:
            continue
        ims = [_load(src) for src, _ in parts]
        if any(i is None for i in ims):
            print('skip (missing raw file):', out)
            continue
        pieces = [i.crop(box) for i, (_, box) in zip(ims, parts)]
        w = max(p.width for p in pieces)
        canvas = Image.new('RGB', (w, sum(p.height for p in pieces)), 'white')
        y = 0
        for p in pieces:
            canvas.paste(p, (0, y))
            y += p.height
        canvas.save(os.path.join(OUT, out), optimize=True)
        done += 1
    print('cropped', done)


if __name__ == '__main__':
    run(set(sys.argv[1:]) or None)
