/**
 * paleo-keyboard.js — Палео-ивритская клавиатура v2
 * Bug #2 fix: LETTERS.indexOf() не работал для массивов внутри forEach
 * Теперь передаём индекс через data-атрибут
 */

const PaleoKey = (function() {
  'use strict';

  const LETTERS = [
    ['𐤀', 'Алеф', 'Бык', 'Сила, лидерство, начало', 'A'],
    ['𐤁', 'Бет', 'Дом', 'Семья, дом, внутреннее', 'B'],
    ['𐤂', 'Гимель', 'Верблюд', 'Движение, путешествие, воздаяние', 'G'],
    ['𐤃', 'Далет', 'Дверь', 'Выбор, путь, решение', 'D'],
    ['𐤄', 'Хе', 'Окно', 'Откровение, вдохновение, благодать', 'H'],
    ['𐤅', 'Вав', 'Крюк', 'Соединение, связь, союз', 'V/W'],
    ['𐤆', 'Заин', 'Оружие', 'Защита, сила, победа', 'Z'],
    ['𐤇', 'Хет', 'Ограда', 'Жизнь, внутренний двор, защита', 'H (горл.)'],
    ['𐤈', 'Тет', 'Змея', 'Добро, скрытое благо, окружение', 'T'],
    ['𐤉', 'Йод', 'Рука', 'Дело, действие, творение', 'Y'],
    ['𐤊', 'Каф', 'Ладонь', 'Власть, покровительство, открытость', 'K'],
    ['𐤋', 'Ламед', 'Посох', 'Учение, направление, контроль', 'L'],
    ['𐤌', 'Мем', 'Вода', 'Народ, хаос, жизнь, течение', 'M'],
    ['𐤍', 'Нун', 'Рыба', 'Потомство, жизнь, активность', 'N'],
    ['𐤎', 'Самех', 'Рыба (скелет)', 'Поддержка, основа, порядок', 'S'],
    ['𐤏', 'Аин', 'Глаз', 'Видение, понимание, источник', 'A (горл.)'],
    ['𐤐', 'Пе', 'Рот', 'Речь, слово, выражение', 'P'],
    ['𐤑', 'Цаде', 'Крюк для рыбы', 'Праведность, охота, цель', 'Ts'],
    ['𐤒', 'Коф', 'Игла/обезьяна', 'Святость, окружение, цикл', 'Q'],
    ['𐤓', 'Реш', 'Голова', 'Начало, мудрость, первый', 'R'],
    ['𐤔', 'Шин', 'Зуб', 'Разрушение, мир, огонь', 'Sh/S'],
    ['𐤕', 'Тав', 'Знак', 'Завет, истина, завершение', 'T']
  ];

  function init() {
    renderKeys();
  }

  function renderKeys() {
    var container = document.getElementById('pk-keys');
    if (!container) return;

    var html = '';
    LETTERS.forEach(function(letter, idx) {
      html += '<div class="lab-card" style="width:100px;text-align:center;cursor:pointer;padding:12px 8px;margin:0;" ' +
        'data-idx="' + idx + '" ' +
        'onclick="PaleoKey.insertByIndex(' + idx + ')" ' +
        'onmouseenter="PaleoKey.showInfo(' + idx + ')" ' +
        'onmouseleave="PaleoKey.hideInfo()">';
      html += '  <div style="font-size:36px;font-family:\'Times New Roman\',serif;line-height:1.2;">' + letter[0] + '</div>';
      html += '  <div style="font-size:12px;color:#8a7a6a;margin-top:4px;">' + letter[1] + '</div>';
      html += '  <div style="font-size:11px;color:#b8a080;">' + letter[4] + '</div>';
      html += '</div>';
    });

    container.innerHTML = html;
  }

  function insertByIndex(idx) {
    if (idx >= 0 && idx < LETTERS.length) {
      var output = document.getElementById('pk-output');
      if (output) {
        output.textContent += LETTERS[idx][0];
        output.focus();
      }
    }
  }

  function copy() {
    var output = document.getElementById('pk-output');
    if (!output || !output.textContent) return;

    navigator.clipboard.writeText(output.textContent).then(function() {
      showToast('Текст скопирован');
    }).catch(function() {
      var range = document.createRange();
      range.selectNode(output);
      window.getSelection().removeAllRanges();
      window.getSelection().addRange(range);
      document.execCommand('copy');
      showToast('Текст скопирован');
    });
  }

  function clearOutput() {
    document.getElementById('pk-output').textContent = '';
  }

  function showInfo(index) {
    var letter = LETTERS[index];
    if (!letter) return;

    document.getElementById('pk-info-title').innerHTML = 
      '<span style="font-size:32px;font-family:\'Times New Roman\',serif;margin-right:10px;">' + letter[0] + '</span> ' +
      letter[1] + ' (' + letter[4] + ')';
    document.getElementById('pk-info-body').innerHTML = 
      '<p><strong>Образ:</strong> ' + letter[2] + '</p>' +
      '<p><strong>Значение:</strong> ' + letter[3] + '</p>';
    document.getElementById('pk-info').style.display = 'block';
  }

  function hideInfo() {
    // Оставляем видимым — пользователь может кликнуть
  }

  function showToast(msg) {
    var t = document.getElementById('pk-toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'pk-toast';
      t.style.cssText = 'position:fixed;top:24px;left:50%;transform:translateX(-50%);background:#2c1810;color:#ede0c8;padding:10px 24px;font-size:14px;font-family:"EB Garamond",serif;opacity:0;pointer-events:none;z-index:9999;border-radius:4px;border:1px solid #b8860b;transition:opacity 0.4s;';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.style.opacity = '1';
    setTimeout(function() { t.style.opacity = '0'; }, 2000);
  }

  return {
    init: init,
    insert: insertByIndex,
    insertByIndex: insertByIndex,
    copy: copy,
    clear: clearOutput,
    showInfo: showInfo,
    hideInfo: hideInfo
  };
})();
