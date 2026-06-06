# From a bitmap (scan / photo) to a polyline SVG

The engine starts from a **vector** SVG whose paths use absolute `M/L/H/V/C/Z`. If the
hand-drawn logo only exists as a raster image (a scan, a phone photo, a PNG/JPG), trace
it to vector first, then feed the result into the normal workflow.

## 1. Clean the raster

A clean black-on-white bitmap traces far better.
- Crop to the artwork; deskew if needed.
- Convert to high-contrast black & white (threshold). Remove paper texture, shadows,
  and JPEG noise. ImageMagick example:

```bash
magick in.jpg -colorspace Gray -auto-level -threshold 55% -despeckle clean.pnm
```

(`potrace` wants a bilevel PBM/PNM; `magick ... clean.pnm` gives you that.)

## 2. Trace to SVG

**potrace** (best for smooth silhouettes — it already outputs Bézier curves):

```bash
potrace clean.pnm --svg --output traced.svg
# useful flags: -t (despeckle), -a (corner smoothness), -O (optimization tolerance)
```

**autotrace** is an alternative; Inkscape's *Path → Trace Bitmap* (Potrace under the
hood) is the GUI option.

## 3. Normalise to absolute M/L/H/V/C/Z

Traced SVGs often use relative commands or arcs. Flatten them so `tokenize_path` can
read them:
- Inkscape: select all → *Path → Object to Path*, then save as *Plain SVG*. Inkscape
  preference "store paths as absolute" (or running it through a tool like `svgo` /
  `svgpathtools`) yields absolute commands.
- Or load with `svgpathtools` in Python and re-emit absolute path data.

## 4. Decide: re-fit, or trust the trace?

Two valid paths once you have a vector SVG:

- **Re-fit with this skill (recommended for full control & variants).** potrace's
  output is already smooth, but running it through `vectorize.py` gives you uniform,
  tunable, parametric control points, exact circles for round parts, the even-odd
  knockout structure, and the variant/raster pipeline. Treat the traced SVG exactly
  like any polyline source (Steps 2–7 of the main workflow).
- **Trust the trace.** If potrace's curves are already perfect for your needs, you can
  skip re-fitting and just restructure into layers/variants. You lose per-contour
  tuning but save a step.

## Caveats

- Tracing invents detail at hard thresholds; compare against the original and tune the
  threshold/trace flags, not just the fit.
- Very thin strokes can break up — thicken slightly before thresholding if needed.
- Hand-lettering (a wordmark) often traces poorly; consider setting the wordmark in a
  real font instead and reconstructing only the pictorial mark.
