# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: smoke.spec.js >> root etymology modal >> shows the unpublished fallback for a root without etymology data
- Location: tests\smoke.spec.js:114:3

# Error details

```
TimeoutError: page.waitForSelector: Timeout 20000ms exceeded.
Call log:
  - waiting for locator('[data-root-id="אבא"]') to be visible

```

# Test source

```ts
  20  |   'club',
  21  |   'workbench',
  22  |   'scripture-reader',
  23  |   'researches',
  24  |   'cartography'
  25  | ]);
  26  | const routesToCheck = process.env.SMOKE_QUICK === '1' ? routes.filter((route) => quickRoutes.has(route)) : routes;
  27  | 
  28  | function routeFileName(route) {
  29  |   return route.replace(/[^a-z0-9а-яё]+/gi, '-').replace(/^-|-$/g, '') || 'dashboard';
  30  | }
  31  | 
  32  | async function checkRoute(page, route, projectName) {
  33  |   const errors = [];
  34  |   page.on('console', (message) => {
  35  |     if (message.type() === 'error' && !message.text().startsWith('Failed to load resource:')) errors.push(`console: ${message.text()}`);
  36  |   });
  37  |   page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`));
  38  |   await page.goto(`/#${route}`, { waitUntil: 'domcontentloaded' });
  39  |   await expect(page.locator('#labContent')).toBeVisible();
  40  |   const metrics = await page.evaluate(() => ({
  41  |     innerWidth: window.innerWidth,
  42  |     scrollWidth: document.documentElement.scrollWidth
  43  |   }));
  44  |   const hasMojibake = await page.locator('#labContent').evaluate((content) => {
  45  |     const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT);
  46  |     let inspected = 0;
  47  |     while (walker.nextNode() && inspected++ < 500) {
  48  |       if (/РѕР|Ð|â€”/.test(walker.currentNode.nodeValue || '')) return true;
  49  |     }
  50  |     return false;
  51  |   }, { timeout: 5_000 });
  52  |   expect(errors, `uncaught errors on #${route}`).toEqual([]);
  53  |   expect(hasMojibake, `mojibake on #${route}`).toBe(false);
  54  |   if (projectName === 'mobile') expect(metrics.scrollWidth, `horizontal overflow on #${route}`).toBeLessThanOrEqual(metrics.innerWidth);
  55  |   if (process.env.SMOKE_QUICK === '1') return;
  56  |   await page.addStyleTag({ content: '* { animation: none !important; transition: none !important; caret-color: transparent !important; }' });
  57  |   await fs.promises.mkdir(screenshotDir, { recursive: true });
  58  |   const viewport = page.viewportSize();
  59  |   const client = await page.context().newCDPSession(page);
  60  |   const screenshot = await client.send('Page.captureScreenshot', {
  61  |     format: 'png',
  62  |     clip: { x: 0, y: 0, width: viewport.width, height: viewport.height, scale: 1 }
  63  |   });
  64  |   await fs.promises.writeFile(path.join(screenshotDir, `${routeFileName(route)}-${projectName}.png`), Buffer.from(screenshot.data, 'base64'));
  65  |   await client.detach();
  66  | }
  67  | 
  68  | test.describe('registered routes', () => {
  69  |   for (const route of routesToCheck) {
  70  |     test(`route #${route} renders without uncaught errors`, async ({ browser }, testInfo) => {
  71  |       for (const viewport of [{ name: 'desktop', width: 1280, height: 800 }, { name: 'mobile', width: 390, height: 844 }]) {
  72  |         const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, isMobile: viewport.name === 'mobile' });
  73  |         const page = await context.newPage();
  74  |         await checkRoute(page, route, viewport.name);
  75  |         await context.close();
  76  |       }
  77  |     });
  78  |   }
  79  | });
  80  | 
  81  | test('agent server offline shows Сервер отключен without uncaught errors', async ({ page }) => {
  82  |   const errors = [];
  83  |   await page.route('http://127.0.0.1:5000/**', (route) => route.abort());
  84  |   page.on('pageerror', (error) => errors.push(error.message));
  85  |   await page.goto('/#pipelines', { waitUntil: 'domcontentloaded' });
  86  |   await expect(page.locator('#labContent')).toBeVisible();
  87  |   await expect(page.locator('[data-pipeline-server-status]')).toHaveAttribute('data-status', /offline|error/, { timeout: 15_000 });
  88  |   await expect(page.locator('[data-pipeline-server-status]')).toContainText('Сервер отключен', { timeout: 5_000 });
  89  |   expect(errors).toEqual([]);
  90  | });
  91  | 
  92  | test.describe('root etymology modal', () => {
  93  |   test('loads pilot data, caches it, and handles keyboard/backdrop close', async ({ page }) => {
  94  |     let requests = 0;
  95  |     page.on('request', (request) => {
  96  |       if (decodeURIComponent(request.url()).includes('/data/roots/etymology/')) requests += 1;
  97  |     });
  98  |     await page.goto('/#root-dictionary/search/AV', { waitUntil: 'domcontentloaded' });
  99  |     await page.waitForSelector('[data-root-id="אב"]', { timeout: 20_000 });
  100 |     const card = page.locator('[data-root-id="אב"]');
  101 |     await card.press('Enter');
  102 |     await expect(page.locator('#labModal')).toHaveClass(/show/);
  103 |     await expect(page.locator('#modalBody')).toContainText('Пра-форма');
  104 |     expect(requests).toBe(1);
  105 |     await page.keyboard.press('Escape');
  106 |     await expect(page.locator('#labModal')).not.toHaveClass(/show/);
  107 |     await card.press(' ');
  108 |     await expect(page.locator('#modalBody')).toContainText('Когнаты');
  109 |     expect(requests).toBe(1);
  110 |     await page.mouse.click(5, 5);
  111 |     await expect(page.locator('#labModal')).not.toHaveClass(/show/);
  112 |   });
  113 | 
  114 |   test('shows the unpublished fallback for a root without etymology data', async ({ page }) => {
  115 |     const roots = require('../data/roots/roots.json');
  116 |     const fs = require('node:fs');
  117 |     const path = require('node:path');
  118 |     const root = roots.find((item) => !fs.existsSync(path.join(__dirname, '..', 'data', 'roots', 'etymology', `${item.root}.json`)));
  119 |     await page.goto(`/#root-dictionary/search/${encodeURIComponent(root.translit)}`, { waitUntil: 'domcontentloaded' });
> 120 |     await page.waitForSelector(`[data-root-id="${root.root}"]`, { timeout: 20_000 });
      |                ^ TimeoutError: page.waitForSelector: Timeout 20000ms exceeded.
  121 |     await page.locator(`[data-root-id="${root.root}"]`).click();
  122 |     await expect(page.locator('#modalBody')).toContainText('Разбор готовится');
  123 |   });
  124 | 
  125 |   test('retries a failed etymology request', async ({ page }) => {
  126 |     let requests = 0;
  127 |     // Glob-паттерны Playwright не гарантируют матчинг percent-encoded Hebrew,
  128 |     // поэтому перехватываем по декодированному pathname.
  129 |     await page.route((url) => decodeURIComponent(url.pathname).indexOf('/data/roots/etymology/') === 0, async (route) => {
  130 |       requests += 1;
  131 |       if (requests === 1) return route.abort();
  132 |       return route.continue();
  133 |     });
  134 |     await page.goto('/#root-dictionary/search/AM', { waitUntil: 'domcontentloaded' });
  135 |     await page.waitForSelector('[data-root-id="אם"]', { timeout: 20_000 });
  136 |     await page.locator('[data-root-id="אם"]').click();
  137 |     await expect(page.locator('[data-rem-retry]')).toBeVisible();
  138 |     await page.locator('[data-rem-retry]').click();
  139 |     await expect(page.locator('#modalBody')).toContainText('Семантические сдвиги');
  140 |     expect(requests).toBe(2);
  141 |   });
  142 | });
  143 | 
  144 | test.describe('checkers module cards', () => {
  145 |   // Поведенческая проверка: клик по карточке-модулю на #checkers меняет
  146 |   // location.hash на её маршрут. Селектор `.gc-card[href^="#"]` берёт только
  147 |   // якорные карточки — карточки-описания без собственного маршрута пропускаются.
  148 |   test('clicking a module card sets location.hash to its route', async ({ browser }) => {
  149 |     const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  150 |     const page = await context.newPage();
  151 |     const pageErrors = [];
  152 |     page.on('pageerror', (error) => pageErrors.push(error.message));
  153 | 
  154 |     await page.goto('/#checkers', { waitUntil: 'domcontentloaded' });
  155 |     await page.waitForSelector('.gc-card[href^="#"]', { timeout: 20_000 });
  156 | 
  157 |     const cards = await page.$$eval('.gc-card[href^="#"]', (nodes) => nodes.map((node) => ({
  158 |       hash: node.getAttribute('href'),
  159 |       title: (node.querySelector('.gc-card-title') || node).textContent.trim()
  160 |     })));
  161 |     expect(cards.length, 'маршрутизируемых карточек .gc-card на #checkers').toBeGreaterThan(0);
  162 | 
  163 |     // Даём отложенной перерисовке модуля завершиться: router дёргает
  164 |     // handleHash повторно на load+100ms, PageController заменяет innerHTML —
  165 |     // клик, попавший в это окно, не синтезирует click-событие.
  166 |     await page.waitForTimeout(1000);
  167 | 
  168 |     for (const card of cards) {
  169 |       const cardSelector = `.gc-card[href="${card.hash}"]`;
  170 |       // Возврат на #checkers перед каждым кликом; на первом проходе это no-op.
  171 |       await page.evaluate(() => { window.location.hash = '#checkers'; });
  172 |       await page.waitForSelector(cardSelector, { timeout: 20_000 });
  173 | 
  174 |       // Клик + ожидание смены hash; один повтор на случай гонки с перерисовкой.
  175 |       let actualHash = null;
  176 |       let navigated = false;
  177 |       for (let attempt = 0; attempt < 2 && !navigated; attempt++) {
  178 |         if (attempt > 0) {
  179 |           await page.evaluate(() => { window.location.hash = '#checkers'; });
  180 |           await page.waitForSelector(cardSelector, { timeout: 20_000 });
  181 |         }
  182 |         await page.click(cardSelector);
  183 |         try {
  184 |           await expect(async () => {
  185 |             actualHash = await page.evaluate(() => window.location.hash);
  186 |             expect(actualHash).toBe(card.hash);
  187 |           }).toPass({ timeout: 4_000 });
  188 |           navigated = true;
  189 |         } catch (error) {
  190 |           if (attempt === 1) {
  191 |             throw new Error(`Карточка «${card.title}»: ожидался hash ${card.hash}, фактически ${actualHash} (после повтора)`);
  192 |           }
  193 |         }
  194 |       }
  195 |     }
  196 | 
  197 |     expect(pageErrors, 'uncaught errors при навигации по карточкам #checkers').toEqual([]);
  198 |     await context.close();
  199 |   });
  200 | });
```