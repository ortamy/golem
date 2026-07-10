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

  // ===== ОБРАБОТКА ХЕША =====
  function handleHash() {
    const hash = window.location.hash.replace('#', '') || 'dashboard';
    
    if (modules[hash]) {
      showModule(hash);
    } else if (hash === 'dashboard') {
      showModule('dashboard');
    }
  }

  // ===== НАВИГАЦИЯ =====
  function navigate(moduleId) {
    window.location.hash = moduleId;
  }

  // ===== ПОКАЗ МОДУЛЯ =====
  function showModule(moduleId) {
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

    // Колбэк
    if (onModuleChange) {
      onModuleChange(moduleId);
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
    current: function() { return currentModule; },
    onChange: onChange
  };
})();