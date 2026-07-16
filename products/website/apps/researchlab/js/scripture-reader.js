// Scripture Reader: Qumran-attested Tanakh books, grid of cards + verse browsing.
const ScriptureReader = (function() {
  'use strict';

  var state = {
    initialized: false,
    books: [],
    currentBook: null,
    verses: [],
    currentVerse: 0,
    selectedIndexes: [],
    roots: []
  };

  var PALEO = window.PaleoLetters;

  function get(id) {
    return document.getElementById(id);
  }

  function setLoading(message) {
    var paleo = get('scripture-paleo');
    if (paleo) paleo.textContent = message;
  }

  function copyText(text, successMessage) {
    var value = String(text || '').trim();
    if (!value) return Promise.reject(new Error('Нечего копировать'));

    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(value).then(function() {
        if (typeof LabToast !== 'undefined') LabToast.show(successMessage || 'Скопировано в буфер обмена.');
      });
    }

    return new Promise(function(resolve, reject) {
      var textarea = document.createElement('textarea');
      textarea.value = value;
      textarea.setAttribute('readonly', '');
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      try {
        if (!document.execCommand('copy')) throw new Error('Копирование недоступно');
        document.body.removeChild(textarea);
        if (typeof LabToast !== 'undefined') LabToast.show(successMessage || 'Скопировано в буфер обмена.');
        resolve();
      } catch (error) {
        document.body.removeChild(textarea);
        reject(error);
      }
    }).catch(function(error) {
      if (typeof LabToast !== 'undefined') LabToast.show('Не удалось скопировать текст.');
      throw error;
    });
  }

  function currentVerseText() {
    var verse = state.verses[state.currentVerse];
    if (!verse || !state.currentBook) return '';
    return [
      state.currentBook.ru + ' 1:' + verse.verse,
      verse.paleo,
      verse.hebrew,
      verse.translit,
      verse.literal
    ].filter(Boolean).join('\n');
  }

  function copyCurrentVerse() {
    copyText(currentVerseText(), 'Стих скопирован в буфер обмена.');
  }

  function copySelection() {
    var letters = selectedLetters();
    if (!letters.length) return;
    var paleo = letters.map(function(letter) { return letter.paleo; }).join('');
    var hebrew = letters.map(function(letter) { return letter.hebrew; }).join('');
    copyText('Палео-иврит: ' + paleo + '\nИврит: ' + hebrew, 'Выбранный фрагмент скопирован.');
  }

  function copyButtonMarkup(disabled) {
    return '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm scripture-copy-button scripture-copy-selection"' +
      (disabled ? ' disabled' : '') +
      ' aria-label="Копировать выбранное" title="Копировать выбранное">' +
      '<svg class="scripture-copy-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
      '<rect x="8" y="8" width="11" height="11" rx="1.5"></rect>' +
      '<path d="M16 8V5.5A1.5 1.5 0 0 0 14.5 4h-9A1.5 1.5 0 0 0 4 5.5v9A1.5 1.5 0 0 0 5.5 16H8"></path>' +
      '</svg>' +
      '</button>';
  }

  function cleanHebrewWord(word) {
    return String(word || '').replace(/[\u0591-\u05C7]/g, '');
  }

  function paleoWordsFor(hebrew, paleo) {
    var hebrewWords = String(hebrew || '').trim().split(/\s+/).filter(Boolean);
    var paleoWords = String(paleo || '').trim().split(/\s+/).filter(Boolean);

    return hebrewWords.map(function(word, wordIndex) {
      var source = paleoWords[wordIndex] || '';
      var cleanWord = cleanHebrewWord(word);
      // Неполные данные достраиваются из полного иврита.
      if (!source || Array.from(source).length !== Array.from(cleanWord).length) {
        return PALEO.toPaleo(cleanWord);
      }
      return source;
    });
  }

  function renderWordLayer(text, className, wordClass, extraAttributes) {
    var words = String(text || '').trim().split(/\s+/).filter(Boolean);
    var attributes = extraAttributes || function() { return ''; };
    return words.map(function(word, wordIndex) {
      return '<span class="' + className + ' ' + wordClass + '" data-word-index="' + wordIndex + '"' +
        attributes(word, wordIndex) + '>' + escapeHtml(word) + '</span>';
    }).join(' ');
  }

  function renderPaleo(text, hebrew) {
    var paleoWords = paleoWordsFor(hebrew, text);
    var hebrewWords = String(hebrew || '').split(/\s+/).filter(Boolean);
    var index = 0;

    return hebrewWords.map(function(hebrewWord, wordIndex) {
      var word = paleoWords[wordIndex] || PALEO.toPaleo(cleanHebrewWord(hebrewWord));
      if (!word) return '';
      var letters = Array.from(word).map(function(symbol, letterIndex) {
        var hebrewLetter = Array.from(cleanHebrewWord(hebrewWord))[letterIndex] || '';
        var html = '<span class="scripture-paleo-letter" data-index="' + index +
          '" data-paleo="' + escapeHtml(symbol) + '" data-hebrew="' + escapeHtml(hebrewLetter) + '">' +
          escapeHtml(symbol) + '</span>';
        index++;
        return html;
      }).join('');
      return '<span class="scripture-word scripture-paleo-word" data-word-index="' + wordIndex + '">' + letters + '</span>';
    }).join(' ');
  }

  function renderBookGrid() {
    var grid = get('scripture-book-grid');
    if (!grid) return;
    grid.innerHTML = state.books.map(function(book) {
      var badge = book.dataFile
        ? ''
        : '<span class="tool-badge">Скоро</span>';
      return '<a href="#" class="tool-card scripture-book-card" data-book-id="' + escapeHtml(book.id) + '">' +
        '<span class="tool-icon"><img src="../../../..../../assets/icons/32/ui/book.png" width="32" height="32" alt=""></span>' +
        '<div class="tool-name">' + escapeHtml(book.ru) + '</div>' +
        '<div class="tool-desc">' + escapeHtml(book.en) + '</div>' +
        badge +
        '</a>';
    }).join('');
  }

  function showBookGrid() {
    var grid = get('scripture-book-grid');
    var article = get('scripture-verse-article');
    var nav = get('scripture-navigation');
    var analysis = get('scripture-analysis');
    if (grid) grid.style.display = 'grid';
    if (article) article.style.display = 'none';
    if (nav) nav.style.display = 'none';
    if (analysis) analysis.style.display = 'none';
    state.currentBook = null;
  }

  function showVerseView() {
    var grid = get('scripture-book-grid');
    var article = get('scripture-verse-article');
    var nav = get('scripture-navigation');
    var analysis = get('scripture-analysis');
    if (grid) grid.style.display = 'none';
    if (article) article.style.display = '';
    if (nav) nav.style.display = '';
    if (analysis) analysis.style.display = '';
  }

  function openBook(bookId) {
    var book = state.books.filter(function(b) { return b.id === bookId; })[0];
    if (!book) return;

    if (!book.dataFile) {
      if (typeof LabToast !== 'undefined') {
        LabToast.show('Текст «' + book.ru + '» пока не оцифрован. Скоро добавим.');
      }
      return;
    }

    state.currentBook = book;
    showVerseView();
    loadVerses(book);
  }
  function loadVerses(book) {
    setLoading('Загрузка ' + book.ru + '…');
    return fetch('data/scripture/' + book.dataFile + '.json')
      .then(function(response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      })
      .then(function(data) {
        if (!Array.isArray(data) || !data.length) throw new Error('Пустой набор стихов');
        state.verses = data;
        state.currentVerse = 0;
        renderVerse();
      })
      .catch(function(error) {
        var article = get('scripture-verse-article');
        if (article) {
          article.innerHTML = '<div class="lab-alert lab-alert-error scripture-reader-error">Ошибка загрузки текста: ' +
            escapeHtml(error.message) + '</div>';
        }
      });
  }

  function renderVerse() {
    var verse = state.verses[state.currentVerse];
    if (!verse || !state.currentBook) return;

    var title = get('scripture-verse-title');
    var paleo = get('scripture-paleo');
    var hebrew = get('scripture-hebrew');
    var translit = get('scripture-translit');
    var literal = get('scripture-literal');
    var previous = get('scripture-prev');
    var next = get('scripture-next');
    var analysis = get('scripture-analysis');

    state.selectedIndexes = [];

    if (title) title.textContent = state.currentBook.ru + ' 1:' + verse.verse;
    if (paleo) paleo.innerHTML = renderPaleo(verse.paleo, verse.hebrew);
    if (hebrew) hebrew.innerHTML = renderWordLayer(verse.hebrew, 'scripture-word', 'scripture-hebrew-word');
    if (translit) translit.innerHTML = renderWordLayer(verse.translit, 'scripture-word', 'scripture-translit-word');
    if (literal) literal.innerHTML = renderWordLayer(verse.literal, 'scripture-word', 'scripture-literal-word');
    if (previous) previous.disabled = state.currentVerse === 0;
    if (next) next.disabled = state.currentVerse === state.verses.length - 1;
    if (analysis) {
      analysis.innerHTML = '<h2>Панель анализа</h2>' +
        '<p class="text-muted">Выберите буквы палео-текста для анализа.</p>' +
        copyButtonMarkup(true);
    }
  }

  function selectedLetters() {
    var paleo = get('scripture-paleo');
    if (!paleo) return [];
    return state.selectedIndexes.slice().sort(function(a, b) { return a - b; }).map(function(index) {
      var letter = paleo.querySelector('[data-index="' + index + '"]');
      if (!letter) return null;
      var hebrew = letter.getAttribute('data-hebrew') || PALEO.paleoToHebrew[letter.getAttribute('data-paleo')] || '';
      return {
        index: index,
        paleo: letter.getAttribute('data-paleo') || '',
        hebrew: hebrew,
        data: PALEO.byHebrew[hebrew] || { name: 'Неизвестная буква', image: 'образ не найден', meaning: '' }
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
        '<p class="text-muted">Выберите ещё одну последовательную букву.</p>' +
        copyButtonMarkup(true);
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
    var canSearchRoot = PALEO.canSearchRoot(selectedHebrew);
    var root = canSearchRoot ? state.roots.filter(function(item) {
      return PALEO.normalizeHebrew(item.root) === PALEO.normalizeHebrew(selectedHebrew);
    })[0] : null;
    var image = root && root.image
      ? root.image
      : letters.map(function(letter) { return letter.data.image; }).join(' + ');
    var rootHTML = letters.length > 4
      ? '<div class="scripture-hypothesis"><strong>Корень не ищется</strong><div>Выбрано ' + letters.length + ' букв. Для поиска корня выберите от 2 до 4 букв.</div></div>'
      : root
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
      copyButtonMarkup(false) +
      rootHTML;
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

  function setHoveredWord(wordIndex) {
    var reader = get('scripture-reader');
    if (!reader) return;
    reader.querySelectorAll('.scripture-word').forEach(function(word) {
      word.classList.toggle('is-word-hovered', word.getAttribute('data-word-index') === String(wordIndex));
    });
  }

  function clearHoveredWord() {
    var reader = get('scripture-reader');
    if (!reader) return;
    reader.querySelectorAll('.scripture-word.is-word-hovered').forEach(function(word) {
      word.classList.remove('is-word-hovered');
    });
  }

  function handleWordHover(event) {
    var word = event.target.closest('.scripture-word');
    if (!word) return;
    setHoveredWord(word.getAttribute('data-word-index'));
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
    var paleo = get('scripture-paleo');
    var reader = get('scripture-reader');
    var grid = get('scripture-book-grid');
    var back = get('scripture-back-btn');

    if (previous) previous.addEventListener('click', function() { moveVerse(-1); });
    if (next) next.addEventListener('click', function() { moveVerse(1); });
    if (paleo) paleo.addEventListener('click', handleLetterClick);
    var copyVerse = get('scripture-copy-verse');
    if (copyVerse) copyVerse.addEventListener('click', copyCurrentVerse);
    var analysis = get('scripture-analysis');
    if (analysis) analysis.addEventListener('click', function(event) {
      if (event.target.closest('.scripture-copy-selection')) copySelection();
    });
    if (reader) {
      reader.addEventListener('mouseover', handleWordHover);
      reader.addEventListener('mouseout', function(event) {
        if (!event.relatedTarget || !event.relatedTarget.closest || !event.relatedTarget.closest('.scripture-word')) {
          clearHoveredWord();
        }
      });
      reader.addEventListener('focusin', handleWordHover);
      reader.addEventListener('focusout', clearHoveredWord);
    }
    if (grid) grid.addEventListener('click', function(event) {
      var card = event.target.closest('.scripture-book-card');
      if (!card) return;
      event.preventDefault();
      openBook(card.getAttribute('data-book-id'));
    });
    if (back) back.addEventListener('click', function() {
      showBookGrid();
    });
  }

  function load() {
    return Promise.all([
      fetch('data/qumran-books.json').then(function(response) {
        if (!response.ok) throw new Error('qumran-books.json HTTP ' + response.status);
        return response.json();
      }),
      fetch('data/roots.json').then(function(response) {
        if (!response.ok) throw new Error('roots.json HTTP ' + response.status);
        return response.json();
      })
    ]).then(function(results) {
        state.books = Array.isArray(results[0].books) ? results[0].books : [];
        state.roots = Array.isArray(results[1]) ? results[1] : [];
        renderBookGrid();
        showBookGrid();
      })
      .catch(function(error) {
        var module = get('scripture-reader');
        if (module) {
          module.innerHTML = '<div class="lab-alert lab-alert-error scripture-reader-error">Ошибка загрузки списка книг: ' +
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

  window.ScriptureReader = { init: init, renderVerse: renderVerse };
  return window.ScriptureReader;
})();
