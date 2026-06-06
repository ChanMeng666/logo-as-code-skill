#!/usr/bin/env node
/*
 * rasterize.js — generate raster (PNG) and icon (ICO) exports from a logo's
 * ready-to-use SVG variants. Companion to vectorize.py / a logo's build.py
 * (which produce the SVGs).
 *
 * GENERIC: edit the CONFIG block below to point at your logo's SVGs and pick
 * the sizes you need. The defaults are wired to the chan-monkey example so you
 * can run it out of the box from that folder.
 *
 * Output (relative to OUT_DIR):
 *   raster/<square>-<size>.png    transparent, square (icons, avatars, favicons)
 *   raster/<wide>-<size>.png      transparent, native aspect (banners, social)
 *   icons/favicon.ico             multi-size, opaque (browser tab)
 *   icons/apple-touch-icon.png    180px opaque
 *   icons/favicon-<size>.png      opaque PNG favicons / web-manifest icons
 *
 * Requires: sharp, png-to-ico (install with `npm install`).
 * Run:  node rasterize.js     (or `npm run rasterize`)
 */
const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const pngToIco = require('png-to-ico').default || require('png-to-ico');

// ===========================================================================
// CONFIG — edit this block for your logo.
// ===========================================================================
// Resolve everything relative to this script's location by default; override
// BASE to point elsewhere (e.g. an absolute assets dir).
const BASE = path.resolve(__dirname, '..', 'examples', 'chan-monkey', 'out');
const OUT_DIR = BASE; // where raster/ and icons/ are written

// SVG sources. Use the *transparent* variants for square/wide PNGs and an
// *opaque* (on-white) variant for the favicon/touch-icon family.
const SRC = {
  squareTransparentBlack: path.join(BASE, 'monkey', 'chan-meng-monkey-black-transparent.svg'),
  squareTransparentWhite: path.join(BASE, 'monkey', 'chan-meng-monkey-white-transparent.svg'),
  squareOpaque:           path.join(BASE, 'monkey', 'chan-meng-monkey-black-on-white.svg'),
  wideTransparentBlack:   path.join(BASE, 'full', 'chan-meng-logo-black-transparent.svg'),
  wideTransparentWhite:   path.join(BASE, 'full', 'chan-meng-logo-white-transparent.svg'),
};

const SQUARE_PREFIX = 'monkey';                                 // filename stem for square PNGs
const WIDE_PREFIX = 'full';                                     // filename stem for wide PNGs
const SQUARE_SIZES = [16, 32, 48, 64, 128, 180, 192, 256, 512]; // square PNGs
const WIDE_SIZES = [256, 512];                                  // wide PNGs (by width)
const ICO_SIZES = [16, 32, 48];                                 // packed into favicon.ico
const PNG_FAVICON_SIZES = [32, 192, 512];                       // opaque PNG favicons
const DENSITY = 384;                                            // SVG raster DPI
const SQUARE_MARGIN = 0.08;                                     // breathing room each side
// ===========================================================================

const RASTER = path.join(OUT_DIR, 'raster');
const ICONS = path.join(OUT_DIR, 'icons');
const TRANSPARENT = { r: 0, g: 0, b: 0, alpha: 0 };
const WHITE = { r: 255, g: 255, b: 255, alpha: 1 };

function ensureDir(d) {
  fs.mkdirSync(d, { recursive: true });
}

// Render an SVG onto a SQUARE canvas of `size`, preserving aspect with margin.
async function renderSquare(svgPath, size, outPath, { opaqueBg = null } = {}) {
  const inner = Math.round(size * (1 - 2 * SQUARE_MARGIN));
  const logo = await sharp(svgPath, { density: DENSITY })
    .resize(inner, inner, { fit: 'contain', background: TRANSPARENT })
    .png()
    .toBuffer();
  await sharp({ create: { width: size, height: size, channels: 4, background: opaqueBg || TRANSPARENT } })
    .composite([{ input: logo, gravity: 'center' }])
    .png()
    .toFile(outPath);
}

// Render an SVG at a target WIDTH keeping native aspect ratio (transparent bg).
async function renderWidth(svgPath, width, outPath) {
  await sharp(svgPath, { density: DENSITY })
    .resize({ width, fit: 'contain', background: TRANSPARENT })
    .png()
    .toFile(outPath);
}

async function main() {
  ensureDir(RASTER);
  ensureDir(ICONS);

  // Square PNGs (transparent) — both ink colours.
  for (const size of SQUARE_SIZES) {
    await renderSquare(SRC.squareTransparentBlack, size, path.join(RASTER, `${SQUARE_PREFIX}-black-${size}.png`));
    await renderSquare(SRC.squareTransparentWhite, size, path.join(RASTER, `${SQUARE_PREFIX}-white-${size}.png`));
  }

  // Wide PNGs (transparent, native aspect) — both ink colours.
  for (const size of WIDE_SIZES) {
    await renderWidth(SRC.wideTransparentBlack, size, path.join(RASTER, `${WIDE_PREFIX}-black-${size}.png`));
    await renderWidth(SRC.wideTransparentWhite, size, path.join(RASTER, `${WIDE_PREFIX}-white-${size}.png`));
  }

  // Favicon: opaque white square so it stays visible on light AND dark chrome.
  const icoBuffers = [];
  for (const size of ICO_SIZES) {
    const buf = await sharp(SRC.squareOpaque, { density: DENSITY })
      .resize(size, size, { fit: 'contain', background: WHITE })
      .flatten({ background: WHITE })
      .png()
      .toBuffer();
    icoBuffers.push(buf);
  }
  fs.writeFileSync(path.join(ICONS, 'favicon.ico'), await pngToIco(icoBuffers));

  // Apple touch icon: 180px opaque white square.
  await renderSquare(SRC.squareOpaque, 180, path.join(ICONS, 'apple-touch-icon.png'), { opaqueBg: WHITE });

  // Opaque PNG favicons / web-manifest icons.
  for (const size of PNG_FAVICON_SIZES) {
    await renderSquare(SRC.squareOpaque, size, path.join(ICONS, `favicon-${size}.png`), { opaqueBg: WHITE });
  }

  console.log('Done. Raster ->', path.relative(OUT_DIR, RASTER), '| Icons ->', path.relative(OUT_DIR, ICONS));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
