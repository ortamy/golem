/* verify-nav.mjs — проверка навигации Этапа 6 на живом приложении.
   Проверяет: фильтр сайдбара, открытие/закрытие палитры, поиск,
   переход по Enter, мост хедер-поиска. Код выхода 0 = все PASS. */
import { chromium } from 'playwright-core';
import { pathToFileURL } from 'node:url';

const URL = pathToFileURL(
  'c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/index.html'
).href + '#dashboard';

const browser = await chromium.launch({
  channel: 'chrome',
  headless: true,
  args: ['--allow-file-access-from-files', '--hide-scrollbars']
});
const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
// Детерминированный офлайн (эпоха Б): внешний CDN режется, локальные либы достаточно
await context.route(/^https?:\/\//, (r) => r.abort());
const page = await context.newPage();

let ok = true;
const check = (name, pass, extra = '') => {
  console.log(`[${pass ? 'PASS' : 'FAIL'}] ${name}${extra ? ' — ' + extra : ''}`);
  ok = ok && pass;
};

await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
await page.waitForSelector('a.sidebar-item', { timeout: 15000 });
await page.waitForTimeout(500); // даём инициализаторам модулей догнать DOM

// 1. Модуль жив и проиндексировал навигацию
const idx = await page.evaluate(() => ({
  total: document.querySelectorAll('a.sidebar-item').length,
  filter: !!document.getElementById('labNavFilter'),
  api: !!(window.LabNav && window.LabNav.openPalette)
}));
check('фильтр установлен', idx.filter);
check('API палитры доступно', idx.api);

// 2. Фильтр скрывает лишнее, сброс возвращает всё
const before = await page.evaluate(() =>
  [...document.querySelectorAll('a.sidebar-item')].filter(i => i.style.display !== 'none').length);
await page.fill('#labNavFilter', 'чекеры');
await page.waitForTimeout(50);
const filtered = await page.evaluate(() =>
  [...document.querySelectorAll('a.sidebar-item')].filter(i => i.style.display !== 'none').length);
check('фильтр сокращает список', filtered > 0 && filtered < before, `${filtered}/${before}`);
await page.fill('#labNavFilter', '');
await page.waitForTimeout(50);
const restored = await page.evaluate(() =>
  [...document.querySelectorAll('a.sidebar-item')].filter(i => i.style.display !== 'none').length);
check('сброс фильтра восстанавливает', restored === before, `${restored}`);

// 3. Палитра: Ctrl+K -> ввод -> Enter -> переход
await page.keyboard.press('Control+k');
await page.waitForSelector('.lab-palette-backdrop', { state: 'visible', timeout: 5000 });
check('Ctrl+K открывает палитру', true);
await page.keyboard.type('таймлайн');
await page.waitForTimeout(80);
const opts = await page.locator('.lab-palette-item').count();
check('поиск находит пункт', opts >= 1, `${opts} вариант(ов)`);
await page.keyboard.press('Enter');
await page.waitForTimeout(300);
const hash = await page.evaluate(() => location.hash);
check('Enter переходит по модулю', hash === '#timeline', hash);

// 4. Esc закрывает; клик по мёртвому хедер-поиску открывает
check('палитра закрылась после перехода', await page.evaluate(() =>
  getComputedStyle(document.querySelector('.lab-palette-backdrop')).display === 'none'));
await page.keyboard.press('Control+k');
await page.waitForSelector('.lab-palette-backdrop', { state: 'visible' });
await page.keyboard.press('Escape');
check('Escape закрывает палитру', await page.evaluate(() =>
  getComputedStyle(document.querySelector('.lab-palette-backdrop')).display === 'none'));
await page.click('#globalSearch');
await page.waitForSelector('.lab-palette-backdrop', { state: 'visible' });
check('клик по хедер-поиску открывает палитру', true);
await page.keyboard.press('Escape');

await browser.close();
console.log(ok ? '\n=== ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ ===' : '\n=== ЕСТЬ ОТКАЗЫ ===');
process.exit(ok ? 0 : 1);
