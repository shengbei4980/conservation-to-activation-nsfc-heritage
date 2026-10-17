import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const FIGURE_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const OUTPUT_DIR = path.join(FIGURE_DIR, "outputs", "reproduced");
await fs.mkdir(OUTPUT_DIR, { recursive: true });
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const SOURCE = path.join(FIGURE_DIR, "data", "original_figures", "svg (1).png");
const OUTPUT = path.join(OUTPUT_DIR, "figure1_redrawn_editable.pptx");
const PREVIEW = path.join(OUTPUT_DIR, "figure1_preview.png");
const LAYOUT = path.join(OUTPUT_DIR, "figure1_layout.json");
const ASSET_DIR = path.join(FIGURE_DIR, "data", "redraw_assets", "assets");

const SW = 2100;
const SH = 1299;
const FONT = "Times New Roman";
const COLORS = {
  blue: "#2878E8",
  teal: "#0AA3B5",
  orange: "#F06424",
  green: "#2F963D",
  purple: "#7955D9",
  darkBlue: "#17275B",
  gray: "#858585",
  black: "#111111",
  white: "#FFFFFF",
  paleGreen: "#EAF6E9",
};

function pos(left, top, width, height) {
  return { left, top, width, height };
}

function cropPx(x, y, w, h) {
  return {
    left: x / SW,
    top: y / SH,
    right: 1 - (x + w) / SW,
    bottom: 1 - (y + h) / SH,
  };
}

function addShape(slide, geometry, frame, options = {}) {
  return slide.shapes.add({
    geometry,
    name: options.name,
    position: frame,
    fill: options.fill ?? "none",
    line: options.line ?? { style: "solid", fill: "none", width: 0 },
    ...(options.borderRadius !== undefined ? { borderRadius: options.borderRadius } : {}),
  });
}

function addText(slide, text, frame, options = {}) {
  const shape = addShape(slide, "textbox", frame, {
    name: options.name,
    fill: options.fill ?? "none",
    line: options.line ?? { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: FONT,
    fontSize: options.fontSize ?? 18,
    bold: options.bold ?? false,
    italic: options.italic ?? false,
    color: options.color ?? COLORS.black,
    alignment: options.align ?? "center",
    verticalAlignment: options.valign ?? "middle",
    autoFit: options.autoFit ?? "shrinkText",
    wrap: options.wrap ?? "square",
    lineSpacing: options.lineSpacing ?? 0.92,
    insets: options.insets ?? { left: 3, right: 3, top: 2, bottom: 2 },
  };
  return shape;
}

function addOuterBand(slide, y, h, color, title, titleY = y + 3) {
  addShape(slide, "roundRect", pos(16, y, 1968, h), {
    name: `band-${title}`,
    fill: "none",
    line: { style: "dashed", fill: color, width: 2.5 },
    borderRadius: 18,
  });
  addText(slide, title, pos(430, titleY, 1130, 40), {
    name: `title-${title}`,
    fontSize: 34,
    bold: true,
    color,
  });
}

function addArrow(slide, x, y, w = 40, h = 42) {
  return addShape(slide, "rightArrow", pos(x, y, w, h), {
    name: `flow-arrow-${x}-${y}`,
    fill: COLORS.gray,
    line: { style: "solid", fill: COLORS.gray, width: 0.5 },
  });
}

async function main() {
  const assetNames = [
    "step1-researcher", "step1-records-icon", "step1-reports-icon", "step1-metadata-icon", "step1-cleaning-icon", "step1-evidence-icon",
    "step2-expert", "step2-role-icon", "step2-boundary-icon", "step2-source-rule-icon", "step2-independence-icon", "step2-injection-icon",
    "step3-manual", "step3-closed-icon", "step3-single-icon", "step3-multi-icon", "step3-phrases-icon", "step3-json-icon", "step3-role-icon", "step3-manual-icon", "step3-evidence-icon",
    "step4-dialogue", "step4-package-icon", "step4-loop-arrows",
    "step5-robot", "step5-independent-icon", "step5-features-icon", "step5-parsing-icon", "step5-manual-icon", "step5-outputs-icon",
    "step5-result-1-icon", "step5-result-2-icon", "step5-result-3-icon", "step5-result-4-icon",
  ];
  const assetCache = new Map();
  await Promise.all(assetNames.map(async (name) => {
    const bytes = await fs.readFile(path.join(ASSET_DIR, `${name}.png`));
    assetCache.set(name, bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength));
  }));
  const presentation = Presentation.create({ slideSize: { width: SW, height: SH } });
  const slide = presentation.slides.add();
  slide.background.fill = COLORS.white;

  function addCrop(name, sourceRect, frame, alt) {
    const blob = assetCache.get(name);
    if (!blob) throw new Error(`Missing cropped asset: ${name}`);
    return slide.images.add({
      blob,
      contentType: "image/png",
      alt,
      fit: "contain",
      position: frame,
      geometry: "rect",
      name,
    });
  }

  function addCard({ name, x, y, w, h, color, header, body, icon, iconFrame, headerFrame, bodyFrame, headerSize = 20, bodySize = 18, bodyAlign = "center" }) {
    const card = addShape(slide, "roundRect", pos(x, y, w, h), {
      name,
      fill: COLORS.white,
      line: { style: "solid", fill: color, width: 2.2 },
      borderRadius: 10,
    });
    if (icon && iconFrame) addCrop(`${name}-icon`, icon, iconFrame, `${header} icon cropped from source figure`);
    if (header) addText(slide, header, headerFrame ?? pos(x + 8, y + 8, w - 16, 28), {
      name: `${name}-header`, fontSize: headerSize, bold: true, color,
    });
    if (body) addText(slide, body, bodyFrame ?? pos(x + 8, y + 37, w - 16, h - 43), {
      name: `${name}-body`, fontSize: bodySize, bold: true, color: COLORS.black, align: bodyAlign,
    });
    return card;
  }

  // Step 1
  addOuterBand(slide, 46, 212, COLORS.blue, "Step 1. Corpus preprocessing and project-level evidence binding", 50);
  addCrop("step1-researcher", { x: 30, y: 56, w: 272, h: 184 }, pos(31, 57, 273, 184), "Researcher working at a laptop");
  addArrow(slide, 645, 127, 39, 45);
  addArrow(slide, 976, 127, 39, 45);
  addArrow(slide, 1307, 127, 39, 45);
  addArrow(slide, 1615, 127, 39, 45);
  addCard({
    name: "step1-records", x: 319, y: 93, w: 324, h: 135, color: COLORS.blue,
    header: "NSFC project records", body: "raw search records = 144\nretained heritage-related\ncorpus = 142",
    icon: { x: 340, y: 100, w: 88, h: 112 }, iconFrame: pos(337, 102, 92, 112),
    headerFrame: pos(430, 99, 205, 30), bodyFrame: pos(430, 133, 205, 78), headerSize: 20, bodySize: 18,
  });
  addCard({
    name: "step1-reports", x: 686, y: 93, w: 287, h: 135, color: COLORS.blue,
    header: "NSFC\nFinal-report texts", body: "OCR recognition and\ntext extraction",
    icon: { x: 709, y: 104, w: 88, h: 110 }, iconFrame: pos(706, 105, 92, 110),
    headerFrame: pos(795, 102, 170, 49), bodyFrame: pos(798, 154, 165, 58), headerSize: 20, bodySize: 18,
  });
  addCard({
    name: "step1-metadata", x: 1018, y: 93, w: 277, h: 135, color: COLORS.blue,
    header: "Metadata and\nachievement statistics", body: "funding category\ndiscipline code\nsub-quantities",
    icon: { x: 1030, y: 103, w: 84, h: 112 }, iconFrame: pos(1030, 102, 88, 113),
    headerFrame: pos(1124, 102, 162, 49), bodyFrame: pos(1123, 153, 165, 65), headerSize: 20, bodySize: 18,
  });
  addCard({
    name: "step1-cleaning", x: 1348, y: 93, w: 265, h: 135, color: COLORS.blue,
    header: "Text cleaning and binding", body: "noise removal\nspacing merge\nmarkdown/image removal",
    icon: { x: 1365, y: 107, w: 86, h: 110 }, iconFrame: pos(1364, 105, 88, 111),
    headerFrame: pos(1450, 102, 154, 30), bodyFrame: pos(1450, 137, 155, 75), headerSize: 19, bodySize: 18,
  });
  addCard({
    name: "step1-evidence", x: 1655, y: 93, w: 285, h: 135, color: COLORS.blue,
    header: "Project-level evidence", body: "one project\none evidence package",
    icon: { x: 1670, y: 104, w: 91, h: 109 }, iconFrame: pos(1671, 104, 92, 110),
    headerFrame: pos(1764, 102, 168, 31), bodyFrame: pos(1765, 139, 164, 70), headerSize: 19, bodySize: 18,
  });
  addText(slide, "All records are normalized and standardized before coding.", pos(675, 230, 770, 26), {
    name: "step1-normalization-note", fontSize: 18, bold: true, italic: true, color: COLORS.blue,
  });

  // Step 2
  addOuterBand(slide, 271, 165, COLORS.teal, "Step 2. System-role specification", 271);
  addCrop("step2-expert", { x: 32, y: 274, w: 250, h: 161 }, pos(32, 274, 250, 161), "Heritage expert with checklist");
  addText(slide, "heritage protection", pos(383, 278, 245, 25), { name: "heritage-protection-label", fontSize: 17, bold: true });
  addArrow(slide, 646, 345, 39, 43);
  addArrow(slide, 976, 345, 39, 43);
  addArrow(slide, 1307, 345, 39, 43);
  addArrow(slide, 1616, 345, 39, 43);
  addCard({
    name: "step2-role", x: 319, y: 308, w: 315, h: 119, color: COLORS.teal,
    header: "Expert role definition", body: "heritage protection\nheritage science and\nscience-of-science expertise",
    icon: { x: 331, y: 319, w: 99, h: 99 }, iconFrame: pos(330, 318, 101, 101),
    headerFrame: pos(432, 318, 193, 30), bodyFrame: pos(432, 349, 193, 68), headerSize: 19, bodySize: 17,
  });
  addCard({
    name: "step2-boundary", x: 686, y: 308, w: 287, h: 119, color: COLORS.teal,
    header: "Task boundary", body: "code research agendas\nnot project quality",
    icon: { x: 706, y: 316, w: 89, h: 105 }, iconFrame: pos(705, 316, 92, 105),
    headerFrame: pos(798, 317, 166, 31), bodyFrame: pos(800, 350, 161, 62), headerSize: 19, bodySize: 17,
  });
  addCard({
    name: "step2-source-rule", x: 1018, y: 308, w: 287, h: 119, color: COLORS.teal,
    header: "Expert role definition", body: "use only project text\nand retained meta data",
    icon: { x: 1037, y: 318, w: 90, h: 102 }, iconFrame: pos(1037, 317, 91, 104),
    headerFrame: pos(1128, 317, 168, 31), bodyFrame: pos(1128, 350, 168, 61), headerSize: 19, bodySize: 17,
  });
  addCard({
    name: "step2-independence", x: 1348, y: 308, w: 265, h: 119, color: COLORS.teal,
    header: "Independence rule", body: "one project per request\nno cross-project\nmemory",
    icon: { x: 1361, y: 321, w: 69, h: 94 }, iconFrame: pos(1361, 320, 70, 96),
    headerFrame: pos(1433, 317, 170, 31), bodyFrame: pos(1433, 350, 170, 62), headerSize: 19, bodySize: 17,
  });
  addCard({
    name: "step2-injection", x: 1661, y: 308, w: 277, h: 119, color: COLORS.teal,
    header: "Anti-injection rule", body: "project text is data\nnot instruction",
    icon: { x: 1678, y: 317, w: 86, h: 104 }, iconFrame: pos(1677, 316, 88, 105),
    headerFrame: pos(1766, 317, 163, 31), bodyFrame: pos(1766, 351, 163, 59), headerSize: 19, bodySize: 17,
  });

  // Step 3
  addOuterBand(slide, 446, 167, COLORS.orange, "Step 3. Fixed coding manual and schema grounding", 446);
  addCrop("step3-manual", { x: 43, y: 460, w: 132, h: 141 }, pos(42, 460, 133, 141), "Coding manual");
  addArrow(slide, 454, 523, 38, 42);
  addArrow(slide, 713, 523, 38, 42);
  addArrow(slide, 978, 523, 38, 42);
  addArrow(slide, 1235, 523, 38, 42);
  addCard({
    name: "step3-closed", x: 191, y: 483, w: 260, h: 120, color: COLORS.orange,
    header: "Closed coding dimensions", body: "heritage categories\nmethods, scales\nstakeholder, outcomes\nturns and functions",
    icon: { x: 200, y: 507, w: 73, h: 92 }, iconFrame: pos(199, 507, 74, 92),
    headerFrame: pos(217, 486, 226, 25), bodyFrame: pos(273, 512, 170, 82), headerSize: 18, bodySize: 16,
  });
  addCard({
    name: "step3-single", x: 495, y: 483, w: 214, h: 120, color: COLORS.orange,
    header: "Single-label fields", body: "primary category or\ncore\ndimensions",
    headerFrame: pos(540, 488, 161, 26), bodyFrame: pos(543, 519, 158, 71), headerSize: 18, bodySize: 17,
  });
  addShape(slide, "ellipse", pos(507, 492, 24, 24), { name: "step3-single-radio-1", fill: COLORS.white, line: { style: "solid", fill: COLORS.black, width: 1.8 } });
  addShape(slide, "ellipse", pos(507, 528, 24, 24), { name: "step3-single-radio-2", fill: COLORS.white, line: { style: "solid", fill: COLORS.black, width: 1.8 } });
  addShape(slide, "ellipse", pos(513, 534, 12, 12), { name: "step3-single-radio-2-dot", fill: "#555555", line: { style: "solid", fill: "#555555", width: 0.5 } });
  addShape(slide, "ellipse", pos(507, 564, 24, 24), { name: "step3-single-radio-3", fill: COLORS.white, line: { style: "solid", fill: COLORS.black, width: 1.8 } });
  addCard({
    name: "step3-multi", x: 754, y: 483, w: 221, h: 120, color: COLORS.orange,
    header: "Multi-label fields", body: "tags for\nco-occurrence\nand secondary\ndimensions",
    icon: { x: 769, y: 505, w: 63, h: 93 }, iconFrame: pos(768, 505, 64, 94),
    headerFrame: pos(826, 488, 141, 26), bodyFrame: pos(835, 516, 132, 78), headerSize: 18, bodySize: 16,
  });
  addCard({
    name: "step3-phrases", x: 1018, y: 483, w: 214, h: 120, color: COLORS.orange,
    header: "Evidence phrases", body: "direct phrases\nretained for\ntraceability",
    icon: { x: 1028, y: 505, w: 88, h: 94 }, iconFrame: pos(1027, 505, 89, 94),
    headerFrame: pos(1086, 488, 138, 26), bodyFrame: pos(1117, 518, 107, 71), headerSize: 18, bodySize: 16,
  });
  addCard({
    name: "step3-json", x: 1273, y: 483, w: 227, h: 120, color: COLORS.orange,
    header: "Strict JSON schema", body: "parsable output\nwith confidence\nand review flags",
    icon: { x: 1287, y: 505, w: 75, h: 95 }, iconFrame: pos(1286, 505, 76, 95),
    headerFrame: pos(1353, 488, 139, 26), bodyFrame: pos(1361, 518, 131, 71), headerSize: 18, bodySize: 16,
  });
  addText(slide, "How the LLM reads the manual", pos(1565, 452, 342, 28), { name: "step3-manual-reading-label", fontSize: 19, bold: true, color: COLORS.orange });
  const manualCards = [
    { x: 1521, w: 135, title: "Role", body: "Act as a\nconservative\nheritage-science\ncoder", crop: { x: 1540, y: 490, w: 33, h: 41 }, iconX: 1538 },
    { x: 1664, w: 135, title: "Manual", body: "Use only\npredefined\ncodebooks", crop: { x: 1673, y: 490, w: 43, h: 41 }, iconX: 1671 },
    { x: 1807, w: 144, title: "Evidence", body: "Retain labels\nonly when\ntextual evidence\nis present", crop: { x: 1818, y: 490, w: 44, h: 42 }, iconX: 1815 },
  ];
  for (const m of manualCards) {
    addShape(slide, "roundRect", pos(m.x, 483, m.w, 120), { fill: COLORS.white, line: { style: "solid", fill: COLORS.orange, width: 2.1 }, borderRadius: 10, name: `step3-${m.title.toLowerCase()}` });
    addCrop(`step3-${m.title.toLowerCase()}-icon`, m.crop, pos(m.iconX, 491, m.crop.w, m.crop.h), `${m.title} icon`);
    addText(slide, m.title, pos(m.x + 45, 489, m.w - 50, 27), { fontSize: 18, bold: true, color: COLORS.orange, name: `step3-${m.title.toLowerCase()}-title` });
    addText(slide, m.body, pos(m.x + 7, 526, m.w - 14, 69), { fontSize: 16, bold: true, name: `step3-${m.title.toLowerCase()}-body` });
  }

  // Step 4
  addOuterBand(slide, 623, 331, COLORS.green, "Step 4. Small-sample polling and prompt convergence", 630);
  addCrop("step4-dialogue", { x: 31, y: 679, w: 364, h: 225 }, pos(31, 679, 364, 225), "Researcher testing prompts with an AI assistant");
  addText(slide, "Researcher questions(Q)", pos(560, 671, 315, 27), { name: "step4-q-title", fontSize: 20, bold: true, color: COLORS.green });
  addText(slide, "AI responses (A)", pos(1296, 671, 270, 27), { name: "step4-a-title", fontSize: 20, bold: true, color: COLORS.green });
  const qaRows = [
    { q: "Q1", question: "Can the model distinguish heritage objects from modern practices?", a: "A1", answer: "It separates carriers, problem delimitations\nand practice scopes." },
    { q: "Q2", question: "Is the model resisting training slogans as scientific evidence?", a: "A2", answer: "It analyzes primitive evidence-only coding and flags\ninsufficient information." },
    { q: "Q3", question: "Can the model handle compound projects with multi-dimensions\nand governance complexity?", a: "A3", answer: "It uses single-label fields for primary categories and\nmulti-label tags for co-occurrence." },
    { q: "Q4", question: "Are multiple codes traceable to manual references?", a: "A4", answer: "It references evidence phrases, confidence scores and review flags" },
  ];
  const qCards = [];
  const aCards = [];
  qaRows.forEach((row, i) => {
    const y = 697 + i * 50;
    const qCard = addShape(slide, "roundRect", pos(398, y, 632, 39), { name: `step4-${row.q}-card`, fill: COLORS.white, line: { style: "solid", fill: COLORS.green, width: 1.8 }, borderRadius: 7 });
    addShape(slide, "roundRect", pos(405, y + 4, 44, 31), { name: `step4-${row.q}-label-box`, fill: COLORS.paleGreen, line: { style: "solid", fill: COLORS.green, width: 1.4 }, borderRadius: 5 });
    addText(slide, row.q, pos(405, y + 4, 44, 31), { name: `step4-${row.q}-label`, fontSize: 19, bold: true, color: COLORS.green });
    addText(slide, row.question, pos(456, y + 2, 566, 35), { name: `step4-${row.q}-text`, fontSize: 17, bold: true });
    const aCard = addShape(slide, "roundRect", pos(1148, y, 551, 39), { name: `step4-${row.a}-card`, fill: COLORS.white, line: { style: "solid", fill: COLORS.green, width: 1.8 }, borderRadius: 7 });
    addShape(slide, "roundRect", pos(1155, y + 4, 44, 31), { name: `step4-${row.a}-label-box`, fill: COLORS.paleGreen, line: { style: "solid", fill: COLORS.green, width: 1.4 }, borderRadius: 5 });
    addText(slide, row.a, pos(1155, y + 4, 44, 31), { name: `step4-${row.a}-label`, fontSize: 19, bold: true, color: COLORS.green });
    addText(slide, row.answer, pos(1204, y + 1, 487, 37), { name: `step4-${row.a}-text`, fontSize: 17, bold: true });
    qCards.push(qCard);
    aCards.push(aCard);
  });
  qCards.forEach((qCard, i) => {
    slide.shapes.connect(qCard, aCards[i], {
      kind: "straight", fromSide: "right", toSide: "left",
      line: { style: "dashed", fill: "#777777", width: 1.8 },
      head: { type: "arrow", width: "sm", length: "sm" },
      tail: { type: "arrow", width: "sm", length: "sm" },
    });
  });
  addShape(slide, "roundRect", pos(574, 895, 918, 48), { name: "step4-stable-package", fill: COLORS.white, line: { style: "solid", fill: COLORS.green, width: 1.8 }, borderRadius: 7 });
  addCrop("step4-package-icon", { x: 615, y: 901, w: 48, h: 42 }, pos(615, 899, 49, 43), "Validated document package icon");
  addText(slide, "Stable prompt package", pos(865, 895, 330, 25), { name: "step4-package-title", fontSize: 19, bold: true, color: COLORS.green });
  addText(slide, "role + coding manual + anti-hallucination rules + JSON schema + review protocol", pos(700, 919, 680, 22), { name: "step4-package-body", fontSize: 16, bold: true });
  addCrop("step4-loop-arrows", { x: 1724, y: 674, w: 242, h: 244 }, pos(1723, 674, 243, 244), "Prompt refinement cycle arrows");
  addText(slide, "prompt\nrefinement\nloop", pos(1767, 718, 172, 150), { name: "step4-loop-text", fontSize: 30, bold: true, color: "#187D2B", lineSpacing: 1.0 });

  // Step 5
  addOuterBand(slide, 969, 239, COLORS.purple, "Step 5. Independent LLM extraction, validation and outputs", 976);
  addCrop("step5-robot", { x: 24, y: 999, w: 185, h: 191 }, pos(23, 999, 186, 191), "AI robot with verification clipboard");
  addArrow(slide, 417, 1081, 38, 42);
  addArrow(slide, 732, 1081, 38, 42);
  addArrow(slide, 995, 1081, 38, 42);
  addArrow(slide, 1282, 1081, 38, 42);
  addCard({
    name: "step5-independent", x: 211, y: 1026, w: 204, h: 146, color: COLORS.purple,
    header: "Independent project", body: "per 1-sample\none project per\nrequest",
    icon: { x: 239, y: 1061, w: 79, h: 108 }, iconFrame: pos(226, 1063, 72, 101),
    headerFrame: pos(235, 1036, 155, 27), bodyFrame: pos(302, 1064, 105, 91), headerSize: 18, bodySize: 17,
  });
  addCard({
    name: "step5-features", x: 458, y: 1026, w: 272, h: 146, color: COLORS.purple,
    header: "Structured feature extraction", body: "Heritage object\nResearch orientations\nScientific methods\nOutcome pathways\nResearch turns\nknowledge functions",
    icon: { x: 479, y: 1064, w: 72, h: 106 }, iconFrame: pos(478, 1063, 74, 107),
    headerFrame: pos(470, 1036, 249, 27), bodyFrame: pos(557, 1063, 164, 101), headerSize: 18, bodySize: 16, bodyAlign: "left",
  });
  addCard({
    name: "step5-parsing", x: 772, y: 1026, w: 221, h: 146, color: COLORS.purple,
    header: "Parsing and normalization", body: "JSON parsing\nlabel reconciliation\nand alias repair",
    icon: { x: 786, y: 1062, w: 77, h: 110 }, iconFrame: pos(784, 1061, 79, 110),
    headerFrame: pos(779, 1036, 207, 27), bodyFrame: pos(863, 1067, 123, 83), headerSize: 17, bodySize: 16,
  });
  addCard({
    name: "step5-manual", x: 1036, y: 1026, w: 244, h: 146, color: COLORS.purple,
    header: "Manual verification", body: "review evidence\nphrases\nlow-confidence cases\nand flags",
    icon: { x: 1055, y: 1058, w: 102, h: 112 }, iconFrame: pos(1053, 1057, 105, 113),
    headerFrame: pos(1143, 1036, 128, 27), bodyFrame: pos(1159, 1065, 112, 92), headerSize: 18, bodySize: 16,
  });
  const outputsCard = addCard({
    name: "step5-outputs", x: 1321, y: 1026, w: 193, h: 146, color: COLORS.purple,
    header: "Analysis-ready\noutputs", body: "CSV/JSONL\ncoding matrix",
    icon: { x: 1337, y: 1064, w: 91, h: 107 }, iconFrame: pos(1334, 1063, 94, 108),
    headerFrame: pos(1418, 1037, 88, 49), bodyFrame: pos(1427, 1090, 79, 61), headerSize: 18, bodySize: 16,
  });
  const resultRows = [
    { y: 990, text: "Object-problem-method structure", crop: { x: 1612, y: 995, w: 55, h: 37 } },
    { y: 1044, text: "Stage-wise evolution", crop: { x: 1614, y: 1054, w: 45, h: 24 } },
    { y: 1098, text: "Research-turn network", crop: { x: 1612, y: 1102, w: 52, h: 35 } },
    { y: 1152, text: "Outcome-pathway profile", crop: { x: 1613, y: 1157, w: 46, h: 34 } },
  ];
  const resultCards = [];
  resultRows.forEach((r, i) => {
    const card = addShape(slide, "roundRect", pos(1594, r.y, 364, 44), { name: `step5-result-${i + 1}`, fill: COLORS.white, line: { style: "solid", fill: COLORS.purple, width: 1.8 }, borderRadius: 7 });
    addCrop(`step5-result-${i + 1}-icon`, r.crop, pos(1610, r.y + 5, 54, 34), `${r.text} icon`);
    addText(slide, r.text, pos(1665, r.y + 4, 283, 36), { name: `step5-result-${i + 1}-text`, fontSize: 17, bold: true });
    resultCards.push(card);
  });
  resultCards.forEach((target, i) => {
    slide.shapes.connect(outputsCard, target, {
      kind: i === 1 || i === 2 ? "straight" : "elbow",
      fromSide: "right", toSide: "left",
      line: { style: "dashed", fill: "#5C80B5", width: 1.8 },
      head: { type: "arrow", width: "sm", length: "sm" },
    });
  });

  slide.speakerNotes.textFrame.setText(`[Sources]\n- User-provided source figure: ${SOURCE}\n[/Sources]`);

  const preview = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(PREVIEW, new Uint8Array(await preview.arrayBuffer()));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(LAYOUT, await layout.text(), "utf8");
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(OUTPUT);
  console.log(JSON.stringify({ output: OUTPUT, preview: PREVIEW, layout: LAYOUT }));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
