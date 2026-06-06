#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vectorize.py — a tiny, dependency-free engine for turning a hand-drawn / sketched
logo (delivered as a *polyline* SVG of hundreds of hand-placed points) into a small
set of smooth **cubic Bézier curves**, i.e. genuine parametric polynomial functions

        B(t) = (1-t)^3 P0 + 3(1-t)^2 t C1 + 3(1-t) t^2 C2 + t^3 P3 ,  t in [0,1]

The result is fully mathematical, reproducible, infinitely scalable and
parametrically tweakable — yet it *follows the original outline* (rather than
replacing it with idealized primitives), so the hand-drawn fullness and character
are preserved.

This module is a LIBRARY. It contains no logo-specific data. Each logo gets its own
short `build.py` that imports these primitives and declares its own structure
(which contour is which, which are holes, which are circles, the colour variants).
See `examples/chan-monkey/build.py` for a complete worked example.

Pipeline per closed contour:
    tokenize original  ->  dedupe  ->  uniform arc-length resample
    ->  light periodic smoothing (removes hand jitter, keeps fullness)
    ->  closed Catmull-Rom spline  ->  exact cubic Bézier segments.

Stdlib only (math, os, re). Python 3.
"""

import math
import os
import re


# ===========================================================================
# 1. Parse SVG path data into contours (lists of points)
# ===========================================================================
def tokenize_path(d, c_samples=8):
    """Return a list of contours; each contour is a list of (x, y) points.

    Handles absolute M/L/H/V/C and Z — the commands a hand-drawn polyline export
    typically uses. Any cubic `C` segment is sampled into `c_samples` points so
    pre-existing curved parts keep their shape before re-fitting.

    If your source uses relative commands (lowercase m/l/c/...) or arcs (A),
    normalise it first (e.g. open it in Inkscape and "flatten"/"object to path",
    or run it through svgpathtools) so it only contains absolute M/L/H/V/C/Z.
    """
    tokens = re.findall(r'([MLHVCZ])|(-?\d*\.?\d+(?:e-?\d+)?)', d)
    stream = []
    for cmd, num in tokens:
        stream.append(('c', cmd) if cmd else ('n', float(num)))

    contours, cur = [], []
    i, cx, cy, start = 0, 0.0, 0.0, (0.0, 0.0)
    cmd = None

    def take(k):
        nonlocal i
        vals = [stream[i + j][1] for j in range(k)]
        i += k
        return vals

    while i < len(stream):
        if stream[i][0] == 'c':
            cmd = stream[i][1]; i += 1
            if cmd == 'Z':
                if cur:
                    contours.append(cur); cur = []
                cx, cy = start
                continue
        if cmd == 'M':
            x, y = take(2); cx, cy = x, y; start = (x, y)
            if cur:
                contours.append(cur)
            cur = [(cx, cy)]; cmd = 'L'
        elif cmd == 'L':
            x, y = take(2); cx, cy = x, y; cur.append((cx, cy))
        elif cmd == 'H':
            x = take(1)[0]; cx = x; cur.append((cx, cy))
        elif cmd == 'V':
            y = take(1)[0]; cy = y; cur.append((cx, cy))
        elif cmd == 'C':
            x1, y1, x2, y2, x, y = take(6)
            for s in range(1, c_samples + 1):
                t = s / float(c_samples); mt = 1 - t
                bx = mt**3*cx + 3*mt*mt*t*x1 + 3*mt*t*t*x2 + t**3*x
                by = mt**3*cy + 3*mt*mt*t*y1 + 3*mt*t*t*y2 + t**3*y
                cur.append((bx, by))
            cx, cy = x, y
        else:
            i += 1
    if cur:
        contours.append(cur)
    return contours


def load_svg_paths(svg_path):
    """Read an SVG file and return the raw `d` strings of every <path>, in order.

    A hand-drawn export usually packs several contours into one `d` (separated by
    `M`/`Z`); `tokenize_path` splits those back into individual contours. Use the
    returned list together with `tokenize_path` to pull out exactly the sub-contours
    you need — see the monkey example, which has two <path> elements (head group and
    features+wordmark group)."""
    svg = open(svg_path, encoding="utf-8").read()
    return re.findall(r'<path[^>]*\bd="(.*?)"', svg, re.S)


# ===========================================================================
# 2. Geometry helpers (the proven fit pipeline)
# ===========================================================================
def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def dedupe(pts, eps=0.01):
    """Drop repeated / near-coincident points (sampling noise)."""
    out = [pts[0]]
    for p in pts[1:]:
        if _dist(p, out[-1]) > eps:
            out.append(p)
    if len(out) > 1 and _dist(out[0], out[-1]) < eps:
        out.pop()
    return out


def resample_closed(pts, step):
    """Walk the closed polyline at uniform arc-length spacing ~= `step` px.

    Even point spacing is what makes the subsequent Catmull-Rom fit behave. A
    larger `step` => fewer, smoother segments; a smaller `step` => closer to the
    original, more segments."""
    n = len(pts)
    seg = [_dist(pts[k], pts[(k + 1) % n]) for k in range(n)]
    total = sum(seg)
    if total == 0:
        return pts
    m = max(16, int(round(total / step)))
    d = total / m
    out = []
    s_idx, cur = 0, 0.0
    for k in range(m):
        target = k * d
        while s_idx < n - 1 and cur + seg[s_idx] < target:
            cur += seg[s_idx]; s_idx += 1
        t = (target - cur) / seg[s_idx] if seg[s_idx] > 0 else 0.0
        a, b = pts[s_idx], pts[(s_idx + 1) % n]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def smooth_closed(pts, passes):
    """Periodic 3-tap [0.25, 0.5, 0.25] smoothing — removes hand jitter while
    keeping the shape full. `passes` controls how much."""
    P = pts
    for _ in range(passes):
        n = len(P)
        P = [(0.25*P[(i-1) % n][0] + 0.5*P[i][0] + 0.25*P[(i+1) % n][0],
              0.25*P[(i-1) % n][1] + 0.5*P[i][1] + 0.25*P[(i+1) % n][1])
             for i in range(n)]
    return P


def catmull_rom_closed(P):
    """Closed uniform Catmull-Rom spline -> list of cubic Bézier segments
    (P0, C1, C2, P3) interpolating every point smoothly.

    For consecutive points P_{i-1}, P_i, P_{i+1}, P_{i+2}, the segment from P_i to
    P_{i+1} uses control points
        C1 = P_i     + (P_{i+1} - P_{i-1}) / 6
        C2 = P_{i+1} - (P_{i+2} - P_i)     / 6
    so the curve passes through every sample point and is everywhere C^1."""
    n = len(P)
    segs = []
    for i in range(n):
        p0, p1 = P[(i - 1) % n], P[i]
        p2, p3 = P[(i + 1) % n], P[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        segs.append((p1, c1, c2, p2))
    return segs


def fit_contour(points, step, passes):
    """The full fit for one closed contour. `step`, `passes` are this contour's
    TUNING knobs: smaller step / fewer passes = more faithful; larger / more = rounder."""
    return catmull_rom_closed(
        smooth_closed(resample_closed(dedupe(points), step), passes))


def fit_circle(points):
    """Best simple circle for an already-circular contour: bbox centre and mean
    radius. Use for contours that are truly circles in the original (e.g. eyes),
    so they come out as exact <circle> elements rather than fitted curves."""
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    r = sum(math.hypot(x - cx, y - cy) for x, y in points) / len(points)
    return cx, cy, r


# ===========================================================================
# 3. SVG emission
# ===========================================================================
def _f(v):
    """Compact number formatting: 2 decimals, trailing zeros stripped."""
    return f"{v:.2f}".rstrip("0").rstrip(".")


def subpath_d(segs):
    """One closed contour's Bézier segments -> an SVG `d` sub-path string."""
    p0 = segs[0][0]
    d = f"M{_f(p0[0])} {_f(p0[1])}"
    for _, c1, c2, p3 in segs:
        d += f"C{_f(c1[0])} {_f(c1[1])} {_f(c2[0])} {_f(c2[1])} {_f(p3[0])} {_f(p3[1])}"
    return d + "Z"


def path_el(contours_segs, fill, evenodd=False, note=""):
    """A <path> element from one or more contours. Pass several contours plus
    `evenodd=True` to knock the inner ones out as holes (the see-through trick:
    with no background they are genuinely transparent).

    `fill` is written verbatim, so besides a hex colour it accepts the keyword
    `"currentColor"` — pair that with `background=None` in `render_svg` to emit a
    single theme-adaptive SVG whose ink follows the CSS `color` of its host. See
    `references/layer-structure.md`."""
    d = "".join(subpath_d(s) for s in contours_segs)
    fr = ' fill-rule="evenodd"' if evenodd else ""
    c = f"  <!-- {note} -->\n" if note else ""
    return f'{c}  <path d="{d}" fill="{fill}"{fr}/>'


def circle_el(cx, cy, r, fill, note=""):
    """An exact <circle> element (from `fit_circle`)."""
    c = f"  <!-- {note} -->\n" if note else ""
    return f'{c}  <circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{fill}"/>'


def render_svg(width, height, background, elements):
    """Assemble a full SVG document.

    width, height : the viewBox / pixel size.
    background    : a fill colour string for a full-bleed <rect>, or None for a
                    transparent canvas.
    elements      : an ordered list of element strings (from path_el / circle_el),
                    painted back-to-front.
    """
    out = [f'<svg width="{_f(width)}" height="{_f(height)}" '
           f'viewBox="0 0 {_f(width)} {_f(height)}" '
           f'xmlns="http://www.w3.org/2000/svg">']
    if background is not None:
        out.append(f'  <rect width="{_f(width)}" height="{_f(height)}" fill="{background}"/>')
    out.extend(elements)
    out.append("</svg>")
    return "\n".join(out)


def write(path, text):
    """Write `text` to `path`, creating parent dirs. Returns `path`."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path
