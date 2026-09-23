# Brand Style Guide — v0.1 (draft)

> Status: **developing**. This guide starts small and gets extended as decisions
> are made. Anything marked `TBD` has not been decided yet.

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
| **Workspace** (free, Google Fonts) | Google Slides, Docs, Sheets, Drawings, web, diagrams | **Jost** (500, 600, 700) | **Nunito Sans** (400, 600, 700) |

- **Jost** is an open-source typeface explicitly modelled on Futura.
- **Nunito Sans** is the closest free match to Avenir's humanist-geometric feel
  (alternative: *Figtree*).

**Rule of thumb:** anything *staged or collaborated on in Google Workspace* uses
the Workspace tier from the start. Only the final, polished export (PDF) may be
re-set in the Master tier — or simply stay in Jost/Nunito Sans. Consistency beats
the original typeface.

> Recommendation for a lean workflow: **use the Workspace tier as the default
> everywhere.** Keep the Master tier for print and special occasions.

### Type scale (Slides, 16:9)

| Role | Font | Weight | Size | Case / tracking |
|---|---|---|---|---|
| Title | Jost | 600 | 40 pt | Sentence case, 0 |
| Section header | Jost | 500 | 28 pt | UPPERCASE, +5 % letter spacing |
| Subtitle | Nunito Sans | 400 | 20 pt | Sentence case |
| Body | Nunito Sans | 400 | 16 pt | line spacing 1.3 |
| Caption / source | Nunito Sans | 400 | 11 pt | muted colour |

### Type scale (Docs, A4)

| Role | Font | Weight | Size |
|---|---|---|---|
| Title | Jost | 600 | 26 pt |
| Heading 1 | Jost | 600 | 18 pt |
| Heading 2 | Jost | 500 | 14 pt |
| Normal text | Nunito Sans | 400 | 11 pt, line spacing 1.3 |
| Caption | Nunito Sans | 400 | 9 pt |

## 2. Colour — `TBD`

Placeholder palette until brand colours are chosen. Keep it to one accent.

| Token | Hex | Use |
|---|---|---|
| `ink` | `#1A1A1A` | Text, headlines |
| `paper` | `#FFFFFF` | Backgrounds |
| `muted` | `#6B6B6B` | Captions, secondary text |
| `line` | `#E3E3E3` | Rules, table borders |
| `accent` | `TBD` | One brand colour — highlights, key numbers |

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
3. Set the Title placeholder to Jost 600, body placeholders to Nunito Sans.
4. *Theme colours* → enter the palette above.
5. Rename the theme (e.g. "Brand v0.1"), save the file as `TEMPLATE – Slides`.
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

## 5. Licensing note

Futura and Avenir Next ship with macOS, but that licence covers use on that Mac —
not web embedding or redistribution. Jost and Nunito Sans are under the SIL Open
Font License: free for any use, including commercial and embedding.

## Changelog

- **v0.1** — Typography tiers, type scales, placeholder palette, Workspace setup.
