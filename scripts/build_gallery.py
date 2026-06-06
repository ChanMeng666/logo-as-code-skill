#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_gallery.py — render a self-contained review gallery for a vectorized logo.

Companion to a logo's `build.py` (which emits the SVG variants). This script reads
`assets/gallery_template.html`, the original hand-drawn SVG, the emitted variants,
the per-contour TUNING, and any AI showcase PNGs, then writes a ready-to-open
`gallery.html`. The gallery has three jobs:

  1. FIDELITY CHECK — original drawing vs fitted reconstruction, with side-by-side /
     overlay / difference views. This is the Step-4 visual-tuning tool: spot a
     deviation, find its contour in the tuning table, adjust (step, passes), re-run.
  2. VARIANT MATRIX — every colour/layout variant, drop-in inspectable.
  3. SHOWCASE — optional AI showcase renders, embedded if present.

GENERIC: edit the CONFIG block to point at your logo. Defaults are wired to the
chan-monkey example so it runs out of the box.

Run:  python scripts/build_gallery.py
Stdlib only (+ imports the logo's build.py and scripts/vectorize.py).
"""

import base64
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)  # make vectorize importable
import vectorize as V  # noqa: E402

# ===========================================================================
# CONFIG — edit this block for your logo.
# ===========================================================================
# The logo's per-logo config module (the template you copied from chan-monkey).
BUILD_PY = os.path.join(ROOT, "examples", "chan-monkey", "build.py")

# Display text.
PRODUCT_NAME = "Chan Meng"
TAGLINE = "Hand-drawn → parametric Bézier curves"
YEAR = "2026"

# Which emitted variant to show as the "reconstruction" in the fidelity check.
# None = auto-pick (a full, transparent, dark-ink variant). Otherwise a path
# relative to the build module's OUT dir, e.g. "full/...-black-transparent.svg".
RECON_REL = None

# Where AI showcase PNGs live (optional). Relative to the logo repo root, or abs.
SHOWCASE_DIR = os.path.join(ROOT, "examples", "chan-monkey", "out", "showcase")

# Where to write the gallery. None = next to the build module (its folder).
OUT_HTML = None

TEMPLATE = os.path.join(ROOT, "assets", "gallery_template.html")
# ===========================================================================


def load_build_module(path):
    """Import a logo's build.py by file path WITHOUT running its __main__ block."""
    spec = importlib.util.spec_from_file_location("logo_build_cfg", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def strip_xml_decl(svg):
    return re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg)


def strip_root_size(svg):
    """Remove width/height on the root <svg> so CSS controls the display size
    (keep the viewBox so it still scales correctly)."""
    def repl(m):
        tag = m.group(0)
        tag = re.sub(r'\s(width|height)="[^"]*"', "", tag)
        return tag
    return re.sub(r"<svg\b[^>]*>", repl, svg, count=1)


def prep_compare_svg(svg):
    """Prepare an SVG for the overlay/difference comparison: transparent, ink-only,
    CSS-sizable. Drops background rects and clip-paths so layers register cleanly
    and can be re-tinted by the gallery's CSS."""
    svg = strip_xml_decl(svg)
    svg = strip_root_size(svg)
    svg = re.sub(r'\sclip-path="[^"]*"', "", svg)      # clip no longer needed
    svg = re.sub(r"<rect\b[^>]*/>", "", svg)            # full-canvas backgrounds
    svg = re.sub(r"<rect\b[^>]*>.*?</rect>", "", svg, flags=re.S)
    return svg.strip()


def prep_card_svg(svg):
    """Prepare an emitted variant for a matrix card: keep its own background
    (so on-white / on-black read correctly), just make it CSS-sizable."""
    return strip_root_size(strip_xml_decl(svg)).strip()


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def auto_pick_recon(variants):
    """Pick a full, transparent, dark-ink variant for the fidelity check."""
    def score(v):
        rel, ink, bg, txt = v
        s = 0
        if bg is None:
            s += 4                       # transparent registers best in overlay
        if txt:
            s += 2                       # full lockup
        if isinstance(ink, str) and ink.lower() not in ("#ffffff", "#fff", "white"):
            s += 1                       # dark ink
        return s
    return max(variants, key=score)[0]


def variant_label(rel, ink, bg, txt):
    """Human title + subtitle from a VARIANTS tuple."""
    stem = os.path.splitext(os.path.basename(rel))[0]
    inkname = "white" if str(ink).lower() in ("#ffffff", "#fff", "white") else (
        "currentColor" if str(ink).lower() == "currentcolor" else "black")
    bgname = "transparent" if bg is None else (
        "on white" if str(bg).lower() in ("#ffffff", "#fff", "white") else "on black")
    layout = "full lockup" if txt else "mark only"
    return stem, f"{inkname} · {bgname} · {layout}"


def contour_table(tuning):
    if not tuning:
        return '<tr><td class="py-2 opacity-40" colspan="3">no TUNING dict found</td></tr>'
    rows = []
    for name, val in tuning.items():
        try:
            step, passes = val
        except (TypeError, ValueError):
            step, passes = val, ""
        rows.append(
            f'<tr class="border-b border-black/5">'
            f'<td class="py-2 pr-4">{name}</td>'
            f'<td class="py-2 pr-4">{step}</td>'
            f'<td class="py-2">{passes}</td></tr>'
        )
    return "\n".join(rows)


def recon_stats(recon_path):
    """Real reconstruction metrics, read back from the emitted SVG."""
    text = read(recon_path)
    ds = V.load_svg_paths(recon_path)
    segments = sum(d.count("C") for d in ds)
    contours = sum(d.count("M") for d in ds)
    circles = text.count("<circle")

    def chip(n, label):
        return (f'<span class="font-mono text-xs px-3 py-2 bg-white border '
                f'border-black/10 rounded">{n} <span class="opacity-40">{label}</span></span>')
    return "".join([
        chip(contours, "contours"),
        chip(segments, "Bézier segs"),
        chip(circles, "circles"),
    ])


def variant_cards(out_dir, variants):
    cards = []
    for v in variants:
        rel, ink, bg, txt = v
        path = os.path.join(out_dir, rel)
        if not os.path.exists(path):
            continue
        title, subtitle = variant_label(rel, ink, bg, txt)
        svg = prep_card_svg(read(path))
        cards.append(f"""
        <div class="flex flex-col items-center logo-card">
            <div class="checker rounded-xl w-full aspect-square p-10 mb-6 relative flex items-center justify-center overflow-hidden">
                <div class="logo-aura"></div>
                <div class="w-3/4 h-3/4 relative z-10 logo-canvas card-canvas">{svg}</div>
            </div>
            <h3 class="text-sm font-medium uppercase tracking-widest mb-1 text-center">{title}</h3>
            <p class="font-mono text-[11px] opacity-50 tracking-wider text-center">{subtitle}</p>
            <div class="divider-line mt-5"></div>
        </div>""")
    return "\n".join(cards) if cards else \
        '<p class="opacity-40 text-sm col-span-full text-center">No variant SVGs found — run build.py first.</p>'


def showcase_section(showcase_dir):
    if not os.path.isdir(showcase_dir):
        return ""
    pngs = sorted(f for f in os.listdir(showcase_dir) if f.lower().endswith(".png"))
    if not pngs:
        return ""
    cards = []
    for fn in pngs:
        with open(os.path.join(showcase_dir, fn), "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        label = os.path.splitext(fn)[0].replace("_", " ")
        cards.append(f"""
        <figure class="showcase-img bg-white">
            <img src="data:image/png;base64,{b64}" alt="{label}" class="w-full block"/>
            <figcaption class="font-mono text-[11px] opacity-50 uppercase tracking-widest p-3 text-center">{label}</figcaption>
        </figure>""")
    return f"""
        <section class="w-full max-w-6xl mb-28">
            <h2 class="text-sm font-medium uppercase tracking-ultra mb-1 text-center">Showcase</h2>
            <p class="text-xs opacity-50 font-light mb-12 text-center">The vectorized mark, composited (unaltered) onto premium backgrounds.</p>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">{''.join(cards)}</div>
        </section>"""


def main():
    cfg = load_build_module(BUILD_PY)
    out_dir = getattr(cfg, "OUT", os.path.join(os.path.dirname(BUILD_PY), "out"))
    src = getattr(cfg, "SRC", None)
    variants = getattr(cfg, "VARIANTS", [])
    tuning = getattr(cfg, "TUNING", {})

    if not variants:
        print("warning: build module exposes no VARIANTS list", file=sys.stderr)

    recon_rel = RECON_REL or (auto_pick_recon(variants) if variants else None)
    recon_path = os.path.join(out_dir, recon_rel) if recon_rel else None

    if not recon_path or not os.path.exists(recon_path):
        sys.exit("error: reconstruction SVG not found — run the logo's build.py first.")
    if not src or not os.path.exists(src):
        sys.exit("error: original source SVG (build module SRC) not found.")

    html = read(TEMPLATE)
    replacements = {
        "{{PRODUCT_NAME}}": PRODUCT_NAME,
        "{{TAGLINE}}": TAGLINE,
        "{{YEAR}}": YEAR,
        "{{ORIGINAL_SVG}}": prep_compare_svg(read(src)),
        "{{RECONSTRUCTION_SVG}}": prep_compare_svg(read(recon_path)),
        "{{CONTOUR_TABLE}}": contour_table(tuning),
        "{{RECON_STATS}}": recon_stats(recon_path),
        "{{VARIANT_CARDS}}": variant_cards(out_dir, variants),
        "{{SHOWCASE_SECTION}}": showcase_section(SHOWCASE_DIR),
    }
    for token, value in replacements.items():
        html = html.replace(token, value)

    out_html = OUT_HTML or os.path.join(os.path.dirname(BUILD_PY), "gallery.html")
    V.write(out_html, html)
    print(f"wrote {os.path.relpath(out_html, ROOT)}")
    print(f"  reconstruction: {recon_rel}")
    print(f"  variants:       {sum(1 for v in variants if os.path.exists(os.path.join(out_dir, v[0])))}")
    sc = showcase_section(SHOWCASE_DIR)
    print(f"  showcase:       {'embedded' if sc else 'none'}")


if __name__ == "__main__":
    main()
