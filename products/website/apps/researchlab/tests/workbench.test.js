'use strict';

// Тест реестра конвейеров и mock-движков «Мастерской» (#workbench).
// Запуск: node tests/workbench.test.js

const assert = require('assert');
const WorkbenchPipelines = require('../js/workbench-pipelines.js');
const fs = require('fs');
const path = require('path');

const KNOWN_VIEWERS = ['translation', 'exposure', 'roots'];

function testRegistry() {
  const list = WorkbenchPipelines.list();
  assert.strictEqual(list.length, 3, 'В реестре три стартовых конвейера');
  const ids = list.map(function(p) { return p.id; });
  assert.deepStrictEqual(ids.sort(), ['book-translation', 'exposure-check', 'root-assembly']);

  list.forEach(function(pipeline) {
    assert.ok(pipeline.id && pipeline.title && pipeline.icon && pipeline.description, 'Базовые поля заполнены: ' + pipeline.id);
    assert.ok(Array.isArray(pipeline.inputs) && pipeline.inputs.length, 'inputs описаны: ' + pipeline.id);
    assert.ok(Array.isArray(pipeline.steps) && pipeline.steps.length >= 3, 'Этапы описаны: ' + pipeline.id);
    assert.ok(KNOWN_VIEWERS.indexOf(pipeline.viewer) !== -1, 'Вьювер известен: ' + pipeline.id);
    assert.ok(WorkbenchPipelines.engine(pipeline.engine), 'Движок подключён: ' + pipeline.id);
    assert.ok(pipeline.cost && pipeline.cost.pricePer1kTokens > 0, 'Константы стоимости заданы: ' + pipeline.id);
  });
  console.log('OK  реестр: 3 конвейера, поля, вьюверы, движки, стоимость');
}

function testBookTranslationInputs() {
  const pipeline = WorkbenchPipelines.get('book-translation');
  const file = pipeline.inputs.filter(function(input) { return input.key === 'file'; })[0];
  const sourceLang = pipeline.inputs.filter(function(input) { return input.key === 'sourceLang'; })[0];
  const languages = sourceLang.options.map(function(option) { return option.value; });

  assert.ok(file.accept.includes('.pdf'), 'Конвейер принимает PDF');
  assert.ok(file.accept.includes('.txt') && file.accept.includes('.md'), 'Текстовые форматы остаются доступны');
  assert.ok(languages.includes('phoenician'), 'Доступно финикийское письмо');
  assert.ok(languages.includes('paleo-hebrew'), 'Доступен палео-иврит');
  console.log('OK  перевод книги: PDF и палео-языки доступны');
}

function testExportFormats() {
  const source = fs.readFileSync(path.join(__dirname, '..', 'js', 'workbench.js'), 'utf8');
  ['export-pdf', 'export-md', 'export-txt', 'export-json'].forEach(function(action) {
    assert.ok(source.includes(action), 'Доступен экспорт: ' + action);
  });
  assert.ok(source.includes('window.print()'), 'PDF открывает печатное представление');
  assert.ok(source.includes('openExportModal(runId)'), 'Экспорт доступен из списка проектов');
  console.log('OK  экспорт: PDF, Markdown, TXT и JSON');
}

function testEstimate() {
  const pipeline = WorkbenchPipelines.get('book-translation');
  const estimate = WorkbenchPipelines.estimate(pipeline, 4000);
  assert.strictEqual(estimate.chars, 4000);
  assert.strictEqual(estimate.tokens, 1000, '4000 знаков ≈ 1000 токенов (chars/4)');
  assert.strictEqual(estimate.price, 2, '1000 токенов по 2₽/1k = 2₽');
  assert.ok(estimate.seconds > 0);
  const empty = WorkbenchPipelines.estimate(pipeline, 0);
  assert.strictEqual(empty.tokens, 1, 'Минимум 1 токен');
  console.log('OK  смета: chars/4 → токены, цена из конфига');
}

function collectProgress(onProgress, stepsCount) {
  const events = [];
  return {
    events: events,
    onProgress: function(update) {
      events.push(update);
      onProgress(update);
    },
    stepsCount: stepsCount
  };
}

async function testMockBookTranslation() {
  const pipeline = WorkbenchPipelines.get('book-translation');
  const recorder = collectProgress(function() {}, pipeline.steps.length);
  const statuses = {};
  const demoText = 'Первый абзац про след на песке.\n\nВторой абзац про дом и тепло.\n\nТретий абзац про воду.';

  const result = await WorkbenchPipelines.engine(pipeline.engine).run({
    runId: 'test-1',
    pipeline: pipeline,
    values: { sourceLang: 'ru', targetLang: 'en', keepPaleo: true, keepStructure: true },
    inputText: demoText,
    inputMeta: { name: 'demo.txt', chars: demoText.length },
    signal: { aborted: false },
    fastMode: true
  }, recorder.onProgress);

  assert.strictEqual(result.kind, 'translation');
  assert.strictEqual(result.placeholder, false);
  assert.strictEqual(result.meta.engine, 'mock-book-translation');
  assert.strictEqual(result.meta.chars, demoText.length);
  assert.ok(result.segments.length === 3, 'Три фрагмента по абзацам');
  assert.ok(result.segments[0].original.indexOf('Первый абзац') === 0);
  assert.ok(result.segments[0].translated.length > 0);

  recorder.events.forEach(function(event) {
    if (event.status === 'done') statuses[event.stepIndex] = true;
  });
  for (let i = 0; i < pipeline.steps.length; i++) {
    assert.ok(statuses[i], 'Этап завершён: ' + pipeline.steps[i]);
  }
  console.log('OK  mock-движок перевода: 5 этапов, фрагменты, результат');
}

async function testCancel() {
  const pipeline = WorkbenchPipelines.get('book-translation');
  const signal = { aborted: false };
  let first = true;

  await assert.rejects(
    WorkbenchPipelines.engine(pipeline.engine).run({
      runId: 'test-2',
      pipeline: pipeline,
      values: { targetLang: 'ru' },
      inputText: 'Абзац.\n\nАбазац два.',
      inputMeta: { name: 'x.txt', chars: 16 },
      signal: signal,
      fastMode: false // реальные задержки, чтобы успеть отменить между шагами
    }, function() {
      if (first) { signal.aborted = true; first = false; }
    }),
    function(error) {
      return error && error.cancelled === true;
    },
    'Отмена должна выбрасывать ошибку с флагом cancelled'
  );
  console.log('OK  отмена: signal.aborted прерывает движение по этапам');
}

async function testPassThrough() {
  const pipeline = WorkbenchPipelines.get('exposure-check');
  const result = await WorkbenchPipelines.engine(pipeline.engine).run({
    runId: 'test-3',
    pipeline: pipeline,
    values: { strictExposure: false },
    inputText: 'Текст для сверки слоёв.',
    inputMeta: { name: '', chars: 22 },
    signal: { aborted: false },
    fastMode: true
  }, function() {});

  assert.strictEqual(result.kind, 'exposure');
  assert.strictEqual(result.placeholder, true, 'Вьювер exposure — заглушка');
  assert.ok(result.note.indexOf('Вьювер') === 0);
  console.log('OK  pass-through: exposure-check проходит этапы, вьювер-заглушка');
}

(async function run() {
  testRegistry();
  testBookTranslationInputs();
  testExportFormats();
  testEstimate();
  await testMockBookTranslation();
  await testCancel();
  await testPassThrough();
  console.log('ВСЕ ТЕСТЫ ПРОЙДЕНЫ');
})().catch(function(error) {
  console.error('ПРОВАЛ:', error);
  process.exit(1);
});
