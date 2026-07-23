/**
 * load-researches.js — каталог и детальный просмотр «Разоблачений» (#researches).
 * Данные: data/exposures/index.json (единая схема дела, см. tools/migrate-exposures.py).
 * Рендер карточек, досье и превью — через ExposureCase (js/modules/exposure-case.js),
 * так что каталог, страница дела и форма создания используют один и тот же шаблон.
 */
const LoadResearches = (function() {
  'use strict';

  var STORAGE_KEY = 'golem_exposure_drafts';
  var state = { query: '', category: 'all', confidence: 'all', activeSlug: '' };
  var items = [];

  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text == null ? '' : text;
    return d.innerHTML;
  }

  function generateId() {
    return 'exp_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
  }

  function readDrafts() {
    try {
      var drafts = JSON.parse(localStorage.getItem(STORAGE_KEY));
      return Array.isArray(drafts) ? drafts : [];
    } catch (e) {
      return [];
    }
  }

  function makeSlug(title, id) {
    var slug = String(title || '').toLowerCase()
      .replace(/[^\w\u0400-\u04ff]+/g, '-')
      .replace(/^-+|-+$/g, '');
    return slug || id;
  }

  function uniqueSlug(base, used) {
    var slug = base;
    var suffix = 2;
    while (used[slug]) {
      slug = base + '-draft-' + suffix;
      suffix += 1;
    }
    used[slug] = true;
    return slug;
  }

  // Приводит черновик редактора к схеме карточки каталога.
  function normalizeDraft(draft, slug) {
    var paleoImages = draft.paleoImages || draft.roots || '';
    var lossMap = draft.lossMap || '';
    var livingImage = draft.livingImage || '';
    var conclusion = draft.conclusion || draft.description || '';
    var content = [
      { heading: 'Палео-образы', body: paleoImages },
      { heading: 'Карта утрат', body: lossMap },
      { heading: 'Живой образ', body: livingImage },
      { heading: 'Вывод', body: conclusion }
    ].filter(function(section) { return section.body; });

    return {
      id: draft.id,
      slug: slug || draft.slug || makeSlug(draft.title, draft.id),
      title: draft.title || 'Без названия',
      summary: conclusion || livingImage || paleoImages,
      category: draft.category || 'other',
      tags: draft.hebrewKeyword ? [draft.hebrewKeyword] : [],
      sources: [],
      confidence: 'needs-review',
      status: 'draft',
      updatedAt: draft.updatedAt || draft.createdAt || '',
      createdAt: draft.createdAt || '',
      hebrewKeyword: draft.hebrewKeyword || '',
      paleoImages: paleoImages,
      lossMap: lossMap,
      livingImage: livingImage,
      conclusion: conclusion,
      sections: {
        thesis: conclusion || livingImage,
        original: { hebrew: draft.hebrewKeyword || '', paleo: paleoImages ? [paleoImages] : [] },
        shift: lossMap,
        content: content
      }
    };
  }

  function mergeDrafts(published) {
    var merged = (published || []).slice();
    var used = {};
    merged.forEach(function(item) { if (item.slug) used[item.slug] = true; });
    readDrafts().forEach(function(draft) {
      if (!draft || !draft.id) return;
      var base = draft.slug || makeSlug(draft.title, draft.id);
      var item = normalizeDraft(draft, uniqueSlug(base, used));
      var existing = merged.filter(function(entry) { return entry.id === item.id; })[0];
      if (existing) {
        merged[merged.indexOf(existing)] = item;
      } else {
        merged.push(item);
      }
    });
    return merged;
  }

  function openNewExposureModal() {
    if (typeof LabModal === 'undefined') {
      LabRouter.navigate('exposure-editor');
      return;
    }

    var body = '<form id="researches-quick-form" novalidate>' +
      '<label>Название дела<input id="quick-exposure-title" class="lab-input" type="text" required></label>' +
      '<label>Ключевое слово на иврите<input id="quick-exposure-hebrew" class="lab-input" type="text"></label>' +
      '<label>Палео-образы<textarea id="quick-exposure-paleo" class="lab-textarea" rows="3"></textarea></label>' +
      '<label>Карта утрат<textarea id="quick-exposure-loss" class="lab-textarea" rows="3"></textarea></label>' +
      '<label>Живой образ<textarea id="quick-exposure-living" class="lab-textarea" rows="3"></textarea></label>' +
      '<label>Вывод<textarea id="quick-exposure-conclusion" class="lab-textarea" rows="3"></textarea></label>' +
      '<div id="quick-exposure-error" class="lab-alert lab-alert-error" hidden></div>' +
      '</form>';
    var footer = '<button type="button" class="lab-btn lab-btn-primary" id="quick-exposure-save">Сохранить как черновик</button>' +
      '<button type="button" class="lab-btn lab-btn-secondary" id="quick-exposure-close">Закрыть</button>';

    LabModal.show('Новое дело', body, footer);

    var form = document.getElementById('researches-quick-form');
    var saveBtn = document.getElementById('quick-exposure-save');
    var closeBtn = document.getElementById('quick-exposure-close');
    if (closeBtn) closeBtn.addEventListener('click', function() { LabModal.close(); });
    if (form) form.addEventListener('submit', function(e) { e.preventDefault(); });
    if (saveBtn) saveBtn.addEventListener('click', function() {
      var title = document.getElementById('quick-exposure-title').value.trim();
      var error = document.getElementById('quick-exposure-error');
      if (!title) {
        error.textContent = 'Укажите название дела.';
        error.hidden = false;
        document.getElementById('quick-exposure-title').focus();
        return;
      }

      var id = generateId();
      var now = new Date().toISOString();
      var draft = {
        id: id,
        slug: makeSlug(title, id),
        title: title,
        category: 'other',
        description: document.getElementById('quick-exposure-conclusion').value.trim(),
        sections: [],
        roots: document.getElementById('quick-exposure-paleo').value.trim(),
        sources: '',
        confidence: 'medium',
        status: 'draft',
        updatedAt: now,
        createdAt: now,
        hebrewKeyword: document.getElementById('quick-exposure-hebrew').value.trim(),
        paleoImages: document.getElementById('quick-exposure-paleo').value.trim(),
        lossMap: document.getElementById('quick-exposure-loss').value.trim(),
        livingImage: document.getElementById('quick-exposure-living').value.trim(),
        conclusion: document.getElementById('quick-exposure-conclusion').value.trim()
      };
      draft.sections = [
        { title: 'Ключевое слово на иврите', content: draft.hebrewKeyword },
        { title: 'Палео-образы', content: draft.paleoImages },
        { title: 'Карта утрат', content: draft.lossMap },
        { title: 'Живой образ', content: draft.livingImage },
        { title: 'Вывод', content: draft.conclusion }
      ].filter(function(section) { return section.content; });

      var drafts = readDrafts();
      drafts.push(draft);
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
      } catch (e) {
        error.textContent = 'Не удалось сохранить черновик в localStorage.';
        error.hidden = false;
        return;
      }

      items = items.filter(function(item) { return item.id !== draft.id; });
      var used = {};
      items.forEach(function(item) { if (item.slug) used[item.slug] = true; });
      items.push(normalizeDraft(draft, uniqueSlug(draft.slug, used)));
      LabModal.close();
      state.activeSlug = '';
      renderPage(document.getElementById('researches'));
    });
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
        items = mergeDrafts(list || []);
        renderPage(container);
      })
      .catch(function(err) {
        container.innerHTML = '<div class="lab-alert lab-alert-error">Не удалось загрузить разоблачения: ' + escapeHtml(err.message) + '</div>';
      });
  }

  function renderPage(container) {
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
      var roots = Array.isArray(item.roots) ? item.roots.join(' ') : (item.roots || '');
      var haystack = [item.title, item.summary, item.category, item.hebrewKeyword, roots,
        (item.tags || []).join(' '), sectionText].join(' ').toLowerCase();
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

  function itemIndex() {
    var index = {};
    items.forEach(function(item) { if (item.slug) index[item.slug] = item; });
    return index;
  }

  // Нижняя панель даёт быстрый переход к соседним делам и не меняет шаблон карточки.
  function renderRelatedDock(source, current) {
    var index = itemIndex();
    var ids = current && Array.isArray(current.related) ? current.related.slice() : [];
    var candidates = source || items;
    candidates.forEach(function(item) {
      if (item !== current && item.slug && ids.indexOf(item.slug) === -1 && ids.length < 4) ids.push(item.slug);
    });
    ids = ids.filter(function(id, position) { return index[id] && ids.indexOf(id) === position && (!current || id !== current.slug); }).slice(0, 4);
    if (!ids.length) return '';
    return '<aside class="exposure-related-dock" aria-label="Связанные разоблачения">' +
      '<div class="exposure-related-dock-inner">' +
        '<div class="exposure-related-dock-links">' + ids.map(function(id) {
          return '<a href="#researches/case/' + encodeURIComponent(id) + '">' + escapeHtml(index[id].title || id) + '</a>';
        }).join('') + '</div>' +
      '</div>' +
    '</aside>';
  }

  function setDockState(container) {
    var host = container.closest('.lab-content') || container;
    host.classList.toggle('exposure-has-related-dock', !!container.querySelector('.exposure-related-dock'));
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
      '<div id="researches-results">' + renderCards(filtered) + '</div>' +
      '<div id="researches-related-dock-slot">' + renderRelatedDock(filtered) + '</div>';

    setDockState(container);
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
      var dockSlot = container.querySelector('#researches-related-dock-slot');
      if (dockSlot) dockSlot.innerHTML = renderRelatedDock(list);
      setDockState(container);
      updateHash();
    }

    if (search) search.addEventListener('input', update);
    if (category) category.addEventListener('change', update);
    if (newBtn) newBtn.addEventListener('click', openNewExposureModal);
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
      setDockState(container);
      return;
    }
    history.replaceState(null, '', '#researches/case/' + encodeURIComponent(item.slug));
    container.innerHTML = ExposureCase.renderCase(item, { relatedItems: itemIndex() }) + renderRelatedDock(items, item);
    setDockState(container);
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
