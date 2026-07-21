/**
 * load-researches.js — каталог и детальный просмотр «Разоблачений» (#researches).
 * Данные: data/exposures/index.json (единая схема дела, см. tools/migrate-exposures.py).
 * Рендер карточек, досье и превью — через ExposureCase (js/modules/exposure-case.js),
 * так что каталог, страница дела и форма создания используют один и тот же шаблон.
 */
const LoadResearches = (function() {
  'use strict';

  var state = { query: '', category: 'all', confidence: 'all', activeSlug: '' };
  var items = [];

  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text == null ? '' : text;
    return d.innerHTML;
  }

  function render(container, parsed) {
    state.activeSlug = (parsed && parsed.segments && parsed.segments[1] === 'case') ? decodeURIComponent(parsed.segments[2] || '') : '';
    if (parsed && parsed.params) {
      if (parsed.params.q != null) state.query = parsed.params.q;
      if (parsed.params.category) state.category = parsed.params.category;
      if (parsed.params.confidence) state.confidence = parsed.params.confidence;
    }

    if (items.length) {
      renderPage(container);
      return;
    }
    container.innerHTML = '<div class="lab-spinner show"><div class="loader"></div><div class="spinner-text">Загрузка разоблачений...</div></div>';
    fetch('data/exposures/index.json')
      .then(function(r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function(list) {
        items = list || [];
        renderPage(container);
      })
      .catch(function(err) {
        container.innerHTML = '<div class="lab-alert lab-alert-error">Не удалось загрузить разоблачения: ' + escapeHtml(err.message) + '</div>';
      });
  }

  function renderPage(container) {
    if (!items.length) {
      container.innerHTML = '<div class="lab-alert lab-alert-info">Разоблачений пока нет.</div>';
      return;
    }
    if (state.activeSlug) {
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
      if (state.confidence !== 'all' && item.confidence !== state.confidence) return false;
      if (!query) return true;
      var sectionText = ((item.sections && item.sections.content) || []).map(function(s) {
        return [s.heading, s.body].join(' ');
      }).join(' ');
      var haystack = [item.title, item.summary, item.category, (item.tags || []).join(' '), sectionText].join(' ').toLowerCase();
      return haystack.indexOf(query) !== -1;
    });
  }

  // history.replaceState вместо LabRouter.navigate — иначе hashchange запускает
  // полный ре-рендер контейнера на каждое нажатие клавиши и сбивает фокус поиска.
  function updateHash() {
    var params = [];
    if (state.query) params.push('q=' + encodeURIComponent(state.query));
    if (state.category !== 'all') params.push('category=' + encodeURIComponent(state.category));
    if (state.confidence !== 'all') params.push('confidence=' + encodeURIComponent(state.confidence));
    var hash = '#researches' + (params.length ? '?' + params.join('&') : '');
    history.replaceState(null, '', hash);
  }

  function renderCards(list) {
    if (!list.length) return '<div class="lab-alert lab-alert-info">Ничего не найдено.</div>';
    return '<div class="exposure-grid">' + list.map(function(item) { return ExposureCase.renderCard(item); }).join('') + '</div>';
  }

  function renderConfidenceChips() {
    var order = ['all', 'verified', 'needs-review', 'hypothesis', 'disputed'];
    var labels = { all: 'Все' };
    order.slice(1).forEach(function(key) { labels[key] = ExposureCase.confidenceMeta(key).label; });
    return '<div class="exposure-chips" id="researches-confidence-chips">' + order.map(function(key) {
      return '<button type="button" class="exposure-chip' + (state.confidence === key ? ' active' : '') + '" data-confidence="' + key + '">' + escapeHtml(labels[key]) + '</button>';
    }).join('') + '</div>';
  }

  function renderList(container) {
    var categories = getCategories();
    var options = categories.map(function(cat) {
      return '<option value="' + escapeHtml(cat) + '"' + (cat === state.category ? ' selected' : '') + '>' + escapeHtml(cat) + '</option>';
    }).join('');
    var filtered = getFiltered();

    container.innerHTML = '<div class="exposure-hero">' +
        '<div class="exposure-hero-text">' +
          '<h1><img src="../../assets/icons/32/scribe/scrolls.png" class="lab-icon" alt="">Разоблачения</h1>' +
          '<p class="subtitle">Разбор подмен смысла в языке, истории, экономике, спорте и других сферах — через восстановление ивритских корней ТаНаХа.</p>' +
        '</div>' +
        '<button type="button" class="lab-btn lab-btn-primary exposure-new-btn" id="researches-new-btn">+ Новое дело</button>' +
      '</div>' +
      '<div class="research-controls exposure-filters">' +
      '<label class="research-search-label">Поиск<input id="researches-search" class="lab-input" type="search" placeholder="Название, тема, тег или категория" value="' + escapeHtml(state.query) + '"></label>' +
      '<label>Категория<select id="researches-category" class="lab-input"><option value="all">Все категории</option>' + options + '</select></label>' +
      '</div>' +
      renderConfidenceChips() +
      '<div class="research-meta"><strong>' + filtered.length + ' из ' + items.length + '</strong><span>Опубликованные разоблачения проекта «Голем»</span></div>' +
      '<div id="researches-results">' + renderCards(filtered) + '</div>';

    bindListEvents(container);
  }

  function bindListEvents(container) {
    var search = document.getElementById('researches-search');
    var category = document.getElementById('researches-category');
    var results = document.getElementById('researches-results');
    var meta = container.querySelector('.research-meta strong');
    var newBtn = document.getElementById('researches-new-btn');
    var chipsWrap = document.getElementById('researches-confidence-chips');

    function update() {
      state.query = search.value || '';
      state.category = category.value;
      var list = getFiltered();
      if (meta) meta.textContent = list.length + ' из ' + items.length;
      results.innerHTML = renderCards(list);
      updateHash();
    }

    if (search) search.addEventListener('input', update);
    if (category) category.addEventListener('change', update);
    if (newBtn) newBtn.addEventListener('click', function() { LabRouter.navigate('exposure-editor'); });
    if (chipsWrap) chipsWrap.addEventListener('click', function(e) {
      var btn = e.target.closest('[data-confidence]');
      if (!btn) return;
      state.confidence = btn.getAttribute('data-confidence');
      chipsWrap.querySelectorAll('.exposure-chip').forEach(function(c) { c.classList.remove('active'); });
      btn.classList.add('active');
      update();
    });
  }

  function renderDetail(container) {
    var item = items.filter(function(i) { return i.slug === state.activeSlug; })[0];
    if (!item) {
      container.innerHTML = '<div class="lab-alert lab-alert-error">Дело «' + escapeHtml(state.activeSlug) + '» не найдено.</div>' +
        '<a class="research-back-link" href="#researches">← Назад к архиву</a>';
      return;
    }
    history.replaceState(null, '', '#researches/case/' + encodeURIComponent(item.slug));
    container.innerHTML = ExposureCase.renderCase(item);
    ExposureCase.bindCase(container, item);

    var back = container.querySelector('[data-exposure-back]');
    if (back) back.addEventListener('click', function(e) {
      e.preventDefault();
      state.activeSlug = '';
      history.replaceState(null, '', '#researches');
      renderList(container);
    });
  }

  window.LoadResearches = { render: render };
  return window.LoadResearches;
})();
