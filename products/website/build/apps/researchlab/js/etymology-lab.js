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
    'אמת': { translit: 'эмет', meaning: 'истина, верность, правда', root: 'אמן', rootMeaning: 'верить, быть верным', subs: [['истина', 'эмет (אמת)', 'Греч. αλήθεια. אמת — первая, средняя и последняя буква алфавита.']] },
    'תורה': { translit: 'тора', meaning: 'учение, наставление', root: 'ירה', rootMeaning: 'направлять, учить', subs: [['закон', 'тора (תורה)', 'Греч. νόμος. Тора от корня ירה — направлять, а не закон.']] },
    'משיח': { translit: 'машиах', meaning: 'помазанник', root: 'משח', rootMeaning: 'мазать, помазывать', subs: [['Христос', 'Машиах (משיח)', 'Греч. Χριστός. Машиах — функция, не имя.']] },
    'יהוה': { translit: 'Яхве', meaning: 'Сущий (личное имя)', root: 'היה', rootMeaning: 'быть, существовать', subs: [['Господь', 'Яхве (יהוה)', 'Замена личного имени на безличный титул.']] },
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

  var EXAMPLE_WORDS = ['אמת', 'תורה', 'שלום', 'קדוש', 'חסד', 'יהוה', 'תשובה', 'ברית'];

  var rootsData = [];

  function init() {
    fetch('data/roots.json')
      .then(function(r) { return r.json(); })
      .then(function(data) { rootsData = data; })
      .catch(function() {});
    showChips();
  }

  function showChips() {
    var el = document.getElementById('el-results');
    if (!el) return;
    el.innerHTML = '<div class="el-examples">' +
      '<p class="el-examples-hint">Введите слово на иврите или транслите. Примеры:</p>' +
      '<div class="el-chips">' +
      EXAMPLE_WORDS.map(function(w) {
        return '<button class="el-chip" onclick="EtymologyLab.example(\'' + w + '\')">' + w + '</button>';
      }).join('') +
      '</div></div>';
  }

  function example(word) {
    var input = document.getElementById('el-input');
    if (input) { input.value = word; }
    analyze();
  }

  function analyze() {
    var resultsEl = document.getElementById('el-results');
    var input = document.getElementById('el-input');
    if (!resultsEl || !input) return;
    var val = input.value.trim();

    if (!val) { showChips(); return; }

    var clean = val.replace(/[֑-ׇ]/g, '');
    var wordData = WORD_DATA[clean];

    if (!wordData && rootsData.length > 0) {
      var q = clean.toLowerCase();
      var match = rootsData.find(function(r) {
        return r.root === clean ||
          r.translit.toLowerCase() === q ||
          r.meaning.toLowerCase().indexOf(q) !== -1;
      });
      if (match) {
        wordData = {
          translit: match.translit,
          meaning: match.meaning,
          root: match.root,
          rootMeaning: match.meaning,
          subs: (match.substitutions || []).map(function(s) {
            return [s, match.root + ' (' + match.translit + ')', ''];
          }),
          _rootEntry: match
        };
      }
    }

    if (!wordData) {
      resultsEl.innerHTML = '<div class="lab-alert lab-alert-warn">Слово «' + val + '» пока нет в базе. Попробуй: ' +
        EXAMPLE_WORDS.slice(0, 4).map(function(w) {
          return '<button class="el-chip el-chip-sm" onclick="EtymologyLab.example(\'' + w + '\')">' + w + '</button>';
        }).join(' ') + '</div>';
      return;
    }

    var lettersHTML = '', paleoStr = '';
    var entry = wordData._rootEntry;
    if (entry && entry.paleo && entry.paleo.length > 0) {
      entry.paleo.forEach(function(pChar, i) {
        var hChar = entry.root[i] || '';
        var pInfo = PALEO[hChar] || {};
        var pMean = (entry.paleoMeanings && entry.paleoMeanings[i]) ? entry.paleoMeanings[i] : (pInfo.meaning || '');
        lettersHTML += '<div class="el-letter-box">' +
          '<div class="ell-paleo">' + pChar + '</div>' +
          '<div class="ell-heb">' + hChar + '</div>' +
          '<div class="ell-name">' + (pInfo.name || '') + '</div>' +
          '<div class="ell-meaning">' + pMean + '</div></div>';
        paleoStr += pChar + ' ';
      });
    } else {
      for (var i = 0; i < clean.length; i++) {
        var ch = clean[i], p = PALEO[ch];
        if (p) {
          lettersHTML += '<div class="el-letter-box"><div class="ell-paleo">' + p.paleo + '</div>' +
            '<div class="ell-heb">' + ch + '</div><div class="ell-name">' + p.name + '</div>' +
            '<div class="ell-meaning">' + p.meaning + '</div></div>';
          paleoStr += p.paleo + ' ';
        }
      }
    }

    var subsHTML = '';
    if (wordData.subs && wordData.subs.length > 0) {
      subsHTML = '<table class="el-substitution-table"><thead><tr><th>Подмена</th><th>Оригинал</th><th>Пояснение</th></tr></thead><tbody>';
      wordData.subs.forEach(function(s) {
        subsHTML += '<tr><td class="sub-red">' + (s[0]||'') + '</td><td class="sub-green">' + (s[1]||'') + '</td><td class="text-small">' + (s[2]||'') + '</td></tr>';
      });
      subsHTML += '</tbody></table>';
    }

    var rootMatches = rootsData.filter(function(r) { return r.root === wordData.root || r.translit === wordData.root; });
    var rootHTML = rootMatches.length > 0
      ? '<div class="el-root-card"><div class="el-root-heb">' + rootMatches[0].root + '</div><div class="text-small text-muted">' + rootMatches[0].translit + '</div><div class="el-root-meaning">' + rootMatches[0].meaning + '</div></div>'
      : '<div class="el-root-card"><div class="el-root-heb">' + wordData.root + '</div><div class="el-root-meaning">' + wordData.rootMeaning + '</div></div>';

    resultsEl.innerHTML =
      '<div class="el-word-header">' +
        '<div class="el-word-heb">' + clean + '</div>' +
        '<div class="el-word-info"><div class="el-word-translit">' + wordData.translit + '</div>' +
        '<div class="el-word-meaning">' + wordData.meaning + '</div></div>' +
        '<div class="el-word-paleo">' + paleoStr.trim() + '</div>' +
      '</div>' +
      '<div class="el-section"><div class="el-section-title">Палео-разбор по буквам</div>' +
        '<p class="text-small text-muted mb-16">Каждая буква — это образ.</p>' +
        '<div class="el-letter-breakdown">' + lettersHTML + '</div></div>' +
      '<div class="el-section"><div class="el-section-title">Корень слова</div>' + rootHTML + '</div>' +
      (subsHTML ? '<div class="el-section"><div class="el-section-title">Цепочка подмен</div>' + subsHTML + '</div>' : '');

    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  return { init: init, analyze: analyze, example: example };
})();

window.EtymologyLab = EtyLab;
