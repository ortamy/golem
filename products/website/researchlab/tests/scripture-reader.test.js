'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const PaleoLetters = require('../js/paleo-letters.js');

const rootsPath = path.join(__dirname, '..', 'data', 'roots.json');
const roots = JSON.parse(fs.readFileSync(rootsPath, 'utf8'));

function findRoot(value) {
  const normalized = PaleoLetters.normalizeHebrew(value);
  return roots.find(function(root) {
    return PaleoLetters.normalizeHebrew(root.root) === normalized;
  });
}

function assertContiguous(indexes) {
  for (let i = 1; i < indexes.length; i += 1) {
    assert.strictEqual(
      indexes[i],
      indexes[i - 1] + 1,
      'Индексы должны образовывать последовательный диапазон'
    );
  }
}

assert.strictEqual(Object.keys(PaleoLetters.byHebrew).length, 27);
assert.strictEqual(Object.keys(PaleoLetters.paleoToHebrew).length, 22);

assert.strictEqual(PaleoLetters.toHebrew('𐤀𐤁'), 'אב');
assert.strictEqual(PaleoLetters.toPaleo('אב'), '𐤀𐤁');
assert.strictEqual(PaleoLetters.normalizeHebrew(' אָב '), 'אב');
assert.strictEqual(PaleoLetters.normalizeHebrew('ךםןףץ'), 'כמנפצ');
assert.strictEqual(PaleoLetters.canSearchRoot('אב'), true);
assert.strictEqual(PaleoLetters.canSearchRoot('אבד'), true);
assert.strictEqual(PaleoLetters.canSearchRoot('אבדד'), true);
assert.strictEqual(PaleoLetters.canSearchRoot('א'), false);
assert.strictEqual(PaleoLetters.canSearchRoot('אבדדה'), false);

Object.keys(PaleoLetters.paleoToHebrew).forEach(function(paleo) {
  const hebrew = PaleoLetters.paleoToHebrew[paleo];
  assert.strictEqual(PaleoLetters.toPaleo(hebrew), paleo);
  assert.strictEqual(PaleoLetters.toHebrew(paleo), hebrew);
});

const av = findRoot('אב');
assert.ok(av, 'Корень אב должен находиться в roots.json');
assert.strictEqual(av.meaning, 'отец, родоначальник, источник');
assert.deepStrictEqual(av.paleo, ['𐤀', '𐤁']);

assert.strictEqual(findRoot('𐤀𐤁'), undefined);
assert.strictEqual(findRoot('א ב'), av);
assert.strictEqual(findRoot('ך'), undefined);

assert.doesNotThrow(function() { assertContiguous([4, 5, 6, 7]); });
assert.throws(function() { assertContiguous([4, 6]); }, /последовательный диапазон/);
assert.doesNotThrow(function() { assertContiguous([1, 2, 3, 4, 5]); });

console.log('OK: PaleoLetters and Scripture Reader core scenarios passed');