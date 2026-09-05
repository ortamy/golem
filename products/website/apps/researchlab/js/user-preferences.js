/**
 * user-preferences.js — персональные настройки для исследователя и гостя.
 * Хранит предпочтения в localStorage по ключу golem_user_preferences.
 * Применяет настройки через data-* атрибуты на <html>.
 */

const UserPreferences = (function() {
  'use strict';

  var STORAGE_KEY = 'golem_user_preferences';
  var HTML = document.documentElement;

  var PRESETS = {
    theme: {
      white: {
        label: 'Белая',
        vars: {
          '--bg-primary': '#ffffff',
          '--bg-secondary': '#fbfaf6',
          '--bg-tertiary': '#f1ece1',
          '--bg-card': '#ffffff',
          '--bg-dark': '#fbfaf6',
          '--bg-dark-hover': '#f1ece1',
          '--text-primary': '#221a10',
          '--text-secondary': '#5c5142',
          '--text-muted': '#8d8271',
          '--text-on-dark': '#3a2c1c',
          '--accent-gold': '#9a7420',
          '--border-light': '#e6dfd0',
          '--border-dark': '#cbbfa8',
          '--border-color': '#e6dfd0',
          '--header-bg': '#ffffff',
          '--header-text': '#221a10'
        }
      },
      brown: {
        label: 'Коричневая',
        vars: {
          '--bg-primary': '#3b2a18',
          '--bg-secondary': '#45321d',
          '--bg-tertiary': '#4f3a23',
          '--bg-card': '#402e1b',
          '--bg-dark': '#271a0d',
          '--bg-dark-hover': '#332413',
          '--text-primary': '#f3e9d6',
          '--text-secondary': '#d8c6a6',
          '--text-muted': '#b09b78',
          '--text-on-dark': '#f6efe0',
          '--accent-gold': '#d4a030',
          '--border-light': '#5c4826',
          '--border-dark': '#705831',
          '--border-color': '#5c4826',
          '--header-bg': '#1f1407',
          '--header-text': '#f3e9d6'
        }
      },
      dark: {
        label: 'Чёрная',
        vars: {
          '--bg-primary': '#100b06',
          '--bg-secondary': '#181006',
          '--bg-tertiary': '#221710',
          '--bg-card': '#140d06',
          '--bg-dark': '#090502',
          '--bg-dark-hover': '#150d06',
          '--text-primary': '#f2ead9',
          '--text-secondary': '#cdbda1',
          '--text-muted': '#9c8d74',
          '--text-on-dark': '#f6efe0',
          '--accent-gold': '#c89b3c',
          '--border-light': '#2e2315',
          '--border-dark': '#453525',
          '--border-color': '#2e2315',
          '--header-bg': '#060301',
          '--header-text': '#f2ead9'
        }
      }
    },
    fontSize: {
      compact: { label: 'Компактный', value: '14px' },
      standard: { label: 'Стандартный', value: '16px' },
      large: { label: 'Крупный', value: '18px' }
    },
    density: {
      compact: { label: 'Компактная' },
      standard: { label: 'Стандартная' },
      comfortable: { label: 'Просторная' }
    },
    contentWidth: {
      narrow: { label: 'Узкая', value: '800px' },
      standard: { label: 'Стандартная', value: '1100px' },
      wide: { label: 'Широкая', value: '1400px' }
    },
    motion: {
      full: { label: 'Полная' },
      reduced: { label: 'Минимальная' }
    },
    fontFamily: {
      'eb-garamond': { label: 'EB Garamond' },
      'cormorant': { label: 'Cormorant Garamond' },
      'system-serif': { label: 'Системный serif' },
      'mono': { label: 'Моноширинный' }
    }
  };

  function defaults(role) {
    return {
      role: role || 'guest',
      theme: 'white',
      fontSize: 'standard',
      density: 'standard',
      contentWidth: 'standard',
      motion: 'full',
      fontFamily: 'eb-garamond',
      startPage: 'dashboard',
      showBreadcrumbs: true
    };
  }

  function load() {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        var parsed = JSON.parse(saved);
        var base = defaults(parsed.role);
        Object.keys(base).forEach(function(k) {
          if (parsed[k] === undefined) parsed[k] = base[k];
        });
        return parsed;
      }
    } catch (e) {}
    return defaults('guest');
  }

  function save(prefs) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  }

  function escapeHtml(text) {
    var el = document.createElement('div');
    el.textContent = text == null ? '' : String(text);
    return el.innerHTML;
  }

  function roleLabel(role) {
    if (role === 'admin') return 'Администратор';
    if (role === 'researcher') return 'Исследователь';
    return 'Гость';
  }

  function apply(prefs) {
    if (!prefs) prefs = load();
    // Защита от устаревших сохранённых тем (parchment удалена): фолбэк — белая.
    var theme = PRESETS.theme[prefs.theme] ? prefs.theme : 'white';
    HTML.setAttribute('data-theme', theme);
    HTML.setAttribute('data-font-size', prefs.fontSize);
    HTML.setAttribute('data-density', prefs.density);
    HTML.setAttribute('data-content-width', prefs.contentWidth);
    HTML.setAttribute('data-motion', prefs.motion);
    HTML.setAttribute('data-font-family', prefs.fontFamily);

    var root = document.documentElement.style;
    root.setProperty('--user-font-size', PRESETS.fontSize[prefs.fontSize].value);
    root.setProperty('--user-content-width', PRESETS.contentWidth[prefs.contentWidth].value);

    var themeVars = PRESETS.theme[theme].vars;
    Object.keys(themeVars).forEach(function(varName) {
      root.setProperty(varName, themeVars[varName]);
    });

    if (prefs.motion === 'reduced') {
      HTML.setAttribute('data-reduced-motion', 'true');
    } else {
      HTML.removeAttribute('data-reduced-motion');
    }
  }

  function render(container, role) {
    var prefs = load();
    prefs.role = role;
    save(prefs);
    container.innerHTML = buildHTML(role);
    bindEvents(container, prefs, role);
    apply(prefs);
  }

  function buildHTML(role) {
    var prefs = load();
    var isResearcher = role === 'researcher';
    return '<div class="up-theme-container">' +
      '<div class="up-panel">' +
        '<div class="up-panel-header"><div>' +
            '<h1 class="up-title">' + (isResearcher ? 'Моё рабочее пространство' : 'Настройки отображения') + '</h1>' +
            '<p class="up-subtitle">' + (isResearcher ?
              'Персонализация интерфейса, навигации и обучения.' :
              'Выберите комфортное оформление для работы с платформой.') + '</p>' +
          '</div>' +
          '<div class="up-role-badge">' + escapeHtml(roleLabel(role)) + '</div>' +
        '</div>' +
        '<div class="up-grid">' +
          tabAppearance(prefs) +
          (isResearcher ? tabNavigation(prefs) : '') +
          (isResearcher ? tabLearning(prefs) : '') +
          tabData(prefs, role) +
        '</div>' +
      '</div>' +
    '</div>';
  }

  function tabAppearance(prefs) {
    return '<section class="up-card">' +
      '<h2 class="up-card-title">Внешний вид</h2>' +
      '<p class="up-card-hint">Тема оформления и типографика.</p>' +
      fieldSelect('theme', 'Тема', PRESETS.theme, prefs.theme) +
      fieldSelect('fontFamily', 'Шрифт', PRESETS.fontFamily, prefs.fontFamily) +
      fieldSelect('fontSize', 'Размер текста', PRESETS.fontSize, prefs.fontSize) +
      '<div class="up-field"><label class="up-label">Плотность</label>' +
        '<div class="up-segmented" data-key="density">' +
          segmentedOption('density', 'compact', PRESETS.density.compact.label, prefs.density) +
          segmentedOption('density', 'standard', PRESETS.density.standard.label, prefs.density) +
          segmentedOption('density', 'comfortable', PRESETS.density.comfortable.label, prefs.density) +
        '</div></div>' +
      '<div class="up-field"><label class="up-label">Ширина контента</label>' +
        '<div class="up-segmented" data-key="contentWidth">' +
          segmentedOption('contentWidth', 'narrow', PRESETS.contentWidth.narrow.label, prefs.contentWidth) +
          segmentedOption('contentWidth', 'standard', PRESETS.contentWidth.standard.label, prefs.contentWidth) +
          segmentedOption('contentWidth', 'wide', PRESETS.contentWidth.wide.label, prefs.contentWidth) +
        '</div></div>' +
      '<div class="up-field"><label class="up-label">Анимации</label>' +
        '<div class="up-segmented" data-key="motion">' +
          segmentedOption('motion', 'full', PRESETS.motion.full.label, prefs.motion) +
          segmentedOption('motion', 'reduced', PRESETS.motion.reduced.label, prefs.motion) +
        '</div></div>' +
    '</section>';
  }

  function tabNavigation(prefs) {
    return '<section class="up-card">' +
      '<h2 class="up-card-title">Навигация</h2>' +
      '<p class="up-card-hint">Стартовая страница и элементы интерфейса.</p>' +
      '<div class="up-field"><label class="up-label">Стартовая страница</label>' +
        '<select id="up-start-page" class="up-select">' +
          '<option value="dashboard"' + (prefs.startPage === 'dashboard' ? ' selected' : '') + '>Рабочий стол</option>' +
          '<option value="learn"' + (prefs.startPage === 'learn' ? ' selected' : '') + '>Обучение</option>' +
          '<option value="root-dictionary"' + (prefs.startPage === 'root-dictionary' ? ' selected' : '') + '>Корневой словарь</option>' +
          '<option value="paleo-linguistics"' + (prefs.startPage === 'paleo-linguistics' ? ' selected' : '') + '>Палео-лингвистика</option>' +
          '<option value="workbench"' + (prefs.startPage === 'workbench' ? ' selected' : '') + '>Мастерская</option>' +
        '</select></div>' +
      '<div class="up-field"><label class="up-label">Хлебные крошки</label>' +
        '<label class="up-toggle"><input type="checkbox" id="up-show-breadcrumbs"' + (prefs.showBreadcrumbs ? ' checked' : '') + '>' +
        '<span class="up-toggle-slider"></span><span class="up-toggle-label">' + (prefs.showBreadcrumbs ? 'Показаны' : 'Скрыты') + '</span></label></div>' +
    '</section>';
  }

  function tabLearning(prefs) {
    return '<section class="up-card">' +
      '<h2 class="up-card-title">Обучение</h2>' +
      '<p class="up-card-hint">Параметры интервального повторения.</p>' +
      '<div class="up-field"><label class="up-label">Новые карточки в день: <span id="up-daily-new-val">10</span></label>' +
        '<input type="range" id="up-daily-new" min="1" max="30" value="10" class="up-range"></div>' +
      '<div class="up-field"><label class="up-label">Повторений в день: <span id="up-daily-review-val">30</span></label>' +
        '<input type="range" id="up-daily-review" min="5" max="100" value="30" class="up-range"></div>' +
    '</section>';
  }

  function tabData(prefs, role) {
    return '<section class="up-card">' +
      '<h2 class="up-card-title">Данные</h2>' +
      '<p class="up-card-hint">Экспорт, импорт и сброс настроек.</p>' +
      '<div class="up-actions">' +
        '<button class="up-btn up-btn-secondary" id="up-export">Экспорт настроек</button>' +
        '<button class="up-btn up-btn-secondary" id="up-import">Импорт настроек</button>' +
        '<button class="up-btn up-btn-danger" id="up-reset">Сбросить настройки</button>' +
      '</div>' +
      '<input type="file" id="up-import-file" accept=".json" style="display:none;">' +
      '<div id="up-notice" class="up-notice" style="display:none;"></div>' +
    '</section>';
  }

  function fieldSelect(key, label, options, current) {
    var opts = Object.keys(options).map(function(k) {
      return '<option value="' + k + '"' + (current === k ? ' selected' : '') + '>' + escapeHtml(options[k].label) + '</option>';
    }).join('');
    return '<div class="up-field"><label class="up-label">' + escapeHtml(label) + '</label>' +
      '<select class="up-select" data-key="' + key + '">' + opts + '</select></div>';
  }

  function segmentedOption(group, value, label, current) {
    return '<button class="up-segment' + (current === value ? ' active' : '') + '" data-group="' + group + '" data-value="' + value + '">' + escapeHtml(label) + '</button>';
  }

  function bindEvents(container, prefs, role) {
    container.querySelectorAll('.up-select').forEach(function(sel) {
      sel.addEventListener('change', function() {
        prefs[sel.getAttribute('data-key')] = sel.value;
        save(prefs);
        apply(prefs);
      });
    });
    container.querySelectorAll('.up-segment').forEach(function(seg) {
      seg.addEventListener('click', function() {
        var group = seg.getAttribute('data-group');
        var value = seg.getAttribute('data-value');
        seg.parentElement.querySelectorAll('.up-segment').forEach(function(s) { s.classList.remove('active'); });
        seg.classList.add('active');
        prefs[group] = value;
        save(prefs);
        apply(prefs);
      });
    });
    var breadToggle = container.querySelector('#up-show-breadcrumbs');
    if (breadToggle) {
      breadToggle.addEventListener('change', function() {
        prefs.showBreadcrumbs = breadToggle.checked;
        var lbl = breadToggle.parentElement.querySelector('.up-toggle-label');
        if (lbl) lbl.textContent = prefs.showBreadcrumbs ? 'Показаны' : 'Скрыты';
        save(prefs);
      });
    }
    var exportBtn = container.querySelector('#up-export');
    if (exportBtn) {
      exportBtn.addEventListener('click', function() {
        var blob = new Blob([JSON.stringify(prefs, null, 2)], { type: 'application/json' });
        var a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'golem-user-preferences.json';
        a.click();
        showNotice('Настройки экспортированы.', false);
      });
    }
    var importBtn = container.querySelector('#up-import');
    var importFile = container.querySelector('#up-import-file');
    if (importBtn && importFile) {
      importBtn.addEventListener('click', function() { importFile.click(); });
      importFile.addEventListener('change', function() {
        var file = importFile.files[0];
        if (!file) return;
        var reader = new FileReader();
        reader.onload = function(e) {
          try {
            var imp = JSON.parse(e.target.result);
            Object.keys(imp).forEach(function(k) { if (k !== 'role') prefs[k] = imp[k]; });
            save(prefs);
            apply(prefs);
            render(container, prefs.role);
            showNotice('Настройки импортированы.', false);
          } catch (err) { showNotice('Ошибка импорта: ' + err.message, true); }
        };
        reader.readAsText(file);
      });
    }
    var resetBtn = container.querySelector('#up-reset');
    if (resetBtn) {
      resetBtn.addEventListener('click', function() {
        if (!confirm('Сбросить все настройки?')) return;
        var r = prefs.role;
        localStorage.removeItem(STORAGE_KEY);
        prefs = defaults(r);
        save(prefs);
        apply(prefs);
        render(container, r);
        showNotice('Настройки сброшены.', false);
      });
    }
  }

  function showNotice(message, isError) {
    var notice = document.getElementById('up-notice');
    if (!notice) return;
    notice.textContent = message;
    notice.className = 'up-notice ' + (isError ? 'up-notice-error' : 'up-notice-success');
    notice.style.display = 'block';
    setTimeout(function() { notice.style.display = 'none'; }, 3000);
  }

  function init() {
    apply(load());
  }

  return {
    load: load,
    save: save,
    apply: apply,
    render: render,
    init: init,
    roleLabel: roleLabel,
    PRESETS: PRESETS,
    defaults: defaults,
    escapeHtml: escapeHtml
  };
})();

window.UserPreferences = UserPreferences;