# Mapping contours to layers (holes, knockouts, circles, variants)

After parsing, you have an ordered list of closed contours. The craft of a faithful
reconstruction is assigning each contour a **role** and composing those roles into the
right SVG elements. This guide explains the building blocks; the worked example
(`examples/chan-monkey/build.py`) shows them combined.

## Roles a contour can play

| Role | Emitted as | Engine call |
|---|---|---|
| Outer silhouette | one sub-path in an `even-odd` group | `fit_contour` → `path_el` |
| Hole (face, letter counter, inner ear) | another sub-path in the **same** `even-odd` group | `fit_contour` |
| Feature painted on top (nostril, mouth, stripe) | its own `path` | `fit_contour` → `path_el` |
| Wordmark glyph | a sub-path in the wordmark `even-odd` group | `fit_contour` |
| True circle (eye, dot) | exact `<circle>` | `fit_circle` → `circle_el` |

## The `even-odd` knockout trick

To make an inner contour a genuine **hole** (see-through), put the outer contour and
the inner contour(s) in **one `<path>`** with `fill-rule="evenodd"`:

```python
path_el([silhouette] + [hole1, hole2], ink, evenodd=True)
```

The even-odd rule fills a region only when a ray crosses an odd number of contours, so
nested contours alternate fill/hole automatically. Why this matters:

- **On a solid background** the hole shows the background color.
- **On a transparent background** the hole is *genuinely transparent* — whatever the
  logo sits on shows through. This is what makes the "knockout" look work everywhere.

A letter like **A** has a counter (the triangular hole); emit the glyph outline and
its counter together as one even-odd path so the hole punches through.

## Paint order

`render_svg(width, height, background, elements)` paints `elements` back-to-front:

1. optional background `<rect>` (or `None` for transparent),
2. the silhouette/knockout group,
3. features (circles, nostrils, mouth…) on top,
4. the wordmark (if this variant includes it).

## Variants

A variant is just a different combination of: **ink color**, **background**
(color or `None`), and **which layer groups are included** (e.g. mark-only drops the
wordmark and crops the canvas height to the mark). Declare them as a list of tuples
and loop — one math definition produces every brand-ready file. See the monkey
example's `VARIANTS` and `render(...)`.

## Theme-adaptive (`currentColor`) variant

Besides a hex colour, the `ink` can be the CSS keyword **`currentColor`**. Paired with
`background=None` (transparent), this emits a *single* SVG whose ink is whatever CSS
`color` the host element has:

```python
("web/logo-currentColor.svg", "currentColor", None, True)   # one VARIANTS row
```

```html
<!-- inline the SVG, then drive its colour from CSS -->
<span style="color:#111">…inline svg…</span>          <!-- black mark -->
<span style="color:#fff">…inline svg…</span>          <!-- white mark -->

<style>
  .logo { color: #111 }
  @media (prefers-color-scheme: dark) { .logo { color: #fff } }   <!-- auto dark/light -->
</style>
```

This is **additive, not a replacement** for the explicit matrix:

- It only collapses the **ink** axis. It cannot express the **background** axis
  (on-white / on-black / transparent are still separate files).
- It only works when the SVG is **inlined** into the DOM — `currentColor` does *not*
  resolve for an SVG loaded via `<img src>` or as a CSS `background-image`.
- The favicon / ICO pipeline (`rasterize.js`) needs a concrete fill, so keep the real
  black/white variants for those.

Use it as the convenient web-embed artifact; keep the matrix for everything else.

## Tips for identifying roles

- Open the source SVG and toggle paths, or print each contour's bounding box, to see
  what is what.
- Holes are usually *inside* a silhouette's bounding box.
- A contour whose points are near-equidistant from a center is a circle candidate —
  use `fit_circle` for crisp results instead of a fitted blob.
