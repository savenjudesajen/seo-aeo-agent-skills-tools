# -*- coding: utf-8 -*-
"""Crop map tool for browser captures: crop, paint out the pointer, blur personal details, stitch two scroll
positions, and re-crop images cut earlier. Use it when a figure needs more than the plain box crop in lean_doc.py.

  python3 crop_map.py map.json [--only name1,name2]

map.json (paths relative to the map file):
{
  "raw_dir": "raw", "out_dir": "img",
  "crops":   {"<name>.png": {"raw": "<capture>.png", "box": [x0, y0, x1, y1],
                              "fill": [[x0, y0, x1, y1]], "blur": [[x0, y0, x1, y1]]}},
  "stitch":  {"<name>.png": [["<capture>.png", [x0, y0, x1, y1]], ["<capture2>.png", [x0, y0, x1, y1]]]},
  "recrop":  {"<name>.png": ["<earlier image path>", [x0, y0, x1, y1]]}
}
Boxes are (left, top, right, bottom) in raw pixels.
- fill: the pointer the browser draws in a capture, covered with the typical colour found just outside the box. Use it
  only on a flat background: on text it cuts letters out of the copy. Two short boxes work better than one tall box
  when the pointer sits on a colour edge.
- blur: personal contact details (names, emails, phone numbers) in a capture; blurred before cropping.
- stitch: two crops of the same page at two scroll positions, stacked top to bottom. Put the seam at a row or block
  boundary so no line is cut.
Needs Pillow.
"""
import json
import os
import sys

from PIL import Image, ImageFilter


def fill(im, box):
    x0, y0, x1, y1 = box
    ring = [im.getpixel((x, y0 - 2)) for x in range(x0, x1)] + [im.getpixel((x, y1 + 1)) for x in range(x0, x1)]
    ring += [im.getpixel((x0 - 2, y)) for y in range(y0, y1)] + [im.getpixel((x1 + 1, y)) for y in range(y0, y1)]
    med = tuple(sorted(c[i] for c in ring)[len(ring) // 2] for i in range(3))
    im.paste(med, box)


def load(path, fills=(), blurs=()):
    im = Image.open(path).convert('RGB')
    for b in fills:
        fill(im, tuple(b))
    for b in blurs:
        b = tuple(b)
        im.paste(im.crop(b).filter(ImageFilter.GaussianBlur(9)), b[:2])
    return im


def check_box(name, im, box):
    if box[2] > im.size[0] or box[3] > im.size[1] or box[0] < 0 or box[1] < 0:
        print('WARNING %s: box %s is outside %s' % (name, list(box), im.size))


def run(map_path, only=None):
    base = os.path.dirname(os.path.abspath(map_path))
    m = json.load(open(map_path, encoding='utf-8'))
    raw = os.path.join(base, m.get('raw_dir', 'raw'))
    out = os.path.join(base, m.get('out_dir', 'img'))
    os.makedirs(out, exist_ok=True)
    n = 0
    for name, c in m.get('crops', {}).items():
        if only and name not in only:
            continue
        im = load(os.path.join(raw, c['raw']), c.get('fill', []), c.get('blur', []))
        check_box(name, im, c['box'])
        im.crop(tuple(c['box'])).save(os.path.join(out, name))
        n += 1
    for name, parts in m.get('stitch', {}).items():
        if only and name not in only:
            continue
        ims = []
        for src, box in parts:
            im = load(os.path.join(raw, src))
            check_box(name, im, box)
            ims.append(im.crop(tuple(box)))
        canvas = Image.new('RGB', (max(i.width for i in ims), sum(i.height for i in ims)), 'white')
        y = 0
        for i in ims:
            canvas.paste(i, (0, y))
            y += i.height
        canvas.save(os.path.join(out, name))
        n += 1
    for name, (src, box) in m.get('recrop', {}).items():
        if only and name not in only:
            continue
        im = Image.open(os.path.join(base, src)).convert('RGB')
        check_box(name, im, box)
        im.crop(tuple(box)).save(os.path.join(out, name))
        n += 1
    print('cropped', n, 'into', out)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    only = None
    if '--only' in sys.argv:
        only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
    run(sys.argv[1], only)
