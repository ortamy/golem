/**
 * page-controller.js — Единый контроллер страниц SPA-лаборатории
 *
 * Централизует рендеринг всех модулей. Роутер вызывает PageController.render(),
 * а не размазывает логику по router.js и index.html.
 *
 * Маршрут: подключён после router.js, перед инициализацией.
 */

const PageController = (function() {
  'use strict';

  // ===== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====

  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text == null ? '' : String(text);
    return d.innerHTML;
  }

  function fetchPage(path) {
    return fetch(path).then(function(r) {
      if (!r.ok) throw new Error('HTTP ' + r.status + ' for ' + path);
      return r.text();
    });
  }

  function fetchJson(path) {
    return fetch(path).then(function(r) {
      if (!r.ok) throw new Error('HTTP ' + r.status + ' for ' + path);
      return r.json();
    });
  }

  function showError(container, msg) {
    container.innerHTML = '<div class="lab-alert lab-alert-error">' + escapeHtml(msg) + '</div>';
  }

  function showSpinner(container, text) {
    container.innerHTML = '<div class="lab-spinner show"><div class="loader"></div><div class="spinner-text">' + escapeHtml(text || 'Загрузка…') + '</div></div>';
  }

  // ===== JSON-СТРАНИЦЫ (словари, разоблачения, палео-механика) =====

  var jsonCache = {};
  var pageState = {
    dictionaries: { key: '', query: '' },
    exposure: { key: '' },
    methodology: { key: '' },
    'paleo-mechanics': { key: '' }
  };

  function loadJsonPage(page, path, container) {
    showSpinner(container, 'Загрузка данных…');
    fetchJson(path).then(function(data) {
      jsonCache[page] = data;
      if (page === 'dictionaries') renderDictionaries(container, data);
      else renderDocumentPage(container, page, data);
    }).catch(function(error) {
      showError(container, 'Ошибка загрузки данных: ' + error.message);
    });
  }

  function renderDictionaries(container, data) {
    var state = pageState.dictionaries;
    var keys = Object.keys(data);
    if (!keys.length) {
      container.innerHTML = '<div class="lab-alert lab-alert-info">Словари пока не заполнены.</div>';
      return;
    }
    if (!state.key) {
      var dictCards = keys.map(function(key, index) {
        var dict = data[key];
        var count = (dict.terms || []).length;
        return '<a href="#" class="dict-card" data-key="' + escapeHtml(key) + '" style="animation-delay: ' + (index * 50) + 'ms">' +
          '<img src="../../assets/icons/32/ui/book.png" class="dict-icon" alt="">' +
          '<div class="dict-name">' + escapeHtml(dict.title || key) + '</div>' +
          '<div class="dict-count">' + count + ' терминов</div>' +
          '<div class="dict-desc">' + escapeHtml((dict.description || '').split('---')[0].trim().substring(0, 100) + (dict.description && dict.description.length > 100 ? '...' : '')) + '</div>' +
          '</a>';
      }).join('');
      container.innerHTML = '<div class="research-page-head">' +
        '<h1><img src="../../assets/icons/32/ui/book.png" class="lab-icon" alt="">Словари</h1>' +
        '<p class="subtitle">Словарные карты подмен с ивритским соответствием и палео-формой.</p>' +
        '</div>' +
        '<div class="dict-grid" id="dict-grid">' + dictCards + '</div>';
      var dictGrid = document.getElementById('dict-grid');
      if (dictGrid) {
        dictGrid.querySelectorAll('.dict-card').forEach(function(card) {
          card.addEventListener('click', function(e) {
            e.preventDefault();
            state.key = this.getAttribute('data-key');
            state.query = '';
            renderDictionaries(container, data);
          });
        });
      }
      return;
    }
    var dictionary = data[state.key];
    var query = state.query.trim().toLowerCase();
    var terms = (dictionary.terms || []).filter(function(term) {
      if (!query) return true;
      return [term.word, term.hebrew, term.restored].some(function(value) {
        return String(value || '').toLowerCase().indexOf(query) !== -1;
      });
    });
    var backBtn = '<button class="lab-btn lab-btn-secondary lab-btn-sm" onclick="PageController.pageState.dictionaries.key=\'\';PageController.renderDictionaries(document.getElementById(\'dictionaries\'), PageController.jsonCache.dictionaries)">← Назад к словарям</button>';
    var options = keys.map(function(key) {
      return '<option value="' + escapeHtml(key) + '"' + (key === state.key ? ' selected' : '') + '>' +
        escapeHtml(data[key].title || key) + '</option>';
    }).join('');
    var termCards = terms.map(function(term, index) {
      var paleo = (term.paleo || []).join(' ');
      return '<article class="term-card" style="animation-delay: ' + (index * 50) + 'ms">' +
        '<div class="term-paleo" lang="hbo" dir="rtl">' + escapeHtml(paleo) + '</div>' +
        '<div class="term-word">' + escapeHtml(term.word) + '</div>' +
        '<div class="term-hebrew" lang="he" dir="rtl">' + escapeHtml(term.hebrew) + '</div>' +
        '<div class="term-restored">' + escapeHtml(term.restored) + '</div>' +
        '</article>';
    }).join('');
    var dictionaryDescription = escapeHtml(dictionary.description || '')
      .replace(/---/g, '<hr class="dictionary-separator">');
    container.innerHTML = '<div class="research-page-head">' +
      '<h1><img src="../../assets/icons/32/ui/book.png" class="lab-icon" alt="">Словари</h1>' +
      '<p class="subtitle">Словарные карты подмен с ивритским соответствием и палео-формой.</p>' +
      '</div>' +
      '<div class="research-controls">' +
      '<label>Словарь<select id="research-dictionary-select" class="lab-input">' + options + '</select></label>' +
      '<label class="research-search-label">Поиск<input id="research-dictionary-search" class="lab-input" type="search" value="' + escapeHtml(state.query) + '" placeholder="Слово, иврит или восстановленный смысл"></label>' +
      '</div>' +
      '<div class="research-meta">' + backBtn + '<span>' + terms.length + ' из ' + (dictionary.terms || []).length + ' терминов</span></div>' +
      '<div class="research-description">' + dictionaryDescription + '</div>' +
      '<div class="term-grid" id="term-grid">' + (termCards || '<div class="lab-alert lab-alert-info">По запросу ничего не найдено.</div>') + '</div>';
    var termGrid = document.getElementById('term-grid');
    if (termGrid) termGrid.querySelectorAll('.term-card').forEach(function(c) { c.classList.add('fade-in-stagger'); });
    var select = document.getElementById('research-dictionary-select');
    var search = document.getElementById('research-dictionary-search');
    if (select) select.addEventListener('change', function() {
      state.key = this.value;
      state.query = '';
      renderDictionaries(container, data);
    });
    if (search) search.addEventListener('input', function() {
      state.query = this.value;
      renderDictionaries(container, data);
      var nextSearch = document.getElementById('research-dictionary-search');
      if (nextSearch) { nextSearch.focus(); nextSearch.setSelectionRange(state.query.length, state.query.length); }
    });
  }

  function renderDocumentPage(container, page, data) {
    var state = pageState[page];
    var keys = Object.keys(data);
    if (!keys.length) {
      container.innerHTML = '<div class="lab-alert lab-alert-info">Материалы пока не заполнены.</div>';
      return;
    }
    if (!state.key) {
      var iconPath = page === 'exposure' ? '../../assets/icons/32/archaeology/lamp.png' : (page === 'paleo-mechanics' ? '../../assets/icons/32/paleo/track.png' : '../../assets/icons/32/crafts/hammer-and-chisel.png');
      var docCards = keys.map(function(key, index) {
        var doc = data[key];
        return '<a href="#" class="doc-card" data-key="' + escapeHtml(key) + '" style="animation-delay: ' + (index * 50) + 'ms">' +
          '<img src="' + iconPath + '" class="doc-icon" alt="">' +
          '<div class="doc-name">' + escapeHtml(doc.title || key) + '</div>' +
          '<div class="doc-desc">' + escapeHtml((doc.description || '').split('---')[0].trim().substring(0, 120) + (doc.description && doc.description.length > 120 ? '...' : '')) + '</div>' +
          '</a>';
      }).join('');
      var heading = page === 'exposure' ? 'Архив' : (page === 'paleo-mechanics' ? 'Палео-механика' : 'Методички');
      container.innerHTML = '<div class="research-page-head">' +
        '<h1><img src="' + iconPath + '" class="lab-icon" alt="">' + heading + '</h1>' +
        '<p class="subtitle">Материалы ResearchLab, собранные из исходных Markdown-документов.</p>' +
        '</div>' +
        '<div class="doc-grid" id="doc-grid">' + docCards + '</div>';
      var docGrid = document.getElementById('doc-grid');
      if (docGrid) {
        docGrid.querySelectorAll('.doc-card').forEach(function(card) {
          card.addEventListener('click', function(e) {
            e.preventDefault();
            state.key = this.getAttribute('data-key');
            renderDocumentPage(container, page, data);
          });
        });
      }
      return;
    }
    var documentData = data[state.key];
    var options = keys.map(function(key) {
      return '<option value="' + escapeHtml(key) + '"' + (key === state.key ? ' selected' : '') + '>' +
        escapeHtml(data[key].title || key) + '</option>';
    }).join('');
    var sections = (documentData.sections || []).map(function(section) {
      var content = typeof marked !== 'undefined' && marked.parse ? marked.parse(section.content || '') : escapeHtml(section.content || '');
      return '<article class="research-section"><h2>' + escapeHtml(section.title || '') + '</h2><div class="research-section-content">' + content + '</div></article>';
    }).join('');
    var heading = page === 'exposure' ? 'Архив' : (page === 'paleo-mechanics' ? 'Палео-механика' : 'Методички');
    var backBtn = '<button class="lab-btn lab-btn-secondary lab-btn-sm" onclick="PageController.pageState[\'' + page + '\'].key=\'\';PageController.renderDocumentPage(document.getElementById(\'' + page + '\'), \'' + page + '\', PageController.jsonCache[\'' + page + '\'])">← Назад к списку</button>';
    container.innerHTML = '<div class="research-page-head"><h1>' + heading + '</h1>' +
      '<p class="subtitle">Материалы ResearchLab, собранные из исходных Markdown-документов.</p></div>' +
      '<div class="research-controls"><label>Документ<select id="research-' + page + '-select" class="lab-input">' + options + '</select></label></div>' +
      '<div class="research-meta">' + backBtn + '</div>' +
      '<div class="research-description">' + escapeHtml(documentData.description || '') + '</div>' +
      '<div class="research-sections">' + sections + '</div>';
    var select = document.getElementById('research-' + page + '-select');
    if (select) select.addEventListener('change', function() {
      state.key = this.value;
      renderDocumentPage(container, page, data);
    });
  }

  function renderManifestPage(container, data) {
    var cards = Array.isArray(data.cards) ? data.cards : [];
    var supportTitles = [
      'ЧТО ТАКОЕ ГОЛЕМ',
      'ПОЧЕМУ ЭТО ВАЖНО',
      'Палео-иврит — первичен',
      'Палео-механика как метод'
    ];
    var supportIcons = ['א', 'ע', 'מ', 'ד'];
    var lossLevels = [0, 2, 3, 4, 5];
    var lossPercentages = ['100%', '70%', '40%', '25%', '15%'];
    var lossCards = lossLevels.map(function(level) {
      return cards.filter(function(card) {
        return new RegExp('^Уровень\\s+' + level + ':', 'i').test(card.title || '');
      })[0];
    }).filter(Boolean);
    var supportCards = supportTitles.map(function(title, index) {
      var card = cards.filter(function(candidate) { return candidate.title === title; })[0];
      if (!card) return '';
      var summary = String(card.text || '').replace(/[*#>\n]/g, ' ').replace(/\s+/g, ' ').trim();
      if (summary.length > 240) summary = summary.substring(0, 237) + '…';
      return '<article class="lab-card manifest-support-card" style="animation-delay: ' + (index * 45) + 'ms">' +
        '<span class="manifest-support-icon paleo" lang="hbo" aria-hidden="true">' + supportIcons[index] + '</span>' +
        '<span class="manifest-support-index">Опора 0' + (index + 1) + '</span>' +
        '<h3>' + escapeHtml(card.title) + '</h3>' +
        '<p>' + escapeHtml(summary) + '</p>' +
        '</article>';
    }).join('');
    var lossHtml = lossCards.map(function(card, index) {
      var title = (card.title || '').replace(/^Уровень\s+[0-5]:\s*/i, '');
      return '<li class="manifest-loss-plate" style="--loss-fill: ' + lossPercentages[index] + '">' +
        '<span class="manifest-loss-number">0' + (index + 1) + '</span>' +
        '<span class="manifest-loss-copy"><strong>' + escapeHtml(title) + '</strong><span>' + escapeHtml(card.text || '') + '</span></span>' +
        '<span class="manifest-loss-percent">' + lossPercentages[index] + '</span>' +
        '</li>';
    }).join('');
    var usedTitles = supportTitles.concat(lossCards.map(function(card) { return card.title; }));
    var accordionCards = cards.filter(function(card) {
      return usedTitles.indexOf(card.title) === -1;
    });
    var accordionHtml = accordionCards.map(function(card, index) {
      var content = typeof marked !== 'undefined' && marked.parse
        ? marked.parse(card.text || '')
        : '<p>' + escapeHtml(card.text || '').replace(/\n/g, '<br>') + '</p>';
      return '<details class="manifest-accordion-item" style="animation-delay: ' + (index * 25) + 'ms">' +
        '<summary><span class="manifest-accordion-index">' + String(index + 1).padStart(2, '0') + '</span>' +
        '<span>' + escapeHtml(card.title || 'Раздел манифеста') + '</span><span class="manifest-accordion-mark" aria-hidden="true">+</span></summary>' +
        '<div class="manifest-accordion-panel"><div class="manifest-accordion-content">' + content + '</div></div>' +
        '</details>';
    }).join('');

    container.innerHTML = '<div class="manifest-page">' +
      '<header class="manifest-hero">' +
      '<div class="manifest-watermark" aria-hidden="true">𐤀 𐤁 𐤂 𐤃 𐤄 𐤅</div>' +
      '<div class="manifest-kicker">RESEARCHLAB · МЕТОДОЛОГИЧЕСКОЕ ЯДРО</div>' +
      '<h1>' + escapeHtml(data.title || 'Манифест проекта') + '</h1>' +
      '<p class="manifest-lead">' + escapeHtml(data.description || '') + '</p>' +
      '</header>' +
      '<section class="manifest-section manifest-loss-section" aria-labelledby="manifest-loss-title">' +
      '<div class="manifest-section-heading"><div><span class="manifest-section-label">01 · слои передачи</span><h2 id="manifest-loss-title">Карта утрат</h2>' +
      '<p>Как образ сжимается до понятия: процент сохранённой физики смысла на каждом слое.</p></div></div>' +
      '<ol class="manifest-loss-map" aria-label="Карта утрат от палео-образов к Синодальному слою">' + (lossHtml || '<li class="lab-alert lab-alert-info">Карта утрат пока не заполнена.</li>') + '</ol>' +
      '</section>' +
      '<section class="manifest-section manifest-support-section" aria-labelledby="manifest-supports-title">' +
      '<div class="manifest-section-heading"><div><span class="manifest-section-label">02 · ядро</span><h2 id="manifest-supports-title">Четыре опоры</h2>' +
      '<p>Минимальный каркас, через который Давар возвращает тексту образ, движение и переход.</p></div></div>' +
      '<div class="manifest-supports">' + (supportCards || '<div class="lab-alert lab-alert-info">Опоры манифеста пока не заполнены.</div>') + '</div>' +
      '</section>' +
      '<section class="manifest-section manifest-accordion-section" aria-labelledby="manifest-accordion-title">' +
      '<div class="manifest-section-heading"><div><span class="manifest-section-label">03 · глубина</span><h2 id="manifest-accordion-title">Глубокие принципы</h2>' +
      '<p>Раскрой блок, чтобы войти в конкретный слой методологии.</p></div></div>' +
      '<div class="manifest-accordion">' + (accordionHtml || '<div class="lab-alert lab-alert-info">Дополнительные разделы пока не заполнены.</div>') + '</div>' +
      '</section>' +
      '</div>';
  }

  // ===== ПРИМЕНЕНИЕ QUERY-ПАРАМЕТРА =====
  function applyQueryParam(parsed, inputId, isReady, run, attempt) {
    var query = parsed && parsed.params && parsed.params.q;
    if (!query) return;
    var input = document.getElementById(inputId);
    if (input) input.value = query;
    attempt = attempt || 0;
    if (!isReady() && attempt < 20) {
      setTimeout(function() { applyQueryParam(parsed, inputId, isReady, run, attempt + 1); }, 150);
      return;
    }
    run(query);
  }

  // ===== ОСНОВНОЙ МЕТОД РЕНДЕРИНГА =====
  function render(moduleId, container, parsed) {
    console.log('[PC] Рендерим модуль:', moduleId, container);
    if (!container) return;

    if (container.dataset.loaded && container.innerHTML.trim() !== '') {
      if (moduleId === 'scripture-reader' && window.ScriptureReader) {
        window.ScriptureReader.init(parsed);
      }
      return;
    }

    switch (moduleId) {

      // ===== СТАТИЧЕСКИЕ МОДУЛИ (HTML встроен) =====
      case 'dashboard':
        container.innerHTML = '<div id="dashboard-widgets" class="dashboard-widgets"><div class="lab-spinner show"><div class="loader"></div><div class="spinner-text">Загрузка статистики…</div></div></div>';
        container.dataset.loaded = '1';
        if (window.Dashboard) window.Dashboard.init();
        break;

      case 'root-dictionary':
        container.innerHTML = '<h1><img src="../../assets/icons/32/ui/book.png" class="lab-icon" alt="">Корневой словарь</h1>' +
          '<p class="subtitle">Поиск по корням иврита. Введите корень, слово или значение.</p>' +
          '<div class="search-wrap"><input type="text" id="rd-search" class="lab-input" placeholder="אמן, AMN, верить..." oninput="if(window.RootsSearch)RootsSearch.filter(this.value)" autofocus></div>' +
          '<div class="rd-stats"><div class="rd-stat"><div class="num" id="rd-total">150</div><div class="label">Корней</div></div><div class="rd-stat"><div class="num" id="rd-found">0</div><div class="label">Найдено</div></div></div>' +
          '<div id="rd-spinner" class="rd-spinner show"><div class="loader"></div><div class="spinner-text">Загрузка словаря…</div></div>' +
          '<div id="rd-list"></div><div id="rd-pagination" class="rd-pagination"></div>' +
          '<div id="rd-empty" class="lab-alert lab-alert-info" style="display:none">Ничего не найдено.</div>';
        container.dataset.loaded = '1';
        applyQueryParam(parsed, 'rd-search',
          function() { return !!window._roots; },
          function(query) { RootsSearch.filter(query); });
        break;

      case 'word-analyzer':
        container.innerHTML = '<h1><img src="../../assets/icons/32/archaeology/testtube.png" class="lab-icon" alt="">Разбор слов</h1>' +
          '<p class="subtitle">Вставьте слова через запятую или каждое с новой строки. Мы найдём корень, палео-образы, транслитерацию и цепочку подмен.</p>' +
          '<textarea id="wa-input" class="lab-textarea" rows="8" placeholder="אמת, תורה, שלום&#10;משיח&#10;צדק, חסד"></textarea>' +
          '<div class="flex gap-8 mb-16">' +
          '<button class="lab-btn lab-btn-primary" onclick="WordAnalyzer.analyze()"><img src="../../assets/icons/32/archaeology/testtube.png" width="32" height="32" alt="Разобрать" style="vertical-align: middle; margin-right: 6px;"> Разобрать</button>' +
          '<button class="lab-btn lab-btn-secondary" onclick="document.getElementById(\'wa-input\').value=\'\';document.getElementById(\'wa-grid\').innerHTML=\'\';document.getElementById(\'wa-export\').style.display=\'none\';document.getElementById(\'wa-status\').className=\'lab-alert lab-alert-info\';document.getElementById(\'wa-status\').textContent=\'Введите слова для разбора.\'"><img src="../../assets/icons/32/nav/alert.png" width="32" height="32" alt="Очистить" style="vertical-align: middle; margin-right: 6px;"> Очистить</button>' +
          '</div>' +
          '<div id="wa-status" class="lab-alert lab-alert-info">Введите слова для разбора.</div>' +
          '<div id="wa-export" class="export-bar" style="display:none">' +
          '<span class="export-title">Экспорт</span>' +
          '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" onclick="WordAnalyzer.copyMarkdown()">Копировать Markdown</button>' +
          '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" onclick="WordAnalyzer.downloadTxt()">Скачать TXT</button>' +
          '</div>' +
          '<div id="wa-grid" class="wa-grid"></div>';
        container.dataset.loaded = '1';
        applyQueryParam(parsed, 'wa-input',
          function() { return typeof WordAnalyzer !== 'undefined'; },
          function() { WordAnalyzer.analyze(); });
        break;

      case 'paleo-images':
        container.innerHTML = '<h1><img src="../../assets/icons/32/paleo/track.png" class="lab-icon" alt="">Палео-образы</h1>' +
          '<p class="subtitle">22 буквы палео-ивритского алфавита. Нажмите на букву, чтобы увидеть описание.</p>' +
          '<div class="pi-grid" id="pi-grid"></div>' +
          '<div class="pi-detail" id="pi-detail">' +
          '<div class="pi-detail-header"><div class="pi-dpaleo" id="pi-dpaleo"></div><div class="pi-dinfo"><div class="pi-dname" id="pi-dname"></div><div class="pi-dtranslit" id="pi-dtranslit"></div></div></div>' +
          '<div class="pi-dmeaning" id="pi-dmeaning"></div><div class="pi-ddesc" id="pi-ddesc"></div><div class="pi-dexample" id="pi-dexample"></div><div class="pi-droots" id="pi-droots"></div>' +
          '</div>';
        container.dataset.loaded = '1';
        break;

      case 'learn':
        container.innerHTML = '<div id="learn-app" aria-live="polite"></div>';
        container.dataset.loaded = '1';
        if (window.LearnLab) window.LearnLab.init();
        break;

      case 'etymology-checker':
        container.innerHTML = '<h1><img src="../../assets/icons/32/archaeology/testtube.png" class="lab-icon" alt="">Чекер этимологии</h1>' +
          '<p class="subtitle">Проверь слово на соответствие палео-корням, образам и карте утрат</p>' +
          '<div class="search-wrap"><input type="text" id="el-input" class="lab-input" placeholder="Введите слово на иврите..." onkeydown="if(event.key===\'Enter\')EtymologyLab.analyze()"><button class="lab-btn lab-btn-primary" onclick="EtymologyLab.analyze()">Разобрать</button></div>' +
          '<div id="el-results"></div>';
        container.dataset.loaded = '1';
        break;

      case 'scripture-reader':
        container.innerHTML = '<div class="research-page-head scripture-reader-head">' +
          '<h1><img src="../../assets/icons/32/ui/book.png" class="lab-icon" alt="">Книгочтение</h1>' +
          '<p class="subtitle">Книги Танаха, засвидетельствованные в кумранских свитках. Чтение на палео-иврите с последовательным просмотром стихов.</p>' +
          '</div>' +
          '<div class="scripture-reader-layout"><main class="scripture-main">' +
          '<div id="scripture-book-grid" class="scripture-book-grid"></div>' +
          '<article class="scripture-verse" id="scripture-verse-article" style="display:none;" aria-labelledby="scripture-verse-title">' +
          '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm scripture-back-btn" id="scripture-back-btn">← К списку книг</button>' +
          '<div class="scripture-verse-meta" id="scripture-verse-title">Берешит 1:1</div>' +
          '<div id="scripture-verse-nav" class="scripture-verse-nav" aria-label="Выбор стиха"></div>' +
          '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm scripture-copy-button scripture-copy-verse" id="scripture-copy-verse" aria-label="Копировать стих" title="Копировать стих">' +
          '<svg class="scripture-copy-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="8" y="8" width="11" height="11" rx="1.5"></rect><path d="M16 8V5.5A1.5 1.5 0 0 0 14.5 4h-9A1.5 1.5 0 0 0 4 5.5v9A1.5 1.5 0 0 0 5.5 16H8"></path></svg>' +
          '</button>' +
          '<div id="scripture-paleo" class="scripture-paleo" dir="rtl" lang="hbo" aria-label="Палео-иврит"></div>' +
          '<div id="scripture-hebrew" class="scripture-hebrew" dir="rtl" lang="he"></div>' +
          '<div id="scripture-translit" class="scripture-translit"></div>' +
          '<div id="scripture-literal" class="scripture-literal"></div>' +
          '</article>' +
          '<nav class="scripture-navigation" id="scripture-navigation" style="display:none;" aria-label="Навигация по стихам">' +
          '<button type="button" class="lab-btn lab-btn-secondary" id="scripture-prev">← Предыдущий стих</button>' +
          '<button type="button" class="lab-btn lab-btn-secondary" id="scripture-next">Следующий стих →</button>' +
          '</nav>' +
          '<section id="scripture-analysis" class="scripture-analysis scripture-physics" style="display:none;" aria-live="polite">' +
          '<button type="button" class="scripture-physics-trigger" id="scripture-physics-trigger" aria-expanded="false" aria-controls="scripture-physics-panel">' +
          '<span class="scripture-physics-trigger-title">Физика слова</span>' +
          '<span class="scripture-physics-trigger-hint">Нажми на слово для разбора</span>' +
          '<span class="scripture-physics-chevron" aria-hidden="true">⌄</span>' +
          '</button>' +
          '<div class="scripture-physics-panel" id="scripture-physics-panel" hidden>' +
          '<div id="scripture-physics-content" class="scripture-physics-content">Выберите слово палео-текста.</div>' +
          '</div>' +
          '</section>' +
          '<section id="scripture-tools" class="scripture-tools" style="display:none;" aria-label="Инструменты исследователя">' +
          '<button type="button" class="lab-btn lab-btn-secondary scripture-tool" id="scripture-tool-analysis" aria-label="Открыть анализ выбранного слова"><img src="../../assets/icons/32/ui/diff.png" alt="" aria-hidden="true"><span>Разобрать</span></button>' +
          '<button type="button" class="lab-btn lab-btn-secondary scripture-tool" id="scripture-tool-save" aria-label="Сохранить свидетельство выбранного слова"><img src="../../assets/icons/32/ui/download.png" alt="" aria-hidden="true"><span>Сохранить</span></button>' +
          '</section>' +
          '</main>' +
          '</div>';
        container.dataset.loaded = '1';
        if (window.ScriptureReader) window.ScriptureReader.init(parsed);
        break;

      case 'investigation':
        container.innerHTML = '<div class="investigation-heading">' +
          '<div><div class="investigation-kicker">AI / ДОСЬЕ</div>' +
          '<h1><img src="../../assets/icons/32/ui/question.png" class="lab-icon" alt="">Расследование</h1>' +
          '<p class="subtitle">Введите слово, корень или перевод. Сопоставьте происхождение, цепочку подмен и текстовые свидетельства.</p></div>' +
          '<div class="investigation-stamp" aria-hidden="true">CASE<br><strong>01</strong></div>' +
          '</div>' +
          '<form id="investigation-form" class="investigation-search" onsubmit="event.preventDefault(); Investigation.investigate();">' +
          '<label for="investigation-input">Объект расследования</label>' +
          '<div class="investigation-search-row"><input type="search" id="investigation-input" class="lab-input" placeholder="חסד, милость, HSD..." autocomplete="off" required>' +
          '<button type="submit" class="lab-btn lab-btn-primary" id="investigation-submit"><img src="../../assets/icons/32/ui/question.png" width="24" height="24" alt="">Расследовать</button></div>' +
          '<div id="investigation-status" class="investigation-status" role="status" aria-live="polite">Данные загружаются из словаря корней и словарей подмен.</div>' +
          '</form>' +
          '<div id="investigation-result" class="investigation-result" aria-live="polite"></div>';
        container.dataset.loaded = '1';
        break;

      case 'board':
        container.innerHTML = '<div class="board-shell" id="research-board-app">' +
          '<div class="board-toolbar" role="toolbar" aria-label="Инструменты исследовательской доски">' +
          '<div class="board-toolbar-heading"><span class="board-kicker">ХУК / СВИВА</span><h1>Исследовательская доска</h1></div>' +
          '<div class="board-actions">' +
          '<button type="button" class="lab-btn lab-btn-primary" data-board-action="add">+ Карточка</button>' +
          '<button type="button" class="lab-btn lab-btn-secondary" data-board-action="connect">Связать</button>' +
          '<button type="button" class="lab-btn lab-btn-secondary" data-board-action="group">Собрать группу</button>' +
          '<button type="button" class="lab-btn lab-btn-secondary" data-board-action="export">Экспорт</button>' +
          '<button type="button" class="lab-btn lab-btn-secondary" data-board-action="import">Импорт</button>' +
          '<button type="button" class="lab-btn lab-btn-danger" data-board-action="reset">Очистить</button>' +
          '<input type="file" accept="application/json" data-board-import-input hidden>' +
          '</div>' +
          '</div>' +
          '<div class="board-help" data-board-status>Карточки — факты и слои разбора. Перетаскивайте их; клик открывает полный Давар. Для группы отметьте карточки флажками.</div>' +
          '<div class="board-workspace" data-board-workspace tabindex="0" aria-label="Поле исследовательской доски">' +
          '<svg class="board-connections" data-board-svg aria-hidden="true"></svg>' +
          '<div class="board-groups" data-board-groups></div>' +
          '<div class="board-cards" data-board-cards></div>' +
          '<div class="board-empty" data-board-empty><strong>Доска пока пуста</strong><span>Добавьте первую карточку, чтобы собрать цепочку смысла.</span></div>' +
          '</div>' +
          '<aside class="board-inspector" data-board-inspector hidden></aside>' +
          '<div class="board-modal" data-board-modal hidden>' +
          '<div class="board-modal-backdrop" data-board-close-modal></div>' +
          '<form class="board-dialog" data-board-card-form>' +
          '<div class="board-dialog-header"><div><span class="board-kicker">КАРТОЧКА</span><h2 data-board-form-title>Новая карточка</h2></div><button type="button" class="board-dialog-close" data-board-close-modal aria-label="Закрыть">×</button></div>' +
          '<label>Заголовок<input name="title" required maxlength="120" placeholder="Например: Слой перевода"></label>' +
          '<label>Краткое описание<textarea name="summary" rows="2" maxlength="280" placeholder="Что фиксирует эта карточка?"></textarea></label>' +
          '<label>Полное содержимое<textarea name="content" rows="8" placeholder="Цитата, наблюдение, аргумент или последовательность действий"></textarea></label>' +
          '<div class="board-dialog-actions"><button type="button" class="lab-btn lab-btn-danger" data-board-delete-card>Удалить</button><span></span><button type="button" class="lab-btn lab-btn-secondary" data-board-close-modal>Отмена</button><button type="submit" class="lab-btn lab-btn-primary">Сохранить</button></div>' +
          '</form>' +
          '</div>' +
          '</div>';
        container.dataset.loaded = '1';
        if (window.ResearchBoard) window.ResearchBoard.init(container);
        break;

      case 'board-generator':
        container.innerHTML = '<h1><img src="../../assets/icons/32/scribe/scroll.png" class="lab-icon" alt="">Генератор исследовательских досок</h1>' +
          '<p class="subtitle">Создавайте визуальные доски для анализа улик, выводов и вложений. Экспортируйте в PNG, PDF или TXT.</p>' +
          '<form id="board-form">' +
          '<div style="margin-bottom:20px"><label style="display:block;font-weight:600;margin-bottom:6px">Заголовок доски <span style="color:var(--accent-red)">*</span></label>' +
          '<input type="text" id="board-title" required placeholder="Например: Анализ перевода Берешит 1:1" style="width:100%;padding:10px 12px;font-family:\'EB Garamond\',Georgia,serif;font-size:16px;border:1px solid var(--border-light);border-radius:4px;background:var(--bg-primary);color:var(--text-primary);outline:none"></div>' +
          '<div style="margin-bottom:20px"><label style="display:block;font-weight:600;margin-bottom:6px">Вывод / главная улика <span style="color:var(--accent-red)">*</span></label>' +
          '<textarea id="main-conclusion" required rows="3" placeholder="Краткий вывод или основная улика..." style="width:100%;padding:10px 12px;font-family:\'EB Garamond\',Georgia,serif;font-size:16px;border:1px solid var(--border-light);border-radius:4px;background:var(--bg-primary);color:var(--text-primary);outline:none;resize:vertical"></textarea></div>' +
          '<div style="margin-bottom:20px"><label style="display:block;font-weight:600;margin-bottom:8px">Улики</label><div id="evidence-list"></div>' +
          '<button type="button" onclick="addEvidence()" class="lab-btn lab-btn-secondary lab-btn-sm" style="margin-top:8px">+ Добавить улику</button></div>' +
          '<div style="margin-bottom:20px"><label style="display:block;font-weight:600;margin-bottom:8px">Вложения</label><div id="attachments-list"></div>' +
          '<button type="button" onclick="addAttachment()" class="lab-btn lab-btn-secondary lab-btn-sm" style="margin-top:8px">+ Добавить вложение</button></div>' +
          '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px">' +
          '<button type="button" onclick="generateBoard()" class="lab-btn lab-btn-primary lab-btn-compact" style="flex:1;min-width:200px">Сгенерировать доску</button></div>' +
          '<div id="export-section" style="display:none;padding:16px;background:var(--bg-primary);border:1px solid var(--border-light);border-radius:4px">' +
          '<h3 style="font-family:\'Cormorant Garamond\',Georgia,serif;font-size:20px;font-weight:600;margin-bottom:12px">Экспорт</h3>' +
          '<div style="display:flex;gap:10px;flex-wrap:wrap">' +
          '<button type="button" onclick="exportPNG()" class="lab-btn lab-btn-secondary lab-btn-sm">PNG</button>' +
          '<button type="button" onclick="exportPDF()" class="lab-btn lab-btn-secondary lab-btn-sm">PDF</button>' +
          '<button type="button" onclick="exportTXT()" class="lab-btn lab-btn-secondary lab-btn-sm">TXT</button>' +
          '<button type="button" onclick="copyPrompt()" class="lab-btn lab-btn-secondary lab-btn-sm">Копировать промпт</button></div></div>' +
          '</form>' +
          '<div style="margin-top:24px"><h2 style="font-family:\'Cormorant Garamond\',Georgia,serif;font-size:24px;font-weight:600;text-align:center;margin-bottom:16px">Предпросмотр доски</h2>' +
          '<div id="board-preview" style="display:none"></div>' +
          '<div id="board-placeholder" style="text-align:center;padding:60px 20px;color:var(--text-muted);font-style:italic;font-size:16px">Заполните форму и нажмите «Сгенерировать доску».</div></div>' +
          '<div id="copy-toast" style="position:fixed;top:24px;left:50%;transform:translateX(-50%);background:var(--bg-dark);color:var(--text-light);padding:10px 24px;font-size:14px;font-family:\'EB Garamond\',Georgia,serif;opacity:0;pointer-events:none;z-index:999;border-radius:4px;border:1px solid var(--accent-gold);transition:opacity 0.4s">Скопировано!</div>';
        container.dataset.loaded = '1';
        break;

      case 'research-generator':
        container.innerHTML = '<h1><img src="../../assets/icons/32/crafts/hammer-and-chisel.png" class="lab-icon" alt="">Генератор исследований</h1>' +
          '<p class="subtitle">Выберите тип исследования, укажите тему и получите основу в формате Markdown.</p>' +
          '<form id="research-generator-form" class="research-generator-form" onsubmit="event.preventDefault(); PageController.generateResearch();">' +
          '<div class="research-generator-fields">' +
          '<label for="rg-type">Тип исследования</label>' +
          '<select id="rg-type" class="lab-select">' +
          '<option value="root">Корень</option><option value="term">Термин</option><option value="verse">Стих</option><option value="substitution">Подмена</option><option value="free">Свободная тема</option>' +
          '</select>' +
          '<label for="rg-topic">Тема</label>' +
          '<input type="text" id="rg-topic" class="lab-input" placeholder="Например: חֶסֶד или подмена смысла слова «закон»" required>' +
          '<button type="submit" class="lab-btn lab-btn-primary" id="rg-generate">Сгенерировать</button>' +
          '</div>' +
          '</form>' +
          '<div id="rg-status" class="lab-alert lab-alert-info" role="status">Заполните тему и выберите тип исследования.</div>' +
          '<div id="rg-export" class="export-bar research-generator-export" style="display:none">' +
          '<span class="export-title">Экспорт</span>' +
          '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" onclick="PageController.downloadResearchTxt()">Скачать TXT</button>' +
          '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" onclick="PageController.copyResearchMarkdown()">Копировать Markdown</button>' +
          '</div>' +
          '<section class="research-preview-wrap" aria-labelledby="rg-preview-title">' +
          '<h2 id="rg-preview-title">Превью</h2>' +
          '<div id="rg-preview" class="research-preview" aria-live="polite">' +
          '<p class="research-preview-placeholder">Здесь появится оформленный шаблон исследования.</p>' +
          '</div>' +
          '</section>';
        container.dataset.loaded = '1';
        break;

      case 'religionism-checker':
        container.innerHTML = '<h1><img src="../../assets/icons/32/ui/question.png" width="32" height="32" alt="Чекер религионимов" style="vertical-align: middle; margin-right: 6px;"> Чекер религионимов</h1>' +
          '<p class="subtitle">Проверка текста на подмены. Вставьте текст на русском — мы подсветим религионизмы.</p>' +
          '<textarea id="rc-input" class="lab-textarea" rows="6" placeholder="Вставьте текст, например: Господь Бог сказал Моисею..."></textarea>' +
          '<div class="flex gap-8 items-center mb-16">' +
          '<button class="lab-btn lab-btn-primary" onclick="RelChecker.check()"><img src="../../assets/icons/32/ui/question.png" width="32" height="32" alt="Проверить" style="vertical-align: middle; margin-right: 6px;"> Проверить текст</button>' +
          '<button class="lab-btn lab-btn-secondary" onclick="RelChecker.clear()"><img src="../../assets/icons/32/nav/alert.png" width="32" height="32" alt="Очистить" style="vertical-align: middle; margin-right: 6px;"> Очистить</button></div>' +
          '<div id="rc-result" class="lab-card" style="display:none;"><div class="lab-card-header"><img src="../../assets/icons/32/scribe/scroll.png" width="32" height="32" alt="Результат" style="vertical-align: middle; margin-right: 6px;"> Результат проверки</div><div class="lab-card-body" id="rc-body"></div></div>' +
          '<div class="lab-card"><div class="lab-card-header"><img src="../../assets/icons/32/ui/book.png" width="32" height="32" alt="Словарь" style="vertical-align: middle; margin-right: 6px;"> Словарь подмен</div><div class="lab-card-body" id="rc-dict"></div></div>';
        container.dataset.loaded = '1';
        break;

      case 'religionisms':
        container.innerHTML = '<h1><img src="../../assets/icons/32/ui/question.png" width="32" height="32" alt="Религионизмы" style="vertical-align: middle; margin-right: 6px;"> Религионизмы</h1>' +
          '<p class="subtitle">Каждая сфера, учреждённая человеком вне откровения Яхве — структурированный шекер со своим алтарём, жрецами и жертвами. 9 компонентов на каждую сферу.</p>' +
          '<div class="search-wrap"><input type="text" id="rel-search" class="lab-input" placeholder="Медицина, алтарь, жрец..." oninput="if(window.Religionisms)Religionisms.filter(this.value)"></div>' +
          '<div class="rd-stats"><div class="rd-stat"><div class="num" id="rel-found">0</div><div class="label">Сфер найдено</div></div></div>' +
          '<div id="rel-grid" class="rel-grid"></div>' +
          '<div id="rel-detail" class="rel-detail" style="display:none;"></div>' +
          '<div id="rel-empty" class="lab-alert lab-alert-info" style="display:none">Ничего не найдено.</div>';
        container.dataset.loaded = '1';
        break;

      case 'translation-comparator':
        container.innerHTML = '<h1><img src="../../assets/icons/32/scribe/scroll.png" width="32" height="32" alt="Сравнение переводов" style="vertical-align: middle; margin-right: 6px;"> Сравнение переводов</h1>' +
          '<p class="subtitle">Параллельный просмотр текста ТаНаХа в разных переводах и текстуальные свидетели расхождений.</p>' +
          '<div class="lab-tabs">' +
          '<button type="button" class="lab-tab active" data-tab="tc-tab-compare">Сравнение</button>' +
          '<button type="button" class="lab-tab" data-tab="tc-tab-witnesses">Свидетели</button>' +
          '</div>' +
          '<div id="tc-tab-compare" class="tc-tab-panel">' +
          '<div class="search-wrap">' +
          '<input type="text" id="tc-search" class="lab-input" placeholder="Берешит 1:1, Исайя 53, Псалом 23" />' +
          '<button class="lab-btn lab-btn-primary" onclick="TransComp.search()"><img src="../../assets/icons/32/ui/book.png" width="32" height="32" alt="Показать" style="vertical-align: middle; margin-right: 6px;"> Показать</button></div>' +
          '<div id="tc-results" style="display:none;"><div class="flex gap-16" style="flex-wrap:wrap;">' +
          '<div class="lab-card flex-1" style="min-width:250px;"><div class="lab-card-header"><img src="../../assets/icons/32/scribe/scroll.png" width="32" height="32" alt="ТМ" style="vertical-align: middle; margin-right: 6px;"> ТМ (иврит)</div><div class="lab-card-body" id="tc-tm" style="font-size:20px;direction:rtl;"></div></div>' +
          '<div class="lab-card flex-1" style="min-width:250px;"><div class="lab-card-header"><img src="../../assets/icons/32/scribe/scroll.png" width="32" height="32" alt="LXX" style="vertical-align: middle; margin-right: 6px;"> LXX (греч.)</div><div class="lab-card-body" id="tc-lxx"></div></div>' +
          '<div class="lab-card flex-1" style="min-width:250px;"><div class="lab-card-header"><img src="../../assets/icons/32/scribe/scroll.png" width="32" height="32" alt="Синодальный" style="vertical-align: middle; margin-right: 6px;"> Синодальный</div><div class="lab-card-body" id="tc-synodal"></div></div>' +
          '</div></div>' +
          '<div id="tc-placeholder" class="lab-alert lab-alert-info">Введите ссылку на стих. Пример: <strong>Берешит 1:1</strong>.</div>' +
          '</div>' +
          '<div id="tc-tab-witnesses" class="tc-tab-panel" style="display:none;">' +
          '<p class="subtitle">Таблица текстуальных расхождений между ТМ, LXX, кумранскими свитками и Пешиттой. Нажмите на стих для подробного разбора.</p>' +
          '<div id="tc-divergence-map"></div>' +
          '<div id="tc-witnesses-table"><div class="lab-spinner show"><div class="loader"></div></div></div>' +
          '</div>';
        container.dataset.loaded = '1';
        break;

      case 'board-library':
        container.innerHTML = '<h1><img src="../../assets/icons/32/scribe/scrolls.png" width="32" height="32" alt="Архив досок" style="vertical-align: middle; margin-right: 6px;"> Архив досок</h1>' +
          '<p class="subtitle">Архив сохранённых исследовательских досок. Просмотр, экспорт и управление.</p>' +
          '<div class="flex gap-8 mb-16"><button class="lab-btn lab-btn-secondary" onclick="BoardLib.clearAll()"><img src="../../assets/icons/32/nav/alert.png" width="32" height="32" alt="Очистить" style="vertical-align: middle; margin-right: 6px;"> Очистить всё</button></div>' +
          '<div id="bl-list"></div>' +
          '<div id="bl-empty" class="lab-alert lab-alert-info">Пока нет сохранённых досок.</div>';
        container.dataset.loaded = '1';
        break;

      case 'vision':
        container.innerHTML = '<h1><img src="../../assets/icons/32/archaeology/lamp.png" width="32" height="32" alt="Визуальный анализатор" style="vertical-align: middle; margin-right: 6px;"> Визуальный анализатор</h1>' +
          '<p class="subtitle">Загрузите изображение для анализа. Модель опишет содержимое: текст, символы, объекты.</p>' +
          '<div class="flex gap-8 mb-16">' +
          '<button class="lab-btn lab-btn-primary" data-mode="huggingface" onclick="VisionUI.setMode(\'huggingface\')">🤗 Hugging Face API</button>' +
          '<button class="lab-btn lab-btn-secondary" data-mode="local" onclick="VisionUI.setMode(\'local\')">💻 Локальный сервер</button></div>' +
          '<div class="lab-card"><div class="lab-card-header"><img src="../../assets/icons/32/nav/door.png" width="32" height="32" alt="Настройки" style="vertical-align: middle; margin-right: 6px;"> Настройки</div><div class="lab-card-body">' +
          '<label class="mb-8" style="display:block;font-weight:600;">API ключ Hugging Face</label>' +
          '<div class="text-small text-muted mb-8"><a href="https://huggingface.co/settings/tokens" target="_blank" style="color:#b8860b;">Получить бесплатный ключ</a></div>' +
          '<div class="flex gap-8"><input type="password" id="vi-apikey" class="lab-input" placeholder="hf_xxxxxxxxxxxx" style="max-width:400px;" />' +
          '<button class="lab-btn lab-btn-secondary" onclick="VisionUI.saveKey()"><img src="../../assets/icons/32/ui/settings.png" width="32" height="32" alt="Сохранить" style="vertical-align: middle; margin-right: 6px;"> Сохранить</button></div></div></div>' +
          '<div class="lab-card" style="text-align:center;cursor:pointer;" onclick="document.getElementById(\'vi-file\').click()">' +
          '<div id="vi-preview" style="display:none;margin-bottom:12px;">' +
          '<img id="vi-img" src="" alt="preview" style="max-width:100%;max-height:300px;border-radius:4px;border:1px solid #d4c4a8;" />' +
          '<button class="lab-btn lab-btn-secondary mt-8" onclick="event.stopPropagation();VisionUI.remove()"><img src="../../assets/icons/32/nav/alert.png" width="32" height="32" alt="Удалить" style="vertical-align: middle; margin-right: 6px;"> Удалить</button></div>' +
          '<div id="vi-placeholder"><span><img src="../../assets/icons/32/ui/placeholder.svg" width="32" height="32" alt="Изображение" style="vertical-align: middle; margin-right: 6px;"></span><div style="font-size:18px;color:#2c1810;margin-top:8px;">Нажмите, чтобы загрузить</div>' +
          '<div class="text-muted text-small mt-8">PNG, JPG, WEBP — до 10 МБ</div></div>' +
          '<input type="file" id="vi-file" accept="image/png,image/jpeg,image/jpg,image/webp" style="display:none;" onchange="VisionUI.load(event)" /></div>' +
          '<button class="lab-btn lab-btn-primary" id="vi-analyze-btn" onclick="VisionUI.analyze()" disabled style="width:100%;justify-content:center;padding:14px;font-size:18px;margin-bottom:16px;"><img src="../../assets/icons/32/ui/question.png" width="32" height="32" alt="Анализировать" style="vertical-align: middle; margin-right: 6px;"> Анализировать</button>' +
          '<div id="vi-spinner" class="lab-spinner"><div class="loader"></div><div class="spinner-text">Анализ…</div></div>' +
          '<div id="vi-result" class="lab-card" style="display:none;"><div class="lab-card-header"><img src="../../assets/icons/32/scribe/scroll.png" width="32" height="32" alt="Результат" style="vertical-align: middle; margin-right: 6px;"> Результат</div><div class="lab-card-body" id="vi-result-body" style="white-space:pre-wrap;"></div>' +
          '<div class="text-muted text-small mt-8 flex justify-between"><span id="vi-model-badge">SmolVLM-256M</span><span id="vi-timestamp"></span></div></div>' +
          '<div id="vi-error" class="lab-alert lab-alert-error" style="display:none;"></div>';
        container.dataset.loaded = '1';
        break;

      case 'ai-agents':
        var agents = [
          { icon: 'ui/arrows', name: 'Оркестратор', desc: 'Оркестратор — получает запрос, разбивает его на подзадачи и распределяет их между агентами.', model: 'GOLEM', cat: 'Оркестрация', featured: true },
          { icon: 'archaeology/testtube', name: 'Исследователь', desc: 'Разбирает корни, стихи, термины.', model: 'Claude Sonnet 4', cat: 'Исследователь' },
          { icon: 'ui/question', name: 'Разоблачитель', desc: 'Ищет подмены в переводах, сравнивает LXX и Синодальный.', model: 'GPT-4o', cat: 'Исследователь' },
          { icon: 'scribe/scrolls', name: 'Сборщик', desc: 'Объединяет результаты в единый отчёт.', model: 'Claude Haiku 3.5', cat: 'Оркестрация' },
          { icon: 'ui/scales', name: 'Критик', desc: 'Проверяет разбор на соответствие методологии.', model: 'Claude Sonnet 4', cat: 'Контроль качества' },
          { icon: 'seals/ring', name: 'Семитолог', desc: 'Ищет параллели в аккадском, угаритском и арамейском.', model: 'GPT-4o', cat: 'Исследователь' },
          { icon: 'scribe/scroll', name: 'Компаратор', desc: 'Трёхстороннее сравнение масоретского текста, Септуагинты и кумранских свитков.', model: 'Claude Sonnet 4', cat: 'Исследователь' },
          { icon: 'ui/keyboard', name: 'Редактор', desc: 'Приводит черновик к стилю проекта.', model: 'Claude Haiku 3.5', cat: 'Документация' },
          { icon: 'scribe/scroll', name: 'Переводчик палео-иврита', desc: 'Переводит букву через палео-образ к физическому смыслу.', model: 'Claude Sonnet 4', cat: 'Исследователь' },
          { icon: 'crafts/hammer-and-chisel', name: 'Фронтенд-разработчик', desc: 'Создаёт интерфейсы Лаборатории на Vanilla JS, CSS и SVG.', model: 'Claude Sonnet 4', cat: 'Разработчик' },
          { icon: 'ui/settings', name: 'AI-инженер', desc: 'Разрабатывает нейросетевые модули на PyTorch и Flask API.', model: 'Claude Sonnet 4', cat: 'Разработчик' },
          { icon: 'ui/scales', name: 'Проверяющий', desc: 'Валидирует код, данные и исследовательские гипотезы.', model: 'Claude Sonnet 4', cat: 'Контроль качества' },
          { icon: 'scribe/scroll', name: 'Технический писатель', desc: 'Оформляет документацию в Markdown.', model: 'Claude Haiku 3.5', cat: 'Документация' },
          { icon: 'ui/scales', name: 'Ревьюер кода', desc: 'Проверяет код на соответствие MANIFEST.md.', model: 'Claude Sonnet 4', cat: 'Контроль качества' },
          { icon: 'paleo/track', name: 'Архитектор потока', desc: 'Проектирует порядок вызова агентов.', model: 'Claude Sonnet 4', cat: 'Оркестрация' },
          { icon: 'ui/link', name: 'Связной', desc: 'Связывает разрозненные исследования в единую сеть.', model: 'Claude Sonnet 4', cat: 'Оркестрация' }
        ];
        agents.forEach(function(a, i) { a.id = 'agent-' + i; });
        agentMapData = agents;
        var cards = agents.map(function(a) {
          return '<button type="button" class="tool-card agent-card agent-list-card' + (a.featured ? ' agent-card-orchestrator' : '') + '" data-agent-id="' + a.id + '" onclick="LabRouter.navigate(\'ai-agents\',[\'' + a.id + '\'])" aria-label="Открыть страницу агента: ' + a.name + '"><span class="tool-icon"><img src="../../assets/icons/32/' + a.icon + '.png" width="32" height="32" alt="' + a.name + '"></span>' +
            '<div class="tool-name">' + a.name + '</div>' +
            '<div class="tool-desc">' + a.desc + '</div>' +
            '<span class="tool-badge model agent-list-model">' + a.model + '</span>' +
            '<span class="agent-list-role" hidden>' + a.cat + '</span>' +
            '<span class="badge-category">' + a.cat + '</span>' +
            '<span class="badge-dev">' + (a.featured ? 'Активен' : 'В разработке') + '</span></button>';
        }).join('');
        container.innerHTML = '<div class="agent-list-view"><div class="agent-grid">' + cards + '</div></div>' +
          '<div id="agent-detail-view" class="agent-detail-view" hidden></div>' +
          '<div id="agent-map-view" class="agent-map-view" hidden></div>' +
          '<div id="agent-server-view" class="agent-server-view" hidden></div>';
        container.dataset.loaded = '1';
        break;

      case 'ed-chat':
        container.innerHTML = '<h1><img src="../../assets/icons/32/crafts/hammer-and-chisel.png" width="32" height="32" alt="Нейрочат" style="vertical-align: middle; margin-right: 6px;"> Нейрочат</h1>' +
          '<p class="subtitle">Чат с исследовательской нейросетью для анализа, разбора слов и поиска подмен.</p>' +
          '<div class="ec-layout"><main class="ec-main">' +
          '<div class="ec-toolbar"><label for="ec-model">Модель</label><select id="ec-model" class="lab-select"><option value="claude">Claude Sonnet 4</option><option value="gpt4o">GPT-4o</option><option value="deepseek">DeepSeek</option><option value="gemini">Gemini</option></select><span id="ec-model-label" class="ec-model-label"></span><span id="ec-tokens" class="ec-tokens" hidden></span></div>' +
          '<div class="lab-card ec-messages" id="ec-messages"><div class="text-muted ec-welcome" id="ec-welcome">Начните диалог.</div></div>' +
          '<div class="ec-composer"><textarea id="ec-input" class="lab-textarea" rows="3" placeholder="Введите запрос..." onkeydown="if(event.key===\'Enter\'&&!event.shiftKey){event.preventDefault();EdChat.send();}"></textarea><div class="ec-actions"><button class="lab-btn lab-btn-primary" onclick="EdChat.send()">Отправить</button><button class="lab-btn lab-btn-secondary" onclick="EdChat.clear()">Очистить</button><button class="lab-btn lab-btn-secondary" onclick="EdChat.save()">Сохранить диалог</button><button class="lab-btn lab-btn-secondary" onclick="EdChat.export()">Экспортировать Markdown</button><button class="lab-btn lab-btn-secondary" onclick="EdChat.useInPromptGenerator()">Использовать в генераторе промптов</button></div></div>' +
          '</main><aside id="ec-sidebar" class="ec-sidebar"><section class="ec-panel"><h2>Контекст</h2><h3>Документы</h3><ul id="ec-context-documents" class="ec-document-list"></ul><h3>Активный промпт</h3><textarea id="ec-prompt" class="lab-textarea ec-prompt" rows="5"></textarea></section><section class="ec-panel"><h2>История диалогов</h2><div id="ec-history" class="ec-history">Сохранённых диалогов пока нет.</div></section></aside></div>' +
          '<div class="text-small text-muted mt-8">Демо-режим: ответы формируются локально и учитывают выбранный стиль модели.</div>';
        container.dataset.loaded = '1';
        break;

      case 'paleo-keyboard':
        container.innerHTML = '<h1><img src="../../assets/icons/32/paleo/track.png" width="32" height="32" alt="Палео-клавиатура" style="vertical-align: middle; margin-right: 6px;"> Палео-ивритская клавиатура</h1>' +
          '<p class="subtitle">Нажимайте на буквы, чтобы вставить их. Каждая буква — с образом и значением.</p>' +
          '<textarea id="pk-output" class="lab-card pk-output" aria-label="Поле палео-текста" placeholder="Введите палео-символы…"></textarea>' +
          '<div class="flex gap-8 mb-16 pk-actions"><button type="button" class="lab-btn lab-btn-secondary" onclick="PaleoKey.copy()"><img src="../../assets/icons/32/scribe/scroll.png" width="32" height="32" alt="Копировать" style="vertical-align: middle; margin-right: 6px;"> Копировать</button><button type="button" class="lab-btn lab-btn-secondary" onclick="PaleoKey.clear()"><img src="../../assets/icons/32/nav/alert.png" width="32" height="32" alt="Очистить" style="vertical-align: middle; margin-right: 6px;"> Очистить</button></div>' +
          '<div id="pk-keys" class="pk-keyboard" aria-label="Палео-клавиатура"></div>' +
          '<div id="pk-info" class="lab-card mt-16" style="display:none;"><div class="lab-card-header" id="pk-info-title"></div><div class="lab-card-body" id="pk-info-body"></div></div>';
        container.dataset.loaded = '1';
        break;

      case 'admin-settings':
        container.innerHTML = '';
        container.dataset.loaded = '1';
        break;

      // ===== МОДУЛИ С FETCH HTML-СТРАНИЦЫ =====
      case 'paleo-builder':
      case 'video-lab':
      case 'generators':
      case 'checkers':
        showSpinner(container, 'Загрузка модуля…');
        fetchPage('pages/' + moduleId + '.html').then(function(html) {
          container.innerHTML = html;
          container.dataset.loaded = '1';
          if (moduleId === 'paleo-builder' && window.PaleoBuilder) {
            window.PaleoBuilder.init(container);
          }
          if (moduleId === 'video-lab' && window.VideoLab) {
            window.VideoLab.init(container);
          }
        }).catch(function(err) {
          showError(container, 'Ошибка загрузки модуля: ' + err.message);
        });
        break;

      case 'prompt-generator':
        showSpinner(container, 'Загрузка конструктора…');
        if (window.PromptGenerator) {
          window.PromptGenerator.init(container);
        } else {
          showError(container, 'Модуль «Генератор промптов» не загрузился.');
        }
        break;

      case 'davar-checker':
        showSpinner(container, 'Загрузка…');
        if (window.DavarChecker) {
          window.DavarChecker.init(container);
        } else {
          showError(container, 'Модуль «Давар-чекер» не загрузился.');
        }
        break;

      // ===== МОДУЛИ С JS-ИНИЦИАЛИЗАЦИЕЙ =====
      case 'cartography':
        showSpinner(container, 'Загрузка картографии…');
        if (window.Cartography) {
          container.dataset.loaded = '1';
          window.Cartography.init(container);
        } else {
          showError(container, 'Модуль «Картография» не загрузился.');
        }
        break;

      case 'heraldry':
        showSpinner(container, 'Загрузка гербовника…');
        if (window.Heraldry) {
          container.dataset.loaded = '1';
          window.Heraldry.init(container);
        } else {
          showError(container, 'Модуль «Гербовник» не загрузился.');
        }
        break;

      case 'states':
        showSpinner(container, 'Загрузка карты состояний…');
        if (window.GolemStates) {
          container.dataset.loaded = '1';
          window.GolemStates.init(parsed);
        } else {
          showError(container, 'Модуль «Карта состояний» не загрузился.');
        }
        break;

      case 'paleo-linguistics':
        showSpinner(container, 'Загрузка палео-лингвистики…');
        if (window.PaleoLinguistics) {
          window.PaleoLinguistics.init(parsed);
        } else {
          showError(container, 'Модуль «Палео-лингвистика» не загрузился.');
        }
        container.dataset.loaded = '1';
        break;

      case 'language-map':
        showSpinner(container, 'Загрузка карты языков…');
        if (window.LanguageMap) {
          window.LanguageMap.init(container, parsed);
        } else {
          showError(container, 'Модуль «Карта языков» не загрузился.');
        }
        container.dataset.loaded = '1';
        break;

      case 'linguistic-tensor':
        showSpinner(container, 'Загрузка лингвистического тензора…');
        if (window.LinguisticTensor) {
          window.LinguisticTensor.init(container, parsed);
        } else {
          showError(container, 'Модуль «Лингвистический тензор» не загрузился.');
        }
        container.dataset.loaded = '1';
        break;

      case 'methodology':
        showSpinner(container, 'Загрузка методологии…');
        if (window.MethodologyLab) {
          window.MethodologyLab.init(container);
        } else {
          showError(container, 'Модуль «Методология» не загрузился.');
        }
        container.dataset.loaded = '1';
        break;

      case 'name-decoder':
        showSpinner(container, 'Загрузка дешифратора имени…');
        if (window.NameDecoder) {
          window.NameDecoder.init(container);
        } else {
          showError(container, 'Модуль «Дешифратор Имени» не загрузился.');
        }
        container.dataset.loaded = '1';
        break;

      case 'researches':
        showSpinner(container, 'Загрузка исследований…');
        if (window.LoadResearches) {
          window.LoadResearches.render(container, parsed);
        } else {
          showError(container, 'Модуль «Исследования» не загрузился.');
        }
        container.dataset.loaded = '1';
        break;

      // ===== JSON-СТРАНИЦЫ =====
      case 'manifest':
        showSpinner(container, 'Загрузка манифеста…');
        fetchJson('data/methodology/manifest.json').then(function(data) {
          renderManifestPage(container, data);
          container.dataset.loaded = '1';
        }).catch(function(err) {
          showError(container, 'Ошибка загрузки манифеста: ' + err.message);
        });
        break;

      case 'dictionaries':
        loadJsonPage('dictionaries', 'data/dictionaries.json', container);
        break;

      case 'exposure':
        loadJsonPage('exposure', 'data/exposures/documents.json', container);
        break;

      case 'paleo-mechanics':
        loadJsonPage('paleo-mechanics', 'data/paleo-mechanics.json', container);
        break;

      // ===== ДИНАМИЧЕСКИЕ МОДУЛИ (создаются на лету) =====
      case 'exposure-editor':
        if (window.ExposureEditor) {
          window.ExposureEditor.init(container);
        } else {
          showError(container, 'Модуль редактора разоблачений не загрузился.');
        }
        break;

      case 'clue-generator':
        if (window.ClueGenerator) {
          window.ClueGenerator.init(container);
        } else {
          showError(container, 'Модуль генератора улик не загрузился.');
        }
        break;

      // ===== MARKDOWN-СТРАНИЦЫ =====
      default:
        // Пробуем загрузить как markdown-страницу
        var mdPaths = {
          'dict-religionims': '../../../analysis/dictionaries/dictionaries-religionims.md',
          'dict-grecisms': '../../../analysis/dictionaries/dictionaries-grecisms.md',
          'dict-latinisms': '../../../analysis/dictionaries/dictionaries-latinisms.md',
          'dict-slavicisms': '../../../analysis/dictionaries/dictionaries-slavicisms.md',
          'dict-names': '../../../analysis/dictionaries/dictionaries-names.md',
          'dict-phrases': '../../../analysis/dictionaries/dictionaries-phrases.md',
          'dict-economisms': '../../../analysis/dictionaries/dictionaries-economisms.md',
          'dict-estethisms': '../../../analysis/dictionaries/dictionaries-estethisms.md',
          'dict-gastronomisms': '../../../analysis/dictionaries/dictionaries-gastronomisms.md',
          'dict-juridisms': '../../../analysis/dictionaries/dictionaries-juridisms.md',
          'dict-marketisms': '../../../analysis/dictionaries/dictionaries-marketisms.md',
          'dict-mediasms': '../../../analysis/dictionaries/dictionaries-mediasms.md',
          'dict-medicinisms': '../../../analysis/dictionaries/dictionaries-medicinisms.md',
          'dict-militarisms': '../../../analysis/dictionaries/dictionaries-militarisms.md',
          'dict-modernisms': '../../../analysis/dictionaries/dictionaries-modernisms.md',
          'dict-newageisms': '../../../analysis/dictionaries/dictionaries-newageisms.md',
          'dict-politisms': '../../../analysis/dictionaries/dictionaries-politisms.md',
          'dict-psychologisms': '../../../analysis/dictionaries/dictionaries-psychologisms.md',
          'dict-scientisms': '../../../analysis/dictionaries/dictionaries-scientisms.md',
          'dict-sportisms': '../../../analysis/dictionaries/dictionaries-sportisms.md',
          'dict-technologisms': '../../../analysis/dictionaries/dictionaries-technologisms.md',
          'exposure-dictionary': '../../../analysis/exposure/exposure-dictionary.md',
          'exposure-principles': '../../../analysis/exposure/exposure-principles.md',
          'exposure-distortions': '../../../analysis/exposure/exposure-distortions.md',
          'exposure-mechanisms': '../../../analysis/exposure/exposure-mechanisms.md',
          'exposure-linguistic-methods': '../../../analysis/exposure/exposure-linguistic-methods.md',
          'exposure-methods': '../../../analysis/exposure/exposure-methods.md',
          'exposure-language': '../../../analysis/exposure/exposure-language.md',
          'exposure-language-shifts': '../../../analysis/exposure/exposure-language-shifts.md',
          'exposure-bavelisms': '../../../analysis/exposure/exposure-bavelisms.md',
          'exposure-masoretic': '../../../analysis/exposure/exposure-masoretic.md',
          'exposure-philosophemes': '../../../analysis/exposure/exposure-philosophemes.md',
          'exposure-system-architecture': '../../../analysis/exposure/exposure-system-architecture.md',
          'exposure-religionism-theory': '../../../analysis/exposure/exposure-religionism-theory.md',
          'exposure-techniques': '../../../analysis/exposure/exposure-techniques.md',
          'method-archeology': '../../../analysis/methodology/methodology-archeology.md',
          'method-hebrew-reconstruction': '../../../analysis/methodology/methodology-hebrew-reconstruction.md',
          'method-layers': '../../../analysis/methodology/methodology-layers.md',
          'method-translation': '../../../analysis/methodology/methodology-translation.md',
          'method-transliteration': '../../../analysis/methodology/methodology-transliteration.md',
          'method-tree': '../../../analysis/methodology/methodology-tree.md'
        };
        var mdPath = mdPaths[moduleId];
        if (mdPath) {
          showSpinner(container, 'Загрузка…');
          fetchPage(mdPath).then(function(md) {
            if (typeof marked !== 'undefined' && marked.parse) {
              container.innerHTML = marked.parse(md);
            } else {
              container.innerHTML = '<div class="lab-alert lab-alert-error">Ошибка: marked.js не загружен</div>';
            }
            container.dataset.loaded = '1';
          }).catch(function(err) {
            showError(container, 'Ошибка загрузки: ' + err.message);
          });
        } else {
          showError(container, 'Маршрут «' + moduleId + '» не зарегистрирован.');
        }
        break;
    }
  }

  // ===== ОЖИДАНИЕ КОНТЕЙНЕРА =====
  var pendingRenderObservers = {};

  function renderWhenReady(moduleId, parsed) {
    var container = document.getElementById(moduleId);
    if (container) {
      if (pendingRenderObservers[moduleId]) {
        pendingRenderObservers[moduleId].disconnect();
        delete pendingRenderObservers[moduleId];
      }
      render(moduleId, container, parsed);
      return;
    }

    var root = document.getElementById('labContent');
    if (!root) return;

    // Не создаём несколько наблюдателей для одного модуля.
    if (pendingRenderObservers[moduleId]) return;

    if (typeof MutationObserver === 'undefined') {
      setTimeout(function() {
        renderWhenReady(moduleId, parsed);
      }, 50);
      return;
    }

    var observer = new MutationObserver(function() {
      var ready = document.getElementById(moduleId);
      if (!ready) return;
      observer.disconnect();
      delete pendingRenderObservers[moduleId];
      render(moduleId, ready, parsed);
    });

    pendingRenderObservers[moduleId] = observer;
    observer.observe(root, { childList: true, subtree: true });
  }

  // ===== ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ =====
  function init() {
    // Инициализируем служебные модули
    if (window.LabTheme) LabTheme.init();
    if (window.LabHotkeys) LabHotkeys.init();

    // Роутер вызывает отложенный рендер при смене модуля.
    if (window.LabRouter) {
      LabRouter.onChange(function(moduleId, parsed) {
        renderWhenReady(moduleId, parsed);
      });
      LabRouter.init();
      if (window.LabHero) LabHero.observe();

    // Инициализируем модули, работающие с готовым DOM
    setTimeout(function() {
      if (window.RootDict) RootDict.init();
    }, 500);
    if (window.EtyLab) EtyLab.init();
    if (window.RelChecker) RelChecker.init();
    if (window.Religionisms) Religionisms.init();
    if (window.TransComp) TransComp.init();
    if (window.BoardLib) BoardLib.init();
    if (window.VisionUI) VisionUI.init();
    if (window.EdChat) EdChat.init();
    if (window.PaleoKey) PaleoKey.init();
    if (window.Investigation) Investigation.init();
    if (window.ScriptureReader) ScriptureReader.init();
    if (window.AdminSettings) AdminSettings.init();
    if (window.LearnLab) LearnLab.init();
    if (window.Dashboard) Dashboard.init();
    if (window.GolemStates) GolemStates.init();

    // Init board generator form
    var boardForm = document.getElementById('board-form');
    if (boardForm) {
      boardForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (typeof generateBoard === 'function') generateBoard();
      });
    }

    // Render paleo-images grid
    var piGrid = document.getElementById('pi-grid');
    if (piGrid && typeof LETTERS !== 'undefined') {
      var html = '';
      LETTERS.forEach(function(l, idx) {
        html += '<div class="pi-card" onclick="PaleoImages.show(' + idx + ')">';
        html += '<div class="pi-paleo">' + l.paleo + '</div>';
        html += '<div class="pi-name">' + l.name + '</div>';
        html += '<div class="pi-translit">' + l.translit + '</div>';
        html += '<div class="pi-meaning">' + l.meaning.split(',')[0] + '</div>';
        html += '</div>';
      });
      piGrid.innerHTML = html;
    }
  }
  }

  // ===== ДАННЫЕ ДЛЯ КАРТЫ АГЕНТОВ =====
  var agentMapData = null;

  // ===== ПУБЛИЧНЫЙ API =====
  return {
    init: init,
    render: render,
    renderWhenReady: renderWhenReady,
    jsonCache: jsonCache  ,
    pageState: pageState,
    agentMapData: agentMapData,
    renderDictionaries: renderDictionaries,
    renderDocumentPage: renderDocumentPage
  };
})();

window.PageController = PageController;