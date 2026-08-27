/* =============================================================
   screenshot.mjs — скриншот-базлайн Research Lab (Этап 0)
   Матрица: тема (light/white/dark) × маршрут (#dashboard и др.)
   Запуск: npm run baseline   (нужен установленный Google Chrome)
   Выход:  baseline/v0/<theme>/<route>.png + errors.log
   Правило проекта: никакого HTTP-сервера; file:// + Chrome-флаг
   --allow-file-access-from-files для относительных fetch() данных.
   ============================================================= */
import { chromium } from 'playwright-core';
import { pathToFileURL } from 'node:url';
import { mkdirSync, appendFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// === КОНФИГ ===
const APP_INDEX = pathToFileURL(
  'c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/index.html'
).href;

const THEMES = ['light', 'white', 'dark']; // golem_theme из index.html (LabTheme)
const ROUTES = [
  // ядро матрицы (этап 0)
  'dashboard',        // рабочий стол, tool-grid
  'manifest',         // reading-режим, максимальная типографика
  'states',           // карточки состояний
  'dictionaries',     // JSON-словари, research-term-card
  'researches',       // библиотека исследований
  // расширение этапа 5 (layout): разные каркасы и плотности
  'timeline',         // герои-секции + детальный слой
  'scripture-reader', // читалка, собственная оболочка --shell-read
  'generators',       // витрина инструментов .gc-page
  'cartography',      // широкое полотно 1480 (--shell-wide)
  'learn',            // обучающие карточки и игра
  'methodology'       // документная оболочка с выпадашкой разделов
];
const VIEWPORT = { width: 1440, height: 900 };
const TAG = process.argv[2] || 'v0';   // метка версии базлайна: node screenshot.mjs v1

// === ПОДГОТОВКА ===
const outRoot = join(__dirname, 'baseline', TAG);
mkdirSync(outRoot, { recursive: true });
const logFile = join(outRoot, 'errors.log');
if (!existsSync(logFile)) appendFileSync(logFile, `# baseline ${TAG} @ ${new Date().toISOString()}\n`);
const log = (msg) => {
  console.log(msg);
  appendFileSync(logFile, msg + '\n');
};

let browser;
try {
  browser = await chromium.launch({
    channel: 'chrome',            // системный Chrome — без скачивания браузеров
    headless: true,
    args: [
      '--allow-file-access-from-files', // fetch относительных JSON на file://
      '--hide-scrollbars'
    ]
  });

  for (const theme of THEMES) {
    const themeDir = join(outRoot, theme);
    mkdirSync(themeDir, { recursive: true });

    for (const route of ROUTES) {
      // Свежий контекст на каждый кадр: чистый localStorage + init-скрипт темы
      const context = await browser.newContext({ viewport: VIEWPORT, deviceScaleFactor: 1 });
      // Детерминированный офлайн (эпоха Б): внешние http(s) режутся всегда,
      // чтобы снимки не зависели от состояния сети и CDN-шрифтов
      await context.route(/^https?:\/\//, (r) => r.abort());
      await context.addInitScript((t) => {
        try { localStorage.setItem('golem_theme', t); } catch (_) {}
      }, theme);

      const page = await context.newPage();
      const errs = [];
      page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
      page.on('pageerror', (e) => errs.push('pageerror: ' + e.message));

      const url = `${APP_INDEX}#${route}`;
      try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      } catch (e) {
        log(`[WARN] ${theme}/${route}: goto ${e.message.split('\n')[0]}`);
      }
      // Даём роутеру и fetch-данным отрисоваться (file:// — networkidle ненадёжен)
      await page.waitForTimeout(2500);

      const shot = join(themeDir, `${route}.png`);
      await page.screenshot({ path: shot, fullPage: true });

      const dataFail = errs.filter((e) => /fetch|Failed to fetch|CORS|HTTP \d/.test(e)).length;
      log(`[OK] ${theme}/${route} -> ${shot}${errs.length ? ` | console errors: ${errs.length} (data-related: ${dataFail})` : ''}`);
      for (const e of errs.slice(0, 8)) log(`    err: ${e.slice(0, 200)}`);

      await context.close();
    }
  }
  log('[DONE] Базлайн снят. Сравнение после рефакторинга: node screenshot.mjs v1 + попиксельная сверка каталогов.');
} catch (e) {
  log(`[FATAL] ${e.message}`);
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
}
