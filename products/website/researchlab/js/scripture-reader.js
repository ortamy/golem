// Scripture Reader: stage 1 verse browsing.
const ScriptureReader = (function() {
  'use strict';

  var state = {
    initialized: false,
    verses: [],
    currentVerse: 0,
    selectedIndexes: [],
    roots: []
  };

  var LETTERS = {
    'א': { paleo: '𐤀', name: 'Алеф', image: 'бык', meaning: 'сила' },
    'ב': { paleo: '𐤁', name: 'Бет', image: 'дом', meaning: 'вместилище' },
    'ג': { paleo: '𐤂', name: 'Гимель', image: 'верблюд', meaning: 'движение' },
    'ד': { paleo: '𐤃', name: 'Далет', image: 'дверь', meaning: 'вход' },
    'ה': { paleo: '𐤄', name: 'Хе', image: 'дыхание', meaning: 'откровение' },
    'ו': { paleo: '𐤅', name: 'Вав', image: 'крюк', meaning: 'соединение' },
    'ז': { paleo: '𐤆', name: 'Заин', image: 'оружие', meaning: 'инструмент' },
    'ח': { paleo: '𐤇', name: 'Хет', image: 'ограда', meaning: 'отделение' },
    'ט': { paleo: '𐤈', name: 'Тет', image: 'змея', meaning: 'оборачивание' },
    'י': { paleo: '𐤉', name: 'Йод', image: 'рука', meaning: 'действие' },
    'כ': { paleo: '𐤊', name: 'Каф', image: 'ладонь', meaning: 'удержание' },
    'ך': { paleo: '𐤊', name: 'Каф (софит)', image: 'ладонь', meaning: 'удержание' },
    'ל': { paleo: '𐤋', name: 'Ламед', image: 'посох', meaning: 'направление' },
    'מ': { paleo: '𐤌', name: 'Мем', image: 'вода', meaning: 'течение' },
    'ם': { paleo: '𐤌', name: 'Мем (софит)', image: 'вода', meaning: 'течение' },
    'נ': { paleo: '𐤍', name: 'Нун', image: 'рыба', meaning: 'жизнь' },
    'ן': { paleo: '𐤍', name: 'Нун (софит)', image: 'рыба', meaning: 'жизнь' },
    'ס': { paleo: '𐤎', name: 'Самех', image: 'опора', meaning: 'поддержка' },
    'ע': { paleo: '𐤏', name: 'Аин', image: 'глаз', meaning: 'видение' },
    'פ': { paleo: '𐤐', name: 'Пе', image: 'рот', meaning: 'речь' },
    'ף': { paleo: '𐤐', name: 'Пе (софит)', image: 'рот', meaning: 'речь' },
    'צ': { paleo: '𐤑', name: 'Цаде', image: 'крюк', meaning: 'цель' },
    'ץ': { paleo: '𐤑', name: 'Цаде (софит)', image: 'крюк', meaning: 'цель' },
    'ק': { paleo: '𐤒', name: 'Коф', image: 'игла', meaning: 'окружение' },
    'ר': { paleo: '𐤓', name: 'Реш', image: 'голова', meaning: 'начало' },
    'ש': { paleo: '𐤔', name: 'Шин', image: 'зуб', meaning: 'разрушение' },
    'ת': { paleo: '𐤕', name: 'Тав', image: 'знак', meaning: 'завет' }
  };

  var PALEO_TO_HEBREW = Object.keys(LETTERS).reduce(function(map, hebrew) {
    if (!map[LETTERS[hebrew].paleo]) map[LETTERS[hebrew].paleo] = hebrew;
    return map;
  }, {});

  function get(id) {
    return document.getElementById(id);
  }

  function setLoading(message) {
    var paleo = get('scripture-paleo');
    if (paleo) paleo.textContent = message;
  }

  function renderPaleo(text, hebrew) {
    var paleoWords = String(text || '').split(' ');
    var hebrewWords = String(hebrew || '').split(' ');
    var index = 0;

    return paleoWords.map(function(word, wordIndex) {
      if (!word) return '';
      var hebrewWord = hebrewWords[wordIndex] || '';
      var letters = Array.from(word).map(function(symbol, letterIndex) {
        var hebrewLetter = Array.from(hebrewWord)[letterIndex] || '';
        var html = '<span class="scripture-paleo-letter" data-index="' + index +
          '" data-paleo="' + escapeHtml(symbol) + '" data-hebrew="' + escapeHtml(hebrewLetter) + '">' +
          escapeHtml(symbol) + '</span>';
        index++;
        return html;
      }).join('');
      return '<span class="scripture-paleo-word">' + letters + '</span>';
    }).join(' ');
  }

  function renderVerse() {
    var verse = state.verses[state.currentVerse];
    if (!verse) return;

    var title = get('scripture-verse-title');
    var paleo = get('scripture-paleo');
    var hebrew = get('scripture-hebrew');
    var translit = get('scripture-translit');
    var literal = get('scripture-literal');
    var previous = get('scripture-prev');
    var next = get('scripture-next');
    var analysis = get('scripture-analysis');

    state.selectedIndexes = [];

    if (title) title.textContent = 'Берешит 1:' + verse.verse;
    if (paleo) paleo.innerHTML = renderPaleo(verse.paleo, verse.hebrew);
    if (hebrew) hebrew.textContent = verse.hebrew;
    if (translit) translit.textContent = verse.translit;
    if (literal) literal.textContent = verse.literal;
    if (previous) previous.disabled = state.currentVerse === 0;
    if (next) next.disabled = state.currentVerse === state.verses.length - 1;
    if (analysis) {
      analysis.innerHTML = '<h2>Панель анализа</h2>' +
        '<p class="text-muted">Выберите буквы палео-текста для анализа.</p>';
    }
  }

  function selectedLetters() {
    var paleo = get('scripture-paleo');
    if (!paleo) return [];
    return state.selectedIndexes.slice().sort(function(a, b) { return a - b; }).map(function(index) {
      var letter = paleo.querySelector('[data-index="' + index + '"]');
      if (!letter) return null;
      var hebrew = letter.getAttribute('data-hebrew') || PALEO_TO_HEBREW[letter.getAttribute('data-paleo')] || '';
      return {
        index: index,
        paleo: letter.getAttribute('data-paleo') || '',
        hebrew: hebrew,
        data: LETTERS[hebrew] || { name: 'Неизвестная буква', image: 'образ не найден', meaning: '' }
      };
    }).filter(Boolean);
  }

  function isContiguous(indexes) {
    for (var i = 1; i < indexes.length; i++) {
      if (indexes[i] !== indexes[i - 1] + 1) return false;
    }
    return true;
  }

  function updateLetterState() {
    var paleo = get('scripture-paleo');
    if (!paleo) return;
    paleo.querySelectorAll('.scripture-paleo-letter').forEach(function(letter) {
      var index = Number(letter.getAttribute('data-index'));
      var selected = state.selectedIndexes.indexOf(index) !== -1;
      letter.classList.toggle('is-selected', selected);
      letter.setAttribute('aria-pressed', selected ? 'true' : 'false');
    });
  }

  function renderAnalysis() {
    var analysis = get('scripture-analysis');
    var letters = selectedLetters();
    if (!analysis) return;

    if (letters.length < 2) {
      analysis.innerHTML = '<h2>Панель анализа</h2>' +
        '<p class="text-muted">Выберите ещё одну последовательную букву.</p>';
      return;
    }

    var letterCards = letters.map(function(letter) {
      return '<div class="scripture-analysis-letter">' +
        '<div class="scripture-analysis-paleo">' + escapeHtml(letter.paleo) + '</div>' +
        '<div class="scripture-analysis-name">' + escapeHtml(letter.data.name) + '</div>' +
        '<div class="scripture-analysis-image">' + escapeHtml(letter.data.image) + '</div>' +
        '</div>';
    }).join('');
    var selectedHebrew = letters.map(function(letter) { return letter.hebrew; }).join('');
    var selectedPaleo = letters.map(function(letter) { return letter.paleo; }).join('');
    var root = letters.length <= 4 ? state.roots.filter(function(item) {
      return normalizeHebrew(item.root) === normalizeHebrew(selectedHebrew);
    })[0] : null;
    var image = root && root.image
      ? root.image
      : letters.map(function(letter) { return letter.data.image; }).join(' + ');
    var rootHTML = root
      ? '<div class="scripture-root-result"><strong>Корень <span class="hebrew">' + escapeHtml(root.root) + '</span></strong>' +
        '<div>' + escapeHtml(root.meaning || '') + '</div>' +
        (root.examples && root.examples.length ? '<ul>' + root.examples.map(function(example) {
          return '<li>' + escapeHtml(example) + '</li>';
        }).join('') + '</ul>' : '') +
        '</div>'
      : '<div class="scripture-hypothesis"><strong>Гипотетический смысл</strong><div>' + escapeHtml(image) + '</div>' +
        '<small>Образная интерпретация, корень не найден в словаре.</small></div>';

    analysis.innerHTML = '<h2>Панель анализа</h2>' +
      '<div class="scripture-analysis-letters">' + letterCards + '</div>' +
      '<p class="scripture-composite"><strong>Составной образ:</strong> ' + escapeHtml(image) + '</p>' +
      '<p class="scripture-selection"><span class="scripture-selection-paleo">' + escapeHtml(selectedPaleo) + '</span> → <span class="hebrew">' + escapeHtml(selectedHebrew) + '</span></p>' +
      rootHTML;
  }

  function normalizeHebrew(value) {
    return String(value || '')
      .replace(/[\u0591-\u05C7]/g, '')
      .replace(/[ךםןףץ]/g, function(letter) {
        return { 'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ' }[letter];
      })
      .replace(/[\s\-־]/g, '');
  }

  function handleLetterClick(event) {
    var letter = event.target.closest('.scripture-paleo-letter');
    if (!letter) return;
    if (!event.ctrlKey && !event.metaKey) {
      if (typeof LabToast !== 'undefined') LabToast.show('Зажмите Ctrl и нажмите на последовательные буквы.');
      return;
    }

    event.preventDefault();
    var index = Number(letter.getAttribute('data-index'));
    var position = state.selectedIndexes.indexOf(index);
    if (position !== -1) {
      state.selectedIndexes.splice(position, 1);
    } else {
      var sorted = state.selectedIndexes.slice().sort(function(a, b) { return a - b; });
      if (sorted.length >= 4) {
        if (typeof LabToast !== 'undefined') LabToast.show('Можно выбрать не более четырёх букв.');
        return;
      }
      if (sorted.length && index !== sorted[0] - 1 && index !== sorted[sorted.length - 1] + 1) {
        if (typeof LabToast !== 'undefined') LabToast.show('Выбирайте последовательные соседние буквы.');
        return;
      }
      state.selectedIndexes.push(index);
    }
    var sortedSelection = state.selectedIndexes.slice().sort(function(a, b) { return a - b; });
    if (!isContiguous(sortedSelection)) state.selectedIndexes = [];
    updateLetterState();
    renderAnalysis();
  }

  function moveVerse(step) {
    var nextIndex = state.currentVerse + step;
    if (nextIndex < 0 || nextIndex >= state.verses.length) return;
    state.currentVerse = nextIndex;
    renderVerse();
  }

  function bindEvents() {
    var previous = get('scripture-prev');
    var next = get('scripture-next');
    var book = get('scripture-book-select');
    var paleo = get('scripture-paleo');

    if (previous) previous.addEventListener('click', function() { moveVerse(-1); });
    if (next) next.addEventListener('click', function() { moveVerse(1); });
    if (book) book.addEventListener('change', function() {
      state.currentVerse = 0;
      renderVerse();
    });
    if (paleo) paleo.addEventListener('click', handleLetterClick);
  }

  function load() {
    setLoading('Загрузка Берешит…');
    return Promise.all([
      fetch('data/scripture/bereshit-1.json').then(function(response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      }),
      fetch('data/roots.json').then(function(response) {
        if (!response.ok) throw new Error('roots.json HTTP ' + response.status);
        return response.json();
      })
    ]).then(function(results) {
        var data = results[0];
        if (!Array.isArray(data) || !data.length) throw new Error('Пустой набор стихов');
        state.verses = data;
        state.roots = Array.isArray(results[1]) ? results[1] : [];
        state.currentVerse = 0;
        renderVerse();
      })
      .catch(function(error) {
        var module = get('scripture-reader');
        if (module) {
          module.innerHTML = '<div class="lab-alert lab-alert-error scripture-reader-error">Ошибка загрузки текста: ' +
            escapeHtml(error.message) + '</div>';
        }
      });
  }

  function init() {
    if (state.initialized || !get('scripture-reader')) return;
    state.initialized = true;
    bindEvents();
    load();
  }

  return { init: init, renderVerse: renderVerse };
})();