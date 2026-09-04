# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: smoke.spec.js >> agent server offline shows Сервер отключен without uncaught errors
- Location: tests\smoke.spec.js:66:1

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: locator('[data-pipeline-server-status]')
Expected substring: "Сервер отключен"
Received string:    "Проверка сервера…"
Timeout: 5000ms

Call log:
  - Expect "toContainText" with timeout 5000ms
  - waiting for locator('[data-pipeline-server-status]')
    4 × locator resolved to <div data-status="checking" class="pipeline-server-status" data-pipeline-server-status="">…</div>
      - unexpected value "Проверка сервера…"

```

```yaml
- text: Проверка сервера…
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
  46 |   await page.screenshot({
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
> 72 |   await expect(page.locator('[data-pipeline-server-status]')).toContainText('Сервер отключен');
     |                                                               ^ Error: expect(locator).toContainText(expected) failed
  73 |   expect(errors).toEqual([]);
  74 | });
```