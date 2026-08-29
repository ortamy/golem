(function(window, document) {
  'use strict';

  var STORAGE_KEY = 'golem.research-board.v1';
  var COLORS = ['#d9a441', '#c96b4b', '#6fa3a8', '#a67c52', '#b6b05f', '#c8c1b3'];
  var DEFAULT_WIDTH = 230;
  var DEFAULT_HEIGHT = 150;
  var active = null;

  function uid(prefix) {
    return prefix + '-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8);
  }

  function number(value, fallback) {
    var parsed = Number(value);
    return isFinite(parsed) ? parsed : fallback;
  }

  function text(value) {
    return String(value == null ? '' : value);
  }

  function cleanState(raw) {
    raw = raw && typeof raw === 'object' ? raw : {};
    var cards = Array.isArray(raw.cards) ? raw.cards : [];
    var cardIds = {};
    var normalizedCards = cards.map(function(card, index) {
      var id = text(card.id) || uid('card');
      if (cardIds[id]) id = uid('card');
      cardIds[id] = true;
      return {
        id: id,
        title: text(card.title) || 'Новая карточка ' + (index + 1),
        summary: text(card.summary),
        content: text(card.content),
        x: Math.max(0, number(card.x, 30 + index * 24)),
        y: Math.max(0, number(card.y, 30 + index * 24)),
        color: text(card.color) || COLORS[index % COLORS.length],
        createdAt: number(card.createdAt, Date.now())
      };
    });
    var valid = {};
    normalizedCards.forEach(function(card) { valid[card.id] = true; });

    var connections = (Array.isArray(raw.connections) ? raw.connections : []).map(function(line, index) {
      var bendX = number(line.bendX, NaN);
      var bendY = number(line.bendY, NaN);
      return {
        id: text(line.id) || uid('line'),
        from: text(line.from),
        to: text(line.to),
        color: text(line.color) || COLORS[index % COLORS.length],
        width: Math.max(1, Math.min(8, number(line.width, 3))),
        bendX: isFinite(bendX) ? Math.max(0, bendX) : null,
        bendY: isFinite(bendY) ? Math.max(0, bendY) : null
      };
    }).filter(function(line) {
      return line.from !== line.to && valid[line.from] && valid[line.to];
    });

    var groups = (Array.isArray(raw.groups) ? raw.groups : []).map(function(group, index) {
      var members = (Array.isArray(group.cardIds) ? group.cardIds : []).filter(function(id) { return valid[id]; });
      return {
        id: text(group.id) || uid('group'),
        name: text(group.name) || 'Группа ' + (index + 1),
        cardIds: members,
        color: text(group.color) || COLORS[index % COLORS.length]
      };
    }).filter(function(group) { return group.cardIds.length > 0; });

    return { cards: normalizedCards, connections: connections, groups: groups };
  }

  function load() {
    try { return cleanState(JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')); }
    catch (error) { return cleanState({}); }
  }

  function save() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(active.state)); }
    catch (error) { setStatus('Локальное сохранение недоступно в этом режиме браузера.'); }
  }

  function esc(value) {
    var node = document.createElement('div');
    node.textContent = text(value);
    return node.innerHTML;
  }

  function cardById(id) {
    return active.state.cards.filter(function(card) { return card.id === id; })[0];
  }

  function setStatus(message) {
    if (active && active.status) active.status.textContent = message;
  }

  function openCard(card) {
    active.editingId = card ? card.id : null;
    active.form.reset();
    active.formTitle.textContent = card ? 'Редактировать карточку' : 'Новая карточка';
    if (card) {
      active.fields.title.value = card.title;
      active.fields.summary.value = card.summary;
      active.fields.content.value = card.content;
    }
    active.modal.hidden = false;
    active.fields.title.focus();
  }

  function closeCard() {
    active.modal.hidden = true;
    active.editingId = null;
  }

  function addCard() {
    openCard(null);
  }

  function saveCard(event) {
    event.preventDefault();
    var title = active.fields.title.value.trim();
    if (!title) return;
    var card = active.editingId ? cardById(active.editingId) : null;
    if (!card) {
      card = { id: uid('card'), x: 40 + active.state.cards.length * 26, y: 40 + active.state.cards.length * 26, color: COLORS[active.state.cards.length % COLORS.length], createdAt: Date.now() };
      active.state.cards.push(card);
    }
    card.title = title;
    card.summary = active.fields.summary.value.trim();
    card.content = active.fields.content.value.trim();
    save(); render(); closeCard();
    setStatus('Карточка сохранена локально.');
  }

  function deleteCard() {
    if (!active.editingId) return;
    var id = active.editingId;
    active.state.cards = active.state.cards.filter(function(card) { return card.id !== id; });
    active.state.connections = active.state.connections.filter(function(line) { return line.from !== id && line.to !== id; });
    active.state.groups.forEach(function(group) { group.cardIds = group.cardIds.filter(function(member) { return member !== id; }); });
    active.state.groups = active.state.groups.filter(function(group) { return group.cardIds.length; });
    save(); closeCard(); render();
    setStatus('Карточка и связанные с ней элементы удалены.');
  }

  function point(event) {
    var rect = active.workspace.getBoundingClientRect();
    return { x: Math.max(0, event.clientX - rect.left + active.workspace.scrollLeft), y: Math.max(0, event.clientY - rect.top + active.workspace.scrollTop) };
  }

  function dragCard(event, card, element) {
    if (event.button !== 0 || event.target.closest('button, input, textarea, label')) return;
    event.preventDefault();
    var start = point(event), origin = { x: card.x, y: card.y }, moved = false;
    function move(moveEvent) {
      var next = point(moveEvent);
      card.x = Math.max(0, origin.x + next.x - start.x);
      card.y = Math.max(0, origin.y + next.y - start.y);
      moved = moved || Math.abs(next.x - start.x) > 3 || Math.abs(next.y - start.y) > 3;
      element.style.left = card.x + 'px'; element.style.top = card.y + 'px';
      renderConnections(); renderGroups();
    }
    function stop() {
      document.removeEventListener('pointermove', move);
      document.removeEventListener('pointerup', stop);
      if (moved) { card._dragged = true; save(); setTimeout(function() { card._dragged = false; }, 0); }
    }
    document.addEventListener('pointermove', move);
    document.addEventListener('pointerup', stop);
  }

  function lineBend(line, from, to) {
    return {
      x: line.bendX == null ? (from.x + to.x) / 2 : line.bendX,
      y: line.bendY == null ? (from.y + to.y) / 2 : line.bendY
    };
  }

  function dragConnection(event, line) {
    if (event.button !== 0) return;
    var from = cardById(line.from), to = cardById(line.to);
    if (!from || !to) return;
    event.preventDefault();
    event.stopPropagation();
    active.connectionId = line.id;
    var start = point(event), initial = lineBend(line, from, to), moved = false;
    function move(moveEvent) {
      var next = point(moveEvent);
      line.bendX = Math.max(0, initial.x + next.x - start.x);
      line.bendY = Math.max(0, initial.y + next.y - start.y);
      moved = moved || Math.abs(next.x - start.x) > 3 || Math.abs(next.y - start.y) > 3;
      renderConnections();
    }
    function stop() {
      document.removeEventListener('pointermove', move);
      document.removeEventListener('pointerup', stop);
      renderInspector();
      if (moved) {
        save();
        setStatus('Изгиб связи сохранён. Маркер на выбранной линии можно перетаскивать снова.');
      }
    }
    document.addEventListener('pointermove', move);
    document.addEventListener('pointerup', stop);
  }

  function renderCards() {
    active.cards.innerHTML = '';
    active.state.cards.forEach(function(card) {
      var element = document.createElement('article');
      element.className = 'board-card' + (active.selected[card.id] ? ' is-selected' : '');
      element.dataset.cardId = card.id;
      element.style.left = card.x + 'px'; element.style.top = card.y + 'px';
      element.style.setProperty('--card-accent', card.color);
      element.innerHTML = '<div class="board-card-bar"><label class="board-card-check"><input type="checkbox" ' + (active.selected[card.id] ? 'checked' : '') + ' aria-label="Выбрать карточку"></label><button type="button" class="board-card-edit" aria-label="Редактировать">···</button></div>' +
        '<h3>' + esc(card.title) + '</h3><p>' + esc(card.summary || 'Без краткого описания') + '</p><span class="board-card-hint">клик — полный Давар</span>';
      element.addEventListener('pointerdown', function(event) { dragCard(event, card, element); });
      element.addEventListener('click', function(event) {
        if (card._dragged || event.target.closest('input,button')) return;
        if (active.mode === 'connect') { chooseConnection(card.id); return; }
        openCard(card);
      });
      element.querySelector('input').addEventListener('change', function(event) {
        active.selected[card.id] = event.target.checked;
        element.classList.toggle('is-selected', event.target.checked);
      });
      element.querySelector('.board-card-edit').addEventListener('click', function() { openCard(card); });
      active.cards.appendChild(element);
    });
    active.empty.hidden = active.state.cards.length > 0;
  }

  function renderConnections() {
    var svg = active.svg, rect = active.workspace.getBoundingClientRect();
    svg.setAttribute('width', Math.max(active.workspace.scrollWidth, rect.width));
    svg.setAttribute('height', Math.max(active.workspace.scrollHeight, rect.height));
    svg.innerHTML = '';
    active.state.connections.forEach(function(line) {
      var from = cardById(line.from), to = cardById(line.to);
      if (!from || !to) return;
      var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      var x1 = from.x + DEFAULT_WIDTH / 2, y1 = from.y + DEFAULT_HEIGHT / 2, x2 = to.x + DEFAULT_WIDTH / 2, y2 = to.y + DEFAULT_HEIGHT / 2;
      var bend = lineBend(line, { x: x1, y: y1 }, { x: x2, y: y2 });
      path.setAttribute('d', 'M ' + x1 + ' ' + y1 + ' Q ' + bend.x + ' ' + bend.y + ' ' + x2 + ' ' + y2);
      path.setAttribute('class', 'board-line' + (active.connectionId === line.id ? ' is-active' : ''));
      path.style.stroke = line.color; path.style.strokeWidth = line.width;
      path.dataset.lineId = line.id;
      path.addEventListener('pointerdown', function(event) { dragConnection(event, line); });
      path.addEventListener('click', function(event) { event.stopPropagation(); active.connectionId = line.id; renderInspector(); renderConnections(); });
      svg.appendChild(path);
      if (active.connectionId === line.id) {
        var handle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        handle.setAttribute('class', 'board-line-handle');
        handle.setAttribute('cx', bend.x); handle.setAttribute('cy', bend.y); handle.setAttribute('r', '9');
        handle.setAttribute('fill', line.color); handle.setAttribute('stroke', '#fff1bf'); handle.setAttribute('stroke-width', '2');
        handle.dataset.lineId = line.id;
        handle.addEventListener('pointerdown', function(event) { dragConnection(event, line); });
        svg.appendChild(handle);
      }
    });
  }

  function renderGroups() {
    active.groups.innerHTML = '';
    active.state.groups.forEach(function(group) {
      var members = group.cardIds.map(cardById).filter(Boolean);
      if (!members.length) return;
      var left = Math.max(8, Math.min.apply(null, members.map(function(card) { return card.x; })) - 16);
      var top = Math.max(8, Math.min.apply(null, members.map(function(card) { return card.y; })) - 34);
      var right = Math.max.apply(null, members.map(function(card) { return card.x + DEFAULT_WIDTH; })) + 16;
      var bottom = Math.max.apply(null, members.map(function(card) { return card.y + DEFAULT_HEIGHT; })) + 16;
      var element = document.createElement('div');
      element.className = 'board-group'; element.style.left = left + 'px'; element.style.top = top + 'px'; element.style.width = (right - left) + 'px'; element.style.height = (bottom - top) + 'px'; element.style.setProperty('--group-accent', group.color);
      element.innerHTML = '<button type="button" class="board-group-name" title="Переименовать группу">' + esc(group.name) + '</button>';
      element.querySelector('button').addEventListener('click', function() { var name = window.prompt('Название группы', group.name); if (name && name.trim()) { group.name = name.trim(); save(); renderGroups(); } });
      active.groups.appendChild(element);
    });
  }

  function renderInspector() {
    var line = active.state.connections.filter(function(item) { return item.id === active.connectionId; })[0];
    if (!line) { active.inspector.hidden = true; return; }
    active.inspector.hidden = false;
    active.inspector.innerHTML = '<div class="board-inspector-title">Связь</div><label>Цвет<input type="color" data-line-color value="' + esc(line.color) + '"></label><label>Толщина<input type="range" min="1" max="8" value="' + line.width + '" data-line-width><output>' + line.width + '</output></label><button type="button" class="lab-btn lab-btn-danger lab-btn-sm" data-line-delete>Удалить линию</button><p class="text-small">Нажмите на линию или её маркер и перетащите, чтобы изменить изгиб.</p>';
    active.inspector.querySelector('[data-line-color]').addEventListener('input', function() { line.color = this.value; save(); renderConnections(); });
    active.inspector.querySelector('[data-line-width]').addEventListener('input', function() { line.width = Number(this.value); this.nextElementSibling.value = line.width; save(); renderConnections(); });
    active.inspector.querySelector('[data-line-delete]').addEventListener('click', function() { active.state.connections = active.state.connections.filter(function(item) { return item.id !== line.id; }); active.connectionId = null; save(); renderInspector(); renderConnections(); });
  }

  function chooseConnection(id) {
    if (!active.connectFrom) { active.connectFrom = id; setStatus('Первая карточка выбрана. Нажмите вторую карточку.'); return; }
    if (active.connectFrom === id) return;
    var exists = active.state.connections.some(function(line) { return (line.from === active.connectFrom && line.to === id) || (line.from === id && line.to === active.connectFrom); });
    if (!exists) active.state.connections.push({ id: uid('line'), from: active.connectFrom, to: id, color: COLORS[active.state.connections.length % COLORS.length], width: 3, bendX: null, bendY: null });
    active.connectFrom = null; active.mode = null; save(); render(); setStatus('Связь сохранена. Нажмите на линию для цвета, толщины или удаления.');
  }

  function groupSelected() {
    var ids = Object.keys(active.selected).filter(function(id) { return active.selected[id] && cardById(id); });
    if (ids.length < 2) { setStatus('Для группы выберите минимум две карточки флажками.'); return; }
    var name = window.prompt('Название группы', 'Новая группа');
    if (!name || !name.trim()) return;
    active.state.groups.push({ id: uid('group'), name: name.trim(), cardIds: ids, color: COLORS[active.state.groups.length % COLORS.length] });
    active.selected = {}; save(); render(); setStatus('Группа сохранена локально.');
  }

  function exportState() {
    var blob = new Blob([JSON.stringify(active.state, null, 2)], { type: 'application/json' });
    var link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = 'golem-research-board.json'; link.click(); URL.revokeObjectURL(link.href);
    setStatus('Доска экспортирована в JSON-файл.');
  }

  function importState(event) {
    var file = event.target.files[0]; if (!file) return;
    var reader = new FileReader();
    reader.onload = function() { try { active.state = cleanState(JSON.parse(reader.result)); active.selected = {}; active.connectionId = null; save(); render(); setStatus('Доска восстановлена из файла.'); } catch (error) { setStatus('Не удалось прочитать JSON доски.'); } };
    reader.readAsText(file); event.target.value = '';
  }

  function render() {
    renderCards(); renderGroups(); renderConnections(); renderInspector();
  }

  function bind(container) {
    active = { container: container, state: load(), selected: {}, mode: null, connectFrom: null, connectionId: null };
    active.workspace = container.querySelector('[data-board-workspace]');
    active.cards = container.querySelector('[data-board-cards]'); active.groups = container.querySelector('[data-board-groups]'); active.svg = container.querySelector('[data-board-svg]'); active.empty = container.querySelector('[data-board-empty]'); active.status = container.querySelector('[data-board-status]'); active.modal = container.querySelector('[data-board-modal]'); active.inspector = container.querySelector('[data-board-inspector]'); active.form = container.querySelector('[data-board-card-form]'); active.formTitle = container.querySelector('[data-board-form-title]');
    active.fields = {
      title: active.form.querySelector('[name="title"]'),
      summary: active.form.querySelector('[name="summary"]'),
      content: active.form.querySelector('[name="content"]')
    };
    container.querySelectorAll('[data-board-action]').forEach(function(button) {
      button.addEventListener('click', function() {
        var action = this.dataset.boardAction;
        if (action === 'add') addCard();
        if (action === 'connect') { active.mode = 'connect'; active.connectFrom = null; setStatus('Режим связи: кликните по двум карточкам по очереди.'); }
        if (action === 'group') groupSelected();
        if (action === 'export') exportState();
        if (action === 'import') container.querySelector('[data-board-import-input]').click();
        if (action === 'reset' && window.confirm('Удалить все карточки, линии и группы?')) { active.state = cleanState({}); active.selected = {}; active.connectionId = null; active.mode = null; active.connectFrom = null; save(); render(); setStatus('Доска очищена.'); }
      });
    });
    container.querySelector('[data-board-import-input]').addEventListener('change', importState);
    active.form.addEventListener('submit', saveCard); container.querySelector('[data-board-delete-card]').addEventListener('click', deleteCard);
    container.querySelectorAll('[data-board-close-modal]').forEach(function(node) { node.addEventListener('click', closeCard); });
    document.addEventListener('keydown', function(event) {
      if (event.key === 'Escape' && active && !active.modal.hidden) closeCard();
    });
    active.workspace.addEventListener('click', function(event) { if (event.target === active.workspace) { active.connectionId = null; renderInspector(); renderConnections(); } });
    render();
  }

  window.ResearchBoard = { init: function(container) { if (!container || container.dataset.boardReady) return; container.dataset.boardReady = '1'; bind(container); } };
})(window, document);