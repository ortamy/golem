# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: smoke.spec.js >> registered routes >> route #state-analyzer renders without uncaught errors
- Location: tests\smoke.spec.js:55:5

# Error details

```
TimeoutError: page.screenshot: Timeout 15000ms exceeded.
Call log:
  - taking page screenshot

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
    - navigation [ref=e8]:
      - button "Переключить тему" [ref=e9] [cursor=pointer]
      - link "Сайт" [ref=e10] [cursor=pointer]:
        - /url: ../../
      - link "GitHub" [ref=e11] [cursor=pointer]:
        - /url: https://github.com/ortamy/golem
  - generic [ref=e12]:
    - complementary [ref=e13]:
      - generic [ref=e14]:
        - searchbox "Фильтр навигации" [ref=e16]
        - link "Манифест" [ref=e17] [cursor=pointer]:
          - /url: "#manifest"
        - link "Рабочий стол" [ref=e18] [cursor=pointer]:
          - /url: "#dashboard"
        - link "Мастерская" [ref=e19] [cursor=pointer]:
          - /url: "#workbench"
        - link "Палео-клуб" [ref=e20] [cursor=pointer]:
          - /url: "#club"
        - generic [ref=e21]:
          - generic [ref=e22] [cursor=pointer]: Данные
          - generic [ref=e24]:
            - link "Книгочтение" [ref=e25] [cursor=pointer]:
              - /url: "#scripture-reader"
            - link "Обучение" [ref=e26] [cursor=pointer]:
              - /url: "#learn"
            - link "Словари" [ref=e27] [cursor=pointer]:
              - /url: "#dictionaries"
            - link "Исследования" [ref=e28] [cursor=pointer]:
              - /url: "#researches"
            - link "Методология" [ref=e29] [cursor=pointer]:
              - /url: "#methodology"
            - link "Палео-механика" [ref=e30] [cursor=pointer]:
              - /url: "#paleo-mechanics"
            - link "Палео-лингвистика" [ref=e31] [cursor=pointer]:
              - /url: "#paleo-linguistics"
            - link "Карта языков" [ref=e32] [cursor=pointer]:
              - /url: "#language-map"
            - link "Картография" [ref=e33] [cursor=pointer]:
              - /url: "#cartography"
            - link "Карта состояний" [ref=e34] [cursor=pointer]:
              - /url: "#states"
            - link "Палео-таймлайн" [ref=e35] [cursor=pointer]:
              - /url: "#timeline"
            - link "Религионизмы" [ref=e36] [cursor=pointer]:
              - /url: "#religionisms"
        - generic [ref=e37]:
          - generic [ref=e38] [cursor=pointer]: Инструменты
          - generic [ref=e40]:
            - link "Палео-конструктор" [ref=e41] [cursor=pointer]:
              - /url: "#paleo-builder"
            - link "Палео-клавиатура" [ref=e42] [cursor=pointer]:
              - /url: "#paleo-keyboard"
            - link "Генераторы" [ref=e43] [cursor=pointer]:
              - /url: "#generators"
            - link "Чекеры" [ref=e44] [cursor=pointer]:
              - /url: "#checkers"
            - link "Компаратор" [ref=e45] [cursor=pointer]:
              - /url: "#translation-comparator"
            - link "Анализаторы" [ref=e46] [cursor=pointer]:
              - /url: "#analyzers"
        - generic [ref=e47]:
          - generic [ref=e48] [cursor=pointer]: AI
          - generic [ref=e50]:
            - link "Агенты" [ref=e51] [cursor=pointer]:
              - /url: "#ai-agents"
            - link "Пайплайны" [ref=e52] [cursor=pointer]:
              - /url: "#pipelines"
            - link "Запуск сервера" [ref=e53] [cursor=pointer]:
              - /url: "#agent-server"
            - link "Нейрочат" [ref=e54] [cursor=pointer]:
              - /url: "#ed-chat"
            - link "Анализ изображений" [ref=e55] [cursor=pointer]:
              - /url: "#vision"
        - generic [ref=e56]:
          - generic [ref=e57] [cursor=pointer]: Система
          - link "Настройки" [ref=e60] [cursor=pointer]:
            - /url: "#admin-settings"
    - main [ref=e61]:
      - generic [ref=e62]:
        - region [ref=e63]:
          - generic [ref=e64]:
            - paragraph [ref=e65]:
              - link "ГОЛЕМ" [ref=e66] [cursor=pointer]:
                - /url: "#dashboard"
              - text: ·
              - link "State Analyzer" [ref=e67] [cursor=pointer]:
                - /url: "#state-analyzer"
            - heading "state analyzer" [level=1] [ref=e68]
        - generic [ref=e70]:
          - generic [ref=e72]:
            - heading "Анализатор состояний (Теhилим)" [level=1] [ref=e73]
            - paragraph [ref=e74]: Выберите состояние потока и получите связанный псалом с краткой диагностикой.
          - generic [ref=e75]:
            - generic [ref=e76]:
              - generic [ref=e77]: Состояние
              - combobox "Состояние" [ref=e78]:
                - option "Выберите состояние" [selected]
                - option "Мидбар"
                - option "Шамаим"
                - option "Эрец"
                - option "Мицраим"
                - option "Тоху"
                - option "Хошех"
                - option "Ракиа"
                - option "Эден"
              - paragraph [ref=e79]: Псалом и диагностика загружаются из локального набора данных Research Lab.
            - generic [ref=e80]: Выберите состояние, чтобы открыть псалом.
  - contentinfo [ref=e82]:
    - link "Проект «Голем»" [ref=e83] [cursor=pointer]:
      - /url: ../pages/index.html
    - text: — восстановление истины. |
    - link "GitHub" [ref=e84] [cursor=pointer]:
      - /url: https://github.com/ortamy/golem
    - text: "| v0.2.0"
  - generic "Горячие клавиши" [ref=e85] [cursor=pointer]: ⌨ ?
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