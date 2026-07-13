// ===== ETYMOLOGY LAB =====
const EtyLab = (function() {
  'use strict';

  const PALEO = {
    'א': { paleo: '𐤀', name: 'Алеф', meaning: 'сила, бык, начало' },
    'ב': { paleo: '𐤁', name: 'Бет', meaning: 'дом, семья' },
    'ג': { paleo: '𐤂', name: 'Гимель', meaning: 'движение, верблюд' },
    'ד': { paleo: '𐤃', name: 'Далет', meaning: 'дверь, выбор' },
    'ה': { paleo: '𐤄', name: 'Хе', meaning: 'откровение, окно' },
    'ו': { paleo: '𐤅', name: 'Вав', meaning: 'соединение, крюк' },
    'ז': { paleo: '𐤆', name: 'Заин', meaning: 'оружие, защита' },
    'ח': { paleo: '𐤇', name: 'Хет', meaning: 'ограда, жизнь' },
    'ט': { paleo: '𐤈', name: 'Тет', meaning: 'скрытое благо' },
    'י': { paleo: '𐤉', name: 'Йод', meaning: 'рука, действие' },
    'כ': { paleo: '𐤊', name: 'Каф', meaning: 'ладонь, власть' },
    'ך': { paleo: '𐤊', name: 'Каф (софит)', meaning: 'ладонь, власть' },
    'ל': { paleo: '𐤋', name: 'Ламед', meaning: 'посох, учение' },
    'מ': { paleo: '𐤌', name: 'Мем', meaning: 'вода, народ' },
    'ם': { paleo: '𐤌', name: 'Мем (софит)', meaning: 'вода, народ' },
    'נ': { paleo: '𐤍', name: 'Нун', meaning: 'рыба, потомство' },
    'ן': { paleo: '𐤍', name: 'Нун (софит)', meaning: 'рыба, потомство' },
    'ס': { paleo: '𐤎', name: 'Самех', meaning: 'поддержка, основа' },
    'ע': { paleo: '𐤏', name: 'Аин', meaning: 'глаз, источник' },
    'פ': { paleo: '𐤐', name: 'Пе', meaning: 'рот, речь' },
    'ף': { paleo: '𐤐', name: 'Пе (софит)', meaning: 'рот, речь' },
    'צ': { paleo: '𐤑', name: 'Цаде', meaning: 'праведность, цель' },
    'ץ': { paleo: '𐤑', name: 'Цаде (софит)', meaning: 'праведность, цель' },
    'ק': { paleo: '𐤒', name: 'Коф', meaning: 'святость, окружение' },
    'ר': { paleo: '𐤓', name: 'Реш', meaning: 'голова, начало' },
    'ש': { paleo: '𐤔', name: 'Шин', meaning: 'мир, разрушение' },
    'ת': { paleo: '𐤕', name: 'Тав', meaning: 'знак, завет, истина' }
  };

  const WORD_DATA = {
    'אמת': { translit: 'эмет', meaning: 'истина, верность, правда', root: 'אמן', rootMeaning: 'верить, быть верным', subs: [['истина', 'эмет (אמת)', 'Греч. αλήθεια. В иврите אמת состоит из первой, средней и последней букв алфавита.']] },
    'תורה': { translit: 'тора', meaning: 'учение, наставление', root: 'ירה', rootMeaning: 'направлять, учить', subs: [['закон', 'тора (תורה)', 'Греч. νόμος. Тора от корня ירה — направлять, а не закон.']] },
    'משיח': { translit: 'машиах', meaning: 'помазанник', root: 'משח', rootMeaning: 'мазать, помазывать', subs: [['Христос', 'Машиах (משיח)', 'Греч. Χριστός. Машиах — функция, не имя.']] },
    'יהוה': { translit: 'Яхве', meaning: 'Сущий (личное имя)', root: 'היה', rootMeaning: 'быть, существовать', subs: [['Господь', 'Яхве (יהוה)', 'Греч. κύριος. Замена имени на титул.']] },
    'שלום': { translit: 'шалом', meaning: 'мир, целостность', root: 'שלם', rootMeaning: 'быть целым', subs: [['мир', 'шалом (שלום)', 'Греч. ειρήνη. Шалом — полнота, не просто отсутствие войны.']] },
    'צדק': { translit: 'цедек', meaning: 'правда, справедливость', root: 'צדק', rootMeaning: 'быть праведным', subs: [['правда', 'цедек (צדק)', 'Цедек — действие справедливости. Цдака — не милостыня.']] },
    'בראשית': { translit: 'берешит', meaning: 'в начале', root: 'ראש', rootMeaning: 'голова, начало', subs: [['в начале', 'берешит (בראשית)', 'От корня ראש — голова. Берешит — в голове, в начале.']] },
    'נביא': { translit: 'нави', meaning: 'пророк', root: 'נבא', rootMeaning: 'провозвещать', subs: [['пророк', 'нави (נביא)', 'Греч. προφήτης. Нави — видящий скрытое.']] },
    'כהן': { translit: 'коhен', meaning: 'служитель', root: 'כה', rootMeaning: 'стоять перед', subs: [['священник', 'коhен (כהן)', 'От корня כון — стоять. Тот, кто стоит перед Яхве.']] },
    'קדוש': { translit: 'кадош', meaning: 'отделённый', root: 'קדש', rootMeaning: 'отделять', subs: [['святой', 'кадош (קדוש)', 'Кадош — статус отделённости, не моральное качество.']] },
    'חסד': { translit: 'хесед', meaning: 'преданная любовь', root: 'חסד', rootMeaning: 'быть верным', subs: [['милость', 'хесед (חסד)', 'Хесед — действие верности завету, не эмоция.']] },
    'תשובה': { translit: 'тшува', meaning: 'возвращение', root: 'שוב', rootMeaning: 'возвращаться', subs: [['покаяние', 'тшува (תשובה)', 'От корня שוב — возвращаться. Не чувство вины.']] },
    'ברית': { translit: 'брит', meaning: 'союз', root: 'בר', rootMeaning: 'чистый', subs: [['завет', 'брит (ברית)', 'От בר — чистый. Брит — союз, основанный на очищении.']] }
  };

  let rootsData = [];

  function init() {
    fetch('data/roots.json')
      .then(r => r.json())
      .then(data => { rootsData = data; })
      .catch(() => {});
  }

  function example(word) {
    var input = document.getElementById('el-input');
    if (input) input.value = word;
    analyze();
  }

  function analyze() {
    var input = document.getElementById('el-input');
    var result = document.getElementById('el-result');
    var placeholder = document.getElementById('el-placeholder');

    if (!input) return;
    var val = input.value.trim();

    if (!val) {
      if (result) result.classList.remove('show');
      if (placeholder) placeholder.style.display = 'block';
      return;
    }

    var clean = val.replace(/[\u0591-\u05C7]/g, '');
    var wordData = WORD_DATA[clean];

    if (!wordData) {
      if (placeholder) {
        placeholder.style.display = 'block';
        placeholder.innerHTML = '<div class="lab-alert lab-alert-warn">Слово «' + val + '» пока нет в базе.</div>';
      }
      if (result) result.classList.remove('show');
      return;
    }

    if (placeholder) placeholder.style.display = 'none';

    var lettersHTML = '', paleoStr = '';
    for (var i = 0; i < clean.length; i++) {
      var ch = clean[i];
      var p = PALEO[ch];
      if (p) {
        lettersHTML += '<div class="el-letter-box"><div class="ell-paleo">' + p.paleo + '</div><div class="ell-heb">' + ch + '</div><div class="ell-name">' + p.name + '</div><div class="ell-meaning">' + p.meaning + '</div></div>';
        paleoStr += p.paleo + ' ';
      }
    }

    var subsHTML = '';
    if (wordData.subs && wordData.subs.length > 0) {
      subsHTML = '<table class="el-substitution-table"><thead><tr><th>Подмена</th><th>Оригинал</th><th>Пояснение</th></tr></thead><tbody>';
      wordData.subs.forEach(function(s) {
        subsHTML += '<tr><td class="sub-red">' + s[0] + '</td><td class="sub-green">' + s[1] + '</td><td class="text-small">' + s[2] + '</td></tr>';
      });
      subsHTML += '</tbody></table>';
    }

    var rootMatches = rootsData.filter(function(r) { return r.root === wordData.root || r.translit === wordData.root; });
    var rootHTML = rootMatches.length > 0
      ? '<div class="el-root-card"><div class="el-root-heb">' + rootMatches[0].root + '</div><div class="text-small text-muted">' + rootMatches[0].translit + '</div><div class="el-root-meaning">' + rootMatches[0].meaning + '</div></div>'
      : '<div class="el-root-card"><div class="el-root-heb">' + wordData.root + '</div><div class="el-root-meaning">' + wordData.rootMeaning + '</div></div>';

    var fullHTML =
      '<div class="el-word-header">' +
        '<div class="el-word-heb">' + clean + '</div>' +
        '<div class="el-word-info"><div class="el-word-translit">' + wordData.translit + '</div><div class="el-word-meaning">' + wordData.meaning + '</div></div>' +
        '<div class="el-word-paleo">' + paleoStr.trim() + '</div>' +
      '</div>' +
      '<div class="el-section"><div class="el-section-title">Палео-разбор по буквам</div><p class="text-small text-muted mb-16">Каждая буква — это образ.</p><div class="el-letter-breakdown">' + lettersHTML + '</div></div>' +
      '<div class="el-section"><div class="el-section-title">Корень слова</div>' + rootHTML + '</div>' +
      (subsHTML ? '<div class="el-section"><div class="el-section-title">Цепочка подмен</div>' + subsHTML + '</div>' : '');

    if (result) {
      result.innerHTML = fullHTML;
      result.classList.add('show');
      result.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  return { init: init, analyze: analyze, example: example };
})();