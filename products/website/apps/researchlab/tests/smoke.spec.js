const fs = require('node:fs');
const path = require('node:path');
const { test, expect } = require('@playwright/test');

const routerPath = path.resolve(__dirname, '..', 'js', 'router.js');
const screenshotDir = path.resolve(__dirname, 'screenshots');
function routesFromRouter() {
  const source = fs.readFileSync(routerPath, 'utf8');
  const match = source.match(/var routedModules = \[(.*?)\];/s);
  if (!match) throw new Error('Could not find routedModules registry in router.js');
  return [...match[1].matchAll(/['"]([^'"]+)['"]/g)].map((item) => item[1]);
}

const routes = routesFromRouter();

function routeFileName(route) {
  return route.replace(/[^a-z0-9а-яё]+/gi, '-').replace(/^-|-$/g, '') || 'dashboard';
}

async function checkRoute(page, route, projectName) {
  const errors = [];
  page.on('console', (message) => {
    if (message.type() === 'error' && !message.text().startsWith('Failed to load resource:')) errors.push(`console: ${message.text()}`);
  });
  page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`));
  await page.goto(`/#${route}`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(200);
  await expect(page.locator('#labContent')).toBeVisible();
  const metrics = await page.evaluate(() => ({
    innerWidth: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth
  }));
  const hasMojibake = await page.locator('#labContent').evaluate((content) => {
    const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT);
    let inspected = 0;
    while (walker.nextNode() && inspected++ < 500) {
      if (/РѕР|Ð|â€”/.test(walker.currentNode.nodeValue || '')) return true;
    }
    return false;
  }, { timeout: 5_000 });
  expect(errors, `uncaught errors on #${route}`).toEqual([]);
  expect(hasMojibake, `mojibake on #${route}`).toBe(false);
  if (projectName === 'mobile') expect(metrics.scrollWidth, `horizontal overflow on #${route}`).toBeLessThanOrEqual(metrics.innerWidth);
  await fs.promises.mkdir(screenshotDir, { recursive: true });
  const viewport = page.viewportSize();
  await page.screenshot({
    path: path.join(screenshotDir, `${routeFileName(route)}-${projectName}.png`),
    clip: { x: 0, y: 0, width: viewport.width, height: viewport.height },
    timeout: 15_000
  });
}

test.describe('registered routes', () => {
  for (const route of routes) {
    test(`route #${route} renders without uncaught errors`, async ({ browser }, testInfo) => {
      for (const viewport of [{ name: 'desktop', width: 1280, height: 800 }, { name: 'mobile', width: 390, height: 844 }]) {
        const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, isMobile: viewport.name === 'mobile' });
        const page = await context.newPage();
        await checkRoute(page, route, viewport.name);
        await context.close();
      }
    });
  }
});

test('agent server offline shows Сервер отключен without uncaught errors', async ({ page }) => {
  const errors = [];
  page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('/#pipelines', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('#labContent')).toBeVisible();
  await expect(page.locator('[data-pipeline-server-status]')).toContainText('Сервер отключен');
  expect(errors).toEqual([]);
});