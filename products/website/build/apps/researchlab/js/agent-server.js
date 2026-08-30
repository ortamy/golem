(function(window, document) {
  'use strict';

  // v2: актуализированные дефолты (порт 5000, host 127.0.0.1) и реальное
  // управление сервером из интерфейса: статус, остановка, перезапуск, запуск через .bat.
  var STORAGE_KEY = 'golem_agent_server_v2';
  var DEFAULTS = {
    python: 'python',
    script: 'server.py',
    cwd: 'products/agents',
    host: '127.0.0.1',
    port: 5000,
    cors: true
  };
  var container = null;
  var state = null;
  var pollTimer = null;
  var ONLINE = false;
  var LAST_INFO = null;

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

  function trimValue(form, name, fallback) {
    return (form.elements[name].value || '').trim() || fallback;
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

  function makeStartBat(values) {
    var python = values.python.trim() || DEFAULTS.python;
    var script = values.script.trim() || DEFAULTS.script;
    var cwd = values.cwd.trim() || DEFAULTS.cwd;
    return [
      '@echo off',
      'setlocal',
      'cd /d ' + shellQuote(cwd),
      'REM GOLEM: запуск сервера агентов и Лаборатории',
      (/[\\/\s]/.test(python) ? shellQuote(python) : python) + ' ' + shellQuote(script) +
        ' --host ' + shellQuote(values.host) + ' --port ' + String(values.port) +
        (values.cors ? '' : ' --no-cors'),
      'if errorlevel 1 (',
      '  echo. & echo Ошибка запуска. Проверьте Python и зависимости.',
      '  pause',
      ')',
      'endlocal'
    ].join('\r\n');
  }

  function makeStopBat(values) {
    return [
      '@echo off',
      'setlocal',
      'set PORT=' + String(values.port),
      'REM GOLEM: остановка сервера по порту',
      'for /f "tokens=5" %%a in (\'netstat -aon ^| findstr :%PORT% ^| findstr LISTENING\') do taskkill /f /pid %%a',
      'endlocal'
    ].join('\r\n');
  }

  function baseUrl(values) {
    return 'http://' + (values.host.trim() || DEFAULTS.host) + ':' + values.port;
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
      python: trimValue(form, 'python', DEFAULTS.python),
      script: trimValue(form, 'script', DEFAULTS.script),
      cwd: trimValue(form, 'cwd', DEFAULTS.cwd),
      host: form.elements.host.value.trim(),
      port: port,
      cors: form.elements.cors.checked
    };
  }

  function setStatus(text, type, meta) {
    var status = container && container.querySelector('[data-agent-server-status]');
    if (!status) return;
    var dot = status.querySelector('.agent-server-status-dot');
    if (dot) dot.dataset.state = type || 'info';
    var textNode = status.querySelector('[data-agent-server-status-text]');
    if (textNode) textNode.textContent = text;
    var metaNode = status.querySelector('[data-agent-server-status-meta]');
    if (metaNode) metaNode.textContent = meta || '';
  }

  function renderOutput(values) {
    var command = makeCommand(values);
    var commandNode = container.querySelector('[data-agent-server-command]');
    var configNode = container.querySelector('[data-agent-server-config]');
    if (commandNode) commandNode.textContent = command;
    if (configNode) configNode.textContent = JSON.stringify(values, null, 2);
  }

  function refreshControls(online) {
    ONLINE = online;
    var controls = container && container.querySelector('[data-agent-server-controls]');
    if (!controls) return;
    var stopBtn = controls.querySelector('[data-agent-server-stop]');
    var restartBtn = controls.querySelector('[data-agent-server-restart]');
    var openBtn = controls.querySelector('[data-agent-server-open]');
    if (stopBtn) stopBtn.disabled = !online;
    if (restartBtn) restartBtn.disabled = !online;
    if (openBtn) {
      openBtn.hidden = !online;
      openBtn.href = baseUrl(state || DEFAULTS) + '/apps/researchlab/';
    }
  }

  function checkServer(manual) {
    var values = state || readState();
    var base = baseUrl(values);
    if (manual) setStatus('Проверка доступности…', 'info');
    return fetch(base + '/api/health', { cache: 'no-store' })
      .then(function(response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.json();
      })
      .then(function() {
        return fetch(base + '/api/info', { cache: 'no-store' }).then(function(r) {
          if (r.ok) return r.json();
          return {};
        });
      })
      .then(function(info) {
        LAST_INFO = info || {};
        refreshControls(true);
        var uptime = LAST_INFO.uptime ? ' · работает ' + LAST_INFO.uptime + ' с' : '';
        var pid = LAST_INFO.pid ? ' · pid ' + LAST_INFO.pid : '';
        var py = LAST_INFO.python ? ' · Python ' + LAST_INFO.python : '';
        setStatus('Сервер работает' + uptime + pid + py, 'success');
      })
      .catch(function() {
        LAST_INFO = null;
        refreshControls(false);
        setStatus('Сервер не отвечает на ' + base + '. Первый запуск — через start-server.bat.', 'error');
      });
  }

  function saveFromForm(showStatus) {
    try {
      state = readForm();
      saveState();
      renderOutput(state);
      if (showStatus !== false) setStatus('Настройки сохранены. Проверьте доступность сервера.', 'success');
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

  function downloadFile(name, content) {
    try {
      var blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      var url = URL.createObjectURL(blob);
      var link = document.createElement('a');
      link.href = url;
      link.download = name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setTimeout(function() { URL.revokeObjectURL(url); }, 1500);
      setStatus('Файл ' + name + ' создан. Дважды щёлкните его для запуска сервера.', 'success');
    } catch (error) {
      setStatus('Не удалось создать файл: ' + error.message, 'error');
    }
  }

  function postLab(action) {
    var values = state || readState();
    var base = baseUrl(values);
    setStatus((action === 'shutdown' ? 'Остановка' : 'Перезапуск') + ' сервера…', 'info');
    return fetch(base + '/api/lab/' + action, { method: 'POST', cache: 'no-store' })
      .then(function(response) { return response.json(); })
      .then(function(body) {
        if (body && body.stopped) {
          refreshControls(false);
          setStatus('Сервер остановлен. Для повторного запуска — start-server.bat.', 'error');
        } else if (body && body.restarted) {
          setStatus('Сервер перезапускается в новом окне. Обновите страницу через несколько секунд.', 'success');
          setTimeout(function() { checkServer(true); }, 3000);
        } else {
          setStatus((action === 'shutdown' ? 'Остановка' : 'Перезапуск') + ' не выполнена.', 'error');
        }
      })
      .catch(function() {
        // При остановке сервер умирает раньше ответа — это нормально.
        if (action === 'shutdown') {
          refreshControls(false);
          setStatus('Сервер остановлен.', 'error');
        } else {
          setStatus('Не удалось перезапустить: сервер недоступен.', 'error');
          refreshControls(false);
        }
      });
  }

  function render() {
    var values = state || readState();
    container.innerHTML = '<div class="agent-server-shell">' +
      '<form class="agent-server-form" data-agent-server-form>' +
        '<fieldset><legend>Среда запуска</legend>' +
          '<label>Интерпретатор Python<input name="python" class="lab-input" value="' + escapeHtml(values.python) + '" placeholder="python или путь к python.exe"></label>' +
          '<label>Рабочая папка<input name="cwd" class="lab-input" value="' + escapeHtml(values.cwd) + '" placeholder="products/agents"></label>' +
          '<label>Скрипт сервера<input name="script" class="lab-input" value="' + escapeHtml(values.script) + '" placeholder="server.py"></label>' +
        '</fieldset>' +
        '<fieldset><legend>Сетевой контур</legend>' +
          '<label>Host<input name="host" class="lab-input" value="' + escapeHtml(values.host) + '" placeholder="127.0.0.1" required></label>' +
          '<label>Порт<input name="port" class="lab-input" type="number" min="1" max="65535" value="' + escapeHtml(values.port) + '" required></label>' +
          '<label class="agent-server-check"><input name="cors" type="checkbox"' + (values.cors ? ' checked' : '') + '> Разрешить CORS для ResearchLab</label>' +
        '</fieldset>' +
        '<div class="agent-server-actions"><button type="submit" class="lab-btn lab-btn-primary">Сохранить</button>' +
          '<button type="button" class="lab-btn lab-btn-secondary" data-agent-server-check>Проверить сервер</button>' +
          '<button type="button" class="lab-btn lab-btn-secondary" data-agent-server-copy>Копировать команду</button></div>' +
      '</form>' +
      '<div class="agent-server-status info" data-agent-server-status role="status" aria-live="polite"><span class="agent-server-status-dot" data-state="info"></span><span data-agent-server-status-text>Проверка доступности…</span><small data-agent-server-status-meta></small></div>' +
      '<div class="agent-server-actions" data-agent-server-controls>' +
        '<a class="lab-btn lab-btn-primary" data-agent-server-open href="#" hidden>Открыть лабораторию</a>' +
        '<button type="button" class="lab-btn lab-btn-secondary" data-agent-server-restart disabled>Перезапустить сервер</button>' +
        '<button type="button" class="lab-btn lab-btn-secondary agent-server-stop" data-agent-server-stop disabled>Остановить сервер</button>' +
        '<button type="button" class="lab-btn lab-btn-secondary" data-agent-server-start-download>Скачать start-server.bat</button>' +
        '<button type="button" class="lab-btn lab-btn-secondary" data-agent-server-stop-download>Скачать stop-server.bat</button>' +
      '</div>' +
      '<div class="agent-server-output-grid"><section class="agent-server-output"><h3>Команда запуска</h3><pre data-agent-server-command></pre></section>' +
        '<section class="agent-server-output"><h3>Конфигурация</h3><pre data-agent-server-config></pre></section></div>' +
      '<div class="lab-alert lab-alert-info agent-server-alert">Браузер не может запускать процессы на компьютере, поэтому <b>первый</b> запуск — один клик: скачайте <b>start-server.bat</b> и дважды щёлкните файл (или выполните команду в терминале). После этого панель покажет статус, а остановка, перезапуск и открытие Лаборатории работают прямо здесь: <code>http://' + escapeHtml(values.host) + ':' + escapeHtml(values.port) + '/apps/researchlab/</code>.</div>' +
    '</div>';
    renderOutput(values);
    container.querySelector('[data-agent-server-form]').addEventListener('submit', function(event) {
      event.preventDefault();
      saveFromForm(true);
    });
    container.querySelector('[data-agent-server-check]').addEventListener('click', function() {
      if (saveFromForm(false)) checkServer(true);
    });
    container.querySelector('[data-agent-server-copy]').addEventListener('click', function() {
      if (saveFromForm(false)) copyText(makeCommand(state));
    });
    container.querySelector('[data-agent-server-stop]').addEventListener('click', function() {
      if (window.confirm('Остановить локальный сервер агентов (порт ' + (state || readState()).port + ')?')) {
        postLab('shutdown');
      }
    });
    container.querySelector('[data-agent-server-restart]').addEventListener('click', function() {
      if (window.confirm('Перезапустить сервер в новом окне? Текущий процесс завершится.')) {
        postLab('restart');
      }
    });
    container.querySelector('[data-agent-server-start-download]').addEventListener('click', function() {
      if (saveFromForm(false)) downloadFile('start-server.bat', makeStartBat(state));
    });
    container.querySelector('[data-agent-server-stop-download]').addEventListener('click', function() {
      if (saveFromForm(false)) downloadFile('stop-server.bat', makeStopBat(state));
    });
    refreshControls(false);
    checkServer(false);
  }

  function close() {
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
    if (container) saveFromForm(false);
    if (window.LabRouter) window.LabRouter.navigate('ai-agents');
  }

  function open(target) {
    container = target || document.getElementById('agent-server');
    if (!container) return;
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
    state = readState();
    render();
    pollTimer = setInterval(function() {
      if (container && container.isConnected) checkServer(false);
    }, 7000);
  }

  window.AgentServer = { open: open, close: close };
})(window, document);