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

  // Путь считается от страницы лаборатории, а не от каталога js/.
  const DATA_PATH = 'data/cartography.json';
  const HERALDRY_DATA_PATH = 'data/heraldry/heraldry.json';
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

  function heraldryDataPath() {
    return new URL(HERALDRY_DATA_PATH, document.baseURI).href;
  }

  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text == null ? '' : String(text);
    return d.innerHTML;
  }

  // ===== ИНИЦИАЛИЗАЦИЯ =====
  function init(el) {
    console.log('[Cartography] init вызван, container:', el);
    var container = el || document.getElementById('cartography');
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

    console.log('[Cartography] Загружаем путь:', dataPath());
    dataPromise = Promise.all([
      fetch(dataPath()).then(function(response) {
        console.log('[Cartography] Ответ fetch:', response.status, response.url, response.ok);
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      }),
      fetch(heraldryDataPath()).then(function(response) {
        if (!response.ok) throw new Error('HTTP ' + response.status + ' for heraldry');
        return response.json();
      })
    ])
      .then(function(results) {
        var data = results[0];
        var modernList = Array.isArray(results[1]) ? results[1] : [];
        var list = Array.isArray(data) ? data : (data && Array.isArray(data.entries) ? data.entries : null);
        if (!list) throw new Error('Неверный формат данных');
        var ancientEntries = list.filter(function(e) { return e && e.id && e.name; }).map(function(e) {
          e.era = e.era || 'ancient';
          return e;
        });
        var modernEntries = modernList.filter(function(e) { return e && e.id && e.name; }).map(function(e) {
          e.era = 'modern';
          e.type = e.type || 'country';
          e.summary = e.summary || e.card_description || e.description || '';
          e.meaning = e.meaning || e.card_description || '';
          return e;
        });
        entries = ancientEntries.concat(modernEntries);
        entriesById = {};
        entries.forEach(function(e) { entriesById[e.id] = e; });
        renderPage(container);
        return entries;
      })
      .catch(function(error) {
        console.error('[Cartography] Ошибка загрузки:', error);
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

  // Контекстная карта: статичная SVG-схема, не участвующая в навигации.
  function renderWorldMap() {
    return '<section class="cartography-world" aria-labelledby="cartography-world-title">' +
      '<div class="cartography-world-head"><div><span class="cartography-world-kicker">RESEARCH LAB · КОНТЕКСТ</span><h2 id="cartography-world-title">Карта мира</h2><p>Материки и основные пространственные узлы перед историческим слоем.</p></div><span class="cartography-world-mark" aria-hidden="true">𐤌</span></div>' +
      '<svg class="cartography-world-svg" viewBox="0 0 1200 560" role="img" aria-label="Схематичная карта мира с материками и основными странами" focusable="false">' +
        '<rect class="world-sea" x="0" y="0" width="1200" height="560" rx="8"></rect>' +
        '<g class="world-graticule" aria-hidden="true"><path d="M40 140H1160M20 280H1180M40 420H1160M200 30V530M400 20V540M600 12V548M800 20V540M1000 30V530"></path></g>' +
        '<g class="world-land">' +
          '<path d="M50 142l18-29 31-8 20-26 43-8 35 13 42-6 35 18 33 7 37 26-8 18-27 8-13 21-32 4-18 27-28 8-24-19-31 5-30-16-37 7-28-22z"></path>' +
          '<path d="M232 211l24-15 31 8 26 27-9 31-20 22-9 35-19 26-8 49-19 38-14-28 4-39-13-32 8-32-11-35 20-24z"></path>' +
          '<path d="M380 113l22-30 36-18 41 7 23 18 38-5 30 14 38-4 34 15 52 4 29 18 39 5 28 27-18 20-40-4-24 16-42-5-29 20-44-8-36 17-40-8-30 13-31-16-29 6-26-22 17-23z"></path>' +
          '<path d="M531 207l28-2 29 17 24 34-13 35-25 17-14 37-24 28-9 35-22 30-22-11 7-37 17-28-7-36 17-28-7-28z"></path>' +
          '<path d="M702 111l25-25 31-9 28 13 20 22 29 11 10 25-22 17-32-7-25 15-26-18-32 5-17-19z"></path>' +
          '<path d="M753 191l31-18 40 4 30 13 45-3 34 18 43 19 30 28-19 27-32 7-15 26-36 8-20 31-31 22-31-14-17-32-29-8-12-30-29-9 8-27-24-17 23-23z"></path>' +
          '<path d="M867 394l25-13 30 13 20 26-18 37-27 10-24-17-19-29z"></path>' +
          '<path d="M1016 232l24-10 30 12 16 22-17 24-31 1-24-15-19-19z"></path>' +
        '</g>' +
        '<g class="world-borders" aria-hidden="true">' +
          '<path d="M111 100l-9 80M153 91l-6 91M194 105l-10 80M236 119l-13 69M92 139l146 8M79 169l148 7M171 201l65 3M259 218l-17 60M277 230l-10 82M286 260l-31 12M265 319l-20 67M412 82l8 116M449 75l2 118M487 77l-6 122M526 91l-5 113M565 93l-10 116M606 101l-7 116M647 111l-13 112M687 128l-22 91M420 124h226M401 155l242 9M442 186l175 4M535 205l-6 112M557 213l-8 108M586 230l-12 93M747 88l-8 100M781 91l-11 102M811 108l-9 93M734 129l89 12M721 160l113 10M805 196l-10 81M842 198l-14 95M881 211l-12 97M916 224l-10 88M951 240l-18 78M790 238l168 24M801 273l130 22M852 315l-24 42M886 319l-20 39M909 330l-15 38M899 395l-18 25M928 406l-14 28M1036 222l-4 62M1064 226l-7 61"></path>' +
          '<path class="world-river" d="M575 242c-18 22-9 37 7 51m-25-8c-17 18-12 32-3 48M170 132c-17 17-22 31-8 44"></path>' +
        '</g>' +
        '<g class="world-labels" aria-hidden="true"><text x="111" y="128">Северная Америка</text><text x="241" y="350">Южная Америка</text><text x="463" y="104">Европа</text><text x="551" y="291">Африка</text><text x="826" y="151">Азия</text><text x="861" y="376">Австралия</text><text x="126" y="151">США</text><text x="171" y="126">Канада</text><text x="522" y="117">Россия</text><text x="800" y="231">Китай</text><text x="284" y="300">Бразилия</text><text x="892" y="426">Австралия</text><text x="1042" y="215">Япония</text></g>' +
      '</svg>' +
    '</section>';
  }

  // ===== РЕНДЕРИНГ СТРАНИЦЫ =====
  function renderPage(container) {
    if (!entries.length) {
      container.innerHTML = '<div class="lab-alert lab-alert-info">Картография пока пуста. Записи добавляются.</div>';
      return;
    }

    var list = getFiltered();
    var filtersHtml = '<div class="cartography-filters">' +
      '<div class="cartography-era-tabs" role="group" aria-label="Слой картографии">' +
        '<button type="button" class="cartography-filter-btn cartography-era-tab' + (!filters.era ? ' active' : '') + '" data-filter-kind="era" data-filter-value="">Все</button>' +
        '<button type="button" class="cartography-filter-btn cartography-era-tab' + (filters.era === 'modern' ? ' active' : '') + '" data-filter-kind="era" data-filter-value="modern">Современные</button>' +
        '<button type="button" class="cartography-filter-btn cartography-era-tab' + (filters.era === 'ancient' ? ' active' : '') + '" data-filter-kind="era" data-filter-value="ancient">Древние</button>' +
      '</div>' +
      buildFilterGroup('type', TYPE_LABELS) +
      buildFilterGroup('region', REGION_LABELS) +
      '<div class="cartography-stats">Найдено: ' + list.length + ' из ' + entries.length + '</div>' +
      '</div>';

    var cardsHtml = list.length
      ? '<div class="cartography-grid">' + list.map(renderCard).join('') + '</div>'
      : '<div class="lab-alert lab-alert-info">Ничего не найдено по выбранным фильтрам.</div>';

    container.innerHTML = '<header class="section-hero">' +
        '<div class="section-hero-watermark" aria-hidden="true">𐤀 𐤁 𐤂 𐤃 𐤄 𐤅</div>' +
        '<div class="section-hero-kicker">ГОЛЕМ · КАРТОГРАФИЯ</div>' +
        '<h1><img src="../../assets/icons/32/ui/web.png" class="lab-icon" alt="">Картография</h1>' +
        '<p class="section-hero-lead">Смысловая карта: страны, города и регионы как пространственные конструкции.</p>' +
      '</header>' +
      '<div class="cartography-page">' +
      renderWorldMap() +
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
    showDetail: showDetail,
    getEntries: function() { return entries; }
  };
})();

window.Cartography = Cartography;
