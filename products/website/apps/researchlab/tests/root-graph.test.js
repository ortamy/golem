'use strict';

const assert = require('assert');
const Graph = require('../js/root-graph.js');

const roots = [
  { translit: 'AV', paleo: ['𐤀', '𐤁'], meaning: 'источник' },
  { translit: 'ABA', paleo: ['𐤀', '𐤁', '𐤀'], meaning: 'отец' },
  { translit: 'AMN', paleo: ['𐤀', '𐤌', '𐤍'], meaning: 'надёжность' }
];
const manual = [{ from: 'AV', to: 'AMN', type: 'semantic-field', confidence: 'hypothesis', source: 'researcher', note: 'проверить' }];

assert.strictEqual(Graph.rootId(roots[0]), 'AV');
assert.strictEqual(Graph.paleo(roots[0]), '𐤀𐤁');
assert.strictEqual(Graph.isPaleo('𐤀𐤁'), true);
assert.strictEqual(Graph.isPaleo('אב'), false);
assert.strictEqual(Graph.getRootById(roots, 'av'), roots[0]);
assert.ok(Graph.buildComputedLinks(roots).some(link => link.from === 'AV' && link.to === 'ABA'));
const merged = Graph.mergeLinks(roots, manual);
assert.strictEqual(merged.filter(link => link.from === 'AV' && link.to === 'AMN')[0].confidence, 'hypothesis');
assert.deepStrictEqual(Graph.localGraph(roots, merged, 'AV').nodes.map(root => root.translit), ['AV', 'AMN', 'ABA']);
assert.strictEqual(merged.every(link => !/[א-ת]/.test(link.note + link.from + link.to)), true);
console.log('OK: root graph scenarios passed');