// Shared Paleo-Hebrew alphabet data and conversion helpers.
(function(root, factory) {
  var api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.PaleoLetters = api;
}(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this), function() {
  'use strict';

  var byHebrew = {
    'א': { paleo: '𐤀', name: 'Алеф', image: 'бык', meaning: 'сила', translit: 'ʼ' },
    'ב': { paleo: '𐤁', name: 'Бет', image: 'дом', meaning: 'вместилище', translit: 'B' },
    'ג': { paleo: '𐤂', name: 'Гимель', image: 'верблюд', meaning: 'движение', translit: 'G' },
    'ד': { paleo: '𐤃', name: 'Далет', image: 'дверь', meaning: 'вход', translit: 'D' },
    'ה': { paleo: '𐤄', name: 'Хе', image: 'дыхание', meaning: 'откровение', translit: 'H' },
    'ו': { paleo: '𐤅', name: 'Вав', image: 'крюк', meaning: 'соединение', translit: 'W' },
    'ז': { paleo: '𐤆', name: 'Заин', image: 'оружие', meaning: 'инструмент', translit: 'Z' },
    'ח': { paleo: '𐤇', name: 'Хет', image: 'ограда', meaning: 'отделение', translit: 'Ḥ' },
    'ט': { paleo: '𐤈', name: 'Тет', image: 'змея', meaning: 'оборачивание', translit: 'Ṭ' },
    'י': { paleo: '𐤉', name: 'Йод', image: 'рука', meaning: 'действие', translit: 'Y' },
    'כ': { paleo: '𐤊', name: 'Каф', image: 'ладонь', meaning: 'удержание', translit: 'K' },
    'ך': { paleo: '𐤊', name: 'Каф (софит)', image: 'ладонь', meaning: 'удержание', translit: 'K' },
    'ל': { paleo: '𐤋', name: 'Ламед', image: 'посох', meaning: 'направление', translit: 'L' },
    'מ': { paleo: '𐤌', name: 'Мем', image: 'вода', meaning: 'течение', translit: 'M' },
    'ם': { paleo: '𐤌', name: 'Мем (софит)', image: 'вода', meaning: 'течение', translit: 'M' },
    'נ': { paleo: '𐤍', name: 'Нун', image: 'рыба', meaning: 'жизнь', translit: 'N' },
    'ן': { paleo: '𐤍', name: 'Нун (софит)', image: 'рыба', meaning: 'жизнь', translit: 'N' },
    'ס': { paleo: '𐤎', name: 'Самех', image: 'опора', meaning: 'поддержка', translit: 'S' },
    'ע': { paleo: '𐤏', name: 'Аин', image: 'глаз', meaning: 'видение', translit: 'ʻ' },
    'פ': { paleo: '𐤐', name: 'Пе', image: 'рот', meaning: 'речь', translit: 'P' },
    'ף': { paleo: '𐤐', name: 'Пе (софит)', image: 'рот', meaning: 'речь', translit: 'P' },
    'צ': { paleo: '𐤑', name: 'Цаде', image: 'крюк', meaning: 'цель', translit: 'Ṣ' },
    'ץ': { paleo: '𐤑', name: 'Цаде (софит)', image: 'крюк', meaning: 'цель', translit: 'Ṣ' },
    'ק': { paleo: '𐤒', name: 'Коф', image: 'игла', meaning: 'окружение', translit: 'Q' },
    'ר': { paleo: '𐤓', name: 'Реш', image: 'голова', meaning: 'начало', translit: 'R' },
    'ש': { paleo: '𐤔', name: 'Шин', image: 'зуб', meaning: 'разрушение', translit: 'Š' },
    'ת': { paleo: '𐤕', name: 'Тав', image: 'знак', meaning: 'завет', translit: 'T' }
  };

  var paleoToHebrew = Object.keys(byHebrew).reduce(function(result, hebrew) {
    var paleo = byHebrew[hebrew].paleo;
    // Prefer the non-final form as the canonical reverse mapping.
    if (!result[paleo] || 'ךםןףץ'.indexOf(result[paleo]) !== -1) result[paleo] = hebrew;
    return result;
  }, {});

  var finalToBase = { 'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ' };

  function normalizeHebrew(value) {
    return String(value || '')
      .replace(/[\u0591-\u05C7]/g, '')
      .replace(/[ךםןףץ]/g, function(letter) { return finalToBase[letter]; })
      .replace(/[\s\-־]/g, '');
  }

  function toPaleo(value) {
    return Array.from(String(value || '')).map(function(char) {
      var entry = byHebrew[char];
      return entry ? entry.paleo : char;
    }).join('');
  }

  function toHebrew(value) {
    return Array.from(String(value || '')).map(function(char) {
      return paleoToHebrew[char] || char;
    }).join('');
  }

  function canSearchRoot(value) {
    var length = Array.from(String(value || '')).length;
    return length >= 2 && length <= 4;
  }

  return {
    byHebrew: byHebrew,
    paleoToHebrew: paleoToHebrew,
    normalizeHebrew: normalizeHebrew,
    toPaleo: toPaleo,
    toHebrew: toHebrew,
    canSearchRoot: canSearchRoot
  };
}));
