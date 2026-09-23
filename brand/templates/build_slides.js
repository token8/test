// Builds brand-slides-template.pptx — upload to Google Drive (converts to Google Slides).
// Fonts are Google Fonts so they survive the conversion. Values mirror ../tokens.json.
const pptxgen = require("pptxgenjs");
const t = require("../tokens.json");

const H = t.font.heading.workspace, B = t.font.body.workspace;
const C = Object.fromEntries(Object.entries(t.color).map(([k, v]) => [k, v.replace("#", "")]));
const M = 0.6; // outer margin (inches)

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.title = "Brand Slides Template v0.2";
pres.theme = { headFontFace: H, bodyFontFace: B };

const footer = (color) => ({ text: { text: "BRAND · v0.2", options: {
  x: M, y: 5.1, w: 3, h: 0.3, margin: 0, fontFace: H, fontSize: 9, charSpacing: 2, color } } });

pres.defineSlideMaster({ title: "Title", background: { color: C.ink }, objects: [
  { placeholder: { options: { name: "title", type: "title", x: M, y: 1.6, w: 8.2, h: 1.4, align: "left",
    fontFace: H, fontSize: 40, bold: true, color: C.paper, valign: "bottom", margin: 0 }, text: "" } },
  { placeholder: { options: { name: "subtitle", type: "body", x: M, y: 3.15, w: 8.2, h: 0.8,
    fontFace: B, fontSize: 18, color: "BDBDBD", valign: "top", margin: 0 }, text: "" } },
  { rect: { x: M, y: 1.2, w: 0.28, h: 0.28, fill: { color: C.accent } } },
  footer("8A8A8A") ] });

pres.defineSlideMaster({ title: "Section", background: { color: C.accent }, objects: [
  { placeholder: { options: { name: "label", type: "body", x: M, y: 1.7, w: 6, h: 0.4,
    fontFace: H, fontSize: 14, charSpacing: 4, color: C.ink, margin: 0 }, text: "" } },
  { placeholder: { options: { name: "title", type: "title", x: M, y: 2.1, w: 8.2, h: 1.4, align: "left",
    fontFace: H, fontSize: 36, bold: true, color: C.paper, valign: "top", margin: 0 }, text: "" } },
  footer(C.ink) ] });

pres.defineSlideMaster({ title: "Content", background: { color: C.paper }, objects: [
  { placeholder: { options: { name: "title", type: "title", x: M, y: 0.45, w: 8.8, h: 0.9, align: "left",
    fontFace: H, fontSize: 28, bold: true, color: C.ink, valign: "top", margin: 0 }, text: "" } },
  { placeholder: { options: { name: "body", type: "body", x: M, y: 1.5, w: 8.8, h: 3.4,
    fontFace: B, fontSize: 16, color: C.ink, valign: "top", margin: 0 }, text: "" } },
  footer(C.muted) ], slideNumber: { x: 9.0, y: 5.1, w: 0.4, h: 0.3, fontFace: H, fontSize: 9, color: C.muted, align: "right" } });

const txt = (s, text, o) => s.addText(text, { isTextBox: true, margin: 0, fontFace: B, color: C.ink, valign: "top", ...o });

// 1 — Title
let s = pres.addSlide({ masterName: "Title" });
s.addText("Presentation title in sentence case", { placeholder: "title" });
s.addText("Subtitle — context, audience or date", { placeholder: "subtitle" });

// 2 — Section divider
s = pres.addSlide({ masterName: "Section" });
s.addText("01 — SECTION", { placeholder: "label" });
s.addText("A section header that frames what comes next", { placeholder: "title" });

// 3 — Headline + bullets with side note
s = pres.addSlide({ masterName: "Content" });
s.addText("The headline states the takeaway, not the topic", { placeholder: "title" });
txt(s, [
  { text: "One idea per slide — split if it needs a second headline", options: { bullet: true, breakLine: true } },
  { text: "Body in Nunito Sans 16 pt, left-aligned", options: { bullet: true, breakLine: true } },
  { text: "Accent colour for the one thing that matters", options: { bullet: true } },
], { x: M, y: 1.5, w: 5.2, h: 2.6, fontSize: 16, paraSpaceAfter: 10 });
s.addShape(pres.shapes.RECTANGLE, { x: 6.3, y: 1.5, w: 3.1, h: 1.9, fill: { color: "F4F4F4" } });
txt(s, "NOTE", { x: 6.55, y: 1.75, w: 2.6, h: 0.3, fontFace: H, fontSize: 11, charSpacing: 3, color: C.accent_text });
txt(s, "Use a tinted panel — not a stripe — to set supporting information apart.",
  { x: 6.55, y: 2.1, w: 2.6, h: 1.2, fontSize: 13, color: C.muted });

// 4 — Big numbers
s = pres.addSlide({ masterName: "Content" });
s.addText("Key numbers get room to breathe", { placeholder: "title" });
[["42%", "Headline stat in Jost, accent colour"], ["3×", "Comparison or multiplier"], ["12", "Count with a short label"]]
  .forEach(([n, l], i) => {
    const x = M + i * 3.0;
    txt(s, n, { x, y: 1.9, w: 2.7, h: 1.1, fontFace: H, fontSize: 60, bold: true, color: i === 0 ? C.accent : C.ink });
    txt(s, l, { x, y: 3.1, w: 2.5, h: 0.7, fontSize: 13, color: C.muted });
  });

// 5 — Process diagram
s = pres.addSlide({ masterName: "Content" });
s.addText("Diagrams: flat shapes, thin lines, one accent", { placeholder: "title" });
["Discover", "Define", "Design", "Deliver"].forEach((step, i) => {
  const x = M + i * 2.25, active = i === 2;
  s.addShape(pres.shapes.RECTANGLE, { x, y: 2.1, w: 1.85, h: 1.1,
    fill: { color: active ? C.accent : C.paper }, line: { color: active ? C.accent : C.ink, width: 1 } });
  txt(s, step, { x, y: 2.1, w: 1.85, h: 1.1, fontFace: H, fontSize: 16, bold: true,
    align: "center", valign: "middle", color: active ? C.paper : C.ink });
  txt(s, `0${i + 1}`, { x, y: 1.7, w: 1.85, h: 0.3, fontFace: H, fontSize: 11, charSpacing: 3, color: C.muted });
  if (i < 3) s.addShape(pres.shapes.LINE, { x: x + 1.9, y: 2.65, w: 0.3, h: 0, line: { color: C.ink, width: 1, endArrowType: "triangle" } });
});
txt(s, "Highlight only the step you are talking about.", { x: M, y: 3.6, w: 8, h: 0.4, fontSize: 13, color: C.muted });

// 6 — Type & colour reference
s = pres.addSlide({ masterName: "Content" });
s.addText("Type & colour reference", { placeholder: "title" });
txt(s, "Jost Bold — Headlines", { x: M, y: 1.5, w: 5, h: 0.5, fontFace: H, fontSize: 24, bold: true });
txt(s, "JOST — SECTION LABELS", { x: M, y: 2.1, w: 5, h: 0.4, fontFace: H, fontSize: 14, charSpacing: 4 });
txt(s, "Nunito Sans — body text for slides, documents and diagram labels. Readable at small sizes.",
  { x: M, y: 2.6, w: 4.8, h: 0.8, fontSize: 14 });
txt(s, "Master tier (print / licensed): Futura PT + Avenir Next", { x: M, y: 3.6, w: 4.8, h: 0.4, fontSize: 11, color: C.muted });
[["ink", C.ink], ["accent", C.accent], ["accent text", C.accent_text], ["muted", C.muted], ["line", C.line]].forEach(([n, c], i) => {
  const y = 1.45 + i * 0.68;
  s.addShape(pres.shapes.RECTANGLE, { x: 6.4, y, w: 0.5, h: 0.5, fill: { color: c }, line: { color: C.line, width: 0.75 } });
  txt(s, `${n}  #${c}`, { x: 7.05, y: y + 0.1, w: 2.3, h: 0.3, fontFace: H, fontSize: 12 });
});

// 7 — Closing
s = pres.addSlide({ masterName: "Title" });
s.addText("Thank you", { placeholder: "title" });
s.addText("name@example.com · website", { placeholder: "subtitle" });

const out = __dirname + "/brand-slides-template.pptx";
// pptxgenjs stores parts uncompressed; re-deflate so the file is ~4x smaller to upload.
pres.write({ outputType: "nodebuffer" })
  .then(buf => require("jszip").loadAsync(buf))
  .then(zip => zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE", compressionOptions: { level: 9 } }))
  .then(buf => { require("fs").writeFileSync(out, buf); console.log("wrote", out); });
