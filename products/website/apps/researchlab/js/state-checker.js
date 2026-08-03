/**
 * state-checker.js — «Чекер стран»: диагностика страны по 8 состояниям пространств.
 * Данные: data/state-matrix.json. Результат: круговая диаграмма, доминирующее состояние,
 * текстовый диагноз в стиле «Голема», экспорт в Markdown.
 */
const StateChecker = (function() {
  'use strict';

  var STATES = [
    { key: 'tohu', label: 'Тоху', paleo: '𐤕𐤅𐤄', desc: 'Запертость. Остановка потока.' },
    { key: 'hoshekh', label: 'Хошех', paleo: '𐤇𐤔𐤊', desc: 'Сжатость. Блокировка потока.' },
    { key: 'mizraim', label: 'Мицраим', paleo: '𐤌𐤑𐤓𐤉𐤌', desc: 'Теснота. Принудительное направление потока.' },
    { key: 'rakia', label: 'Ракиа', paleo: '𐤓𐤒𐤉𐤏', desc: 'Разделение. Создание границы.' },
    { key: 'shamaim', label: 'Шамаим', paleo: '𐤔𐤌𐤉𐤌', desc: 'Открытость. Свободное течение потока.' },
    { key: 'midbar', label: 'Мидбар', paleo: '𐤌𐤃𐤁𐤓', desc: 'Движение. Калибровка потока через поиск.' },
    { key: 'erets', label: 'Эрец', paleo: '𐤀𐤓𐤑', desc: 'Опора. Фиксация потока на твёрдой поверхности.' },
    { key: 'eden', label: 'Эден', paleo: '𐤏𐤃𐤍', desc: 'Завершённость. Непрерывное течение жизни.' }
  ];

  var COLORS = ['#8e2f25', '#5c4a3a', '#b8860b', '#2f6b1f', '#6b9ec4', '#2455a4', '#8a5a2b', '#d4a030'];
  var CACHE_KEY = 'golem_state_checker_cache';
  var matrix = null;
  var loadPromise = null;

  // ===== ЗАГРУЗКА ДАННЫХ =====
  function loadMatrix() {
    if (matrix) return Promise.resolve(matrix);
    if (loadPromise) return loadPromise;
    loadPromise = fetch('data/state-matrix.json')
      .then(function(r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function(data) {
        matrix = data;
        return matrix;
      })
      .catch(function(err) {
        loadPromise = null;
        throw err;
      });
    return loadPromise;
  }

  function readCache() {
    try {
      return JSON.parse(localStorage.getItem(CACHE_KEY)) || {};
    } catch (e) {
      return {};
    }
  }

  function writeCache(cache) {
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
    } catch (e) {}
  }

  // ===== ПОИСК / ГЕНЕРАЦИЯ =====
  function findCountry(name) {
    var query = String(name || '').trim().toLowerCase();
    if (!query) return null;
    var countries = (matrix && matrix.countries) || [];
    var exact = countries.filter(function(c) { return c.name.toLowerCase() === query; })[0];
    if (exact) return exact;
    var partial = countries.filter(function(c) { return c.name.toLowerCase().indexOf(query) !== -1 || query.indexOf(c.name.toLowerCase()) !== -1; })[0];
    return partial || null;
  }

  // Если данных для страны нет — генерируем детерминированную матрицу по имени.
  function generateCountry(name) {
    var query = String(name || '').toLowerCase();
    var seed = 0;
    for (var i = 0; i < query.length; i += 1) seed = (seed * 31 + query.charCodeAt(i)) >>> 0;
    var values = STATES.map(function(s, idx) {
      var v = ((seed >> (idx * 3)) % 100) + 8;
      return { key: s.key, v: v };
    });
    var total = values.reduce(function(sum, item) { return sum + item.v; }, 0);
    var states = {};
    values.forEach(function(item) {
      states[item.key] = Math.round((item.v / total) * 100);
    });
    // Корректируем сумму до 100
    var sum = STATES.reduce(function(acc, s) { return acc + (states[s.key] || 0); }, 0);
    if (sum !== 100) {
      var diff = 100 - sum;
      states[values[0].key] += diff;
    }
    return { name: name, states: states, note: 'Сгенерировано автоматически по имени страны.' };
  }

  function getCountry(name) {
    var found = findCountry(name);
    if (found) return Promise.resolve(found);

    var cache = readCache();
    var query = String(name || '').trim().toLowerCase();
    if (cache[query]) return Promise.resolve(cache[query]);

    var generated = generateCountry(name);
    cache[query] = generated;
    writeCache(cache);
    return Promise.resolve(generated);
  }

  // ===== ДИАГНОЗ =====
  function dominantState(states) {
    var best = null;
    STATES.forEach(function(s) {
      var v = states[s.key] || 0;
      if (!best || v > best.value) best = { key: s.key, value: v };
    });
    return best;
  }

  function buildDiagnosis(country, dom) {
    var labels = {};
    STATES.forEach(function(s) { labels[s.key] = s.label; });
    var domLabel = labels[dom.key] || dom.key;
    var domDesc = '';
    STATES.forEach(function(s) { if (s.key === dom.key) domDesc = s.desc; });

    return 'Страна «' + country.name + '» находится под доминирующим состоянием ' + domLabel +
      ' (' + dom.value + '%). ' + domDesc + '\n\n' +
      'Это означает, что поток силы (𐤌) в данной стране ' +
      (dom.key === 'tohu' ? 'остановлен и заперт — система держит пространство в замкнутом круге.' :
      dom.key === 'hoshekh' ? 'сжат и блокирован — внешние структуры давят на среду, не давая ей раскрыться.' :
      dom.key === 'mizraim' ? 'захвачен и принудительно направлен — каналы тесноты управляют вниманием и ресурсами.' :
      dom.key === 'rakia' ? 'разделён и растянут — страна стоит на границе между естественным и искусственным.' :
      dom.key === 'shamaim' ? 'течёт свободно — пространство открыто для движения и обновления.' :
      dom.key === 'midbar' ? 'находится в поиске — калибруется через движение, испытания и разведку.' :
      dom.key === 'erets' ? 'закреплён на опоре — страна реализует устойчивость и возможность строить.' :
      'завершён и непрерывен — пространство достигло целостности и пребывания.');
  }

  // ===== КРУГОВАЯ ДИАГРАММА (SVG) =====
  function donutChart(states, size, dominantPct) {
    size = size || 260;
    var cx = size / 2;
    var cy = size / 2;
    var radius = size / 2 - 20;
    var innerRadius = radius - 36;
    var total = STATES.reduce(function(acc, s) { return acc + (states[s.key] || 0); }, 0) || 1;
    var angle = -90;
    var segments = '';
    var index = 0;

    STATES.forEach(function(s) {
      var value = states[s.key] || 0;
      if (value <= 0) return;
      var frac = value / total;
      var start = angle;
      var end = angle + frac * 360;
      angle = end;

      var large = (end - start) > 180 ? 1 : 0;
      var sx = cx + radius * Math.cos(start * Math.PI / 180);
      var sy = cy + radius * Math.sin(start * Math.PI / 180);
      var ex = cx + radius * Math.cos(end * Math.PI / 180);
      var ey = cy + radius * Math.sin(end * Math.PI / 180);

      var ix = cx + innerRadius * Math.cos(end * Math.PI / 180);
      var iy = cy + innerRadius * Math.sin(end * Math.PI / 180);
      var ixs = cx + innerRadius * Math.cos(start * Math.PI / 180);
      var iys = cy + innerRadius * Math.sin(start * Math.PI / 180);

      segments += '<path d="M ' + sx + ' ' + sy +
        ' A ' + radius + ' ' + radius + ' 0 ' + large + ' 1 ' + ex + ' ' + ey +
        ' L ' + ix + ' ' + iy +
        ' A ' + innerRadius + ' ' + innerRadius + ' 0 ' + large + ' 0 ' + ixs + ' ' + iys +
        ' Z" fill="' + COLORS[index % COLORS.length] + '" stroke="#f7f1e5" stroke-width="1.5">' +
        '<title>' + s.label + ': ' + value + '%</title></path>';
      index += 1;
    });

    return '<svg class="stc-chart" viewBox="0 0 ' + size + ' ' + size + '" role="img" aria-label="Диаграмма состояний">' +
      segments +
      '<text x="' + cx + '" y="' + (cy - 4) + '" text-anchor="middle" class="stc-chart-center-pct">' +
      (dominantPct != null ? dominantPct + '%' : '') +
      '</text>' +
      '<text x="' + cx + '" y="' + (cy + 16) + '" text-anchor="middle" class="stc-chart-center-label">доминирует</text>' +
      '</svg>';
  }

  // ===== MARKDOWN =====
  function toMarkdown(country, dom, diagnosis) {
    var lines = [];
    lines.push('# Чекер стран: ' + country.name);
    lines.push('');
    lines.push('## Доминирующее состояние');
    lines.push('');
    lines.push('**' + dom.label + ' (' + dom.value + '%)**');
    lines.push('');
    lines.push('## Распределение по 8 состояниям');
    lines.push('');
    STATES.forEach(function(s) {
      lines.push('- ' + s.label + ' (' + s.paleo + '): ' + (country.states[s.key] || 0) + '%');
    });
    lines.push('');
    lines.push('## Диагноз');
    lines.push('');
    lines.push(diagnosis);
    lines.push('');
    if (country.note) {
      lines.push('## Примечание');
      lines.push('');
      lines.push(country.note);
    }
    return lines.join('\n');
  }

  // ===== РЕНДЕР =====
  function render(container) {
    container.innerHTML =
      '<section class="state-checker-page">' +
        '<header class="stc-hero">' +
          '<div class="stc-hero-watermark" aria-hidden="true">𐤕 𐤇 𐤌 𐤓 𐤔 𐤌</div>' +
          '<p class="stc-kicker">ГОЛЕМ · ЧЕКЕР СТРАН</p>' +
          '<h1>Чекер стран</h1>' +
          '<p class="stc-subtitle">Диагностика стран по 8 состояниям пространств.</p>' +
        '</header>' +
        '<div class="stc-form-row">' +
          '<input type="text" id="stc-input" class="lab-input" placeholder="Введите страну" autocomplete="off" onkeydown="if(event.key===\'Enter\')StateChecker.check()" />' +
          '<button type="button" class="lab-btn lab-btn-primary" onclick="StateChecker.check()">Проверить</button>' +
        '</div>' +
        '<div id="stc-result"></div>' +
      '</section>';

    var input = document.getElementById('stc-input');
    if (input) input.focus();
  }

  function check() {
    var input = document.getElementById('stc-input');
    var result = document.getElementById('stc-result');
    if (!input || !result) return;
    var name = input.value.trim();
    if (!name) {
      result.innerHTML = '<div class="lab-alert lab-alert-warn">Введите страну.</div>';
      return;
    }
    result.innerHTML = '<div class="lab-spinner show"><div class="loader"></div><div class="spinner-text">Диагностика…</div></div>';

    loadMatrix()
      .then(function() { return getCountry(name); })
      .then(function(country) {
        renderResult(result, country);
      })
      .catch(function(err) {
        result.innerHTML = '<div class="lab-alert lab-alert-error">Ошибка: ' + escapeHtml(err.message) + '</div>';
      });
  }

  function renderResult(result, country) {
    var dom = dominantState(country.states);
    var diagnosis = buildDiagnosis(country, dom);
    var domState = null;
    STATES.forEach(function(s) { if (s.key === dom.key) domState = s; });

    var legend = STATES.map(function(s) {
      return '<div class="stc-legend-item">' +
        '<span class="stc-legend-dot" style="background:' + COLORS[STATES.indexOf(s) % COLORS.length] + '"></span>' +
        '<span class="stc-legend-label">' + s.paleo + ' ' + s.label + '</span>' +
        '<span class="stc-legend-value">' + (country.states[s.key] || 0) + '%</span>' +
        '</div>';
    }).join('');

    result.innerHTML =
      '<div class="stc-result-card">' +
        '<div class="stc-result-head">' +
          '<h2>' + escapeHtml(country.name) + '</h2>' +
          '<span class="stc-dom-badge">Доминирует: ' + escapeHtml(domState.label) + ' (' + dom.value + '%)</span>' +
        '</div>' +
        '<div class="stc-result-body">' +
          '<div class="stc-chart-wrap">' +
            '<div class="stc-chart-box">' + donutChart(country.states, 260, dom.value) + '</div>' +
            '<div class="stc-legend">' + legend + '</div>' +
          '</div>' +
          '<div class="stc-diagnosis">' +
            '<h3>Диагноз</h3>' +
            '<p>' + escapeHtml(diagnosis).replace(/\n/g, '<br>') + '</p>' +
            (country.note ? '<p class="stc-note">' + escapeHtml(country.note) + '</p>' : '') +
          '</div>' +
        '</div>' +
        '<div class="stc-actions">' +
          '<button type="button" class="lab-btn lab-btn-secondary lab-btn-sm" onclick="StateChecker.copy()">Копировать Markdown</button>' +
        '</div>' +
        '<div id="stc-copy-status" class="stc-copy-status" aria-live="polite"></div>' +
      '</div>';
  }

  function copy() {
    var name = document.getElementById('stc-input');
    var status = document.getElementById('stc-copy-status');
    if (!name || !name.value.trim()) return;
    getCountry(name.value.trim()).then(function(country) {
      var dom = dominantState(country.states);
      var diagnosis = buildDiagnosis(country, dom);
      var md = toMarkdown(country, dom, diagnosis);
      if (navigator.clipboard) {
        navigator.clipboard.writeText(md).then(function() {
          if (status) { status.textContent = 'Скопировано в буфер'; status.className = 'stc-copy-status stc-copy-ok'; }
        });
      } else {
        var ta = document.createElement('textarea');
        ta.value = md;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        if (status) { status.textContent = 'Скопировано в буфер'; status.className = 'stc-copy-status stc-copy-ok'; }
      }
    });
  }

  // Вспомогательная: escapeHtml
  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text == null ? '' : String(text);
    return d.innerHTML;
  }

  window.StateChecker = {
    init: render,
    render: render,
    check: check,
    copy: copy,
    loadMatrix: loadMatrix
  };
  return window.StateChecker;
})();