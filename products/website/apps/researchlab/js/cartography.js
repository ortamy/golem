/**
 * cartography.js — Модуль «Картография»
 *
 * Смысловая карта стран, городов и регионов: название на иврите/палео-иврите,
 * значение, ключевые события, связь с распространением алфавита.
 *
 * Маршрут: #cartography
 */

const Cartography = (function() {
  'use strict';

  const DATA_PATH = 'data/cartography.json';
  const TYPE_LABELS = { country: 'Страна', city: 'Город', region: 'Регион', empire: 'Империя' };
  const ERA_LABELS = { ancient: 'Древние', modern: 'Современные' };
  const REGION_LABELS = {
    Levant: 'Левант', Egypt: 'Египет', Mesopotamia: 'Месопотамия',
    Arabia: 'Аравия', Europe: 'Европа', Persia: 'Персия'
  };

  let entries = [];
  let entriesById = {};
  let dataPromise = null;
  let filters = { era: '', type: '', region: '' };

  function dataPath() {
    return new URL(DATA_PATH, document.baseURI).href;
  }

  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text == null ? '' : String(text);
    return d.innerHTML;
  }

  // ===== ИНИЦИАЛИЗАЦИЯ =====
  function init() {
    var container = document.getElementById('cartography');
    if (container) loadData(container);
  }

  // ===== ЗАГРУЗКА ДАННЫХ =====
  function loadData(target) {
    var container = target || document.getElementById('cartography');
    if (!container) return;

    if (entries.length) {
      renderPage(container);
      return Promise.resolve(entries);
    }

    if (dataPromise) return dataPromise;

    container.innerHTML = '<div class="lab-spinner show"><div class="loader"></div><div class="spinner-text">Загрузка картографии...</div></div>';

    dataPromise = fetch(dataPath())
      .then(function(response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      })
      .then(function(data) {
        var list = Array.isArray(data) ? data : (data && Array.isArray(data.entries) ? data.entries : null);
        if (!list) throw new Error('Неверный формат данных');
        entries = list.filter(function(e) { return e && e.id && e.name; });
        entriesById = {};
        entries.forEach(function(e) { entriesById[e.id] = e; });
        renderPage(container);
        return entries;
      })
      .catch(function(error) {
        dataPromise = null;
        container.innerHTML = '<div class="lab-alert lab-alert-error">Ошибка загрузки картографии: ' + escapeHtml(error.message) + '</div>';
        throw error;
      });

    dataPromise.catch(function() {});
    return dataPromise;
  }

  // ===== ФИЛЬТРАЦИЯ =====
  function getFiltered() {
    return entries.filter(function(e) {
      if (filters.era && e.era !== filters.era) return false;
      if (filters.type && e.type !== filters.type) return false;
      if (filters.region && e.region !== filters.region) return false;
      return true;
    });
  }

  function setFilter(kind, value) {
    filters[kind] = filters[kind] === value ? '' : value;
    var container = document.getElementById('cartography');
    if (container) renderPage(container);
  }

  // ===== СБОРКА НАБОРА ЗНАЧЕНИЙ ДЛЯ ФИЛЬТРОВ =====
  function buildFilterGroup(kind, labels) {
    var seen = {};
    entries.forEach(function(e) { if (e[kind]) seen[e[kind]] = true; });
    var values = Object.keys(seen);
    if (!values.length) return '';
    var buttons = values.map(function(v) {
      var active = filters[kind] === v ? ' active' : '';
      var label = (labels[v] || v);
      return '<button type="button" class="cartography-filter-btn' + active + '" data-filter-kind="' + kind + '" data-filter-value="' + escapeHtml(v) + '">' + escapeHtml(label) + '</button>';
    }).join('');
    return '<div class="cartography-filter-group" data-filter-group="' + kind + '">' + buttons + '</div>';
  }

  // ===== РЕНДЕРИНГ СТРАНИЦЫ =====
  function renderPage(container) {
    if (!entries.length) {
      container.innerHTML = '<div class="lab-alert lab-alert-info">Картография пока пуста. Записи добавляются.</div>';
      return;
    }

    var list = getFiltered();
    var filtersHtml = '<div class="cartography-filters">' +
      buildFilterGroup('era', ERA_LABELS) +
      buildFilterGroup('type', TYPE_LABELS) +
      buildFilterGroup('region', REGION_LABELS) +
      '<div class="cartography-stats">Найдено: ' + list.length + ' из ' + entries.length + '</div>' +
      '</div>';

    var cardsHtml = list.length
      ? '<div class="cartography-grid">' + list.map(renderCard).join('') + '</div>'
      : '<div class="lab-alert lab-alert-info">Ничего не найдено по выбранным фильтрам.</div>';

    container.innerHTML = '<div class="cartography-page">' +
      '<div class="cartography-head">' +
        '<h1><img src="../../assets/icons/32/ui/web.png" class="lab-icon" alt=""> Картография</h1>' +
        '<p class="subtitle">Смысловая карта: страны, города и регионы как пространственные конструкции.</p>' +
      '</div>' +
      filtersHtml +
      cardsHtml +
    '</div>';

    container.querySelectorAll('.cartography-filter-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        setFilter(this.getAttribute('data-filter-kind'), this.getAttribute('data-filter-value'));
      });
    });

    container.querySelectorAll('.cartography-card').forEach(function(card) {
      card.addEventListener('click', function() {
        var id = this.getAttribute('data-id');
        if (id) showDetail(id);
      });
    });
  }

  function renderCard(e, index) {
    return '<div class="cartography-card" data-id="' + escapeHtml(e.id) + '" tabindex="0" style="animation-delay:' + (index * 60) + 'ms">' +
      '<div class="cartography-card-type">' + escapeHtml(TYPE_LABELS[e.type] || e.type || '') + '</div>' +
      '<h2 class="cartography-card-title">' + escapeHtml(e.name) + '</h2>' +
      '<div class="cartography-card-hebrew" dir="rtl" lang="he">' + escapeHtml(e.hebrew || '') + '</div>' +
      '<div class="cartography-card-paleo" dir="rtl">' + escapeHtml(e.paleo || '') + '</div>' +
      '<div class="cartography-card-meaning">' + escapeHtml(e.meaning || '') + '</div>' +
      '<p class="cartography-card-summary">' + escapeHtml(e.summary || '') + '</p>' +
    '</div>';
  }

  // ===== ДЕТАЛЬНЫЙ ПРОСМОТР =====
  function showDetail(id) {
    var entry = entriesById[id];
    if (!entry) {
      if (window.LabToast) LabToast.show('Запись не найдена');
      return;
    }

    var html = buildDetailHTML(entry);
    if (window.LabModal) {
      LabModal.show(escapeHtml(entry.name), html, '<button class="lab-btn lab-btn-secondary lab-btn-sm" onclick="LabModal.close()">Закрыть</button>');
    }
  }

  function buildDetailHTML(entry) {
    var eventsHtml = (entry.key_events || []).map(function(ev, index) {
      return '<div class="cartography-event" role="listitem"><span class="cartography-event-number" aria-hidden="true">' + (index + 1) + '</span><span>' + escapeHtml(ev) + '</span></div>';
    }).join('');

    var relatedHtml = (entry.related || []).map(function(id) {
      var target = entriesById[id];
      var label = target ? target.name : id;
      return '<span class="cartography-related-tag" data-related-id="' + escapeHtml(id) + '">' + escapeHtml(label) + '</span>';
    }).join('');

    var html = '<div class="cartography-detail">' +
      '<div class="cartography-detail-names">' +
        '<div class="cartography-detail-name">' + escapeHtml(entry.name) + '</div>' +
        '<div class="cartography-detail-hebrew" dir="rtl">' + escapeHtml(entry.hebrew || '') + '</div>' +
        '<div class="cartography-detail-paleo" dir="rtl">' + escapeHtml(entry.paleo || '') + '</div>' +
      '</div>' +
      '<div class="cartography-detail-section cartography-callout cartography-meaning">' +
        '<h3>Значение</h3>' +
        '<p>' + escapeHtml(entry.meaning || '—') + '</p>' +
      '</div>' +
      '<div class="cartography-detail-section cartography-callout cartography-summary">' +
        '<h3>Описание</h3>' +
        '<p>' + escapeHtml(entry.summary || '—') + '</p>' +
      '</div>' +
      (eventsHtml ? '<div class="cartography-detail-section"><h3>Ключевые события</h3><div class="cartography-events" role="list">' + eventsHtml + '</div></div>' : '') +
      (relatedHtml ? '<div class="cartography-detail-section"><h3>Связанные</h3><div class="cartography-related">' + relatedHtml + '</div></div>' : '') +
    '</div>';

    return html;
  }

  document.addEventListener('click', function(e) {
    var tag = e.target.closest ? e.target.closest('.cartography-related-tag') : null;
    if (tag) {
      var id = tag.getAttribute('data-related-id');
      if (id && entriesById[id]) showDetail(id);
    }
  });

  // ===== ПУБЛИЧНЫЙ API =====
  return {
    init: init,
    loadData: loadData,
    showDetail: showDetail
  };
})();

window.Cartography = Cartography;
