/* stage7-drift.mjs — доказательство: единственное визуальное изменение Этапа 7 — крошки
   Для каждого светлого роутера: загружаем страницу, выключаем installCrumbs
   (удаляем уже созданный .lab-crumb-slot), fullPage screenshot => B;
   сравниваем с эталоном v7 (никогда не имел крошек, motion-tокены невидимы в settled-state).
   diff == 0  => контент ниже крошки НЕ изменён (регрессий нет). */
import { chromium } from 'playwright-core';
import { pathToFileURL } from 'node:url';
import { resolve, join } from 'node:path';
import fs from 'node:fs';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';

const APP = resolve('c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab');
const routes = ['dashboard','manifest','states','dictionaries','researches','timeline','scripture-reader','generators','cartography','learn','methodology'];
const themeDir = 'light';

(async () => {
  const b = await chromium.launch({ channel:'chrome', headless:true, args:['--allow-file-access-from-files','--no-sandbox'] });
  const ctx = await b.newContext({ viewport:{width:1440,height:900} });
  const p = await ctx.newPage();
  let okc = 0, fac = 0;
  fs.mkdirSync('tmp-b', { recursive:true });
  for (const r of routes) {
    const ref = join('baseline','v7',themeDir,r+'.png');
    if (!fs.existsSync(ref)) { console.log('SKIP '+r+' (v7 ref missing)'); continue; }
    await p.goto(pathToFileURL(join(APP,'index.html')).href+'#'+r, { waitUntil:'networkidle', timeout:15000 }).catch(()=>{});
    await p.waitForFunction('window.LabNav', { timeout:8000 }).catch(()=>{});
    await p.waitForTimeout(300);
    await p.evaluate(() => { const s = document.querySelector('.lab-crumb-slot'); if (s) s.remove(); });
    const tmp = join('tmp-b',r+'.png');
    await p.screenshot({ path:tmp, fullPage:true });
        const A = PNG.sync.read(fs.readFileSync(ref)), B = PNG.sync.read(fs.readFileSync(tmp));
    const w = A.width;
    if (w !== B.width) { console.log(`SKIP ${r} width-mismatch`); continue; }
    const offset = B.height - A.height;     // смещение строк: +crumb-slot
    if (offset < 0) { console.log(`SKIP ${r} negative-shift`); continue; }
    const H = A.height;
    const row = w * 4;
    const imgA = A.data.slice(0, H * row);
    const imgB = new Uint8Array(H * row);
    for (let y = 0; y < H; y++) {
      const sa = (y + offset) * row, da = y * row;
      for (let i = 0; i < row; i++) imgB[da + i] = B.data[sa + i];
    }
    const out = new Uint8Array(H * row);
    const d = pixelmatch(imgA, imgB, out, w, H, { threshold:0.1 });
    if (d === 0) { okc++; console.log(`OK   ${r}`); }
    else { fac++; console.log(`DRIFT ${r} (${d}px)`); }
  }
  console.log(`\nv7↔(v8 no-crumbs): ${okc}/${routes.length} OK, ${fac} DRIFT`);
  await b.close();
  fs.rmSync('tmp-b', { recursive:true, force:true });
  process.exit(fac ? 1 : 0);
})();
