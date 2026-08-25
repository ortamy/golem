/**
 * video-lab.js — Генератор видео-образов.
 * Визуализирует физику переходов между палео-буквами в слове.
 */
(function(window, document) {
  'use strict';

  var PALEO_CHARS = {
    'א': { char: '𐤀', name: 'Алеф', meaning: 'сила, бык, начало', motion: 'Инициация импульса, зарождение силы из источника.' },
    'ב': { char: '𐤁', name: 'Бет', meaning: 'дом, семья', motion: 'Концентрация и удержание силы внутри пространства.' },
    'ג': { char: '𐤂', name: 'Гимель', meaning: 'движение, верблюд', motion: 'Направленное перемещение, перенос импульса.' },
    'ד': { char: '𐤃', name: 'Далет', meaning: 'дверь, выбор', motion: 'Прохождение через барьер, изменение уровня или состояния.' },
    'ה': { char: '𐤄', name: 'Хе', meaning: 'откровение, окно', motion: 'Излучение вовне, проявление скрытого.' },
    'ו': { char: '𐤅', name: 'Вав', meaning: 'соединение, крюк', motion: 'Сцепление элементов, выстраивание оси связи.' },
    'ז': { char: '𐤆', name: 'Заин', meaning: 'оружие, защита', motion: 'Разделение сред, отсечение лишнего, фиксация границы.' },
    'ח': { char: '𐤇', name: 'Хет', meaning: 'ограда, жизнь', motion: 'Ограничение области для сохранения жизненной энергии.' },
    'ט': { char: '𐤈', name: 'Тет', meaning: 'скрытое благо', motion: 'Сворачивание силы во внутренний центр.' },
    'י': { char: '𐤉', name: 'Йод', meaning: 'рука, действие', motion: 'Точечное приложение силы, вектор направленного действия.' },
    'כ': { char: '𐤊', name: 'Каф', meaning: 'ладонь, власть', motion: 'Охват, принятие формы, подчинение импульса структуре.' },
    'ך': { char: '𐤊', name: 'Каф (софит)', meaning: 'ладонь, власть', motion: 'Завершение охвата и фиксация формы.' },
    'ל': { char: '𐤋', name: 'Ламед', meaning: 'посох, учение', motion: 'Управление движением, направление потока сверху вниз.' },
    'מ': { char: '𐤌', name: 'Мем', meaning: 'вода, народ', motion: 'Волновой процесс, непрерывный поток, растворение и перенос.' },
    'ם': { char: '𐤌', name: 'Мем (софит)', meaning: 'вода, народ', motion: 'Замыкание волнового процесса в конечный объем.' },
    'נ': { char: '𐤍', name: 'Нун', meaning: 'рыба, потомство', motion: 'Прорастание, непрерывное продолжение жизни, активность.' },
    'ן': { char: '𐤍', name: 'Нун (софит)', meaning: 'рыба, потомство', motion: 'Финальное закрепление ростка в структуре.' },
    'ס': { char: '𐤎', name: 'Самех', meaning: 'поддержка, основа', motion: 'Круговая защита, стабилизация опорного каркаса.' },
    'ע': { char: '𐤏', name: 'Аин', meaning: 'глаз, источник', motion: 'Фокусировка внимания, вскрытие глубинного пласта.' },
    'פ': { char: '𐤐', name: 'Пе', meaning: 'рот, речь', motion: 'Выброс энергии, расширение и передача импульса вовне.' },
    'ף': { char: '𐤐', name: 'Пе (софит)', meaning: 'рот, речь', motion: 'Выход во внешнюю среду завершен.' },
    'צ': { char: '𐤑', name: 'Цаде', meaning: 'праведность, цель', motion: 'Стремление к вершине, выстраивание вертикали напряжения.' },
    'ץ': { char: '𐤑', name: 'Цаде (софит)', meaning: 'праведность, цель', motion: 'Достижение цели и её жесткая фиксация.' },
    'ק': { char: '𐤒', name: 'Коф', meaning: 'святость, окружение', motion: 'Выделение священного контура, фильтрация хаоса.' },
    'ר': { char: '𐤓', name: 'Реш', meaning: 'голова, начало', motion: 'Определение главного вектора, доминирование идеи.' },
    'ש': { char: '𐤔', name: 'Шин', meaning: 'мир, разрушение', motion: 'Динамическое трение, огонь, поглощение старой структуры.' },
    'ת': { char: '𐤕', name: 'Тав', meaning: 'знак, завет, истина', motion: 'Печать завершенности, кристаллизация опыта в форму завета.' }
  };

  function init(container) {
    if (!container) return;
    
    var wordInput = container.querySelector('#vl-word-input');
    var generateBtn = container.querySelector('#vl-generate-btn');
    var visualOutput = container.querySelector('#vl-visual-output');
    var descOutput = container.querySelector('#vl-description-output');
    var status = container.querySelector('#vl-status');

    if (!wordInput || !generateBtn) return;

    generateBtn.onclick = function() {
      var word = wordInput.value.trim();
      if (!word) {
        status.textContent = 'Введите слово на иврите.';
        status.className = 'prompt-generator-status text-warn';
        return;
      }

      status.textContent = '';
      status.className = 'prompt-generator-status';

      var letters = word.split('');
      var validLetters = [];
      
      letters.forEach(function(l) {
        var clean = l.replace(/[\u0591-\u05C7]/g, ''); // Очистка от огласовок
        if (clean && PALEO_CHARS[clean]) {
          validLetters.push({ raw: clean, info: PALEO_CHARS[clean] });
        }
      });

      if (validLetters.length === 0) {
        status.textContent = 'Не найдено палео-символов в введённом слове.';
        status.className = 'prompt-generator-status text-warn';
        return;
      }

      // Отрисовка визуальной ленты
      var timelineHtml = '<div class="vl-timeline">';
      validLetters.forEach(function(item, idx) {
        timelineHtml += '<div class="vl-timeline-node">' +
          '<div class="vl-paleo-char">' + item.info.char + '</div>' +
          '<div class="vl-char-name">' + item.info.name + ' (' + item.raw + ')</div>' +
          '<div class="vl-char-meaning">' + item.info.meaning + '</div>' +
          '</div>';

        if (idx < validLetters.length - 1) {
          timelineHtml += '<div class="vl-timeline-arrow">' +
            '<div class="vl-arrow-shaft"></div>' +
            '<div class="vl-arrow-label">переход</div>' +
            '</div>';
        }
      });
      timelineHtml += '</div>';
      visualOutput.innerHTML = timelineHtml;

      // Отрисовка описания физики движения
      var descHtml = '<ol class="vl-desc-list">';
      validLetters.forEach(function(item, idx) {
        descHtml += '<li><strong>Состояние ' + (idx + 1) + ' (' + item.info.name + '):</strong> ' + item.info.motion + '</li>';
      });
      descHtml += '</ol>';

      if (validLetters.length > 1) {
        descHtml += '<div class="vl-synthesis"><h4>Общая динамика перехода:</h4><p>Импульс начинается как <strong>' + validLetters[0].info.meaning + '</strong>, проходит трансформацию через состояние <strong>' + validLetters[Math.min(1, validLetters.length - 1)].info.meaning + '</strong> и запечатывается в финальном состоянии <strong>' + validLetters[validLetters.length - 1].info.meaning + '</strong>.</p></div>';
      }

      descOutput.innerHTML = descHtml;
    };
  }

  window.VideoLab = {
    init: init,
    PALEO_CHARS: PALEO_CHARS
  };
})(window, document);
