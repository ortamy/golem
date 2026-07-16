/**
 * load-researches.js — fetches data/researches.json (built from content/researches/*.md
 * by tools/generators/generate-researches-json.py) and renders a searchable card grid
 * plus a per-item detail view on the #researches page.
 */
const LoadResearches = (function() {
  'use strict';

  var state = { query: '', category: 'all', activeId: '' };
  var items = [];

  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text == null ? '' : text;
    return d.innerHTML;
  }

  function render(container) {
    if (items.length) {
      renderPage(container);
      return;
    }
    container.innerHTML = '<div class="lab-spinner show"><div class="loader"></div><div class="spinner-text">Загрузка исследований...</div></div>';
    fetch('data/researches.json')
      .then(function(r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function(list) {
        items = list || [];
        renderPage(container);
      })
      .catch(function(err) {
        container.innerHTML = '<div class="lab-alert lab-alert-error">Не удалось загрузить исследования: ' + escapeHtml(err.message) + '</div>';
      });
  }

  function renderPage(container) {
    if (!items.length) {
      container.innerHTML = '<div class="lab-alert lab-alert-info">Исследований пока нет.</div>';
      return;
    }
    if (state.activeId) {
      renderDetail(container);
    } else {
      renderList(container);
    }
  }

  function getCategories() {
    var seen = {};
    items.forEach(function(item) { if (item.category) seen[item.category] = true; });
    return Object.keys(seen).sort();
  }

  function getFiltered() {
    var query = state.query.trim().toLowerCase();
    return items.filter(function(item) {
      if (state.category !== 'all' && item.category !== state.category) return false;
      if (!query) return true;
      var haystack = [item.title, item.summary, item.category].join(' ').toLowerCase();
      return haystack.indexOf(query) !== -1;
    });
  }

  function renderCards(list) {
    if (!list.length) return '<div class="lab-alert lab-alert-info">Ничего не найдено.</div>';
    return '<div class="tool-grid research-library-grid">' + list.map(function(item) {
      return '<a class="tool-card research-library-card" href="#" data-id="' + escapeHtml(item.id) + '">' +
        '<div class="tool-name">' + escapeHtml(item.title) + '</div>' +
        '<span class="tool-badge new">' + escapeHtml(item.category || '') + '</span>' +
        '<div class="tool-desc">' + escapeHtml(item.summary || '') + '</div>' +
      '</a>';
    }).join('') + '</div>';
  }

  function renderList(container) {
    var categories = getCategories();
    var options = categories.map(function(cat) {
      return '<option value="' + escapeHtml(cat) + '"' + (cat === state.category ? ' selected' : '') + '>' + escapeHtml(cat) + '</option>';
    }).join('');
    var filtered = getFiltered();

    container.innerHTML = '<div class="research-page-head">' +
      '<h1><img src="../assets/icons/32/scribe/scrolls.png" class="lab-icon" alt="">Разоблачения</h1>' +
      '<p class="subtitle">Разбор подмен смысла в языке, истории, экономике, спорте и других сферах — через восстановление ивритских корней ТаНаХа.</p>' +
      '</div>' +
      '<div class="research-controls">' +
      '<label class="research-search-label">Поиск<input id="researches-search" class="lab-input" type="search" placeholder="Название, тема или категория" value="' + escapeHtml(state.query) + '"></label>' +
      '<label>Категория<select id="researches-category" class="lab-input"><option value="all">Все категории</option>' + options + '</select></label>' +
      '</div>' +
      '<div class="research-meta"><strong>' + filtered.length + ' из ' + items.length + '</strong><span>Опубликованные исследования проекта «Голем»</span></div>' +
      '<div id="researches-results">' + renderCards(filtered) + '</div>';

    var search = document.getElementById('researches-search');
    var category = document.getElementById('researches-category');
    var results = document.getElementById('researches-results');
    var meta = container.querySelector('.research-meta strong');

    function update() {
      state.query = search.value || '';
      state.category = category.value;
      var list = getFiltered();
      if (meta) meta.textContent = list.length + ' из ' + items.length;
      results.innerHTML = renderCards(list);
      bindCardClicks(results, container);
    }

    if (search) search.addEventListener('input', update);
    if (category) category.addEventListener('change', update);
    bindCardClicks(results, container);
  }

  function bindCardClicks(scope, container) {
    scope.querySelectorAll('[data-id]').forEach(function(card) {
      card.addEventListener('click', function(e) {
        e.preventDefault();
        state.activeId = card.getAttribute('data-id');
        renderDetail(container);
      });
    });
  }

  function renderDetail(container) {
    var item = items.filter(function(i) { return i.id === state.activeId; })[0];
    if (!item) {
      state.activeId = '';
      renderList(container);
      return;
    }
    var body = typeof marked !== 'undefined' && marked.parse ? marked.parse(item.body || '') : escapeHtml(item.body || '');
    container.innerHTML = '<div class="research-detail-page">' +
      '<div class="research-detail-topbar"><a class="research-back-link" href="#" id="researches-back">← Назад к списку</a></div>' +
      '<header class="research-detail-header">' +
        '<h1>' + escapeHtml(item.title) + '</h1>' +
        '<div class="research-detail-tags"><span class="tool-badge">' + escapeHtml(item.category || '') + '</span></div>' +
        '<p class="research-detail-summary">' + escapeHtml(item.summary || '') + '</p>' +
      '</header>' +
      '<article class="research-detail-section"><div class="research-section-content">' + body + '</div></article>' +
    '</div>';

    var back = document.getElementById('researches-back');
    if (back) back.addEventListener('click', function(e) {
      e.preventDefault();
      state.activeId = '';
      renderList(container);
    });
  }

  window.LoadResearches = { render: render };
  return window.LoadResearches;
})();
