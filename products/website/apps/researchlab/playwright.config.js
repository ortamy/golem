const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  testMatch: ['smoke.spec.js', 'dashboard-probe.spec.js'],
  timeout: 90_000,
  workers: 1,
  fullyParallel: false,
  reporter: [['list'], ['json', { outputFile: 'test-results/smoke.json' }]],
  use: { baseURL: 'http://127.0.0.1:4173', channel: 'chrome', ignoreHTTPSErrors: true, trace: 'retain-on-failure' },
  webServer: {
    command: 'python -m http.server 4173',
    cwd: __dirname,
    url: 'http://127.0.0.1:4173/index.html',
    reuseExistingServer: true,
    timeout: 120_000
  },
  projects: [{ name: 'smoke', use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } } }]
});