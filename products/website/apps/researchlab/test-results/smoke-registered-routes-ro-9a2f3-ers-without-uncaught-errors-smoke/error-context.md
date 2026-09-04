# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: smoke.spec.js >> registered routes >> route #exposure-editor renders without uncaught errors
- Location: tests\smoke.spec.js:55:5

# Error details

```
TimeoutError: page.screenshot: Timeout 15000ms exceeded.
Call log:
  - taking page screenshot
  - waiting for fonts to load...

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - banner [ref=e2]:
    - link "ГОЛЕМ Бета-версия" [ref=e3] [cursor=pointer]:
      - /url: "#dashboard"
      - img "ГОЛЕМ" [ref=e4]
      - generic "Бета-версия" [ref=e5]: BETA
    - textbox "Поиск по лаборатории..." [ref=e7]
    - generic [ref=e8]:
      - button "Переключить тему" [ref=e9] [cursor=pointer]
      - link "Сайт" [ref=e10] [cursor=pointer]:
        - /url: ../../
      - link "GitHub" [ref=e11] [cursor=pointer]:
        - /url: https://github.com/ortamy/golem
    - button "Открыть меню" [ref=e12] [cursor=pointer]
  - generic [ref=e13]:
    - complementary [ref=e14]:
      - generic [ref=e15]:
        - searchbox "Фильтр навигации" [ref=e17]
        - link "Манифест" [ref=e18] [cursor=pointer]:
          - /url: "#manifest"
        - link "Рабочий стол" [ref=e19] [cursor=pointer]:
          - /url: "#dashboard"
        - link "Мастерская" [ref=e20] [cursor=pointer]:
          - /url: "#workbench"
        - link "Палео-клуб" [ref=e21] [cursor=pointer]:
          - /url: "#club"
        - generic [ref=e22]:
          - generic [ref=e23] [cursor=pointer]: Данные
          - generic [ref=e25]:
            - link "Книгочтение" [ref=e26] [cursor=pointer]:
              - /url: "#scripture-reader"
            - link "Обучение" [ref=e27] [cursor=pointer]:
              - /url: "#learn"
            - link "Словари" [ref=e28] [cursor=pointer]:
              - /url: "#dictionaries"
            - link "Исследования" [ref=e29] [cursor=pointer]:
              - /url: "#researches"
            - link "Методология" [ref=e30] [cursor=pointer]:
              - /url: "#methodology"
            - link "Палео-механика" [ref=e31] [cursor=pointer]:
              - /url: "#paleo-mechanics"
            - link "Палео-лингвистика" [ref=e32] [cursor=pointer]:
              - /url: "#paleo-linguistics"
            - link "Карта языков" [ref=e33] [cursor=pointer]:
              - /url: "#language-map"
            - link "Картография" [ref=e34] [cursor=pointer]:
              - /url: "#cartography"
            - link "Карта состояний" [ref=e35] [cursor=pointer]:
              - /url: "#states"
            - link "Палео-таймлайн" [ref=e36] [cursor=pointer]:
              - /url: "#timeline"
            - link "Религионизмы" [ref=e37] [cursor=pointer]:
              - /url: "#religionisms"
        - generic [ref=e38]:
          - generic [ref=e39] [cursor=pointer]: Инструменты
          - generic [ref=e41]:
            - link "Палео-конструктор" [ref=e42] [cursor=pointer]:
              - /url: "#paleo-builder"
            - link "Палео-клавиатура" [ref=e43] [cursor=pointer]:
              - /url: "#paleo-keyboard"
            - link "Генераторы" [ref=e44] [cursor=pointer]:
              - /url: "#generators"
            - link "Чекеры" [ref=e45] [cursor=pointer]:
              - /url: "#checkers"
            - link "Компаратор" [ref=e46] [cursor=pointer]:
              - /url: "#translation-comparator"
            - link "Анализаторы" [ref=e47] [cursor=pointer]:
              - /url: "#analyzers"
        - generic [ref=e48]:
          - generic [ref=e49] [cursor=pointer]: AI
          - generic [ref=e51]:
            - link "Агенты" [ref=e52] [cursor=pointer]:
              - /url: "#ai-agents"
            - link "Пайплайны" [ref=e53] [cursor=pointer]:
              - /url: "#pipelines"
            - link "Запуск сервера" [ref=e54] [cursor=pointer]:
              - /url: "#agent-server"
            - link "Нейрочат" [ref=e55] [cursor=pointer]:
              - /url: "#ed-chat"
            - link "Анализ изображений" [ref=e56] [cursor=pointer]:
              - /url: "#vision"
        - generic [ref=e57]:
          - generic [ref=e58] [cursor=pointer]: Система
          - link "Настройки" [ref=e61] [cursor=pointer]:
            - /url: "#admin-settings"
    - main [ref=e62]:
      - generic [ref=e63]:
        - region [ref=e64]:
          - generic [ref=e65]:
            - paragraph [ref=e66]:
              - link "ГОЛЕМ" [ref=e67] [cursor=pointer]:
                - /url: "#dashboard"
              - text: ·
              - link "Редактор разоблачений" [ref=e68] [cursor=pointer]:
                - /url: "#exposure-editor"
            - heading "Редактор разоблачений" [level=1] [ref=e69]
            - paragraph [ref=e72]: Сборка материала, источников и выводов в единое исследовательское дело.
        - generic [ref=e73]: Модуль редактора разоблачений не загрузился.
  - contentinfo [ref=e74]:
    - link "Проект «Голем»" [ref=e75] [cursor=pointer]:
      - /url: ../pages/index.html
    - text: — восстановление истины. |
    - link "GitHub" [ref=e76] [cursor=pointer]:
      - /url: https://github.com/ortamy/golem
    - text: "| v0.2.0"
  - generic "Горячие клавиши" [ref=e77] [cursor=pointer]: ⌨ ?
```

# Test source

```ts
  1  | const fs = require('node:fs');
  2  | const path = require('node:path');
  3  | const { test, expect } = require('@playwright/test');
  4  | 
  5  | const routerPath = path.resolve(__dirname, '..', 'js', 'router.js');
  6  | const screenshotDir = path.resolve(__dirname, 'screenshots');
  7  | function routesFromRouter() {
  8  |   const source = fs.readFileSync(routerPath, 'utf8');
  9  |   const match = source.match(/var routedModules = \[(.*?)\];/s);
  10 |   if (!match) throw new Error('Could not find routedModules registry in router.js');
  11 |   return [...match[1].matchAll(/['"]([^'"]+)['"]/g)].map((item) => item[1]);
  12 | }
  13 | 
  14 | const routes = routesFromRouter();
  15 | 
  16 | function routeFileName(route) {
  17 |   return route.replace(/[^a-z0-9а-яё]+/gi, '-').replace(/^-|-$/g, '') || 'dashboard';
  18 | }
  19 | 
  20 | async function checkRoute(page, route, projectName) {
  21 |   const errors = [];
  22 |   page.on('console', (message) => {
  23 |     if (message.type() === 'error' && !message.text().startsWith('Failed to load resource:')) errors.push(`console: ${message.text()}`);
  24 |   });
  25 |   page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`));
  26 |   await page.goto(`/#${route}`, { waitUntil: 'domcontentloaded' });
  27 |   await page.waitForTimeout(200);
  28 |   await expect(page.locator('#labContent')).toBeVisible();
  29 |   const metrics = await page.evaluate(() => ({
  30 |     innerWidth: window.innerWidth,
  31 |     scrollWidth: document.documentElement.scrollWidth
  32 |   }));
  33 |   const hasMojibake = await page.locator('#labContent').evaluate((content) => {
  34 |     const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT);
  35 |     let inspected = 0;
  36 |     while (walker.nextNode() && inspected++ < 500) {
  37 |       if (/РѕР|Ð|â€”/.test(walker.currentNode.nodeValue || '')) return true;
  38 |     }
  39 |     return false;
  40 |   }, { timeout: 5_000 });
  41 |   expect(errors, `uncaught errors on #${route}`).toEqual([]);
  42 |   expect(hasMojibake, `mojibake on #${route}`).toBe(false);
  43 |   if (projectName === 'mobile') expect(metrics.scrollWidth, `horizontal overflow on #${route}`).toBeLessThanOrEqual(metrics.innerWidth);
  44 |   await fs.promises.mkdir(screenshotDir, { recursive: true });
  45 |   const viewport = page.viewportSize();
> 46 |   await page.screenshot({
     |              ^ TimeoutError: page.screenshot: Timeout 15000ms exceeded.
  47 |     path: path.join(screenshotDir, `${routeFileName(route)}-${projectName}.png`),
  48 |     clip: { x: 0, y: 0, width: viewport.width, height: viewport.height },
  49 |     timeout: 15_000
  50 |   });
  51 | }
  52 | 
  53 | test.describe('registered routes', () => {
  54 |   for (const route of routes) {
  55 |     test(`route #${route} renders without uncaught errors`, async ({ browser }, testInfo) => {
  56 |       for (const viewport of [{ name: 'desktop', width: 1280, height: 800 }, { name: 'mobile', width: 390, height: 844 }]) {
  57 |         const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, isMobile: viewport.name === 'mobile' });
  58 |         const page = await context.newPage();
  59 |         await checkRoute(page, route, viewport.name);
  60 |         await context.close();
  61 |       }
  62 |     });
  63 |   }
  64 | });
  65 | 
  66 | test('agent server offline shows Сервер отключен without uncaught errors', async ({ page }) => {
  67 |   const errors = [];
  68 |   page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
  69 |   page.on('pageerror', (error) => errors.push(error.message));
  70 |   await page.goto('/#pipelines', { waitUntil: 'domcontentloaded' });
  71 |   await expect(page.locator('#labContent')).toBeVisible();
  72 |   await expect(page.locator('[data-pipeline-server-status]')).toContainText('Сервер отключен');
  73 |   expect(errors).toEqual([]);
  74 | });
```