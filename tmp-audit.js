const fs = require("fs");
const base = "c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/";
function lines(p) { return fs.readFileSync(base + p, "utf8").split("\n"); }

const pc = lines("js/page-controller.js");
console.log("== page-controller: case list ==");
pc.forEach((l, i) => { const m = l.match(/case '([a-z-]+)'/); if (m) console.log((i + 1) + " " + m[1]); });
console.log("== page-controller: h1 lines ==");
pc.forEach((l, i) => { if (l.includes("<h1")) console.log((i + 1) + " " + l.trim().slice(0, 140)); });
console.log("== page-controller: learn case region ==");
const li = pc.findIndex(l => /case 'learn'/.test(l));
console.log(pc.slice(li, li + 14).join("\n"));

const hero = lines("js/lab-hero.js").join("\n");
const keys = [...hero.matchAll(/^    '([a-z-]+)': \{/gm)].map(m => m[1]);
console.log("== lab-hero TARGETS keys (" + keys.length + ") ==");
console.log(keys.join(", "));
const vi = hero.indexOf("var VIEWS");
console.log("== lab-hero VIEWS block ==");
console.log(hero.slice(vi, vi + 900));
console.log("== lab-hero dup var check ==");
console.log([...hero.matchAll(/var observedContainers = \[\];/g)].length + " declarations");

const files = ["js/states.js", "js/paleo-linguistics.js", "js/load-researches.js", "js/methodology-lab.js",
  "js/dashboard.js", "js/scripture-reader.js", "js/cartography.js", "js/timeline.js", "js/heraldry.js",
  "js/word-analyzer.js", "js/etymology-checker.js", "js/linguistic-tensor.js", "js/name-decoder.js"];
files.forEach(f => {
  if (!fs.existsSync(base + f)) { console.log("== " + f + " : ABSENT =="); return; }
  const ls = lines(f);
  const hits = [];
  ls.forEach((l, i) => { if (l.includes("<h1")) hits.push((i + 1) + " " + l.trim().slice(0, 150)); });
  const seg = ls.some(l => /segments\[1\]|params\.state|params\.diagnostic|params\.book/.test(l));
  console.log("== " + f + " | internal-route:" + seg + " | h1:" + hits.length);
  hits.forEach(h => console.log("   " + h));
});

const idx = lines("index.html");
console.log("== index.html data-module values ==");
const set = new Set();
idx.forEach(l => [...l.matchAll(/data-module="([a-z-]+)"/g)].forEach(x => set.add(x[1])));
console.log([...set].join(", "));
console.log("== index.html hero mount / LabHero ==");
idx.forEach((l, i) => { if (/LabHero|lab-hero/i.test(l)) console.log((i + 1) + " " + l.trim().slice(0, 140)); });
