/**
 * paleo-glossary.js — интерфейс первой партии палео-глоссария.
 * Записи загружаются из локального JSON, чтобы данные и UI оставались разделены.
 */
const PaleoGlossary = (function() {
  'use strict';

  var PAGE_SIZE = 20;
  var words = [];
  var state = { query: '', root: 'all', page: 1, container: null, loading: false };

  function escapeHtml(value) {
    var node = document.createElement('div');
    node.textContent = value == null ? '' : String(value);
    return node.innerHTML;
  }

  function filteredWords() {
    var query = state.query.trim().toLowerCase();
    return words.filter(function(word) {
      var matchesRoot = state.root === 'all' || word.root === state.root;
      var haystack = [word.paleo, word.square, word.translit, word.function, word.root].join(' ').toLowerCase();
      return matchesRoot && (!query || haystack.indexOf(query) !== -1);
    });
  }

  function render() {
    var visible = filteredWords();
    var totalPages = Math.max(1, Math.ceil(visible.length / PAGE_SIZE));
    state.page = Math.min(state.page, totalPages);
    var start = (state.page - 1) * PAGE_SIZE;
    var pageWords = visible.slice(start, start + PAGE_SIZE);
    var grid = document.getElementById('paleo-glossary-grid');
    var meta = document.getElementById('paleo-glossary-meta');
    var pagination = document.getElementById('paleo-glossary-pagination');

    if (meta) meta.textContent = visible.length + ' слов · страница ' + state.page + ' из ' + totalPages;
    if (grid) {
      grid.innerHTML = pageWords.length ? pageWords.map(function(word) {
        return '<article class="paleo-glossary-card">' +
          '<div class="paleo-glossary-card-paleo" lang="hbo" dir="rtl">' + escapeHtml(word.paleo) + '</div>' +
          '<div class="paleo-glossary-card-translit">' + escapeHtml(word.translit) + '</div>' +
          '<p class="paleo-glossary-card-function">' + escapeHtml(word.function) + '</p>' +
          '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm paleo-glossary-details" data-paleo-word="' + escapeHtml(word.square) + '">Подробнее</button>' +
          '</article>';
      }).join('') : '<div class="lab-alert lab-alert-info">По запросу ничего не найдено.</div>';
      grid.querySelectorAll('.paleo-glossary-details').forEach(function(button) {
        button.addEventListener('click', function() { showDetails(this.getAttribute('data-paleo-word')); });
      });
    }
    if (pagination) {
      pagination.innerHTML = totalPages > 1 ? Array.from({ length: totalPages }, function(_, index) {
        var page = index + 1;
        return '<button type="button" class="paleo-glossary-page-btn' + (page === state.page ? ' active' : '') + '" data-page="' + page + '">' + page + '</button>';
      }).join('') : '';
      pagination.querySelectorAll('[data-page]').forEach(function(button) {
        button.addEventListener('click', function() { state.page = Number(this.getAttribute('data-page')); render(); });
      });
    }
  }

  function showDetails(square) {
    var word = words.find(function(item) { return item.square === square; });
    if (!word || !window.LabModal) return;
    LabModal.show(word.translit, '<div class="paleo-glossary-detail"><div class="paleo-glossary-detail-paleo" dir="rtl">' + escapeHtml(word.paleo) + '</div><p><strong>Квадратное письмо:</strong> ' + escapeHtml(word.square) + '</p><p><strong>Функция:</strong> ' + escapeHtml(word.function) + '</p><p><strong>Корень:</strong> ' + escapeHtml(word.root) + '</p></div>');
  }

  function init(container) {
    state.container = container;
    var rootSelect = document.getElementById('paleo-glossary-root');
    var search = document.getElementById('paleo-glossary-search');
    if (rootSelect) {
      rootSelect.addEventListener('change', function() { state.root = this.value; state.page = 1; render(); });
    }
    if (search) search.addEventListener('input', function() { state.query = this.value; state.page = 1; render(); });
    state.loading = true;
    if (document.getElementById('paleo-glossary-meta')) document.getElementById('paleo-glossary-meta').textContent = 'Загрузка свитка…';
    fetch('data/paleo-glossary/roots.json')
      .then(function(response) {
        if (!response.ok) throw new Error('roots.json: HTTP ' + response.status);
        return response.json();
      })
      .then(function(data) {
        words = Array.isArray(data) ? data.map(function(word) {
          // JSON хранит квадратное письмо в поле hebrew; UI использует square.
          return Object.assign({}, word, { square: word.square || word.hebrew || '' });
        }) : [];
        state.loading = false;
        if (rootSelect) {
          var roots = words.map(function(word) { return word.root; });
          rootSelect.innerHTML = '<option value="all">Все корни</option>' + roots.map(function(root) {
            return '<option value="' + escapeHtml(root) + '">' + escapeHtml(root) + '</option>';
          }).join('');
        }
        render();
      })
      .catch(function(error) {
        state.loading = false;
        console.error('[PaleoGlossary] Не удалось загрузить данные:', error);
        var meta = document.getElementById('paleo-glossary-meta');
        if (meta) meta.innerHTML = '<span class="text-warn">Не удалось открыть свиток глоссария.</span>';
      });
  }

  return { init: init };
})();

window.PaleoGlossary = PaleoGlossary;