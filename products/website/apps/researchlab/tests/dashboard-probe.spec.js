const fs = require('node:fs');
const path = require('node:path');
const { test } = require('@playwright/test');

const traceDir = path.resolve(__dirname, '..', 'test-results');

function withTimeout(promise, timeoutMs, label) {
  let timer;
  const timeout = new Promise((resolve) => {
    timer = setTimeout(() => resolve({ timedOut: true, label }), timeoutMs);
  });
  return Promise.race([promise.then((value) => ({ timedOut: false, value })), timeout])
    .finally(() => clearTimeout(timer));
}

async function stopTracing(client) {
  const complete = new Promise((resolve) => client.once('Tracing.tracingComplete', resolve));
  await client.send('Tracing.end').catch(() => {});
  const result = await withTimeout(complete, 5_000, 'Tracing.tracingComplete');
  if (result.timedOut || !result.value || !result.value.stream) return Buffer.alloc(0);
  const chunks = [];
  let eof = false;
  while (!eof) {
    const chunk = await client.send('IO.read', { handle: result.value.stream });
    if (chunk.data) chunks.push(Buffer.from(chunk.data));
    eof = chunk.eof;
  }
  await client.send('IO.close', { handle: result.value.stream }).catch(() => {});
  return Buffer.concat(chunks);
}

test('dashboard main-thread probe', async ({ page }, testInfo) => {
  test.setTimeout(90_000);
  const events = [];
  page.on('console', (message) => events.push({ type: 'console', level: message.type(), text: message.text() }));
  page.on('pageerror', (error) => events.push({ type: 'pageerror', text: error.message, stack: error.stack }));

  const client = await page.context().newCDPSession(page);
  await client.send('Tracing.start', {
    categories: 'devtools.timeline,v8.execute,disabled-by-default-devtools.timeline',
    transferMode: 'ReturnAsStream'
  });

  const navigation = await withTimeout(page.goto('/#dashboard', { waitUntil: 'domcontentloaded' }), 10_000, 'goto');
  await page.waitForTimeout(2_500).catch(() => {});
  const evaluate = await withTimeout(page.evaluate(() => 1), 5_000, 'page.evaluate(() => 1)');
  const trace = await stopTracing(client);

  await fs.promises.mkdir(traceDir, { recursive: true });
  await fs.promises.writeFile(path.join(traceDir, 'dashboard-trace.json'), trace);
  await fs.promises.writeFile(path.join(traceDir, 'dashboard-probe.json'), JSON.stringify({
    navigation,
    evaluate,
    events,
    route: testInfo.project.name
  }, null, 2));

  testInfo.attachments.push({ name: 'dashboard-trace', contentType: 'application/json', path: path.join(traceDir, 'dashboard-trace.json') });
  testInfo.attachments.push({ name: 'dashboard-probe', contentType: 'application/json', path: path.join(traceDir, 'dashboard-probe.json') });
  console.log(JSON.stringify({ navigation, evaluate, events }, null, 2));
});