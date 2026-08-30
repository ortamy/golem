const RootDict = (function() {
  'use strict';
  const PER_PAGE = 20;
  let roots = [];
  let filtered = [];
  let currentPage = 1;
  let loading = false;
  let currentQuery = '';

  function navigate(segments) {
    if (window.LabRouter) window.LabRouter.navigate('root-dictionary', segments);
  }

  function applyRoute(parsed) {
    var segments = parsed && parsed.segments ? parsed.segments.slice(1) : [];
    currentQuery = segments[0] === 'search' ? decodeURIComponent(segments[1] || '') : '';
    currentPage = segments[0] === 'search' && segments[2] === 'page'
      ? Math.max(1, parseInt(segments[3], 10) || 1)
      : segments[0] === 'page' ? Math.max(1, parseInt(segments[1], 10) || 1) : 1;
    if (roots.length) {
      var searchInput = document.getElementById('rd-search');
      if (searchInput) searchInput.value = currentQuery;
      filter(currentQuery, true);
    }
  }

  function init() {
    if (roots.length) {
      var readySpinner = document.getElementById('rd-spinner');
      if (readySpinner) readySpinner.classList.remove('show');
      applyRoute(window.LabRouter && window.LabRouter.parseHash ? window.LabRouter.parseHash() : null);
      return;
    }
    if (loading) return;
    loading = true;
    fetch('data/roots/roots.json')
      .then(function(response) {
        if (!response.ok) {
          throw new Error('roots.json: HTTP ' + response.status);
        }
        return response.json();
      })
      .then(data => {
        loading = false;
        roots = Array.isArray(data) ? data : [];
        window._roots = data;
        var totalEl = document.getElementById('rd-total');
        var spinnerEl = document.getElementById('rd-spinner');
        if (totalEl) totalEl.textContent = roots.length;
        var foundEl = document.getElementById('rd-found');
        if (foundEl) foundEl.textContent = roots.length;
        if (spinnerEl) spinnerEl.classList.remove('show');
        applyRoute(window.LabRouter && window.LabRouter.parseHash ? window.LabRouter.parseHash() : null);
      })
      .catch(err => {
        loading = false;
        console.error('[RootDict] Не удалось загрузить словарь:', err);
        var spinnerEl = document.getElementById('rd-spinner');
        if (spinnerEl) spinnerEl.innerHTML = '<div class="lab-alert lab-alert-error">Ошибка загрузки словаря. Проверьте, что ResearchLab открыт через HTTP-сервер.</div>';
      });
  }

  function filter(query, keepPage) {
    query = query.trim().toLowerCase();
    currentQuery = query;
    filtered = query
      ? roots.filter(r => r.root.indexOf(query) !== -1 || r.translit.toLowerCase().indexOf(query) !== -1 || r.meaning.toLowerCase().indexOf(query) !== -1 || (r.image && r.image.toLowerCase().indexOf(query) !== -1) || (r.substitutions && r.substitutions.some(function(s) { return s.toLowerCase().indexOf(query) !== -1; })))
      : roots.slice();
    if (!keepPage) currentPage = 1;
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
    if (currentPage > totalPages) currentPage = totalPages;
    var start = (currentPage - 1) * PER_PAGE;
    var pageItems = filtered.slice(start, start + PER_PAGE);
    var html = '';
    pageItems.forEach(function(r) {
      html += '<div class="rd-card"><div class="rd-card-header">';

      // Paleo symbols рядом с корнем
      if (r.paleo && r.paleo.length > 0) {
        html += '<span class="root-paleo">';
        r.paleo.forEach(function(p, idx) {
          html += '<span class="rd-paleo-char" title="' + (r.paleoMeanings && r.paleoMeanings[idx] ? r.paleoMeanings[idx] : '') + '">' + p + '</span>';
        });
        html += '</span>';
      }

      html += '<span class="root-heb">' + r.root + '</span>';
      html += '<span class="root-translit">' + r.translit + '</span>';
      html += '</div><div class="meaning"><strong>Значение:</strong> ' + r.meaning + '</div>';

      // Image — образное значение
      if (r.image) {
        html += '<div class="rd-image text-small text-muted mt-8"><strong>Образ:</strong> ' + r.image + '</div>';
      }

      // Substitutions — подмены
      if (r.substitutions && r.substitutions.length > 0) {
        html += '<div class="rd-subs mt-8">';
        html += '<span class="rd-subs-label">Подмены: </span>';
        r.substitutions.forEach(function(s, idx) {
          html += '<span class="rd-sub-item">' + escapeHtml(s) + '</span>';
          if (idx < r.substitutions.length - 1) html += ', ';
        });
        html += '</div>';
      }

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
    navigate(currentQuery ? ['search', encodeURIComponent(currentQuery), 'page', String(page)] : ['page', String(page)]);
    var list = document.getElementById('rd-list');
    if (list) list.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
  }

  window.RootsSearch = { filter: function(query) { navigate(query.trim() ? ['search', encodeURIComponent(query.trim())] : []); }, goTo: goTo };
  window.RootDict = { init: init, applyRoute: applyRoute };
  return window.RootDict;
})();
