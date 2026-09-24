# Brand Style Guide — v0.4 (draft)

> Status: **developing**. This guide starts small and gets extended as decisions
> are made. Anything marked *provisional* has not been decided yet.

## 1. Logo

### XLRTE (company brand)

**XLRTE** reads as *accelerate*. The wordmark is set in Jost Medium with 6 % letter
spacing, converted to outlines. The left half of the X is a forward chevron in
vermilion, split from the rest by a hairline gap: an arrow hidden in the first
letter, pointing into the name. Everything else stays in ink. Understatement is
the point: one accent, no decoration.

| File | Use |
|---|---|
| `logo/xlrte-color.svg` | Default, on white or light backgrounds |
| `logo/xlrte-white.svg` | On ink, dark photos, the dark title slide |
| `logo/xlrte-black.svg` | Single colour: print, stamps, fax, embossing |
| `logo/xlrte-mono-white.svg` | Single colour on vermilion or busy backgrounds |
| `logo/x-monogram.svg`, `favicon.ico`, `favicon-16/32.png`, `apple-touch-icon.png` | Favicons, app icons, social avatars |

PNG versions sit next to each SVG. Use the SVG wherever possible.

### P·E (personal mark)

Your initials, **P** (human: round, open) and **E** (machine: straight, modular),
overlap slightly. Both letters are ink. Only the area they share is vermilion:
the spark of human–machine interaction. Use it for your signature, profile and
author line. XLRTE remains the company brand.

Files: `logo/pe-color.svg`, `pe-white.svg`, `pe-black.svg`, `pe-mono-white.svg`. In the
single-colour versions the spark becomes a cut-out.

### Rules

- **Clear space:** keep free space of at least **half the letter height** on all
  sides. Nothing else may enter it.
- **Minimum size:** letter height 16 px on screen (wordmark about 90 px wide),
  6 mm in print. Below that, use the X monogram.
- **Together:** XLRTE first, P·E after it, separated by a thin `line` rule and with
  both at the same letter height.
- **Backgrounds:** white or ink. On vermilion, use the single-colour versions.
  On photos, use white, and only where the image is calm.

**Don't**

- recolour the chevron or the spark, or add a second accent colour
- set XLRTE in live text: always use the logo files
- change the letter spacing, stretch, rotate, outline or add shadows
- place the colour logo on vermilion (the chevron disappears)
- combine XLRTE and P·E into one mark

## 2. Typography

### The core problem

Futura and Avenir are **commercial fonts** (Futura: Neufville/URW/Linotype;
Avenir / Avenir Next: Linotype/Monotype). **Google Workspace (Docs, Slides,
Sheets, Drawings) cannot use custom or uploaded fonts** — only the Google Fonts
library. If a PPTX or DOCX set in Futura/Avenir is opened in Google Slides/Docs,
the text silently falls back to a default (usually Arial) and layouts shift.

### The solution: two tiers, one look

| Tier | Where | Headline | Body |
|---|---|---|---|
| **Master** (licensed) | Keynote, PowerPoint, Word, InDesign, Figma, PDF exports made on a Mac with the fonts | **Futura PT** / Futura (Medium, Bold) | **Avenir Next** (Regular, Medium, Demi) |
| **Workspace** (free, Google Fonts) | Google Slides, Docs, Sheets, Drawings, web, diagrams | **Jost** (Regular, Bold) | **Nunito Sans** (Regular, Bold) |

- **Jost** is an open-source typeface explicitly modelled on Futura.
- **Nunito Sans** is the closest free match to Avenir's humanist-geometric feel
  (alternative: *Figtree*).

**Rule of thumb:** anything *staged or collaborated on in Google Workspace* uses
the Workspace tier from the start. Only the final, polished export (PDF) may be
re-set in the Master tier — or simply stay in Jost/Nunito Sans. Consistency beats
the original typeface.

Stick to Regular and Bold: they carry over reliably when files move between
PowerPoint, Word and Google Workspace. Medium/SemiBold weights may not.

> Recommendation for a lean workflow: **use the Workspace tier as the default
> everywhere.** Keep the Master tier for print and special occasions.

### Type scale (Slides, 16:9)

| Role | Font | Weight | Size | Case / tracking |
|---|---|---|---|---|
| Title | Jost | Bold | 40 pt | Sentence case |
| Section label | Jost | Regular | 14 pt | UPPERCASE, wide letter spacing |
| Slide headline | Jost | Bold | 28 pt | Sentence case |
| Subtitle | Nunito Sans | Regular | 18 pt | Sentence case |
| Body | Nunito Sans | Regular | 16 pt | line spacing 1.3 |
| Caption / source | Nunito Sans | Regular | 11 pt | muted colour |

### Type scale (Docs, A4)

| Role | Font | Weight | Size |
|---|---|---|---|
| Title | Jost | Bold | 26 pt |
| Heading 1 | Jost | Bold | 18 pt |
| Heading 2 | Jost | Bold | 14 pt |
| Heading 3 | Jost, `accent_text` colour | Bold | 11 pt |
| Normal text | Nunito Sans | Regular | 11 pt, line spacing 1.3 |
| Caption | Nunito Sans | Regular | 9 pt |

## 3. Colour

Neutral base plus **one** accent: a warm vermilion that echoes the geometric,
Bauhaus-era roots of Futura. Use it sparingly — roughly 10 % of any page or slide.

| Token | Hex | Use |
|---|---|---|
| `ink` | `#1A1A1A` | Text, headlines |
| `paper` | `#FFFFFF` | Backgrounds |
| `muted` | `#6B6B6B` | Captions, secondary text |
| `line` | `#E3E3E3` | Rules, table borders |
| `accent` | `#E4572E` | Brand colour: title-slide mark, section slides, big numbers, the one highlighted diagram element |
| `accent_text` | `#C4421D` | Small accent text on white (labels, links, doc sub-headings) |

**Contrast rule.** `accent` on white is 3.7 : 1 — fine for shapes and large text
(≥ 18 pt bold or ≥ 24 pt), too light for small text. For anything smaller use
`accent_text` (5.1 : 1, meets WCAG AA). White text on an `accent` background
only at ≥ 18 pt bold; `ink` on `accent` works at any size (4.7 : 1).

## 4. Charts & diagrams

Charts use the same two typefaces and the same accent. Colours below were checked
with a colour-vision-deficiency validator (adjacent series stay distinguishable
for the common forms of colour blindness), in light and dark.

### Highlight first, palette second

Most charts should be **grey plus one accent**: the series or bar you are talking
about in `accent`, everything else in `neutral_series` `#BDBDBD`. Reach for the
full palette only when several series really need their own identity.

### Series colours (categorical)

Always assign in this order, never skip or shuffle. Slot 1 is the brand accent.

| Slot | Light | Dark | Hue |
|---|---|---|---|
| 1 | `#E4572E` | `#E4572E` | vermilion (accent) |
| 2 | `#2A78D6` | `#3987E5` | blue |
| 3 | `#1BAF7A` | `#199E70` | aqua |
| 4 | `#EDA100` | `#C98500` | ochre |
| 5 | `#4A3AA7` | `#9085E9` | violet |
| 6 | `#E87BA4` | `#D55181` | pink |
| 7 | `#008300` | `#008300` | green |

- **Lines, bars, stacks:** up to 7 series. More than 7 → group the rest as "Other"
  or split into small charts.
- **Scatter plots, maps, anything where every colour sits next to every other:**
  max **3** series (slot 4 ochre is too close to the vermilion accent there).
- Slots 3, 4 and 6 are light on white: label those series directly or add a table.
- A series keeps its colour when filters change; colour follows the thing, not its rank.

### Magnitude (sequential) and above/below (diverging)

- **Sequential** (heatmaps, "how much"): one hue, vermilion from light to dark:
  `#FBE3DA` `#F6C3B1` `#F0A084` `#EA7B55` `#E4572E` `#C4421D` `#9C3417` `#742712`.
  For discrete ordered steps (tiers, funnel stages) start at `#F0A084` or darker.
- **Diverging** (above/below target, gain/loss): blue ← grey `#EFEFEF` → vermilion.
  Blue arm `#1F5FAD` `#2A78D6` `#86B3EA` `#B3CFF2`; vermilion arm `#F6C3B1`
  `#F0A084` `#E4572E` `#C4421D`. The midpoint is always grey.

### Chart anatomy

- One y-axis only; never two scales on one chart.
- Gridlines hairline `#E3E3E3`, axis line `#BDBDBD`, labels Nunito Sans 11 pt in `muted`.
- Chart title = the takeaway, in Jost Bold; source line in caption style.
- Values and labels are set in ink/muted text colours, not in the series colour.
- Legend whenever there are 2+ series; with 4 or fewer, also label the lines directly.
- Status colours (good / warning / critical) are *not* series colours; if you need
  them, pair them with an icon and a word.

### Diagrams

- Flat shapes, 1 px strokes in `ink`, labels in Nunito Sans, titles in Jost.
- Fill: `paper` (white) by default; the one element that matters in `accent` with
  white bold text (≥ 14 pt).
- Grouping: a light grey panel (`#F4F4F4`), not coloured borders.
- If a diagram needs categories, use series slots 2 and 3 (blue, aqua) —
  keep vermilion for the highlight.

## 5. Layout principles (starting set)

1. One idea per slide; a headline that states the takeaway.
2. Generous white space — margins ≥ 5 % of slide width.
3. Left-aligned text; no centred body copy.
4. Max two typefaces (Jost + Nunito Sans). No third font.
5. Diagrams: flat shapes, 1 px `line` strokes, labels in Nunito Sans, accent colour
   for the single element that matters.

## 6. Setting it up in Google Workspace

**Google Slides — create a master theme once**

1. New presentation → *Slide → Edit theme*.
2. Font menu → *More fonts* → add **Jost** and **Nunito Sans**.
3. Set the Title placeholder to Jost Bold, body placeholders to Nunito Sans.
4. *Theme colours* → Accent 1 `#E4572E`, Dark 1 `#1A1A1A`, Light 1 `#FFFFFF`.
5. Rename the theme (e.g. "Brand v0.2"), save the file as `TEMPLATE – Slides`.
   New decks: *File → Make a copy*, or *Slide → Change theme → Import theme*.

**Google Docs — set default styles**

1. Format the Title / H1 / H2 / Normal text as in the table above.
2. For each: *Format → Paragraph styles → [style] → Update to match*.
3. *Options → Save as my default styles* — every new Doc now uses them.

**Diagrams** (Google Drawings, Excalidraw, Mermaid, etc.): use Jost for titles,
Nunito Sans for labels; export as SVG/PNG and place into Slides/Docs.

**PPTX / DOCX files coming from outside:** before importing into Workspace,
replace Futura → Jost and Avenir → Nunito Sans (PowerPoint: *Home → Replace →
Replace Fonts*), then upload.

## 7. Templates

| File | Use |
|---|---|
| `templates/brand-slides-template.pptx` | Upload to Drive, then open as Google Slides. Includes Title, Section and Content layouts plus example slides |
| `templates/brand-docs-template.docx` | Upload to Drive, then open as Google Docs. Heading styles are pre-set and the file contains this guide |
| `templates/build_slides.js`, `templates/build_docs.py` | Rebuild the templates from `tokens.json` and this guide |

On GitHub, the **Build brand templates** workflow reruns both scripts whenever
`tokens.json`, this guide or the build scripts change, and commits the fresh
templates. Locally: `cd brand/templates && npm ci && pip install -r requirements.txt`,
then `node build_slides.js && python3 build_docs.py`.

## 8. Licensing note

Futura and Avenir Next ship with macOS, but that licence covers use on that Mac —
not web embedding or redistribution. Jost and Nunito Sans are under the SIL Open
Font License: free for any use, including commercial and embedding.

## Changelog

- **v0.4** — Logo: XLRTE wordmark with forward chevron, X monogram and favicons, P·E personal mark.
- **v0.3** — Chart & diagram colours (validated for colour-blind readers), chart anatomy rules.
- **v0.2** — Accent `#E4572E` confirmed as brand colour; added `accent_text` and contrast rule.
- **v0.1** — Typography tiers, type scales, provisional accent, Workspace setup, Slides + Docs templates.
