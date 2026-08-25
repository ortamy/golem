const EdChat = (function() {
  'use strict';

  const STORAGE_KEY = 'golem_ed_chat';
  const HISTORY_KEY = 'golem_ed_chat_history';
  const SETTINGS_KEY = 'golem_ed_chat_settings';
  const TOKEN_LIMIT = 4096;
  const CONTEXT_DOCUMENTS = ['MANIFEST.md', 'docs/06-METHODOLOGY/', 'docs/01-ARCHITECTURE/ARCHITECTURE.md'];
  const MODELS = {
    claude: { name: 'Claude Sonnet 4', style: 'структурно, спокойно и подробно' },
    gpt4o: { name: 'GPT-4o', style: 'кратко, ясно и по пунктам' },
    deepseek: { name: 'DeepSeek', style: 'аналитично, с проверкой корней и связей' },
    gemini: { name: 'Gemini', style: 'с образными аналогиями и несколькими ракурсами' }
  };
  const DEFAULT_PROMPT = 'Палео-исследовательский режим: возвращать физику образа, показывать подмены и отделять факт от гипотезы.';
  const DEMO_RESPONSES = [
    'Запрос принят. Разберу его через образ, движение и возможную подмену смысла.',
    'Вижу здесь несколько слоёв. Сначала отделю наблюдаемое от интерпретации, затем проверю связь корней.',
    'Для точного разбора нужен контекст: кто действует, что меняется и какое движение скрыто за формулировкой.'
  ];

  let messages = [];
  let settings = { model: 'claude', prompt: DEFAULT_PROMPT };

  function read(key, fallback) {
    try {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : fallback;
    } catch (error) {
      return fallback;
    }
  }

  function write(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      // Локальное хранилище может быть недоступно в приватном режиме.
    }
  }

  function byId(id) {
    return document.getElementById(id);
  }

  function model() {
    return MODELS[settings.model] || MODELS.claude;
  }

  function tokenCount(text) {
    return Math.ceil(String(text || '').length / 4);
  }

  function hasApiKey() {
    return Boolean(localStorage.getItem('golem_hf_api_key') || localStorage.getItem('golem_api_key'));
  }

  function init() {
    messages = read(STORAGE_KEY, []);
    settings = Object.assign(settings, read(SETTINGS_KEY, {}));
    if (!MODELS[settings.model]) settings.model = 'claude';
    const select = byId('ec-model');
    const prompt = byId('ec-prompt');
    if (select) {
      select.value = settings.model;
      select.addEventListener('change', function() {
        settings.model = select.value;
        write(SETTINGS_KEY, settings);
        renderContext();
        renderTokens();
      });
    }
    if (prompt) {
      prompt.value = settings.prompt;
      prompt.addEventListener('input', function() {
        settings.prompt = prompt.value;
        write(SETTINGS_KEY, settings);
        renderContext();
      });
    }
    renderMessages();
    renderContext();
    renderTokens();
    renderHistory();
  }

  function renderMessages() {
    const container = byId('ec-messages');
    if (!container) return;
    container.textContent = '';
    if (!messages.length) {
      const welcome = document.createElement('div');
      welcome.className = 'text-muted ec-welcome';
      welcome.textContent = 'Начните диалог.';
      container.appendChild(welcome);
      return;
    }
    messages.forEach(function(message) {
      const item = document.createElement('article');
      item.className = 'ec-message ec-message-' + (message.role === 'user' ? 'user' : 'assistant');
      const meta = document.createElement('div');
      meta.className = 'ec-message-meta';
      meta.textContent = message.role === 'user' ? 'Вы' : (message.model || model().name);
      const body = document.createElement('div');
      body.className = 'ec-message-body';
      body.textContent = message.text || '';
      item.appendChild(meta);
      item.appendChild(body);
      container.appendChild(item);
    });
    container.scrollTop = container.scrollHeight;
  }

  function renderContext() {
    const documents = byId('ec-context-documents');
    const prompt = byId('ec-prompt');
    const label = byId('ec-model-label');
    if (documents) {
      documents.textContent = '';
      CONTEXT_DOCUMENTS.forEach(function(documentName) {
        const item = document.createElement('li');
        item.textContent = documentName;
        documents.appendChild(item);
      });
    }
    if (prompt && document.activeElement !== prompt) prompt.value = settings.prompt;
    if (label) label.textContent = model().name + ' · ' + model().style;
  }

  function renderTokens() {
    const indicator = byId('ec-tokens');
    if (!indicator) return;
    if (!hasApiKey()) {
      indicator.hidden = true;
      return;
    }
    const used = messages.reduce(function(total, message) {
      return total + tokenCount(message.text);
    }, tokenCount(settings.prompt));
    indicator.hidden = false;
    indicator.textContent = 'Токены: ' + Math.min(used, TOKEN_LIMIT) + ' использовано · ' + Math.max(0, TOKEN_LIMIT - used) + ' осталось';
  }

  function send() {
    const input = byId('ec-input');
    if (!input || !input.value.trim()) return;
    const text = input.value.trim();
    input.value = '';
    messages.push({ role: 'user', text: text, date: new Date().toISOString(), model: model().name });
    saveMessages();
    renderMessages();
    renderTokens();
    window.setTimeout(function() {
      messages.push({ role: 'assistant', text: createResponse(text), date: new Date().toISOString(), model: model().name });
      saveMessages();
      renderMessages();
      renderTokens();
    }, 450);
  }

  function createResponse(text) {
    const sample = DEMO_RESPONSES[messages.length % DEMO_RESPONSES.length];
    return model().name + ': ' + sample + '\n\nФокус ответа: ' + model().style + '.\nПромпт: ' + settings.prompt + '\n\nИсходный запрос: «' + text + '»';
  }

  function saveMessages() {
    write(STORAGE_KEY, messages);
  }

  function saveDialog() {
    if (!messages.length) return;
    const defaultTitle = 'Нейрочат · ' + new Date().toLocaleDateString('ru-RU');
    const title = window.prompt('Название диалога:', defaultTitle);
    if (!title || !title.trim()) return;
    const history = read(HISTORY_KEY, []);
    history.unshift({ title: title.trim(), date: new Date().toISOString(), model: model().name, messages: messages.slice() });
    write(HISTORY_KEY, history.slice(0, 30));
    renderHistory();
  }

  function renderHistory() {
    const container = byId('ec-history');
    if (!container) return;
    const history = read(HISTORY_KEY, []);
    container.textContent = '';
    if (!history.length) {
      container.textContent = 'Сохранённых диалогов пока нет.';
      return;
    }
    history.forEach(function(dialog, index) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'ec-history-item';
      button.dataset.index = String(index);
      button.textContent = dialog.title + ' · ' + new Date(dialog.date).toLocaleDateString('ru-RU');
      button.addEventListener('click', function() { loadHistory(index); });
      container.appendChild(button);
    });
  }

  function loadHistory(index) {
    const history = read(HISTORY_KEY, []);
    const dialog = history[index];
    if (!dialog) return;
    messages = Array.isArray(dialog.messages) ? dialog.messages : [];
    settings.model = Object.keys(MODELS).find(function(key) { return MODELS[key].name === dialog.model; }) || settings.model;
    saveMessages();
    write(SETTINGS_KEY, settings);
    const select = byId('ec-model');
    if (select) select.value = settings.model;
    renderMessages();
    renderContext();
    renderTokens();
  }

  function exportDialog() {
    if (!messages.length) return;
    const markdown = messages.map(function(message) {
      return '## ' + (message.role === 'user' ? 'Вы' : (message.model || model().name)) + '\n\n' + message.text;
    }).join('\n\n');
    const blob = new Blob(['# Нейрочат\n\nМодель: ' + model().name + '\nДата: ' + new Date().toLocaleString('ru-RU') + '\n\n' + markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'neurochat-' + new Date().toISOString().slice(0, 10) + '.md';
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function useInPromptGenerator() {
    const input = byId('ec-input');
    const text = input && input.value.trim() ? input.value.trim() : (messages.filter(function(message) { return message.role === 'user'; }).pop() || {}).text;
    if (!text || !window.LabRouter) return;
    window.LabRouter.navigate('prompt-generator');
    window.setTimeout(function() {
      if (window.PromptGenerator && window.PromptGenerator.addExternalBlock) {
        window.PromptGenerator.addExternalBlock('Запрос из Нейрочата', text);
      }
    }, 100);
  }

  function clearChat() {
    messages = [];
    saveMessages();
    renderMessages();
    renderTokens();
  }

  return { init: init, send: send, clear: clearChat, save: saveDialog, export: exportDialog, useInPromptGenerator: useInPromptGenerator, loadHistory: loadHistory };
})();

window.EdChat = EdChat;