'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const PaleoLetters = require('../js/paleo-letters.js');

const rootsPath = path.join(__dirname, '..', 'data', 'roots', 'roots.json');
const roots = JSON.parse(fs.readFileSync(rootsPath, 'utf8'));
const bereshitPath = path.join(__dirname, '..', 'data', 'scripture', 'bereshit-1.json');
const bereshit = JSON.parse(fs.readFileSync(bereshitPath, 'utf8'));

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

assert.strictEqual(bereshit.length, 1533, 'Берешит содержит полный корпус из 1533 стихов');
assert.ok(bereshit.every(function(verse) {
  return verse.hebrew && verse.paleo && Array.isArray(verse.words) && verse.words.length;
}), 'У каждого стиха есть квадратный и палео-слой');
assert.ok(bereshit.every(function(verse) {
  return verse.words.every(function(word) { return word.hebrew && word.paleo; });
}), 'У каждого слова есть квадратная и палео-графика');
assert.ok(bereshit.every(function(verse) {
  return PaleoLetters.toPaleo(PaleoLetters.normalizeHebrew(verse.hebrew)) === verse.paleo.replace(/\s/g, '');
}), 'Палео-строка механически соответствует согласному квадратному слою');

console.log('OK: PaleoLetters and Scripture Reader core scenarios passed');
