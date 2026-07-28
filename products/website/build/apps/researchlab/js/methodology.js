/**
   * methodology.js — раздел «Методология»: полные названия рабочих табов.
 * CRUD карточек: localStorage (быстрый кеш) + запись в data/methodology/cards.json через
 * сервер products/agents/server.py (порт 8000).
 */
(function(window, document) {
  'use strict';

  var PAGE_PATH = 'pages/methodology.html';
  var DATA_PATH = 'data/methodology/cards.json';
  var API_URL = 'http://localhost:8000/api/methodology/cards';
  var STORAGE_KEY = 'golem_methodology_cards_v1';

  var CATEGORIES = [
    { key: 'principles', label: 'Принципы разоблачения' },
    { key: 'methods', label: 'Методы разоблачения' },
    { key: 'mechanisms', label: 'Механизмы подмены' }
  ];

  var store = null; // { categories: {...}, cards: [...] }
  var activeTab = CATEGORIES[0].key;

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
  var EDIT_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4 20h4l10-10-4-4L4 16v4z"></path><path d="M13 7l4 4"></path></svg>';
  var DELETE_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 7h14"></path><path d="M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"></path><path d="M7 7l1 13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1l1-13"></path></svg>';
  var CHECK_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M5 13l4 4L19 7"></path></svg>';
  var SAVE_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>';

  function toast(msg) {
    if (window.LabToast) window.LabToast.show(msg);
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text).catch(function() { fallbackCopy(text); });
    }
    fallbackCopy(text);
    return Promise.resolve();
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.cssText = 'position:fixed;opacity:0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch(e) {}
    document.body.removeChild(ta);
  }

  function copyTextWithFeedback(btn, text) {
    copyText(text).then(function() {
      btn.innerHTML = CHECK_ICON;
      btn.classList.add('is-copied');
      setTimeout(function() {
        btn.innerHTML = COPY_ICON;
        btn.classList.remove('is-copied');
      }, 1500);
    });
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

  // ===== ХРАНИЛИЩЕ =====
  function loadLocalStore() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function saveLocalStore(data) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {}
  }

  function generateId(category) {
    return category + '-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5);
  }

  function persistStore() {
    saveLocalStore(store);
    fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(store)
    }).then(function(response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      toast('Сохранено в файл');
    }).catch(function() {
      toast('Сохранено локально. Файл не обновлён — запустите сервер на порту 8000.');
    });
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
      bindAddButton(container);
      loadStore(container);
    }).catch(function(error) {
      container.innerHTML = '<div class="lab-alert lab-alert-error">Не удалось загрузить раздел: ' + escapeHtml(error.message) + '</div>';
      container.dataset.methodologyReady = '0';
    });
  }

  function loadStore(container) {
    fetch(DATA_PATH).then(function(response) {
      if (!response.ok) throw new Error('HTTP ' + response.status + ' for ' + DATA_PATH);
      return response.json();
    }).then(function(data) {
      store = data;
      saveLocalStore(store);
      showTab(container, activeTab);
    }).catch(function() {
      var cached = loadLocalStore();
      if (cached) {
        store = cached;
        showTab(container, activeTab);
      } else {
        var panel = container.querySelector('#methodology-panel');
        if (panel) {
          panel.className = 'methodology-panel methodology-panel-empty';
          panel.innerHTML = '<div class="lab-alert lab-alert-error">Не удалось загрузить материалы методологии.</div>';
        }
      }
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

  function bindAddButton(container) {
    var btn = container.querySelector('#methodology-add-btn');
    if (btn) btn.addEventListener('click', function() { openForm(container); });
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
    if (!panel || !store) return;

    var catInfo = (store.categories || {})[key] || {};
    if (descriptionEl) descriptionEl.textContent = catInfo.description || '';

    var cards = (store.cards || []).filter(function(c) { return c.category === key; });
    renderPanel(container, panel, cards);
  }

  function renderPanel(container, panel, cards) {
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
            '<button type="button" class="methodology-icon-btn methodology-copy-btn" data-id="' + escapeHtml(card.id) + '" title="Копировать" aria-label="Копировать карточку">' + COPY_ICON + '</button>' +
            '<button type="button" class="methodology-icon-btn methodology-prompt-btn" data-id="' + escapeHtml(card.id) + '" title="В конструктор промптов" aria-label="Отправить в конструктор промптов">' + WAND_ICON + '</button>' +
            '<button type="button" class="methodology-icon-btn methodology-edit-btn" data-id="' + escapeHtml(card.id) + '" title="Редактировать" aria-label="Редактировать карточку">' + EDIT_ICON + '</button>' +
            '<button type="button" class="methodology-icon-btn methodology-delete-btn" data-id="' + escapeHtml(card.id) + '" title="Удалить" aria-label="Удалить карточку">' + DELETE_ICON + '</button>' +
          '</div>' +
        '</div>' +
        '<p class="methodology-card-text">' + escapeHtml(card.text) + '</p>' +
      '</article>';
    }).join('');

    bindCardActions(container, panel);
  }

  function findCard(id) {
    var cards = store.cards || [];
    for (var i = 0; i < cards.length; i++) {
      if (cards[i].id === id) return cards[i];
    }
    return null;
  }

  function bindCardActions(container, panel) {
    panel.querySelectorAll('.methodology-copy-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var card = findCard(btn.dataset.id);
        if (!card) return;
        copyTextWithFeedback(btn, card.title + '\n\n' + card.text);
      });
    });
    panel.querySelectorAll('.methodology-prompt-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var card = findCard(btn.dataset.id);
        if (!card) return;
        sendToPromptGenerator(card.title, card.text);
      });
    });
    panel.querySelectorAll('.methodology-edit-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var card = findCard(btn.dataset.id);
        var article = btn.closest('.methodology-card');
        if (!card || !article) return;
        if (article.classList.contains('is-editing')) {
          finishInlineEdit(article, card);
        } else {
          startInlineEdit(article, card);
        }
      });
    });
    panel.querySelectorAll('.methodology-delete-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var card = findCard(btn.dataset.id);
        if (card) deleteCard(container, card);
      });
    });
  }

  function startInlineEdit(article, card) {
    var textEl = article.querySelector('.methodology-card-text');
    var editBtn = article.querySelector('.methodology-edit-btn');
    if (!textEl || !editBtn) return;

    var textarea = document.createElement('textarea');
    textarea.className = 'methodology-card-textarea';
    textarea.value = card.text;
    textarea.rows = Math.min(16, Math.max(4, card.text.split('\n').length + 1));
    textEl.replaceWith(textarea);
    textarea.focus();

    article.classList.add('is-editing');
    editBtn.classList.add('is-active');
    editBtn.innerHTML = SAVE_ICON;
    editBtn.title = 'Сохранить';
    editBtn.setAttribute('aria-label', 'Сохранить карточку');
  }

  function finishInlineEdit(article, card) {
    var textarea = article.querySelector('.methodology-card-textarea');
    var editBtn = article.querySelector('.methodology-edit-btn');
    if (!textarea) return;

    var newText = textarea.value.trim();
    if (newText && newText !== card.text) {
      card.text = newText;
      persistStore();
    }

    var textEl = document.createElement('p');
    textEl.className = 'methodology-card-text';
    textEl.textContent = card.text;
    textarea.replaceWith(textEl);

    article.classList.remove('is-editing');
    if (editBtn) {
      editBtn.classList.remove('is-active');
      editBtn.innerHTML = EDIT_ICON;
      editBtn.title = 'Редактировать';
      editBtn.setAttribute('aria-label', 'Редактировать карточку');
    }
  }

  function deleteCard(container, card) {
    if (!window.confirm('Удалить карточку «' + card.title + '»?')) return;
    store.cards = (store.cards || []).filter(function(c) { return c.id !== card.id; });
    persistStore();
    showTab(container, activeTab);
  }

  // ===== ФОРМА ДОБАВЛЕНИЯ НОВОЙ КАРТОЧКИ =====
  function openForm(container) {
    var options = CATEGORIES.map(function(c) {
      var selected = activeTab === c.key ? ' selected' : '';
      return '<option value="' + c.key + '"' + selected + '>' + escapeHtml(c.label) + '</option>';
    }).join('');

    var body =
      '<div class="methodology-form">' +
        '<label class="admin-label" for="mf-title">Заголовок</label>' +
        '<input type="text" id="mf-title" class="admin-input" value="">' +
        '<label class="admin-label" for="mf-category">Раздел</label>' +
        '<select id="mf-category" class="admin-input">' + options + '</select>' +
        '<label class="admin-label" for="mf-text">Текст</label>' +
        '<textarea id="mf-text" class="admin-textarea" rows="8"></textarea>' +
      '</div>';

    var footer =
      '<button class="lab-btn lab-btn-secondary lab-btn-sm" onclick="LabModal.close()">Отмена</button>' +
      '<button class="lab-btn lab-btn-primary lab-btn-sm" id="mf-save-btn">Сохранить</button>';

    window.LabModal.show('Добавить карточку', body, footer);

    document.getElementById('mf-save-btn').addEventListener('click', function() {
      saveForm(container);
    });
  }

  function saveForm(container) {
    var titleInput = document.getElementById('mf-title');
    var categoryInput = document.getElementById('mf-category');
    var textInput = document.getElementById('mf-text');
    if (!titleInput || !categoryInput || !textInput) return;

    var titleValue = titleInput.value.trim();
    var textValue = textInput.value.trim();
    if (!titleValue || !textValue) {
      toast('Заполните заголовок и текст');
      return;
    }

    var categoryValue = categoryInput.value;
    store.cards = store.cards || [];
    store.cards.push({
      id: generateId(categoryValue),
      category: categoryValue,
      title: titleValue,
      text: textValue
    });

    persistStore();
    window.LabModal.close();
    activeTab = categoryValue;
    showTab(container, activeTab);
  }
})(window, document);
