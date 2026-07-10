/**
 * root-dictionary.js — Корневой словарь иврита v2
 * Bug #7 fix: улучшена логика подсветки
 * + экспорт данных для глобального поиска
 */

const RootDict = (function() {
  'use strict';

  let roots = [];
  let loaded = false;

  function init() {
    loadData();
    var el = document.getElementById('rd-search');
    if (el) el.focus();
  }

  function loadData() {
    fetch('data/roots.json')
      .then(function(r) { return r.json(); })
      .then(function(data) {
        roots = data;
        loaded = true;
        // Экспортируем для глобального поиска
        window._roots = roots;
        var spinner = document.getElementById('rd-spinner');
        if (spinner) spinner.classList.remove('show');
        var empty = document.getElementById('rd-empty');
        if (empty) empty.style.display = 'block';
        console.log('[RootDict] Загружено корней:', roots.length);
      })
      .catch(function(err) {
        console.error('[RootDict] Ошибка загрузки:', err);
        var spinner = document.getElementById('rd-spinner');
        if (spinner) spinner.classList.remove('show');
        var results = document.getElementById('rd-results');
        if (results) results.innerHTML = '<div class="lab-alert lab-alert-error">Ошибка загрузки словаря.</div>';
      });
  }

  function search(query) {
    if (!loaded) return;

    query = query.trim();
    const resultsEl = document.getElementById('rd-results');
    const emptyEl = document.getElementById('rd-empty');
    const countEl = document.getElementById('rd-count');

    if (!query) {
      if (resultsEl) resultsEl.innerHTML = '';
      if (emptyEl) emptyEl.style.display = 'block';
      if (countEl) countEl.style.display = 'none';
      return;
    }

    const q = query.toLowerCase();

    const matches = roots.filter(function(r) {
      return r.root.indexOf(q) !== -1 ||
             r.translit.toLowerCase().indexOf(q) !== -1 ||
             r.meaning.toLowerCase().indexOf(q) !== -1 ||
             r.examples.some(function(ex) { return ex.toLowerCase().indexOf(q) !== -1; });
    });

    if (matches.length === 0) {
      if (resultsEl) resultsEl.innerHTML = '<div class="lab-alert lab-alert-warn">Ничего не найдено. Попробуйте другой запрос.</div>';
      if (emptyEl) emptyEl.style.display = 'none';
      if (countEl) countEl.style.display = 'none';
      return;
    }

    if (emptyEl) emptyEl.style.display = 'none';
    if (countEl) {
      countEl.style.display = 'block';
      countEl.textContent = 'Найдено: ' + matches.length + ' корней';
    }

    matches.sort(function(a, b) {
      var aExact = a.root === q || a.translit.toLowerCase() === q ? 0 : 1;
      var bExact = b.root === q || b.translit.toLowerCase() === q ? 0 : 1;
      return aExact - bExact;
    });

    var html = '';
    matches.forEach(function(r) {
      html += '<div class="lab-card">';
      html += '  <div class="lab-card-header">';
      html += '    <span style="font-size:28px;font-family:\'Times New Roman\',serif;margin-right:8px;">' + r.root + '</span>';
      html += '    <span style="font-family:monospace;font-size:14px;color:var(--text-muted);">' + r.translit + '</span>';
      html += '  </div>';
      html += '  <div class="lab-card-body">';
      html += '    <p style="margin-bottom:8px;"><strong>Значение:</strong> ' + r.meaning + '</p>';
      if (r.examples && r.examples.length > 0) {
        html += '    <p><strong>Примеры:</strong></p><ul style="margin:4px 0 0 20px;">';
        r.examples.forEach(function(ex) {
          var highlighted = ex;
          if (q.length >= 2) {
            // Ищем совпадение в оригинале (иврит) или транслитерации
            var idx = ex.indexOf(q);
            if (idx === -1) idx = ex.toLowerCase().indexOf(q);
            if (idx !== -1) {
              highlighted = ex.substring(0, idx) + '<span class="highlight">' + 
                ex.substring(idx, idx + q.length) + '</span>' + ex.substring(idx + q.length);
            }
          }
          html += '<li style="font-size:16px;line-height:1.7;">' + highlighted + '</li>';
        });
        html += '</ul>';
      }
      html += '  </div>';
      html += '</div>';
    });

    if (resultsEl) resultsEl.innerHTML = html;
  }

  return {
    init: init,
    search: search
  };
})();