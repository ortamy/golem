/* shortcuts.js — overlay горячих клавиш (как в Linear: ? показывает список) */
(function () {
  var shortcuts = [
    { key: 'N', label: 'Новое исследование' },
    { key: '/', label: 'Фокус на поиск' },
    { key: 'G then I', label: 'Перейти к Исследованиям' },
    { key: 'G then D', label: 'Перейти к Рабочему столу' },
    { key: 'G then C', label: 'Перейти к Клубу' },
    { key: '?', label: 'Показать этот список' },
    { key: 'Esc', label: 'Закрыть окно' }
  ];

  function show() {
    var existing = document.getElementById('shortcuts-overlay');
    if (existing) { existing.remove(); return; }

    var ov = document.createElement('div');
    ov.id = 'shortcuts-overlay';
    ov.innerHTML =
      '<div class="shortcuts-backdrop"></div>' +
      '<div class="shortcuts-panel" role="dialog" aria-label="Keyboard shortcuts">' +
        '<div class="shortcuts-header"><h3>Горячие клавиши</h3><button class="shortcuts-close" aria-label="Закрыть">Esc</button></div>' +
        '<div class="shortcuts-list">' +
          shortcuts.map(function (s) {
            return '<div class="shortcuts-row"><kbd>' + s.key + '</kbd><span>' + s.label + '</span></div>';
          }).join('') +
        '</div>' +
      '</div>';
    document.body.appendChild(ov);

    ov.querySelector('.shortcuts-close').addEventListener('click', function () { ov.remove(); });
    ov.querySelector('.shortcuts-backdrop').addEventListener('click', function () { ov.remove(); });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === '?' && !e.ctrlKey && !e.metaKey && !e.altKey) {
      var tag = (e.target && e.target.tagName) || '';
      if (tag === 'INPUT' || tag === 'TEXTAREA') return;
      e.preventDefault(); show();
    }
    if (e.key === 'Escape') {
      var ov = document.getElementById('shortcuts-overlay');
      if (ov) { ov.remove(); e.preventDefault(); }
    }
    if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
      var t = (e.target && e.target.tagName) || '';
      if (t !== 'INPUT' && t !== 'TEXTAREA') {
        e.preventDefault();
        var search = document.getElementById('researches-search') || document.querySelector('input[type="search"]');
        if (search) search.focus();
      }
    }
  });

  window.ShortcutsOverlay = { show: show };
})();
