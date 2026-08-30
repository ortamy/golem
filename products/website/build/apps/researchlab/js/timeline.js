/**
 * timeline.js — Палео-таймлайн (каталог контейнеров)
 *
 * Каждый таймлайн — отдельный белый контейнер с палео-иконкой,
 * названием, чипом количества событий и кнопкой.
 * Внутри — компактная горизонтальная лента событий.
 */

const Timeline = (function() {
  'use strict';

  var timelineItems = [];
  var timelineContainer = null;

  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text == null ? '' : String(text);
    return d.innerHTML;
  }

  function init(container, parsed) {
    if (!container) return;

    timelineContainer = container;

    // Hero-шапка
    container.innerHTML =
      '<header class="tl-hero">' +
        '<div class="tl-watermark" aria-hidden="true">𐤀 𐤁 𐤂 𐤃 𐤄 𐤅</div>' +
        '<div class="tl-kicker">ПАЛЕО-ТАЙМЛАЙН</div>' +
        '<h1>Каталог таймлайнов</h1>' +
        '<p class="tl-lead">Хронологические карты событий: от палео-ивритского письма до цифровых инструментов восстановления.</p>' +
      '</header>' +
      '<div class="tl-spinner show"><div class="loader"></div><div class="spinner-text">Загрузка таймлайнов…</div></div>';

    // Загружаем данные
    fetch('data/timeline.json')
      .then(function(r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function(timelines) {
        timelineItems = Array.isArray(timelines) ? timelines : [];
        renderCatalog(container, timelineItems);
      })
      .catch(function(err) {
        var spinner = container.querySelector('.tl-spinner');
        if (spinner) spinner.remove();
        container.innerHTML += '<div class="lab-alert lab-alert-error">Ошибка загрузки таймлайнов: ' + escapeHtml(err.message) + '</div>';
      });
  }

  function renderCatalog(container, timelines) {
    if (!timelines || !timelines.length) {
      container.innerHTML = '<div class="lab-alert lab-alert-info">Таймлайны пока не добавлены.</div>';
      return;
    }

    var catalogHtml = timelines.map(function(tl) {
      var count = tl.events ? tl.events.length : 0;

      var events = tl.events || [];
      var visibleEvents = events.slice(0, 3);
      var hiddenEvents = events.slice(3);
      var eventMarkup = function(ev, hidden) {
          return '' +
            '<div class="timeline-event-row' + (hidden ? ' event-card-hidden' : '') + '"' + (hidden ? ' hidden' : '') + '>' +
              '<span class="timeline-date">' + escapeHtml(ev.date) + '</span>' +
              '<span class="timeline-title">' + escapeHtml(ev.title) + '</span>' +
            '</div>';
      };
      var eventsHtml = visibleEvents.map(function(ev) { return eventMarkup(ev, false); }).join('') +
        hiddenEvents.map(function(ev) { return eventMarkup(ev, true); }).join('');
      var moreHtml = hiddenEvents.length
        ? '<button class="tl-show-all" type="button" aria-expanded="false">… показать все (ещё ' + hiddenEvents.length + ')</button>'
        : '';

      return '' +
        '<article class="tl-container" data-timeline-id="' + escapeHtml(tl.id) + '" tabindex="0" role="button" aria-label="Открыть таймлайн: ' + escapeHtml(tl.title) + '">' +
          '<div class="tl-container-header">' +
            '<div class="tl-header-left">' +
              '<span class="tl-container-icon" lang="hbo" aria-hidden="true">' + escapeHtml(tl.paleoIcon) + '</span>' +
              '<h2 class="tl-container-title">' + escapeHtml(tl.title) + '</h2>' +
            '</div>' +
            '<div class="tl-header-right">' +
              '<span class="tl-container-chip">• ' + count + ' ' + pluralize(count, 'событие', 'события', 'событий') + '</span>' +
            '</div>' +
          '</div>' +
          '<p class="tl-container-description">' + escapeHtml(tl.description || '') + '</p>' +
          '<div class="tl-event-list">' +
            eventsHtml +
          '</div>' +
          moreHtml +
          '<div class="tl-container-footer">' +
            '<span class="tl-container-meta">Хронология</span>' +
            '<button class="tl-container-btn" type="button" title="Открыть таймлайн">→ Открыть</button>' +
          '</div>' +
        '</article>';
    }).join('');

    container.innerHTML =
      '<header class="tl-hero">' +
        '<div class="tl-watermark" aria-hidden="true">𐤀 𐤁 𐤂 𐤃 𐤄 𐤅</div>' +
        '<div class="tl-kicker">ПАЛЕО-ТАЙМЛАЙН</div>' +
        '<h1>Каталог таймлайнов</h1>' +
        '<p class="tl-lead">Хронологические карты событий: от палео-ивритского письма до цифровых инструментов восстановления.</p>' +
      '</header>' +
      '<div class="tl-catalog">' + catalogHtml + '</div>';
    bindCatalogEvents(container);
  }

  function bindCatalogEvents(container) {
    container.querySelectorAll('.tl-container').forEach(function(card) {
      var open = function() {
        renderDetail(card.getAttribute('data-timeline-id'));
      };
      card.addEventListener('click', function(event) {
        if (event.target.closest('button')) return;
        open();
      });
      card.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          open();
        }
      });
      var button = card.querySelector('.tl-container-btn');
      if (button) button.addEventListener('click', function(event) {
        event.stopPropagation();
        open();
      });
      var showAll = card.querySelector('.tl-show-all');
      if (showAll) showAll.addEventListener('click', function(event) {
        event.stopPropagation();
        var expanded = this.getAttribute('aria-expanded') === 'true';
        card.querySelectorAll('.event-card-hidden').forEach(function(eventCard) {
          eventCard.hidden = expanded;
        });
        this.setAttribute('aria-expanded', expanded ? 'false' : 'true');
        this.textContent = expanded ? '… показать все (ещё ' + card.querySelectorAll('.event-card-hidden').length + ')' : '← свернуть события';
      });
    });
  }

  function renderDetail(timelineId) {
    var timeline = timelineItems.filter(function(item) {
      return item.id === timelineId;
    })[0];
    if (!timeline || !timelineContainer) return;

    // Шапка модуля подменяется на динамический заголовок таймлайна
    if (window.LabHero && window.LabHero.setView) {
      window.LabHero.setView('timeline', 'detail', {
        kicker: 'ГОЛЕМ · ПАЛЕО-ТАЙМЛАЙН',
        title: timeline.title,
        subtitle: timeline.description || '',
        icon: 'paleo/track.png'
      });
    }

    var eventsHtml = (timeline.events || []).map(function(event, index) {
      return '<article class="tl-detail-event" style="--tl-event-index:' + index + '" role="listitem">' +
        '<div class="tl-detail-event-date">' + escapeHtml(event.date) + '</div>' +
        '<h3 class="tl-detail-event-title">' + escapeHtml(event.title) + '</h3>' +
        '<p class="tl-detail-event-desc">' + escapeHtml(event.description || '') + '</p>' +
      '</article>';
    }).join('');

    timelineContainer.innerHTML =
      '<section class="tl-detail" aria-labelledby="tl-detail-title">' +
        '<header class="tl-detail-hero">' +
          '<div class="tl-detail-icon" lang="hbo" aria-hidden="true">' + escapeHtml(timeline.paleoIcon) + '</div>' +
          '<div class="tl-kicker">ПАЛЕО-ТАЙМЛАЙН · ДЕТАЛЬНЫЙ СЛОЙ</div>' +
          '<div class="tl-detail-title">' + escapeHtml(timeline.title) + '</div>' +
          '<p class="tl-lead">' + escapeHtml(timeline.description || '') + '</p>' +
        '</header>' +
        '<div class="tl-detail-meta">' + (timeline.events || []).length + ' ' + pluralize((timeline.events || []).length, 'событие', 'события', 'событий') + '</div>' +
        '<div class="tl-detail-events" role="list" aria-label="События таймлайна">' + eventsHtml + '</div>' +
      '</section>';

    var backButton = timelineContainer.querySelector('.tl-detail-back');
    if (backButton) backButton.addEventListener('click', function() {
      renderCatalog(timelineContainer, timelineItems);
    });
  }

  function pluralize(n, one, two, five) {
    n = Math.abs(n) % 100;
    var n1 = n % 10;
    if (n > 10 && n < 20) return five;
    if (n1 > 1 && n1 < 5) return two;
    if (n1 === 1) return one;
    return five;
  }

  return {
    init: init,
    render: renderCatalog,
    renderDetail: renderDetail
  };
})();

window.Timeline = Timeline;
