/* wb-smoke.cjs — живая проверка «Мастерской» (#workbench) в headless Chrome.
   Запуск: node tools/design-baseline/wb-smoke.cjs */
import { chromium } from 'playwright-core';
import { pathToFileURL } from 'node:url';

const APP = 'c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/index.html';
const URL = pathToFileURL(APP).href;

const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--allow-file-access-from-files'] });
const page = await browser.newPage();
const errors = [];
page.on('pageerror', function (e) { errors.push(String(e)); });

async function open(hash) {
  await page.goto(URL + '#' + hash, { waitUntil: 'load' });
  await page.waitForTimeout(600);
}

// 1. Хаб
await open('workbench');
await page.waitForSelector('.wb-pipeline-card', { timeout: 8000 });
const cards = await page.locator('.wb-pipeline-card').count();
if (cards !== 3) throw new Error('Карточек конвейеров: ' + cards + ', ожидалось 3');
const heroTitle = await page.locator('#workbench .lab-hero__title').first().textContent();
if (!/Мастерская/.test(heroTitle)) throw new Error('Шапка хаба: ' + heroTitle);
const crumb = await page.locator('#workbench .lab-hero__kicker').first().textContent();
if (!/ГОЛЕМ/.test(crumb)) throw new Error('Крошки хаба: ' + crumb);
const empty = await page.locator('#workbench').textContent();
if (!/Пока пусто/.test(empty)) throw new Error('Список проектов не пустой при первом входе');
console.log('OK  #workbench: 3 карточки, шапка «Мастерская», крошки, пустой список проектов');

// 2. Экран запуска book-translation
await open('workbench/run/book-translation');
await page.waitForSelector('#wb-run-form', { timeout: 8000 });
const fileInputs = await page.locator('#wb-run-form input[type=file]').count();
const selects = await page.locator('#wb-run-form select').count();
const toggles = await page.locator('#wb-run-form .wb-toggle input').count();
if (fileInputs !== 1 || selects !== 2 || toggles !== 2) throw new Error('Форма: file=' + fileInputs + ' select=' + selects + ' toggle=' + toggles);
const estimateBtn = await page.locator('#wb-estimate-btn').textContent();
const startBtn = await page.locator('#wb-start-btn').textContent();
if (!/Оценить/.test(estimateBtn) || !/Старт/.test(startBtn)) throw new Error('Кнопки сметы отсутствуют');
const runTitle = await page.locator('#workbench .lab-hero__title').first().textContent();
if (!/Перевод книги/.test(runTitle)) throw new Error('Шапка запуска: ' + runTitle);
console.log('OK  #workbench/run/book-translation: форма из конфига (файл, 2 селекта, 2 тумблера), [Оценить][Старт], шапка из реестра');

// 3. Смета по вставленному тексту (вход text отсутствует у этого конвейера — проверяем пустую смету и валидацию)
await page.locator('#wb-estimate-btn').click();
const estimateText = await page.locator('#wb-estimate-body').textContent();
if (!/смета нулевая/.test(estimateText) && !/знаков/.test(estimateText)) throw new Error('Смета не отрисовалась: ' + estimateText);
await page.locator('#wb-start-btn').click();
const formStatus = await page.locator('#wb-form-status').textContent();
if (!/Заполните вход/.test(formStatus)) throw new Error('Валидация не сработала: ' + formStatus);
console.log('OK  смета и валидация входа работают');

// 4. Проект: несуществующий runId → аккуратный empty-state
await open('workbench/project/no-such-run');
await page.waitForTimeout(400);
const projectText = await page.locator('#workbench').textContent();
if (!/Проект не найден/.test(projectText)) throw new Error('Empty-state проекта не показан');
console.log('OK  #workbench/project/<нет>: аккуратный empty-state');

// 5. Другие конвейеры: свои формы
await open('workbench/run/exposure-check');
await page.waitForSelector('#wb-run-form', { timeout: 8000 });
const ta = await page.locator('#wb-run-form textarea').count();
if (ta !== 1) throw new Error('exposure-check: нет textarea');
await open('workbench/run/root-assembly');
await page.waitForSelector('#wb-run-form', { timeout: 8000 });
const wordInput = await page.locator('#wb-run-form input[type=text]').count();
if (wordInput !== 1) throw new Error('root-assembly: нет поля слова');
console.log('OK  exposure-check и root-assembly открывают свои формы');

if (errors.length) {
  console.error('JS-ОШИБКИ НА СТРАНИЦЕ:', errors);
  process.exit(1);
}
await browser.close();
console.log('SMOKE ПРОЙДЕН');
