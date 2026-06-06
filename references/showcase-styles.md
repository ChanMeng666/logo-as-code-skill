# Showcase backgrounds (optional AI render step)

The 12 curated backgrounds `scripts/generate_showcase.py` can composite a **vectorized**
mark onto, using Nano Banana (Gemini image generation). This is an optional, presentation
step — it does not change your SVGs.

**Fidelity first.** The showcase must honour the same promise as the vectorization: the
model recolours and composites the mark, but must **never redraw, simplify, re-letter, or
re-proportion it**. The script's prompt enforces this; if a render alters the mark,
regenerate (and check the quality checklist).

## Choosing the input PNG

- Feed a **transparent** rasterized variant from `out/raster/` (produced by `rasterize.js`),
  not the SVG. A larger size (256–512px) extracts most cleanly.
- Match **polarity to the background**: a **black** transparent mark for *light*
  backgrounds, a **white** transparent mark for *dark* backgrounds. (The script also sets
  the target logo colour automatically, so a clean transparent mark of either polarity
  works — matching just gives the model the least to do.)

---

## Dark styles → white mark

### 1. THE VOID (绝对虚空)
- **Base**: pure black (#000000); extremely fine silver/white micro noise; cold electronic grain
- **Atmosphere**: only a faint icy white/blue glow at one corner, like distant starlight
- **Suitable for**: hardcore tech, data security, infrastructure · **Saturation**: ~5%

### 2. FROSTED HORIZON (磨砂穹顶)
- **Base**: deep titanium / midnight slate gray (not pure black); organic dust noise, rough metal/stone
- **Atmosphere**: large, very-low-saturation cold gray-blue halo, edges dissolved like mist
- **Suitable for**: premium, design-focused brands · **Saturation**: ~10%

### 3. FLUID ABYSS (流体深渊)
- **Base**: deep midnight purple / very dark Klein blue; slight color-tinted noise, nebula feel
- **Atmosphere**: fluid fusion — dark orange (right) + dark blue (left) interweaving in the center
- **Suitable for**: AI products, dynamic systems, data viz · **Saturation**: ~20%

### 4. STUDIO SPOTLIGHT (物理影棚)
- **Base**: very dark warm carbon gray; larger grain like low-light camera film
- **Atmosphere**: single-side softbox/spotlight with natural vignette, editorial magazine quality
- **Suitable for**: editorial, magazine-style presentations · **Saturation**: 0%

### 5. ANALOG LIQUID (物理流体)
- **Base**: ONE solid color — vibrant orange (#FF6B00), Klein blue (#002FA7), or lime (#00FF41)
- **Texture**: metallic shimmer (gold dust, mica, iridescent oil-slick), extreme grainy "thermal" roughness
- **Suitable for**: creative tools, artistic / experimental brands · **Saturation**: high (40–60%)
- **Key**: maximum contrast between chaotic organic texture and the ultra-clean vector mark

### 6. LED MATRIX (数字硬件)
- **Base**: black with glowing dot-matrix waves; CRT/LED-billboard/halftone artifacts
- **Atmosphere**: waves of glowing points create depth, the mark floating above as a solid entity
- **Suitable for**: AI compute, Web3, data services, hardware · **Saturation**: ~25–35%

---

## Light styles → black mark

### 7. EDITORIAL PAPER (纸本编辑)
- **Base**: off-white / alabaster / pearl (not pure white); watercolor / rough art-paper texture
- **Atmosphere**: natural diffuse light, slight warm gray corner vignette
- **Suitable for**: serious, human-centered brands · **Saturation**: ~5%

### 8. IRIDESCENT FROST (幻彩透砂)
- **Base**: very light silver-gray / cold white; very fine micro noise, frosted glass / sandblasted aluminum
- **Atmosphere**: soft holographic light purple / blue / pink, as if through thick frosted glass
- **Suitable for**: tech, hardware, scientific products · **Saturation**: ~25%

### 9. MORNING AURA (晨雾光域)
- **Base**: warm ivory / very light cream; soft mist-like noise
- **Atmosphere**: large blurred pastels (mint, baby blue, dawn orange) dissolving into warm white
- **Suitable for**: friendly, accessible AI products · **Saturation**: ~15%

### 10. CLINICAL STUDIO (无菌影棚)
- **Base**: pure white / very light cold gray; high-frequency sharp cold micro noise
- **Atmosphere**: pure light/shadow — large softbox gradient, sterile geometric order, 3D depth in 2D
- **Suitable for**: algorithm-driven, data-centric, confident brands · **Saturation**: ~2%

### 11. UI CONTAINER (容器化界面)
- **Base**: clean gradient / solid; minimal digital noise; frosted-glass app-icon container
- **Atmosphere**: rounded corners, transparency, micro-shadows — digital-product native
- **Suitable for**: apps, SaaS, UI/UX-focused brands · **Saturation**: ~10–20%

### 12. SWISS FLAT (瑞士扁平)
- **Base**: 100% pure solid color — deep vintage green, rich burgundy, or classic navy
- **Atmosphere**: zero gradients, zero noise, zero effects — pure color + form
- **Suitable for**: established brands, classic institutions, sustainability · **Saturation**: rich, deep

---

## Quick selection guide

- **By contrast** — High: THE VOID, CLINICAL STUDIO, SWISS FLAT · Medium: FROSTED HORIZON,
  IRIDESCENT FROST · Low: EDITORIAL PAPER, MORNING AURA
- **By mood** — Cold/rational: THE VOID, CLINICAL STUDIO, IRIDESCENT FROST, LED MATRIX ·
  Warm/approachable: MORNING AURA, EDITORIAL PAPER, ANALOG LIQUID · Dynamic: FLUID ABYSS,
  FROSTED HORIZON · Classic: SWISS FLAT, EDITORIAL PAPER
- **By complexity** — Minimal: THE VOID, SWISS FLAT, CLINICAL STUDIO · Moderate: FROSTED
  HORIZON, IRIDESCENT FROST, EDITORIAL PAPER · Complex: ANALOG LIQUID, LED MATRIX, UI CONTAINER

All styles aim for restrained saturation, fine physical noise, micro-typography, generous
breathing space, and a high-end brand-identity finish — with the mark reproduced faithfully.
