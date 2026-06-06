# Quality checklist — the fidelity gate before delivery

Run this before handing off a vectorized logo. It is tailored to *faithful
reconstruction*: the goal is a mark that is mathematically clean **and** still the
drawing the user gave you. Most items are checkable straight from the review gallery
(`python scripts/build_gallery.py` → `gallery.html`); a few need a quick look at the
SVG source. Treat any unchecked box as a reason not to ship yet.

## Fidelity vs the original

- [ ] In the gallery's **Difference** view, aligned ink cancels to black and only thin
      hairlines glow — no thick glowing bands (those are real deviations to tune out).
- [ ] In **Overlay** at 50%, the tinted original and the reconstruction track each other;
      no contour has drifted, shrunk, or bloated.
- [ ] The hand-drawn **character is preserved** — an off-centre curl, a deliberate wobble,
      an asymmetry the user wanted is still there, not "idealized away."
- [ ] No contour was **snapped to a primitive** it shouldn't be (the silhouette is a fitted
      curve, not a perfect circle/rounded-rect). See `references/method.md`.

## Curve sanity

- [ ] Each contour's **segment count is sane** — roughly `perimeter / resample_step`, not
      thousands (under-smoothed) and not a handful (over-smoothed). The gallery's
      reconstruction stats give the totals.
- [ ] No visible **cusps or kinks** from too-large a `step`; no residual **jitter** from
      too-small a `step` with too-few `passes`.
- [ ] No **self-intersections** — zoom in on tight concavities (inner ears, letter joins)
      and confirm the path doesn't pinch or cross itself.

## Holes & fill-rule

- [ ] Every intended **hole** (face, inner ears, letter counters like the bowl of an *A*)
      reads as see-through on the **transparent** variant.
- [ ] On **solid-background** variants those same holes show the *background* colour, not ink
      — proof the group is one `<path>` with `fill-rule="evenodd"`. See
      `references/layer-structure.md`.

## Circles

- [ ] Parts that are **truly round** in the drawing (eyes, dots) are emitted as exact
      `<circle>` via `fit_circle`, not as fitted blobs.

## Path hygiene

- [ ] The source used only **absolute** `M/L/H/V/C/Z` — no relative (lowercase) commands or
      `A` arcs leaked through. If they did, flatten the source and re-run (see
      `references/bitmap-input.md`).
- [ ] Every contour is **closed** (`Z`).

## Variant consistency

- [ ] Every intended cell of the **matrix** exists (ink × background × layout) and the
      gallery shows them all; filenames follow one consistent scheme.
- [ ] **black-on-white** and **white-on-black** are exact polarity inverses.
- [ ] **Transparent** variants have **no stray background `<rect>`**.
- [ ] The **viewBox is identical** across variants of the same layout, so they are drop-in
      replaceable.
- [ ] (If used) the **`currentColor`** variant recolours correctly when embedded inline and
      a CSS `color` is set — and you have *not* treated it as a replacement for the matrix
      (it only collapses the ink axis; see `references/layer-structure.md`).

## Raster & showcase (only if produced)

- [ ] `favicon.ico` is **multi-size** and still legible at 16px; `apple-touch-icon.png` is
      opaque (not transparent — iOS shows it on a tile).
- [ ] Any **AI showcase** images reproduce the mark **faithfully** — the model recoloured and
      composited it but did **not** redraw, re-letter, or re-proportion it. If it did,
      regenerate; the showcase must honour the same fidelity promise as the vectorization.
