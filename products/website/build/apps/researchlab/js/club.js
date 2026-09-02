/**
 * club.js — заглушка модуля «Палео-клуб».
 * Показывает hero, буллеты и форму waitlist.
 * Данные сохраняются через адаптер (Supabase или localStorage).
 */

const ClubModule = (function() {
  'use strict';

  var STORAGE_KEY = 'golem_waitlist';

  function escapeHtml(text) {
    var el = document.createElement('div');
    el.textContent = text == null ? '' : String(text);
    return el.innerHTML;
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function loadWaitlist() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch (e) {
      return [];
    }
  }

  function saveWaitlist(list) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  }

  function alreadyExists(email) {
    var list = loadWaitlist();
    return list.some(function(item) {
      return item.email.toLowerCase() === email.toLowerCase();
    });
  }

  function addToWaitlist(email) {
    return new Promise(function(resolve) {
      if (!isValidEmail(email)) {
        resolve({ ok: false, error: 'Введите корректный email.' });
        return;
      }
      if (alreadyExists(email)) {
        resolve({ ok: false, duplicate: true, message: 'Вы уже в списке.' });
        return;
      }

      var list = loadWaitlist();
      list.push({ email: email, created_at: new Date().toISOString() });
      saveWaitlist(list);

      if (window.supabaseClient) {
        window.supabaseClient.from('waitlist').insert({ email: email }).then(function(res) {
          resolve({ ok: true, message: 'Вы в списке. Код придёт на почту.' });
        }).catch(function() {
          resolve({ ok: true, message: 'Вы в списке. Код придёт на почту.' });
        });
      } else {
        resolve({ ok: true, message: 'Вы в списке. Код придёт на почту.' });
      }
    });
  }

  function render(container) {
    container.innerHTML = buildHTML();
    bindEvents(container);
  }

  function buildHTML() {
    return '<div class="club-content">' +
      '<div class="club-features">' +
        '<div class="club-feature"><span class="club-feature-icon">✦</span><div><strong>Буква и корень дня</strong><p>Ежедневная порция палео-образного мышления.</p></div></div>' +
        '<div class="club-feature"><span class="club-feature-icon">✦</span><div><strong>Живые сессии</strong><p>Разборы текстов и совместные исследования.</p></div></div>' +
        '<div class="club-feature"><span class="club-feature-icon">✦</span><div><strong>Круги</strong><p>Малые группы для практики и обмена находками.</p></div></div>' +
        '<div class="club-feature"><span class="club-feature-icon">✦</span><div><strong>Делимся исследованиями</strong><p>Публикации и обсуждения внутри клуба.</p></div></div>' +
      '</div>' +
      '<div class="club-waitlist">' +
        '<h2>Сообщить об открытии</h2>' +
        '<p class="club-waitlist-hint">Оставьте email — мы пришлём код для входа в день запуска.</p>' +
        '<div class="club-form">' +
          '<input type="email" id="club-email" class="club-input" placeholder="your@email.com">' +
          '<button class="club-btn" id="club-submit">Сообщить об открытии</button>' +
        '</div>' +
        '<div id="club-notice" class="club-notice" style="display:none;"></div>' +
      '</div>' +
    '</div>';
  }

  function bindEvents(container) {
    var submit = container.querySelector('#club-submit');
    var emailInput = container.querySelector('#club-email');
    var notice = container.querySelector('#club-notice');

    function showNotice(message, isError) {
      notice.textContent = message;
      notice.className = 'club-notice ' + (isError ? 'club-notice-error' : 'club-notice-success');
      notice.style.display = 'block';
      setTimeout(function() { notice.style.display = 'none'; }, 4000);
    }

    function submitForm() {
      var email = emailInput.value.trim();
      addToWaitlist(email).then(function(res) {
        if (res.ok) {
          showNotice(res.message, false);
          emailInput.value = '';
        } else if (res.duplicate) {
          showNotice('Вы уже в списке.', false);
        } else {
          showNotice(res.error || 'Ошибка.', true);
        }
      });
    }

    if (submit) {
      submit.addEventListener('click', submitForm);
    }
    if (emailInput) {
      emailInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') submitForm();
      });
    }
  }

  return {
    render: render,
    addToWaitlist: addToWaitlist
  };
})();

window.ClubModule = ClubModule;
