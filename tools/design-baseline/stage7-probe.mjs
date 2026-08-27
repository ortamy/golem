/* stage7-probe.mjs — атрибуционная проверка крошек и motion-токенов (Этап 7) */
import { chromium } from 'playwright-core';
import { pathToFileURL } from 'node:url';
import { resolve, join } from 'node:path';

const APP = resolve('c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab');
const ROUTES = ['dashboard','manifest','states','dictionaries','researches','checkers','generators','learn'];
const HAS_H1 = new Set(ROUTES);
const opts = { channel:'chrome', headless:true, args:['--allow-file-access-from-files','--no-sandbox'] };

(async () => {
  const b = await chromium.launch(opts);
  const ctx = await b.newContext({ viewport:{width:1440,height:900} });
  const p = await ctx.newPage();
  let pass=0, fail=0;
  const ok = (c, m) => { console.log('[' + (c?'PASS':'FAIL') + '] ' + m); c ? pass++ : fail++; };

  for (const r of ROUTES) {
    const u = pathToFileURL(join(APP,'index.html')).href + '#' + r;
    await p.goto(u, {waitUntil:'networkidle', timeout:15000}).catch(()=>{});
    await p.waitForTimeout(300);
    const exists = (await p.$('.lab-crumbs')) !== null;
    const cur = (await p.$eval('.lab-crumb-current', e => e.textContent || '').catch(()=>'')) || '';
    ok(exists && cur.trim() && HAS_H1.has(r), 'crumbs: ' + r + ' current="' + (cur.slice(0,20)) + '"');
  }
  await p.goto(pathToFileURL(join(APP,'index.html')).href + '#dashboard', {waitUntil:'networkidle',timeout:15000}).catch(()=>{});
  await p.waitForTimeout(300);
    const td = await p.$eval('.lab-btn', e => getComputedStyle(e).transitionDuration).catch(()=>'(none)');
    ok(td === '0.12s' || td === '0.18s', 'motion: .lab-btn transitionDuration=' + td + ' (migrated motion-token)');
  await b.close();
  console.log('\n' + pass + ' PASS, ' + fail + ' FAIL');
  process.exit(fail ? 1 : 0);
})();
