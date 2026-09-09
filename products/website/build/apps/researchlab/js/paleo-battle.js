/* Чистая модель «Палео-битвы»: карточки, очки, матч и local-first storage. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.PaleoBattle = factory();
}(typeof window !== 'undefined' ? window : this, function () {
  'use strict';

  var STORAGE_KEY = 'golem_paleo_battle';
  var MATCH_ROUNDS = 5;
  var STATUS = ['факт', 'интерпретация', 'гипотеза'];

  function text(value) { return String(value == null ? '' : value).trim(); }
  function normalize(value) { return text(value).toLocaleLowerCase('ru-RU').replace(/[ё]/g, 'е').replace(/\s+/g, ' '); }
  function includesAnswer(answer, expected) {
    var actual = normalize(answer), target = normalize(expected);
    return !!target && (actual === target || actual.indexOf(target) !== -1 || target.indexOf(actual) !== -1 && actual.length > 2);
  }
  function makeCards(roots, letters) {
    roots = Array.isArray(roots) ? roots : [];
    var byKey = {};
    (letters || []).forEach(function (letter) { byKey[letter.hebrew] = letter; });
    return roots.map(function (entry, index) {
      var word = text(entry && entry.root), chars = Array.from(word);
      var chain = chars.map(function (char) {
        var letter = byKey[char] || {};
        return { hebrew: char, paleo: letter.paleo || '', name: letter.name || '', meaning: letter.meaning || '' };
      });
      if (chain.some(function (part) { return !part.paleo; }) && Array.isArray(entry.paleo)) {
        chain = entry.paleo.map(function (paleo, i) { return { hebrew: chars[i] || '', paleo: paleo, name: '', meaning: (entry.paleoMeanings || [])[i] || '' }; });
      }
      if (word.length < 2 || !chain.length) return null;
      return {
        id: 'root-' + index + '-' + word,
        word: word,
        chain: chain,
        image: text(entry.image || entry.meaning),
        function: text(entry.function || entry.action || 'сборка образа через буквенную цепочку'),
        reconstruction: text(entry.reconstruction || entry.meaning || entry.image),
        status: STATUS.indexOf(entry.status) !== -1 ? entry.status : 'интерпретация',
        source: text(entry.source || 'корневой словарь')
      };
    }).filter(Boolean);
  }
  function fallbackCards() {
    return [{ id: 'fallback-av', word: 'אב', chain: [{ hebrew: 'א', paleo: '𐤀', name: 'Алеф', meaning: 'сила' }, { hebrew: 'ב', paleo: '𐤁', name: 'Бет', meaning: 'вместилище' }], image: 'Сила дома — отец, источник семьи', function: 'образ источника в доме', reconstruction: 'отец, родоначальник, источник', status: 'интерпретация', source: 'локальный fallback' }];
  }
  function selectCards(cards, count, random) {
    var list = (cards && cards.length ? cards : fallbackCards()).slice();
    var result = [], pick = random || Math.random;
    while (list.length && result.length < (count || MATCH_ROUNDS)) result.push(list.splice(Math.floor(pick() * list.length), 1)[0]);
    return result;
  }
  function createRoomCode(random) { return String(1000 + Math.floor((random || Math.random)() * 9000)); }
  function createMatch(cards, names) {
    names = names || {};
    return { version: 1, roomCode: createRoomCode(), status: 'question', round: 0, currentPlayer: 0, players: [{ name: text(names.a) || 'Исследователь А', score: 0, streak: 0 }, { name: text(names.b) || 'Исследователь Б', score: 0, streak: 0 }], cards: selectCards(cards), history: [], startedAt: new Date().toISOString() };
  }
  function scorePart(correct, points, hinted) { return correct ? Math.round(points * (hinted ? 0.5 : 1)) : 0; }
  function scoreRound(question, answer, hintsUsed) {
    question = question || {}; answer = answer || {}; hintsUsed = Number(hintsUsed || 0) > 0;
    var checks = { image: includesAnswer(answer.image, question.image), function: includesAnswer(answer.function, question.function), sequence: normalize(answer.sequence) === normalize(question.word), explanation: normalize(answer.explanation).length >= 12, status: normalize(answer.status) === normalize(question.status) };
    var weights = { image: 100, function: 50, sequence: 100, explanation: 50, status: 25 }, points = 0;
    Object.keys(checks).forEach(function (key) { points += scorePart(checks[key], weights[key], hintsUsed); });
    return { points: points, maxPoints: hintsUsed ? 163 : 325, accuracy: Math.round(Object.keys(checks).filter(function (key) { return checks[key]; }).length / 5 * 100), checks: checks, confidence: text(answer.confidence) || 'не указана', reviewRequired: !checks.sequence || !checks.explanation || answer.confidence === 'низкая' };
  }
  function achievements(match) {
    var history = match.history || [], earned = [];
    if (history.some(function (round) { return round.result.accuracy === 100; })) earned.push('Точная сборка');
    if (history.filter(function (round) { return round.result.checks.sequence; }).length >= 3) earned.push('След потока');
    if (history.some(function (round) { return round.result.checks.explanation; })) earned.push('Голос Давар');
    if (history.some(function (round) { return round.result.checks.status; })) earned.push('Эмет прежде Хошеха');
    if (history.length === MATCH_ROUNDS * 2) earned.push('Исследователь поля');
    return earned;
  }
  function submitRound(match, answer) {
    if (!match || match.status !== 'question' || !match.cards[match.round]) return match;
    var player = match.players[match.currentPlayer], result = scoreRound(match.cards[match.round], answer);
    player.score += result.points; player.streak = result.accuracy === 100 ? player.streak + 1 : 0;
    match.history.push({ round: match.round + 1, player: match.currentPlayer, answer: answer || {}, result: result });
    match.status = 'review';
    return match;
  }
  function nextRound(match) {
    if (!match || match.status !== 'review') return match;
    if (match.currentPlayer === 0) { match.currentPlayer = 1; match.status = 'question'; return match; }
    if (match.round + 1 >= match.cards.length) { match.status = 'finished'; return match; }
    match.round += 1; match.currentPlayer = 0; match.status = 'question'; return match;
  }
  function winner(match) {
    if (!match || match.players[0].score === match.players[1].score) return 'draw';
    return match.players[0].score > match.players[1].score ? 0 : 1;
  }
  function save(match, storage) { try { (storage || localStorage).setItem(STORAGE_KEY, JSON.stringify(match)); return true; } catch (e) { return false; } }
  function load(storage) { try { var value = JSON.parse((storage || localStorage).getItem(STORAGE_KEY)); return value && value.version === 1 ? value : null; } catch (e) { return null; } }
  return { STORAGE_KEY: STORAGE_KEY, MATCH_ROUNDS: MATCH_ROUNDS, STATUS: STATUS, makeCards: makeCards, fallbackCards: fallbackCards, selectCards: selectCards, createRoomCode: createRoomCode, createMatch: createMatch, scoreRound: scoreRound, submitRound: submitRound, nextRound: nextRound, winner: winner, achievements: achievements, save: save, load: load };
}));