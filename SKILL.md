---
name: vectorizing-handdrawn-logos
description: Use when turning a hand-drawn, sketched, or scanned logo into clean reproducible code — fitting smooth cubic Bézier curves to the real outline to produce an editable SVG, color/layout variants, an interactive side-by-side/difference review gallery, PNG/ICO/favicon exports, and optional AI showcase renders. For brand logos, monkey/mascot marks, wordmarks, avatars, or any artwork that should become a parametric, infinitely scalable, version-controlled asset instead of a flat image. This reconstructs an existing drawing; it does not generate brand-new logo designs from scratch.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Vectorizing hand-drawn logos

## Overview

A hand-drawn logo is charming but **unmeasurable**: it lives as a flat image, or as
an SVG of hundreds of hand-placed polyline points — smooth to the eye, but rough,
impossible to edit, and not truly scalable. This skill turns each contour into a
small set of **smooth cubic Bézier curves** — genuine parametric polynomials

```
B(t) = (1-t)³P₀ + 3(1-t)²t·C₁ + 3(1-t)t²·C₂ + t³P₃,   t ∈ [0,1]
```

The curve is fitted **along the original outline** (not replaced by idealized
circles/rectangles), so the hand-drawn fullness and character — even an off-centre
curl or a wobble you want to keep — survive. The output is fully mathematical:
reproducible, infinitely scalable, parametrically tweakable, and diff-able in git.
From one definition you fan out color/layout variants and rasterize to PNG/ICO.

**Core insight:** resample the outline to even spacing → lightly smooth out hand
jitter → fit a *closed Catmull-Rom spline* → emit it as exact cubic Béziers. The fit
*interpolates every sample point* and is everywhere C¹ (tangent-continuous), which is
the mathematical source of the smoothness.

## When to use

- "Turn my hand-drawn / sketched logo into an SVG / into code."
- "Make my logo reproducible, scalable, editable; generate favicon / app-icon sizes."
- "Recreate this mark precisely as math / parametric curves; give me color variants."
- Any mascot, wordmark, monogram, or brand mark that should become a versioned asset.

**Not for:** generating a brand-new logo design from scratch (this *reconstructs* an
existing drawing); photographic images; logos that are already clean vector files and
only need recoloring (just edit the SVG directly).

## The toolkit in this skill

- `scripts/vectorize.py` — the **generic engine** (stdlib only). Importable library of
  the fit pipeline + SVG emission. You do **not** edit this per logo.
- `scripts/build_gallery.py` — generic, stdlib-only **review-gallery generator**: builds a
  self-contained `gallery.html` (original vs reconstruction comparison + variant matrix).
- `scripts/rasterize.js` — generic SVG → PNG/ICO/favicon exporter (sharp + png-to-ico).
- `scripts/generate_showcase.py` — **optional** AI showcase renders (Gemini / Nano Banana).
  The only part that needs Python deps + an API key; everything else is dependency-free.
- `assets/gallery_template.html` — the gallery template `build_gallery.py` fills.
- `examples/chan-monkey/build.py` — a complete **worked example**; the template to copy.
- `references/` — the math, tuning, layer-mapping, bitmap input, quality checklist, showcase styles.

## Workflow

Follow these steps. Keep the user in the loop at the **visual comparison** step (4) —
that is where the craft is.

### 1. Get a vector polyline SVG of the drawing

The engine needs an SVG whose paths use absolute `M/L/H/V/C/Z`.
- Already a vector/polyline SVG (e.g. exported from a drawing app)? Proceed.
- A **bitmap** (scan/photo/PNG)? Trace it to SVG first — see
  `references/bitmap-input.md` (potrace / autotrace, then flatten to absolute paths).

### 2. Inspect the SVG and map its contours to roles

Read the SVG's `<path d="…">` data. Each `M…Z` is one closed contour. Identify what
each one is: outer **silhouette**, interior **holes** (a face, a counter in a letter),
**features** painted on top, **wordmark** glyphs, and any contour that is really a
**circle** (eyes, dots). See `references/layer-structure.md` for how holes, the
`even-odd` "knockout" trick, and circles work.

### 3. Scaffold a logo project from the template

Create a new repo/folder for the logo and copy in the two scripts. Write a
`build.py` modeled on `examples/chan-monkey/build.py` that declares, for *this* logo:
- the contour→role mapping (step 2),
- per-contour `TUNING` = `(resample_step_px, smoothing_passes)`,
- how roles compose into `even-odd` paths / circles (the render function),
- the `VARIANTS` matrix (ink color × background × which layers are included).

Reuse the engine's primitives — `tokenize_path`, `load_svg_paths`, `fit_contour`,
`fit_circle`, `path_el`, `circle_el`, `render_svg`, `write`. Don't reimplement maths.

### 4. Build, compare visually, and tune

Run `python build.py` to emit the SVG(s), then `python scripts/build_gallery.py` (point
its CONFIG block at this logo's `build.py`) to write a self-contained `gallery.html`.
**Open it and compare to the original**: the gallery's **Side-by-side / Overlay /
Difference** views make mismatches obvious — in *Difference* mode aligned ink cancels to
black and any deviation glows. Its per-contour tuning table maps each visible wobble to
the knob to turn. Adjust each contour's `(step, passes)` and re-run `build.py` +
`build_gallery.py`:
- too rough / jittery → raise `passes` or `step`;
- lost detail / too round → lower `step` and/or `passes`.

See `references/tuning-guide.md`. Iterate until faithful. This is the one step that
benefits from the user's eye — show them the gallery.

### 5. Fan out the variant matrix

Extend `VARIANTS` for the color schemes and layouts the brand needs (e.g. black/white
ink × white/black/transparent background × full-lockup/mark-only). One math
definition, many ready files. Optionally add a single **theme-adaptive** row with
`ink="currentColor"` + `background=None` — an inline-SVG whose color follows the host's
CSS (great with `prefers-color-scheme`). It's additive (collapses only the ink axis,
inline-only), not a replacement for the matrix — see `references/layer-structure.md`.

### 6. Rasterize to PNG / ICO / favicon

Point the CONFIG block in `scripts/rasterize.js` at the logo's SVGs, then
`npm install` (first time) and `npm run rasterize`. Produces square transparent PNGs,
wide PNGs, a multi-size `favicon.ico`, an Apple touch icon, and web-manifest icons.

### 6.5. Generate showcase images (optional — needs network + an API key)

For presentation-ready brand renders, composite the mark onto premium backgrounds with
`scripts/generate_showcase.py` (Gemini / Nano Banana). This is the **only** step with
external dependencies: `cp .env.example .env` and add `GEMINI_API_KEY`, then
`pip install -r requirements.txt`. Feed a **transparent** raster variant from step 6
(matching the background's polarity):

```bash
python scripts/generate_showcase.py "Brand Name" out/raster/monkey-black-512.png \
    --all-styles --output-dir assets/showcase
```

The prompt forces the model to reproduce the mark **faithfully** (recolor + composite
only — never redraw). Pick styles from `references/showcase-styles.md`. Skip this step
entirely if you don't want the dependency — the rest of the skill is unaffected.

### 7. Run the quality checklist, then lay out a clean repo

Before delivering, walk `references/quality-checklist.md` — the fidelity gate (curve
sanity, holes, circles, variant consistency, faithful rasters/showcase). Then organize
as `assets/` (the SVG + raster + showcase outputs), `src/` (build.py + the scripts),
`archive/` (the original drawing), `docs/` (a short math write-up — model it on
`references/method.md`), the `gallery.html`, and a `README.md`. Everything regenerates
from `build.py` (+ `build_gallery.py` / `rasterize.js`), so the repo stays fully
reproducible.

## References (read when you reach that step)

- `references/method.md` — the full mathematical method and why it stays smooth & full.
- `references/layer-structure.md` — contour roles, holes, the `even-odd` knockout, circles, `currentColor`.
- `references/tuning-guide.md` — choosing `(resample_step, smoothing_passes)`; fidelity vs smoothness.
- `references/bitmap-input.md` — turning a scan/photo into a polyline SVG first.
- `references/quality-checklist.md` — the fidelity gate to run before delivery (step 7).
- `references/showcase-styles.md` — the 12 premium backgrounds for the optional showcase (step 6.5).

## Common mistakes

- **Replacing the outline with primitives.** Don't snap the silhouette to a perfect
  circle — fit *along* the drawing; that's what preserves the character.
- **Relative/arc path commands.** The parser expects absolute `M/L/H/V/C/Z`. Flatten
  the SVG first if it has lowercase commands or `A` arcs.
- **Forgetting `even-odd`.** Inner contours only become see-through holes when their
  group is one path with `fill-rule="evenodd"`.
- **Tuning blind.** Always compare to the original visually (the gallery) before locking parameters.
- **Editing the engine per logo.** Per-logo specifics belong in `build.py`, never in
  `scripts/vectorize.py`.
- **Letting the showcase model redraw the logo.** The showcase step must reproduce the
  vectorized mark faithfully (recolor + composite only); if a render alters it, regenerate.
- **Treating `currentColor` as a replacement for the variant matrix.** It only collapses the
  ink axis and works inline-only — keep the explicit black/white/transparent files.
