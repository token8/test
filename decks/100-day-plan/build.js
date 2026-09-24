// 100-day plan & operating model: pitch deck for C-level stakeholders.
// Built on the brand masters; figures are illustrative until the Day-15 baseline.
const { tokens: t, H, B, C, M, LOGO, createDeck, txt, save } = require("../../brand/templates/masters");

const pres = createDeck("XLRTE: 100-day plan & operating model");
const GREY = "F4F4F4", NEUTRAL = t.chart.neutral_series.replace("#", ""), LINE = C.line;
const W = 10 - 2 * M; // content width

const note = (s, text) => txt(s, text, { x: M, y: 4.72, w: 7.6, h: 0.25, fontSize: 9, color: C.muted, italic: true });
const label = (s, text, x, y, w, color = C.accent_text) =>
  txt(s, text, { x, y, w, h: 0.28, fontFace: H, fontSize: 10, charSpacing: 3, color });

// Table helper: header row tinted, hairline borders, brand fonts.
function table(s, rows, opts) {
  const border = { type: "solid", pt: 0.75, color: LINE };
  const data = rows.map((r, i) => r.map(cell => {
    const o = typeof cell === "object" ? cell : { text: String(cell) };
    return { text: o.text, options: { fontFace: i === 0 ? H : B, bold: i === 0 || o.bold, fontSize: opts.fontSize || 10,
      color: o.color || C.ink, fill: { color: i === 0 ? GREY : C.paper }, border: [border, border, border, border],
      valign: "middle", margin: [3, 5, 3, 5], align: o.align || "left" } };
  }));
  s.addTable(data, { x: opts.x ?? M, y: opts.y, w: opts.w ?? W, colW: opts.colW, rowH: opts.rowH });
}

// 1 — Title
let s = pres.addSlide({ masterName: "Title" });
s.addText("From AI ambition to operating reality in 100 days", { placeholder: "title" });
s.addText("100-day plan & operating model · Executive Board · Example client: Nordhafen Logistik", { placeholder: "subtitle" });
s.addNotes("Open with the promise: in 100 days the board sees AI running in production under the same governance as every other service. All client names and figures in this deck are illustrative.");

// 2 — Outcomes
s = pres.addSlide({ masterName: "Content" });
s.addText("After 100 days: proof, not a PowerPoint", { placeholder: "title" });
[["3", "AI use cases live in production, each with a named business owner"],
 ["1", "operating model agreed, staffed and running under ITIL & PMI practices"],
 ["−30 %", "handling time in the pilot process, measured weekly against baseline"]].forEach(([n, l], i) => {
  const x = M + i * 3.0;
  txt(s, n, { x, y: 1.75, w: 2.8, h: 1.0, fontFace: H, fontSize: 54, bold: true, color: i === 2 ? C.accent : C.ink });
  txt(s, l, { x, y: 2.85, w: 2.55, h: 0.9, fontSize: 13, color: C.muted });
});
note(s, "Illustrative targets. Confirmed at Gate 1 (Day 15) once the baseline is measured.");

// 3 — Principles
s = pres.addSlide({ masterName: "Content" });
s.addText("Trust comes from visibility, not from promises", { placeholder: "title" });
[["01", "One plan, one owner", "Executive sponsor, steering committee and three stage gates (PMI). Every decision has a date and an owner."],
 ["02", "Service before technology", "Each AI use case becomes a managed service with an owner, service levels and a change path (ITIL)."],
 ["03", "Humans stay in the loop", "AI proposes, people decide. Every automated decision is explainable, reviewable and reversible."],
 ["04", "Measured every week", "One scorecard for value, service, delivery and adoption, from Day 15 until handover."]].forEach(([n, h, d], i) => {
  const x = M + (i % 2) * 4.5, y = 1.45 + Math.floor(i / 2) * 1.62;
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.3, h: 1.45, fill: { color: GREY }, line: { color: GREY } });
  label(s, n, x + 0.25, y + 0.2, 0.6);
  txt(s, h, { x: x + 0.25, y: y + 0.45, w: 3.8, h: 0.35, fontFace: H, fontSize: 15, bold: true });
  txt(s, d, { x: x + 0.25, y: y + 0.8, w: 3.85, h: 0.6, fontSize: 11, color: C.muted });
});

// 4 — Section
s = pres.addSlide({ masterName: "Section" });
s.addText("01 — THE PLAN", { placeholder: "label" });
s.addText("Four phases, three decision gates, one steering rhythm", { placeholder: "title" });

// 5 — Timeline
s = pres.addSlide({ masterName: "Content" });
s.addText("100 days, four phases, three board decisions", { placeholder: "title" });
const phases = [
  { name: "Mobilise", d0: 0, d1: 15, pts: ["Sponsor & steering set up", "Stakeholder interviews", "Baseline measured"] },
  { name: "Diagnose & design", d0: 15, d1: 45, pts: ["Use-case portfolio ranked", "Target operating model", "Data & risk assessment"] },
  { name: "Pilot & prove", d0: 45, d1: 80, pts: ["3 pilots in production", "Services onboarded (ITIL)", "Weekly value tracking"], hi: true },
  { name: "Scale & hand over", d0: 80, d1: 100, pts: ["Roadmap for next 12 months", "Team trained", "Run handed to owners"] }];
const X0 = M, SCALE = W / 100, BAR_Y = 1.75;
phases.forEach(p => {
  const x = X0 + p.d0 * SCALE, w = (p.d1 - p.d0) * SCALE - 0.06;
  s.addShape(pres.shapes.RECTANGLE, { x, y: BAR_Y, w, h: 0.55, fill: { color: p.hi ? C.accent : C.paper },
    line: { color: p.hi ? C.accent : C.ink, width: 1 } });
  txt(s, p.name, { x: x + 0.1, y: BAR_Y, w: w - 0.15, h: 0.55, fontFace: H, fontSize: 12, bold: true, valign: "middle",
    color: p.hi ? C.paper : C.ink });
  txt(s, `Day ${p.d0 === 0 ? 1 : p.d0 + 1}–${p.d1}`, { x, y: BAR_Y - 0.32, w, h: 0.25, fontSize: 10, color: C.muted });
  txt(s, p.pts.map((b, i) => ({ text: b, options: { bullet: { indent: 10 }, breakLine: i < p.pts.length - 1 } })),
    { x, y: BAR_Y + 0.75, w: Math.max(w, 1.3), h: 1.2, fontSize: 10, paraSpaceAfter: 4 });
});
[15, 45, 80].forEach((d, i) => {
  const x = X0 + d * SCALE - 0.03;
  s.addShape(pres.shapes.LINE, { x, y: BAR_Y + 0.6, w: 0, h: 1.85, line: { color: C.ink, width: 0.75, dashType: "dash" } });
  txt(s, `Gate ${i + 1}`, { x: x - 0.45, y: 4.28, w: 0.9, h: 0.25, fontFace: H, fontSize: 10, bold: true, align: "center" });
});
s.addNotes("Gates follow PMI stage-gate practice: the steering committee decides go / adjust / stop at Days 15, 45 and 80.");

// 6 — Phase table
s = pres.addSlide({ masterName: "Content" });
s.addText("Deliverables and decisions per phase", { placeholder: "title" });
table(s, [
  ["Phase", "Key deliverables", "Board decision at the gate"],
  [{ text: "Mobilise  ·  Day 1–15", bold: true }, "Project charter, stakeholder map, RACI, KPI baseline", "Gate 1: confirm scope, targets and budget envelope"],
  [{ text: "Diagnose & design  ·  16–45", bold: true }, "Ranked use-case portfolio, target operating model, risk & compliance assessment", "Gate 2: select 3 pilots, approve operating model"],
  [{ text: "Pilot & prove  ·  46–80", bold: true }, "3 pilots live as managed services, change & incident paths, weekly scorecard", "Gate 3: scale, adjust or stop each pilot"],
  [{ text: "Scale & hand over  ·  81–100", bold: true }, "12-month roadmap, trained owners, service levels in force", "Approve roadmap and run budget"],
], { y: 1.45, colW: [2.3, 3.6, 2.9], rowH: [0.38, 0.72, 0.72, 0.72, 0.72], fontSize: 10.5 });

// 7 — Section
s = pres.addSlide({ masterName: "Section" });
s.addText("02 — THE OPERATING MODEL", { placeholder: "label" });
s.addText("Who decides, who delivers, who runs it", { placeholder: "title" });

// 8 — Operating model layers
s = pres.addSlide({ masterName: "Content" });
s.addText("One operating model, one flow of value", { placeholder: "title" });
const layers = [
  ["GOVERN", "PMI governance", "Executive sponsor · AI steering committee (fortnightly) · portfolio board with stage gates"],
  ["DELIVER", "PMI delivery", "PMO · hybrid delivery: agile sprints inside stage gates · risk & benefits registers"],
  ["RUN", "ITIL practices", "Service desk · incident · change enablement · service level management · continual improvement"],
  ["ENABLE", "Platform & data", "AI & data platform · security & privacy · model monitoring · vendor management"]];
layers.forEach(([n, fw, d], i) => {
  const y = 1.45 + i * 0.82;
  s.addShape(pres.shapes.RECTANGLE, { x: M, y, w: 7.35, h: 0.7, fill: { color: i % 2 ? C.paper : GREY }, line: { color: C.ink, width: 0.75 } });
  txt(s, n, { x: M + 0.2, y: y + 0.12, w: 1.3, h: 0.25, fontFace: H, fontSize: 11, bold: true, charSpacing: 2 });
  txt(s, fw, { x: M + 0.2, y: y + 0.38, w: 1.3, h: 0.25, fontSize: 9.5, color: C.muted });
  txt(s, d, { x: M + 1.6, y, w: 5.6, h: 0.7, fontSize: 11, valign: "middle" });
});
// Value stream: forward chevron echoing the logo
s.addShape(pres.shapes.CHEVRON, { x: 8.25, y: 1.45, w: 1.15, h: 2.9, fill: { color: C.accent }, line: { color: C.accent } });
txt(s, "Demand → value", { x: 8.1, y: 4.4, w: 1.3, h: 0.25, fontFace: H, fontSize: 11, bold: true, align: "center" });
s.addNotes("The chevron is the ITIL value stream: every request flows from demand to value through all four layers. Terminology follows ITIL practices; confirm naming against the ITIL (version 5) publication used by the client.");

// 9 — RACI
s = pres.addSlide({ masterName: "Content" });
s.addText("Clear accountability from day one", { placeholder: "title" });
const A = { text: "A", bold: true, align: "center" }, R = { text: "R", align: "center" },
      Cc = { text: "C", align: "center", color: C.muted }, I = { text: "I", align: "center", color: C.muted };
table(s, [
  ["Decision", { text: "Sponsor (CEO)", align: "center" }, { text: "CIO", align: "center" }, { text: "CISO / DPO", align: "center" },
   { text: "Business owner", align: "center" }, { text: "XLRTE PMO", align: "center" }, { text: "Service owner", align: "center" }],
  ["Prioritise use cases", A, Cc, Cc, R, R, I],
  ["Change scope or budget", A, R, I, Cc, R, I],
  ["Go-live of an AI service", I, A, Cc, R, R, R],
  ["Change to production", I, A, Cc, I, Cc, R],
  ["Data access & privacy", I, Cc, A, R, Cc, I],
  ["Service levels & incidents", I, A, I, Cc, I, R],
], { y: 1.4, colW: [2.5, 1.05, 1.05, 1.05, 1.05, 1.05, 1.05], rowH: 0.42, fontSize: 10.5 });
txt(s, "R Responsible   A Accountable   C Consulted   I Informed", { x: M, y: 4.55, w: 6, h: 0.25, fontSize: 9, color: C.muted });

// 10 — Section
s = pres.addSlide({ masterName: "Section" });
s.addText("03 — PROOF AND CONTROL", { placeholder: "label" });
s.addText("How you will know it works, every week", { placeholder: "title" });

// 11 — Scorecard with chart
s = pres.addSlide({ masterName: "Content" });
s.addText("The pilot pays back: handling time down 30 %", { placeholder: "title" });
const weeks = ["Base", "W1", "W2", "W3", "W4", "W5", "W6", "W7"];
const mins = [24, 24, 23, 22, 20, 19, 18, 17];
s.addChart(pres.charts.BAR, [{ name: "Minutes per case", labels: weeks, values: mins }], {
  x: M, y: 1.65, w: 5.2, h: 2.95, barDir: "col", barGapWidthPct: 55,
  chartColors: mins.map((_, i) => (i === mins.length - 1 ? C.accent : NEUTRAL)),
  valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
  catAxisLabelColor: C.muted, catAxisLabelFontFace: B, catAxisLabelFontSize: 10,
  catAxisLineShow: true, catAxisLineColor: t.chart.axis.replace("#", ""),
  showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.ink, dataLabelFontFace: B, dataLabelFontSize: 10,
  showLegend: false, showTitle: false });
txt(s, "Average handling time per case, pilot process (minutes)", { x: M, y: 1.4, w: 5.2, h: 0.25, fontSize: 10, color: C.muted });
label(s, "WEEKLY SCORECARD", 6.2, 1.45, 3.2);
[["Value", "Hours saved · cost per case"], ["Service", "SLA met · change success rate · time to restore"],
 ["Delivery", "Milestones on time · budget variance"], ["Adoption", "Active users · tasks handled with AI"]].forEach(([k, v], i) => {
  const y = 1.85 + i * 0.68;
  txt(s, k, { x: 6.2, y, w: 3.2, h: 0.28, fontFace: H, fontSize: 13, bold: true });
  txt(s, v, { x: 6.2, y: y + 0.28, w: 3.2, h: 0.3, fontSize: 10.5, color: C.muted });
});
note(s, "Illustrative data.");

// 12 — Risks
s = pres.addSlide({ masterName: "Content" });
s.addText("Risks managed from day one", { placeholder: "title" });
table(s, [
  ["Risk", "Early signal", "How we manage it"],
  [{ text: "Data not fit for AI", bold: true }, "Gaps found in data assessment", "Data readiness check in Diagnose; pilots only where data passes"],
  [{ text: "Low adoption", bold: true }, "Active users flat after week 2", "Business owner per use case; training; human-in-the-loop design"],
  [{ text: "Compliance (EU AI Act, GDPR)", bold: true }, "Use case touches personal data or high-risk category", "CISO/DPO accountable; risk classification before Gate 2"],
  [{ text: "Vendor lock-in & cost creep", bold: true }, "Run cost per case above plan", "Open interfaces; cost per case on the weekly scorecard"],
], { y: 1.45, colW: [2.4, 2.8, 3.6], rowH: [0.38, 0.68, 0.68, 0.68, 0.68], fontSize: 10.5 });

// 13 — The ask
s = pres.addSlide({ masterName: "Content" });
s.addText("What we need from you in the first 10 days", { placeholder: "title" });
[["Name the executive sponsor", "CEO", "Day 1"],
 ["Confirm steering committee and fortnightly cadence", "Sponsor", "Day 3"],
 ["Grant access to data, systems and process owners", "CIO", "Day 5"],
 ["Nominate business owners for candidate use cases", "Board", "Day 7"],
 ["Approve the pilot budget envelope", "CFO", "Day 10"]].forEach(([a, who, when], i) => {
  const y = 1.45 + i * 0.62;
  txt(s, String(i + 1).padStart(2, "0"), { x: M, y, w: 0.6, h: 0.45, fontFace: H, fontSize: 20, bold: true, color: C.accent, valign: "middle" });
  txt(s, a, { x: M + 0.75, y, w: 5.6, h: 0.45, fontSize: 14, valign: "middle" });
  txt(s, who, { x: 7.0, y, w: 1.2, h: 0.45, fontSize: 12, color: C.muted, valign: "middle" });
  txt(s, when, { x: 8.3, y, w: 1.1, h: 0.45, fontFace: H, fontSize: 12, bold: true, valign: "middle", align: "right" });
  if (i < 4) s.addShape(pres.shapes.LINE, { x: M, y: y + 0.54, w: W, h: 0, line: { color: LINE, width: 0.75 } });
});

// 14 — Closing
s = pres.addSlide({ masterName: "Title" });
s.addText("Let's make the first 100 days count", { placeholder: "title" });
s.addText("P·E  ·  XLRTE  ·  name@example.com", { placeholder: "subtitle" });
s.addImage({ path: LOGO("pe-white.png"), x: 9.4 - 0.3 * 1.295, y: 4.95, h: 0.3, w: 0.3 * 1.295, altText: "P·E" });

save(pres, __dirname + "/xlrte-100-day-plan.pptx");
