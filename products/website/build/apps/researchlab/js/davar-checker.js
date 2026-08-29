/**
 * Давар-чекер — проверка физической воплощаемости слова.
 */
(function(window, document) {
  'use strict';

  var PAGE_PATH = 'pages/davar-checker.html';
  var davarList = ['вода', 'дверь', 'рука', 'рыба', 'ветер', 'дом', 'хлеб', 'земля'];
  var noiseList = ['духовность', 'самореализация', 'энергия', 'ресурс', 'травма'];

  function getNode(root, selector) {
    return root && root.querySelector ? root.querySelector(selector) : document.querySelector(selector);
  }

  function showResult(root, kind, message) {
    var result = getNode(root, '#davar-checker-result');
    if (!result) return;
    result.className = 'davar-checker-result davar-checker-result-' + kind;
    result.textContent = message;
    result.hidden = false;
  }

  function check(root) {
    root = root || document;
    var input = getNode(root, '#davar-checker-input');
    if (!input) return '';

    var word = input.value.trim().toLowerCase();
    if (!word) {
      showResult(root, 'warn', 'Введите слово');
      return 'Введите слово';
    }

    if (davarList.indexOf(word) !== -1) {
      showResult(root, 'davar', 'Это Давар — воплощается в реальность');
      return 'Это Давар — воплощается в реальность';
    }

    if (noiseList.indexOf(word) !== -1) {
      showResult(root, 'noise', 'Это Шум — пустой звук');
      return 'Это Шум — пустой звук';
    }

    showResult(root, 'unknown', 'Неизвестно. Проверь через палео-сборку');
    return 'Неизвестно. Проверь через палео-сборку';
  }

  function bind(container) {
    var form = container.querySelector('#davar-checker-form');
    var input = container.querySelector('#davar-checker-input');
    if (!form || !input) return;

    form.addEventListener('submit', function(event) {
      event.preventDefault();
      check(container);
    });
    input.focus();
  }

  function init(container) {
    if (!container) return;
    if (container.dataset.loaded === '1' || container.dataset.loading === '1') return;
    container.dataset.loading = '1';

    fetch(PAGE_PATH)
      .then(function(response) {
        if (!response.ok) throw new Error('HTTP ' + response.status + ' for ' + PAGE_PATH);
        return response.text();
      })
      .then(function(markup) {
        container.innerHTML = markup;
        container.dataset.loaded = '1';
        delete container.dataset.loading;
        bind(container);
      })
      .catch(function(error) {
        delete container.dataset.loading;
        container.innerHTML = '<div class="lab-alert lab-alert-error">Не удалось загрузить Давар-чекер: ' + error.message + '</div>';
      });
  }

  window.DavarChecker = {
    init: init,
    check: function() { return check(document); },
    davarList: davarList,
    noiseList: noiseList
  };
})(window, document);