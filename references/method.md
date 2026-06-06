# The method: fitting smooth cubic Béziers to a hand-drawn outline

This is the mathematical core the skill applies. It is logo-agnostic; the worked
example (`examples/chan-monkey/`) is one instantiation.

## 1. The core object — the cubic Bézier curve

Each segment is defined by four control points $P_0, C_1, C_2, P_3$ and is a
parametric cubic polynomial:

$$\mathbf{B}(t)=(1-t)^3 P_0 + 3(1-t)^2 t\,C_1 + 3(1-t)t^2 C_2 + t^3 P_3,\qquad t\in[0,1].$$

A whole logo is a set of **piecewise cubic Bézier curves** (each closed contour a
chain), plus optionally a few **exact circles** for parts that are truly circular.
Every control point lands in the `<path d="…C…">` data of the generated SVG.

## 2. Coordinate system

SVG `viewBox="0 0 W H"`, origin top-left, $y$ pointing down — keep it identical to
the source so the result is a drop-in replacement. (For a centered, $y$-up Cartesian
frame for analysis, use $X = x - W/2$, $Y = H_0 - y$.)

## 3. From the original polyline to Bézier curves

For each closed contour, in order (implemented in `scripts/vectorize.py`):

1. **Parse** the path into a polyline — `tokenize_path` (handles `M/L/H/V/C/Z`,
   sampling any pre-existing `C` into points).
2. **De-duplicate** near-coincident points — `dedupe` (removes sampling noise).
3. **Resample at uniform arc length**, step $h$ — `resample_closed`. Even point
   spacing is what makes the spline fit behave.
4. **Periodic smoothing**, $k$ passes — `smooth_closed`:
   $$P_i \leftarrow \tfrac14 P_{i-1} + \tfrac12 P_i + \tfrac14 P_{i+1}.$$
   Removes hand jitter while keeping the shape full.
5. **Closed Catmull-Rom spline → cubic Bézier** — `catmull_rom_closed`. For
   consecutive points $P_{i-1}, P_i, P_{i+1}, P_{i+2}$, the segment from $P_i$ to
   $P_{i+1}$ uses control points
   $$C_1 = P_i + \frac{P_{i+1}-P_{i-1}}{6},\qquad C_2 = P_{i+1} - \frac{P_{i+2}-P_i}{6}.$$

This guarantees the curve **passes through every sample point** and is everywhere
$C^1$ (tangent-continuous) — the mathematical source of the smoothness. A larger step
$h$ or more smoothing passes $k$ → smoother and fewer segments; smaller → closer to
the original. See `tuning-guide.md`.

Contours that are genuinely circular use `fit_circle` instead (bbox centre + mean
radius) and are emitted as exact `<circle>` elements.

## 4. Why this stays smooth *and* full

Rather than **approximating** the shape with a few idealized primitives (which throws
away the hand-drawn fullness and charm), this approach **fits smooth curves along the
real outline**. Resample → lightly smooth → interpolating spline. Because the spline
passes through the sampled outline points and only smooths *between* them, it hugs the
original shape while staying naturally smooth — you keep the character, you lose the
jitter.

## 5. Reproduce and tweak

Each logo's `build.py` reads the archived original and writes every variant; rerun to
regenerate — fully reproducible, no third-party Python deps. Adjust the
`(resample_step, smoothing_passes)` per contour in its `TUNING` dict to trade
smoothness against fidelity; the exact control points all land in the output SVG,
where each segment is the parametric cubic polynomial from §1.
