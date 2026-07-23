/**
 * prompt-generator.js — сборка исследовательских промптов
 */
(function(window, document) {
  'use strict';

  var PAGE_PATH = 'pages/prompt-generator.html';
  var DATA_PATH = 'data/prompts/index.json';

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function renderPrompt(template, values) {
    var result = template || '';

    result = result.replace(/{{#if\s+([\w-]+)}}([\s\S]*?){{\/if}}/g, function(_, name, body) {
      return values[name] ? body : '';
    });

    result = result.replace(/{{\s*([\w-]+)\s*}}/g, function(_, name) {
      return values[name] == null ? '' : String(values[name]);
    });

    return result.replace(/\n{3,}/g, '\n\n').trim();
  }

  function getValues(container) {
    var values = {};
    container.querySelectorAll('[data-prompt-field]').forEach(function(field) {
      values[field.name] = field.type === 'checkbox' ? field.checked : field.value.trim();
    });
    return values;
  }

  function updateCounter(container, text) {
    var counter = container.querySelector('#prompt-generator-counter');
    if (counter) counter.textContent = text.length + ' знаков';
  }

  function setStatus(container, message, type) {
    var status = container.querySelector('#prompt-generator-status');
    if (!status) return;
    status.textContent = message || '';
    status.className = 'prompt-generator-status' + (type ? ' is-' + type : '');
  }

  function renderFields(container, template, previousValues) {
    var fields = container.querySelector('#prompt-generator-fields');
    if (!fields) return;
    fields.innerHTML = '';

    (template.fields || []).forEach(function(field) {
      var wrapper = document.createElement('div');
      wrapper.className = 'prompt-generator-field';

      if (field.type === 'checkbox') {
        var label = document.createElement('label');
        label.className = 'prompt-generator-check';
        var checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.name = field.name;
        checkbox.setAttribute('data-prompt-field', '');
        checkbox.checked = previousValues[field.name] === true;
        label.appendChild(checkbox);
        var checkText = document.createElement('span');
        checkText.textContent = field.label || field.name;
        label.appendChild(checkText);
        wrapper.appendChild(label);
      } else {
        var textLabel = document.createElement('label');
        textLabel.className = 'prompt-generator-label';
        textLabel.setAttribute('for', 'prompt-field-' + field.name);
        textLabel.textContent = (field.label || field.name) + (field.required ? ' *' : '');
        var input = document.createElement('input');
        input.type = 'text';
        input.id = 'prompt-field-' + field.name;
        input.name = field.name;
        input.className = 'lab-input';
        input.setAttribute('data-prompt-field', '');
        input.placeholder = field.placeholder || '';
        input.required = Boolean(field.required);
        input.value = previousValues[field.name] || '';
        wrapper.appendChild(textLabel);
        wrapper.appendChild(input);
      }
      fields.appendChild(wrapper);
    });
  }

  function renderTemplateCards(container, templates, selectedId, selectTemplate) {
    var list = container.querySelector('#prompt-template-list');
    if (!list) return;
    list.innerHTML = '';
    templates.forEach(function(template) {
      var card = document.createElement('button');
      card.type = 'button';
      card.className = 'prompt-generator-template' + (template.id === selectedId ? ' is-selected' : '');
      card.setAttribute('data-template-id', template.id);
      card.setAttribute('role', 'listitem');
      var title = document.createElement('strong');
      title.textContent = template.title || template.id;
      var description = document.createElement('span');
      description.textContent = template.description || '';
      card.appendChild(title);
      card.appendChild(description);
      card.addEventListener('click', function() { selectTemplate(template.id); });
      list.appendChild(card);
    });
  }

  function copyText(container) {
    var output = container.querySelector('#prompt-generator-output');
    var status = container.querySelector('#prompt-generator-copy-status');
    if (!output || !output.value) return Promise.resolve(false);

    var copied = function() {
      if (status) status.textContent = 'Скопировано';
      return true;
    };

    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(output.value).then(copied).catch(function() {
        return fallbackCopy(output) ? copied() : false;
      });
    }
    return Promise.resolve(fallbackCopy(output) ? copied() : false);
  }

  function fallbackCopy(output) {
    output.focus();
    output.select();
    try {
      return document.execCommand('copy');
    } catch (error) {
      return false;
    }
  }

  function init(container) {
    if (!container || container.dataset.promptGeneratorReady === '1') return;
    container.dataset.promptGeneratorReady = '1';
    container.innerHTML = '<div class="prompt-generator-loading">Загрузка генератора…</div>';

    Promise.all([
      fetch(PAGE_PATH).then(function(response) {
        if (!response.ok) throw new Error('HTTP ' + response.status + ' for ' + PAGE_PATH);
        return response.text();
      }),
      fetch(DATA_PATH).then(function(response) {
        if (!response.ok) throw new Error('HTTP ' + response.status + ' for ' + DATA_PATH);
        return response.json();
      })
    ]).then(function(result) {
      var templates = result[1].templates || [];
      if (!templates.length) throw new Error('Шаблоны не найдены');
      container.innerHTML = result[0];

      var select = container.querySelector('#prompt-template-select');
       var modelSelect = container.querySelector('#prompt-generator-model');
      var description = container.querySelector('#prompt-template-description');
      var form = container.querySelector('#prompt-generator-form');
      var output = container.querySelector('#prompt-generator-output');
      var copyButton = container.querySelector('#prompt-generator-copy');
      var valuesByTemplate = {};
      var currentTemplate = null;

      function selectTemplate(id) {
        currentTemplate = templates.filter(function(template) { return template.id === id; })[0] || templates[0];
        valuesByTemplate[currentTemplate.id] = valuesByTemplate[currentTemplate.id] || {};
        if (select) select.value = currentTemplate.id;
        if (description) description.textContent = currentTemplate.description || '';
        renderFields(container, currentTemplate, valuesByTemplate[currentTemplate.id]);
        renderTemplateCards(container, templates, currentTemplate.id, selectTemplate);
        setStatus(container, '', '');
      }

      function generate() {
        if (!currentTemplate) return;
        var values = getValues(container);
        var missing = (currentTemplate.fields || []).filter(function(field) {
          return field.required && field.type !== 'checkbox' && !values[field.name];
        });
        if (missing.length) {
          setStatus(container, 'Заполните поле: ' + (missing[0].label || missing[0].name), 'error');
          var missingInput = container.querySelector('[name="' + missing[0].name + '"]');
          if (missingInput) missingInput.focus();
          return;
        }
        valuesByTemplate[currentTemplate.id] = values;
         var model = modelSelect ? modelSelect.value : 'Claude';
         var prompt = 'Целевая нейросеть: ' + model + '\n\n' + renderPrompt(currentTemplate.prompt_template, values);
        if (output) output.value = prompt;
        if (copyButton) copyButton.disabled = !prompt;
        updateCounter(container, prompt);
        setStatus(container, 'Промпт собран. Проверьте формулировки перед отправкой.', 'success');
      }

      if (select) select.addEventListener('change', function() { selectTemplate(this.value); });
      if (form) form.addEventListener('submit', function(event) { event.preventDefault(); generate(); });
      if (copyButton) copyButton.addEventListener('click', function() {
        copyButton.disabled = true;
        copyText(container).then(function(success) {
          copyButton.disabled = !output || !output.value;
          if (!success) {
            var copyStatus = container.querySelector('#prompt-generator-copy-status');
            if (copyStatus) copyStatus.textContent = 'Не удалось скопировать';
          }
        });
      });

      selectTemplate(templates[0].id);
    }).catch(function(error) {
      container.innerHTML = '<div class="lab-alert lab-alert-error">Не удалось загрузить генератор: ' + escapeHtml(error.message) + '</div>';
      container.dataset.promptGeneratorReady = '0';
    });
  }

  window.PromptGenerator = {
    init: init,
    renderPrompt: renderPrompt
  };
})(window, document);