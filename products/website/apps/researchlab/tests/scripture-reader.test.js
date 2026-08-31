'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const PaleoLetters = require('../js/paleo-letters.js');

const rootsPath = path.join(__dirname, '..', 'data', 'roots', 'roots.json');
const roots = JSON.parse(fs.readFileSync(rootsPath, 'utf8'));
const bereshitPath = path.join(__dirname, '..', 'data', 'scripture', 'bereshit-1.json');
const bereshit = JSON.parse(fs.readFileSync(bereshitPath, 'utf8'));
const booksPath = path.join(__dirname, '..', 'data', 'qumran-books.json');
const books = JSON.parse(fs.readFileSync(booksPath, 'utf8')).books;
const readerSource = fs.readFileSync(path.join(__dirname, '..', 'js', 'scripture-reader.js'), 'utf8');
const PaleoWeaver = require('../js/paleo-weaver.js');

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

assert.strictEqual(
  PaleoWeaver.readWord(['вместилище', 'вершина', 'сила', 'разрушение', 'действие', 'фиксация']),
  'вместилище, которое направляет силу к вершине через разрушение и действие, фиксируя ход.'
);
assert.strictEqual(
  PaleoWeaver.verseFunction([['вместилище', 'вершина', 'сила', 'разрушение']]),
  'направление силы через вершину.'
);

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

books.forEach(function(book) {
  assert.ok(book.dataFile, 'Для книги подключён файл данных: ' + book.id);
  const file = path.join(__dirname, '..', 'data', 'scripture', book.dataFile + '.json');
  assert.ok(fs.existsSync(file), 'Файл данных существует: ' + book.dataFile);
  const verses = JSON.parse(fs.readFileSync(file, 'utf8'));
  assert.ok(verses.length > 0, 'Книга содержит стихи: ' + book.id);
  assert.ok(verses.every(function(verse) {
    return verse.hebrew && verse.paleo && Array.isArray(verse.words) && verse.words.length;
  }), 'Нет пропусков в слоях книги: ' + book.id);
  assert.ok(verses.every(function(verse) {
    return PaleoLetters.toPaleo(PaleoLetters.normalizeHebrew(verse.hebrew)) === verse.paleo.replace(/\s/g, '');
  }), 'Палео-графика синхронизирована: ' + book.id);
  assert.ok(verses.every(function(verse) {
    return verse.paleo_translation && ['draft', 'review', 'verified'].includes(verse.paleo_translation_status);
  }), 'У каждого стиха есть маркированная палео-сборка: ' + book.id);
});

assert.ok(readerSource.includes('scripture-meaning-card'), 'Смысловая сборка выводится отдельной карточкой');
assert.ok(readerSource.includes('scripture-assembly-details'), 'Технический след сворачивается в details');
assert.ok(readerSource.includes('scripture-constructor-chips'), 'Палео-конструктор выводит глиф-чипы');
assert.ok(readerSource.includes('scripture-glyph-tooltip'), 'У глиф-чипов есть тултипы образов');
assert.ok(readerSource.includes('meaningPass.verse_reading'), 'Meaning-pass имеет приоритет для связного образа');
assert.ok(readerSource.includes('meaningPass.verse_function'), 'Meaning-pass имеет отдельную функцию стиха');
assert.ok(!readerSource.includes('escapeHtml(verseTranslation.toUpperCase())'), 'Смысловая сборка не переводится в верхний регистр');
assert.ok(!readerSource.includes('escapeHtml(verseFunction.toUpperCase())'), 'Функция стиха не переводится в верхний регистр');

console.log('OK: PaleoLetters and Scripture Reader core scenarios passed');
