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
  const STATE_MATRIX_PATH = 'data/state-matrix.json';
  const MODERN_COUNTRIES_PATH = 'data/modern-countries.json';
  const TYPE_LABELS = { country: 'Страна', 'modern-state': 'Современное государство', city: 'Город', region: 'Регион', empire: 'Империя' };
  const ERA_LABELS = { ancient: 'Древние', modern: 'Современные' };
  const REGION_LABELS = {
    Levant: 'Левант', Egypt: 'Египет', Mesopotamia: 'Месопотамия',
    Arabia: 'Аравия', Europe: 'Европа', Persia: 'Персия'
  };

  let entries = [];
  let entriesById = {};
  let dataPromise = null;
  let worldMapPromise = null;
  let worldMapMarkup = '';
  let countryDescriptions = {};
  let countryStates = {};
  let filters = { era: '', type: '', region: '' };

  const MAP_INFO = {
    russia: ['Россия', 'Европа и Азия'], usa: ['США', 'Северная Америка'], canada: ['Канада', 'Северная Америка'],
    mexico: ['Мексика', 'Северная Америка'], brazil: ['Бразилия', 'Южная Америка'], argentina: ['Аргентина', 'Южная Америка'],
    egypt: ['Египет', 'Африка'], 'south africa': ['ЮАР', 'Африка'], china: ['Китай', 'Азия'], india: ['Индия', 'Азия'],
    japan: ['Япония', 'Азия'], israel: ['Израиль', 'Азия'], iran: ['Иран', 'Азия'], iraq: ['Ирак', 'Азия'],
    turkey: ['Турция', 'Европа и Азия'], france: ['Франция', 'Европа'], germany: ['Германия', 'Европа'],
    ukraine: ['Украина', 'Европа'], australia: ['Австралия', 'Океания'],
    britain: ['Великобритания', 'Европа'], italy: ['Италия', 'Европа'], spain: ['Испания', 'Европа'],
    mexico: ['Мексика', 'Северная Америка'], argentina: ['Аргентина', 'Южная Америка'],
    canada: ['Канада', 'Северная Америка'], 'south africa': ['ЮАР', 'Африка'], saudi: ['Саудовская Аравия', 'Азия']
  };
  const MAP_COUNTRY_NAMES = {
    finland: ['Финляндия', 'Европа'], norway: ['Норвегия', 'Европа'], sweden: ['Швеция', 'Европа'],
    poland: ['Польша', 'Европа'], kazakhstan: ['Казахстан', 'Азия'], indonesia: ['Индонезия', 'Азия'],
    philippines: ['Филиппины', 'Азия'], colombia: ['Колумбия', 'Южная Америка'], peru: ['Перу', 'Южная Америка'],
    chile: ['Чили', 'Южная Америка'], venezuela: ['Венесуэла', 'Южная Америка'], ecuador: ['Эквадор', 'Южная Америка'],
    bolivia: ['Боливия', 'Южная Америка'], paraguay: ['Парагвай', 'Южная Америка'], uruguay: ['Уругвай', 'Южная Америка'],
    guyana: ['Гайана', 'Южная Америка'], suriname: ['Суринам', 'Южная Америка'],
    algeria: ['Алжир', 'Африка'], morocco: ['Марокко', 'Африка'], tunisia: ['Тунис', 'Африка'],
    nigeria: ['Нигерия', 'Африка'], kenya: ['Кения', 'Африка'], ethiopia: ['Эфиопия', 'Африка'],
    madagascar: ['Мадагаскар', 'Африка'], namibia: ['Намибия', 'Африка'], botswana: ['Ботсвана', 'Африка'],
    iran: ['Иран', 'Азия'], iraq: ['Ирак', 'Азия'], afghanistan: ['Афганистан', 'Азия'], pakistan: ['Пакистан', 'Азия'],
    mongolia: ['Монголия', 'Азия'], vietnam: ['Вьетнам', 'Азия'], thailand: ['Таиланд', 'Азия'], malaysia: ['Малайзия', 'Азия'],
    'north korea': ['Северная Корея', 'Азия'], 'south korea': ['Южная Корея', 'Азия'],
    portugal: ['Португалия', 'Европа'], netherlands: ['Нидерланды', 'Европа'], belgium: ['Бельгия', 'Европа'],
    switzerland: ['Швейцария', 'Европа'], austria: ['Австрия', 'Европа'], czechia: ['Чехия', 'Европа'],
    romania: ['Румыния', 'Европа'], greece: ['Греция', 'Европа'], serbia: ['Сербия', 'Европа'],
    'new zealand': ['Новая Зеландия', 'Австралия'], papua: ['Папуа — Новая Гвинея', 'Австралия']
  };
  const CONTINENT_COUNTRIES = {
    'Северная Америка': ['Канада', 'США', 'Мексика', 'Гватемала', 'Белиз', 'Гондурас', 'Сальвадор', 'Никарагуа', 'Коста-Рика', 'Панама', 'Куба', 'Гаити', 'Доминиканская Республика', 'Ямайка'],
    'Южная Америка': ['Аргентина', 'Боливия', 'Бразилия', 'Чили', 'Колумбия', 'Эквадор', 'Гайана', 'Парагвай', 'Перу', 'Суринам', 'Уругвай', 'Венесуэла'],
    'Европа': ['Австрия', 'Бельгия', 'Болгария', 'Великобритания', 'Венгрия', 'Германия', 'Греция', 'Дания', 'Ирландия', 'Исландия', 'Испания', 'Италия', 'Латвия', 'Литва', 'Нидерланды', 'Норвегия', 'Польша', 'Португалия', 'Румыния', 'Сербия', 'Словакия', 'Словения', 'Финляндия', 'Франция', 'Хорватия', 'Чехия', 'Швейцария', 'Швеция', 'Эстония'],
    'Азия': ['Афганистан', 'Бангладеш', 'Бахрейн', 'Вьетнам', 'Индия', 'Индонезия', 'Иордания', 'Ирак', 'Иран', 'Израиль', 'Казахстан', 'Камбоджа', 'Катар', 'Китай', 'Киргизия', 'Кувейт', 'Лаос', 'Малайзия', 'Монголия', 'Непал', 'Оман', 'Пакистан', 'Палестина', 'Саудовская Аравия', 'Северная Корея', 'Сингапур', 'Сирия', 'Таиланд', 'Таджикистан', 'Туркменистан', 'Турция', 'Узбекистан', 'Филиппины', 'Шри-Ланка', 'Южная Корея', 'Япония'],
    'Африка': ['Алжир', 'Ангола', 'Бенин', 'Ботсвана', 'Буркина-Фасо', 'Бурунди', 'Габон', 'Гана', 'Гвинея', 'Египет', 'Замбия', 'Зимбабве', 'Камерун', 'Кения', 'Конго', 'Либерия', 'Ливия', 'Мадагаскар', 'Малави', 'Мали', 'Марокко', 'Мозамбик', 'Намибия', 'Нигер', 'Нигерия', 'Руанда', 'Сенегал', 'Сомали', 'Судан', 'Тунис', 'Уганда', 'ЦАР', 'Чад', 'Эфиопия', 'ЮАР'],
    'Австралия': ['Австралия', 'Новая Зеландия', 'Папуа — Новая Гвинея', 'Фиджи', 'Вануату', 'Самоа', 'Тонга']
  };
  function registerCountryAliases(countryNames) {
    countryNames.forEach(function(name) {
      var id = String(name).toLowerCase().replace(/[—’']/g, ' ').replace(/[^a-zа-яё0-9]+/gi, ' ').trim();
      if (!MAP_INFO[id]) {
        var continent = Object.keys(CONTINENT_COUNTRIES).find(function(key) { return CONTINENT_COUNTRIES[key].indexOf(name) !== -1; }) || 'Не определён';
        MAP_INFO[id] = [name, continent];
      }
    });
  }
  Object.keys(MAP_COUNTRY_NAMES).forEach(function(id) { MAP_INFO[id] = MAP_COUNTRY_NAMES[id]; });
  const STATE_COUNTRY_IDS = {
    'Россия': 'russia', 'Израиль': 'israel', 'США': 'usa', 'Египет': 'egypt',
    'Германия': 'germany', 'Китай': 'china', 'Индия': 'india', 'Украина': 'ukraine',
    'Япония': 'japan', 'Франция': 'france', 'Бразилия': 'brazil', 'Саудовская Аравия': 'saudi',
    'Австралия': 'australia', 'Канада': 'canada', 'Великобритания': 'britain', 'Италия': 'italy',
    'Испания': 'spain', 'Мексика': 'mexico', 'Аргентина': 'argentina', 'Турция': 'turkey', 'ЮАР': 'south africa'
  };

  function dataPath() {
    return new URL(DATA_PATH, document.baseURI).href;
  }

  function heraldryDataPath() {
    return new URL(HERALDRY_DATA_PATH, document.baseURI).href;
  }

  function stateMatrixPath() {
    return new URL(STATE_MATRIX_PATH, document.baseURI).href;
  }

  function modernCountriesPath() {
    return new URL(MODERN_COUNTRIES_PATH, document.baseURI).href;
  }

  function modernCountryId(name) {
    return 'modern-' + String(name).toLowerCase().replace(/[^a-zа-яё0-9]+/gi, '-').replace(/^-|-$/g, '');
  }

  function applyStateClasses(markup) {
    return markup.replace(/(<path\b[^>]*class="world-country"[^>]*data-country-id="([^"]+)"[^>]*)(\/?>)/gi, function(match, prefix, id, close) {
      var info = MAP_INFO[id] || MAP_COUNTRY_NAMES[id];
      var state = info && countryStates[info[0]];
      return prefix.replace('class="world-country"', 'class="world-country world-state-' + (state || 'unknown') + '"') + close;
    });
  }

  function loadWorldMap() {
    if (worldMapPromise) return worldMapPromise;
    var mapUrl = new URL('../../assets/maps/world-map.svg', document.baseURI).href;
    worldMapPromise = fetch(mapUrl).then(function(response) {
      if (!response.ok) throw new Error('HTTP ' + response.status + ' for world map');
      return response.text();
    }).then(function(source) {
      var documentNode = new DOMParser().parseFromString(source, 'image/svg+xml');
      if (documentNode.querySelector('parsererror')) throw new Error('Неверный формат world-map.svg');
      return Array.prototype.map.call(documentNode.querySelectorAll('path'), function(path) {
        var id = path.getAttribute('id');
        if (!id || id === 'path1' || id === 'path-1') return '';
        path.removeAttribute('style');
        path.removeAttribute('inkscape:path-effect');
        path.removeAttribute('inkscape:original-d');
        path.removeAttribute('transform');
        path.setAttribute('class', 'world-country');
        path.setAttribute('data-country-id', id);
        path.setAttribute('tabindex', '0');
        path.setAttribute('role', 'button');
        return new XMLSerializer().serializeToString(path);
      }).join('');
    });
    return worldMapPromise;
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
      }),
      fetch(stateMatrixPath()).then(function(response) {
        if (!response.ok) throw new Error('HTTP ' + response.status + ' for state matrix');
        return response.json();
      }),
      fetch(modernCountriesPath()).then(function(response) {
        if (!response.ok) throw new Error('HTTP ' + response.status + ' for modern countries');
        return response.json();
      }),
      loadWorldMap()
    ])
      .then(function(results) {
        var data = results[0];
        var heraldryList = Array.isArray(results[1]) ? results[1] : [];
        var matrix = results[2] && Array.isArray(results[2].countries) ? results[2].countries : [];
        var countryNames = results[3] && Array.isArray(results[3].countries) ? results[3].countries : [];
        registerCountryAliases(countryNames);
        matrix.forEach(function(country) {
          countryDescriptions[country.name] = country.note || '';
          var states = country.states || {};
          countryStates[country.name] = Object.keys(states).sort(function(a, b) { return Number(states[b]) - Number(states[a]); })[0] || '';
        });
        worldMapMarkup = applyStateClasses(results[4]);
        var list = Array.isArray(data) ? data : (data && Array.isArray(data.entries) ? data.entries : null);
        if (!list) throw new Error('Неверный формат данных');
        var ancientEntries = list.filter(function(e) { return e && e.id && e.name; }).map(function(e) {
          e.era = e.era || 'ancient';
          return e;
        });
        var heraldryByName = {};
        heraldryList.forEach(function(e) { if (e && e.name) heraldryByName[e.name] = e; });
        var modernEntries = countryNames.map(function(name) {
          var source = heraldryByName[name] || {};
          var e = Object.assign({}, source);
          e.id = source.id || modernCountryId(name);
          e.name = name;
          e.era = 'modern';
          e.type = 'modern-state';
          e.paleo = e.paleo || e.hebrew || '';
          e.summary = e.summary || e.card_description || e.description || (name + ' — современное государство со своей территорией, историей и языковой средой.');
          e.meaning = e.meaning || e.card_description || 'Государство и его географическая среда';
          e.dominantState = countryStates[name] || '';
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
      '<svg class="cartography-world-svg" viewBox="0 0 950 620" role="img" aria-label="Интерактивная карта мира" focusable="false">' +
        '<rect class="world-sea" x="0" y="0" width="950" height="620"></rect>' +
        '<g class="world-countries">' + worldMapMarkup + '</g>' +
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
      card.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          var id = this.getAttribute('data-id');
          if (id) showDetail(id);
        }
      });
    });

    container.querySelectorAll('.world-country').forEach(function(country) {
      country.addEventListener('click', function() { showCountryDetail(this.getAttribute('data-country-id')); });
      country.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); showCountryDetail(this.getAttribute('data-country-id')); }
      });
    });
  }

  function showCountryDetail(countryId) {
    var info = MAP_INFO[countryId] || MAP_COUNTRY_NAMES[countryId] || [countryId.replace(/[-_]/g, ' '), 'Не определён'];
    var hasData = Boolean(countryStates[info[0]]);
    var description = countryDescriptions[info[0]] || (hasData
      ? 'Географическая точка в карте потока.'
      : 'Данные уточняются. Поток в этой стране пока не диагностирован');
    var diagnosis = hasData ? countryStates[info[0]] : 'Данные уточняются. Поток в этой стране пока не диагностирован';
    var html = '<div class="cartography-detail cartography-map-detail"><div class="cartography-detail-section cartography-callout">' +
      '<p><strong>Материк:</strong> ' + escapeHtml(info[1]) + '</p>' +
      '<p><strong>Диагноз:</strong> ' + escapeHtml(diagnosis) + '</p>' +
      '<p>' + escapeHtml(description) + '</p>' +
      '</div></div>';
    if (typeof LabModal !== 'undefined') LabModal.show(escapeHtml(info[0]), html, '<button class="lab-btn lab-btn-secondary lab-btn-sm" onclick="LabModal.close()">Закрыть</button>');
  }

  function renderCard(e, index) {
    return '<div class="cartography-card" data-id="' + escapeHtml(e.id) + '" tabindex="0" role="button" aria-label="Открыть карточку: ' + escapeHtml(e.name) + '" style="animation-delay:' + (index * 60) + 'ms">' +
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
    if (typeof LabModal !== 'undefined') {
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

    var paleoBreakdown = entry.symbol_paleo_breakdown && entry.symbol_paleo_breakdown.elements
      ? entry.symbol_paleo_breakdown.elements.map(function(element) {
          return '<li><strong>' + escapeHtml(element.element || '') + '</strong>: ' + escapeHtml(element.paleo || '') + ' — ' + escapeHtml(element.meaning || '') + '</li>';
        }).join('')
      : '<li><strong>' + escapeHtml(entry.paleo || 'Палео-форма не задана') + '</strong>: последовательность знаков для отдельного исследования.</li>';

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
      '<div class="cartography-detail-section cartography-paleo-analysis">' +
        '<h3>Разбор на палео-иврите</h3>' +
        '<p><strong>Палео-форма:</strong> <span class="cartography-detail-paleo" dir="rtl">' + escapeHtml(entry.paleo || '—') + '</span></p>' +
        '<p><strong>Смысловая сборка:</strong> ' + escapeHtml(entry.meaning || 'Географическая среда и её поток') + '</p>' +
        '<ul>' + paleoBreakdown + '</ul>' +
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
