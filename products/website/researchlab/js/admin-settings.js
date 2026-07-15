/**
 * admin-settings.js — admin panel: change local password, generate guest
 * invite links, customize the lab (accent color, default module, hidden
 * sections for guests). Changes only take effect for all visitors once
 * the exported lab-config.json is committed to the repo.
 */
const AdminSettings = (function() {
  'use strict';

  var SECTIONS = [
    { key: 'root-dictionary', label: 'Корневой словарь' },
    { key: 'paleo-images', label: 'Палео-образы' },
    { key: 'etymology-lab', label: 'Этимология' },
    { key: 'word-analyzer', label: 'Разбор слов' },
    { key: 'scripture-reader', label: 'Книгочтение' },
    { key: 'research-library', label: 'Библиотека' },
    { key: 'researches', label: 'Разоблачения' },
    { key: 'religionism-checker', label: 'Чекер религионимов' },
    { key: 'translation-comparator', label: 'Сравнение переводов' },
    { key: 'dictionaries', label: 'Словари' },
    { key: 'exposure', label: 'Принципы' },
    { key: 'methodology', label: 'Методички' },
    { key: 'board-generator', label: 'Генератор досок' },
    { key: 'research-generator', label: 'Генератор исследований' },
    { key: 'board-library', label: 'Архив досок' },
    { key: 'investigation', label: 'Расследование' },
    { key: 'ed-chat', label: 'Нейрочат' },
    { key: 'paleo-keyboard', label: 'Палео-клавиатура' },
    { key: 'vision', label: 'Анализ изображений' }
  ];

  var draft = null;

  function init() {
    render();
  }

  function cloneConfig() {
    var base = (window.AccessGate && AccessGate.getConfig()) || {};
    return {
      accentColor: base.accentColor || '#b8860b',
      defaultModule: base.defaultModule || 'dashboard',
      hiddenSectionsForGuests: (base.hiddenSectionsForGuests || []).slice(),
      guestTokens: (base.guestTokens || []).slice()
    };
  }

  function render() {
    var container = document.getElementById('admin-settings');
    if (!container) return;

    if (!window.AccessGate || !AccessGate.isAdmin()) {
      container.innerHTML = '<div class="lab-alert lab-alert-info">Доступ только для администратора.</div>';
      return;
    }

    if (!draft) draft = cloneConfig();
    renderPanel(container);
  }

  function renderPanel(container) {
    container.innerHTML =
      '<div class="admin-panel">' +
        '<h1 class="admin-title">Настройки лаборатории</h1>' +
        '<p class="admin-subtitle">Изменения действуют локально, пока не экспортированы и закоммичены в data/lab-config.json.</p>' +

        '<section class="settings-section">' +
          '<h2 class="admin-list-title">Пароль администратора</h2>' +
          '<p class="settings-hint">Логин всегда «admin». Меняет пароль только в этом браузере — гейт защищён на уровне удобства, не безопасности.</p>' +
          '<div class="settings-row">' +
            '<input type="password" id="settings-new-pass" class="admin-input" placeholder="Новый пароль">' +
            '<button class="admin-btn admin-btn-secondary" id="settings-pass-btn">Сохранить пароль</button>' +
          '</div>' +
        '</section>' +

        '<section class="settings-section">' +
          '<h2 class="admin-list-title">Гостевые ссылки-приглашения</h2>' +
          '<p class="settings-hint">Ссылка пропускает форму входа и открывает гостевой режим. Не является защитой — не публикуйте её на виду.</p>' +
          '<div class="settings-row">' +
            '<input type="text" id="settings-token-label" class="admin-input" placeholder="Кому: например, коллега">' +
            '<button class="admin-btn admin-btn-secondary" id="settings-token-btn">Создать ссылку</button>' +
          '</div>' +
          '<div id="settings-token-list"></div>' +
        '</section>' +

        '<section class="settings-section">' +
          '<h2 class="admin-list-title">Внешний вид</h2>' +
          '<div class="settings-row">' +
            '<label class="admin-label" for="settings-accent">Акцентный цвет</label>' +
            '<input type="color" id="settings-accent" value="' + escapeHtml(draft.accentColor) + '">' +
          '</div>' +
          '<div class="settings-row">' +
            '<label class="admin-label" for="settings-default-module">Раздел по умолчанию</label>' +
            '<select id="settings-default-module" class="admin-input">' + moduleOptions() + '</select>' +
          '</div>' +
        '</section>' +

        '<section class="settings-section">' +
          '<h2 class="admin-list-title">Разделы, скрытые от гостей</h2>' +
          '<div id="settings-sections-grid" class="settings-checkbox-grid">' + sectionCheckboxes() + '</div>' +
        '</section>' +

        '<div class="admin-actions">' +
          '<button class="admin-btn admin-btn-primary" id="settings-export-btn">Экспортировать lab-config.json</button>' +
        '</div>' +
        '<div id="settings-notice" class="admin-notice" style="display:none;"></div>' +
      '</div>';

    bindEvents();
    renderTokenList();
  }

  function moduleOptions() {
    var html = '<option value="dashboard"' + (draft.defaultModule === 'dashboard' ? ' selected' : '') + '>Дашборд</option>';
    SECTIONS.forEach(function(s) {
      html += '<option value="' + s.key + '"' + (draft.defaultModule === s.key ? ' selected' : '') + '>' + escapeHtml(s.label) + '</option>';
    });
    return html;
  }

  function sectionCheckboxes() {
    return SECTIONS.map(function(s) {
      var checked = draft.hiddenSectionsForGuests.indexOf(s.key) !== -1;
      return '<label class="settings-checkbox">' +
        '<input type="checkbox" data-section-key="' + s.key + '"' + (checked ? ' checked' : '') + '>' +
        escapeHtml(s.label) +
      '</label>';
    }).join('');
  }

  function showNotice(msg, isError) {
    var notice = document.getElementById('settings-notice');
    if (!notice) return;
    notice.className = 'admin-notice' + (isError ? ' admin-notice-error' : ' admin-notice-success');
    notice.textContent = msg;
    notice.style.display = 'block';
    setTimeout(function() { notice.style.display = 'none'; }, 3000);
  }

  function bindEvents() {
    document.getElementById('settings-pass-btn').addEventListener('click', function() {
      var val = document.getElementById('settings-new-pass').value.trim();
      if (!val) {
        showNotice('Введите новый пароль.', true);
        return;
      }
      AccessGate.setPasswordOverride(val);
      document.getElementById('settings-new-pass').value = '';
      showNotice('Пароль обновлён в этом браузере.', false);
    });

    document.getElementById('settings-token-btn').addEventListener('click', function() {
      var label = document.getElementById('settings-token-label').value.trim() || 'Без пометки';
      var token = 'g' + Math.abs(hashString(label + draft.guestTokens.length + Date.now())).toString(36);
      draft.guestTokens.push({ token: token, label: label });
      document.getElementById('settings-token-label').value = '';
      renderTokenList();
      showNotice('Ссылка создана. Не забудьте экспортировать конфигурацию.', false);
    });

    document.getElementById('settings-accent').addEventListener('input', function(e) {
      draft.accentColor = e.target.value;
    });

    document.getElementById('settings-default-module').addEventListener('change', function(e) {
      draft.defaultModule = e.target.value;
    });

    document.querySelectorAll('#settings-sections-grid input[type=checkbox]').forEach(function(cb) {
      cb.addEventListener('change', function() {
        var key = cb.getAttribute('data-section-key');
        var idx = draft.hiddenSectionsForGuests.indexOf(key);
        if (cb.checked && idx === -1) draft.hiddenSectionsForGuests.push(key);
        if (!cb.checked && idx !== -1) draft.hiddenSectionsForGuests.splice(idx, 1);
      });
    });

    document.getElementById('settings-export-btn').addEventListener('click', exportConfig);
  }

  function hashString(str) {
    var h = 0;
    for (var i = 0; i < str.length; i++) {
      h = ((h << 5) - h) + str.charCodeAt(i);
      h |= 0;
    }
    return h;
  }

  function renderTokenList() {
    var list = document.getElementById('settings-token-list');
    if (!list) return;
    if (!draft.guestTokens.length) {
      list.innerHTML = '<div class="admin-empty">Пока нет гостевых ссылок.</div>';
      return;
    }
    var base = window.location.origin + window.location.pathname;
    var html = '';
    draft.guestTokens.forEach(function(t, i) {
      var url = base + '#access=' + encodeURIComponent(t.token);
      html += '<div class="admin-list-item">' +
        '<div class="admin-list-item-title">' + escapeHtml(t.label) + '<br><span class="settings-hint">' + escapeHtml(url) + '</span></div>' +
        '<button class="admin-btn admin-btn-secondary admin-btn-sm" data-copy-url="' + escapeHtml(url) + '">Копировать</button>' +
        '<button class="admin-btn admin-btn-danger admin-btn-sm" data-remove-token="' + i + '">Удалить</button>' +
      '</div>';
    });
    list.innerHTML = html;
    list.querySelectorAll('[data-copy-url]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        navigator.clipboard.writeText(btn.getAttribute('data-copy-url'));
        showNotice('Ссылка скопирована.', false);
      });
    });
    list.querySelectorAll('[data-remove-token]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        draft.guestTokens.splice(Number(btn.getAttribute('data-remove-token')), 1);
        renderTokenList();
      });
    });
  }

  function exportConfig() {
    var blob = new Blob([JSON.stringify(draft, null, 2)], { type: 'application/json;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'lab-config.json';
    a.click();
    URL.revokeObjectURL(a.href);
    showNotice('Файл lab-config.json скачан. Замените data/lab-config.json и закоммитьте.', false);
  }

  window.AdminSettings = { init: init };
  return window.AdminSettings;
})();

