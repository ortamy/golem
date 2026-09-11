import { chromium } from 'playwright';

const browser = await chromium.launch({ channel: 'chrome' });
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
const errors = [];
page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));

await page.goto('http://127.0.0.1:4173/index.html#root-dictionary/search/AV', { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(5000);

const state = await page.evaluate(() => ({
  rootsCount: (window._roots || []).length,
  cards: [...document.querySelectorAll('[data-root-id]')].slice(0, 5).map((n) => n.getAttribute('data-root-id')),
  cardCount: document.querySelectorAll('[data-root-id]').length,
  rdListChildren: (document.getElementById('rd-list') || {}).childElementCount,
  rdListText: ((document.getElementById('rd-list') || {}).textContent || '').slice(0, 160),
  spinnerVisible: !!(document.getElementById('rd-spinner') || {}).classList,
  etyApi: typeof window.RootEtymologyModal,
  modalApi: typeof window.LabModal,
  swController: !!(navigator.serviceWorker && navigator.serviceWorker.controller),
  hash: location.hash,
  labContentHead: ((document.getElementById('labContent') || {}).textContent || '').replace(/\s+/g, ' ').slice(0, 200)
}));
console.log('STATE ' + JSON.stringify(state, null, 2));

const fetchCheck = await page.evaluate(async () => {
  try {
    const r = await fetch('data/roots/roots.json');
    const t = await r.text();
    const j = JSON.parse(t);
    return { ok: true, count: j.length, head: t.slice(0, 80) };
  } catch (e) {
    return { ok: false, err: String(e) };
  }
});
console.log('FETCH ' + JSON.stringify(fetchCheck));
console.log('ERRORS ' + (errors.length ? errors.join(' || ') : 'none'));

await browser.close();
