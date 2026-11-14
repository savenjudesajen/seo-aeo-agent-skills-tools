#!/usr/bin/env python3
"""Visual gate for the mockup: region-aware compare of the live screenshot against the mock render.

Finds the hero band by its background colour (sampled in the left margin, away from photos and
headline glyphs), splits each image into a HEADER region and a HERO region, scales each pair to the
same width and reports a per-region score, plus side-by-side and difference images in out/.
The hero region is also scored on its text column alone, because photos inflate pixel difference
without meaning the layout is off.

Needs Pillow and numpy (pip install pillow numpy).
usage: python3 visual_parity.py <live.jpg> <mock.png> --band R,G,B [--width 1280] [--text-col 0.5]
  --band      the hero band's background colour (read it with probe.js: band.bg)
  --width     the site's container width in CSS px; both images are compared at this width
  --text-col  fraction of the width, from the left, that holds the hero text column
"""
import argparse
import os

import numpy as np
from PIL import Image

PASS_MAD = 12      # mean absolute difference must be below this
PASS_CLOSE = 75    # and this share (%) of pixels must differ by < 26 on every channel


def load(p):
    return np.asarray(Image.open(p).convert("RGB"))


def to_width(arr, w):
    im = Image.fromarray(arr)
    h = round(im.height * w / im.width)
    return np.asarray(im.resize((w, h), Image.LANCZOS))


def band_rows(arr, band, tol=16, frac=0.7):
    left = arr[:, : max(1, int(arr.shape[1] * 0.10))]
    d = np.abs(left.astype(int) - band).max(2)
    return (d <= tol).mean(1) >= frac


def nonwhite_rows(arr, thr=246, frac=0.02):
    return (arr.min(2) < thr).mean(1) >= frac


def longest_run(mask):
    best, i, n = (0, 0), 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]:
                j += 1
            if j - i > best[1] - best[0]:
                best = (i, j)
            i = j
        else:
            i += 1
    return best if best[1] > best[0] else None


def extent(mask):
    ys = np.where(mask)[0]
    return (int(ys.min()), int(ys.max()) + 1) if len(ys) else None


def split_regions(arr, band):
    hero = longest_run(band_rows(arr, band))
    if hero is None:
        return extent(nonwhite_rows(arr)), None
    above = extent(nonwhite_rows(arr[: hero[0]]))
    header = (max(0, above[0] - 6), above[1] + 2) if above else (0, hero[0])
    return header, hero


def side_by_side(a, b, gap=24):
    h = max(a.shape[0], b.shape[0])
    canvas = np.full((h, a.shape[1] + b.shape[1] + gap, 3), 255, np.uint8)
    canvas[: a.shape[0], : a.shape[1]] = a
    canvas[: b.shape[0], a.shape[1] + gap:] = b
    return canvas


def score(a, b):
    h = min(a.shape[0], b.shape[0])
    a, b = a[:h], b[:h]
    diff = np.abs(a.astype(int) - b.astype(int)).astype(np.uint8)
    return float(diff.mean()), float((diff.max(2) < 26).mean()) * 100, diff


def compare(live, mock, tag, width, text_col=None):
    r, m = to_width(live, width), to_width(mock, width)
    mad, close, diff = score(r, m)
    Image.fromarray(side_by_side(r, m)).save(os.path.join("out", f"{tag}_compare.png"))
    Image.fromarray(np.stack([255 - diff.max(2)] * 3, 2)).save(os.path.join("out", f"{tag}_diff.png"))
    extra = ""
    if text_col:
        cut = int(width * text_col)
        mad, close, _ = score(r[:, :cut], m[:, :cut])
        extra = f" | text column (left {int(text_col * 100)}%) scored"
    print(f"[{tag:6}] live {live.shape[1]}x{live.shape[0]} | mock {mock.shape[1]}x{mock.shape[0]} "
          f"| heights@{width}px live={r.shape[0]} mock={m.shape[0]} (Δ{r.shape[0] - m.shape[0]:+d}) "
          f"| MAD={mad:5.2f} | close={close:5.1f}%{extra}")
    return mad, close


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("live")
    ap.add_argument("mock")
    ap.add_argument("--band", required=True, help="hero band colour as R,G,B")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--text-col", type=float, default=0.5)
    args = ap.parse_args()
    band = np.array([int(x) for x in args.band.split(",")])
    os.makedirs("out", exist_ok=True)

    live, mock = load(args.live), load(args.mock)
    lh, lr = split_regions(live, band)
    mh, mr = split_regions(mock, band)
    print(f"live regions: header={lh} hero={lr}")
    print(f"mock regions: header={mh} hero={mr}")
    results = {}
    if lh and mh:
        results["header"] = compare(live[lh[0]:lh[1]], mock[mh[0]:mh[1]], "header", args.width)
    if lr and mr:
        results["hero"] = compare(live[lr[0]:lr[1]], mock[mr[0]:mr[1]], "hero", args.width, args.text_col)
    if not results:
        print("VISUAL GATE: no comparable regions found; check --band")
        return 1
    print("\nVISUAL GATE summary:")
    ok_all = True
    for k, (mad, close) in results.items():
        ok = mad < PASS_MAD and close > PASS_CLOSE
        ok_all &= ok
        print(f"  {k:6}: MAD={mad:.2f} close={close:.1f}%  -> {'PASS' if ok else 'REVIEW'}")
    print("Look at out/*_compare.png before you accept a PASS.")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
