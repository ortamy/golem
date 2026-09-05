const { chromium } = require('@playwright/test');
const fs = require('node:fs');

(async () => {
  const route = process.argv[2] || 'dashboard';
  const outDir = 'C:/Users/DELL/Desktop/golem/tasks/pilot';
  fs.mkdirSync(outDir, { recursive: true });
  const base = 'http://127.0.0.1:4180/index.html#' + route;
  const b = await chromium.launch({ channel: 'chrome' });
  const shots = [
    { name: 'light-desktop', width: 1280, height: 800, theme: null, mobile: false },
    { name: 'dark-desktop', width: 1280, height: 800, theme: 'dark', mobile: false },
    { name: 'light-mobile', width: 390, height: 844, theme: null, mobile: true }
  ];
  for (const s of shots) {
    const ctx = await b.newContext({
      viewport: { width: s.width, height: s.height },
      isMobile: s.mobile,
      deviceScaleFactor: 1
    });
    if (s.theme) await ctx.addInitScript(t => localStorage.setItem('golem_theme', t), s.theme);
    const p = await ctx.newPage();
    await p.goto(base, { waitUntil: 'domcontentloaded' });
    // Любой маршрут: ждём либо lab-hero, либо основной контент (fallback для кастомных шапок)
    const hero = p.locator('.lab-hero__title');
    const body = p.locator('body');
    try { await hero.waitFor({ state: 'visible', timeout: 8000 }); } catch { await body.waitFor({ state: 'visible', timeout: 8000 }); }
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(1200);
    await p.screenshot({ path: outDir + '/after-' + route + '-' + s.name + '.png' });
    await ctx.close();
    console.log('shot: ' + s.name);
  }
  await b.close();
  console.log('done');
})().catch(e => { console.error('PILOT_FAIL', e.message); process.exit(1); });
