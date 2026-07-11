const RootDict = (function() {
  'use strict';
  const PER_PAGE = 20;
  let roots = [];
  let filtered = [];
  let currentPage = 1;

  function init() {
    fetch('data/roots.json')
      .then(r => r.json())
      .then(data => {
        roots = data;
        window._roots = data;
        filtered = roots.slice();
        var totalEl = document.getElementById('rd-total');
        var spinnerEl = document.getElementById('rd-spinner');
        if (totalEl) totalEl.textContent = roots.length;
        if (spinnerEl) spinnerEl.classList.remove('show');
        render();
      })
      .catch(err => {
        console.error(err);
        var spinnerEl = document.getElementById('rd-spinner');
        if (spinnerEl) spinnerEl.innerHTML = '<div class="lab-alert lab-alert-error">Ошибка загрузки словаря.</div>';
      });
  }

  function filter(query) {
    query = query.trim().toLowerCase();
    filtered = query
      ? roots.filter(r => r.root.indexOf(query) !== -1 || r.translit.toLowerCase().indexOf(query) !== -1 || r.meaning.toLowerCase().indexOf(query) !== -1)
      : roots.slice();
    currentPage = 1;
    var foundEl = document.getElementById('rd-found');
    if (foundEl) foundEl.textContent = filtered.length;
    render();
  }

  function render() {
    var list = document.getElementById('rd-list');
    var empty = document.getElementById('rd-empty');
    var pagination = document.getElementById('rd-pagination');
    if (!list) return;
    if (filtered.length === 0) {
      list.innerHTML = '';
      if (pagination) pagination.innerHTML = '';
      if (empty) empty.style.display = 'block';
      return;
    }
    if (empty) empty.style.display = 'none';
    var totalPages = Math.ceil(filtered.length / PER_PAGE);
    var start = (currentPage - 1) * PER_PAGE;
    var pageItems = filtered.slice(start, start + PER_PAGE);
    var html = '';
    pageItems.forEach(function(r) {
      html += '<div class="rd-card"><div class="rd-card-header">';
      html += '<span class="root-heb">' + r.root + '</span>';
      html += '<span class="root-translit">' + r.translit + '</span>';
      html += '</div><div class="meaning"><strong>Значение:</strong> ' + r.meaning + '</div>';
      if (r.examples && r.examples.length > 0) {
        html += '<ul class="examples">';
        r.examples.forEach(function(ex) { html += '<li>' + ex + '</li>'; });
        html += '</ul>';
      }
      html += '</div>';
    });
    list.innerHTML = html;
    if (pagination) {
      var pHtml = '';
      if (totalPages > 1) {
        pHtml += '<button class="rd-page-btn" onclick="RootsSearch.goTo(' + (currentPage - 1) + ')" ' + (currentPage <= 1 ? 'disabled' : '') + '>←</button>';
        for (var i = 1; i <= totalPages; i++) {
          pHtml += '<button class="rd-page-btn' + (i === currentPage ? ' active' : '') + '" onclick="RootsSearch.goTo(' + i + ')">' + i + '</button>';
        }
        pHtml += '<button class="rd-page-btn" onclick="RootsSearch.goTo(' + (currentPage + 1) + ')" ' + (currentPage >= totalPages ? 'disabled' : '') + '>→</button>';
      }
      pagination.innerHTML = pHtml;
    }
  }

  function goTo(page) {
    var totalPages = Math.ceil(filtered.length / PER_PAGE);
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    render();
    var list = document.getElementById('rd-list');
    if (list) list.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  window.RootsSearch = { filter: filter, goTo: goTo };
  return { init: init };
})();