const RootDict = (function() {
  'use strict';
  const PER_PAGE = 20;
  let roots = [];
  let filtered = [];
  let currentPage = 1;
  let loading = false;
  let currentQuery = '';
  let links = [];
  let graphLoading = false;

  function navigate(segments) {
    if (window.LabRouter) window.LabRouter.navigate('root-dictionary', segments);
  }

  function applyRoute(parsed) {
    var segments = parsed && parsed.segments ? parsed.segments.slice(1) : [];
    if (segments[0] === 'graph') { renderGraph(decodeURIComponent(segments[1] || '')); return; }
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
        return fetch('data/roots/root-links.json').then(function(response) {
          if (!response.ok) throw new Error('root-links.json: HTTP ' + response.status);
          return response.json();
        }).catch(function() { return []; }).then(function(manualLinks) {
          links = window.RootGraph ? RootGraph.mergeLinks(roots, manualLinks) : [];
        });
      })
      .then(function() {
        loading = false;
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
      html += '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" onclick="RootsSearch.graph(\'' + encodeURIComponent(r.translit) + '\')">Связи</button></div>';
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

  function graph(id) { navigate(['graph', encodeURIComponent(id)]); }
  function renderGraph(id) {
    if (graphLoading || !roots.length) return;
    if (!window.RootGraph) return;
    var graphData = RootGraph.localGraph(roots, links, id);
    if (!graphData.root) { filter(''); return; }
    var list = document.getElementById('rd-list');
    var pagination = document.getElementById('rd-pagination');
    var empty = document.getElementById('rd-empty');
    if (!list) return;
    if (pagination) pagination.innerHTML = '';
    if (empty) empty.style.display = 'none';
    var center = graphData.nodes[0], width = 760, height = 360, cx = width / 2, cy = height / 2;
    var positions = {};
    graphData.nodes.forEach(function(node, index) {
      var angle = index === 0 ? 0 : (index - 1) * Math.PI * 2 / Math.max(1, graphData.nodes.length - 1);
      var radius = index === 0 ? 0 : Math.min(125, 55 + graphData.nodes.length * 10);
      positions[RootGraph.rootId(node)] = { x:cx + Math.cos(angle) * radius, y:cy + Math.sin(angle) * radius };
    });
    var edges = graphData.links.map(function(link) { var a=positions[link.from], b=positions[link.to]; return a && b ? '<line class="rd-graph-edge" data-confidence="' + escapeHtml(link.confidence) + '" x1="' + a.x + '" y1="' + a.y + '" x2="' + b.x + '" y2="' + b.y + '"></line>' : ''; }).join('');
    var nodes = graphData.nodes.map(function(node) { var p=positions[RootGraph.rootId(node)], selected=RootGraph.rootId(node) === id.toUpperCase(); return '<g class="rd-graph-node" tabindex="0" role="button" aria-label="' + escapeHtml(node.translit + ': ' + node.meaning) + '" onclick="RootsSearch.graph(\'' + encodeURIComponent(node.translit) + '\')" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();RootsSearch.graph(\'' + encodeURIComponent(node.translit) + '\')}"' + (selected ? ' aria-current="true"' : '') + '><circle cx="' + p.x + '" cy="' + p.y + '" r="' + (selected ? 42 : 34) + '"></circle><text x="' + p.x + '" y="' + p.y + '" lang="hbo">' + escapeHtml(RootGraph.paleo(node)) + '</text><text class="rd-graph-node-label" x="' + p.x + '" y="' + (p.y + 58) + '">' + escapeHtml(node.translit) + '</text></g>'; }).join('');
    var relationItems = graphData.links.map(function(link) { var other = link.from.toUpperCase() === id.toUpperCase() ? link.to : link.from; var node = RootGraph.getRootById(roots, other); return '<li><button type="button" class="lab-btn lab-btn-link" onclick="RootsSearch.graph(\'' + encodeURIComponent(other) + '\')">' + escapeHtml(node ? node.translit : other) + '</button> — ' + escapeHtml(link.label || link.type) + '; <span class="rd-graph-confidence">' + escapeHtml(link.confidence) + '</span>; ' + escapeHtml(link.source) + '. ' + escapeHtml(link.note || '') + '</li>'; }).join('');
    list.innerHTML = '<section class="rd-graph" aria-labelledby="rd-graph-title"><div class="rd-graph-toolbar"><button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" onclick="RootsSearch.back()">← К словарю</button><a class="lab-btn lab-btn-primary lab-btn-sm" href="#learn/paleo-trainer?root=' + encodeURIComponent(id) + '">Цепочка в палео-тренажёре</a><span class="rd-graph-note">Только палео-иврит / протоханаанейские глифы.</span></div><h2 id="rd-graph-title">Связи: ' + escapeHtml(center.translit) + '</h2><p>' + escapeHtml(center.meaning) + '</p><div class="rd-graph-canvas"><svg viewBox="0 0 760 360" role="img" aria-label="Локальная карта палео-связей">' + edges + nodes + '</svg></div><div class="rd-graph-legend" aria-label="Легенда"><span>сплошная — подтверждённая/вероятная</span><span class="is-dashed">пунктир — гипотеза/непроверено</span><span>Уверенность и источник также указаны текстом.</span></div><div class="rd-graph-list"><h3>Список отношений</h3><ul>' + (relationItems || '<li>Связи не найдены.</li>') + '</ul></div></section>';
  }

  window.RootsSearch = { filter: function(query) { navigate(query.trim() ? ['search', encodeURIComponent(query.trim())] : []); }, goTo: goTo, graph: graph, back: function() { navigate([]); } };
  window.RootDict = { init: init, applyRoute: applyRoute };
  return window.RootDict;
})();
