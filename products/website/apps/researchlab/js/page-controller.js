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

  var AGENT_API_URL = 'http://127.0.0.1:5000';

  function checkAgentServer() {
    return fetch(AGENT_API_URL + '/api/health', { cache: 'no-store' }).then(function(response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return response.json();
    });
  }

  function isAgentServerUnavailable(error) {
    return error && (error.name === 'TypeError' || error.name === 'NetworkError' || /Failed to fetch|NetworkError|ERR_CONNECTION_REFUSED/i.test(error.message || ''));
  }

  function agentServerMessage() {
    return '<div class="lab-alert lab-alert-error">Сервер AI-Агентов недоступен. Запустите из корня проекта: <code>python products/agents/server.py</code></div>';
  }

  // ===== JSON-СТРАНИЦЫ (словари, методология, палео-механика) =====

  var jsonCache = {};
  var pageState = {
    dictionaries: { key: '', query: '' },
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
      var specialCards = [
        '<a href="#" class="dict-card" data-key="__root_dictionary" style="animation-delay: 0ms">' +
          '<img src="../../assets/icons/32/ui/book.png" class="dict-icon" alt="">' +
          '<div class="dict-name">Корневой словарь</div>' +
          '<div class="dict-count">150 корней</div>' +
          '<div class="dict-desc">Поиск по корням иврита. Введите корень, слово или значение.</div>' +
          '</a>',
        '<a href="#" class="dict-card" data-key="__paleo_glossary" style="animation-delay: 50ms">' +
          '<img src="../../assets/icons/32/paleo/track.png" class="dict-icon" alt="">' +
          '<div class="dict-name">Палео-глоссарий</div>' +
          '<div class="dict-count">100 слов</div>' +
          '<div class="dict-desc">Первая партия: 100 слов как русла потока — палео-форма, квадратное письмо, функция и корень.</div>' +
          '</a>'
      ].join('');
      var dictCards = specialCards + keys.map(function(key, index) {
        var dict = data[key];
        var count = (dict.terms || []).length;
        return '<a href="#" class="dict-card" data-key="' + escapeHtml(key) + '" style="animation-delay: ' + ((index + 2) * 50) + 'ms">' +
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
    if (state.key === '__root_dictionary') {
      renderRootDictionaryModule(container, data);
      return;
    }
    if (state.key === '__paleo_glossary') {
      renderPaleoGlossaryModule(container, data);
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
    var dictionaryDescription = escapeHtml((dictionary.description || '').replace(/---/g, '').trim());
    var dictionaryHeading = escapeHtml(dictionary.title || 'Словари');
    container.innerHTML = '<div class="research-page-head">' +
      '<h1><img src="../../assets/icons/32/ui/book.png" class="lab-icon" alt="">' + dictionaryHeading + '</h1>' +
      '<p class="subtitle text-muted">' + dictionaryDescription + '</p>' + backBtn +
      '</div>' +
      '<div class="research-controls">' +
      '<label>Словарь<select id="research-dictionary-select" class="lab-input">' + options + '</select></label>' +
      '<label class="research-search-label">Поиск<input id="research-dictionary-search" class="lab-input" type="search" value="' + escapeHtml(state.query) + '" placeholder="Слово, иврит или восстановленный смысл"></label>' +
      '</div>' +
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

  function renderRootDictionaryModule(container, data) {
    var backBtn = '<button class="lab-btn lab-btn-secondary lab-btn-sm" onclick="PageController.pageState.dictionaries.key=\'\';PageController.renderDictionaries(document.getElementById(\'dictionaries\'), PageController.jsonCache.dictionaries)">← Назад к словарям</button>';
    container.innerHTML = '<div class="research-page-head">' +
      '<h1><img src="../../assets/icons/32/ui/book.png" class="lab-icon" alt="">Корневой словарь</h1>' +
      '<p class="subtitle">Поиск по корням иврита. Введите корень, слово или значение.</p>' + backBtn +
      '</div>' +
      '<div class="search-wrap"><input type="text" id="rd-search" class="lab-input" placeholder="אמן, AMN, верить..." oninput="if(window.RootsSearch)RootsSearch.filter(this.value)" autofocus></div>' +
      '<div class="rd-stats"><div class="rd-stat"><div class="num" id="rd-total">150</div><div class="label">Корней</div></div><div class="rd-stat"><div class="num" id="rd-found">0</div><div class="label">Найдено</div></div></div>' +
      '<div id="rd-spinner" class="rd-spinner show"><div class="loader"></div><div class="spinner-text">Загрузка словаря…</div></div>' +
      '<div id="rd-list"></div><div id="rd-pagination" class="rd-pagination"></div>' +
      '<div id="rd-empty" class="lab-alert lab-alert-info" style="display:none">Ничего не найдено.</div>';
    if (window.RootDict) RootDict.init();
  }

  function renderPaleoGlossaryModule(container, data) {
    var backBtn = '<button class="lab-btn lab-btn-secondary lab-btn-sm" onclick="PageController.pageState.dictionaries.key=\'\';PageController.renderDictionaries(document.getElementById(\'dictionaries\'), PageController.jsonCache.dictionaries)">← Назад к словарям</button>';
    container.innerHTML = '<div class="research-page-head">' +
      '<div class="paleo-glossary-head">' +
      '<div class="paleo-glossary-icon" aria-hidden="true">𐤌</div>' +
      '<div><p class="paleo-glossary-kicker">ГОЛЕМ · СЛОВАРИ</p><h1>Палео-глоссарий</h1>' +
      '<p class="subtitle">Первая партия: 100 слов как русла потока — палео-форма, квадратное письмо, функция и корень.</p></div>' +
      '</div>' + backBtn +
      '</div>' +
      '<div class="paleo-glossary-controls">' +
      '<label class="paleo-glossary-search">Поиск<input id="paleo-glossary-search" class="lab-input" type="search" placeholder="Палео-форма, слово или транслитерация" autocomplete="off"></label>' +
      '<label>Корень<select id="paleo-glossary-root" class="lab-input"><option value="all">Все корни</option></select></label>' +
      '</div>' +
      '<div id="paleo-glossary-meta" class="paleo-glossary-meta" aria-live="polite"></div>' +
      '<div id="paleo-glossary-grid" class="paleo-glossary-grid"></div>' +
      '<nav id="paleo-glossary-pagination" class="paleo-glossary-pagination" aria-label="Страницы глоссария"></nav>';
    if (window.PaleoGlossary) window.PaleoGlossary.init(container);
  }

  function renderInlineMarkdown(text) {
    if (typeof marked !== 'undefined' && marked.parseInline) {
      return marked.parseInline(text || '');
    }
    return escapeHtml(text || '').replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  }

  function parsePaleoMechanicsContent(content) {
    var labels = ['Образ', 'Функция', 'Палео-написание', 'Как работает', 'Пример в слове', 'Сравнение с греческой подменой'];
    var source = String(content || '').replace(/\r/g, '');
    var fields = {};

    labels.forEach(function(label, index) {
      var marker = '**' + label + ':**';
      var start = source.indexOf(marker);
      if (start === -1) return;
      start += marker.length;
      var end = source.length;
      labels.slice(index + 1).forEach(function(nextLabel) {
        var next = source.indexOf('**' + nextLabel + ':**', start);
        if (next !== -1 && next < end) end = next;
      });
      fields[label] = source.slice(start, end).trim();
    });

    fields.steps = (fields['Как работает'] || '').split('\n')
      .map(function(line) { return line.replace(/^\s*-\s*/, '').trim(); })
      .filter(Boolean);
    return fields;
  }

  function getPaleoGlyph(letterName) {
    var glyphs = {
      'Алеф': '𐤀', 'Бет': '𐤁', 'Гимель': '𐤂', 'Далет': '𐤃', 'Вав': '𐤅',
      'Хей': '𐤄', 'Заин': '𐤆', 'Хет': '𐤇', 'Тет': '𐤈', 'Йод': '𐤉',
      'Каф': '𐤊', 'Ламед': '𐤋', 'Мем': '𐤌', 'Нун': '𐤍', 'Самех': '𐤎',
      'Аин': '𐤏', 'Пей': '𐤐', 'Цади': '𐤑', 'Коф': '𐤒', 'Реш': '𐤓',
      'Шин': '𐤔', 'Тав': '𐤕'
    };
    return glyphs[letterName] || '';
  }

  function renderPaleoMechanicsDocument(container, documentData, options, backBtn) {
    var fields = parsePaleoMechanicsContent((documentData.sections || [])[0] && documentData.sections[0].content);
    var assemblyNames = (fields['Пример в слове'] || '').match(/[А-ЯЁ][а-яё]+/g) || [];
    var assemblyGlyphs = assemblyNames.map(getPaleoGlyph).filter(Boolean);
    var paleoAssembly = assemblyGlyphs.length ? assemblyGlyphs.join(' + ') : (fields['Палео-написание'] || '');
    var paleoWord = assemblyGlyphs.length ? assemblyGlyphs.join('') : (fields['Палео-написание'] || '');
    var image = fields['Образ'] || 'Палео-образ не указан';
    var functionText = fields['Функция'] || '';
    var exampleText = fields['Пример в слове'] || '';
    var comparisonText = fields['Сравнение с греческой подменой'] || '';
    var steps = fields.steps || [];
    var cards = [
      '<article class="paleo-module paleo-module-image">' +
        '<div class="paleo-module-heading"><img src="../../assets/icons/32/paleo/track.png" alt=""><h2>Образ</h2></div>' +
        '<p class="paleo-module-lead">' + renderInlineMarkdown(image) + '</p>' +
      '</article>',
      '<article class="paleo-module paleo-module-function">' +
        '<div class="paleo-module-heading"><img src="../../assets/icons/32/archaeology/testtube.png" alt=""><h2>Функция</h2></div>' +
        '<div class="paleo-module-copy">' + renderInlineMarkdown(functionText) + '</div>' +
      '</article>',
      '<article class="paleo-module paleo-module-example">' +
        '<div class="paleo-module-heading"><img src="../../assets/icons/32/ui/book.png" alt=""><h2>Пример в слове</h2></div>' +
        '<div class="paleo-word-display" lang="hbo">' + escapeHtml(paleoWord) + '</div>' +
        '<div class="paleo-assembly"><span>Сборка</span><strong lang="hbo">' + escapeHtml(paleoAssembly) + '</strong></div>' +
        '<p class="paleo-module-copy">' + renderInlineMarkdown(exampleText) + '</p>' +
      '</article>',
      '<article class="paleo-module paleo-module-steps">' +
        '<div class="paleo-module-heading"><img src="../../assets/icons/32/crafts/hammer-and-chisel.png" alt=""><h2>Как работает</h2></div>' +
        '<ol class="paleo-steps">' + steps.map(function(step, index) {
          return '<li class="paleo-step"><span>' + (index + 1) + '</span><div>' + renderInlineMarkdown(step) + '</div></li>';
        }).join('') + '</ol>' +
      '</article>',
      '<article class="paleo-module paleo-module-comparison">' +
        '<div class="paleo-module-heading"><img src="../../assets/icons/32/ui/scales.png" alt=""><h2>Сравнение с греческой подменой</h2></div>' +
        '<div class="paleo-comparison-copy">' + renderInlineMarkdown(comparisonText) + '</div>' +
      '</article>'
    ].join('');

    container.innerHTML = '<div class="research-page-head paleo-mechanics-head">' +
      '<h1>' + escapeHtml(documentData.title || 'Палео-механика') + '</h1>' +
      '<p class="subtitle text-muted">' + escapeHtml((documentData.description || '').replace(/---/g, '').trim()) + '</p>' +
      backBtn +
      '</div>' +
      '<div class="research-controls"><label>Документ<select id="research-paleo-mechanics-select" class="lab-input">' + options + '</select></label></div>' +
      '<div class="paleo-mechanics-modules">' + cards + '</div>';

    var select = document.getElementById('research-paleo-mechanics-select');
    if (select) select.addEventListener('change', function() {
      PageController.pageState['paleo-mechanics'].key = this.value;
      renderDocumentPage(container, 'paleo-mechanics', PageController.jsonCache['paleo-mechanics']);
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
      var iconPath = page === 'paleo-mechanics' ? '../../assets/icons/32/paleo/track.png' : '../../assets/icons/32/crafts/hammer-and-chisel.png';
      var docCards = keys.map(function(key, index) {
        var doc = data[key];
        return '<a href="#" class="doc-card" data-key="' + escapeHtml(key) + '" style="animation-delay: ' + (index * 50) + 'ms">' +
          '<img src="' + iconPath + '" class="doc-icon" alt="">' +
          '<div class="doc-name">' + escapeHtml(doc.title || key) + '</div>' +
          '<div class="doc-desc">' + escapeHtml((doc.description || '').split('---')[0].trim().substring(0, 120) + (doc.description && doc.description.length > 120 ? '...' : '')) + '</div>' +
          '</a>';
      }).join('');
      var heading = page === 'paleo-mechanics' ? 'Палео-механика' : 'Методички';
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
    var backBtn = '<button class="lab-btn lab-btn-secondary lab-btn-sm" onclick="PageController.pageState[\'' + page + '\'].key=\'\';PageController.renderDocumentPage(document.getElementById(\'' + page + '\'), \'' + page + '\', PageController.jsonCache[\'' + page + '\'])">← Назад к списку</button>';
    if (page === 'paleo-mechanics') {
      renderPaleoMechanicsDocument(container, documentData, options, backBtn);
      return;
    }
    var mechanismIndex = 0;
    var mechanismIcons = ['ui/question.png', 'ui/scales.png', 'paleo/track.png', 'ui/anchor.png', 'ui/diff.png', 'ui/arrows.png', 'ui/markbook.png'];
    var firstMechanismSummary = 'Система берёт два понятия, которые в иврите имеют ясное функциональное различие, и заменяет их моральной оценкой. Функция становится моралью. Пригодность становится «добром». Непригодность — «злом».';
    var sections = (documentData.sections || []).map(function(section) {
      var isMechanism = page === 'methodology' && /^\s*\d+[.)\-:]?\s+/.test(section.title || '');
      if (isMechanism) {
        var summary = String(section.content || '').replace(/\r/g, '').split(/\n\s*\n/)[0]
          .replace(/^\s*[-*]\s*/, '')
          .replace(/^\s*\*{0,2}Суть:\s*\*{0,2}/i, '')
          .replace(/\*\*/g, '').replace(/\s+/g, ' ').trim();
        if (mechanismIndex === 0) summary = firstMechanismSummary;
        summary = summary ? summary.charAt(0).toLocaleUpperCase('ru-RU') + summary.slice(1) : 'Краткое описание механизма подмены.';
        var icon = mechanismIcons[mechanismIndex % mechanismIcons.length];
        mechanismIndex++;
        return '<article class="research-section methodology-card"><div class="methodology-card-head"><h2><img src="../../assets/icons/32/' + icon + '" class="methodology-card-icon" alt="" aria-hidden="true">' + escapeHtml(section.title || '').replace(/^\s*\d+[.)\-:]?\s*/, '') + '</h2></div><div class="research-section-content"><p>' + escapeHtml(summary) + '</p></div></article>';
      }
      var content = typeof marked !== 'undefined' && marked.parse ? marked.parse(section.content || '') : escapeHtml(section.content || '');
      return '<article class="research-section"><h2>' + escapeHtml(section.title || '') + '</h2><div class="research-section-content">' + content + '</div></article>';
    }).join('');
    var heading = page === 'paleo-mechanics' ? (documentData.title || 'Палео-механика') : 'Методички';
    var documentDescription = escapeHtml(documentData.description || '');
    var paleoDescription = escapeHtml((documentData.description || '').replace(/---/g, '').trim());
    var documentHead = page === 'paleo-mechanics'
      ? '<div class="research-page-head"><h1>' + heading + '</h1>' +
        '<p class="subtitle text-muted">' + paleoDescription + '</p>' + backBtn + '</div>'
      : '<div class="research-page-head"><h1>' + heading + '</h1>' +
        '<p class="subtitle">Материалы ResearchLab, собранные из исходных Markdown-документов.</p></div>';
    container.innerHTML = documentHead +
      '<div class="research-controls"><label>Документ<select id="research-' + page + '-select" class="lab-input">' + options + '</select></label></div>' +
      (page === 'paleo-mechanics' ? '' : '<div class="research-meta">' + backBtn + '</div>') +
      (page === 'paleo-mechanics' ? '' : '<div class="research-description">' + documentDescription + '</div>') +
      '<div class="research-sections">' + sections + '</div>';
    var select = document.getElementById('research-' + page + '-select');
    if (select) select.addEventListener('change', function() {
      state.key = this.value;
      renderDocumentPage(container, page, data);
    });
  }

  function renderManifestPage(container, data) {
    document.title = 'Манифест — Golem';
    var story = data.story || {};
    var acts = story.acts || {};
    var problem = acts.problem || {};
    var methodology = acts.methodology || {};
    var application = acts.application || {};
    var paragraphs = function(items) {
      return (items || []).map(function(text) { return '<p>' + escapeHtml(text) + '</p>'; }).join('');
    };

    // Карта утрат — вертикальный стек слоёв без наложений.
    var lossHtml = (story.lossMap || []).map(function(layer, index) {
      var num = '0' + (index + 1);
      return '<li class="manifest-loss-layer">' +
        '<span class="manifest-loss-layer-num">' + num + '</span>' +
        '<div class="manifest-loss-layer-copy">' +
          '<h4 class="manifest-loss-layer-title">' + escapeHtml(layer.title) + '</h4>' +
          '<p class="manifest-loss-layer-text">' + escapeHtml(layer.text) + '</p>' +
        '</div>' +
        '<span class="manifest-loss-layer-percent">' + escapeHtml(layer.percent) + '</span>' +
      '</li>';
    }).join('');

    // Разбор Мицраим
    var mizraimSteps = (methodology.mizraim || []).map(function(step, index) {
      return '<li class="manifest-mizraim-step"><span class="manifest-mizraim-glyph paleo" lang="hbo">' + escapeHtml(step.glyph) + '</span>' +
        '<span class="manifest-mizraim-index">0' + (index + 1) + '</span><strong>' + escapeHtml(step.title) + '</strong><p>' + escapeHtml(step.text) + '</p></li>';
    }).join('');

    // Принцип потока
    var flow = methodology.flowPrinciple || {};
    var flowHtml = '';
    if (flow.title) {
      flowHtml = '<div class="manifest-flow">' +
        '<div class="manifest-section-heading"><div><span class="manifest-section-label">Принцип</span><h3>' + escapeHtml(flow.title) + '</h3></div></div>' +
        '<p class="manifest-flow-lead">' + escapeHtml(flow.lead || '') + '</p>' +
        '<p>' + escapeHtml(flow.body || '') + '</p>' +
        '<p class="manifest-flow-paleo"><span class="paleo" lang="hbo">' + escapeHtml(flow.paleoImage || '') + '</span></p>' +
        '<p class="manifest-flow-criterion">' + escapeHtml(flow.criterion || '') + '</p>' +
        '</div>';
    }

    // Эмет / Шекер
    var es = methodology.emetSheker || {};
    var emetShekerHtml = '';
    if (es.title) {
      var checksHtml = (es.checks || []).map(function(c, i) {
        return '<li><span class="manifest-es-check-num">' + (i + 1) + '</span><span>' + escapeHtml(c) + '</span></li>';
      }).join('');
      emetShekerHtml = '<div class="manifest-es">' +
        '<div class="manifest-section-heading"><div><span class="manifest-section-label">Критерий</span><h3>' + escapeHtml(es.title) + '</h3><p>' + escapeHtml(es.lead || '') + '</p></div></div>' +
        '<div class="manifest-es-pair">' +
          '<div class="manifest-es-card manifest-es-emet">' +
            '<div class="manifest-es-glyph paleo" lang="hbo">' + escapeHtml(es.emet.glyph) + '</div>' +
            '<h4>' + escapeHtml(es.emet.word) + '</h4>' +
            '<p class="manifest-es-meaning">' + escapeHtml(es.emet.meaning) + '</p>' +
            '<p class="manifest-es-paleo">' + escapeHtml(es.emet.paleoImage) + '</p>' +
          '</div>' +
          '<div class="manifest-es-card manifest-es-sheker">' +
            '<div class="manifest-es-glyph paleo" lang="hbo">' + escapeHtml(es.sheker.glyph) + '</div>' +
            '<h4>' + escapeHtml(es.sheker.word) + '</h4>' +
            '<p class="manifest-es-meaning">' + escapeHtml(es.sheker.meaning) + '</p>' +
            '<p class="manifest-es-paleo">' + escapeHtml(es.sheker.paleoImage) + '</p>' +
          '</div>' +
        '</div>' +
        '<ol class="manifest-es-checks">' + checksHtml + '</ol>' +
        '</div>';
    }

    // Давар
    var davar = methodology.davar || {};
    var davarHtml = '';
    if (davar.title) {
      var davarLetters = (davar.letters || []).map(function(l) {
        return '<div class="manifest-davar-letter">' +
          '<span class="manifest-davar-glyph paleo" lang="hbo">' + escapeHtml(l.glyph) + '</span>' +
          '<span class="manifest-davar-name">' + escapeHtml(l.name) + '</span>' +
          '<span class="manifest-davar-image">' + escapeHtml(l.image) + '</span>' +
        '</div>';
      }).join('');
      var exampleSteps = (davar.example && davar.example.steps || []).map(function(s, i) {
        return '<li><span class="manifest-davar-step-num">' + (i + 1) + '</span><span>' + escapeHtml(s) + '</span></li>';
      }).join('');
      davarHtml = '<div class="manifest-davar">' +
        '<div class="manifest-section-heading"><div><span class="manifest-section-label">Слово-действие</span><h3>' + escapeHtml(davar.title) + '</h3></div></div>' +
        '<p class="manifest-davar-lead">' + escapeHtml(davar.lead || '') + '</p>' +
        '<div class="manifest-davar-letters">' + davarLetters + '</div>' +
        '<p class="manifest-davar-assembly">' + escapeHtml(davar.assembly || '') + '</p>' +
        '<p class="manifest-davar-function">' + escapeHtml(davar.function || '') + '</p>' +
        '<p>' + escapeHtml(davar.body || '') + '</p>' +
        '<p class="manifest-davar-conclusion">' + escapeHtml(davar.conclusion || '') + '</p>' +
        (davar.example ? '<div class="manifest-davar-example">' +
          '<div class="manifest-davar-example-head">' +
            '<span class="manifest-davar-example-from">' + escapeHtml(davar.example.from) + '</span>' +
            '<span class="manifest-davar-example-davar paleo" lang="hbo">𐤃𐤁𐤓</span>' +
            '<span class="manifest-davar-example-text">' + escapeHtml(davar.example.davar) + '</span>' +
          '</div>' +
          '<ol class="manifest-davar-steps">' + exampleSteps + '</ol>' +
        '</div>' : '') +
        '</div>';
    }

    // Карта пространств
    var spaceCards = (story.spaces || []).map(function(space, index) {
      return '<article class="lab-card manifest-space-card" style="animation-delay:' + (index * 40) + 'ms">' +
        '<span class="manifest-space-glyph paleo" lang="hbo" aria-hidden="true">' + escapeHtml(space.glyph) + '</span>' +
        '<span class="manifest-space-index">0' + (index + 1) + ' · ' + escapeHtml(space.name) + '</span>' +
        '<h3>' + escapeHtml(space.title) + '</h3>' +
        '<p>' + escapeHtml(space.text) + '</p>' +
        '<p class="manifest-space-life"><strong>В жизни:</strong> ' + escapeHtml(space.life || '') + '</p>' +
        '<p class="manifest-space-examples"><strong>Примеры:</strong> ' + escapeHtml(space.examples || '') + '</p>' +
        '</article>';
    }).join('');

    // Палео-стандарт — 22 буквы
    var paleoLetters = story.paleoStandard || [];
    var paleoGridHtml = paleoLetters.map(function(letter, index) {
      return '<button type="button" class="manifest-paleo-card" data-paleo-index="' + index + '" ' +
        'aria-label="' + escapeHtml(letter.name) + ' — ' + escapeHtml(letter.image) + ', функция: ' + escapeHtml(letter.function) + '">' +
        '<span class="manifest-paleo-glyph paleo" lang="hbo">' + escapeHtml(letter.glyph) + '</span>' +
        '<span class="manifest-paleo-name">' + escapeHtml(letter.name) + '</span>' +
        '<span class="manifest-paleo-image">' + escapeHtml(letter.image) + '</span>' +
        '<span class="manifest-paleo-function">' + escapeHtml(letter.function) + '</span>' +
        '</button>';
    }).join('');

    // Шаги применения
    var appSteps = (application.steps || []).map(function(step, index) {
      return '<li class="manifest-app-step"><span class="manifest-app-step-num">' + (index + 1) + '</span>' +
        '<div><strong>' + escapeHtml(step.title) + '</strong><p>' + escapeHtml(step.text) + '</p></div></li>';
    }).join('');

    // Связанные документы
    var relatedDocs = (application.relatedDocs || []).map(function(doc) {
      return '<a href="' + escapeHtml(doc.path) + '" class="manifest-related-doc">' + escapeHtml(doc.title) + '</a>';
    }).join('');

    container.innerHTML = '<div class="manifest-progress" aria-hidden="true"><span class="manifest-progress-bar" id="manifest-progress-bar"></span></div>' +
      '<div class="manifest-toc" id="manifest-toc" aria-label="Навигация по манифесту">' +
      '<div class="manifest-toc-acts">' +
      '<a href="#manifest-act-problem" class="manifest-toc-link" data-toc="manifest-act-problem">Акт I · Проблема</a>' +
      '<a href="#manifest-act-methodology" class="manifest-toc-link" data-toc="manifest-act-methodology">Акт II · Методология</a>' +
      '<a href="#manifest-act-application" class="manifest-toc-link" data-toc="manifest-act-application">Акт III · Применение</a>' +
      '</div>' +
      '</div>' +
      '<div class="manifest-page">' +
      '<header class="manifest-hero">' +
      '<div class="manifest-watermark" aria-hidden="true">𐤀 𐤁 𐤂 𐤃 𐤄 𐤅</div>' +
      '<div class="manifest-kicker">RESEARCHLAB · МАНИФЕСТ v' + escapeHtml(data.version || '8.0') + '</div>' +
      '<h1>' + escapeHtml(story.title || data.title || 'Манифест проекта') + '</h1>' +
      '<p class="manifest-lead">' + escapeHtml(story.lead || data.description || '') + '</p>' +
      '</header><div class="manifest-hero-divider" aria-hidden="true"></div>' +

      // АКТ I: ПРОБЛЕМА
      '<section class="manifest-act manifest-act-problem" id="manifest-act-problem" aria-labelledby="manifest-problem-title">' +
      '<div class="manifest-act-heading"><span class="manifest-act-number">I</span><div><span class="manifest-section-label">Акт I · проблема</span><h2 id="manifest-problem-title">' + escapeHtml(problem.title || 'Проблема') + '</h2></div></div>' +
      '<div class="manifest-story-copy">' + paragraphs(problem.paragraphs) + '</div>' +
      '<section class="manifest-loss-section lab-card" aria-labelledby="manifest-loss-title"><div class="manifest-section-heading manifest-loss-heading"><div><span class="manifest-section-label">Карта утрат</span><h3 id="manifest-loss-title">Как образ сжимается до понятия</h3></div></div><ol class="manifest-loss-map" aria-label="Карта утрат">' + lossHtml + '</ol></section>' +
      '</section>' +

      // АКТ II: МЕТОДОЛОГИЯ
      '<section class="manifest-act manifest-act-methodology" id="manifest-act-methodology" aria-labelledby="manifest-methodology-title">' +
      '<div class="manifest-act-heading"><span class="manifest-act-number">II</span><div><span class="manifest-section-label">Акт II · методология</span><h2 id="manifest-methodology-title">' + escapeHtml(methodology.title || 'Методология') + '</h2></div></div>' +
      '<div class="manifest-story-copy">' + paragraphs(methodology.paragraphs) + '</div>' +

      // Разбор Мицраим
      '<div class="manifest-mizraim"><div class="manifest-section-heading"><div><span class="manifest-section-label">Разбор слова</span><h3>Мицраим</h3><p>' + escapeHtml(methodology.mizraimLead || '') + '</p></div></div><ol class="manifest-mizraim-list">' + mizraimSteps + '</ol><p class="manifest-mizraim-conclusion">' + escapeHtml(methodology.mizraimConclusion || '') + '</p></div>' +

      // Принцип потока
      flowHtml +

      // Эмет / Шекер
      emetShekerHtml +

      // Давар
      davarHtml +

      // Карта пространств
      '<section class="manifest-spaces-section" aria-labelledby="manifest-spaces-title"><div class="manifest-section-heading"><div><span class="manifest-section-label">Семь моделей среды</span><h3 id="manifest-spaces-title">Карта пространств</h3><p>Семь состояний, через которые проходит поток.</p></div></div><div class="manifest-spaces">' + spaceCards + '</div></section>' +

      // Палео-стандарт — интерактивная сетка 22 букв
      '<section class="manifest-paleo-section" aria-labelledby="manifest-paleo-title">' +
      '<div class="manifest-section-heading"><div><span class="manifest-section-label">Палео-стандарт</span><h3 id="manifest-paleo-title">Двадцать две буквы</h3><p>Наведи на букву — увидишь функцию. Нажми — получишь разбор.</p></div></div>' +
      '<div class="manifest-paleo-grid" id="manifest-paleo-grid">' + paleoGridHtml + '</div>' +
      '<div class="manifest-paleo-detail" id="manifest-paleo-detail" hidden aria-live="polite">' +
        '<div class="manifest-paleo-detail-glyph paleo" lang="hbo" id="manifest-paleo-detail-glyph"></div>' +
        '<div class="manifest-paleo-detail-info">' +
          '<h4 id="manifest-paleo-detail-name"></h4>' +
          '<p class="manifest-paleo-detail-image" id="manifest-paleo-detail-image"></p>' +
          '<p class="manifest-paleo-detail-function" id="manifest-paleo-detail-function"></p>' +
          '<p class="manifest-paleo-detail-desc" id="manifest-paleo-detail-desc"></p>' +
        '</div>' +
      '</div>' +
      '</section>' +

      '</section>' +

      // АКТ III: ПРИМЕНЕНИЕ
      '<section class="manifest-act manifest-act-application" id="manifest-act-application" aria-labelledby="manifest-application-title">' +
      '<div class="manifest-act-heading"><span class="manifest-act-number">III</span><div><span class="manifest-section-label">Акт III · применение</span><h2 id="manifest-application-title">' + escapeHtml(application.title || 'Применение') + '</h2></div></div>' +
      '<div class="manifest-story-copy">' + paragraphs(application.paragraphs) + '</div>' +
      (appSteps ? '<ol class="manifest-app-steps">' + appSteps + '</ol>' : '') +
      (relatedDocs ? '<div class="manifest-related"><div class="manifest-section-heading"><div><span class="manifest-section-label">Связанные документы</span><h3>Иди дальше</h3><p>Манифест говорит «что и зачем». Остальные документы — «как».</p></div></div><div class="manifest-related-list">' + relatedDocs + '</div></div>' : '') +
      '<div class="manifest-cta-wrap"><a class="lab-btn lab-btn-primary manifest-cta" href="#dashboard">Начать исследование <span aria-hidden="true">→</span></a>' +
      '<a class="lab-btn lab-btn-secondary manifest-cta manifest-cta-secondary" href="#root-dictionary">Открыть корневой словарь</a></div>' +
      '</section>' +

      '</div>';

    // Инициализация интерактивности палео-сетки
    initManifestPaleoGrid(container, paleoLetters);

    // Инициализация интерактивности карты утрат
    initManifestLossMap(container);

    // Инициализация оглавления, scroll-spy и progress-bar
    initManifestNav(container);
  }

  // ===== НАВИГАЦИЯ ПО МАНИФЕСТУ: TOC + SCROLL-SPY + PROGRESS =====
  function initManifestNav(container) {
    var toc = container.querySelector('#manifest-toc');
    var progressBar = container.querySelector('#manifest-progress-bar');
    var actIds = ['manifest-act-problem', 'manifest-act-methodology', 'manifest-act-application'];

    if (progressBar) {
      var doc = container;
      window.addEventListener('scroll', function() {
        var rect = doc.getBoundingClientRect();
        var total = doc.offsetHeight - window.innerHeight;
        if (total <= 0) return;
        var progress = Math.min(1, Math.max(0, -rect.top / total));
        progressBar.style.width = (progress * 100) + '%';
      }, { passive: true });
    }

    if (!toc) return;

    // Scroll-spy: подсветка текущего акта
    var links = toc.querySelectorAll('.manifest-toc-link');
    var spy = function() {
      var current = actIds[0];
      actIds.forEach(function(id) {
        var el = doc.querySelector('#' + id);
        if (!el) return;
        var rect = el.getBoundingClientRect();
        if (rect.top <= 120) current = id;
      });
      links.forEach(function(link) {
        link.classList.toggle('is-active', link.getAttribute('data-toc') === current);
      });
    };

    window.addEventListener('scroll', spy, { passive: true });
    spy();

    // Плавная прокрутка по якорям внутри SPA
    links.forEach(function(link) {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        var id = this.getAttribute('data-toc');
        var target = doc.querySelector('#' + id);
        if (!target) return;
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  // ===== ИНТЕРАКТИВНОСТЬ ПАЛЕО-СЕТКИ =====
  function initManifestPaleoGrid(container, letters) {
    var grid = container.querySelector('#manifest-paleo-grid');
    if (!grid || !letters.length) return;

    var detail = container.querySelector('#manifest-paleo-detail');
    var detailGlyph = container.querySelector('#manifest-paleo-detail-glyph');
    var detailName = container.querySelector('#manifest-paleo-detail-name');
    var detailImage = container.querySelector('#manifest-paleo-detail-image');
    var detailFunction = container.querySelector('#manifest-paleo-detail-function');
    var detailDesc = container.querySelector('#manifest-paleo-detail-desc');

    var cards = grid.querySelectorAll('.manifest-paleo-card');
    cards.forEach(function(card) {
      // Hover — подсветка и показ функции (CSS обрабатывает визуал)
      card.addEventListener('mouseenter', function() {
        cards.forEach(function(c) { c.classList.remove('is-hovered'); });
        card.classList.add('is-hovered');
      });

      // Click — разбор буквы
      card.addEventListener('click', function() {
        var idx = parseInt(card.getAttribute('data-paleo-index'), 10);
        var letter = letters[idx];
        if (!letter) return;

        cards.forEach(function(c) { c.classList.remove('is-active'); });
        card.classList.add('is-active');

        if (detail) {
          detail.hidden = false;
          if (detailGlyph) detailGlyph.textContent = letter.glyph;
          if (detailName) detailName.textContent = letter.name + ' — ' + letter.image;
          if (detailImage) detailImage.textContent = 'Образ: ' + letter.image;
          if (detailFunction) detailFunction.textContent = 'Функция: ' + letter.function;
          if (detailDesc) detailDesc.textContent = letter.desc;
        }
      });

      // Keyboard support
      card.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          card.click();
        }
      });
    });
  }

  // ===== ИНТЕРАКТИВНОСТЬ КАРТЫ УТРАТ =====
  function initManifestLossMap(container) {
    var cards = container.querySelectorAll('.manifest-loss-card');
    if (!cards.length) return;

    cards.forEach(function(card) {
      var detail = card.querySelector('.manifest-loss-card-detail');
      if (!detail) return;

      // Click — выезжающий блок с подробным описанием
      card.addEventListener('click', function() {
        var isOpen = !detail.hidden;
        // Закрываем все остальные
        cards.forEach(function(c) {
          var d = c.querySelector('.manifest-loss-card-detail');
          if (d && d !== detail) {
            d.hidden = true;
            c.classList.remove('is-expanded');
            c.setAttribute('aria-expanded', 'false');
          }
        });
        // Переключаем текущую
        detail.hidden = isOpen;
        card.classList.toggle('is-expanded', !isOpen);
        card.setAttribute('aria-expanded', !isOpen ? 'true' : 'false');
      });

      // Keyboard support
      card.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          card.click();
        }
      });
    });
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

  function renderAgentDetail(container, agentId) {
    var detail = container.querySelector('#agent-detail-view');
    var list = container.querySelector('.agent-list-view');
    var agent = (agentMapData || []).filter(function(item) { return item.id === agentId; })[0];
    if (!detail || !agent) return;
    if (list) list.hidden = true;
    detail.hidden = false;
    detail.innerHTML = '<div class="agent-detail-page">' +
      '<div class="agent-detail-hero"><div class="agent-detail-icon"><img src="../../assets/icons/32/' + escapeHtml(agent.icon) + '.png" alt=""></div><div><div class="agent-detail-kicker">GOLEM · AI-AGENTS</div><h1>' + escapeHtml(agent.name) + '</h1><p class="agent-detail-role">' + escapeHtml(agent.desc) + '</p><div class="agent-detail-meta"><span>' + escapeHtml(agent.cat) + '</span><span>' + escapeHtml(agent.model) + '</span><span class="agent-detail-status">Готов к запуску</span></div></div></div>' +
      '<div class="agent-detail-grid"><section class="agent-detail-section agent-detail-wide"><h2>Запуск агента</h2><form id="agent-run-form"><label for="agent-run-input">Запрос</label><textarea id="agent-run-input" class="lab-textarea agent-prompt" rows="4">разбери слово Берешит</textarea><button type="submit" class="lab-btn lab-btn-primary" id="agent-run-button">Запустить</button></form></section>' +
      '<section class="agent-detail-section agent-detail-wide"><h2>Результат</h2><pre id="agent-run-output" class="agent-output" aria-live="polite">Результат появится после запуска.</pre></section></div>' +
      '<button type="button" class="lab-btn lab-btn-secondary agent-detail-back" onclick="LabRouter.navigate(\'ai-agents\')">← К списку агентов</button></div>';
    var form = detail.querySelector('#agent-run-form');
    var input = detail.querySelector('#agent-run-input');
    var output = detail.querySelector('#agent-run-output');
    var button = detail.querySelector('#agent-run-button');
    form.addEventListener('submit', function(event) {
      event.preventDefault();
      var query = input.value.trim();
      if (!query) return;
      button.disabled = true;
      output.textContent = 'Запуск пайплайна…';
      checkAgentServer().then(function() {
        return fetch(AGENT_API_URL + '/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: query }) });
      })
        .then(function(response) { if (!response.ok) throw new Error('HTTP ' + response.status); return response.json(); })
        .then(function(result) { output.textContent = JSON.stringify(result, null, 2); })
        .catch(function(error) { output.innerHTML = isAgentServerUnavailable(error) ? agentServerMessage() : 'Ошибка запуска: ' + escapeHtml(error.message); })
        .then(function() { button.disabled = false; });
    });
  }

  function showAgentList(container) {
    var detail = container.querySelector('#agent-detail-view');
    var list = container.querySelector('.agent-list-view');
    var pipelines = container.querySelector('.agent-pipelines-view');
    if (detail) detail.hidden = true;
    if (pipelines) pipelines.hidden = true;
    if (list) list.hidden = false;
  }

  function openAgentPipelines(container) {
    var list = container.querySelector('.agent-list-view');
    var detail = container.querySelector('#agent-detail-view');
    var mapView = container.querySelector('.agent-map-view');
    var serverView = container.querySelector('.agent-server-view');
    var pipelines = container.querySelector('.agent-pipelines-view');
    if (!pipelines) {
      pipelines = document.createElement('section');
      pipelines.className = 'agent-pipelines-view';
      container.appendChild(pipelines);
    }
    if (list) list.hidden = true;
    if (detail) detail.hidden = true;
    if (mapView) mapView.hidden = true;
    if (serverView) serverView.hidden = true;
    pipelines.hidden = false;
    pipelines.innerHTML = '<div class="agent-pipelines-head"><div><p class="agent-detail-kicker">GOLEM · ОРКЕСТРАЦИЯ</p><h2>Пайплайны</h2><p>Готовые цепочки передачи контекста между агентами.</p></div><div class="pipeline-page-actions"><button type="button" class="lab-btn lab-btn-primary pipeline-create-btn" data-pipeline-create>+ Создать пайплайн</button><button type="button" class="lab-btn lab-btn-secondary" data-pipelines-back>← К списку агентов</button></div></div><div class="agent-pipelines-status lab-spinner show"><div class="loader"></div><div class="spinner-text">Загрузка пайплайнов…</div></div>';
    pipelines.querySelector('[data-pipelines-back]').addEventListener('click', function() {
      showAgentList(container);
    });
    checkAgentServer().then(function() {
      return fetch(AGENT_API_URL + '/api/pipelines');
    }).then(function(response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return response.json();
    }).then(function(data) {
      renderAgentPipelines(container, pipelines, data);
    }).catch(function(error) {
      pipelines.querySelector('.agent-pipelines-status').outerHTML = isAgentServerUnavailable(error) ? agentServerMessage() : '<div class="lab-alert lab-alert-error">Не удалось загрузить пайплайны: ' + escapeHtml(error.message) + '</div>';
    });
  }

  function renderAgentPipelines(container, pipelines, data) {
    var cards = (Array.isArray(data) ? data : []).map(function(pipeline) {
      var agents = (pipeline.agents || []).map(function(agentName, agentIndex) {
        var agent = (agentMapData || []).filter(function(item) { return item.name === agentName; })[0] || { name: agentName, desc: 'Участник цепочки передачи контекста.', icon: 'paleo/track' };
        return (agentIndex ? '<span class="pipeline-flow-arrow" aria-hidden="true">→</span>' : '') + '<li class="pipeline-timeline-step" tabindex="0" title="' + escapeHtml(agent.desc) + '" data-agent-name="' + escapeHtml(agent.name) + '" data-status="pending"><img src="../../assets/icons/32/' + escapeHtml(agent.icon) + '.png" alt=""><span class="pipeline-status-dot" aria-hidden="true"></span><div><strong>' + escapeHtml(agent.name) + '</strong><small>' + escapeHtml(agent.desc) + '</small></div></li>';
      }).join('');
      return '<article class="agent-pipeline-card" data-pipeline-id="' + escapeHtml(pipeline.id) + '"><div class="pipeline-card-head"><div class="pipeline-card-title"><img src="../../assets/icons/32/paleo/track.png" alt=""><h3>' + escapeHtml(pipeline.name) + '</h3><span class="pipeline-status-badge" data-pipeline-run-status data-status="pending">Ожидание запуска</span></div><div class="agent-pipeline-actions"><button type="button" class="pipeline-icon-btn" data-pipeline-edit aria-label="Редактировать пайплайн">✎</button><button type="button" class="pipeline-icon-btn pipeline-delete" data-pipeline-delete aria-label="Удалить пайплайн">✕</button></div></div><p class="agent-pipeline-route">' + escapeHtml(pipeline.description || 'Цепочка передачи контекста') + '</p><ol class="pipeline-timeline" aria-label="Этапы пайплайна">' + agents + '</ol><button type="button" class="lab-btn lab-btn-primary pipeline-run-btn" data-pipeline-run>Запустить</button></article>';
    }).join('');
    pipelines.querySelector('.agent-pipelines-status').outerHTML = '<div class="agent-pipelines-grid">' + (cards || '<div class="lab-alert lab-alert-info">Пайплайны пока не созданы.</div>') + '</div>';
    pipelines.querySelector('[data-pipeline-create]').addEventListener('click', function() { openPipelineModal(container, pipelines, null); });
    pipelines.querySelectorAll('[data-pipeline-edit]').forEach(function(button) {
      button.addEventListener('click', function() { openPipelineModal(container, pipelines, findPipeline(data, this.closest('[data-pipeline-id]').dataset.pipelineId)); });
    });
    pipelines.querySelectorAll('[data-pipeline-delete]').forEach(function(button) {
      button.addEventListener('click', function() { deletePipeline(container, pipelines, data, this.closest('[data-pipeline-id]').dataset.pipelineId); });
    });
    pipelines.querySelectorAll('[data-pipeline-run]').forEach(function(button) {
      button.addEventListener('click', function() { runPipeline(this.closest('[data-pipeline-id]'), findPipeline(data, this.closest('[data-pipeline-id]').dataset.pipelineId)); });
    });
  }

  function runPipeline(card, pipeline) {
    var steps = Array.prototype.slice.call(card.querySelectorAll('.pipeline-timeline-step'));
    var status = card.querySelector('[data-pipeline-run-status]');
    var button = card.querySelector('[data-pipeline-run]');
    if (!steps.length || !pipeline || button.disabled) return;
    button.disabled = true;
    steps.forEach(function(step) { step.dataset.status = 'pending'; });
    var index = 0;
    function advance() {
      if (index >= steps.length) {
        status.textContent = 'Готово';
        status.dataset.status = 'done';
        button.disabled = false;
        return;
      }
      var step = steps[index];
      step.dataset.status = 'running';
      status.textContent = '⏳ ' + step.dataset.agentName;
      setTimeout(function() {
        if (pipeline.failAt && index === pipeline.failAt) {
          step.dataset.status = 'error';
          status.textContent = 'Ошибка: ' + step.dataset.agentName;
          status.dataset.status = 'error';
          button.disabled = false;
          return;
        }
        step.dataset.status = 'done';
        index += 1;
        advance();
      }, 700);
    }
    advance();
  }

  function findPipeline(pipelines, id) {
    return pipelines.filter(function(item) { return item.id === id; })[0] || null;
  }

  function openPipelineModal(container, pipelines, pipeline) {
    var modal = document.createElement('div');
    modal.className = 'pipeline-modal';
    modal.innerHTML = '<div class="pipeline-modal-backdrop" data-pipeline-close></div><form class="pipeline-dialog"><div class="modal-header"><h3>' + (pipeline ? 'Редактировать пайплайн' : 'Новый пайплайн') + '</h3><button type="button" class="modal-close" data-pipeline-close aria-label="Закрыть">×</button></div><div class="pipeline-form-body"><label>Название<input name="name" class="lab-input" required maxlength="100" value="' + escapeHtml(pipeline ? pipeline.name : '') + '"></label><label>Краткое описание<textarea name="description" class="lab-textarea" rows="3" maxlength="240">' + escapeHtml(pipeline ? pipeline.description : '') + '</textarea></label><fieldset><legend>Агенты по порядку</legend><div class="pipeline-agent-list" data-pipeline-agent-list></div><div class="pipeline-agent-add"><select class="lab-select" data-pipeline-agent-select><option value="">Выберите агента</option>' + agentMapData.map(function(agent) { return '<option value="' + escapeHtml(agent.name) + '">' + escapeHtml(agent.name) + '</option>'; }).join('') + '</select><button type="button" class="lab-btn lab-btn-secondary" data-pipeline-agent-add>Добавить</button></div></fieldset></div><div class="modal-footer"><button type="button" class="lab-btn lab-btn-secondary" data-pipeline-close>Отмена</button><button type="submit" class="lab-btn lab-btn-primary">Сохранить</button></div></form>';
    document.body.appendChild(modal);
    var list = modal.querySelector('[data-pipeline-agent-list]');
    var selected = (pipeline && pipeline.agents || []).slice();
    function renderSelected() { list.innerHTML = selected.map(function(agent, index) { return '<div class="pipeline-agent-row"><span>' + (index + 1) + '. ' + escapeHtml(agent) + '</span><button type="button" data-agent-up aria-label="Поднять">↑</button><button type="button" data-agent-down aria-label="Опустить">↓</button><button type="button" data-agent-remove aria-label="Удалить">✕</button></div>'; }).join('') || '<span class="text-muted">Добавьте хотя бы одного агента.</span>'; }
    renderSelected();
    modal.querySelector('[data-pipeline-agent-add]').addEventListener('click', function() { var value = modal.querySelector('[data-pipeline-agent-select]').value; if (value && selected.indexOf(value) === -1) { selected.push(value); renderSelected(); } });
    list.addEventListener('click', function(event) { var row = event.target.closest('.pipeline-agent-row'); if (!row) return; var index = Array.prototype.indexOf.call(list.children, row); if (event.target.hasAttribute('data-agent-up') && index > 0) { var item = selected.splice(index, 1)[0]; selected.splice(index - 1, 0, item); } if (event.target.hasAttribute('data-agent-down') && index < selected.length - 1) { var next = selected.splice(index, 1)[0]; selected.splice(index + 1, 0, next); } if (event.target.hasAttribute('data-agent-remove')) selected.splice(index, 1); renderSelected(); });
    modal.querySelectorAll('[data-pipeline-close]').forEach(function(button) { button.addEventListener('click', function() { modal.remove(); }); });
    modal.querySelector('form').addEventListener('submit', function(event) { event.preventDefault(); var form = new FormData(event.target); if (!selected.length) { alert('Добавьте хотя бы одного агента.'); return; } savePipeline(container, pipelines, pipeline, { name: form.get('name'), description: form.get('description'), agents: selected }).then(function() { modal.remove(); }); });
  }

  function savePipeline(container, pipelines, pipeline, payload) {
    return fetch(AGENT_API_URL + '/api/pipelines' + (pipeline ? '/' + encodeURIComponent(pipeline.id) : ''), { method: pipeline ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }).then(function(response) { if (!response.ok) return response.json().then(function(error) { throw new Error(error.error || 'HTTP ' + response.status); }); return response.json(); }).then(function() { openAgentPipelines(container); });
  }

  function deletePipeline(container, pipelines, data, id) {
    if (!window.confirm('Удалить этот пайплайн?')) return;
    fetch(AGENT_API_URL + '/api/pipelines/' + encodeURIComponent(id), { method: 'DELETE' }).then(function(response) { if (!response.ok) throw new Error('HTTP ' + response.status); return response.json(); }).then(function() { openAgentPipelines(container); }).catch(function(error) { alert('Не удалось удалить пайплайн: ' + error.message); });
  }

  // ===== ОСНОВНОЙ МЕТОД РЕНДЕРИНГА =====
  function render(moduleId, container, parsed) {
    console.log('[PC] Рендерим модуль:', moduleId, container);
    if (!container) return;

    if (container.dataset.loaded && container.innerHTML.trim() !== '') {
      if (moduleId === 'scripture-reader' && window.ScriptureReader) {
        window.ScriptureReader.init(parsed);
      }
      if (moduleId === 'methodology' && window.MethodologyLab) {
        window.MethodologyLab.init(container, parsed);
      }
      if (moduleId === 'ai-agents' && parsed && parsed.segments && parsed.segments[1]) {
        renderAgentDetail(container, parsed.segments[1]);
      } else if (moduleId === 'ai-agents') {
        showAgentList(container);
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

      case 'analyzers':
      case 'layer-analyzer':
      case 'ai-analyzer':
      case 'dialect-analyzer':
        container.innerHTML = '';
        container.dataset.loaded = '1';
        if (window.GolemAnalyzers) window.GolemAnalyzers.render(container, moduleId);
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
        if (window.RootDict) RootDict.init();
        break;

      case 'paleo-glossary':
        container.innerHTML = '<div class="paleo-glossary-page">' +
          '<header class="paleo-glossary-head">' +
          '<div class="paleo-glossary-icon" aria-hidden="true">𐤌</div>' +
          '<div><p class="paleo-glossary-kicker">ГОЛЕМ · ИНСТРУМЕНТЫ</p><h1>Палео-глоссарий</h1>' +
          '<p class="subtitle">Первая партия: 100 слов как русла потока — палео-форма, квадратное письмо, функция и корень.</p></div>' +
          '</header>' +
          '<div class="paleo-glossary-controls">' +
          '<label class="paleo-glossary-search">Поиск<input id="paleo-glossary-search" class="lab-input" type="search" placeholder="Палео-форма, слово или транслитерация" autocomplete="off"></label>' +
          '<label>Корень<select id="paleo-glossary-root" class="lab-input"><option value="all">Все корни</option></select></label>' +
          '</div>' +
          '<div id="paleo-glossary-meta" class="paleo-glossary-meta" aria-live="polite"></div>' +
          '<div id="paleo-glossary-grid" class="paleo-glossary-grid"></div>' +
          '<nav id="paleo-glossary-pagination" class="paleo-glossary-pagination" aria-label="Страницы глоссария"></nav>' +
          '</div>';
        container.dataset.loaded = '1';
        if (window.PaleoGlossary) window.PaleoGlossary.init(container);
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
        container.innerHTML = '<header class="section-hero">' +
          '<div class="section-hero-watermark" aria-hidden="true">𐤀 𐤁 𐤂 𐤃 𐤄 𐤅</div>' +
          '<div class="section-hero-kicker">ГОЛЕМ · РАССЛЕДОВАНИЕ</div>' +
          '<h1><img src="../../assets/icons/32/ui/question.png" class="lab-icon" alt="">Расследование</h1>' +
          '<p class="section-hero-lead">Введите слово, корень или перевод. Сопоставьте происхождение, цепочку подмен и текстовые свидетельства.</p>' +
        '</header>' +
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
        if (window.Religionisms) Religionisms.init();
        break;

      case 'translation-comparator':
        container.innerHTML = '<div class="tc-search-row"><label for="tc-search">Ссылка на стих</label><div class="search-wrap">' +
          '<input type="text" id="tc-search" class="lab-input" placeholder="Берешит 1:1, Исайя 53:5" />' +
          '<button class="lab-btn lab-btn-primary" onclick="TransComp.search()"><img src="../../assets/icons/32/ui/book.png" width="32" height="32" alt="">Показать</button></div></div>' +
          '<div id="tc-placeholder" class="lab-alert lab-alert-info">Введите ссылку на стих. Пример: <strong>Берешит 1:1</strong>.</div>' +
          '<main id="tc-results" class="tc-map-page" style="display:none;">' +
          '<section class="tc-section"><h2><img src="../../assets/icons/32/scribe/scroll.png" alt="">Ивритские источники</h2><div class="tc-source-grid">' +
          '<article class="lab-card tc-source-card"><h3><img src="../../assets/icons/32/scribe/scroll.png" alt=""><span>ТМ<small>масоретский текст · квадратное письмо</small></span></h3><div id="tc-tm" class="tc-text tc-hebrew" dir="rtl" lang="he"></div></article>' +
          '<article class="lab-card tc-source-card"><h3><img src="../../assets/icons/32/scribe/scroll.png" alt=""><span>Кумранский свиток<small>квадратное письмо · без огласовок</small></span></h3><div id="tc-qumran" class="tc-text tc-hebrew" dir="rtl" lang="he"></div></article>' +
          '<article class="lab-card tc-source-card"><h3><img src="../../assets/icons/32/paleo/track.png" alt=""><span>Сам. Пятикнижие<small>палео-шрифт</small></span></h3><div id="tc-samaritan" class="tc-text tc-paleo" lang="hbo"></div></article></div></section>' +
          '<section class="tc-section"><h2><img src="../../assets/icons/32/scribe/scroll.png" alt="">Древние переводы</h2><div class="tc-source-grid"><article class="lab-card tc-source-card"><h3><img src="../../assets/icons/32/scribe/scroll.png" alt=""><span>LXX <small>греч.</small></span></h3><div id="tc-lxx" class="tc-text"></div></article><article class="lab-card tc-source-card"><h3><img src="../../assets/icons/32/scribe/scroll.png" alt=""><span>Пешитта <small>сир.</small></span></h3><div id="tc-peshitta" class="tc-text" dir="rtl" lang="syr"></div></article><article class="lab-card tc-source-card"><h3><img src="../../assets/icons/32/scribe/scroll.png" alt=""><span>Вульгата <small>лат.</small></span></h3><div class="tc-text">Латинский слой пока не загружен.</div></article></div></section>' +
          '<section class="tc-section"><h2><img src="../../assets/icons/32/scribe/scroll.png" alt="">Современные переводы</h2><div class="tc-source-grid"><article class="lab-card tc-source-card"><h3><img src="../../assets/icons/32/scribe/scroll.png" alt=""><span>Синодальный <small>рус.</small></span></h3><div id="tc-synodal" class="tc-text"></div></article><article class="lab-card tc-source-card"><h3><img src="../../assets/icons/32/scribe/scroll.png" alt=""><span>Современный русский</span></h3><div id="tc-modern" class="tc-text"></div></article></div></section>' +
          '<section id="tc-analysis-section" class="tc-source-analysis tc-analysis-section" hidden aria-labelledby="tc-source-analysis-title"><h2 id="tc-source-analysis-title"><img src="../../assets/icons/32/ui/scales.png" alt="">Аналитика расхождений</h2><div class="tc-analysis-subsection"><h3>Расхождения и разбор</h3><div id="tc-divergence-block" class="tc-analysis-block"><h4>Описание расхождения</h4><div id="tc-divergence" class="tc-analysis-text"></div></div><div id="tc-paleo-block" class="tc-analysis-block"><h4>Палео-разбор ключевых слов</h4><div id="tc-paleo-analysis" class="tc-analysis-text"></div></div></div><div class="tc-analysis-subsection tc-analysis-stats"><h3>Статистика</h3><div id="tc-source-ratio" class="tc-source-ratio"></div><p id="tc-source-key-difference" class="tc-source-key-difference"></p></div></section></main>';
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
        var agentSlugs = ['orchestrator', 'researcher', 'exposer', 'collector', 'critic', 'semitologist', 'comparator', 'editor', 'paleo-translator', 'frontend-developer', 'ai-engineer', 'verifier', 'technical-writer', 'code-reviewer', 'flow-architect', 'liaison'];
        agents.forEach(function(a, i) { a.id = agentSlugs[i] || ('agent-' + i); });
        agentMapData = agents;
        var cards = agents.map(function(a) {
          return '<button type="button" class="tool-card agent-card agent-list-card' + (a.featured ? ' agent-card-orchestrator' : '') + '" data-agent-id="' + a.id + '" onclick="LabRouter.navigate(\'ai-agents\',[\'' + a.id + '\'])" aria-label="Открыть страницу агента: ' + a.name + '"><span class="tool-icon"><img src="../../assets/icons/32/' + a.icon + '.png" width="32" height="32" alt="' + a.name + '"></span>' +
            '<div class="tool-name">' + a.name + '</div>' +
            '<div class="tool-desc">' + a.desc + '</div>' +
            '<span class="tool-badge model agent-list-model">' + a.model + '</span>' +
            '<span class="agent-list-role" hidden>' + a.cat + '</span>' +
            '<span class="badge-category">' + a.cat + '</span>' +
            '<span class="badge-dev ' + (a.featured ? 'badge-dev-active' : 'badge-dev-progress') + '">' + (a.featured ? 'Активен' : 'В разработке') + '</span></button>';
        }).join('');
        container.innerHTML = '<div class="agent-list-view"><div class="agent-grid">' + cards + '</div></div>' +
          '<div id="agent-detail-view" class="agent-detail-view" hidden></div>' +
          '<div id="agent-map-view" class="agent-map-view" hidden></div>' +
          '<div id="agent-server-view" class="agent-server-view" hidden></div>' +
          '<div class="agent-pipelines-view" hidden></div>';
        var agentControls = document.createElement('section');
        agentControls.className = 'agent-controls-panel';
        agentControls.setAttribute('aria-label', 'Управление агентами');
        agentControls.innerHTML = '<button type="button" class="lab-btn lab-btn-primary agent-control-button" data-agent-map-open><img src="../../assets/icons/32/ui/web.png" alt="" aria-hidden="true"><span>Карта агентов</span></button>' +
          '<button type="button" class="lab-btn lab-btn-secondary agent-control-button" data-agent-pipelines-open><img src="../../assets/icons/32/paleo/track.png" alt="" aria-hidden="true"><span>Пайплайны</span></button>' +
          '<button type="button" class="lab-btn lab-btn-secondary agent-control-button" data-agent-server-open><img src="../../assets/icons/32/ui/settings.png" alt="" aria-hidden="true"><span>Запустить сервер</span></button>';
        container.insertBefore(agentControls, container.querySelector('.agent-list-view'));
        agentControls.querySelector('[data-agent-map-open]').addEventListener('click', function() {
          if (window.AgentMap) window.AgentMap.open();
        });
        agentControls.querySelector('[data-agent-pipelines-open]').addEventListener('click', function() {
          openAgentPipelines(container);
        });
        agentControls.querySelector('[data-agent-server-open]').addEventListener('click', function() {
          if (window.AgentServer) window.AgentServer.open();
        });
        container.dataset.loaded = '1';
        if (parsed && parsed.segments && parsed.segments[1]) {
          renderAgentDetail(container, parsed.segments[1]);
        }
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

      case 'state-checker':
        showSpinner(container, 'Загрузка чекера стран…');
        if (window.StateChecker) {
          window.StateChecker.init(container);
        } else {
          showError(container, 'Модуль «Чекер стран» не загрузился.');
        }
        container.dataset.loaded = '1';
        break;

      case 'tree-checker':
        showSpinner(container, 'Загрузка дерева…');
        if (window.TreeChecker) {
          window.TreeChecker.init(container);
        } else {
          showError(container, 'Модуль «Чекер дерева» не загрузился.');
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

      case 'timeline':
        showSpinner(container, 'Загрузка палео-таймлайна…');
        if (window.Timeline) {
          container.dataset.loaded = '1';
          window.Timeline.init(container, parsed);
        } else {
          showError(container, 'Модуль «Палео-таймлайн» не загрузился.');
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
          window.MethodologyLab.init(container, parsed);
        } else {
          showError(container, 'Модуль «Методология» не загрузился.');
        }
        container.dataset.loaded = '1';
        break;

      case 'name-decoder':
        showSpinner(container, 'Загрузка чекера имени…');
        if (window.NameDecoder) {
          window.NameDecoder.init(container);
        } else {
          showError(container, 'Модуль «Чекер имени» не загрузился.');
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
        if (jsonCache.manifest) {
          renderManifestPage(container, jsonCache.manifest);
          container.dataset.loaded = '1';
          break;
        }
        fetchJson('data/methodology/manifest.json').then(function(data) {
          jsonCache.manifest = data;
          renderManifestPage(container, data);
          container.dataset.loaded = '1';
        }).catch(function(err) {
          showError(container, 'Ошибка загрузки манифеста: ' + err.message);
        });
        break;

      case 'dictionaries':
        loadJsonPage('dictionaries', 'data/dictionaries.json', container);
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