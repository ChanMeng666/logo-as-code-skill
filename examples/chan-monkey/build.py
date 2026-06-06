#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — worked example: the "Chan Monkey" logo.

This is the per-logo CONFIG that drives the generic engine in
`scripts/vectorize.py`. It is the template to copy when vectorizing a new logo:
declare which contour is which, which contours are holes, which are circles, the
per-contour TUNING, and the colour/layout variant matrix — then let the library do
the maths and the SVG emission.

Run:  python build.py        # regenerates every variant into ./out/
Stdlib only.
"""

import math
import os
import sys

# Make the shared engine importable no matter the current working directory.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))
import vectorize as V  # noqa: E402

SRC = os.path.join(HERE, "handdrawn.svg")
OUT = os.path.join(HERE, "out")

W, H = 276, 356          # full-lockup canvas (monkey + CHAN wordmark)
BLACK = "#000000"
WHITE = "#ffffff"

# --- Per-contour tuning: (resample step in px, smoothing passes) ----------
# Smaller step / fewer passes = more faithful; larger / more = rounder.
TUNING = {
    "head":     (5.0, 1),   # head silhouette incl. the off-centre hair curl
    "facemask": (5.0, 1),   # white face (a hole)
    "ear":      (3.5, 1),   # inner ear holes
    "nostril":  (2.5, 1),
    "mouth":    (3.5, 1),
    "letter":   (4.0, 1),   # CHAN glyphs
}


# --- Map the source contours to named roles -------------------------------
# The hand-drawn source has two <path> elements. The first packs the head group;
# the second packs the features + the CHAN wordmark. tokenize_path splits each
# back into its individual closed contours, in drawing order.
def load_contours():
    d1, d2 = V.load_svg_paths(SRC)[:2]
    head, facemask, ear_r, ear_l = V.tokenize_path(d1)
    (eye_l, eye_r, nos_l, nos_r, mouth,
     gC, gH, gA, gA_hole, gN) = V.tokenize_path(d2)

    def F(pts, key):
        return V.fit_contour(pts, *TUNING[key])

    monkey_h = max(p[1] for p in head)          # tight bottom of the chin
    return {
        "head":     F(head, "head"),
        "face":     [F(facemask, "facemask"), F(ear_r, "ear"), F(ear_l, "ear")],
        "eyes":     [V.fit_circle(eye_l), V.fit_circle(eye_r)],
        "features": [F(nos_l, "nostril"), F(nos_r, "nostril"), F(mouth, "mouth")],
        "chan":     [F(gC, "letter"), F(gH, "letter"), F(gA, "letter"),
                     F(gA_hole, "letter"), F(gN, "letter")],
        "monkey_h": monkey_h,
    }


# --- Compose one variant into a full SVG ----------------------------------
# Single-colour knockout design: the head is one even-odd path whose inner
# contours (face + inner ears) are HOLES. With a solid background they show that
# colour; with no background they are genuinely transparent — the face is
# see-through. Eyes / nostrils / mouth / CHAN are `ink` marks painted on top.
def render(C, ink=BLACK, background=WHITE, with_text=True):
    vb_h = H if with_text else int(math.ceil(C["monkey_h"]))
    els = [V.path_el([C["head"]] + C["face"], ink, evenodd=True,
                     note="head silhouette with see-through face/ear holes")]
    for cx, cy, r in C["eyes"]:
        els.append(V.circle_el(cx, cy, r, ink, note="eye"))
    els.append(V.path_el(C["features"], ink, note="nostrils + mouth"))
    if with_text:
        els.append(V.path_el(C["chan"], ink, evenodd=True, note="CHAN wordmark"))
    return V.render_svg(W, vb_h, background, els)


# --- Variant matrix: (relative out path, ink, background, with_text) -------
VARIANTS = [
    # Full lockup (monkey + CHAN)
    ("full/chan-meng-logo-black-on-white.svg",    BLACK, WHITE, True),
    ("full/chan-meng-logo-white-on-black.svg",    WHITE, BLACK, True),
    ("full/chan-meng-logo-black-transparent.svg", BLACK, None,  True),
    ("full/chan-meng-logo-white-transparent.svg", WHITE, None,  True),
    # Monkey only (no wordmark) — for avatars, app icons, favicons
    ("monkey/chan-meng-monkey-black-on-white.svg",    BLACK, WHITE, False),
    ("monkey/chan-meng-monkey-white-on-black.svg",    WHITE, BLACK, False),
    ("monkey/chan-meng-monkey-black-transparent.svg", BLACK, None,  False),
    ("monkey/chan-meng-monkey-white-transparent.svg", WHITE, None,  False),
    # Theme-adaptive: one inline-SVG file whose ink follows the host's CSS `color`
    # (transparent background). Additive — it collapses only the ink axis, so it
    # complements the explicit matrix above, it doesn't replace it. See
    # references/layer-structure.md.
    ("web/chan-meng-logo-currentColor.svg",   "currentColor", None, True),
    ("web/chan-meng-monkey-currentColor.svg", "currentColor", None, False),
]


if __name__ == "__main__":
    C = load_contours()
    for rel, ink, bg, txt in VARIANTS:
        path = os.path.join(OUT, rel)
        V.write(path, render(C, ink=ink, background=bg, with_text=txt))
        print(f"wrote {os.path.relpath(path, HERE)}")
