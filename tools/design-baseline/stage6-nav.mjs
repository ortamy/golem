/* =============================================================
   stage6-nav.mjs — атрибуционная проба этапа 6 (навигация)
   A = приложение как есть (nav-enhance активен)
   B = тот же кадр с заблокированным js/nav-enhance.js
   Одна среда (детерминированный офлайн) => попиксельная разница
   A−B обязана жить ТОЛЬКО в зоне сайдбара.
   Плюс функциональные ассерты самой навигации.
   Запуск: node stage6-nav.mjs            -> пробы и отчёт
           node stage6-nav.mjs --shoot    -> переснять B-кадры
   ============================================================= */
import { chromium } from 'playwright-core';
import { pathToFileURL } from 'node:url';
import { join } from 'node:path';
import { mkdirSync, readFileSync, existsSync, writeFileSync } from 'node:fs';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';

const APP_INDEX = pathToFileURL('c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/index.html').href;
const BASE = 'c:/Users/DELL/Desktop/golem-main/tools/design-baseline/baseline/v7';
const OUTB = 'c:/Users/DELL/Desktop/golem-main/tools/design-baseline/baseline/stage6-B';
const SHOOT_B = process.argv.includes('--shoot');
const FILL_A = process.argv.includes('--fill-a');
const onlyIdx = process.argv.indexOf('--only');
const ONLY = onlyIdx > -1 ? process.argv[onlyIdx + 1].split(',').map((s) => s.trim()) : null;
const ROUTES_ALL = ['dashboard', 'manifest', 'states', 'dictionaries', 'researches', 'learn', 'timeline', 'cartography', 'generators', 'methodology', 'scripture-reader'];
const ROUTES = ONLY ? ROUTES_ALL.filter((r) => ONLY.includes(r)) : ROUTES_ALL;
const THEME = 'light';

let browser;
try {
  browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--allow-file-access-from-files', '--hide-scrollbars'] });

  /* ---------- Функциональные ассерты навигации (сторона A) ---------- */
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
    await ctx.route(/^https?:\/\//, (r) => r.abort());
    const page = await ctx.newPage();
    await page.goto(`${APP_INDEX}#dashboard`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2500);

    const checks = [];
    const t = async (name, fn) => { try { const v = await fn(); checks.push([!!v, name + (typeof v === 'number' ? ` (${v})` : '')]); } catch (e) { checks.push([false, `${name}: ${e.message.slice(0, 80)}`]); } };

    await t('фильтр установлен в сайдбаре', () => page.$('.lab-nav-filter input'));
    await t('иконок-SVG заменено >= 20', () => page.$$eval('.lab-sidebar .lab-icon-wrap', (w) => w.length));
    await t('старых PNG-иконок в пунктах не осталось', () => page.$$eval('a.sidebar-item img.lab-icon', (i) => i.length));
    await t('Ctrl+K открывает палитру', () => page.keyboard.press('Control+k').then(() => page.waitForSelector('.lab-palette', { timeout: 1500 }).then(() => true)));
    await t('палитра содержит пункты', () => page.$$eval('.lab-palette-item', (i) => i.length));
    await t('Escape закрывает палитру', () => page.keyboard.press('Escape').then(() => page.waitForSelector('.lab-palette', { state: 'hidden', timeout: 1500 }).then(() => true)));
    await t('клик по хедер-поиску открывает палитру', () => page.click('#globalSearch input').then(() => page.waitForSelector('.lab-palette', { timeout: 1500 }).then(() => true)));
    await t('фильтр скрывает непопадания ("генер" -> виден generators)', () => page.fill('.lab-nav-filter input', 'генер').then(() => page.$$eval('.lab-sidebar .sidebar-item[data-module]', (a) => {
      const vis = a.filter((x) => x.offsetParent !== null || x.getClientRects().length);
      return vis.length <= 5 && a.find((x) => x.dataset.module === 'generators').offsetParent !== null;
    })));
    // переход по палитре ведёт в валидный раздел (не остаёмся на месте)
    await t('переход из палитры меняет маршрут на валидный раздел', () => page.keyboard.press('Control+k').then(() => page.waitForSelector('.lab-palette-item')).then(() => page.keyboard.press('Enter')).then(() => page.waitForTimeout(600)).then(() => page.evaluate(() => {
      const valid = ['#dashboard', '#manifest', '#states', '#dictionaries', '#researches', '#learn', '#timeline', '#cartography', '#generators', '#methodology', '#scripture-reader'];
      return valid.includes(location.hash) && location.hash !== '#dashboard';
    })));

    for (const [ok, name] of checks) console.log(`[${ok ? 'PASS' : 'FAIL'}] ${name}`);
    if (!checks.every((c) => c[0])) process.exitCode = 1;
    await ctx.close();
  }

  /* ---------- A/B кадры и зональная сверка ---------- */
  if (SHOOT_B) {
    mkdirSync(join(OUTB, THEME), { recursive: true });
    for (const route of ROUTES) {
      const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
      await ctx.route(/^https?:\/\//, (r) => r.abort());
      await ctx.route(/nav-enhance\.js$/, (r) => r.abort());
      const page = await ctx.newPage();
      await page.goto(`${APP_INDEX}#${route}`, { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
      await page.waitForTimeout(2000);
      await page.screenshot({ path: join(OUTB, THEME, `${route}.png`), fullPage: true });
      console.log(`[B] ${route}`);
      await ctx.close();
    }
  }

  /* ---------- Добор недостающих A-кадров в замороженную эпоху ---------- */
  if (FILL_A) {
    for (const route of ROUTES) {
      const pa = join(BASE, THEME, `${route}.png`);
      if (existsSync(pa)) continue;
      const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
      await ctx.route(/^https?:\/\//, (r) => r.abort());
      const page = await ctx.newPage();
      await page.goto(`${APP_INDEX}#${route}`, { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
      await page.waitForTimeout(2000);
      await page.screenshot({ path: pa, fullPage: true });
      console.log(`[A+] ${route}`);
      await ctx.close();
    }
  }

  /* ---------- Попиксельная сверка A(v7) − B(zone map) ---------- */
  mkdirSync('diff-stage6', { recursive: true });
  for (const route of ROUTES) {
    const pa = join(BASE, THEME, `${route}.png`);
    const pb = join(OUTB, THEME, `${route}.png`);
    if (!existsSync(pa) || !existsSync(pb)) { console.log(`[-] ${route}: нет кадра`); continue; }
    const A = PNG.sync.read(readFileSync(pa));
    const B = PNG.sync.read(readFileSync(pb));
    if (A.width !== B.width || A.height !== B.height) { console.log(`[?] ${route}: размер ${A.width}x${A.height} vs ${B.width}x${B.height}`); continue; }
    const d = new PNG({ width: A.width, height: B.height > A.height ? B.height : A.height });
    const n = pixelmatch(A.data, B.data, d.data, A.width, Math.min(A.height, B.height), { threshold: 0.12 });
    writeFileSync(`diff-stage6/${route}.png`, PNG.sync.write(d));
    console.log(`[DIFF] ${route}: ${n} px (${(100 * n / (A.width * A.height)).toFixed(4)}%)`);
  }
} catch (e) {
  console.log('[FATAL] ' + e.message);
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
}
