/**
 * router.js — SPA Router for Golem Research Lab
 * 
 * Переключение между модулями без перезагрузки страницы
 * Использует hash-based routing: #root-dictionary, #religionism-checker, и т.д.
 */

const LabRouter = (function() {
  'use strict';

  // ===== СОСТОЯНИЕ =====
  let currentModule = 'dashboard';
  let modules = {};
  let onModuleChange = null;

  // ===== ИНИЦИАЛИЗАЦИЯ =====
  function init() {
    // Регистрируем все модули
    document.querySelectorAll('.module').forEach(function(el) {
      const id = el.id;
      if (id) {
        modules[id] = el;
      }
    });

    // Слушаем hashchange
    window.addEventListener('hashchange', handleHash);
    window.addEventListener('load', function() {
      // Если есть хеш при загрузке — переходим
      setTimeout(handleHash, 100);
    });

    // Обработка кликов по sidebar-item
    document.querySelectorAll('.sidebar-item').forEach(function(item) {
      item.addEventListener('click', function(e) {
        const module = item.dataset.module;
        if (module) {
          e.preventDefault();
          navigate(module);
        }
      });
    });

    console.log('[Router] Инициализирован. Модулей:', Object.keys(modules).length);
  }

  // ===== РАЗБОР ХЕША С ПАРАМЕТРАМИ =====
  // Формат: #<module>[/<sub1>/<sub2>...][?key=value&...]
  function parseHash() {
    var raw = window.location.hash.replace('#', '') || 'dashboard';
    var queryIndex = raw.indexOf('?');
    var path = queryIndex === -1 ? raw : raw.substring(0, queryIndex);
    var queryString = queryIndex === -1 ? '' : raw.substring(queryIndex + 1);
    var segments = path.split('/').filter(function(s) { return s.length > 0; });
    var params = {};
    queryString.split('&').forEach(function(pair) {
      if (!pair) return;
      var eq = pair.indexOf('=');
      var key = eq === -1 ? pair : pair.substring(0, eq);
      var value = eq === -1 ? '' : pair.substring(eq + 1);
      if (key) params[decodeURIComponent(key)] = decodeURIComponent(value || '');
    });
    return { module: segments[0] || 'dashboard', segments: segments, params: params, raw: raw };
  }

  // ===== ОБРАБОТКА ХЕША =====
  function handleHash() {
    var parsed = parseHash();
    var hash = parsed.module;

    // #settings is an alias for #admin-settings
    if (hash === 'settings') {
      navigate('admin-settings');
      return;
    }

    // #research-library — устаревший маршрут, объединён с #researches
    if (hash === 'research-library') {
      navigate('researches');
      return;
    }

    // #prompt-generator — сборщик промптов исследователя
    if (hash === 'prompt-generator') {
      showModule('prompt-generator', parsed);
      return;
    }

    if (modules[hash]) {
      showModule(hash, parsed);
    } else if (hash === 'exposure-editor') {
      // Dynamic module — будет создан в showModule
      showModule(hash, parsed);
    } else if (hash === 'dashboard') {
      showModule('dashboard', parsed);
    }
  }

  // ===== НАВИГАЦИЯ =====
  function navigate(moduleId, segments, params) {
    var hash = moduleId;
    if (segments && segments.length) hash += '/' + segments.join('/');
    if (params) {
      var query = Object.keys(params)
        .filter(function(k) { return params[k] !== '' && params[k] != null; })
        .map(function(k) { return encodeURIComponent(k) + '=' + encodeURIComponent(params[k]); })
        .join('&');
      if (query) hash += '?' + query;
    }
    window.location.hash = hash;
  }

  // ===== ПОКАЗ МОДУЛЯ =====
  function showModule(moduleId, parsed) {
    // Создаём контейнер для exposure-editor если его ещё нет
    if (moduleId === 'exposure-editor' && !modules['exposure-editor']) {
      const editor = document.createElement('div');
      editor.id = 'exposure-editor';
      editor.className = 'module';
      document.getElementById('labContent').appendChild(editor);
      modules['exposure-editor'] = editor;
    }

    // Скрываем все
    Object.keys(modules).forEach(function(id) {
      modules[id].classList.remove('active');
    });

    // Показываем dashboard если нужно
    const dashboard = document.getElementById('dashboard');
    if (dashboard) {
      dashboard.classList.remove('active');
    }

    // Показываем целевой модуль
    if (moduleId === 'dashboard') {
      if (dashboard) dashboard.classList.add('active');
    } else if (modules[moduleId]) {
      modules[moduleId].classList.add('active');
    } else {
      // Если модуль не найден — показываем dashboard
      if (dashboard) dashboard.classList.add('active');
      moduleId = 'dashboard';
    }

    // Обновляем sidebar
    document.querySelectorAll('.sidebar-item').forEach(function(item) {
      const isActive = item.dataset.module === moduleId ||
                       (!item.dataset.module && moduleId === 'dashboard');
      item.classList.toggle('active', isActive);
    });

    currentModule = moduleId;

    // Инициализация exposure-editor при активации
    if (moduleId === 'exposure-editor' && window.ExposureEditor) {
      const editorEl = document.getElementById('exposure-editor');
      if (editorEl) {
        ExposureEditor.init(editorEl);
      }
    }

    // Колбэк
    if (onModuleChange) {
      onModuleChange(moduleId, parsed);
    }

    // Прокрутка вверх
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // ===== РЕГИСТРАЦИЯ КОЛБЭКА =====
  function onChange(callback) {
    onModuleChange = callback;
  }

  // ===== ПУБЛИЧНЫЙ API =====
  return {
    init: init,
    navigate: navigate,
    show: showModule,
    parseHash: parseHash,
    current: function() { return currentModule; },
    onChange: onChange
  };
})();
