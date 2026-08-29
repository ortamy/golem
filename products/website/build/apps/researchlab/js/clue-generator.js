/** Генератор улик: собирает наблюдения в проверяемую цепочку. */
(function() {
  'use strict';

  var STORAGE_KEY = 'golem_clue_cases';
  var state = { clues: [], links: [], conclusion: '', cases: [], selected: null };
  var container;

  function id() { return 'clue-' + Date.now() + '-' + Math.random().toString(16).slice(2); }
  function esc(value) { var node = document.createElement('div'); node.textContent = value || ''; return node.innerHTML; }
  function loadCases() { try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); } catch (e) { return []; } }
  function saveCases() { localStorage.setItem(STORAGE_KEY, JSON.stringify(state.cases)); }
  function clueById(clueId) { return state.clues.filter(function(clue) { return clue.id === clueId; })[0]; }

  function render() {
    if (!container) return;
    var clueHtml = state.clues.map(function(clue, index) {
      var selected = state.selected === clue.id ? ' is-selected' : '';
      return '<article class="clue-card' + selected + '" draggable="true" data-clue-id="' + clue.id + '">' +
        '<div class="clue-card-head"><span class="clue-drag" title="Перетащить">⋮⋮</span><span class="clue-number">' + String(index + 1).padStart(2, '0') + '</span><button type="button" class="clue-select" data-select="' + clue.id + '">' + (state.selected === clue.id ? 'Выбрана' : 'Выбрать') + '</button></div>' +
        '<textarea class="clue-text" data-text="' + clue.id + '" rows="3" placeholder="Наблюдение, факт или след…">' + esc(clue.text) + '</textarea></article>';
    }).join('');
    var linkOptions = state.clues.map(function(clue) { return '<option value="' + clue.id + '">' + esc(clue.text || 'Улика без текста') + '</option>'; }).join('');
    var linksHtml = state.links.map(function(link, index) {
      return '<div class="clue-link-row" data-link-index="' + index + '"><select data-link-from="' + index + '">' + linkOptions.replace('value="' + link.from + '"', 'value="' + link.from + '" selected') + '</select><input class="lab-input" data-link-text="' + index + '" value="' + esc(link.text) + '" placeholder="потому что / поэтому"><select data-link-to="' + index + '">' + linkOptions.replace('value="' + link.to + '"', 'value="' + link.to + '" selected') + '</select><button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" data-remove-link="' + index + '">Удалить</button></div>';
    }).join('');
    var casesHtml = state.cases.map(function(item, index) { return '<li><button type="button" data-case="' + index + '">' + esc(item.title || 'Кейс ' + (index + 1)) + '</button><span>' + item.clues.length + ' улик</span></li>'; }).join('');
    container.innerHTML = '<div class="clue-page"><p class="gc-kicker">ГЕНЕРАТОРЫ · СВИДЕТЕЛЬСТВА</p><h1>Генератор улик — Цепочка разоблачения</h1><p class="subtitle">Собери наблюдения в последовательность, ведущую к выводу.</p>' +
      '<div class="clue-layout"><section class="clue-workspace"><div class="clue-section-head"><h2>Наблюдения</h2><span class="clue-hint">Перетащите карточки в нужный порядок</span></div><div id="clue-list" class="clue-list">' + clueHtml + '</div><div class="clue-actions"><button type="button" class="lab-btn lab-btn-primary" id="clue-add">Добавить улику</button><button type="button" class="lab-btn lab-btn-secondary" id="clue-delete">Удалить выбранную</button></div><div class="clue-section-head"><h2>Логическое соединение</h2><span class="clue-hint">Причина → следствие</span></div><div id="clue-links">' + (linksHtml || '<p class="clue-empty">Добавьте связь между двумя уликами.</p>') + '</div><button type="button" class="lab-btn lab-btn-secondary" id="clue-add-link">Добавить стрелку</button></section>' +
      '<aside class="clue-side"><label for="clue-conclusion">Финальный вывод</label><textarea id="clue-conclusion" class="lab-textarea" rows="7" placeholder="Что следует из всей цепочки?">' + esc(state.conclusion) + '</textarea><button type="button" class="lab-btn lab-btn-primary" id="clue-build">Собрать цепочку</button><div id="clue-output" class="clue-output"><p class="clue-empty">Здесь появится схема цепочки.</p></div><div class="clue-save"><input id="clue-title" class="lab-input" placeholder="Название кейса"><button type="button" class="lab-btn lab-btn-secondary" id="clue-save">Сохранить кейс</button></div><div class="clue-export"><button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" id="clue-export-text">Экспортировать как текст</button><button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" id="clue-export-cards">Экспортировать как карточки</button></div><h2>Сохранённые улики</h2><ul class="clue-cases">' + (casesHtml || '<li class="clue-empty">Сохранённых цепочек пока нет.</li>') + '</ul></aside></div></div>';
    bind();
  }

  function bind() {
    container.querySelectorAll('[data-select]').forEach(function(el) { el.onclick = function() { state.selected = el.dataset.select; render(); }; });
    container.querySelectorAll('[data-text]').forEach(function(el) { el.oninput = function() { clueById(el.dataset.text).text = el.value; }; });
    container.querySelector('#clue-conclusion').oninput = function(e) { state.conclusion = e.target.value; };
    container.querySelector('#clue-add').onclick = function() { state.clues.push({ id: id(), text: '' }); state.selected = state.clues[state.clues.length - 1].id; render(); };
    container.querySelector('#clue-delete').onclick = function() { if (state.selected) { state.clues = state.clues.filter(function(c) { return c.id !== state.selected; }); state.links = state.links.filter(function(l) { return l.from !== state.selected && l.to !== state.selected; }); state.selected = null; render(); } };
    container.querySelector('#clue-add-link').onclick = function() { if (state.clues.length < 2) return; state.links.push({ from: state.clues[0].id, to: state.clues[1].id, text: 'потому что' }); render(); };
    container.querySelectorAll('[data-link-from]').forEach(function(el) { el.onchange = function() { state.links[el.dataset.linkFrom].from = el.value; }; });
    container.querySelectorAll('[data-link-to]').forEach(function(el) { el.onchange = function() { state.links[el.dataset.linkTo].to = el.value; }; });
    container.querySelectorAll('[data-link-text]').forEach(function(el) { el.oninput = function() { state.links[el.dataset.linkText].text = el.value; }; });
    container.querySelectorAll('[data-remove-link]').forEach(function(el) { el.onclick = function() { state.links.splice(Number(el.dataset.removeLink), 1); render(); }; });
    container.querySelector('#clue-build').onclick = build;
    container.querySelector('#clue-save').onclick = function() { state.cases.unshift({ title: container.querySelector('#clue-title').value.trim() || 'Кейс ' + new Date().toLocaleDateString('ru-RU'), clues: state.clues, links: state.links, conclusion: state.conclusion }); saveCases(); render(); };
    container.querySelector('#clue-export-text').onclick = exportText;
    container.querySelector('#clue-export-cards').onclick = exportCards;
    container.querySelectorAll('[data-case]').forEach(function(el) { el.onclick = function() { var item = state.cases[Number(el.dataset.case)]; state.clues = item.clues; state.links = item.links; state.conclusion = item.conclusion; render(); build(); }; });
    container.querySelectorAll('.clue-card').forEach(function(card) { card.ondragstart = function(e) { e.dataTransfer.setData('text/plain', card.dataset.clueId); }; card.ondragover = function(e) { e.preventDefault(); }; card.ondrop = function(e) { e.preventDefault(); reorder(e.dataTransfer.getData('text/plain'), card.dataset.clueId); }; });
  }
  function reorder(source, target) { var from = state.clues.findIndex(function(c) { return c.id === source; }); var to = state.clues.findIndex(function(c) { return c.id === target; }); if (from < 0 || to < 0 || from === to) return; var item = state.clues.splice(from, 1)[0]; state.clues.splice(to, 0, item); render(); }
  function build() { var output = container.querySelector('#clue-output'); output.innerHTML = state.clues.map(function(c) { var next = state.links.filter(function(l) { return l.from === c.id; }).map(function(l) { return '<div class="clue-arrow">↓ ' + esc(l.text || 'связь') + '</div>'; }).join(''); return '<div class="clue-output-card"><strong>' + esc(c.text || 'Улика без текста') + '</strong>' + next + '</div>'; }).join('') + '<div class="clue-conclusion"><b>Вывод:</b> ' + esc(state.conclusion || 'Вывод не указан.') + '</div>'; }
  function text() { return state.clues.map(function(c, i) { var links = state.links.filter(function(l) { return l.from === c.id; }).map(function(l) { var to = clueById(l.to); return '  → ' + (l.text || 'связь') + ' → ' + (to ? to.text : ''); }).join('\n'); return (i + 1) + '. ' + c.text + (links ? '\n' + links : ''); }).join('\n') + '\n\nВывод: ' + state.conclusion; }
  function download(content, name, type) { var link = document.createElement('a'); link.href = URL.createObjectURL(new Blob([content], { type: type })); link.download = name; link.click(); URL.revokeObjectURL(link.href); }
  function exportText() { download(text(), 'golem-clue-chain.txt', 'text/plain;charset=utf-8'); }
  function exportCards() { var cards = state.clues.map(function(c) { return { type: 'clue', title: 'Улика', content: c.text }; }); cards.push({ type: 'conclusion', title: 'Вывод', content: state.conclusion }); localStorage.setItem('golem_board_import', JSON.stringify(cards)); if (window.LabRouter) window.LabRouter.navigate('board'); }
  window.ClueGenerator = { init: function(el) { container = el; if (container.dataset.ready) return; container.dataset.ready = '1'; state.cases = loadCases(); state.clues = [{ id: id(), text: '' }]; render(); } };
})();