(function(window, document) {
  'use strict';

  var STORAGE_KEY = 'golem_agent_server_v1';
  var DEFAULTS = {
    python: 'python',
    script: 'server.py',
    cwd: 'products/agents',
    host: '0.0.0.0',
    port: 8000,
    cors: true
  };
  var container = null;
  var state = null;

  function escapeHtml(value) {
    var node = document.createElement('div');
    node.textContent = String(value == null ? '' : value);
    return node.innerHTML;
  }

  function readState() {
    try {
      var saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
      return Object.assign({}, DEFAULTS, saved || {});
    } catch (error) {
      return Object.assign({}, DEFAULTS);
    }
  }

  function saveState() {
    if (!state) return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (error) {}
  }

  function shellQuote(value) {
    return '"' + String(value || '').replace(/"/g, '\\"') + '"';
  }

  function makeCommand(values) {
    var python = values.python.trim() || DEFAULTS.python;
    var script = values.script.trim() || DEFAULTS.script;
    var cwd = values.cwd.trim() || DEFAULTS.cwd;
    // Команда рассчитана на Windows cmd.exe: /d меняет и диск, && останавливает цепочку при ошибке.
    var command = 'cd /d ' + shellQuote(cwd) + ' && ' +
      (/[\\/\s]/.test(python) ? shellQuote(python) : python) + ' ' +
      shellQuote(script) + ' --host ' + shellQuote(values.host) +
      ' --port ' + String(values.port);
    if (!values.cors) command += ' --no-cors';
    return command;
  }

  function readForm() {
    var form = container && container.querySelector('[data-agent-server-form]');
    if (!form) return null;
    var port = parseInt(form.elements.port.value, 10);
    if (!form.elements.host.value.trim()) {
      form.elements.host.focus();
      throw new Error('Укажите host сервера.');
    }
    if (!Number.isInteger(port) || port < 1 || port > 65535) {
      form.elements.port.focus();
      throw new Error('Порт должен быть числом от 1 до 65535.');
    }
    return {
      python: form.elements.python.value.trim() || DEFAULTS.python,
      script: form.elements.script.value.trim() || DEFAULTS.script,
      cwd: form.elements.cwd.value.trim() || DEFAULTS.cwd,
      host: form.elements.host.value.trim(),
      port: port,
      cors: form.elements.cors.checked
    };
  }

  function setStatus(text, type) {
    var status = container && container.querySelector('[data-agent-server-status]');
    if (!status) return;
    status.className = 'agent-server-status ' + (type || 'info');
    status.textContent = text;
  }

  function renderOutput(values) {
    var command = makeCommand(values);
    var commandNode = container.querySelector('[data-agent-server-command]');
    var configNode = container.querySelector('[data-agent-server-config]');
    if (commandNode) commandNode.textContent = command;
    if (configNode) configNode.textContent = JSON.stringify(values, null, 2);
  }

  function saveFromForm(showStatus) {
    try {
      state = readForm();
      saveState();
      renderOutput(state);
      if (showStatus !== false) setStatus('Настройки сохранены локально. Команда готова к запуску в терминале.', 'success');
      return true;
    } catch (error) {
      setStatus(error.message, 'error');
      return false;
    }
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function() {
        setStatus('Команда скопирована в буфер обмена.', 'success');
      }).catch(function() { copyTextFallback(text); });
      return;
    }
    copyTextFallback(text);
  }

  function copyTextFallback(text) {
    var textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      setStatus('Команда скопирована в буфер обмена.', 'success');
    } catch (error) {
      setStatus('Не удалось скопировать команду. Выделите её вручную.', 'error');
    }
    document.body.removeChild(textarea);
  }

  function render() {
    var values = state || readState();
    container.innerHTML = '<div class="agent-server-shell">' +
      '<div class="agent-server-heading"><div>' +
        '<p class="agent-server-kicker">ХОШЕХ · ЛОКАЛЬНЫЙ КОНТУР</p>' +
        '<h2>Запуск сервера агентов</h2>' +
        '<p class="agent-server-intro">Заполните параметры процесса. Лаборатория сохранит конфигурацию и подготовит команду; сам процесс запускается в терминале на вашем компьютере.</p>' +
      '</div><img src="../../assets/icons/32/ui/arrows.png" alt="" aria-hidden="true"></div>' +
      '<form class="agent-server-form" data-agent-server-form>' +
        '<fieldset><legend>Среда запуска</legend>' +
          '<label>Интерпретатор Python<input name="python" class="lab-input" value="' + escapeHtml(values.python) + '" placeholder="python или путь к python.exe"></label>' +
          '<label>Рабочая папка<input name="cwd" class="lab-input" value="' + escapeHtml(values.cwd) + '" placeholder="products/agents"></label>' +
          '<label>Скрипт сервера<input name="script" class="lab-input" value="' + escapeHtml(values.script) + '" placeholder="server.py"></label>' +
        '</fieldset>' +
        '<fieldset><legend>Сетевой контур</legend>' +
          '<label>Host<input name="host" class="lab-input" value="' + escapeHtml(values.host) + '" placeholder="0.0.0.0" required></label>' +
          '<label>Порт<input name="port" class="lab-input" type="number" min="1" max="65535" value="' + escapeHtml(values.port) + '" required></label>' +
          '<label class="agent-server-check"><input name="cors" type="checkbox"' + (values.cors ? ' checked' : '') + '> Разрешить CORS для ResearchLab</label>' +
        '</fieldset>' +
        '<div class="agent-server-actions"><button type="submit" class="lab-btn lab-btn-primary">Сохранить и подготовить</button>' +
          '<button type="button" class="lab-btn lab-btn-secondary" data-agent-server-copy>Копировать команду</button>' +
          '<button type="button" class="lab-btn lab-btn-secondary" data-agent-server-back>← Назад к списку агентов</button></div>' +
      '</form>' +
      '<div class="agent-server-status info" data-agent-server-status role="status" aria-live="polite">Конфигурация загружена из локального хранилища.</div>' +
      '<div class="agent-server-output-grid"><section class="agent-server-output"><h3>Команда запуска</h3><pre data-agent-server-command></pre></section>' +
        '<section class="agent-server-output"><h3>Конфигурация</h3><pre data-agent-server-config></pre></section></div>' +
      '<p class="agent-server-note">После копирования откройте терминал в корне проекта и выполните команду. Проверка доступности: <code>http://localhost:' + escapeHtml(values.port) + '/api/run</code>. Закрытие — <kbd>Ctrl+C</kbd>.</p>' +
    '</div>';
    renderOutput(values);
    container.querySelector('[data-agent-server-form]').addEventListener('submit', function(event) {
      event.preventDefault();
      saveFromForm(true);
    });
    container.querySelector('[data-agent-server-copy]').addEventListener('click', function() {
      if (saveFromForm(false)) copyText(makeCommand(state));
    });
    container.querySelector('[data-agent-server-back]').addEventListener('click', close);
  }

  function close() {
    if (!container) return;
    saveFromForm(false);
    var list = container.querySelector('.agent-list-view');
    var mapView = container.querySelector('.agent-map-view');
    var serverView = container.querySelector('.agent-server-view');
    if (serverView) serverView.hidden = true;
    if (mapView) mapView.hidden = true;
    if (list) list.hidden = false;
  }

  function open() {
    container = document.getElementById('ai-agents');
    if (!container) return;
    var list = container.querySelector('.agent-list-view');
    var mapView = container.querySelector('.agent-map-view');
    var serverView = container.querySelector('.agent-server-view');
    if (!list || !serverView) return;
    state = readState();
    list.hidden = true;
    if (mapView) mapView.hidden = true;
    serverView.hidden = false;
    render();
  }

  window.AgentServer = { open: open, close: close };
})(window, document);