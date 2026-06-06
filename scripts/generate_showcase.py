#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_showcase.py — OPTIONAL premium showcase renders for a vectorized logo.

Composites an already-vectorized mark onto one of 12 curated premium backgrounds
using Nano Banana (Gemini image generation). Works with the official Google API or a
third-party endpoint.

  *** OPTIONAL STEP ***
  The core skill (vectorize → variants → gallery) needs NO Python dependencies. This
  script is the only part that does. It depends on `google-genai`, `python-dotenv`,
  and `Pillow` (`pip install -r requirements.txt`) and a GEMINI_API_KEY in `.env`. If
  those are missing it exits cleanly — nothing else in the skill is affected.

FIDELITY CONTRACT: this skill *reconstructs* a real drawing, so the showcase must
reproduce the supplied mark EXACTLY — the model recolours and composites it, but must
never redraw, simplify, re-letter, or re-proportion it. The prompt below enforces that.

INPUT: a transparent PNG of a variant produced by `rasterize.js` (e.g.
`out/raster/monkey-black-512.png`). Feed the transparent variant whose polarity matches
the chosen background (a black mark for light backgrounds, a white mark for dark ones);
the script picks the target logo colour automatically.

Run:
  python scripts/generate_showcase.py "Chan Meng" out/raster/monkey-black-512.png \\
      --all-styles --output-dir examples/chan-monkey/out/showcase
"""

import argparse
import base64
import os
import sys
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: python-dotenv not installed. This is the OPTIONAL showcase step.")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai not installed. This is the OPTIONAL showcase step.")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)

load_dotenv()

# Configuration — official Google API or any compatible third-party endpoint.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_BASE_URL = os.getenv("GEMINI_API_BASE_URL", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-image-preview")

# Background style prompts. See references/showcase-styles.md for the full catalog.
BACKGROUND_STYLES = {
    "void": """THE VOID (绝对虚空)
Absolute black (#000000) background with extremely fine silver/white high-contrast micro noise.
Cold, sharp electronic film grain texture. Minimal atmosphere light - only a faint, icy white or blue glow
at the extreme corner, like distant starlight at the edge of the universe.""",

    "frosted": """FROSTED HORIZON (磨砂穹顶)
Deep titanium gray or midnight slate gray base, not pure black. Organic film-like dust noise texture,
resembling unpolished rough metal or stone surface. Large area but extremely low saturation cold-toned
light halo (low-saturation gray-blue), edges completely dissolved like mist.""",

    "fluid": """FLUID ABYSS (流体深渊)
Deep midnight purple or extremely dark Klein blue base. Noise texture with slight color tint,
blending with the base to create deep-sea sediment or nebula texture. Fluid fusion light -
dark orange on right side, dark blue on left side, slowly interweaving in the dark space center.""",

    "spotlight": """STUDIO SPOTLIGHT (物理影棚)
Extremely dark warm carbon gray base. Slightly larger grain simulating low-light camera photography,
like paper print grain in weak light. Single-side softbox or spotlight creating natural vignette,
editorial magazine quality with professional photography feel.""",

    "analog_liquid": """ANALOG LIQUID (物理流体)
Solid color base - choose ONE color only: vibrant orange (#FF6B00), Klein blue (#002FA7), or lime green (#00FF41).
Physical liquid textures with metallic shimmer overlaying the solid base - gold dust flow, metallic mica powder
suspended in liquid, iridescent pigments creating rainbow oil slick effects. Dry mineral textures like crushed
gemstones. Macro photography of natural materials - copper oxidation, rust patterns, gold leaf fragments.
Extreme grainy texture like thermal imaging or pushed film grain. Create maximum contrast between chaotic
organic texture and ultra-clean sharp vector logo.""",

    "led_matrix": """LED MATRIX (数字硬件)
Black background with glowing dot matrix patterns creating waves of light. Simulate old-school CRT displays,
LED billboards, or halftone printing dots. Retro computer display artifacts with modern execution.
Waves of glowing points creating depth, logo as solid entity floating above. Cyberpunk and retro-futurism
aesthetics with hardcore geek appeal.""",

    "editorial": """EDITORIAL PAPER (纸本编辑)
Off-white, alabaster, or pearl white base (not pure white). High-grade watercolor or rough art paper
texture suggesting physical paper tactile quality. Natural light diffuse reflection with slight warm
gray vignette in corners. Humanistic, independent magazine aesthetic.""",

    "iridescent": """IRIDESCENT FROST (幻彩透砂)
Extremely light silver-gray or cold white base, creating calm, rational experimental space.
Extremely fine micro noise, simulating high-density frosted glass or sandblasted aluminum surface.
Restrained holographic/iridescent atmosphere light - faint low-saturation light purple, light blue
or soft pink fluid diffused light in the clean background depth, like through thick frosted glass.""",

    "morning": """MORNING AURA (晨雾光域)
Warm ivory or extremely light cream color base. Soft noise blending into base like morning mist or dust,
creating thin layer of atmospheric haze. Large area blurred low-saturation pastel colors (mint green,
baby blue, dawn orange) dissolving into warm white. Warm, intelligent, pressure-free atmosphere.""",

    "clinical": """CLINICAL STUDIO (无菌影棚)
Pure white or extremely light cold gray base. High-frequency sharp cold-toned digital micro noise with
enhanced sharpness. Pure light/shadow structure - large softbox from top/side creating smooth gray-white
gradient. Sterile space with geometric order, creating 3D depth in 2D presentation.""",

    "ui_container": """UI CONTAINER (容器化界面)
Clean gradient or solid color background with minimal digital noise. Frosted glass container effect
(like app icon base) with rounded corners and subtle transparency. Micro-shadows creating depth illusion.
UI-native presentation suggesting interactivity and digital product context. Logo sits in transparent
container with modern interface design language.""",

    "swiss_flat": """SWISS FLAT (瑞士扁平)
100% pure solid color background - deep vintage green, rich burgundy, or classic navy. Absolutely no
gradients, no noise, no effects. Pure graphic design with zero tricks. Just perfect color and form.
Extreme confidence and timeless authority. Classic Swiss International Style with absolute flatness.""",
}

# Dark backgrounds → white mark; light backgrounds → black mark.
DARK_STYLES = {"void", "frosted", "fluid", "spotlight", "analog_liquid", "led_matrix"}
LIGHT_STYLES = {"editorial", "iridescent", "morning", "clinical", "ui_container", "swiss_flat"}


def load_reference_image(image_path: str) -> Optional[str]:
    """Load and base64-encode the reference (rasterized variant) PNG."""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"Error loading reference image: {e}")
        return None


def build_prompt(logo_name: str, logo_color: str, style_description: str,
                 product_description: str) -> str:
    """The showcase prompt. The LOGO PROCESSING block is rewritten for this skill so
    the model reproduces the vectorized mark faithfully instead of re-stylizing it."""
    desc = product_description.upper() if product_description else "VECTORIZED IDENTITY"
    return f"""Place the EXACT logo from the reference image onto a premium background.
Treat the reference mark as a finished, fixed vector asset.

LOGO PROCESSING (fidelity is mandatory):
- Reproduce the supplied mark EXACTLY as given. Do NOT redraw, simplify, re-letter,
  re-proportion, add, or remove any detail.
- Preserve every curve, hole, counter, and proportion of the original geometry.
- The only permitted change is colour: render the mark as 100% solid flat {logo_color}
  for maximum contrast, with sharp clean edges.
- Strip only the reference's own background/frame; keep the graphic itself untouched.
- CRITICAL: fidelity to the reference geometry overrides all stylization. If in doubt,
  copy the reference more closely.

BACKGROUND CONSTRUCTION:
{style_description}

TYPOGRAPHY AND LAYOUT:
Use classic Swiss-style typography logic with extreme proportion contrast.
- Main subject centered: place the faithful flat logo at the absolute visual center with
  huge breathing space around it.
- Micro-typography only: no large titles. Use a very small (6pt-9pt) clean sans-serif
  (Inter, Helvetica, Geist) in the corners / bottom center.
- Text content (strictly aligned):
  Left corner: {logo_name.upper()}
  Right corner: v. 1.0.0 // 2026
  Bottom center: {desc}

CRITICAL: the logo MUST be the exact reference mark, in {logo_color}, perfectly centered,
flat vector with sharp edges — composited unaltered onto the background above."""


def generate_showcase_image(logo_name: str, reference_image_path: str, style: str,
                            output_path: str, product_description: str = "") -> bool:
    """Generate one showcase image. Returns True on success."""
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not set (see .env.example). This is the OPTIONAL showcase step.")
        return False
    if style not in BACKGROUND_STYLES:
        print(f"Error: unknown style '{style}'. Available: {list(BACKGROUND_STYLES)}")
        return False

    reference_image_b64 = load_reference_image(reference_image_path)
    if not reference_image_b64:
        return False

    logo_color = "pure white (#FFFFFF)" if style in DARK_STYLES else "pure black (#000000)"
    prompt = build_prompt(logo_name, logo_color, BACKGROUND_STYLES[style], product_description)

    try:
        client_config = {"api_key": GEMINI_API_KEY}
        if GEMINI_API_BASE_URL:
            client_config["http_options"] = {"api_endpoint": GEMINI_API_BASE_URL}
        client = genai.Client(**client_config)

        contents = [
            types.Part.from_bytes(
                data=base64.b64decode(reference_image_b64), mime_type="image/png"),
            types.Part.from_text(text=prompt),
        ]

        print(f"Generating showcase: style={style}, model={GEMINI_MODEL}"
              + (f", endpoint={GEMINI_API_BASE_URL}" if GEMINI_API_BASE_URL else ""))

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio="16:9", image_size="2K"),
            ),
        )

        for part in response.parts:
            if part.inline_data is not None:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                part.as_image().save(output_path)
                print(f"✓ saved {output_path}")
                return True
            elif part.text is not None:
                print(f"Model response: {part.text}")

        print("Error: no image in response")
        return False
    except Exception as e:
        print(f"Error generating showcase image: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="OPTIONAL: generate premium showcase renders for a vectorized logo "
                    "(Gemini / Nano Banana). The core skill needs no Python deps.")
    parser.add_argument("logo_name", help="Display name of the logo/brand")
    parser.add_argument("reference_image",
                        help="Path to a transparent rasterized variant PNG (from rasterize.js)")
    parser.add_argument("--style", choices=list(BACKGROUND_STYLES),
                        default="iridescent", help="Background style (default: iridescent)")
    parser.add_argument("--output", "-o",
                        help="Output path for a single style (overrides --output-dir)")
    parser.add_argument("--output-dir", default="output",
                        help="Directory for outputs (default: output/; "
                             "use e.g. assets/showcase for delivery)")
    parser.add_argument("--description", "-d", default="",
                        help="Short product/brand description for the micro-typography")
    parser.add_argument("--all-styles", action="store_true",
                        help=f"Generate all {len(BACKGROUND_STYLES)} styles")

    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = args.logo_name.lower().replace(" ", "-")

    if args.all_styles:
        ok = 0
        for style in BACKGROUND_STYLES:
            path = out_dir / f"{safe_name}_{style}.png"
            if generate_showcase_image(args.logo_name, args.reference_image, style,
                                       str(path), args.description):
                ok += 1
        print(f"\n✓ generated {ok}/{len(BACKGROUND_STYLES)} showcase images into {out_dir}/")
        sys.exit(0 if ok else 1)
    else:
        path = args.output or str(out_dir / f"{safe_name}_{args.style}.png")
        ok = generate_showcase_image(args.logo_name, args.reference_image, args.style,
                                     path, args.description)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
