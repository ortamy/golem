/**
 * states.js — Модуль «Карта состояний»
 *
 * 7 пространств палео-механики: Тоху → Хошех → Мицраим → Мидбар → Шамаим → Эрец → Эден.
 * - Карточки состояний с палео-символами и описанием
 * - Страница каждого состояния с палео-разбором, переходами и городами
 * - Диагностика: вопросы → определение текущего состояния → рекомендация перехода
 *
 * Маршрут: #states
 * Подмаршруты: #states?state=tohu, #states?diagnostic=true
 */

const GolemStates = (function() {
  'use strict';

  const STATES_DATA_PATH = 'data/states.json';
  const CARTOGRAPHY_PATH = 'data/cartography.json';

  let states = [];
  let statesById = {};
  let cartographyEntries = [];
  let dataPromise = null;

  // Состояние модуля
  let currentView = 'grid'; // 'grid' | 'detail' | 'diagnostic'
  let currentStateId = null;
  let diagnosticState = {
    currentQuestion: 0,
    answers: {},
    completed: false
  };

  // ===== УТИЛИТЫ =====
  function escapeHtml(text) {
    var d = document.createElement('div');
    d.textContent = text == null ? '' : String(text);
    return d.innerHTML;
  }

  function dataPath(path) {
    return new URL(path, document.baseURI).href;
  }

  // ===== ИНИЦИАЛИЗАЦИЯ =====
  function init(parsed) {
    var container = document.getElementById('states');
    if (!container) return;

    // Повторно применяем маршрут при каждом hashchange.
    if (states.length && cartographyEntries.length) {
      checkRouteParams(parsed);
      renderView(container);
      return;
    }

    loadData(container);
  }

  // ===== ЗАГРУЗКА ДАННЫХ =====
  function loadData(target) {
    var container = target || document.getElementById('states');
    if (!container) return;

    if (states.length && cartographyEntries.length) {
      checkRouteParams();
      renderView(container);
      return;
    }

    if (dataPromise) return dataPromise;

    container.innerHTML = '<div class="lab-spinner show"><div class="loader"></div><div class="spinner-text">Загрузка карты состояний...</div></div>';

    dataPromise = Promise.all([
      fetch(dataPath(STATES_DATA_PATH)).then(function(r) {
        if (!r.ok) throw new Error('HTTP ' + r.status + ' for states.json');
        return r.json();
      }),
      fetch(dataPath(CARTOGRAPHY_PATH)).then(function(r) {
        if (!r.ok) throw new Error('HTTP ' + r.status + ' for cartography.json');
        return r.json();
      })
    ])
    .then(function(results) {
      var statesData = results[0];
      var cartData = results[1];

      var list = Array.isArray(statesData) ? statesData : (statesData && Array.isArray(statesData.states) ? statesData.states : null);
      if (!list) throw new Error('Неверный формат states.json');
      states = list.filter(function(s) { return s && s.id && s.name; });
      statesById = {};
      states.forEach(function(s) { statesById[s.id] = s; });

      var cartList = Array.isArray(cartData) ? cartData : (cartData && Array.isArray(cartData.entries) ? cartData.entries : null);
      if (cartList) cartographyEntries = cartList.filter(function(e) { return e && e.id && e.name; });

      // Проверяем query-параметры при загрузке
      checkRouteParams();
      renderView(container);
    })
    .catch(function(error) {
      dataPromise = null;
      container.innerHTML = '<div class="lab-alert lab-alert-error">Ошибка загрузки: ' + escapeHtml(error.message) + '</div>';
      throw error;
    });

    dataPromise.catch(function() {});
    return dataPromise;
  }

  // ===== ПРОВЕРКА QUERY-ПАРАМЕТРОВ URL =====
  function checkRouteParams(parsed) {
    parsed = parsed || (LabRouter.parseHash ? LabRouter.parseHash() : { params: {} });
    var params = parsed.params || {};

    if (params.state && statesById[params.state]) {
      currentView = 'detail';
      currentStateId = params.state;
    } else if (params.diagnostic === 'true') {
      currentView = 'diagnostic';
    } else {
      currentView = 'grid';
      currentStateId = null;
    }
  }

  // ===== ОСНОВНОЙ РЕНДЕР =====
  function renderView(container) {
    if (!states.length) {
      container.innerHTML = '<div class="lab-alert lab-alert-info">Карта состояний пока пуста.</div>';
      return;
    }

    var html = '';

    if (currentView === 'detail' && currentStateId) {
      html = renderStateDetail(currentStateId);
    } else if (currentView === 'diagnostic') {
      html = renderDiagnostic();
    } else {
      html = renderGrid();
    }

    container.innerHTML = html;
    attachHandlers(container);
  }

  function attachHandlers(container) {
    // Клики по карточкам состояний
    container.querySelectorAll('.state-card').forEach(function(card) {
      card.addEventListener('click', function() {
        var id = this.getAttribute('data-state-id');
        if (id) openState(id);
      });
    });

    // Клики по переходам
    container.querySelectorAll('.transition-item').forEach(function(item) {
      item.addEventListener('click', function() {
        var id = this.getAttribute('data-to');
        if (id) openState(id);
      });
    });

    // Клики по городам (открыть в картографии)
    container.querySelectorAll('.state-city-card').forEach(function(card) {
      card.addEventListener('click', function() {
        var id = this.getAttribute('data-city-id');
        if (id && window.Cartography) {
          Cartography.showDetail(id);
        }
      });
    });
  }

  // ===== РЕНДЕР СЕТКИ КАРТОЧЕК =====
  function renderGrid() {
    // Сортируем: сначала сжатые, потом открытые
    var sorted = states.slice().sort(function(a, b) {
      return (a.intensity || 0) - (b.intensity || 0);
    });

    var cardsHtml = sorted.map(function(s, i) {
      var color = s.color || '#b8860b';
      return '<div class="state-card" data-state-id="' + escapeHtml(s.id) + '" tabindex="0" style="animation-delay:' + (i * 70) + 'ms; --state-color: ' + color + '">' +
        '<div class="state-card-paleo">' + escapeHtml(s.paleo || '') + '</div>' +
        '<h2 class="state-card-name">' + escapeHtml(s.name) + '</h2>' +
        '<div class="state-card-hebrew" dir="rtl">' + escapeHtml(s.hebrew || '') + '</div>' +
        '<div class="state-card-physics">' + escapeHtml(s.physics || '') + '</div>' +
        '<div class="state-card-olam"><span>Олам:</span> ' + escapeHtml(s.olam || '') + '</div>' +
        '<div class="state-card-intensity">' +
          '<span>' + escapeHtml(s.intensity_label || '') + '</span>' +
          '<div class="state-intensity-bar">' +
            '<div class="state-intensity-fill" style="width: ' + (s.intensity * 100) + '%; background: ' + color + '"></div>' +
          '</div>' +
        '</div>' +
      '</div>';
    }).join('');

    return '<div class="states-page">' +
      '<div class="states-controls">' +
        '<span class="states-nav-back"></span>' +
        '<button class="states-nav-btn active" onclick="GolemStates.openGrid()">' +
          '<img src="../../assets/icons/32/ui/web.png" class="lab-icon" alt=""> Карта' +
        '</button>' +
        '<button class="states-nav-btn" onclick="GolemStates.openDiagnostic()">' +
          '<img src="../../assets/icons/32/archaeology/testtube.png" class="lab-icon" alt=""> Диагностика' +
        '</button>' +
      '</div>' +
      '<div class="states-head">' +
        '<h1><img src="../../assets/icons/32/ui/web.png" class="lab-icon" alt=""> Карта состояний</h1>' +
        '<p class="subtitle">Семь пространств палео-механики — от запертости (Тоху) до завершённости (Эден). Каждое состояние — это не метафора, а физика: степень сжатости или открытости твоего пространства.</p>' +
      '</div>' +
      '<div class="states-map">' +
        '<div class="states-grid">' + cardsHtml + '</div>' +
      '</div>' +
      '<div style="text-align: center; margin-top: 8px;">' +
        '<button class="lab-btn lab-btn-primary lab-btn-sm" onclick="GolemStates.openDiagnostic()">' +
          '<img src="../../assets/icons/32/archaeology/testtube.png" class="lab-icon" alt=""> Пройти диагностику' +
        '</button>' +
      '</div>' +
    '</div>';
  }

  // ===== РЕНДЕР СТРАНИЦЫ СОСТОЯНИЯ =====
  function renderStateDetail(id) {
    var s = statesById[id];
    if (!s) return '<div class="lab-alert lab-alert-error">Состояние не найдено</div>';

    var color = s.color || '#b8860b';

    // Палео-разбор
    var paleoHtml = '';
    if (s.paleo_breakdown && s.paleo_breakdown.length) {
      paleoHtml = '<div class="state-detail-section">' +
        '<h3>Палео-разбор</h3>' +
        '<div class="paleo-breakdown">';
      s.paleo_breakdown.forEach(function(p) {
        paleoHtml += '<div class="paleo-breakdown-item">' +
          '<span class="paleo-char">' + escapeHtml(p.paleo || '') + '</span>' +
          '<span class="paleo-name">' + escapeHtml(p.name || '') + '</span>' +
          '<span class="paleo-func">' + escapeHtml(p.function || '') + '</span>' +
        '</div>';
      });
      paleoHtml += '</div>' +
        (s.paleo_meaning ? '<p style="text-align:center;font-style:italic;color:var(--text-muted);">' + escapeHtml(s.paleo_meaning) + '</p>' : '') +
      '</div>';
    }

    // Смысл
    var meaningHtml = s.meaning ? '<div class="state-detail-section"><h3>Смысл</h3><p>' + escapeHtml(s.meaning) + '</p></div>' : '';

    // Примеры
    var examplesHtml = '';
    if (s.examples && s.examples.length) {
      examplesHtml = '<div class="state-detail-section">' +
        '<h3>Примеры</h3>' +
        '<div class="examples-list state-card-grid" role="list">' +
        s.examples.map(function(ex, index) {
          return '<div class="example-tag state-example-card" role="listitem"><span class="state-example-index" aria-hidden="true">' + String(index + 1).padStart(2, '0') + '</span><span>' + escapeHtml(ex) + '</span></div>';
        }).join('') +
        '</div></div>';
    }

    // Переходы
    var transitionsHtml = '';
    if (s.transitions && s.transitions.length) {
      transitionsHtml = '<div class="state-detail-section">' +
        '<h3>Переходы</h3>' +
        '<div class="transitions-list state-timeline" role="list">';
      s.transitions.forEach(function(t) {
        var target = statesById[t.to];
        var targetName = target ? target.name : t.to;
        transitionsHtml += '<div class="transition-item state-timeline-item" role="listitem" data-to="' + escapeHtml(t.to) + '">' +
          '<span class="transition-arrow" aria-hidden="true">→</span>' +
          '<div class="transition-info">' +
            '<div class="transition-label">' + escapeHtml(targetName) + (t.label ? ': ' + escapeHtml(t.label) : '') + '</div>' +
            (t.action ? '<div class="transition-action">' + escapeHtml(t.action) + '</div>' : '') +
          '</div>' +
        '</div>';
      });
      transitionsHtml += '</div></div>';
    }

    // Города в этом состоянии
    var citiesHtml = renderCitiesForState(id);

    // Интенсивность
    var intensityHtml = '';
    if (s.intensity !== undefined) {
      intensityHtml = '<div class="state-detail-section">' +
        '<h3>Интенсивность</h3>' +
        '<div class="state-card-intensity" style="max-width:300px;">' +
          '<span>' + escapeHtml(s.intensity_label || '') + '</span>' +
          '<div class="state-intensity-bar">' +
            '<div class="state-intensity-fill" style="width: ' + (s.intensity * 100) + '%; background: ' + color + '"></div>' +
          '</div>' +
          '<span>' + Math.round(s.intensity * 100) + '%</span>' +
        '</div>' +
      '</div>';
    }

    return '<div class="states-page">' +
      '<div class="states-controls">' +
        '<button class="states-nav-btn states-nav-back" onclick="GolemStates.openGrid()"><img src="../../assets/icons/32/nav/home.png" class="lab-icon" alt=""> Назад к карте</button>' +
        '<button class="states-nav-btn" onclick="GolemStates.openDiagnostic()"><img src="../../assets/icons/32/archaeology/testtube.png" class="lab-icon" alt=""> Диагностика</button>' +
      '</div>' +
      '<div class="state-detail">' +
        '<div class="state-detail-hero" style="border-bottom-color: ' + color + '33;">' +
          '<span class="state-detail-hero-paleo">' + escapeHtml(s.paleo || '') + '</span>' +
          '<h2>' + escapeHtml(s.name) + '</h2>' +
          '<div class="hebrew" dir="rtl">' + escapeHtml(s.hebrew || '') + '</div>' +
          '<div class="physics">' + escapeHtml(s.physics || '') + '</div>' +
          '<div class="state-detail-olam"><span>Олам:</span> ' + escapeHtml(s.olam || '') + '</div>' +
        '</div>' +
        intensityHtml +
        paleoHtml +
        meaningHtml +
        examplesHtml +
        transitionsHtml +
        citiesHtml +
      '</div>' +
    '</div>';
  }

  // ===== ГОРОДА ДЛЯ СОСТОЯНИЯ =====
  function renderCitiesForState(stateId) {
    var matching = cartographyEntries.filter(function(e) {
      return e.state === stateId;
    });

    if (!matching.length) {
      return '<div class="state-detail-section">' +
        '<h3>Города и страны в этом состоянии</h3>' +
        '<p class="text-muted">Нет записей в картографии для этого состояния.</p>' +
      '</div>';
    }

    return '<div class="state-detail-section">' +
      '<h3>Города и страны в этом состоянии</h3>' +
      '<div class="state-cities">' +
      matching.map(function(e) {
        return '<div class="state-city-card" data-city-id="' + escapeHtml(e.id) + '">' +
          '<div class="city-name">' + escapeHtml(e.name) + '</div>' +
          (e.hebrew ? '<div class="city-hebrew" dir="rtl">' + escapeHtml(e.hebrew) + '</div>' : '') +
          (e.summary ? '<div class="city-summary">' + escapeHtml(e.summary) + '</div>' : '') +
        '</div>';
      }).join('') +
      '</div>' +
    '</div>';
  }

  // ===== ДИАГНОСТИКА =====
  function renderDiagnostic() {
    // Собираем все вопросы
    var allQuestions = [];
    states.forEach(function(s) {
      if (s.diagnostic_questions) {
        s.diagnostic_questions.forEach(function(q) {
          allQuestions.push({
            question: q,
            stateId: s.id
          });
        });
      }
    });

    if (!allQuestions.length) {
      return '<div class="lab-alert lab-alert-info">Для диагностики пока нет вопросов.</div>';
    }

    var total = allQuestions.length;
    var current = diagnosticState.currentQuestion;
    var answers = diagnosticState.answers;

    // Если диагностика завершена — показываем результат
    if (diagnosticState.completed) {
      return renderDiagnosticResult(allQuestions);
    }

    // Текущий вопрос
    var q = allQuestions[current];
    if (!q) {
      return renderDiagnosticResult(allQuestions);
    }

    var selectedValue = answers[q.question.id] || '';

    // Варианты ответов (шкала)
    var scaleOptions = [
      { value: 0, label: 'Совсем нет' },
      { value: 0.25, label: 'Скорее нет' },
      { value: 0.5, label: 'Не уверен' },
      { value: 0.75, label: 'Скорее да' },
      { value: 1, label: 'Полностью да' }
    ];

    var scaleHtml = '<div class="question-options-scale">';
    scaleOptions.forEach(function(opt) {
      var isSelected = selectedValue === opt.value;
      scaleHtml += '<div class="scale-option' + (isSelected ? ' selected' : '') + '" data-value="' + opt.value + '" onclick="GolemStates.selectAnswer(\'' + escapeHtml(q.question.id) + '\', ' + opt.value + ')">' +
        '<span class="scale-value">' + opt.value * 4 + '</span>' +
        '<span class="scale-label">' + escapeHtml(opt.label) + '</span>' +
      '</div>';
    });
    scaleHtml += '</div>';

    var progressPercent = ((current) / total) * 100;
    var hasAnswer = selectedValue !== '';

    return '<div class="states-page">' +
      '<div class="states-controls">' +
        '<button class="states-nav-btn states-nav-back" onclick="GolemStates.openGrid()"><img src="../../assets/icons/32/nav/home.png" class="lab-icon" alt=""> Назад к карте</button>' +
      '</div>' +
      '<div class="diagnostic-page">' +
        '<div class="diagnostic-header">' +
          '<h2><img src="../../assets/icons/32/archaeology/testtube.png" class="lab-icon" alt=""> Диагностика состояния</h2>' +
          '<p>Ответь на 7 вопросов, чтобы определить своё текущее пространство.</p>' +
        '</div>' +
        '<div class="diagnostic-progress">' +
          '<div class="diagnostic-progress-bar">' +
            '<div class="diagnostic-progress-fill" style="width: ' + progressPercent + '%"></div>' +
          '</div>' +
          '<div class="diagnostic-progress-text">Вопрос ' + (current + 1) + ' из ' + total + '</div>' +
        '</div>' +
        '<div class="question-card">' +
          '<div class="question-text">' + escapeHtml(q.question.text) + '</div>' +
          scaleHtml +
        '</div>' +
        '<div class="diagnostic-actions">' +
          (current > 0
            ? '<button class="btn-diagnostic-prev" onclick="GolemStates.prevQuestion()"><img src="../../assets/icons/32/nav/home.png" class="lab-icon" alt=""> Назад</button>'
            : '') +
          (hasAnswer
            ? (current < total - 1
                ? '<button class="btn-diagnostic-next" onclick="GolemStates.nextQuestion()"><img src="../../assets/icons/32/nav/door.png" class="lab-icon" alt=""> Далее</button>'
                : '<button class="btn-diagnostic-next" onclick="GolemStates.completeDiagnostic()"><img src="../../assets/icons/32/archaeology/lamp.png" class="lab-icon" alt=""> Узнать результат</button>')
            : '<button class="btn-diagnostic-next" disabled>Выберите ответ</button>'
          ) +
        '</div>' +
      '</div>' +
    '</div>';
  }

  // ===== РЕЗУЛЬТАТ ДИАГНОСТИКИ =====
  function renderDiagnosticResult(allQuestions) {
    var answers = diagnosticState.answers;

    // Вычисляем взвешенные суммы
    var scores = {};
    states.forEach(function(s) { scores[s.id] = 0; });

    allQuestions.forEach(function(q) {
      var value = answers[q.question.id];
      if (value === undefined || value === '') return;
      var weights = q.question.weight || {};
      Object.keys(weights).forEach(function(stateId) {
        if (scores[stateId] !== undefined) {
          scores[stateId] += weights[stateId] * value;
        }
      });
    });

    // Определяем лучшее состояние
    var bestStateId = null;
    var bestScore = -1;
    Object.keys(scores).forEach(function(id) {
      if (scores[id] > bestScore) {
        bestScore = scores[id];
        bestStateId = id;
      }
    });

    // Если нет результата
    if (!bestStateId || bestScore <= 0) {
      return '<div class="states-page"><div class="diagnostic-page">' +
        '<div class="diagnostic-header"><h2>Результат диагностики</h2></div>' +
        '<p class="text-muted" style="text-align:center;">Недостаточно данных для определения состояния. Пройди диагностику заново.</p>' +
        '<div class="result-actions"><button class="btn-result-restart" onclick="GolemStates.restartDiagnostic()">Пройти заново</button></div>' +
      '</div></div>';
    }

    var state = statesById[bestStateId];
    if (!state) {
      return '<div class="lab-alert lab-alert-error">Ошибка: состояние не найдено</div>';
    }

    // Рекомендуемый переход
    var transition = (state.transitions && state.transitions.length)
      ? state.transitions[0]
      : null;
    var targetName = transition && statesById[transition.to]
      ? statesById[transition.to].name
      : '';

    return '<div class="states-page">' +
      '<div class="states-controls">' +
        '<button class="states-nav-btn states-nav-back" onclick="GolemStates.openGrid()"><img src="../../assets/icons/32/nav/home.png" class="lab-icon" alt=""> Назад к карте</button>' +
      '</div>' +
      '<div class="diagnostic-page">' +
        '<div class="diagnostic-result">' +
          '<span class="diagnostic-result-paleo">' + escapeHtml(state.paleo || '') + '</span>' +
          '<h3>Твоё состояние — ' + escapeHtml(state.name) + '</h3>' +
          '<div class="result-physics">' + escapeHtml(state.physics || '') + '</div>' +
          (transition
            ? '<div class="result-transition">' +
                '<span class="arrow">→</span>' +
                '<div>' +
                  '<span class="to-state">' + escapeHtml(targetName) + '</span>' +
                  (transition.action ? '<span class="action">' + escapeHtml(transition.action) + '</span>' : '') +
                '</div>' +
              '</div>'
            : '') +
          '<div class="result-actions">' +
            '<button class="btn-result-state" onclick="GolemStates.openState(\'' + escapeHtml(bestStateId) + '\')"><img src="../../assets/icons/32/ui/book.png" class="lab-icon" alt=""> Подробнее о состоянии</button>' +
            '<button class="btn-result-restart" onclick="GolemStates.restartDiagnostic()"><img src="../../assets/icons/32/ui/hourglass.png" class="lab-icon" alt=""> Пройти заново</button>' +
            '<button class="btn-result-share" onclick="GolemStates.shareResult(\'' + escapeHtml(state.name) + '\', \'' + escapeHtml(transition ? targetName : '') + '\')"><img src="../../assets/icons/32/ui/export.png" class="lab-icon" alt=""> Поделиться</button>' +
          '</div>' +
        '</div>' +
      '</div>' +
    '</div>';
  }

  // ===== НАВИГАЦИЯ ПО ДИАГНОСТИКЕ =====
  function selectAnswer(questionId, value) {
    diagnosticState.answers[questionId] = value;
    renderCurrentContainer();
  }

  function nextQuestion() {
    var allQuestions = [];
    states.forEach(function(s) {
      if (s.diagnostic_questions) {
        s.diagnostic_questions.forEach(function(q) {
          allQuestions.push({ question: q, stateId: s.id });
        });
      }
    });

    if (diagnosticState.currentQuestion < allQuestions.length - 1) {
      diagnosticState.currentQuestion++;
      renderCurrentContainer();
    }
  }

  function prevQuestion() {
    if (diagnosticState.currentQuestion > 0) {
      diagnosticState.currentQuestion--;
      renderCurrentContainer();
    }
  }

  function completeDiagnostic() {
    diagnosticState.completed = true;
    renderCurrentContainer();
  }

  function restartDiagnostic() {
    diagnosticState.currentQuestion = 0;
    diagnosticState.answers = {};
    diagnosticState.completed = false;
    renderCurrentContainer();
  }

  function renderCurrentContainer() {
    var container = document.getElementById('states');
    if (container) renderView(container);
  }

  // ===== ПУБЛИЧНАЯ НАВИГАЦИЯ =====
  function openGrid() {
    currentView = 'grid';
    currentStateId = null;
    diagnosticState.completed = false;
    LabRouter.navigate('states');
  }

  function openState(id) {
    currentView = 'detail';
    currentStateId = id;
    LabRouter.navigate('states', null, { state: id });
  }

  function openDiagnostic() {
    currentView = 'diagnostic';
    currentStateId = null;
    diagnosticState.currentQuestion = 0;
    diagnosticState.answers = {};
    diagnosticState.completed = false;
    LabRouter.navigate('states', null, { diagnostic: 'true' });
  }

  function shareResult(stateName, transitionName) {
    var text = '🧪 Моё состояние по карте «Голем»: ' + stateName;
    if (transitionName) text += ' → Рекомендуемый переход: ' + transitionName;
    text += '\n\nУзнай своё состояние: https://ortamy.github.io/golem/pages/lab/#states';

    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(function() {
        if (window.LabToast) LabToast.show('Результат скопирован в буфер');
      }).catch(function() {
        fallbackCopy(text);
      });
    } else {
      fallbackCopy(text);
    }
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    if (window.LabToast) LabToast.show('Результат скопирован в буфер');
  }

  // ===== ПУБЛИЧНЫЙ API =====
  return {
    init: init,
    loadData: loadData,
    openGrid: openGrid,
    openState: openState,
    openDiagnostic: openDiagnostic,
    selectAnswer: selectAnswer,
    nextQuestion: nextQuestion,
    prevQuestion: prevQuestion,
    completeDiagnostic: completeDiagnostic,
    restartDiagnostic: restartDiagnostic,
    shareResult: shareResult
  };
})();

window.GolemStates = GolemStates;