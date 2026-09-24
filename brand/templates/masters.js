// Shared brand slide masters and helpers: used by the template and by every deck.
// Values come from ../tokens.json; logos from ../logo (PNG, since Google Slides does not import SVG).
const pptxgen = require("pptxgenjs");
const t = require("../tokens.json");

const H = t.font.heading.workspace, B = t.font.body.workspace;
const C = Object.fromEntries(Object.entries(t.color).map(([k, v]) => [k, v.replace("#", "")]));
const M = 0.6; // outer margin (inches)
const LOGO = (file) => __dirname + "/../logo/" + file;
const logoW = (h) => h * (1709 / 400); // wordmark aspect ratio (width / height of the PNGs)

function createDeck(title) {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
  pres.title = title;
  pres.theme = { headFontFace: H, bodyFontFace: B };

  const footer = (file) => ({ image: { x: M, y: 5.12, h: 0.14, w: logoW(0.14), path: LOGO(file), altText: "XLRTE" } });

  pres.defineSlideMaster({ title: "Title", background: { color: C.ink }, objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 1.6, w: 8.2, h: 1.4, align: "left",
      fontFace: H, fontSize: 40, bold: true, color: C.paper, valign: "bottom", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "subtitle", type: "body", x: M, y: 3.15, w: 8.2, h: 0.8,
      fontFace: B, fontSize: 18, color: "BDBDBD", valign: "top", margin: 0 }, text: "" } },
    { image: { x: M, y: 0.6, h: 0.3, w: logoW(0.3), path: LOGO("xlrte-white.png"), altText: "XLRTE" } } ] });

  pres.defineSlideMaster({ title: "Section", background: { color: C.accent }, objects: [
    { placeholder: { options: { name: "label", type: "body", x: M, y: 1.7, w: 6, h: 0.4,
      fontFace: H, fontSize: 14, charSpacing: 4, color: C.ink, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.1, w: 8.2, h: 1.4, align: "left",
      fontFace: H, fontSize: 36, bold: true, color: C.paper, valign: "top", margin: 0 }, text: "" } },
    footer("xlrte-black.png") ] });

  pres.defineSlideMaster({ title: "Content", background: { color: C.paper }, objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.45, w: 8.8, h: 0.9, align: "left",
      fontFace: H, fontSize: 28, bold: true, color: C.ink, valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 1.5, w: 8.8, h: 3.4,
      fontFace: B, fontSize: 16, color: C.ink, valign: "top", margin: 0 }, text: "" } },
    footer("xlrte-color.png") ],
    slideNumber: { x: 9.0, y: 5.1, w: 0.4, h: 0.3, fontFace: H, fontSize: 9, color: C.muted, align: "right" } });

  return pres;
}

// Text box with brand defaults.
const txt = (s, text, o) => s.addText(text, { isTextBox: true, margin: 0, fontFace: B, color: C.ink, valign: "top", ...o });

// pptxgenjs stores parts uncompressed; re-deflate so the file is ~4x smaller to upload.
function save(pres, out) {
  return pres.write({ outputType: "nodebuffer" })
    .then(buf => require("jszip").loadAsync(buf))
    .then(zip => zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE", compressionOptions: { level: 9 } }))
    .then(buf => { require("fs").writeFileSync(out, buf); console.log("wrote", out); });
}

module.exports = { tokens: t, H, B, C, M, LOGO, logoW, createDeck, txt, save };
