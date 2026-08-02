/*
 * analyzers.js — frontend-модуль анализаторов Research Lab
 * Метаданные: заголовок — Анализаторы; описание — интерфейс слоя, ИИ и диалекта;
 * версия — 1.0.0; дата создания — 2026-08-02.
 *
 * Архитектура: AnalyzerAdapter сначала пробует локальный endpoint, затем
 * использует автономный mock. UI не зависит от способа получения результата.
 */
(function(window, document) {
  'use strict';

  var ICONS = {
    layer: '../../assets/icons/32/archaeology/testtube.png',
    ai: '../../assets/icons/32/crafts/hammer-and-chisel.png',
    dialect: '../../assets/icons/32/scribe/scroll.png'
  };
  var LAYERS = [
    { id: 'hellenization', name: 'Эллинизация', markers: ['абстракц', 'идея', 'философ', 'категор', 'теор'], diagnosis: 'Предметное действие переводится в отвлечённую идею или категорию.' },
    { id: 'psychologization', name: 'Психологизация', markers: ['психик', 'эмоц', 'личност', 'мотивац', 'травм', 'чувств'], diagnosis: 'Источник движения помещается во внутреннее состояние вместо описания среды и действия.' },
    { id: 'juridization', name: 'Юридизация', markers: ['закон', 'право', 'обязан', 'долг', 'вина', 'контракт', 'запрет'], diagnosis: 'Живое отношение собирается как норма, долг, вина или контракт.' },
    { id: 'technology', name: 'Технослой', markers: ['систем', 'алгоритм', 'оптимиз', 'ресурс', 'функц', 'интерфейс', 'контрол'], diagnosis: 'Поток описывается как управляемый ресурс, система или функция.' },
    { id: 'media', name: 'Медиа-слой', markers: ['информац', 'сообщен', 'новост', 'контент', 'аудитор', 'нарратив', 'публикац'], diagnosis: 'Событие может быть заменено его упаковкой, сообщением или метрикой внимания.' },
    { id: 'religious_calque', name: 'Религиозная калька', markers: ['бог', 'господ', 'свят', 'грех', 'молитв', 'жертв', 'спасен', 'церков'], diagnosis: 'Готовая переводная рамка закрывает исходную механику образа.' },
    { id: 'paleo', name: 'Палео-слой', markers: ['поток', 'двер', 'дом', 'крюк', 'оград', 'огон', 'движен', 'сред', 'давар', 'свив', 'хук', 'эмет', 'шекер'], diagnosis: 'Сохраняется предметная механика потока, среды, прохода и перехода.' },
    { id: 'physical', name: 'Физический слой', markers: ['тел', 'ног', 'глаз', 'земл', 'камен', 'ветер', 'дыхан', 'давлен', 'удар', 'откры', 'закры'], diagnosis: 'Текст опирается на наблюдаемое тело и материальную среду.' }
  ];
  var DIALECTS = {
    grecisims: { title: 'Грецизмы', terms: { 'философия': 'חכמה / мудрость действия', 'теория': 'ראיה / наблюдаемый образ', 'категория': 'שורש / корень', 'психология': 'Свива / среда и отношение', 'идея': 'Давар / слово-действие' } },
    latinisms: { title: 'Латинизмы', terms: { 'контракт': 'ברית / связка', 'обязанность': 'Хук / установленный ход', 'юрисдикция': 'граница действия', 'ресурс': 'поток', 'эффективность': 'коах / действующая сила' } }
  };

  function esc(value) { var node = document.createElement('div'); node.textContent = value == null ? '' : String(value); return node.innerHTML; }
  function words(text) { return (text.match(/[\p{L}\p{N}_-]+/gu) || []); }
  function sentences(text) { return text.split(/(?<=[.!?…])\s+|\n+/).filter(function(item) { return item.trim(); }); }
  function markerMatches(word, marker) { var value = word.toLowerCase(); if (marker === 'право') return /^(право|права|праву|праве|правы)$/.test(value); return value.indexOf(marker) !== -1; }

  function layerAnalysis(text) {
    var tokens = words(text), results = LAYERS.map(function(layer) {
      var found = {}, markerCounts = {};
      tokens.forEach(function(word, index) {
        layer.markers.forEach(function(marker) {
          if (markerMatches(word, marker)) { found[index] = word; markerCounts[marker] = (markerCounts[marker] || 0) + 1; }
        });
      });
      var count = Object.keys(found).length;
      return { id: layer.id, name: layer.name, count: count, percentage: tokens.length ? +(count / tokens.length * 100).toFixed(2) : 0, markers: markerCounts, diagnosis: layer.diagnosis };
    });
    var dominant = results.reduce(function(best, item) { return !best || item.count > best.count ? item : best; }, null);
    return { words: tokens.length, sentences: sentences(text).length, layers: results, dominant: dominant && dominant.count ? dominant : null };
  }

  function dialectAnalysis(text) {
    var lower = text.toLowerCase(), result = {};
    Object.keys(DIALECTS).forEach(function(group) {
      result[group] = Object.keys(DIALECTS[group].terms).filter(function(term) { return lower.indexOf(term) !== -1; }).map(function(term) { return { term: term, replacement: DIALECTS[group].terms[term] }; });
    });
    result.total = result.grecisims.length + result.latinisms.length;
    return result;
  }

  function mockAnalyze(text, kind, settings) {
    var layer = layerAnalysis(text);
    if (kind === 'layer') return Promise.resolve({ source: 'mock', kind: kind, layer: layer });
    if (kind === 'dialect') return Promise.resolve({ source: 'mock', kind: kind, dialect: dialectAnalysis(text), layer: layer });
    var dominant = layer.dominant ? layer.dominant.name : 'не выявлен';
    return Promise.resolve({ source: 'mock', kind: kind, model: settings.model, mode: settings.mode, layer: layer, interpretation: 'Смысловой контур текста тяготеет к слою «' + dominant + '». Это предварительная интерпретация: её следует проверить через Давар, Свиву и критерий эмет / шекер.', recommendations: ['Отделить наблюдаемое действие от абстрактного ярлыка.', 'Вернуть в текст тело, среду и направление потока.', 'Сверить заменяемый термин с палео-аналогом и зафиксировать основание замены.'] });
  }

  var AnalyzerAdapter = {
    endpoint: '/api/analyzers/analyze',
    analyze: function(text, kind, settings) {
      if (!text.trim()) return Promise.reject(new Error('Введите текст перед запуском анализа.'));
      return fetch(this.endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: text, kind: kind, settings: settings || {} }) }).then(function(response) {
        if (!response.ok) throw new Error('API unavailable');
        return response.json();
      }).catch(function() { return mockAnalyze(text, kind, settings || { model: 'golem-local', mode: 'local' }); });
    }
  };

  function hero(kicker, title, description) { return '<div class="analyzers-hero"><div class="analyzers-kicker">' + esc(kicker) + '</div><h1>' + esc(title) + '</h1><p>' + esc(description) + '</p><div class="analyzers-hero-meta"><span class="analyzers-chip">8 слоёв</span><span class="analyzers-chip">локальный mock</span><span class="analyzers-chip">эмет / шекер</span></div></div>'; }
  function pageHead(icon, title, description) { return '<a class="lab-btn lab-btn-secondary lab-btn-sm analyzer-back" href="#analyzers">← Все анализаторы</a><div class="analyzer-page-head"><img class="analyzer-page-head__icon" src="' + icon + '" alt=""><div><h1>' + esc(title) + '</h1><p>' + esc(description) + '</p></div></div>'; }
  function card(icon, title, description, route, tag) { return '<article class="analyzer-card"><img class="analyzer-card__icon" src="' + icon + '" alt=""><h2>' + esc(title) + '</h2><p>' + esc(description) + '</p><div class="analyzer-card__footer"><span class="analyzer-card__tag">' + esc(tag) + '</span><a class="lab-btn lab-btn-primary lab-btn-sm" href="#' + route + '">Открыть</a></div></article>'; }

  function renderOverview(container) {
    container.innerHTML = '<div class="analyzers-shell">' + hero('GOLEM · RESEARCH LAB', 'Анализаторы', 'Вертикальные инструменты для диагностики текста: увидеть слой, проверить смысловой сдвиг и найти слова, которые требуют палео-восстановления.') + '<div class="analyzers-grid">' + card(ICONS.layer, 'Слой-анализ', 'Показывает процентное соотношение восьми слоёв подмен и формирует краткую диагностику доминирующего слоя.', 'layer-analyzer', 'структура / проценты') + card(ICONS.ai, 'ИИ-анализ', 'Даёт смысловую интерпретацию и рекомендации. Сейчас работает автономный mock; API подключается через единый адаптер.', 'ai-analyzer', 'локально / API') + card(ICONS.dialect, 'Диалект-анализ', 'Находит грецизмы и латинизмы и предлагает ивритские или палео-аналоги для дальнейшей проверки.', 'dialect-analyzer', 'словарь / замена') + '</div></div>';
  }

  function resultShell(container, body) { var result = container.querySelector('.analyzer-result'); if (result) result.innerHTML = body; }
  function layerResult(result) {
    var rows = result.layers.map(function(item) { return '<div class="analyzer-layer-row"><div class="analyzer-layer-row__head"><span>' + esc(item.name) + '</span><span class="analyzer-layer-row__value">' + item.percentage.toFixed(2) + '% · ' + item.count + '</span></div><div class="analyzer-bar"><span style="width:' + item.percentage + '%"></span></div></div>'; }).join('');
    var table = result.layers.map(function(item) { var markers = Object.keys(item.markers).map(function(key) { return esc(key) + ' × ' + item.markers[key]; }).join(', ') || '—'; return '<tr><td>' + esc(item.name) + '</td><td>' + markers + '</td><td>' + item.percentage.toFixed(2) + '%</td></tr>'; }).join('');
    return '<div class="analyzer-result__summary"><div class="analyzer-stat"><strong>' + result.words + '</strong><span>слов</span></div><div class="analyzer-stat"><strong>' + result.sentences + '</strong><span>предложений</span></div><div class="analyzer-stat"><strong>' + (result.dominant ? esc(result.dominant.name) : '—') + '</strong><span>доминанта</span></div></div><div aria-label="Проценты слоёв">' + rows + '</div><div class="analyzer-table-wrap"><table class="analyzer-table"><thead><tr><th>Слой</th><th>Маркеры</th><th>Доля</th></tr></thead><tbody>' + table + '</tbody></table></div>' + (result.dominant ? '<div class="analyzer-diagnosis"><strong>Диагностика: ' + esc(result.dominant.name) + '</strong>' + esc(result.dominant.diagnosis) + '</div>' : '<div class="analyzer-empty">Маркеры слоёв не выявлены. Проверьте текст через физический образ и Свиву.</div>');
  }
  function dialectResult(result) {
    function group(key) { var items = result.dialect[key]; return '<div class="analyzer-dialect-card"><h3>' + esc(DIALECTS[key].title) + ' <small>(' + items.length + ')</small></h3>' + (items.length ? items.map(function(item) { return '<div class="analyzer-dialect-item"><span class="analyzer-mark">' + esc(item.term) + '</span><span>→ ' + esc(item.replacement) + '</span></div>'; }).join('') : '<p class="analyzer-helper">Не найдены</p>') + '</div>'; }
    return '<div class="analyzer-result__summary"><div class="analyzer-stat"><strong>' + result.dialect.total + '</strong><span>маркеров</span></div><div class="analyzer-stat"><strong>' + result.layer.words + '</strong><span>слов проверено</span></div></div><div class="analyzer-dialect-grid">' + group('grecisims') + group('latinisms') + '</div><div class="analyzer-diagnosis"><strong>Рекомендация</strong>Рассматривайте замену как рабочую гипотезу: подтвердите её через корень, палео-образ и физическую конструкцию.</div>';
  }
  function aiResult(result) { return '<div class="analyzer-diagnosis"><strong>Источник: ' + esc(result.mode === 'api' ? 'API' : 'локальный mock') + ' · модель: ' + esc(result.model) + '</strong>' + esc(result.interpretation) + '</div><div class="analyzer-ai-copy"><h3>Рекомендации по очищению</h3><ul class="analyzer-list">' + result.recommendations.map(function(item) { return '<li>' + esc(item) + '</li>'; }).join('') + '</ul></div><div class="analyzer-diagnosis"><strong>Слой-сигнал</strong>' + layerResult(result.layer) + '</div>'; }

  function renderAnalyzerPage(container, kind) {
    var isLayer = kind === 'layer', isAI = kind === 'ai';
    var title = isLayer ? 'Слой-анализ' : isAI ? 'ИИ-анализ' : 'Диалект-анализ';
    var desc = isLayer ? 'Измерьте присутствие восьми слоёв и найдите доминирующий сдвиг.' : isAI ? 'Получите смысловую интерпретацию с прозрачным выбором режима и модели.' : 'Найдите грецизмы и латинизмы и соберите карту возможных замен.';
    var settings = isAI ? '<div class="analyzer-settings"><label class="analyzer-label">Модель<select class="analyzer-select" id="analyzer-model"><option value="golem-local">Golem Local</option><option value="paleo-reasoner">Paleo Reasoner</option><option value="api-default">API Default</option></select></label><label class="analyzer-label">Режим<select class="analyzer-select" id="analyzer-mode"><option value="local">Локально</option><option value="api">API</option></select></label></div>' : '';
    container.innerHTML = '<div class="analyzers-shell">' + pageHead(isLayer ? ICONS.layer : isAI ? ICONS.ai : ICONS.dialect, title, desc) + '<div class="analyzer-workspace"><form class="analyzer-panel" id="analyzer-form"><h2>Входной Давар</h2>' + settings + '<label class="analyzer-label" for="analyzer-input">Текст для анализа</label><textarea class="analyzer-textarea" id="analyzer-input" required placeholder="Вставьте текст для вертикального прохода…"></textarea><div class="analyzer-controls"><button class="lab-btn lab-btn-primary" type="submit">Запустить анализ</button><button class="lab-btn lab-btn-secondary" type="button" id="analyzer-clear">Очистить</button></div><p class="analyzer-helper">Результат — диагностический сигнал, а не автоматический приговор. Сверяйте его с методологией MANIFEST.</p><div class="analyzer-status" id="analyzer-status" role="status" aria-live="polite"></div></form><section class="analyzer-panel" aria-live="polite"><h2>Результат прохода</h2><div class="analyzer-result"><div class="analyzer-empty">Заполните поле и запустите анализ.</div></div></section></div></div>';
    var form = container.querySelector('#analyzer-form'), input = container.querySelector('#analyzer-input'), status = container.querySelector('#analyzer-status');
    form.addEventListener('submit', function(event) { event.preventDefault(); status.textContent = 'Проход выполняется…'; var settingsValue = { model: container.querySelector('#analyzer-model') ? container.querySelector('#analyzer-model').value : 'golem-local', mode: container.querySelector('#analyzer-mode') ? container.querySelector('#analyzer-mode').value : 'local' }; AnalyzerAdapter.analyze(input.value, kind, settingsValue).then(function(result) { status.textContent = result.source === 'mock' ? 'Готово · автономный mock' : 'Готово · API'; resultShell(container, isLayer ? layerResult(result.layer) : kind === 'dialect' ? dialectResult(result) : aiResult(result)); }).catch(function(error) { status.textContent = error.message; }); });
    container.querySelector('#analyzer-clear').addEventListener('click', function() { input.value = ''; status.textContent = ''; resultShell(container, '<div class="analyzer-empty">Заполните поле и запустите анализ.</div>'); input.focus(); });
  }

  window.GolemAnalyzers = { render: function(container, moduleId) { if (moduleId === 'analyzers') renderOverview(container); else renderAnalyzerPage(container, moduleId === 'layer-analyzer' ? 'layer' : moduleId === 'ai-analyzer' ? 'ai' : 'dialect'); }, adapter: AnalyzerAdapter, layers: LAYERS };
})(window, document);