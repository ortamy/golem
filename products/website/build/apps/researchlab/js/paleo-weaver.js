// Детерминированный сборщик связного палео-образа без внешней модели.
(function(root, factory) {
  var api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.PaleoWeaver = api;
}(typeof window !== 'undefined' ? window : (typeof globalThis !== 'undefined' ? globalThis : this), function() {
  'use strict';

  var FORMS = {
    'вместилище': { pronoun: 'которое', accusative: 'вместилище', genitive: 'вместилища', dative: 'вместилищу' },
    'сила': { pronoun: 'которая', accusative: 'силу', genitive: 'силы', dative: 'силе' },
    'связка': { pronoun: 'которая', accusative: 'связку', genitive: 'связки', dative: 'связке' },
    'вершина': { pronoun: 'которая', accusative: 'вершину', genitive: 'вершины', dative: 'вершине' },
    'фиксация': { pronoun: 'которая', accusative: 'фиксацию', genitive: 'фиксации', dative: 'фиксации' },
    'поток': { pronoun: 'который', accusative: 'поток', genitive: 'потока', dative: 'потоку' },
    'источник': { pronoun: 'который', accusative: 'источник', genitive: 'источника', dative: 'источнику' },
    'захват': { pronoun: 'который', accusative: 'захват', genitive: 'захвата', dative: 'захвату' },
    'откровение': { pronoun: 'которое', accusative: 'откровение', genitive: 'откровения', dative: 'откровению' },
    'действие': { pronoun: 'которое', accusative: 'действие', genitive: 'действия', dative: 'действию' },
    'разрушение': { pronoun: 'которое', accusative: 'разрушение', genitive: 'разрушения', dative: 'разрушению' },
    'направление': { pronoun: 'которое', accusative: 'направление', genitive: 'направления', dative: 'направлению' },
    'открытие': { pronoun: 'которое', accusative: 'открытие', genitive: 'открытия', dative: 'открытию' }
  };
  var VERBS = { 'направление': 'направляет', 'фиксация': 'фиксирует', 'разрушение': 'разрушает', 'захват': 'захватывает', 'действие': 'действует', 'откровение': 'открывает', 'остановка': 'останавливает' };
  var MEANS = ['разрушение', 'действие', 'поток', 'огонь'];
  var PARTICLES = { 'связка': 'и', 'захват': 'через' };
  var TRANSLIT = { 'א':'ʼ','ב':'б','ג':'г','ד':'д','ה':'h','ו':'в','ז':'з','ח':'х','ט':'т','י':'й','כ':'к','ך':'к','ל':'л','מ':'м','ם':'м','נ':'н','ן':'н','ס':'с','ע':'ʼ','פ':'п','ף':'п','צ':'ц','ץ':'ц','ק':'к','ר':'р','ש':'ш','ת':'т' };

  function normal(value) { return String(value || '').toLocaleLowerCase('ru-RU').trim(); }
  function unique(list) { return list.filter(function(value, index) { return list.indexOf(value) === index; }); }
  function form(value, key) { return (FORMS[value] && FORMS[value][key]) || value; }
  function first(list, allowed) { return list.filter(function(value) { return allowed.indexOf(value) !== -1; })[0] || ''; }
  function content(chain) { return (chain || []).map(normal).filter(Boolean); }

  function isParticle(chain) {
    var values = content(chain);
    return values.length <= 2 && !!PARTICLES[values[0]];
  }

  function particleText(chain) { return PARTICLES[content(chain)[0]] || ''; }

  function wordReading(chain) {
    var values = content(chain);
    if (!values.length) return 'образ требует проверки';
    if (isParticle(values)) return particleText(values);
    var subject = first(values, Object.keys(FORMS)) || values[0];
    // Подлежащее не может повторять себя как глагол: «разрушение, которое разрушает».
    var verbKey = Object.keys(VERBS).filter(function(key) { return values.indexOf(key) !== -1 && key !== subject; })[0] || (VERBS[subject] ? 'остановка' : 'направление');
    var object = values.slice(values.indexOf(subject) + 1).filter(function(value) { return FORMS[value] && !VERBS[value] && value !== subject; })[0] || '';
    var target = values.filter(function(value) { return (value === 'вершина' || value === 'откровение') && value !== subject; })[0] || '';
    var means = unique(values.filter(function(value) { return MEANS.indexOf(value) !== -1 && value !== verbKey && value !== subject; })).slice(0, 1);
    var reading = subject + ', ' + form(subject, 'pronoun') + ' ' + VERBS[verbKey];
    if (object) reading += ' ' + form(object, 'accusative');
    if (target && target !== object) reading += ' к ' + form(target, 'dative');
    if (means.length) reading += ' через ' + means[0];
    return reading.split(/\s+/).slice(0, 8).join(' ');
  }

  function verseReading(chains) {
    var usable = (chains || []).filter(function(chain) { return !isParticle(chain); });
    if (!usable.length) return 'Связка образов требует проверки.';
    var primary = usable.reduce(function(longest, chain) { return chain.length > longest.length ? chain : longest; }, usable[0]);
    var result = wordReading(primary);
    usable.filter(function(chain) { return chain !== primary; }).slice(0, 2).forEach(function(chain, index) {
      var values = content(chain);
      if (values.indexOf('фиксация') !== -1 && index === 0) result += ', фиксируя ход';
      else if (values.indexOf('направление') !== -1 && index === 0) result += ', направляя поток';
    });
    return result.split(/\s+/).slice(0, 20).join(' ').replace(/[,.]+$/, '') + '.';
  }

  function verseFunction(chains) {
    var values = unique((chains || []).reduce(function(all, chain) { return all.concat(content(chain)); }, []));
    var primary = values.filter(function(value) { return FORMS[value]; })[0] || values[0] || '';
    var action = Object.keys(VERBS).filter(function(value) { return values.indexOf(value) !== -1; })[0] || 'направление';
    var means = values.filter(function(value) { return MEANS.indexOf(value) !== -1 && value !== action; })[0] || '';
    return primary ? action + ' ' + form(primary, 'genitive') + (means ? ' через ' + means : '') + '.' : 'Функция стиха требует проверки.';
  }

  function transliterate(hebrew) { return Array.from(String(hebrew || '').replace(/[\u0591-\u05C7־]/g, '')).map(function(letter) { return TRANSLIT[letter] || ''; }).join(''); }

  return { isParticle: isParticle, particleText: particleText, wordReading: wordReading, verseReading: verseReading, verseFunction: verseFunction, transliterate: transliterate };
}));