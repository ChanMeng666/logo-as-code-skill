# Tuning guide: `(resample_step, smoothing_passes)` per contour

Each contour has two knobs, set in the logo's `TUNING` dict and passed to
`fit_contour(points, step, passes)`:

- **`resample_step`** (px) — spacing of the arc-length resample. It sets how many
  Bézier segments you get: roughly `perimeter / step`. Larger step → fewer segments,
  rounder, less faithful. Smaller step → more segments, closer to the original.
- **`smoothing_passes`** (int) — how many times the 3-tap `[¼, ½, ¼]` filter runs
  before fitting. More passes → more hand jitter removed, but also more shrinkage/
  rounding of fine detail.

## The trade-off

```
faithful, rough  <───────────────────────────────>  smooth, simplified
small step                                              large step
few passes                                              many passes
```

You are balancing **fidelity** (hug the drawing, keep its character) against
**smoothness/editability** (fewer, cleaner curves). The sweet spot is per-contour:
big smooth shapes tolerate a larger step; small detailed features need a small one.

## A practical procedure

1. Start everyone at `(step=4.0, passes=1)`.
2. Build, render, and diff against the original (a difference image where matching
   pixels go black makes errors pop).
3. Per contour:
   - **Jagged / wobbly edges** → raise `passes` to 2, or raise `step`.
   - **Lost a notch, tip, or asymmetry you wanted** → lower `step` (e.g. 2.5–3.5) and
     keep `passes=1`.
   - **Too many redundant segments on a simple curve** → raise `step`.
4. Re-build and re-diff. Lock each contour when it looks right.

## Reference values (from the monkey example)

| Contour | step $h$ | passes $k$ | resulting segments |
|---|---|---|---|
| Head silhouette (incl. curl) | 5.0 | 1 | ~189 |
| White face hole | 5.0 | 1 | ~89 |
| Inner ears | 3.5 | 1 | ~29 each |
| Nostrils | 2.5 | 1 | ~22 each |
| Mouth | 3.5 | 1 | ~40 |
| Letters (C/H/A/N) | 4.0 | 1 | ~58–81 |
| Eyes | — | — | exact circle (`fit_circle`) |

Large smooth regions (head, face) take a big step; small features (nostrils) take a
small one; perfectly round parts (eyes) bypass tuning entirely as exact circles.

## Don't over-smooth

Two passes is usually plenty. Heavy smoothing makes everything bland near a blobby
mean and you lose exactly the hand-drawn fullness this method exists to preserve. When
in doubt, prefer a slightly smaller step with `passes=1` over many passes.
