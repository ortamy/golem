/**
 * methodology.js — раздел «Методология»: табы Манифест/Принципы/Методы/Механизмы подмены.
 */
(function(window, document) {
  'use strict';

  var PAGE_PATH = 'pages/methodology.html';
  var TABS = [
    { key: 'manifest', dataPath: 'data/methodology/manifest.json' },
    { key: 'principles', dataPath: 'data/methodology/principles.json' },
    { key: 'methods', dataPath: 'data/methodology/methods.json' },
    { key: 'mechanisms', dataPath: 'data/methodology/mechanisms.json' }
  ];

  var cache = {};
  var activeTab = TABS[0].key;

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  var COPY_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="8" y="8" width="11" height="11" rx="1.5"></rect><path d="M16 8V5.5A1.5 1.5 0 0 0 14.5 4h-9A1.5 1.5 0 0 0 4 5.5v9A1.5 1.5 0 0 0 5.5 16H8"></path></svg>';
  var WAND_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M15 4l1.5 1.5M19 8l1.5 1.5M4 20l9-9M13 9l2 2"></path><path d="M15 4l-1 3 3-1z"></path></svg>';

  function toast(msg) {
    if (window.LabToast) window.LabToast.show(msg);
  }

  function copyText(text) {
    if (window.LabExport) {
      window.LabExport.copyText(text);
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function() { toast('Скопировано!'); });
    }
  }

  function sendToPromptGenerator(title, text) {
    if (window.LabRouter) window.LabRouter.navigate('prompt-generator');
    var attempt = 0;
    function tryAdd() {
      if (window.PromptGenerator && typeof window.PromptGenerator.addExternalBlock === 'function') {
        window.PromptGenerator.addExternalBlock(title, text);
        toast('Добавлено в конструктор промптов');
        return;
      }
      attempt++;
      if (attempt < 30) setTimeout(tryAdd, 100);
    }
    setTimeout(tryAdd, 50);
  }

  window.MethodologyLab = { init: init };

  function init(container) {
    if (!container) return;
    if (container.dataset.methodologyReady === '1') return;
    container.dataset.methodologyReady = '1';
    container.innerHTML = '<div class="lab-spinner show"><div class="loader"></div><div class="spinner-text">Загрузка…</div></div>';

    fetch(PAGE_PATH).then(function(response) {
      if (!response.ok) throw new Error('HTTP ' + response.status + ' for ' + PAGE_PATH);
      return response.text();
    }).then(function(html) {
      container.innerHTML = html;
      bindTabs(container);
      showTab(container, activeTab);
    }).catch(function(error) {
      container.innerHTML = '<div class="lab-alert lab-alert-error">Не удалось загрузить раздел: ' + escapeHtml(error.message) + '</div>';
      container.dataset.methodologyReady = '0';
    });
  }

  function bindTabs(container) {
    var tabs = container.querySelectorAll('.methodology-tab');
    tabs.forEach(function(tab) {
      tab.addEventListener('click', function() {
        var key = tab.dataset.tab;
        if (key === activeTab) return;
        activeTab = key;
        showTab(container, key);
      });
    });
  }

  function getTabConfig(key) {
    for (var i = 0; i < TABS.length; i++) {
      if (TABS[i].key === key) return TABS[i];
    }
    return TABS[0];
  }

  function showTab(container, key) {
    var tabs = container.querySelectorAll('.methodology-tab');
    tabs.forEach(function(tab) {
      var isActive = tab.dataset.tab === key;
      tab.classList.toggle('active', isActive);
      tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });

    var panel = container.querySelector('#methodology-panel');
    var descriptionEl = container.querySelector('#methodology-tab-description');
    if (!panel) return;

    if (cache[key]) {
      renderPanel(panel, descriptionEl, cache[key]);
      return;
    }

    panel.className = 'methodology-panel methodology-panel-empty';
    panel.innerHTML = '<div class="lab-spinner show"><div class="loader"></div><div class="spinner-text">Загрузка материалов…</div></div>';
    if (descriptionEl) descriptionEl.textContent = '';

    var config = getTabConfig(key);
    fetch(config.dataPath).then(function(response) {
      if (!response.ok) throw new Error('HTTP ' + response.status + ' for ' + config.dataPath);
      return response.json();
    }).then(function(data) {
      cache[key] = data;
      if (activeTab === key) renderPanel(panel, descriptionEl, data);
    }).catch(function(error) {
      panel.className = 'methodology-panel methodology-panel-empty';
      panel.innerHTML = '<div class="lab-alert lab-alert-error">Ошибка загрузки: ' + escapeHtml(error.message) + '</div>';
    });
  }

  function renderPanel(panel, descriptionEl, data) {
    if (descriptionEl) descriptionEl.textContent = data.description || '';

    var cards = Array.isArray(data.cards) ? data.cards : [];
    if (!cards.length) {
      panel.className = 'methodology-panel methodology-panel-empty';
      panel.innerHTML = '<div class="lab-alert lab-alert-info">Материалы пока не заполнены.</div>';
      return;
    }

    panel.className = 'methodology-panel';
    panel.innerHTML = cards.map(function(card, index) {
      return '<article class="methodology-card" style="animation-delay:' + (index * 30) + 'ms">' +
        '<div class="methodology-card-head">' +
          '<h3 class="methodology-card-title">' + escapeHtml(card.title) + '</h3>' +
          '<div class="methodology-card-actions">' +
            '<button type="button" class="methodology-icon-btn methodology-copy-btn" data-index="' + index + '" title="Копировать" aria-label="Копировать карточку">' + COPY_ICON + '</button>' +
            '<button type="button" class="methodology-icon-btn methodology-prompt-btn" data-index="' + index + '" title="В конструктор промптов" aria-label="Отправить в конструктор промптов">' + WAND_ICON + '</button>' +
          '</div>' +
        '</div>' +
        '<p class="methodology-card-text">' + escapeHtml(card.text) + '</p>' +
      '</article>';
    }).join('');

    panel.querySelectorAll('.methodology-copy-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var card = cards[Number(btn.dataset.index)];
        if (!card) return;
        copyText(card.title + '\n\n' + card.text);
      });
    });
    panel.querySelectorAll('.methodology-prompt-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var card = cards[Number(btn.dataset.index)];
        if (!card) return;
        sendToPromptGenerator(card.title, card.text);
      });
    });
  }
})(window, document);
