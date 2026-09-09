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

const withDataSandbox = {
  window: {
    fetch: function (url) {
      const files = {
        'data/roots/roots.json': [{ translit: 'AV', root: 'אב', meaning: 'источник' }, { translit: 'ABA', root: 'אבא', meaning: 'отец' }],
        'data/roots/root-links.json': [{ from: 'AV', to: 'ABA', type: 'example', source: 'researcher', confidence: 'confirmed', note: 'Расширенная форма' }],
        'data/dictionaries.json': {},
        'data/methodology/cards.json': [],
        'data/qumran-books.json': { books: [] }
      };
      return Promise.resolve({ ok: true, json: function () { return Promise.resolve(files[url]); } });
    }
  },
  document: { readyState: 'loading', addEventListener() {} },
  console
};
vm.runInNewContext(source, withDataSandbox);
withDataSandbox.window.LabSearch.load().then(function (items) {
  const links = items.filter(function (item) { return item.type === 'root-link'; });
  assert.strictEqual(links.length, 1);
  assert.strictEqual(links[0].route, 'root-dictionary/graph/AV');
  assert.ok(links[0].keywords.indexOf('aba') !== -1);
  assert.strictEqual(withDataSandbox.window.LabSearch.search('confirmed')[0], links[0]);
  assert.strictEqual(withDataSandbox.window.LabSearch.search('Расширенная')[0], links[0]);
  console.log('OK lab-search: root links and graph routes');
}).catch(function (error) {
  console.error(error);
  process.exitCode = 1;
});