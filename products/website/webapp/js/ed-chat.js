/**
 * ed-chat.js — Чат с нейросетью Эд v2
 * Bug #8 fix: saveMessages после первого send
 */

const EdChat = (function() {
  'use strict';

  const STORAGE_KEY = 'golem_ed_chat';

  const DEMO_RESPONSES = [
    'Отличный вопрос. В иврите корень קדש (KDSh) означает «отделённый», «посвящённый». Отсюда «кадош» — святой, то есть отделённый для особого использования. Понимание этого корня раскрывает, что святость — это не моральное качество, а статус отделённости.',
    'Слово «церковь» в русском — это калька с греческого ἐκκλησία (экклесия), что значит «собрание». В иврите соответствующее понятие — קהל (каhаль) — тоже собрание, но с оттенком «созванный по делу». Подмена в том, что «церковь» стала обозначать здание и иерархию, а не собрание.',
    'Яхве (יהוה) — это личное имя, а не титул. Оно происходит от корня היה (HYH) — «быть». Поэтому «Яхве» означает «Тот, Кто есть», «Сущий». Замена на «Господь» стирает это значение и превращает личные отношения в формальные.',
    'Машиах (משיח) — это не имя и не титул в современном смысле. Это причастие от корня משח (MShH) — «мазать, помазывать». Машиах — это «помазанный», то есть тот, кто посвящён на служение: царь, коэн или пророк. Это функция, а не божественная личность.',
    'Тшува (תשובה) — одно из самых глубоких понятий. Корень שוב (ShVB) — «возвращаться». Тшува — это не «покаяние» с чувством вины, а возвращение к своему источнику, к Яхве, к истинному пути. Это действие, а не эмоция.',
    'Тора (תורה) — от корня ירה (YRH) — «направлять, стрелять, учить». Тора — это не «закон» в юридическом смысле, а наставление, указание пути. Это свет, который показывает направление, а не свод правил.',
    'Септуагинта (LXX) — греческий перевод, созданный в III-II вв. до н.э. в Александрии. Именно в ней впервые появились многие подмены: אדוני (Адонай) перевели как κύριος (Господь), что потом перешло в славянские и русские переводы.',
    'Имя Яхшуа (יהושע) означает «Яхве спасает». Греческая форма Ἰησοῦς (Иисус) искажает это значение. Когда вы читаете «Иисус» в русском переводе, помните, что оригинал — Яхшуа, и это имя содержит в себе имя Яхве.'
  ];

  let messages = [];

  function init() {
    loadMessages();
    renderMessages();
  }

  function loadMessages() {
    try {
      var data = localStorage.getItem(STORAGE_KEY);
      if (data) messages = JSON.parse(data);
    } catch(e) {
      messages = [];
    }
  }

  function saveMessages() {
    try {
      if (messages.length > 50) messages = messages.slice(-50);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch(e) {
      console.warn('[EdChat] save error:', e);
    }
  }

  function renderMessages() {
    var container = document.getElementById('ec-messages');
    if (!container) return;

    if (messages.length === 0) {
      container.innerHTML = '<div class="text-muted" style="text-align:center;padding:40px;" id="ec-welcome">Начните диалог с Эдом. Задайте вопрос об иврите, подменах, истории.</div>';
      return;
    }

    var html = '';
    messages.forEach(function(msg) {
      var isUser = msg.role === 'user';
      html += '<div style="margin-bottom:12px;' + (isUser ? 'text-align:right;' : '') + '">';
      html += '  <div style="display:inline-block;max-width:80%;padding:10px 14px;border-radius:6px;' +
        (isUser ? 'background:#b8860b;color:#faf3e0;text-align:left;' : 'background:#faf3e0;border:1px solid #d4c4a8;color:#2c1810;') + '">';
      html += '    <div style="font-size:15px;line-height:1.6;">' + escapeHTML(msg.text) + '</div>';
      html += '    <div style="font-size:11px;color:' + (isUser ? '#d4c4a8' : '#8a7a6a') + ';margin-top:4px;">' +
        new Date(msg.timestamp).toLocaleTimeString('ru-RU') + '</div>';
      html += '  </div>';
      html += '</div>';
    });

    container.innerHTML = html;
    container.scrollTop = container.scrollHeight;
  }

  function send() {
    var input = document.getElementById('ec-input');
    if (!input) return;
    var text = input.value.trim();
    if (!text) return;

    messages.push({
      role: 'user',
      text: text,
      timestamp: new Date().toISOString()
    });
    // Сохраняем сразу после первого сообщения
    saveMessages();
    input.value = '';
    renderMessages();
    simulateResponse(text);
  }

  function simulateResponse(userText) {
    var idx = Math.floor(Math.random() * DEMO_RESPONSES.length);
    var response = DEMO_RESPONSES[idx];

    var lower = userText.toLowerCase();
    if (lower.indexOf('свят') !== -1) response = DEMO_RESPONSES[0];
    else if (lower.indexOf('церков') !== -1) response = DEMO_RESPONSES[1];
    else if (lower.indexOf('яхве') !== -1 || lower.indexOf('господ') !== -1) response = DEMO_RESPONSES[2];
    else if (lower.indexOf('машиах') !== -1 || lower.indexOf('помазан') !== -1 || lower.indexOf('христ') !== -1) response = DEMO_RESPONSES[3];
    else if (lower.indexOf('покаян') !== -1 || lower.indexOf('тшув') !== -1) response = DEMO_RESPONSES[4];
    else if (lower.indexOf('тор') !== -1 || lower.indexOf('закон') !== -1) response = DEMO_RESPONSES[5];
    else if (lower.indexOf('септуагинт') !== -1 || lower.indexOf('lxx') !== -1 || lower.indexOf('перевод') !== -1) response = DEMO_RESPONSES[6];
    else if (lower.indexOf('иисус') !== -1 || lower.indexOf('яхшу') !== -1) response = DEMO_RESPONSES[7];

    setTimeout(function() {
      messages.push({
        role: 'assistant',
        text: response,
        timestamp: new Date().toISOString()
      });
      saveMessages();
      renderMessages();
    }, 800 + Math.random() * 1200);
  }

  function clearChat() {
    if (confirm('Очистить историю чата?')) {
      messages = [];
      localStorage.removeItem(STORAGE_KEY);
      renderMessages();
    }
  }

  function escapeHTML(text) {
    var d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
  }

  return {
    init: init,
    send: send,
    clear: clearChat
  };
})();