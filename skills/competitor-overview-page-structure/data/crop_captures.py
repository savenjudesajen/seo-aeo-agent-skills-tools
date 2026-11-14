# -*- coding: utf-8 -*-
"""Crop browser captures into document figures from one crop map. Needs Pillow.

The crop map is a JSON file:
{
  "raw_dir": "raw",                      # folder of full captures (viewport screenshots at scale 1)
  "out_dir": "img",                      # where the figures go
  "pointer": [600, 300, 640, 340],       # optional default box where the browser drew the pointer
  "crops": {
    "hub_cards.png":  {"src": "capture-01.png", "box": [100, 100, 1200, 500],
                       "fill": "pointer", "blur": []},
    "hub_footer.png": {"src": "capture-02.png", "box": [700, 200, 1300, 500]}
  },
  "stitch": {
    "hub_table.png": [{"src": "capture-03.png", "box": [400, 100, 1300, 600]},
                      {"src": "capture-04.png", "box": [400, 100, 1300, 300]}]
  }
}
Boxes are (left, top, right, bottom) in raw pixels.
fill: boxes (or "pointer") painted over in one flat colour, the median of the pixels just outside the box. Only on a flat
  background: on text a painted box cuts letters out of the copy the caption quotes, so re-capture instead.
fill_rows: like fill, but each row takes the colour just left of the box (for gradients that run left to right).
blur: boxes to blur (personal contact details, account names, anything the caption does not need).
stitch: crops of the same page at two scroll positions stacked top to bottom; put each seam at a row or block
  boundary so the joined figure never splits a line of text.
Run: python3 crop_captures.py cropmap.json [name ...]"""
import json
import os
import sys

from PIL import Image, ImageFilter


def _boxes(spec, key, pointer):
    out = []
    for b in spec.get(key, []) if isinstance(spec.get(key), list) else ([spec[key]] if key in spec else []):
        out.append(tuple(pointer) if b == 'pointer' else tuple(b))
    return out


def fill_ring(im, box):
    x0, y0, x1, y1 = box
    ring = [im.getpixel((x, y0 - 2)) for x in range(x0, x1)] + [im.getpixel((x, y1 + 1)) for x in range(x0, x1)]
    ring += [im.getpixel((x0 - 2, y)) for y in range(y0, y1)] + [im.getpixel((x1 + 1, y)) for y in range(y0, y1)]
    med = tuple(sorted(c[i] for c in ring)[len(ring) // 2] for i in range(3))
    im.paste(med, box)


def fill_rows(im, box, tol=9):
    x0, y0, x1, y1 = box
    px = im.load()
    for y in range(y0, y1):
        ref = px[x0 - 2, y]
        for x in range(x0, x1):
            if sum(abs(a - b) for a, b in zip(px[x, y], ref)) > tol:
                px[x, y] = ref


def load(raw_dir, spec, pointer):
    im = Image.open(os.path.join(raw_dir, spec['src'])).convert('RGB')
    for b in _boxes(spec, 'fill', pointer):
        fill_ring(im, b)
    for b in _boxes(spec, 'fill_rows', pointer):
        fill_rows(im, b)
    for b in _boxes(spec, 'blur', pointer):
        region = im.crop(b).filter(ImageFilter.GaussianBlur(9))
        im.paste(region, b[:2])
    return im


def run(cfg, names=None):
    raw_dir, out_dir = cfg['raw_dir'], cfg['out_dir']
    pointer = cfg.get('pointer', [0, 0, 0, 0])
    os.makedirs(out_dir, exist_ok=True)
    done = 0
    for name, spec in cfg.get('crops', {}).items():
        if names and name not in names:
            continue
        load(raw_dir, spec, pointer).crop(tuple(spec['box'])).save(os.path.join(out_dir, name))
        done += 1
    for name, parts in cfg.get('stitch', {}).items():
        if names and name not in names:
            continue
        ims = [load(raw_dir, p, pointer).crop(tuple(p['box'])) for p in parts]
        out = Image.new('RGB', (max(i.width for i in ims), sum(i.height for i in ims)), 'white')
        y = 0
        for i in ims:
            out.paste(i, (0, y))
            y += i.height
        out.save(os.path.join(out_dir, name))
        done += 1
    return done


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding='utf-8') as f:
        conf = json.load(f)
    print('cropped', run(conf, sys.argv[2:] or None))
