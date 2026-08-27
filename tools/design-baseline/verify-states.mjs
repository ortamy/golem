/* =============================================================
   verify-states.mjs вЂ” Р¶РёРІР°СЏ РїСЂРѕРІРµСЂРєР° Card States API (Р­С‚Р°Рї 4)
   Р“СЂСѓР·РёС‚ РґР°С€Р±РѕСЂРґ, РЅР°РІРµС€РёРІР°РµС‚ СЃРѕСЃС‚РѕСЏРЅРёСЏ РєР»Р°СЃСЃР°РјРё, С‡РёС‚Р°РµС‚
   computed style Рё СѓС‚РІРµСЂР¶РґР°РµС‚, С‡С‚Рѕ API СЂРµР°Р»СЊРЅРѕ СЂР°Р±РѕС‚Р°РµС‚.
   Р—Р°РїСѓСЃРє: node verify-states.mjs   (exit 1 РїСЂРё РїСЂРѕРІР°Р»Рµ)
   ============================================================= */
import { chromium } from 'playwright-core';

const APP = 'file:///c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/index.html';

const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--allow-file-access-from-files'] });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errs = [];
  page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  page.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
  await page.goto(APP + '#dashboard', { waitUntil: 'load', timeout: 30000 });
  await page.waitForTimeout(3000); // РєР°Рє РІ screenshot.mjs: СЂРѕСѓС‚РµСЂ + fetch РґР°РЅРЅС‹С…

  // РС‰РµРј Р¶РёРІСѓСЋ РєР°СЂС‚РѕС‡РєСѓ: СЃРїРµСЂРІР° РґР°С€Р±РѕСЂРґ, Р·Р°С‚РµРј СЃРєСЂРёРїС‚СѓСЂРЅР°СЏ РїРѕР»РєР° (.tool-card)
  let SEL = null;
  const count = async (s) => page.evaluate((q) => document.querySelectorAll(q).length, s);
  if (await count('.lab-card')) SEL = '.lab-card';
  else if (await count('.tool-card')) SEL = '.tool-card';
  else {
    await page.goto(APP + '#scripture-reader', { waitUntil: 'load', timeout: 30000 });
    await page.waitForTimeout(3000);
    if (await count('.tool-card')) SEL = '.tool-card';
  }
  if (!SEL) {
    console.log('[FAIL] РЅРё .lab-card, РЅРё .tool-card РЅРµ РЅР°Р№РґРµРЅС‹ РЅР° dashboard/scripture-reader');
    console.log('console errors:', JSON.stringify(errs.slice(0, 5), null, 2));
    process.exit(1);
  }

  const r = await page.evaluate(async (sel) => {
    const c = document.querySelector(sel);
    if (!c) return { fail: 'РєР°СЂС‚РѕС‡РєР° РёСЃС‡РµР·Р»Р° РёР· DOM' };
    const cs = () => getComputedStyle(c);
    const settle = () => new Promise(res => setTimeout(res, 400)); // > СЃР°РјРѕР№ РґРѕР»РіРѕР№ Р»РµРіР°СЃРё-РґР»РёС‚РµР»СЊРЅРѕСЃС‚Рё (.25s)

    const base = { border: cs().borderColor, shadow: cs().boxShadow };

    c.classList.add('is-selected');
    await settle(); // РґР°С‚СЊ С‚СЂР°РЅР·РёС€РЅСѓ Р·Р°РІРµСЂС€РёС‚СЊСЃСЏ, РёРЅР°С‡Рµ С‡РёС‚Р°РµРј t=0
    const selStyle = { border: cs().borderColor, shadow: cs().boxShadow };
    c.classList.remove('is-selected');

    c.classList.add('is-disabled');
    await settle();
    const dis = { opacity: cs().opacity, pe: cs().pointerEvents, shadow: cs().boxShadow };
    c.classList.remove('is-disabled');

    return { sel, base, selStyle, dis };
  }, SEL);

  let ok = true;
  const neq = (a, b) => a !== b;
  const t1 = neq(r.base.border, r.selStyle.border);
  const t2 = neq(r.base.shadow, r.selStyle.shadow);
  const t3 = r.dis.opacity === '0.55';
  const t4 = r.dis.pe === 'none';
  for (const [name, pass] of [['selected: СЂР°РјРєР° РёР·РјРµРЅРёР»Р°СЃСЊ', t1], ['selected: С‚РµРЅСЊ РёР·РјРµРЅРёР»Р°СЃСЊ', t2], ['disabled: opacity .55', t3], ['disabled: pointer-events none', t4]]) {
    console.log(`[${pass ? 'PASS' : 'FAIL'}] ${name}`);
    ok = ok && pass;
  }
  console.log(`\nРїСЂРѕР±Р° РЅР° ${r.sel}`);
  console.log('base     ->', JSON.stringify(r.base));
  console.log('selected ->', JSON.stringify(r.selStyle));
  console.log('disabled ->', JSON.stringify(r.dis));
  process.exit(ok ? 0 : 1);
} finally {
  await browser.close();
}
