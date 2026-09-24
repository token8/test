# Brand Style Guide — v0.2 (draft)

> Status: **developing**. This guide starts small and gets extended as decisions
> are made. Anything marked *provisional* has not been decided yet.

## 1. Typography

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

## 2. Colour

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

## 3. Layout principles (starting set)

1. One idea per slide; a headline that states the takeaway.
2. Generous white space — margins ≥ 5 % of slide width.
3. Left-aligned text; no centred body copy.
4. Max two typefaces (Jost + Nunito Sans). No third font.
5. Diagrams: flat shapes, 1 px `line` strokes, labels in Nunito Sans, accent colour
   for the single element that matters.

## 4. Setting it up in Google Workspace

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

## 5. Templates

| File | Use |
|---|---|
| `templates/brand-slides-template.pptx` | Upload to Drive, then open as Google Slides. Includes Title, Section and Content layouts plus example slides |
| `templates/brand-docs-template.docx` | Upload to Drive, then open as Google Docs. Heading styles are pre-set and the file contains this guide |
| `templates/build_slides.js`, `templates/build_docs.py` | Rebuild the templates from `tokens.json` and this guide |

On GitHub, the **Build brand templates** workflow reruns both scripts whenever
`tokens.json`, this guide or the build scripts change, and commits the fresh
templates. Locally: `cd brand/templates && npm ci && pip install -r requirements.txt`,
then `node build_slides.js && python3 build_docs.py`.

## 6. Licensing note

Futura and Avenir Next ship with macOS, but that licence covers use on that Mac —
not web embedding or redistribution. Jost and Nunito Sans are under the SIL Open
Font License: free for any use, including commercial and embedding.

## Changelog

- **v0.2** — Accent `#E4572E` confirmed as brand colour; added `accent_text` and contrast rule.
- **v0.1** — Typography tiers, type scales, provisional accent, Workspace setup, Slides + Docs templates.
