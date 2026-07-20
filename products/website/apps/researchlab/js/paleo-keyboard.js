/**
 * paleo-keyboard.js — Палео-ивритская клавиатура v3
 * Features: keyboard shortcuts, click=info+insert, etymology link, textarea, PNG export
 */

const PaleoKey = (function() {
  'use strict';

  const LETTERS = [
    ['𐤀', 'Алеф', 'Бык',         'Сила, лидерство, начало',              'A'],
    ['𐤁', 'Бет',  'Дом',         'Семья, дом, внутреннее',               'B'],
    ['𐤂', 'Гимель','Верблюд',    'Движение, путешествие, воздаяние',     'G'],
    ['𐤃', 'Далет','Дверь',       'Выбор, путь, решение',                 'D'],
    ['𐤄', 'Хе',   'Окно',        'Откровение, вдохновение, благодать',   'H'],
    ['𐤅', 'Вав',  'Крюк',        'Соединение, связь, союз',              'V'],
    ['𐤆', 'Заин', 'Оружие',      'Защита, сила, победа',                 'Z'],
    ['𐤇', 'Хет',  'Ограда',      'Жизнь, внутренний двор, защита',      'X'],
    ['𐤈', 'Тет',  'Змея',        'Добро, скрытое благо, окружение',      'T'],
    ['𐤉', 'Йод',  'Рука',        'Дело, действие, творение',             'Y'],
    ['𐤊', 'Каф',  'Ладонь',      'Власть, покровительство, открытость',  'K'],
    ['𐤋', 'Ламед','Посох',       'Учение, направление, контроль',        'L'],
    ['𐤌', 'Мем',  'Вода',        'Народ, хаос, жизнь, течение',         'M'],
    ['𐤍', 'Нун',  'Рыба',        'Потомство, жизнь, активность',         'N'],
    ['𐤎', 'Самех','Рыба (скелет)','Поддержка, основа, порядок',          'S'],
    ['𐤏', 'Аин',  'Глаз',        'Видение, понимание, источник',         'E'],
    ['𐤐', 'Пе',   'Рот',         'Речь, слово, выражение',               'P'],
    ['𐤑', 'Цаде', 'Крюк',        'Праведность, охота, цель',             'C'],
    ['𐤒', 'Коф',  'Игла',        'Святость, окружение, цикл',            'Q'],
    ['𐤓', 'Реш',  'Голова',      'Начало, мудрость, первый',             'R'],
    ['𐤔', 'Шин',  'Зуб',         'Разрушение, мир, огонь',               'W'],
    ['𐤕', 'Тав',  'Знак',        'Завет, истина, завершение',            'J']
  ];

  // Single-key shortcuts: press the letter to insert the paleo char
  const KEY_MAP = {
    'A':0,'B':1,'G':2,'D':3,'H':4,'V':5,'Z':6,'X':7,
    'T':8,'Y':9,'K':10,'L':11,'M':12,'N':13,'S':14,
    'E':15,'P':16,'C':17,'Q':18,'R':19,'W':20,'J':21
  };

  var activeIdx = -1;

  function init() {
    renderKeys();
    attachKeyboardListener();
  }

  function renderKeys() {
    var container = document.getElementById('pk-keys');
    if (!container) return;
    var html = '';
    LETTERS.forEach(function(letter, idx) {
      html += '<div class="lab-card pk-key" id="pk-key-' + idx + '" ' +
        'style="width:90px;text-align:center;cursor:pointer;padding:10px 6px;margin:0;transition:all 0.15s;" ' +
        'onclick="PaleoKey.selectLetter(' + idx + ')" ' +
        'onmouseenter="PaleoKey.showInfo(' + idx + ')">' +
        '<div style="font-size:34px;font-family:\'Times New Roman\',serif;line-height:1.2;">' + letter[0] + '</div>' +
        '<div style="font-size:11px;color:#8a7a6a;margin-top:3px;">' + letter[1] + '</div>' +
        '<div style="font-size:10px;color:#b8a080;opacity:0.7;">' + letter[4] + '</div>' +
        '</div>';
    });
    container.innerHTML = html;
  }

  function selectLetter(idx) {
    if (idx < 0 || idx >= LETTERS.length) return;
    var output = document.getElementById('pk-output');
    if (output) {
      var start = output.selectionStart != null ? output.selectionStart : output.value.length;
      var end = output.selectionEnd != null ? output.selectionEnd : output.value.length;
      output.value = output.value.slice(0, start) + LETTERS[idx][0] + output.value.slice(end);
      output.selectionStart = output.selectionEnd = start + LETTERS[idx][0].length;
      output.focus();
    }
    // Highlight active key
    if (activeIdx >= 0) {
      var prev = document.getElementById('pk-key-' + activeIdx);
      if (prev) prev.style.outline = '';
    }
    activeIdx = idx;
    var el = document.getElementById('pk-key-' + idx);
    if (el) el.style.outline = '2px solid var(--accent-gold, #b8860b)';
    showInfo(idx);
  }

  function showInfo(idx) {
    var letter = LETTERS[idx];
    if (!letter) return;
    var titleEl = document.getElementById('pk-info-title');
    var bodyEl = document.getElementById('pk-info-body');
    var infoEl = document.getElementById('pk-info');
    if (titleEl) titleEl.innerHTML =
      '<span style="font-size:40px;font-family:\'Times New Roman\',serif;margin-right:12px;vertical-align:middle;">' + letter[0] + '</span>' +
      '<strong>' + letter[1] + '</strong>' +
      '<span style="font-size:12px;color:#8a7a6a;margin-left:8px;">/' + letter[4] + '/</span>';
    if (bodyEl) bodyEl.innerHTML =
      '<p style="margin:4px 0;"><strong>Образ:</strong> ' + letter[2] + '</p>' +
      '<p style="margin:4px 0;"><strong>Значение:</strong> ' + letter[3] + '</p>';
    if (infoEl) infoEl.style.display = 'block';
  }

  function hideInfo() { /* kept open intentionally */ }

  function copy() {
    var output = document.getElementById('pk-output');
    var text = output ? output.value : '';
    if (!text) { showToast('Нечего копировать'); return; }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function() { showToast('Скопировано'); }).catch(fallbackCopy);
    } else { fallbackCopy(); }
    function fallbackCopy() {
      output.select();
      document.execCommand('copy');
      showToast('Скопировано');
    }
  }

  function clearOutput() {
    var output = document.getElementById('pk-output');
    if (output) { output.value = ''; output.focus(); }
    if (activeIdx >= 0) {
      var el = document.getElementById('pk-key-' + activeIdx);
      if (el) el.style.outline = '';
      activeIdx = -1;
    }
    var infoEl = document.getElementById('pk-info');
    if (infoEl) infoEl.style.display = 'none';
  }

  function analyzeInEtymology() {
    var output = document.getElementById('pk-output');
    var text = output ? output.value.trim() : '';
    if (!text) { showToast('Введи слово для разбора'); return; }
    if (window.LabRouter) LabRouter.navigate('etymology-lab');
    setTimeout(function() {
      var input = document.getElementById('el-input');
      if (input) { input.value = text; }
      if (window.EtymologyLab) EtymologyLab.analyze();
    }, 150);
  }

  function downloadAsPng() {
    var output = document.getElementById('pk-output');
    var text = output ? output.value.trim() : '';
    if (!text) { showToast('Введи слово для скачивания'); return; }
    var fontSize = 80;
    var pad = 40;
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');
    ctx.font = fontSize + 'px "Times New Roman", serif';
    var textW = ctx.measureText(text).width;
    canvas.width = Math.max(300, textW + pad * 2);
    canvas.height = fontSize + pad * 2;
    ctx.fillStyle = '#faf3e0';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#5a3e1b';
    ctx.font = fontSize + 'px "Times New Roman", serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, canvas.width / 2, canvas.height / 2);
    var a = document.createElement('a');
    a.href = canvas.toDataURL('image/png');
    a.download = 'paleo-' + Date.now() + '.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast('PNG скачан');
  }

  function showToast(msg) {
    var t = document.getElementById('pk-toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'pk-toast';
      t.className = 'pk-toast';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.classList.add('show');
    t.style.display = 'block';
    setTimeout(function() { t.classList.remove('show'); setTimeout(function() { t.style.display = 'none'; }, 300); }, 2000);
  }

  return { init: init, insertByIndex: selectLetter, insert: selectLetter, selectLetter: selectLetter,
    copy: copy, clear: clearOutput, showInfo: showInfo, hideInfo: hideInfo,
    analyzeInEtymology: analyzeInEtymology, downloadAsPng: downloadAsPng };
})();

window.PaleoKey = PaleoKey;

  function attachKeyboardListener() {
    document.addEventListener('keydown', function(e) {
      var module = document.getElementById('paleo-keyboard');
      if (!module || !module.classList.contains('active')) return;
      var focused = document.activeElement;
      if (focused && focused.id === 'pk-output') {
        var key = e.key.toUpperCase();
        if (KEY_MAP[key] !== undefined) {
          e.preventDefault();
          selectLetter(KEY_MAP[key]);
        }
      }
    });
  }

