/**
 * admin-editor.js — client-side admin panel for adding researches.
 * Password gate is a UI convenience only, not real access control:
 * anyone can read this file's source, so it does not stop a determined visitor.
 */
const AdminEditor = (function() {
  'use strict';

  var STORAGE_KEY = 'golem_researches';
  var SESSION_KEY = 'golem_admin_session';

  function isAuthenticated() {
    if (window.AccessGate) return AccessGate.isAdmin();
    return sessionStorage.getItem(SESSION_KEY) === '1';
  }

  function init() {
    render();
  }

  function render() {
    var container = document.getElementById('admin');
    if (!container) return;
    if (!isAuthenticated()) {
      renderLogin(container);
    } else {
      renderEditor(container);
    }
  }

  function renderLogin(container) {
    container.innerHTML =
      '<div class="admin-login-wrap">' +
        '<div class="admin-login-card">' +
          '<h1 class="admin-title">Админ-панель</h1>' +
          '<p class="admin-subtitle">Доступ только для автора проекта.</p>' +
          '<input type="password" id="admin-pass" class="admin-input" placeholder="Пароль" autocomplete="off">' +
          '<button class="admin-btn admin-btn-primary" id="admin-login-btn">Войти</button>' +
          '<div id="admin-login-error" class="admin-error" style="display:none;">Неверный пароль.</div>' +
        '</div>' +
      '</div>';

    var btn = document.getElementById('admin-login-btn');
    var input = document.getElementById('admin-pass');
    btn.addEventListener('click', tryLogin);
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') tryLogin();
    });
    input.focus();
  }

  function tryLogin() {
    var input = document.getElementById('admin-pass');
    var error = document.getElementById('admin-login-error');
    if (!input) return;
    var expected = window.AccessGate ? AccessGate.currentPassword() : 'Golem2026';
    if (input.value === expected) {
      sessionStorage.setItem(SESSION_KEY, '1');
      render();
    } else {
      error.style.display = 'block';
      input.value = '';
      input.focus();
    }
  }

  function logout() {
    if (window.AccessGate) {
      AccessGate.logout();
      return;
    }
    sessionStorage.removeItem(SESSION_KEY);
    render();
  }

  function loadResearches() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch (e) {
      return [];
    }
  }

  function saveResearches(list) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  }

  function renderEditor(container) {
    container.innerHTML =
      '<div class="admin-panel">' +
        '<div class="admin-panel-header">' +
          '<h1 class="admin-title">Админ-панель — новое исследование</h1>' +
          '<button class="admin-btn admin-btn-ghost" id="admin-logout-btn">Выйти</button>' +
        '</div>' +
        '<div class="admin-field">' +
          '<label class="admin-label" for="admin-field-title">Заголовок исследования</label>' +
          '<input type="text" id="admin-field-title" class="admin-input" placeholder="Например: חסד — разоблачение подмены «милость»">' +
        '</div>' +
        '<div class="admin-field">' +
          '<label class="admin-label" for="admin-field-body">Текст исследования (Markdown / HTML)</label>' +
          '<textarea id="admin-field-body" class="admin-textarea" rows="16" placeholder="## Заголовок&#10;&#10;Текст исследования..."></textarea>' +
        '</div>' +
        '<div class="admin-field">' +
          '<label class="admin-label" for="admin-field-image">Ссылка на изображение (опционально)</label>' +
          '<input type="text" id="admin-field-image" class="admin-input" placeholder="https://...">' +
        '</div>' +
        '<div class="admin-actions">' +
          '<button class="admin-btn admin-btn-primary" id="admin-save-btn">Сохранить локально</button>' +
          '<button class="admin-btn admin-btn-secondary" id="admin-export-btn">Экспортировать JSON</button>' +
        '</div>' +
        '<div id="admin-notice" class="admin-notice" style="display:none;"></div>' +
        '<div class="admin-list-section">' +
          '<h2 class="admin-list-title">Сохранённые исследования</h2>' +
          '<div id="admin-list"></div>' +
        '</div>' +
      '</div>';

    document.getElementById('admin-logout-btn').addEventListener('click', logout);
    document.getElementById('admin-save-btn').addEventListener('click', saveCurrent);
    document.getElementById('admin-export-btn').addEventListener('click', exportJSON);
    renderList();
  }

  function showNotice(msg, isError) {
    var notice = document.getElementById('admin-notice');
    if (!notice) return;
    notice.className = 'admin-notice' + (isError ? ' admin-notice-error' : ' admin-notice-success');
    notice.textContent = msg;
    notice.style.display = 'block';
    setTimeout(function() { notice.style.display = 'none'; }, 3000);
  }

  function saveCurrent() {
    var title = document.getElementById('admin-field-title').value.trim();
    var body = document.getElementById('admin-field-body').value.trim();
    var image = document.getElementById('admin-field-image').value.trim();

    if (!title || !body) {
      showNotice('Заполните заголовок и текст исследования.', true);
      return;
    }

    var list = loadResearches();
    list.push({
      id: 'r' + Date.now(),
      title: title,
      body: body,
      image: image,
      createdAt: new Date().toISOString()
    });
    saveResearches(list);

    document.getElementById('admin-field-title').value = '';
    document.getElementById('admin-field-body').value = '';
    document.getElementById('admin-field-image').value = '';

    showNotice('Исследование сохранено локально.', false);
    renderList();
  }

  function exportJSON() {
    var list = loadResearches();
    var blob = new Blob([JSON.stringify(list, null, 2)], { type: 'application/json;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'researches.json';
    a.click();
    URL.revokeObjectURL(a.href);
    showNotice('Файл researches.json скачан.', false);
  }

  function deleteResearch(id) {
    var list = loadResearches().filter(function(r) { return r.id !== id; });
    saveResearches(list);
    renderList();
  }

  function renderList() {
    var container = document.getElementById('admin-list');
    if (!container) return;
    var list = loadResearches();
    if (!list.length) {
      container.innerHTML = '<div class="admin-empty">Пока нет сохранённых исследований.</div>';
      return;
    }
    var html = '';
    list.slice().reverse().forEach(function(r) {
      html += '<div class="admin-list-item">' +
        '<div class="admin-list-item-title">' + escapeHtml(r.title) + '</div>' +
        '<div class="admin-list-item-date">' + new Date(r.createdAt).toLocaleString('ru-RU') + '</div>' +
        '<button class="admin-btn admin-btn-danger admin-btn-sm" data-delete-id="' + escapeHtml(r.id) + '">Удалить</button>' +
      '</div>';
    });
    container.innerHTML = html;
    container.querySelectorAll('[data-delete-id]').forEach(function(btn) {
      btn.addEventListener('click', function() {
        deleteResearch(btn.getAttribute('data-delete-id'));
      });
    });
  }

  window.AdminEditor = { init: init };
  return window.AdminEditor;
})();
