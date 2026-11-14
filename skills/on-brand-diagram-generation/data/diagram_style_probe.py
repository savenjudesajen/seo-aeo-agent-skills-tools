#!/usr/bin/env python3
"""
diagram_style_probe.py - "measured, not claimed" gate for on-brand-diagram-generation.

Checks a produced SVG against a brand style-spec so you don't ship a diagram that
drifted off the brand's real visual language. Reads the SVG SOURCE (exact authored
colours, not rendered pixels), so colour checks are precise.

Python standard library only; makes no network calls.

Checks:
  1. palette_adherence  - every fill / stroke / stop-color (attributes, inline style
                          and <style> blocks) is within tolerance of an approved
                          colour (the palette you SAMPLED from the brand's own
                          published assets).
  2. aspect_ratio_match - the viewBox (or width/height) ratio matches the brand's
                          existing image ratio (e.g. 16:9), so it drops into their
                          layout without letterboxing.
  3. pure_vector        - no embedded raster (<image> / data:image href). Vector stays
                          crisp at 2x and keeps the file small.
  4. accessibility      - <title> and <desc> present (screen readers, alt-text source,
                          and it forces you to say what the diagram shows).
  5. required_marks     - OPTIONAL: every spec.required_ids entry must appear inside
                          some id="..." (e.g. the brand's reusable logo <g id="...">).

Exit code: 0 = PASS, 1 = FAIL, 2 = bad input (unreadable SVG or spec).
Usage: python3 diagram_style_probe.py --svg diagram.svg --spec style_spec.json [--json]

style_spec.json shape (everything brand-specific lives here, nothing hard-coded):
  {
    "client": "ExampleBrand (example.com)",
    "approved_palette": ["#FFFFFF", "#333333", "#777777", "#DDDDDD", "#0066CC"],
    "palette_tolerance": 6,          # optional, RGB Euclidean distance; default 6
    "target_ratio": "16:9",          # "16:9" | number | [w, h]
    "ratio_tolerance": 0.02,         # optional; default 0.02
    "require_title_desc": true,      # optional; default true
    "required_ids": ["brand-logo"],  # optional; each must be a substring of some id=
    "allow_extra_accent_colors": []  # optional: hexes exempt from the palette check
                                     # (e.g. a partner mark drawn true to its brand)
  }
"""
import argparse
import json
import math
import re
import sys

NAMED = {"white": "#ffffff", "black": "#000000",
         "red": "#ff0000", "green": "#008000", "blue": "#0000ff",
         "gray": "#808080", "grey": "#808080"}
SKIP = {"none", "transparent", "currentcolor", "inherit", ""}
COLOR_PROPS = ("fill", "stroke", "stop-color")


def norm_hex(c):
    """Return #rrggbb lowercase, or None if not a resolvable solid colour."""
    if c is None:
        return None
    c = c.strip().lower().replace("!important", "").strip()
    if c in SKIP:
        return None
    if c in NAMED:
        c = NAMED[c]
    m = re.fullmatch(r"#([0-9a-f]{3})", c)
    if m:
        r, g, b = m.group(1)
        return f"#{r}{r}{g}{g}{b}{b}"
    m = re.fullmatch(r"#([0-9a-f]{6})(?:[0-9a-f]{2})?", c)
    if m:
        return "#" + m.group(1)
    m = re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+).*", c)
    if m:
        return "#{:02x}{:02x}{:02x}".format(*(min(255, int(m.group(i))) for i in (1, 2, 3)))
    return None  # gradients (url(#..)), unknown keywords: not a solid colour to check


def to_rgb(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(to_rgb(a), to_rgb(b))))


def _add(found, raw):
    h = norm_hex(raw)
    if h:
        found[h] = found.get(h, 0) + 1


def _scan_declarations(text, found):
    """Find prop: value declarations (inline style or CSS) for the colour props."""
    for prop in COLOR_PROPS:
        # (?<![\w-]) so 'fill' doesn't match inside 'stop-fill' style names
        for m in re.finditer(r"(?<![\w-])" + prop + r"\s*:\s*([^;}\"']+)", text, flags=re.I):
            _add(found, m.group(1))


def extract_colors(svg):
    """All authored solid colours from attributes, inline style and <style> blocks, with counts."""
    found = {}
    for attr in COLOR_PROPS:
        pattern = r"(?<![\w-])" + attr + r"\s*=\s*(?:\"([^\"]*)\"|'([^']*)')"
        for m in re.finditer(pattern, svg, flags=re.I):
            _add(found, m.group(1) if m.group(1) is not None else m.group(2))
    for m in re.finditer(r"\bstyle\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", svg, flags=re.I):
        _scan_declarations(m.group(1) if m.group(1) is not None else m.group(2), found)
    for m in re.finditer(r"<style\b[^>]*>(.*?)</style>", svg, flags=re.I | re.S):
        _scan_declarations(m.group(1), found)
    return found


def parse_ratio(spec_val):
    if isinstance(spec_val, (int, float)):
        return float(spec_val)
    if isinstance(spec_val, (list, tuple)) and len(spec_val) == 2:
        return float(spec_val[0]) / float(spec_val[1])
    if isinstance(spec_val, str) and ":" in spec_val:
        w, h = spec_val.split(":")
        return float(w) / float(h)
    if isinstance(spec_val, str):
        return float(spec_val)
    raise ValueError(f"bad target_ratio: {spec_val!r}")


def svg_ratio(svg):
    m = re.search(r"viewBox\s*=\s*[\"']([-\d.\s,]+)[\"']", svg, flags=re.I)
    if m:
        parts = re.split(r"[\s,]+", m.group(1).strip())
        if len(parts) == 4 and float(parts[3]) != 0:
            return float(parts[2]) / float(parts[3])
    root = re.search(r"<svg\b[^>]*>", svg, flags=re.I)
    tag = root.group(0) if root else svg
    w = re.search(r"\bwidth\s*=\s*[\"']([\d.]+)", tag, flags=re.I)
    h = re.search(r"\bheight\s*=\s*[\"']([\d.]+)", tag, flags=re.I)
    if w and h and float(h.group(1)) != 0:
        return float(w.group(1)) / float(h.group(1))
    return None


def verify(svg, spec):
    approved = [norm_hex(c) or str(c).lower() for c in spec.get("approved_palette", [])]
    approved = [c for c in approved if re.fullmatch(r"#[0-9a-f]{6}", c)]
    exempt = {norm_hex(c) for c in spec.get("allow_extra_accent_colors", []) if norm_hex(c)}
    tol = spec.get("palette_tolerance", 6)
    rtol = spec.get("ratio_tolerance", 0.02)
    rep = {"client": spec.get("client"), "checks": {}}
    fails = []

    if not approved:
        rep["checks"]["palette_adherence"] = {"status": "FAIL", "reason": "spec has no approved_palette"}
        fails.append("palette_adherence")
    else:
        used = extract_colors(svg)
        off = []
        for c, n in used.items():
            if c in exempt:
                continue
            nearest = min(approved, key=lambda a: dist(c, a))
            d = dist(c, nearest)
            if d > tol:
                off.append({"color": c, "count": n, "nearest_approved": nearest, "distance": round(d, 1)})
        off.sort(key=lambda x: -x["distance"])
        ok = not off
        rep["checks"]["palette_adherence"] = {
            "status": "PASS" if ok else "FAIL",
            "distinct_colors_used": len(used), "approved": len(approved),
            "tolerance": tol, "off_palette": off}
        if not ok:
            fails.append("palette_adherence")

    tr = None
    try:
        tr = parse_ratio(spec["target_ratio"])
    except Exception as e:  # missing key or unparsable value
        rep["checks"]["aspect_ratio_match"] = {"status": "FAIL", "reason": f"bad target_ratio ({e})"}
        fails.append("aspect_ratio_match")
    if tr is not None:
        sr = svg_ratio(svg)
        ok = sr is not None and abs(sr - tr) <= rtol
        rep["checks"]["aspect_ratio_match"] = {
            "status": "PASS" if ok else "FAIL",
            "svg_ratio": round(sr, 4) if sr else None,
            "target_ratio": round(tr, 4), "tolerance": rtol}
        if not ok:
            fails.append("aspect_ratio_match")

    raster = re.findall(r"<image\b", svg, flags=re.I)
    datauri = re.findall(r"href\s*=\s*[\"']\s*data:image", svg, flags=re.I)
    ok = not raster and not datauri
    rep["checks"]["pure_vector"] = {"status": "PASS" if ok else "FAIL",
                                    "image_tags": len(raster), "data_uri_images": len(datauri)}
    if not ok:
        fails.append("pure_vector")

    if spec.get("require_title_desc", True):
        has_t = bool(re.search(r"<title\b[^>]*>\s*\S", svg, flags=re.I))
        has_d = bool(re.search(r"<desc\b[^>]*>\s*\S", svg, flags=re.I))
        ok = has_t and has_d
        rep["checks"]["accessibility"] = {"status": "PASS" if ok else "FAIL",
                                          "has_title": has_t, "has_desc": has_d}
        if not ok:
            fails.append("accessibility")

    req = spec.get("required_ids", [])
    if req:
        ids = set(re.findall(r"\bid\s*=\s*[\"']([^\"']+)[\"']", svg))
        missing = [r for r in req if not any(r in i for i in ids)]
        ok = not missing
        rep["checks"]["required_marks"] = {"status": "PASS" if ok else "FAIL", "missing": missing}
        if not ok:
            fails.append("required_marks")

    rep["overall_status"] = "PASS" if not fails else "FAIL"
    rep["failed_checks"] = fails
    return rep


def main():
    ap = argparse.ArgumentParser(description="Check an SVG diagram against a brand style-spec.")
    ap.add_argument("--svg", required=True, help="path to the authored SVG")
    ap.add_argument("--spec", required=True, help="path to style_spec.json")
    ap.add_argument("--json", action="store_true", help="print the full report as JSON")
    a = ap.parse_args()
    try:
        with open(a.svg, encoding="utf-8") as f:
            svg = f.read()
        with open(a.spec, encoding="utf-8") as f:
            spec = json.load(f)
    except (OSError, ValueError) as e:
        print(f"diagram_style_probe: cannot read input: {e}", file=sys.stderr)
        sys.exit(2)
    rep = verify(svg, spec)
    if a.json:
        print(json.dumps(rep, indent=2))
    else:
        print(f"\n=== diagram_style_probe: {rep.get('client')} ===")
        for n, c in rep["checks"].items():
            print(f"  [{c['status']}] {n}: " + json.dumps({k: v for k, v in c.items() if k != 'status'}))
        print(f"\n  OVERALL: {rep['overall_status']}" +
              (f"  (failed: {', '.join(rep['failed_checks'])})" if rep["failed_checks"] else ""))
    sys.exit(0 if rep["overall_status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
