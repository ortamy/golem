/* =============================================
   nav-enhance.js — Этап 6: навигация
   Фильтр сайдбара + палитра команд (Ctrl/Cmd+K).
   Только навигационная оболочка: палео-логику
   и рендеры модулей не затрагивает.
   ============================================= */
(function () {
  'use strict';

  var INDEX = [];
  var pal = null, listEl = null, inpEl = null;
  var flat = [], sel = -1, opener = null;

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  /* ---- индекс навигации из DOM ---- */
  function collectItems() {
    var out = [];
    document.querySelectorAll('a.sidebar-item').forEach(function (a) {
      var secEl = a.closest('.sidebar-section');
      var sec = '';
      if (secEl) {
        var h = secEl.querySelector('.sidebar-section-header span:not(.toggle-icon)');
        if (h) sec = h.textContent.trim();
      }
      out.push({
        el: a,
        title: a.textContent.replace(/\s+/g, ' ').trim(),
        id: a.getAttribute('data-module') || '',
        hash: a.getAttribute('href'),
        section: sec
      });
    });
    return out;
  }

  /* ---- фильтр сайдбара ---- */
  function applyFilter(qRaw) {
    var q = qRaw.trim().toLowerCase();
    INDEX.forEach(function (it) {
      var hay = (it.title + ' ' + it.id + ' ' + it.section).toLowerCase();
      it.el.style.display = (!q || hay.indexOf(q) > -1) ? '' : 'none';
    });
    document.querySelectorAll('.sidebar-section').forEach(function (sec) {
      var any = false;
      sec.querySelectorAll('.sidebar-item').forEach(function (i) {
        if (i.style.display !== 'none') any = true;
      });
      sec.style.display = any ? '' : 'none';
    });
  }

  function installFilter() {
    var items = document.querySelector('.lab-sidebar .sidebar-items');
    if (!items || document.getElementById('labNavFilter')) return;
    var box = document.createElement('div');
    box.className = 'lab-nav-filter';
    var inp = document.createElement('input');
    inp.type = 'search';
    inp.id = 'labNavFilter';
    inp.placeholder = 'Фильтр по разделам…';
    inp.setAttribute('aria-label', 'Фильтр навигации');
    inp.addEventListener('input', function () { applyFilter(this.value); });
    box.appendChild(inp);
    items.insertBefore(box, items.firstChild);
  }

  /* ---- палитра команд ---- */
  function ensurePalette() {
    if (pal) return;
    pal = document.createElement('div');
    pal.className = 'lab-palette-backdrop';
    pal.style.display = 'none';
    pal.innerHTML =
      '<div class="lab-palette" role="dialog" aria-modal="true" aria-label="Быстрая навигация">' +
      '<input type="text" aria-label="Поиск по разделам" autocomplete="off" spellcheck="false">' +
      '<div class="lab-palette-list" role="listbox"></div>' +
      '</div>';
    document.body.appendChild(pal);
    inpEl = pal.querySelector('input');
    listEl = pal.querySelector('.lab-palette-list');

    pal.addEventListener('mousedown', function (e) {
      if (e.target === pal) closePalette();
    });
    inpEl.addEventListener('input', render);
    inpEl.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        move(e.key === 'ArrowDown' ? 1 : -1);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        go(sel);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        closePalette();
      }
    });
  }

  function render() {
    var q = inpEl.value.trim().toLowerCase();
    flat = INDEX.filter(function (it) {
      if (!q) return true;
      return (it.title + ' ' + it.id + ' ' + it.section).toLowerCase().indexOf(q) > -1;
    }).slice(0, 25);
    sel = flat.length ? 0 : -1;
    listEl.innerHTML = '';
    flat.forEach(function (it, i) {
      var d = document.createElement('div');
      d.className = 'lab-palette-item';
      d.setAttribute('role', 'option');
      d.setAttribute('aria-selected', i === sel ? 'true' : 'false');
      d.innerHTML = '<span>' + esc(it.title) + '</span>' +
        (it.section ? '<kbd>' + esc(it.section) + '</kbd>' : '');
      d.addEventListener('click', function () { go(i); });
      d.addEventListener('mousemove', function () { if (sel !== i) { sel = i; paint(); } });
      listEl.appendChild(d);
    });
    if (!flat.length) {
      var empty = document.createElement('div');
      empty.className = 'lab-palette-empty';
      empty.textContent = 'Ничего не найдено';
      listEl.appendChild(empty);
    } else {
      paint();
    }
  }

  function paint() {
    listEl.querySelectorAll('.lab-palette-item').forEach(function (n, i) {
      n.setAttribute('aria-selected', i === sel ? 'true' : 'false');
    });
    var s = listEl.querySelector('[aria-selected="true"]');
    if (s && s.scrollIntoView) s.scrollIntoView({ block: 'nearest' });
  }

  function move(d) {
    if (!flat.length) return;
    sel = (sel + d + flat.length) % flat.length;
    paint();
  }

  function go(i) {
    if (i < 0 || !flat[i]) return;
    var hash = flat[i].hash;
    closePalette();
    if (location.hash !== hash) location.hash = hash;
    if (window.LabSidebar && typeof LabSidebar.close === 'function') LabSidebar.close();
  }

  function openPalette() {
    ensurePalette();
    opener = document.activeElement;
    pal.style.display = 'block';
    inpEl.value = '';
    render();
    setTimeout(function () { inpEl.focus(); }, 0);
  }

  function closePalette() {
    if (!pal || pal.style.display === 'none') return;
    pal.style.display = 'none';
    if (opener && typeof opener.focus === 'function') {
      try { opener.focus(); } catch (e) { /* нода исчезла */ }
    }
  }

  /* ---- глобальные клавиши и мост мёртвого хедер-поиска ---- */
  function installKeys() {
    window.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K' || e.code === 'KeyK')) {
        e.preventDefault();
        openPalette();
      } else if (e.key === 'Escape' && pal && pal.style.display !== 'none') {
        /* Этап 6: Escape гасит палитру независимо от того, где фокус */
        closePalette();
      }
    }, true);

    var gs = document.getElementById('globalSearch');
    if (!gs) return;
    var gi = gs.querySelector('input');
    if (gi) {
      gi.readOnly = true;
      gi.tabIndex = -1;
      gi.removeAttribute('oninput');
      gi.removeAttribute('onkeydown');
    }
    gs.addEventListener('click', function (e) {
      e.preventDefault();
      openPalette();
    });
  }

  /* ===== Иконки: инлайн-SVG на currentColor вместо PNG 32px (Этап 6) =====
     Тема наследуется автоматически; там, где своей семантики нет
     (religionisms, paleo-linguistics) — исходная иконка сохраняется. */
  var ICONS = {
    'dashboard': '<rect x="3.5" y="3.5" width="7" height="7" rx="1"/><rect x="13.5" y="3.5" width="7" height="7" rx="1"/><rect x="3.5" y="13.5" width="7" height="7" rx="1"/><rect x="13.5" y="13.5" width="7" height="7" rx="1"/>',
    'manifest': '<path d="M6 3.5h9l4 4V20.5H6z"/><path d="M15 3.5v4h4"/><path d="M9 12h6M9 16h6"/>',
    'scripture-reader': '<path d="M12 5.5C10 4 7 3.5 4 3.8v14c3-.3 6 .2 8 1.7 2-1.5 5-2 8-1.7v-14c-3-.3-6 .2-8 1.7z"/><path d="M12 5.5v14"/>',
    'timeline': '<path d="M4 12h16"/><circle cx="8" cy="12" r="1.8"/><circle cx="16" cy="12" r="1.8"/><path d="M8 10.2V6M16 13.8V18"/>',
    'states': '<path d="M6 21V4"/><path d="M6 4h11l-2.5 3.5L17 11H6"/>',
    'dictionaries': '<rect x="4.5" y="3.5" width="15" height="17" rx="1.5"/><path d="M9 15.5l3-8 3 8M10.2 13h3.6"/>',
    'researches': '<circle cx="11" cy="11" r="5.5"/><path d="M15.5 15.5L20 20"/>',
    'generators': '<path d="M5 19l6.5-6.5"/><path d="M11 5l8 8-2.5 2.5-8-8z"/><path d="M4 20h5"/>',
    'checkers': '<rect x="4.5" y="4.5" width="15" height="15" rx="2"/><path d="M9 12l2.5 2.5L16 9.5"/>',
    'analyzers': '<path d="M10 3.5h4M11 3.5v5l-5 9.5a1.5 1.5 0 0 0 1.3 2.5h9.4a1.5 1.5 0 0 0 1.3-2.5l-5-9.5v-5"/>',
    'cartography': '<circle cx="12" cy="12" r="8.5"/><ellipse cx="12" cy="12" rx="4" ry="8.5"/><path d="M4 12h16"/>',
    'learn': '<path d="M12 4L2.5 8.5 12 13l9.5-4.5z"/><path d="M6 10.5V15c0 1.5 2.7 3 6 3s6-1.5 6-3v-4.5"/>',
    'methodology': '<circle cx="12" cy="12" r="8.5"/><path d="M15 9l-2 4.5L8.5 15l2-4.5z"/>',
    'ai-agents': '<path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><circle cx="12" cy="12" r="3"/>',
    'ed-chat': '<path d="M20 15.5a1.5 1.5 0 0 1-1.5 1.5H10l-5 4v-4H5.5A1.5 1.5 0 0 1 4 15.5v-9A1.5 1.5 0 0 1 5.5 5h13A1.5 1.5 0 0 1 20 6.5z"/>',
    'vision': '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
    'translation-comparator': '<path d="M7 8h12l-3.5-3.5M17 16H5l3.5 3.5"/>',
    'paleo-keyboard': '<rect x="3.5" y="7" width="17" height="10" rx="1.5"/><path d="M7 10.5h.01M10.5 10.5h.01M14 10.5h.01M17 10.5h.01M7.5 14h9"/>',
    'paleo-builder': '<rect x="4" y="13" width="7" height="7"/><rect x="13" y="13" width="7" height="7"/><rect x="8.5" y="4" width="7" height="7"/>',
    'paleo-mechanics': '<circle cx="12" cy="12" r="3.5"/><path d="M12 4v3M12 17v3M4 12h3M17 12h3M6.3 6.3l2.1 2.1M15.6 15.6l2.1 2.1M17.7 6.3l-2.1 2.1M8.4 15.6l-2.1 2.1"/>',
    'admin-settings': '<path d="M4 7h16M4 12h16M4 17h16"/><circle cx="9" cy="7" r="2"/><circle cx="15" cy="12" r="2"/><circle cx="8" cy="17" r="2"/>',
    'language-map': '<path d="M12 21V11l-6-6M12 11l6-6"/><circle cx="6" cy="4.5" r="1.5"/><circle cx="18" cy="4.5" r="1.5"/>'
  };

  function iconSvg(inner) {
    return '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + inner + '</svg>';
  }

  function installIcons() {
    var items = document.querySelectorAll('a.sidebar-item[data-module]');
    for (var i = 0; i < items.length; i++) {
      var mod = items[i].getAttribute('data-module');
      var img = items[i].querySelector('img.lab-icon');
      if (!mod || !ICONS[mod] || !img) continue;
      var wrap = document.createElement('span');
      wrap.className = 'lab-icon-wrap';
      wrap.innerHTML = iconSvg(ICONS[mod]);
      img.parentNode.replaceChild(wrap, img);
    }
  }

  function init() {
    if (!document.querySelector('.lab-sidebar')) return;
    INDEX = collectItems();
    installFilter();
            installIcons();
    installCrumbs();
    installKeys();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

      /* ===== Хлебные крошки (Этап 7) =====
     Одноуровневая крошка: «Главная / <Текущий>». Роутер подменяет
     .lab-content после DOMContentLoaded, поэтому рендер привязан к
     hashchange + наблюдателю за DOM-сменой модуля + повторному рендеру. */
  function installCrumbs() {
    var root = document.querySelector('main') || document.body;
    var slot = null, current = null;

    function render() {
      var h = root.querySelector('h1');
      if (slot && slot.parentNode) { slot.parentNode.removeChild(slot); slot = null; }
      if (!h || !h.parentElement) return;

      var wrap = document.createElement('div');
      wrap.className = 'lab-crumb-slot';
      wrap.innerHTML = (
        '<nav class="lab-crumbs" aria-label="Хлебные крошки">' +
          '<a href="#dashboard" class="lab-crumb">Главная</a>' +
          '<span class="lab-crumb-sep" aria-hidden="true">›</span>' +
          '<span class="lab-crumb-current"></span>' +
        '</nav>'
      );
      current = wrap.querySelector('.lab-crumb-current');
      var hash = location.hash || '#';
      var hit = INDEX && INDEX.find ? INDEX.find(function (it) { return it.hash === hash; }) : null;
      current.textContent = hit && hit.name ? hit.name : (h.textContent.trim() || 'Страница');
      h.parentElement.insertBefore(wrap, h);
      slot = wrap;
    }

    // роутер подменяет .lab-content после DOMContentLoaded — перерисовать после него
    var locked = false, pending = false;
    function schedule() {
      if (pending || locked) return;
      pending = true;
      setTimeout(function () { pending = false; if (!locked) render(); }, 60);
    }

    render();
    setTimeout(render, 0);                  // после синхронного роутера
    window.addEventListener('hashchange', schedule);
    new MutationObserver(schedule).observe(root, { childList: true, subtree: true });
  }
  window.LabNav = { openPalette: openPalette, closePalette: closePalette };
})();
