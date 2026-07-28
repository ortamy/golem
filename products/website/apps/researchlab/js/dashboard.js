/**
 * dashboard.js — «Рабочий стол исследователя» (#dashboard)
 * Виджеты со статистикой, собранной из data/roots/roots.json, data/dictionaries.json,
 * data/exposures/index.json, data/heraldry/heraldry.json, data/qumran-books.json.
 */
const Dashboard = (function() {
  'use strict';

  var loaded = false;
  var reloading = false;

  function esc(text) {
    var d = document.createElement('div');
    d.textContent = text == null ? '' : String(text);
    return d.innerHTML;
  }

  function fetchJson(path) {
    var forceReload = arguments.length > 1 && arguments[1];
    var requestPath = forceReload ? path + '?_reload=' + Date.now() : path;
    return fetch(requestPath, forceReload ? { cache: 'no-store' } : undefined).then(function(r) {
      if (!r.ok) throw new Error('HTTP ' + r.status + ' для ' + path);
      return r.json();
    });
  }

  function loadData(forceReload) {
    return Promise.all([
      fetchJson('data/roots/roots.json', forceReload),
      fetchJson('data/dictionaries.json', forceReload),
      fetchJson('data/exposures/index.json', forceReload),
      fetchJson('data/heraldry/heraldry.json', forceReload),
      fetchJson('data/qumran-books.json', forceReload),
      fetchJson('data/scripture/bereshit-1.json', forceReload).catch(function() { return []; })
    ]).then(function(results) {
      return {
        roots: results[0] || [],
        dictionaries: results[1] || {},
        researches: results[2] || [],
        heraldry: results[3] || [],
        qumranBooks: (results[4] && results[4].books) || [],
        scriptureVerses: results[5] || []
      };
    });
  }

  function init() {
    var container = document.getElementById('dashboard-widgets');
    if (!container) return;
    if (loaded) return;

    loadData(false).then(function(data) {
      loaded = true;
      render(container, data);
    }).catch(function(err) {
      container.innerHTML = '<div class="lab-alert lab-alert-error">Ошибка загрузки статистики: ' + esc(err.message) + '</div>';
    });
  }

  function reload() {
    var container = document.getElementById('dashboard-widgets');
    if (!container || reloading) return;
    reloading = true;
    container.innerHTML = '<div class="lab-spinner show"><div class="loader"></div><div class="spinner-text">Обновление статистики…</div></div>';
    loadData(true).then(function(data) {
      loaded = true;
      render(container, data);
    }).catch(function(err) {
      container.innerHTML = '<div class="lab-alert lab-alert-error">Ошибка обновления статистики: ' + esc(err.message) + '</div>';
    }).then(function() {
      reloading = false;
    });
  }

  function render(container, data) {
    var dictEntries = Object.keys(data.dictionaries).map(function(key) {
      var dict = data.dictionaries[key];
      return { key: key, title: dict.title || key, count: (dict.terms || []).length };
    }).sort(function(a, b) { return b.count - a.count; });

    var totalTerms = dictEntries.reduce(function(sum, d) { return sum + d.count; }, 0);

    container.innerHTML =
      renderCounters(data, dictEntries, totalTerms) +
      '<div class="dw-grid">' +
        renderSubstitutionMap(dictEntries) +
        renderMechanismsBars(dictEntries) +
        renderLatestResearches(data.researches) +
        renderBooksProgress(data.qumranBooks, data.scriptureVerses) +
      '</div>';

    bindMapClicks(container);
  }

  function renderCounters(data, dictEntries, totalTerms) {
    var items = [
      { num: data.roots.length, label: 'Корней' },
      { num: totalTerms, label: 'Терминов подмен' },
      { num: data.researches.length, label: 'Исследований' },
      { num: dictEntries.length, label: 'Словарей' },
      { num: data.heraldry.length, label: 'Империй/гербов' }
    ];
    return '<div class="dw-counters">' + items.map(function(item) {
      return '<div class="dw-counter"><div class="dw-num">' + esc(item.num) + '</div><div class="dw-label">' + esc(item.label) + '</div></div>';
    }).join('') + '</div>';
  }

  function renderSubstitutionMap(dictEntries) {
    var top = dictEntries.slice(0, 6);
    var cx = 200, cy = 180;
    // Фиксированная геометрия сохраняет карту цельной при любом ресайзе SVG.
    var nodePositions = [
      { x: 200, y: 42 },
      { x: 300, y: 111 },
      { x: 300, y: 249 },
      { x: 200, y: 318 },
      { x: 100, y: 249 },
      { x: 100, y: 111 }
    ];
    var lines = '', nodes = '';

    top.forEach(function(d, i) {
      var position = nodePositions[i];
      var x = position.x;
      var y = position.y;
      var label = String(d.title || d.key);
      var nodeWidth = Math.min(180, Math.max(94, label.length * 7 + 42));
      lines += '<line class="dw-map-line" x1="' + cx + '" y1="' + cy + '" x2="' + x + '" y2="' + y + '"></line>';
      nodes += '<g class="dw-map-node" data-dict-key="' + esc(d.key) + '" role="button" tabindex="0" aria-label="Открыть словарь: ' + esc(label) + '" transform="translate(' + x.toFixed(1) + ',' + y.toFixed(1) + ')">' +
        '<rect x="-' + (nodeWidth / 2).toFixed(1) + '" y="-20" width="' + nodeWidth.toFixed(1) + '" height="40" rx="24"></rect>' +
        '<text dy="4">' + esc(label) + '</text>' +
      '</g>';
    });

    var svg = '<svg viewBox="0 0 400 360" role="img" aria-label="Карта подмен">' +
      lines +
      '<g class="dw-map-center" transform="translate(' + cx + ',' + cy + ')"><circle r="34"></circle><image href="../../assets/icons/32/ui/book.png" x="-15" y="-15" width="30" height="30" preserveAspectRatio="xMidYMid meet" role="presentation"></image></g>' +
      nodes +
    '</svg>';

    return '<div class="dw-widget dw-widget-wide">' +
      '<h3>Карта подмен</h3>' +
      '<div class="dw-map">' + svg + '</div>' +
    '</div>';
  }

  function renderMechanismsBars(dictEntries) {
    var top = dictEntries.slice(0, 8);
    var maxCount = top.reduce(function(m, d) { return Math.max(m, d.count); }, 1);
    var bars = top.map(function(d) {
      var pct = Math.round((d.count / maxCount) * 100);
      return '<div class="dw-bar-row" data-dict-key="' + esc(d.key) + '" role="button" tabindex="0">' +
        '<span class="dw-bar-label" title="' + esc(d.title) + '">' + esc(d.title) + '</span>' +
        '<span class="dw-bar-track"><span class="dw-bar-fill" style="width:' + pct + '%"></span></span>' +
        '<span class="dw-bar-value">' + esc(d.count) + '</span>' +
      '</div>';
    }).join('');
    return '<div class="dw-widget">' +
      '<h3>Топ словарей подмен</h3>' +
      '<div class="dw-bars">' + bars + '</div>' +
    '</div>';
  }

  function renderLatestResearches(researches) {
    var latest = researches.slice().sort(function(a, b) {
      return String(b.date || '').localeCompare(String(a.date || ''));
    }).slice(0, 5);
    var items = latest.map(function(item) {
      return '<a class="dw-list-item" href="#researches">' +
        '<div class="dw-list-title">' + esc(item.title) + '</div>' +
        '<div class="dw-list-meta">' + esc(item.category || '') + (item.date ? ' · ' + esc(item.date) : '') + '</div>' +
      '</a>';
    }).join('');
    return '<div class="dw-widget">' +
      '<h3>Последние разборы</h3>' +
      '<div class="dw-list">' + (items || '<div class="lab-alert lab-alert-info">Пока пусто.</div>') + '</div>' +
    '</div>';
  }

  function renderBooksProgress(books, verses) {
    var withData = (books || []).filter(function(b) { return b && b.dataFile; });
    var pctBooks = books.length ? Math.round((withData.length / books.length) * 100) : 0;
    var bookNames = withData.map(function(b) { return b.ru; }).join(', ') || '—';
    return '<div class="dw-widget">' +
      '<h3>Прогресс по книгам</h3>' +
      '<div class="dw-progress-track"><div class="dw-progress-fill" style="width:' + pctBooks + '%">' + withData.length + ' / ' + books.length + '</div></div>' +
      '<div class="dw-progress-caption">Оцифровано: ' + esc(bookNames) + ' — ' + esc(verses.length) + ' стихов на палео-иврите.</div>' +
    '</div>';
  }

  function bindMapClicks(container) {
    container.querySelectorAll('[data-dict-key]').forEach(function(el) {
      var go = function() {
        var key = el.getAttribute('data-dict-key');
        if (window.PageController && PageController.pageState && PageController.pageState.dictionaries) {
          PageController.pageState.dictionaries.key = key;
          PageController.pageState.dictionaries.query = '';
        }
        LabRouter.navigate('dictionaries');
      };
      el.addEventListener('click', go);
      el.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); }
      });
    });
  }

  window.Dashboard = { init: init, reload: reload };
  return window.Dashboard;
})();
