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
    roots: [],
    states: [],
    selectedWordIndex: null,
    loaded: false,
    loading: null,
    pendingBookId: null,
    pendingVerse: null,
    boundRoot: null
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
          '" data-paleo="' + escapeHtml(symbol) + '" data-hebrew="' + escapeHtml(hebrewLetter) +
          '" role="button" tabindex="0" aria-pressed="false" aria-label="Разобрать букву ' + escapeHtml(hebrewLetter) + '">' +
          escapeHtml(symbol) + '</span>';
        index++;
        return html;
      }).join('');
      return '<span class="scripture-word scripture-paleo-word" data-word-index="' + wordIndex + '" role="button" tabindex="0" aria-label="Разобрать слово ' + escapeHtml(hebrewWord) + '">' + letters + '</span>';
    }).join(' ');
  }

  function renderBookGrid() {
    var grid = get('scripture-book-grid');
    if (!grid) return;
    grid.innerHTML = state.books.map(function(book) {
      var statusClass = book.dataFile ? 'book-status-ready' : 'book-status-pending';
      var statusLabel = book.dataFile ? 'Есть данные' : 'В работе';
      var badge = '<div class="book-status ' + statusClass + '">' + statusLabel + '</div>';
      return '<a href="#" class="tool-card scripture-book-card" data-book-id="' + escapeHtml(book.id) + '">' +
'<span class="tool-icon"><img src="../../assets/icons/32/ui/book.png" width="32" height="32" alt=""></span>' +
        '<div class="tool-name">' + escapeHtml(book.ru) + '</div>' +
        '<div class="tool-desc">' + escapeHtml(book.paleo || '') + '</div>' +
        badge +
        '</a>';
    }).join('');
  }

  function showBookGrid() {
    var grid = get('scripture-book-grid');
    var article = get('scripture-verse-article');
    var nav = get('scripture-navigation');
    var topNav = get('scripture-navigation-top');
    var analysis = get('scripture-analysis');
    var tools = get('scripture-tools');
    if (grid) grid.style.display = 'grid';
    if (article) article.style.display = 'none';
    if (nav) nav.style.display = 'none';
    if (topNav) topNav.style.display = 'none';
    if (analysis) analysis.style.display = 'none';
    if (tools) tools.style.display = 'none';
    state.currentBook = null;
  }

  function showVerseView() {
    var grid = get('scripture-book-grid');
    var article = get('scripture-verse-article');
    var nav = get('scripture-navigation');
    var topNav = get('scripture-navigation-top');
    var analysis = get('scripture-analysis');
    var tools = get('scripture-tools');
    if (grid) grid.style.display = 'none';
    if (article) article.style.display = '';
    if (nav) nav.style.display = '';
    if (topNav) topNav.style.display = '';
    if (analysis) analysis.style.display = '';
    if (tools) tools.style.display = '';
  }

  function openBook(bookId, verseNumber) {
    if (!state.books.length) {
      state.pendingBookId = bookId;
      state.pendingVerse = verseNumber || null;
      return;
    }
    var book = state.books.filter(function(b) { return b.id === bookId; })[0];
    if (!book) return;

    state.currentBook = book;
    showVerseView();
    loadVerses(book, verseNumber);
  }
  function loadVerses(book, verseNumber) {
    setLoading('Загрузка ' + book.ru + '…');
    // Не запрашиваем несуществующий файл: в каталоге пока есть только Берешит.
    if (!book.dataFile) {
      var pendingArticle = get('scripture-verse-article');
      if (pendingArticle) {
        pendingArticle.innerHTML = '<div class="lab-alert lab-alert-info scripture-reader-error">Текст книги «' + escapeHtml(book.ru) + '» пока не загружен в библиотеку.</div>';
      }
      state.verses = [];
      return Promise.resolve([]);
    }
    var dataFile = book.dataFile;
    return fetch('data/scripture/' + dataFile.replace(/\.json$/, '') + '.json')
      .then(function(response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      })
      .then(function(data) {
        if (!Array.isArray(data) || !data.length) throw new Error('Пустой набор стихов');
        state.verses = data;
        var requestedIndex = verseNumber == null ? -1 : data.findIndex(function(item) {
          return String(item && item.verse) === String(verseNumber);
        });
        state.currentVerse = requestedIndex >= 0 ? requestedIndex : 0;
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
    var physicsTrigger = get('scripture-physics-trigger');
    var physicsPanel = get('scripture-physics-panel');

    state.selectedIndexes = [];
    state.selectedWordIndex = null;

    if (title) title.textContent = state.currentBook.ru + ' 1:' + verse.verse;
    if (paleo) paleo.innerHTML = renderPaleo(verse.paleo, verse.hebrew);
    if (hebrew) hebrew.innerHTML = renderWordLayer(verse.hebrew, 'scripture-word', 'scripture-hebrew-word');
    if (translit) translit.innerHTML = renderWordLayer(verse.translit, 'scripture-word', 'scripture-translit-word');
    if (literal) literal.innerHTML = renderWordLayer(verse.literal, 'scripture-word', 'scripture-literal-word');
    if (previous) previous.disabled = state.currentVerse === 0;
    if (next) next.disabled = state.currentVerse === state.verses.length - 1;
    renderVerseNavigation();
    if (analysis) {
      var content = get('scripture-physics-content');
      if (content) content.innerHTML = '<p class="text-muted">Нажми на слово для разбора.</p>';
      if (physicsTrigger) physicsTrigger.setAttribute('aria-expanded', 'false');
      if (physicsPanel) { physicsPanel.hidden = true; physicsPanel.classList.remove('is-open'); }
    }
  }

  function renderVerseNavigation() {
    var navigation = get('scripture-verse-nav');
    if (!navigation) return;
    navigation.innerHTML = state.verses.map(function(item, index) {
      var number = item && item.verse != null ? item.verse : index + 1;
      var active = index === state.currentVerse;
      return '<button type="button" class="verse-num' + (active ? ' active' : '') + '" data-verse-index="' + index + '"' +
        (active ? ' aria-current="true"' : '') + ' aria-label="Открыть стих ' + escapeHtml(number) + '">' +
        escapeHtml(number) + '</button>';
    }).join('');
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

  function selectedState() {
    if (!state.states.length) return null;
    return state.states.filter(function(item) { return item.id === 'tohu'; })[0] || state.states[0];
  }

  function lossLayersMarkup(compact) {
    var layers = [
      { label: 'Палео', value: 100 },
      { label: 'Слитный поток', value: 90 },
      { label: 'Масорет', value: 70 },
      { label: 'Греческий слой', value: 40 },
      { label: 'Латинский слой', value: 25 },
      { label: 'Синодальный слой', value: 15 }
    ];
    return '<div class="scripture-loss-scale' + (compact ? ' scripture-loss-scale-compact' : '') + '" aria-label="Шкала сохранности физики образа">' +
      layers.map(function(layer) {
        return '<div class="scripture-loss-scale-row"><span>' + escapeHtml(layer.label) + '</span>' +
          '<span class="scripture-loss-track"><span style="width:' + layer.value + '%"></span></span>' +
          '<strong>' + layer.value + '%</strong></div>';
      }).join('') + '</div>';
  }

  function stateMarkup() {
    var item = selectedState();
    if (!item) {
      return '<div class="scripture-state-card"><strong>Карта пространств</strong><p class="text-muted">Состояния не загружены.</p></div>';
    }
    return '<section class="scripture-state-card" aria-labelledby="scripture-state-title">' +
      '<div class="scripture-state-kicker">Состояние пространства</div>' +
      '<h3 id="scripture-state-title">' + escapeHtml(item.name || item.id) + '</h3>' +
      '<p>' + escapeHtml(item.physics || item.meaning || '') + '</p>' +
      '<small>Диагностическая гипотеза для выбранной цепи, не окончательный вывод.</small>' +
      '</section>';
  }

  function renderAnalysis() {
    var content = get('scripture-physics-content');
    var letters = selectedLetters();
    if (!content) return;

    if (letters.length < 2) {
      content.innerHTML = '<p class="text-muted">Выберите слово или последовательность букв палео-потока.</p>' +
        copyButtonMarkup(true);
      return;
    }

    var letterCards = letters.map(function(letter) {
      return '<article class="scripture-analysis-letter">' +
        '<div class="scripture-analysis-paleo">' + escapeHtml(letter.paleo) + '</div>' +
        '<div class="scripture-analysis-name">' + escapeHtml(letter.data.name) + '</div>' +
        '<div class="scripture-analysis-image">' + escapeHtml(letter.data.image || '') + '</div>' +
        (letter.data.meaning ? '<p>' + escapeHtml(letter.data.meaning) + '</p>' : '') +
        '</article>';
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

    var assembly = letters.map(function(letter) {
      return letter.data.meaning || letter.data.image || letter.data.name;
    }).join(' → ');

    content.innerHTML = '<div class="scripture-physics-summary">' +
      '<div class="scripture-analysis-letters">' + letterCards + '</div>' +
      '<section class="scripture-assembly"><div class="scripture-section-label">Сборка-действие</div><p>' + escapeHtml(assembly) + '</p></section>' +
      '<p class="scripture-composite"><strong>Цепь образов:</strong> ' + escapeHtml(image) + '</p>' +
      '<p class="scripture-selection"><span class="scripture-selection-paleo">' + escapeHtml(selectedPaleo) + '</span> → <span class="hebrew">' + escapeHtml(selectedHebrew) + '</span></p>' +
      copyButtonMarkup(false) +
      rootHTML + stateMarkup() + lossLayersMarkup(true) + '</div>';
  }

  function openPhysics() {
    var trigger = get('scripture-physics-trigger');
    var panel = get('scripture-physics-panel');
    if (!trigger || !panel) return;
    panel.hidden = false;
    panel.classList.add('is-open');
    trigger.setAttribute('aria-expanded', 'true');
    panel.style.maxHeight = panel.scrollHeight + 'px';
  }

  function closePhysics() {
    var trigger = get('scripture-physics-trigger');
    var panel = get('scripture-physics-panel');
    if (!trigger || !panel) return;
    trigger.setAttribute('aria-expanded', 'false');
    panel.classList.remove('is-open');
    panel.style.maxHeight = '0px';
    window.setTimeout(function() {
      if (trigger.getAttribute('aria-expanded') === 'false') panel.hidden = true;
    }, 280);
  }

  function currentEvidence() {
    var verse = state.verses[state.currentVerse];
    var letters = selectedLetters();
    if (!verse || !letters.length) return null;
    return {
      book: state.currentBook && state.currentBook.ru,
      verse: verse.verse,
      paleo: letters.map(function(letter) { return letter.paleo; }).join(''),
      hebrew: letters.map(function(letter) { return letter.hebrew; }).join(''),
      letters: letters.map(function(letter) {
        return { paleo: letter.paleo, hebrew: letter.hebrew, image: letter.data.image, meaning: letter.data.meaning };
      }),
      savedAt: new Date().toISOString()
    };
  }

  function saveEvidence() {
    var evidence = currentEvidence();
    if (!evidence) {
      if (typeof LabToast !== 'undefined') LabToast.show('Сначала выберите слово или буквы.');
      return;
    }
    try {
      var key = 'golem_scripture_evidence_v1';
      var saved = JSON.parse(localStorage.getItem(key) || '[]');
      if (!Array.isArray(saved)) saved = [];
      saved.unshift(evidence);
      localStorage.setItem(key, JSON.stringify(saved.slice(0, 50)));
      copyText(JSON.stringify(evidence, null, 2), 'Свидетельство сохранено и скопировано.');
    } catch (error) {
      if (typeof LabToast !== 'undefined') LabToast.show('Не удалось сохранить свидетельство.');
    }
  }

  function requestAIAnalysis() {
    var evidence = currentEvidence();
    if (!evidence) return Promise.resolve();
    return fetch('http://localhost:8000/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent: 'researcher',
        task: 'Разбери выбранный палео-фрагмент без замены локальной физики: ' + JSON.stringify(evidence)
      })
    }).then(function(response) {
      if (!response.ok) throw new Error('AI HTTP ' + response.status);
      return response.json();
    }).then(function(result) {
      var content = get('scripture-physics-content');
      var text = result && (result.result || result.output || result.text);
      if (content && text) {
        content.insertAdjacentHTML('beforeend', '<div class="scripture-ai-note"><strong>Заметка исследователя</strong><p>' + escapeHtml(text) + '</p></div>');
        openPhysics();
      }
    }).catch(function() {
      // Локальный разбор остаётся доступен без сервера.
    });
  }

  function selectWord(wordIndex) {
    var paleo = get('scripture-paleo');
    var word = paleo && paleo.querySelector('.scripture-paleo-word[data-word-index="' + wordIndex + '"]');
    if (!word) return;
    state.selectedWordIndex = Number(wordIndex);
    state.selectedIndexes = Array.prototype.map.call(word.querySelectorAll('.scripture-paleo-letter'), function(letter) {
      return Number(letter.getAttribute('data-index'));
    });
    updateLetterState();
    renderAnalysis();
    openPhysics();
  }

  function handleLetterClick(event) {
    var word = event.target.closest('.scripture-paleo-word');
    if (word && !event.target.closest('.scripture-paleo-letter')) {
      event.preventDefault();
      selectWord(word.getAttribute('data-word-index'));
      return;
    }
    var letter = event.target.closest('.scripture-paleo-letter');
    if (!letter) return;

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
    if (state.selectedIndexes.length) openPhysics();
  }

  function handlePaleoKeydown(event) {
    var target = event.target.closest('.scripture-paleo-word, .scripture-paleo-letter');
    if (!target || (event.key !== 'Enter' && event.key !== ' ')) return;
    event.preventDefault();
    if (target.classList.contains('scripture-paleo-word')) {
      selectWord(target.getAttribute('data-word-index'));
    } else {
      handleLetterClick({ target: target, preventDefault: function() {} });
    }
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
    if (paleo) paleo.addEventListener('keydown', handlePaleoKeydown);
    var copyVerse = get('scripture-copy-verse');
    if (copyVerse) copyVerse.addEventListener('click', copyCurrentVerse);
    var analysis = get('scripture-analysis');
    if (analysis) analysis.addEventListener('click', function(event) {
      if (event.target.closest('.scripture-copy-selection')) copySelection();
    });
    var physicsTrigger = get('scripture-physics-trigger');
    if (physicsTrigger) physicsTrigger.addEventListener('click', function() {
      if (physicsTrigger.getAttribute('aria-expanded') === 'true') closePhysics();
      else openPhysics();
    });
    var analysisTool = get('scripture-tool-analysis');
    var saveTool = get('scripture-tool-save');
    if (analysisTool) analysisTool.addEventListener('click', function() {
      if (state.selectedIndexes.length) { renderAnalysis(); openPhysics(); }
      else if (typeof LabToast !== 'undefined') LabToast.show('Сначала выберите слово палео-текста.');
      requestAIAnalysis();
    });
    if (saveTool) saveTool.addEventListener('click', saveEvidence);
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
    var verseNavigation = get('scripture-verse-nav');
    if (verseNavigation) verseNavigation.addEventListener('click', function(event) {
      var button = event.target.closest('.verse-num');
      if (!button) return;
      state.currentVerse = Number(button.getAttribute('data-verse-index'));
      renderVerse();
    });
  }

  function load() {
    if (state.loading) return state.loading;
    if (state.loaded) return Promise.resolve();
    state.loading = Promise.all([
      fetch('data/qumran-books.json').then(function(response) {
        if (!response.ok) throw new Error('qumran-books.json HTTP ' + response.status);
        return response.json();
      }),
    fetch('data/roots/roots.json').then(function(response) {
      if (!response.ok) throw new Error('roots/roots.json HTTP ' + response.status);
        return response.json();
      }),
      fetch('data/states.json').then(function(response) {
        if (!response.ok) throw new Error('states.json HTTP ' + response.status);
        return response.json();
      }).catch(function() { return { states: [] }; })
    ]).then(function(results) {
        state.books = Array.isArray(results[0].books) ? results[0].books : [];
        state.roots = Array.isArray(results[1]) ? results[1] : [];
        state.states = Array.isArray(results[2].states) ? results[2].states : [];
        renderBookGrid();
        showBookGrid();
        state.loaded = true;
        if (state.pendingBookId) {
          var requestedBookId = state.pendingBookId;
          var requestedVerse = state.pendingVerse;
          state.pendingBookId = null;
          state.pendingVerse = null;
          openBook(requestedBookId, requestedVerse);
        }
      })
      .catch(function(error) {
        var module = get('scripture-reader');
        if (module) {
          module.innerHTML = '<div class="lab-alert lab-alert-error scripture-reader-error">Ошибка загрузки списка книг: ' +
            escapeHtml(error.message) + '</div>';
        }
        throw error;
      });
    return state.loading;
  }

  function init(parsed) {
    var reader = get('scripture-reader');
    if (!reader) return;
    var requestedBookId = parsed && parsed.params && parsed.params.book;
    var requestedVerse = parsed && parsed.params && parsed.params.verse;
    if (requestedBookId) {
      if (state.loaded) openBook(requestedBookId, requestedVerse);
      else {
        state.pendingBookId = requestedBookId;
        state.pendingVerse = requestedVerse || null;
      }
    }
    if (state.boundRoot !== reader) {
      bindEvents();
      state.boundRoot = reader;
      state.initialized = true;
      if (state.loaded) {
        renderBookGrid();
        showBookGrid();
        if (requestedBookId) openBook(requestedBookId, requestedVerse);
      }
    }
    if (!state.loaded) load().catch(function() {});
  }

  window.ScriptureReader = {
    init: init,
    openBook: openBook,
    renderVerse: renderVerse,
    getBooks: function() { return state.books; },
    getVerses: function() { return state.verses; },
    getCurrentBook: function() { return state.currentBook; }
  };
  return window.ScriptureReader;
})();
