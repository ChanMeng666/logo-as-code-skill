<div align="center">

<img src="examples/chan-monkey/out/monkey/chan-meng-monkey-black-on-white.svg" alt="logo-as-code preview" width="140" />

# logo-as-code-skill

**Turn a hand-drawn logo into clean, reproducible code.**

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that fits smooth
cubic Bézier curves to a sketched / scanned mark's real outline — producing an editable
SVG, a matrix of color &amp; layout variants, an interactive review gallery, PNG / ICO /
favicon exports, and optional AI showcase renders.

![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-d97757)
![Python](https://img.shields.io/badge/Python-stdlib%20core-3776ab)
![Node.js](https://img.shields.io/badge/Node.js-rasterize-339933)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

[English](#english) · [中文](#中文)

</div>

---

## English

A hand-drawn logo is charming but **unmeasurable** — a flat image, or an SVG of hundreds
of hand-placed points that is rough, uneditable, and not truly scalable. This skill turns
each contour into a small set of **smooth cubic Bézier curves** (genuine parametric
polynomials), fitted *along the original outline* so the hand-drawn character survives,
yet the result is fully mathematical: reproducible, infinitely scalable, parametrically
tweakable, and diff-able in git.

It generalizes the method developed for the
[Chan Meng personal-brand logo](https://github.com/ChanMeng666/chan-meng-personal-brand-logo):
a hand-drawn mark of hundreds of hand-placed points was reconstructed into a small set
of genuine parametric polynomial curves — reproducible, infinitely scalable, and
parametrically tweakable, while preserving the original's hand-drawn character. This
skill packages that pipeline so it can be applied to **any** logo.

> **This skill *reconstructs* an existing drawing — it does not generate new logo designs
> from scratch.** Photographic images and already-clean vector files are out of scope.

### What's inside

```
logo-as-code-skill/
├── SKILL.md                  # the skill: when to use it + the step-by-step workflow
├── references/
│   ├── method.md             # the mathematics (Catmull-Rom → cubic Bézier)
│   ├── layer-structure.md    # contour roles, holes, even-odd knockout, currentColor
│   ├── tuning-guide.md       # choosing (resample_step, smoothing_passes)
│   ├── bitmap-input.md       # scan/photo → polyline SVG (potrace) first
│   ├── quality-checklist.md  # the fidelity gate to run before delivery
│   └── showcase-styles.md    # 12 premium backgrounds for AI showcase renders (optional)
├── scripts/
│   ├── vectorize.py          # GENERIC engine (Python stdlib only) — never edited per logo
│   ├── build_gallery.py      # GENERIC review-gallery generator (stdlib only)
│   ├── rasterize.js          # GENERIC SVG → PNG/ICO/favicon exporter (sharp + png-to-ico)
│   └── generate_showcase.py  # OPTIONAL AI showcase renders (Gemini / Nano Banana)
├── assets/
│   └── gallery_template.html # the interactive comparison + variant gallery template
├── examples/
│   └── chan-monkey/          # complete worked example — the template to copy
│       ├── handdrawn.svg     #   the original hand-drawn source
│       ├── build.py          #   per-logo config that drives the engine
│       └── out/              #   generated SVG variants (full / monkey / web)
├── package.json              # rasterize toolchain deps
├── requirements.txt          # OPTIONAL showcase-step Python deps (core needs none)
└── .env.example              # OPTIONAL showcase API config
```

### How the method works

Per closed contour: **parse** the polyline → **dedupe** → **resample** at uniform arc
length → **lightly smooth** out hand jitter → fit a **closed Catmull-Rom spline** →
emit it as exact **cubic Bézier** segments. The fit interpolates every sample point and
is everywhere C¹, so it hugs the drawing while staying smooth. Truly circular parts
(eyes, dots) become exact `<circle>`s. Inner contours become see-through **holes** via
the `even-odd` fill rule. See [`references/method.md`](references/method.md).

### Review gallery & fidelity check

The craft is in **step 4 — comparing the reconstruction to the original and tuning**.
`scripts/build_gallery.py` builds a self-contained `gallery.html` that makes this concrete:

- **Side-by-side / Overlay / Difference** views of the original vs the fitted mark. In
  *Difference* mode, perfectly-aligned ink cancels to black and any deviation **glows** —
  a pure-CSS visual diff. An opacity slider onion-skins the two in *Overlay*.
- A **per-contour tuning table** (`resample_step`, `smoothing_passes`) plus real
  reconstruction stats (contour, Bézier-segment, and circle counts) so a visible wobble
  maps straight to the knob to turn.
- The full **variant matrix** and any showcase renders, in one polished page.

Spot a deviation → find its contour in the table → lower its `step`/`passes` → re-run
`build.py` and `build_gallery.py`. Repeat until faithful.

### Variants & theme-adaptive SVG

One math definition fans out the whole brand matrix — ink color × background
(color / transparent) × layout (full lockup / mark only). You can also emit a single
**`currentColor`** SVG whose ink follows the host's CSS `color` (great with
`prefers-color-scheme` for automatic dark/light). It's *additive* — it collapses only the
ink axis and works only when the SVG is inlined — so it complements the explicit matrix
rather than replacing it. See [`references/layer-structure.md`](references/layer-structure.md).

### Showcase images (optional)

Once you have a rasterized variant, `scripts/generate_showcase.py` can composite the mark —
**faithfully, never redrawn** — onto one of **12 curated premium backgrounds** (Gemini /
Nano Banana image generation), with Swiss-style micro-typography. This is the one step
that needs external dependencies and an API key; everything else is dependency-free. See
[`references/showcase-styles.md`](references/showcase-styles.md).

### Quality checklist

Before delivering, walk [`references/quality-checklist.md`](references/quality-checklist.md):
a fidelity gate covering curve sanity, holes, circles, variant consistency, and that
neither the rasters nor the AI showcase silently altered the mark.

### Try the example

```bash
# 1) regenerate the monkey SVG variants (Python stdlib only — no install needed)
python examples/chan-monkey/build.py

# 2) build the interactive review gallery, then open examples/chan-monkey/gallery.html
python scripts/build_gallery.py

# 3) rasterize to PNG / ICO / favicon
npm install
npm run rasterize
```

The example reproduces the published Chan Meng logo assets exactly.

### Optional dependencies

The **core is `python` standard library only** — vectorizing, the variant matrix, and the
review gallery need nothing installed. Two steps are optional add-ons:

| Step | Needs |
|---|---|
| Rasterize (PNG/ICO/favicon) | Node.js + `npm install` (sharp, png-to-ico) |
| AI showcase renders | `pip install -r requirements.txt` + a Gemini API key in `.env` |

The showcase script fails gracefully with a clear message if its deps or key are missing,
so the rest of the skill is never blocked.

### Install as a Claude Code skill

Copy or symlink this repo into your skills directory so Claude can invoke it on demand:

```powershell
# Windows (PowerShell) — symlink keeps it updated with this repo
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.claude\skills\vectorizing-handdrawn-logos" `
  -Target "D:\github_repository\logo-as-code-skill"
```

```bash
# macOS / Linux
ln -s /path/to/logo-as-code-skill ~/.claude/skills/vectorizing-handdrawn-logos
```

Then in any session, a request like *"turn this hand-drawn logo into an SVG with color
variants and favicons"* triggers the skill, and Claude follows the workflow in
[`SKILL.md`](SKILL.md).

### License

MIT for the code. The Chan Meng monkey logo and "CHAN" wordmark in `examples/` are a
personal brand identity — study the technique, but please don't reuse the mark itself.

---

## 中文

手绘 logo 很有韵味，却**无法度量**——它要么是一张位图，要么是一份由几百个手工放置的点组成
的 SVG：看着平滑，实则粗糙、无法编辑、也并非真正可缩放。本技能把每条轮廓拟合成一小组
**平滑的三次贝塞尔曲线**（真正的参数化多项式），并且是*沿着原始轮廓*拟合，因此手绘的神韵
得以保留，而结果却是完全数学化的：可复现、可无限缩放、可参数化微调、可在 git 中 diff。

它把为
[Chan Meng 个人品牌 logo](https://github.com/ChanMeng666/chan-meng-personal-brand-logo)
开发的方法加以泛化：一个由几百个手工点构成的手绘标识，被重建为一小组真正的参数化多项式曲线
——可复现、可无限缩放、可参数化微调，同时保留原作的手绘character。本技能把这条流水线封装起来，
使其可应用于**任意** logo。

> **本技能是*重建*一份已有的手绘稿，而非从零*生成*全新的 logo 设计。** 照片类图像、以及本就
> 干净的矢量文件，均不在适用范围内。

### 目录结构

```
logo-as-code-skill/
├── SKILL.md                  # 技能本体：何时使用 + 分步工作流
├── references/
│   ├── method.md             # 数学方法（Catmull-Rom → 三次贝塞尔）
│   ├── layer-structure.md    # 轮廓角色、镂空、even-odd 挖洞、currentColor
│   ├── tuning-guide.md       # 如何选择 (resample_step, smoothing_passes)
│   ├── bitmap-input.md       # 先把 扫描/照片 → 折线 SVG（potrace）
│   ├── quality-checklist.md  # 交付前要走一遍的保真度检查清单
│   └── showcase-styles.md    # AI 展示图的 12 种高级背景（可选）
├── scripts/
│   ├── vectorize.py          # 通用引擎（仅用 Python 标准库）——不为单个 logo 修改
│   ├── build_gallery.py      # 通用「评审画廊」生成器（仅标准库）
│   ├── rasterize.js          # 通用 SVG → PNG/ICO/favicon 导出器（sharp + png-to-ico）
│   └── generate_showcase.py  # 可选：AI 展示图渲染（Gemini / Nano Banana）
├── assets/
│   └── gallery_template.html # 交互式「对比 + 变体」画廊模板
├── examples/
│   └── chan-monkey/          # 完整范例——可直接复制的模板
│       ├── handdrawn.svg     #   原始手绘源文件
│       ├── build.py          #   驱动引擎的单 logo 配置
│       └── out/              #   生成的 SVG 变体（full / monkey / web）
├── package.json              # 栅格化工具链依赖
├── requirements.txt          # 可选：展示图步骤的 Python 依赖（核心无需任何依赖）
└── .env.example              # 可选：展示图 API 配置
```

### 方法原理

对每条闭合轮廓：**解析**折线 → **去重** → 按均匀弧长**重采样** → 轻度**平滑**去除手抖 →
拟合一条**闭合 Catmull-Rom 样条** → 输出为精确的**三次贝塞尔**段。该拟合会经过每一个采样点，
且处处 C¹ 连续，因此既贴合手绘又保持平滑。真正是圆的部分（眼睛、圆点）输出为精确的
`<circle>`；内部轮廓通过 `even-odd` 填充规则成为可透视的**镂空**。详见
[`references/method.md`](references/method.md)。

### 评审画廊与保真度检查

真正的手艺在于**第 4 步——把重建结果与原稿对比并调参**。`scripts/build_gallery.py` 会生成一个
自包含的 `gallery.html`，把这一步落到实处：

- 原稿 vs 拟合标识的**并排 / 叠加 / 差异**三种视图。在*差异*模式下，完美对齐的墨色相互抵消为
  纯黑，任何偏差都会**发亮**——一个纯 CSS 实现的可视化 diff。*叠加*模式下用不透明度滑块做
  洋葱皮对比。
- 一张**逐轮廓调参表**（`resample_step`、`smoothing_passes`），外加真实的重建统计（轮廓数、
  贝塞尔段数、圆数），让你一眼看到的抖动直接对应到该拧的那个旋钮。
- 完整的**变体矩阵**与展示图，统统汇于一个精致页面。

发现偏差 → 在表中找到对应轮廓 → 调低它的 `step`/`passes` → 重新运行 `build.py` 与
`build_gallery.py`，如此往复直到忠实为止。

### 变体与主题自适应 SVG

一份数学定义即可展开整套品牌矩阵——墨色 × 背景（颜色 / 透明）× 版式（完整组合 / 仅标识）。
你还可以输出单个 **`currentColor`** SVG，其墨色跟随宿主的 CSS `color`（配合
`prefers-color-scheme` 可自动深/浅色）。它是*增量*能力——只折叠墨色这一维，且仅在 SVG 被内联
时生效——因此是对显式矩阵的补充，而非替代。详见
[`references/layer-structure.md`](references/layer-structure.md)。

### 展示图（可选）

拿到栅格化的变体后，`scripts/generate_showcase.py` 可把标识——**忠实地、绝不重画**——合成到
**12 种精选高级背景**之一（Gemini / Nano Banana 图像生成），并配以瑞士风格的微排版。这是唯一
需要外部依赖与 API key 的步骤；其余一切都无需依赖。详见
[`references/showcase-styles.md`](references/showcase-styles.md)。

### 质量检查清单

交付前请走一遍 [`references/quality-checklist.md`](references/quality-checklist.md)：一道保真度
关卡，覆盖曲线合理性、镂空、圆、变体一致性，以及确认栅格图与 AI 展示图都没有悄悄改动标识。

### 试运行范例

```bash
# 1) 重新生成 monkey 的 SVG 变体（仅 Python 标准库，无需安装）
python examples/chan-monkey/build.py

# 2) 构建交互式评审画廊，然后打开 examples/chan-monkey/gallery.html
python scripts/build_gallery.py

# 3) 栅格化为 PNG / ICO / favicon
npm install
npm run rasterize
```

范例会精确复现已发布的 Chan Meng logo 资产。

### 可选依赖

**核心仅依赖 `python` 标准库**——矢量化、变体矩阵、评审画廊都无需安装任何东西。只有两个步骤是
可选附加项：

| 步骤 | 需要 |
|---|---|
| 栅格化（PNG/ICO/favicon） | Node.js + `npm install`（sharp、png-to-ico） |
| AI 展示图渲染 | `pip install -r requirements.txt` + 在 `.env` 中配置 Gemini API key |

若展示图脚本缺少依赖或 key，会以清晰的提示优雅退出，因此绝不会阻塞技能的其余部分。

### 安装为 Claude Code 技能

把本仓库复制或软链接到你的 skills 目录，Claude 即可按需调用：

```powershell
# Windows（PowerShell）——软链接可随本仓库自动更新
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.claude\skills\vectorizing-handdrawn-logos" `
  -Target "D:\github_repository\logo-as-code-skill"
```

```bash
# macOS / Linux
ln -s /path/to/logo-as-code-skill ~/.claude/skills/vectorizing-handdrawn-logos
```

随后在任意会话中，一句*“把这张手绘 logo 变成带配色变体和 favicon 的 SVG”*即可触发本技能，
Claude 会按照 [`SKILL.md`](SKILL.md) 中的工作流执行。

### 许可

代码采用 MIT 许可。`examples/` 中的 Chan Meng 猴子标识与 “CHAN” 字标属于个人品牌标识——
欢迎研究其技法，但请勿直接复用该标识本身。
