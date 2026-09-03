/**
 * club.js — Палео-клуб: лента исследований, деталь, комментарии.
 * Данные через ClubData (MOCK или Supabase).
 */

const ClubModule = (function() {
  'use strict';

  var STORAGE_KEY = 'golem_waitlist';
  var currentCardId = null;

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

  function getRole() {
    return (window.AccessGate && AccessGate.getRole) ? AccessGate.getRole() : 'guest';
  }

  function render(container) {
    if (currentCardId) {
      renderDetail(container, currentCardId);
    } else {
      renderFeed(container);
    }
  }

  function renderFeed(container) {
    if (!window.ClubData) {
      container.innerHTML = '<div class="lab-alert">Загрузка данных...</div>';
      return;
    }
    Promise.all([ClubData.getCards(), ClubData.getWordOfDay()]).then(function(results) {
      var cards = results[0];
      var wordOfDay = results[1];
      container.innerHTML = buildFeedHTML(cards, wordOfDay);
      bindFeedEvents(container);
    });
  }

  function buildFeedHTML(cards, wordOfDay) {
    var role = getRole();
    var wordHtml = '';
    if (wordOfDay) {
      var paleoStr = (wordOfDay.paleo || []).join('');
      wordHtml = '<div class="club-word">' +
        '<div class="club-word-paleo">' + escapeHtml(paleoStr) + '</div>' +
        '<div class="club-word-info">' +
          '<strong>' + escapeHtml(wordOfDay.hebrew) + ' · ' + escapeHtml(wordOfDay.translit) + '</strong>' +
          '<p>' + escapeHtml(wordOfDay.gloss) + '</p>' +
        '</div>' +
        '<div class="club-word-actions">' +
          '<a class="lab-btn lab-btn-primary lab-btn-sm" href="#learn/paleo-trainer?word=' + encodeURIComponent(wordOfDay.translit || wordOfDay.hebrew || '') + '">Собрать →</a>' +
          '<button class="lab-btn lab-btn-secondary lab-btn-sm club-word-discuss" data-id="' + escapeHtml('shabbat') + '">Обсудить</button>' +
        '</div>' +
      '</div>';
    }

    var cardsHtml = cards.map(function(card) {
      var typeLabels = { word: 'Слово', state: 'Состояние', board: 'Доска', verse: 'Стих' };
      var participants = card.participants || [];
      return '<article class="club-card" data-id="' + escapeHtml(card.id) + '">' +
        '<div class="club-card-head">' +
          '<span class="club-card-type type-' + (card.type || 'word') + '">' + (typeLabels[card.type] || card.type) + '</span>' +
          '<span class="club-card-ref">' + escapeHtml(card.ref) + '</span>' +
        '</div>' +
        '<h3 class="club-card-title">' + escapeHtml(card.title) + '</h3>' +
        '<p class="club-card-synthesis">' + escapeHtml(card.synthesis) + '</p>' +
        '<div class="club-card-foot">' +
          renderAvatarStack(participants, 5) +
          '<span class="club-card-meta">· ' + (card.posts_count || 0) + ' постов · эмет: ' + (card.emet || 0) + ' · вопрос: ' + (card.questions || 0) + '</span>' +
        '</div>' +
        '<div class="club-card-actions">' +
      '<a class="lab-btn lab-btn-secondary lab-btn-sm" href="' + attachmentHref(card.attachment) + '">Открыть в модуле ↗</a>' +
          '<button class="lab-btn lab-btn-secondary lab-btn-sm club-join" data-id="' + escapeHtml(card.id) + '">Вступить</button>' +
        '</div>' +
      '</article>';
    }).join('');

    var sidePanel = buildSidePanel(role);

    return clubHeader() + '<div class="club-feed">' +
      '<div class="club-main">' +
        wordHtml +
        '<div class="club-cards">' + cardsHtml + '</div>' +
      '</div>' +
      '<aside class="club-side">' + sidePanel + '</aside>' +
    '</div>';
  }

  function buildSidePanel(role) {
    var waitlistHtml = '';
    if (role === 'guest') {
      waitlistHtml = '<div class="club-waitlist">' +
        '<h3>Сообщить об открытии</h3>' +
        '<p>Оставьте email — мы пришлём код для входа.</p>' +
        '<div class="club-form">' +
          '<input type="email" id="club-email" class="club-input" placeholder="your@email.com">' +
          '<button class="club-btn" id="club-submit">Сообщить</button>' +
        '</div>' +
        '<div id="club-notice" class="club-notice" style="display:none;"></div>' +
      '</div>';
    }
    return '<div class="club-side-card">' +
      '<h3>Сейчас в клубе</h3>' +
      renderAvatarStack(ClubData.MOCK.profiles, 5) +
      '<p class="club-side-stub">Исследователи онлайн: 6</p>' +
    '</div>' +
    '<div class="club-side-card">' +
      '<h3>Ближайшая сессия</h3>' +
      '<p class="club-side-stub">Скоро анонс</p>' +
    '</div>' +
    '<div class="club-side-card">' +
      '<h3>Мои круги</h3>' +
      '<p class="club-side-stub">—</p>' +
    '</div>' +
    waitlistHtml;
  }

  function renderDetail(container, cardId) {
    if (!window.ClubData) {
      container.innerHTML = '<div class="lab-alert">Загрузка...</div>';
      return;
    }
    Promise.all([ClubData.getCard(cardId), ClubData.getComments(cardId)]).then(function(results) {
      var card = results[0];
      var comments = results[1];
      if (!card) {
        container.innerHTML = '<div class="lab-alert">Исследование не найдено.</div>';
        return;
      }
      currentCardId = cardId;
      container.innerHTML = buildDetailHTML(card, comments);
      bindDetailEvents(container);
    });
  }

  function buildDetailHTML(card, comments) {
    var role = getRole();
    var typeLabels = { word: 'Слово', state: 'Состояние', board: 'Доска', verse: 'Стих' };
    var participants = card.participants || [];

    var commentsHtml = comments.map(function(c) {
      var author = (window.ClubData && window.ClubData.getProfile) ? window.ClubData.getProfile(c.author) : { handle: '?', initial: '?', color: '#999' };
      var attachHtml = c.attachment ? '<a class="club-comment-attach" href="' + attachmentHref(c.attachment) + '">📎 ' + escapeHtml(c.attachment.label) + ' ↗</a>' : '';
      var reactions = role !== 'guest' ? '<div class="club-reactions">' +
        '<button class="club-react" data-type="emet" data-id="' + c.id + '">эмет (' + (c.emet || 0) + ')</button>' +
        '<button class="club-react" data-type="question" data-id="' + c.id + '">вопрос (' + (c.questions || 0) + ')</button>' +
      '</div>' : '';
      return '<div class="club-comment">' +
        '<button type="button" class="avatar-circle sm" data-profile="' + (c.author || 0) + '" style="background:' + (author.color || '#999') + ';" title="Профиль ' + escapeHtml(author.handle) + '">' + (author.initial || '?') + '</button>' +
        '<div class="club-comment-body">' +
          '<strong>' + escapeHtml(author.handle) + '</strong>' +
          '<p>' + escapeHtml(c.body) + '</p>' +
          attachHtml +
          reactions +
        '</div>' +
      '</div>';
    }).join('');

    var composerHtml = role !== 'guest' ? '<div class="club-composer">' +
      '<textarea id="club-comment-text" class="club-textarea" placeholder="Ваш комментарий..."></textarea>' +
      '<div class="club-composer-actions">' +
        '<button class="lab-btn lab-btn-secondary lab-btn-sm" id="club-attach" type="button">📎 Прикрепить</button>' +
        '<button class="lab-btn lab-btn-primary lab-btn-sm" id="club-publish">Опубликовать</button>' +
      '</div>' +
      '<div id="club-attachment-picker" class="club-attachment-picker" hidden>' +
        '<button type="button" data-attachment="verse">Стих</button>' +
        '<button type="button" data-attachment="word">Слово</button>' +
        '<button type="button" data-attachment="board">Доска</button>' +
        '<button type="button" data-attachment="state">Состояние</button>' +
        '<button type="button" data-attachment="search">Поиск</button>' +
      '</div>' +
    '</div>' : '<div class="club-guest-hint">Войдите, чтобы участвовать в обсуждении.</div>';

    var attachHtml = card.attachment ? '<div class="club-attachment">' +
      '<span class="club-attach-label">' + escapeHtml(card.attachment.label) + '</span>' +
      '<span class="club-attachment-confidence">Уверенность: ' + escapeHtml(card.confidence || 'рабочая карта') + '</span>' +
      '<p class="club-attachment-synthesis">' + escapeHtml(card.synthesis) + '</p>' +
      '<a class="lab-btn lab-btn-secondary lab-btn-sm" href="' + attachmentHref(card.attachment) + '">Открыть в модуле ↗</a>' +
    '</div>' : '';

    return clubHeader() + '<div class="club-detail">' +
      '<button class="club-back" id="club-back">← Назад</button>' +
      '<div class="club-detail-head">' +
        '<span class="club-card-type type-' + (card.type || 'word') + '">' + (typeLabels[card.type] || card.type) + '</span>' +
        '<h2>' + escapeHtml(card.title) + '</h2>' +
        '<p>' + escapeHtml(card.synthesis) + '</p>' +
        renderAvatarStack(participants, 5) +
        '<span class="club-participants-count">= ' + participants.length + ' участников</span>' +
      '</div>' +
      attachHtml +
      '<div class="club-comments">' + commentsHtml + '</div>' +
      composerHtml +
    '</div>';
  }

  function bindFeedEvents(container) {
    var cards = container.querySelectorAll('.club-card');
    cards.forEach(function(card) {
      card.addEventListener('click', function(e) {
        if (e.target.closest('a') || e.target.closest('button')) return;
        var id = card.getAttribute('data-id');
        if (id && window.LabRouter) {
          window.LabRouter.navigate('club', [id]);
        }
      });
    });
    container.querySelectorAll('.club-join').forEach(function(button) {
      button.addEventListener('click', function() {
        button.textContent = 'Вы в круге';
        button.disabled = true;
      });
    });
    bindAvatarProfiles(container);
    bindWaitlistEvents(container);
  }

  function clubHeader() {
    return '<header class="club-hero" aria-labelledby="club-title">' +
      '<p class="lab-hero__kicker">ГОЛЕМ · КЛУБ · СВИВА ИССЛЕДОВАТЕЛЕЙ</p>' +
      '<h1 class="club-hero-title" id="club-title">Палео-клуб</h1>' +
      '<span class="club-hero-badge">СКОРО</span>' +
      '<p class="club-hero-subtitle">Живая община исследователей: буква и корень дня, совместные разборы и круги практики.</p>' +
    '</header>';
  }

  function bindDetailEvents(container) {
    var back = container.querySelector('#club-back');
    if (back) {
      back.addEventListener('click', function() {
        currentCardId = null;
        if (window.LabRouter) window.LabRouter.navigate('club');
      });
    }
    container.querySelectorAll('[data-attachment]').forEach(function(button) {
      button.addEventListener('click', function() {
        var picker = container.querySelector('#club-attachment-picker');
        if (picker) {
          picker.dataset.selected = button.getAttribute('data-attachment');
          picker.hidden = true;
          button.classList.add('is-selected');
        }
      });
    });
    var publish = container.querySelector('#club-publish');
    if (publish) {
      publish.addEventListener('click', function() {
        var textarea = container.querySelector('#club-comment-text');
        var body = textarea.value.trim();
        if (!body || !window.ClubData) return;
        var role = getRole();
        var authorIdx = 0;
        ClubData.addComment(currentCardId, { author: authorIdx, body: body }).then(function() {
          renderDetail(container, currentCardId);
        });
      });
    }
    var reacts = container.querySelectorAll('.club-react');
    reacts.forEach(function(btn) {
      btn.addEventListener('click', function() {
        var count = parseInt(btn.textContent.match(/\d+/)[0], 10) + 1;
        btn.textContent = btn.textContent.replace(/\d+/, count);
        btn.disabled = true;
      });
    });
    bindAvatarProfiles(container);
  }

  function attachmentHref(attachment) {
    if (!attachment || !attachment.route) return '#club';
    return attachment.route + (attachment.params ? '?' + encodeURIComponent(attachment.params) : '');
  }

  function bindAvatarProfiles(container) {
    container.querySelectorAll('.avatar-circle[data-profile]').forEach(function(avatar) {
      avatar.addEventListener('click', function(event) {
        event.stopPropagation();
        var profile = ClubData.getProfile(parseInt(avatar.getAttribute('data-profile'), 10) || 0);
        var old = document.querySelector('.club-mini-profile');
        if (old) old.remove();
        var popup = document.createElement('div');
        popup.className = 'club-mini-profile';
        popup.innerHTML = '<strong>' + escapeHtml(profile.handle) + '</strong><span>Уровень ' + profile.initial + '– · плоды: ' + (profile.level * 3) + '</span>';
        document.body.appendChild(popup);
        var rect = avatar.getBoundingClientRect();
        popup.style.left = Math.max(8, Math.min(window.innerWidth - 230, rect.left)) + 'px';
        popup.style.top = (rect.bottom + 8) + 'px';
        setTimeout(function() {
          document.addEventListener('click', function closeProfile(e) {
            if (!popup.contains(e.target)) { popup.remove(); document.removeEventListener('click', closeProfile); }
          });
        }, 0);
      });
    });
  }

  function bindWaitlistEvents(container) {
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

  function setCardId(id) {
    currentCardId = id || null;
  }

  return {
    render: render,
    addToWaitlist: addToWaitlist,
    _setCardId: setCardId
  };
})();

window.ClubModule = ClubModule;
