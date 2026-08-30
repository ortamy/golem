/* wb-e2e.mjs — полный прогон конвейера book-translation: форма → смета →
   прогресс → проект → вьювер «оригинал ↔ перевод» → «Мои проекты» → перезагрузка.
   Запуск: node tools/design-baseline/wb-e2e.mjs */
import { chromium } from 'playwright-core';
import { pathToFileURL } from 'node:url';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const URL = pathToFileURL('c:/Users/DELL/Desktop/golem-main/products/website/apps/researchlab/index.html').href;

const book = [
  'Песок держит след ноги недолго, но след всё же был.',
  'Дом — это не стены, а то, что стены удерживают: тепло, спор, сон.',
  'Вода не спорит с камнем. Она проходит и оставляет русло.'
].join('\n\n');
const dir = mkdtempSync(join(tmpdir(), 'wb-e2e-'));
const filePath = join(dir, 'kniga.txt');
writeFileSync(filePath, book, 'utf8');

const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--allow-file-access-from-files'] });
const page = await browser.newPage();
const errors = [];
page.on('pageerror', function (e) { errors.push(String(e)); });

await page.goto(URL + '#workbench/run/book-translation', { waitUntil: 'load' });
await page.waitForSelector('#wb-run-form', { timeout: 8000 });

// Загружаем файл, ждём чтения FileReader
await page.setInputFiles('#wb-field-file', filePath);
await page.waitForFunction(function () {
  return document.getElementById('wb-field-file-status').textContent.indexOf('знаков') !== -1;
}, null, { timeout: 8000 });
const fileStatus = await page.locator('#wb-field-file-status').textContent();
console.log('DIAG статус файла:', fileStatus);

// Смета
await page.locator('#wb-estimate-btn').click();
const estimate = await page.locator('#wb-estimate-body').textContent();
if (!/Токены/.test(estimate)) throw new Error('Смета не показала токены: ' + estimate);
console.log('OK  смета:', estimate.replace(/\s+/g, ' ').trim().slice(0, 120));

// Старт → прогресс по этапам
await page.locator('#wb-start-btn').click();
await page.waitForSelector('.wb-steps .wb-step', { timeout: 8000 });
const cancelVisible = await page.locator('[data-wb-action="cancel"]').count();
if (!cancelVisible) throw new Error('Кнопка [Отмена] не видна во время запуска');
console.log('OK  прогресс пошёл, кнопка [Отмена] на месте');

// Ждём завершения и автоперехода на проект
await page.waitForSelector('.wb-pair', { timeout: 20000 });
const pairs = await page.locator('.wb-pair').count();
if (pairs !== 3) throw new Error('Фрагментов во вьювере: ' + pairs);
const pairText = await page.locator('.wb-pair').first().textContent();
if (!/Оригинал/.test(pairText) || !/Перевод/.test(pairText)) throw new Error('Параллельный вид не собрался');
if (!/Песок держит след/.test(pairText)) throw new Error('Оригинал не отображается');
console.log('OK  проект открыт: вьювер «оригинал ↔ перевод», фрагментов: ' + pairs);

// Проект в «Мои проекты»
const meta = await page.evaluate(function () {
  return JSON.parse(localStorage.getItem('golem.workbench.projects') || '[]');
});
if (!meta.length) throw new Error('localStorage пуст — мета не сохранилась');
if (meta[0].status !== 'done' || !meta[0].progress || meta[0].progress.percent !== 100) throw new Error('Мета проекта не завершена: ' + JSON.stringify(meta[0]));
if (meta[0].result || meta[0].segments) throw new Error('В localStorage попал результат — должны быть только метаданные');
console.log('OK  localStorage: мета проекта со статусом done, результата в хранилище нет');

// Перезагрузка: проект переживает reload, результат — в памяти
await page.reload({ waitUntil: 'load' });
await page.waitForTimeout(800);
await page.goto(URL + '#workbench', { waitUntil: 'load' });
await page.waitForTimeout(600);
await page.waitForSelector('.wb-project-row', { timeout: 8000 });
const rowText = await page.locator('.wb-project-row').first().textContent();
if (!/Готово/.test(rowText)) throw new Error('Проект не отображается после перезагрузки: ' + rowText);
console.log('OK  после перезагрузки проект в «Моих проектах» со статусом Готово');

// Повторное открытие проекта после перезагрузки: результат держался в памяти
await page.locator('.wb-project-name').first().click();
await page.waitForTimeout(600);
const reopened = await page.locator('#workbench').textContent();
if (!/Результат держался в памяти/.test(reopened) && !/Взор: перевод/.test(reopened)) {
  throw new Error('После перезагрузки проект не открылся корректно');
}
console.log('OK  повторное открытие проекта после reload (в памяти или честный lost-result)');

if (errors.length) {
  console.error('JS-ОШИБКИ:', errors);
  process.exit(1);
}
await browser.close();
console.log('E2E ПРОЙДЕН');
