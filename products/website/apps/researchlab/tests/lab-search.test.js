'use strict';
const assert = require('assert');
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync(require('path').join(__dirname, '..', 'js', 'lab-search.js'), 'utf8');
const sandbox = { window: {}, document: { readyState: 'loading', addEventListener() {} }, console };
vm.runInNewContext(source, sandbox);
const search = sandbox.window.LabSearch;
assert.strictEqual(search.normalize(' Ёлка  '), 'елка');
assert.strictEqual(search.search('кор').length, 0);
assert.strictEqual(typeof search.load, 'function');
search.load().then(function (items) {
  assert.ok(Array.isArray(items));
  assert.ok(items.some(function (item) { return item.type === 'module'; }));
  console.log('OK lab-search: API, нормализация и fallback без fetch');
}).catch(function (error) {
  console.error(error);
  process.exitCode = 1;
});