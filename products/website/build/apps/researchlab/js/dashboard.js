/**
 * dashboard.js — «Рабочий стол исследователя» (#dashboard)
 * Виджеты со статистикой, собранной из data/roots.json, data/dictionaries.json,
 * data/researches.json, data/heraldry.json, data/qumran-books.json.
 */
const Dashboard = (function() {
  'use strict';

  var loaded = false;

  function esc(text) {
    var d = document.createElement('div');
    d.textContent = text == null ? '' : String(text);
    return d.innerHTML;
  }

  function fetchJson(path) {
    return fetch(path).then(function(r) {
      if (!r.ok) throw new Error('HTTP ' + r.status + ' для ' + path);
      return r.json();
    });
  }

  function init() {
    var container = document.getElementById('dashboard-widgets');
    if (!container) return;
    if (loaded) return;

    Promise.all([
      fetchJson('data/roots.json'),
      fetchJson('data/dictionaries.json'),
      fetchJson('data/researches.json'),
      fetchJson('data/heraldry.json'),
      fetchJson('data/qumran-books.json'),
      fetchJson('data/scripture/bereshit-1.json').catch(function() { return []; })
    ]).then(function(results) {
      loaded = true;
      render(container, {
        roots: results[0] || [],
        dictionaries: results[1] || {},
        researches: results[2] || [],
        heraldry: results[3] || [],
        qumranBooks: (results[4] && results[4].books) || [],
        scriptureVerses: results[5] || []
      });
    }).catch(function(err) {
      container.innerHTML = '<div class="lab-alert lab-alert-error">Ошибка загрузки статистики: ' + esc(err.message) + '</div>';
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
    var maxCount = top.reduce(function(m, d) { return Math.max(m, d.count); }, 1);
    var cx = 200, cy = 180, radius = 130;
    var lines = '', nodes = '';

    top.forEach(function(d, i) {
      var angle = (i / top.length) * Math.PI * 2 - Math.PI / 2;
      var x = cx + radius * Math.cos(angle);
      var y = cy + radius * Math.sin(angle);
      var r = 18 + (d.count / maxCount) * 22;
      lines += '<line class="dw-map-line" x1="' + cx + '" y1="' + cy + '" x2="' + x.toFixed(1) + '" y2="' + y.toFixed(1) + '"></line>';
      var label = d.title.length > 16 ? d.title.slice(0, 15) + '…' : d.title;
      nodes += '<g class="dw-map-node" data-dict-key="' + esc(d.key) + '" transform="translate(' + x.toFixed(1) + ',' + y.toFixed(1) + ')">' +
        '<circle r="' + r.toFixed(1) + '"></circle>' +
        '<text dy="4">' + esc(label) + '</text>' +
      '</g>';
    });

    var svg = '<svg viewBox="0 0 400 360" role="img" aria-label="Карта подмен">' +
      lines +
      '<g class="dw-map-center" transform="translate(' + cx + ',' + cy + ')"><circle r="34"></circle><text dy="5">ТаНаХ</text></g>' +
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
    var withData = books.filter(function(b) { return b.dataFile; });
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
        if (window.LabRenderer && LabRenderer.pageState && LabRenderer.pageState.dictionaries) {
          LabRenderer.pageState.dictionaries.key = key;
          LabRenderer.pageState.dictionaries.query = '';
        }
        LabRouter.navigate('dictionaries');
      };
      el.addEventListener('click', go);
      el.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); }
      });
    });
  }

  window.Dashboard = { init: init };
  return window.Dashboard;
})();
