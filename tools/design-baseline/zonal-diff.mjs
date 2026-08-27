/* zonal-diff.mjs — Этап 7
   Сравнение v7↔v8 ТОЛЬКО строками ниже верхней полосы крошек (row 0..TOP_MASK-1).
   Крошки занимают топ-зону; если ниже нечаянных регрессий — diff == 0. */
import fs from 'node:fs';
import path from 'node:path';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';

const BASE = 'baseline';
const TOP_MASK = 84;                                  // px под крошками + отступ h1
const routes = ['dashboard','manifest','states','dictionaries','researches','timeline','scripture-reader','generators','cartography','learn','methodology'];
const themes = ['light','white','dark'];

let pass = 0, fail = 0, skip = 0;
for (const t of themes) {
  for (const r of routes) {
    const a = path.join(BASE,'v7',t,r+'.png'), b = path.join(BASE,'v8',t,r+'.png');
    if (!fs.existsSync(a) || !fs.existsSync(b)) { console.log(`SKIP ${t}/${r}`); skip++; continue; }
        if (!fs.existsSync(a) || !fs.existsSync(b)) { console.log(`SKIP ${t}/${r}`); skip++; continue; }
        const A = PNG.sync.read(fs.readFileSync(a)), B = PNG.sync.read(fs.readFileSync(b));
    const w = A.width;
    if (w !== B.width) { console.log(`SKIP ${t}/${r} width-mismatch`); skip++; continue; }
    const H = Math.min(A.height, B.height);           // крошки растянули страницу — сравниваем пересечение
    const stride = w * H * 4;
        const imgA = A.data.slice(0, stride);
    const imgB = B.data.slice(0, stride);
    const out  = new Uint8Array(stride);
    for (let i = 0; i < w * TOP_MASK * 4; i++) { imgA[i]=0; imgB[i]=0; }   // игнорируем топ-зону крошек
        const diff = pixelmatch(imgA, imgB, out, w, H, { threshold:0.1 });
    if (diff === 0) { pass++; console.log(`OK   ${t}/${r}`); }
    else { fail++; console.log(`DRIFT ${t}/${r} (${diff}px)`); }
  }
}
console.log(`\ncontent-zone: ${pass}/${themes.length*routes.length} OK, ${fail} DRIFT, ${skip} SKIP`);
process.exit(fail ? 1 : 0);
