// Детерминированный сборщик связного палео-образа без внешней модели.
(function(root, factory) {
  var api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.PaleoWeaver = api;
}(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this), function() {
  'use strict';

  var SUBJECTS = ['вместилище', 'сила', 'связка', 'откровение', 'поток', 'вершина'];
  var VERBS = {
    'направление': 'направляет', 'фиксация': 'фиксирует', 'разрушение': 'разрушает',
    'захват': 'захватывает', 'действие': 'действует', 'откровение': 'открывает'
  };
  var GOALS = { 'вершина': 'к вершине', 'откровение': 'к откровению' };
  var MEANS = ['разрушение', 'действие', 'поток', 'огонь'];
  var ACCUSATIVE = { 'сила': 'силу', 'связка': 'связку', 'вершина': 'вершину', 'откровение': 'откровение', 'поток': 'поток', 'вместилище': 'вместилище' };
  var GENITIVE = { 'сила': 'силы', 'связка': 'связки', 'вершина': 'вершины', 'откровение': 'откровения', 'поток': 'потока', 'вместилище': 'вместилища' };

  function normal(value) { return String(value || '').toLocaleLowerCase('ru-RU').trim(); }
  function unique(list) { return list.filter(function(value, index) { return list.indexOf(value) === index; }); }
  function first(list, allowed) { return list.filter(function(value) { return allowed.indexOf(value) !== -1; })[0] || ''; }

  function readWord(chain) {
    var values = (chain || []).map(normal).filter(Boolean);
    var subject = first(values, SUBJECTS) || values[0] || 'образ';
    var verbKey = values.indexOf('направление') !== -1 ? 'направление' : '';
    var verb = VERBS[verbKey] || 'направляет';
    var subjectIndex = values.indexOf(subject);
    var object = values.slice(subjectIndex + 1).filter(function(value) {
      return SUBJECTS.indexOf(value) !== -1 && !GOALS[value];
    })[0] || '';
    var goalKey = first(values, Object.keys(GOALS));
    var goal = goalKey ? GOALS[goalKey] : '';
    var means = unique(values.filter(function(value) { return MEANS.indexOf(value) !== -1 && value !== verbKey; })).slice(0, 2);
    var result = subject + ', которое ' + verb;
    if (object && object !== subject) result += ' ' + (ACCUSATIVE[object] || object);
    if (goal && goalKey !== object) result += ' ' + goal;
    if (means.length) result += ' через ' + means.join(' и ');
    if (values.indexOf('фиксация') !== -1) result += ', фиксируя ход';
    return result + '.';
  }

  function readVerse(chains) {
    var readings = (chains || []).map(readWord);
    if (!readings.length) return '';
    return readings.map(function(reading, index) {
      var sentence = reading.replace(/\.$/, '');
      return index ? sentence.charAt(0).toLocaleLowerCase('ru-RU') + sentence.slice(1) : sentence;
    }).join(', затем ') + '.';
  }

  function verseFunction(chains) {
    var functions = unique((chains || []).reduce(function(all, chain) { return all.concat(chain || []); }, []).map(normal).filter(Boolean)).slice(0, 3);
    var primary = functions[2] || functions[1] || functions[0] || '';
    var path = functions[1] || functions[0] || '';
    return primary ? 'направление ' + (GENITIVE[primary] || primary) + (path ? ' через ' + (ACCUSATIVE[path] || path) : '') + '.' : 'Сборка палео-функций требует проверки.';
  }

  return { readWord: readWord, readVerse: readVerse, verseFunction: verseFunction };
}));