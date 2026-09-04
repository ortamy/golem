'use strict';
const assert = require('assert');
const Battle = require('../js/paleo-battle.js');

const card = { word: 'אב', image: 'сила дома', function: 'образ источника', reconstruction: 'отец', status: 'интерпретация' };
let result = Battle.scoreRound(card, { image: 'Сила дома', function: 'образ источника', sequence: 'אב', explanation: 'Сила входит в дом как источник', status: 'интерпретация', confidence: 'высокая' });
assert.strictEqual(result.points, 325);
assert.strictEqual(result.accuracy, 100);
assert.strictEqual(result.reviewRequired, false);
result = Battle.scoreRound(card, { sequence: 'אב', explanation: 'коротко', status: 'гипотеза' });
assert.strictEqual(result.points, 100);
assert.strictEqual(result.reviewRequired, true);

const cards = [1, 2, 3, 4, 5, 6].map((n) => ({ id: String(n), word: 'אב', chain: [], image: '', function: '', reconstruction: '', status: 'интерпретация' }));
const match = Battle.createMatch(cards, { a: 'А', b: 'Б' });
assert.match(match.roomCode, /^\d{4}$/);
assert.strictEqual(match.cards.length, 5);
assert.strictEqual(new Set(match.cards.map((item) => item.id)).size, 5);
for (let i = 0; i < 10; i += 1) {
  Battle.submitRound(match, { sequence: 'אב', explanation: 'Содержательное объяснение этапа', status: 'интерпретация' });
  Battle.nextRound(match);
}
assert.strictEqual(match.status, 'finished');
assert.strictEqual(match.history.length, 10);
assert.deepStrictEqual(Battle.winner(match), 'draw');
assert.ok(Battle.achievements(match).length >= 4);
const storage = { value: '', setItem(k, v) { this.value = v; }, getItem() { return this.value; } };
assert.strictEqual(Battle.save(match, storage), true);
assert.strictEqual(Battle.load(storage).history.length, 10);
storage.value = '{broken';
assert.strictEqual(Battle.load(storage), null);
console.log('OK: Paleo Battle scoring, match, achievements and storage');