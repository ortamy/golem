import fs from 'node:fs';
import path from 'node:path';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';

const routes = ['dashboard','manifest','states','dictionaries','researches','timeline','scripture-reader','generators','cartography','learn','methodology'];
const theme = 'light';
let ok = 0, dr = 0;
for (const r of routes) {
  const ap = path.join('baseline','v7',theme,r+'.png'), bp = path.join('baseline','v8',theme,r+'.png');
  if (!fs.existsSync(ap) || !fs.existsSync(bp)) { console.log('SKIP '+r+' missing'); continue; }
  const A = PNG.sync.read(fs.readFileSync(ap)), B = PNG.sync.read(fs.readFileSync(bp));
  const offset = B.height - A.height; // +39 crumb строка на всех кадрах
  const rowA = A.width * 4, H = A.height;
  const imgA = A.data.slice(0, H * rowA);
  const imgB = new Uint8Array(H * rowA);
  for (let y = 0; y < H; y++) {
    const sa = (y + offset) * rowA, da = y * rowA;
    for (let i = 0; i < rowA; i++) imgB[da + i] = B.data[sa + i];
  }
  const out = new Uint8Array(H * rowA);
  const d = pixelmatch(imgA, imgB, out, A.width, H, { threshold:0.1 });
  if (d === 0) { ok++; console.log('OK   '+r+' (offset='+offset+')'); }
  else { dr++; console.log('DRIFT '+r+' ('+d+'px offset='+offset+')'); }
}
console.log('\nv7(light)↔v8(light) aligned-by-crumbs: '+ok+'/'+routes.length+' OK, '+dr+' DRIFT');
process.exit(dr ? 1 : 0);
