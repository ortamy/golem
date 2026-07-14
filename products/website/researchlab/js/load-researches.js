/**
 * load-researches.js — fetches data/researches.json and renders
 * the exported admin-panel researches on the #researches page.
 */
const LoadResearches = (function() {
  'use strict';

  function render(container) {
    fetch('data/researches.json')
      .then(function(r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function(list) {
        renderList(container, list);
      })
      .catch(function(err) {
        container.innerHTML = '<div class="lab-alert lab-alert-error">Не удалось загрузить исследования: ' + err.message + '</div>';
      });
  }

  function renderList(container, list) {
    if (!list || !list.length) {
      container.innerHTML = '<div class="lab-alert lab-alert-info">Исследований пока нет.</div>';
      return;
    }
    var html = '<div class="research-page-head"><h1>Разоблачения</h1>' +
      '<p class="subtitle">Опубликованные исследования проекта «Голем».</p></div>';
    list.slice().reverse().forEach(function(item) {
      html += renderItem(item);
    });
    container.innerHTML = html;
  }

  function renderItem(item) {
    var image = item.image ? '<img class="research-item-image" src="' + escapeHtml(item.image) + '" alt="">' : '';
    var body = typeof marked !== 'undefined' && marked.parse ? marked.parse(item.body || '') : escapeHtml(item.body || '');
    return '<article class="lab-card research-item">' +
      '<h2 class="research-item-title">' + escapeHtml(item.title || '') + '</h2>' +
      image +
      '<div class="research-item-body">' + body + '</div>' +
    '</article>';
  }

  window.LoadResearches = { render: render };
  return window.LoadResearches;
})();
