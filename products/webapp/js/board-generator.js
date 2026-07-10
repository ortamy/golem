/**
 * board-generator.js — Генератор детективных досок
 * Открывает полноценный генератор из research-board/
 */

const BoardGen = (function() {
  'use strict';

  function init() {
    // Готово
  }

  function openFull() {
    window.open('../website/research-board/generator.html', '_blank');
  }

  return {
    init: init,
    openFull: openFull
  };
})();