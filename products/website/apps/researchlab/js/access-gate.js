/**
 * access-gate.js — entry gate for the research lab: admin login or guest mode.
 * This is a UX split (admin vs guest view), not real access control:
 * the password and logic are visible in this file's source to anyone.
 */
const AccessGate = (function() {
  'use strict';

  var ADMIN_LOGIN = 'admin';
  var DEFAULT_PASSWORD = 'Golem2026';
  var SESSION_ADMIN_KEY = 'golem_admin_session';
  var SESSION_GUEST_KEY = 'golem_guest_session';
  var PASSWORD_OVERRIDE_KEY = 'golem_admin_password_override';
  var CONFIG_PATH = 'data/lab-config.json';

  var config = null;

  function isAdmin() {
    return sessionStorage.getItem(SESSION_ADMIN_KEY) === '1';
  }

  function isGuest() {
    return sessionStorage.getItem(SESSION_GUEST_KEY) === '1';
  }

  function hasSession() {
    return isAdmin() || isGuest();
  }

  function currentPassword() {
    return localStorage.getItem(PASSWORD_OVERRIDE_KEY) || DEFAULT_PASSWORD;
  }

  function setPasswordOverride(pass) {
    localStorage.setItem(PASSWORD_OVERRIDE_KEY, pass);
  }

  function loadConfig() {
    return fetch(CONFIG_PATH)
      .then(function(r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .catch(function() {
        return { accentColor: '#b8860b', defaultModule: 'dashboard', hiddenSectionsForGuests: [], guestTokens: [] };
      })
      .then(function(data) {
        config = data;
        return data;
      });
  }

  function getConfig() {
    return config;
  }

  function checkTokenInHash() {
    var match = window.location.hash.match(/access=([^&]+)/);
    if (!match || !config) return false;
    var token = decodeURIComponent(match[1]);
    var found = (config.guestTokens || []).some(function(t) { return t.token === token; });
    if (found) {
      sessionStorage.setItem(SESSION_GUEST_KEY, '1');
      return true;
    }
    return false;
  }

  function init(onReady) {
    loadConfig().then(function() {
      if (checkTokenInHash()) {
        history.replaceState(null, '', window.location.pathname + window.location.search);
      }
      if (hasSession()) {
        onReady(isAdmin() ? 'admin' : 'guest');
      } else {
        renderGate(onReady);
      }
    });
  }

  function renderGate(onReady) {
    var overlay = document.createElement('div');
    overlay.id = 'access-gate-overlay';
    overlay.className = 'gate-overlay';
    overlay.innerHTML =
      '<div class="gate-card">' +
        '<div class="gate-logo">ГОЛЕМ</div>' +
        '<h1 class="gate-title">Исследовательская лаборатория</h1>' +
        '<p class="gate-subtitle">Войдите как администратор или продолжите в гостевом режиме.</p>' +
        '<label class="gate-label" for="gate-login">Логин</label>' +
        '<input type="text" id="gate-login" class="admin-input" placeholder="admin" autocomplete="off">' +
        '<label class="gate-label" for="gate-pass">Пароль</label>' +
        '<input type="password" id="gate-pass" class="admin-input" placeholder="Пароль" autocomplete="off">' +
        '<button class="admin-btn admin-btn-primary gate-btn" id="gate-login-btn">Войти</button>' +
        '<div id="gate-error" class="admin-error" style="display:none;">Неверный логин или пароль.</div>' +
        '<div class="gate-divider">или</div>' +
        '<button class="admin-btn admin-btn-secondary gate-btn" id="gate-guest-btn">Гостевой режим</button>' +
      '</div>';
    document.body.appendChild(overlay);

    var loginInput = document.getElementById('gate-login');
    var passInput = document.getElementById('gate-pass');
    var errorBox = document.getElementById('gate-error');

    function tryLogin() {
      var login = loginInput.value.trim();
      var pass = passInput.value;
      if (login === ADMIN_LOGIN && pass === currentPassword()) {
        sessionStorage.setItem(SESSION_ADMIN_KEY, '1');
        overlay.remove();
        onReady('admin');
      } else {
        errorBox.style.display = 'block';
        passInput.value = '';
        passInput.focus();
      }
    }

    document.getElementById('gate-login-btn').addEventListener('click', tryLogin);
    document.getElementById('gate-guest-btn').addEventListener('click', function() {
      sessionStorage.setItem(SESSION_GUEST_KEY, '1');
      overlay.remove();
      onReady('guest');
    });
    [loginInput, passInput].forEach(function(input) {
      input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') tryLogin();
      });
    });
    loginInput.focus();
  }

  function logout() {
    sessionStorage.removeItem(SESSION_ADMIN_KEY);
    sessionStorage.removeItem(SESSION_GUEST_KEY);
    window.location.reload();
  }

  window.AccessGate = {
    init: init,
    isAdmin: isAdmin,
    isGuest: isGuest,
    getConfig: getConfig,
    currentPassword: currentPassword,
    setPasswordOverride: setPasswordOverride,
    logout: logout
  };
  return window.AccessGate;
})();
