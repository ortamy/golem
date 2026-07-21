/**
 * translation-comparator.js — Сравнение переводов
 * Параллельный просмотр ТМ, LXX, Синодального
 */

const TransComp = (function() {
  'use strict';

  // Тестовые данные для демонстрации
  const DATA = {
    'Берешит 1:1': {
      tm: 'בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ',
      lxx: 'Ἐν ἀρχῇ ἐποίησεν ὁ θεὸς τὸν οὐρανὸν καὶ τὴν γῆν',
      synodal: 'В начале сотворил Бог небо и землю.'
    },
    'Берешит 1:2': {
      tm: 'וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם וְרוּחַ אֱלֹהִים מְרַחֶפֶת עַל־פְּנֵי הַמָּיִם',
      lxx: 'ἡ δὲ γῆ ἦν ἀόρατος καὶ ἀκατασκεύαστος, καὶ σκότος ἐπάνω τῆς ἀβύσσου, καὶ πνεῦμα θεοῦ ἐπεφέρετο ἐπάνω τοῦ ὕδατος',
      synodal: 'Земля же была безвидна и пуста, и тьма над бездною, и Дух Божий носился над водою.'
    },
    'Берешит 1:3': {
      tm: 'וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי אוֹר',
      lxx: 'καὶ εἶπεν ὁ θεός· γενηθήτω φῶς. καὶ ἐγένετο φῶς',
      synodal: 'И сказал Бог: да будет свет. И стал свет.'
    },
    'Теилим 23:1': {
      tm: 'מִזְמוֹר לְדָוִד יְהוָה רֹעִי לֹא אֶחְסָר',
      lxx: 'Ψαλμὸς τῷ Δαυίδ. Κύριος ποιμαίνει με, καὶ οὐδέν με ὑστερήσει',
      synodal: 'Псалом Давида. Господь — Пастырь мой; я ни в чем не буду нуждаться.'
    },
    'Теилим 23:2': {
      tm: 'בִּנְאוֹת דֶּשֶׁא יַרְבִּיצֵנִי עַל מֵי מְנֻחוֹת יְנַהֲלֵנִי',
      lxx: 'εἰς τόπον χλόης, ἐκεῖ με κατεσκήνωσεν, ἐπὶ ὕδατος ἀναπαύσεως ἐξέθρεψέν με',
      synodal: 'Он покоит меня на злачных пажитях и водит меня к водам тихим.'
    },
    'Исайя 53:5': {
      tm: 'וְהוּא מְחֹלָל מִפְּשָׁעֵינוּ מְדֻכָּא מֵעֲוֹנֹתֵינוּ מוּסַר שְׁלוֹמֵנוּ עָלָיו וּבַחֲבֻרָתוֹ נִרְפָּא לָנוּ',
      lxx: 'αὐτὸς δὲ ἐτραυματίσθη διὰ τὰς ἀνομίας ἡμῶν καὶ μεμαλάκισται διὰ τὰς ἁμαρτίας ἡμῶν· παιδεία εἰρήνης ἡμῶν ἐπʼ αὐτόν· τῷ μώλωπι αὐτοῦ ἡμεῖς ἰάθημεν',
      synodal: 'Он изъязвлен был за грехи наши и мучим за беззакония наши; наказание мира нашего было на Нем, и ранами Его мы исцелились.'
    },
    'Шмот 20:2': {
      tm: 'אָנֹכִי יְהוָה אֱלֹהֶיךָ אֲשֶׁר הוֹצֵאתִיךָ מֵאֶרֶץ מִצְרַיִם מִבֵּית עֲבָדִים',
      lxx: 'ἐγώ εἰμι κύριος ὁ θεός σου, ὅστις ἐξήγαγόν σε ἐκ γῆς Αἰγύπτου, ἐξ οἴκου δουλείας',
      synodal: 'Я Господь, Бог твой, который вывел тебя из земли Египетской, из дома рабства.'
    },
    'Шмот 20:3': {
      tm: 'לֹא יִהְיֶה לְךָ אֱלֹהִים אֲחֵרִים עַל פָּנָי',
      lxx: 'οὐκ ἔσονταί σοι θεοὶ ἕτεροι πλὴν ἐμοῦ',
      synodal: 'Да не будет у тебя других богов пред лицем Моим.'
    }
  };

  function init() {
    // Готово
  }

  function search() {
    var query = document.getElementById('tc-search').value.trim();
    var results = document.getElementById('tc-results');
    var placeholder = document.getElementById('tc-placeholder');

    if (!query) {
      results.style.display = 'none';
      placeholder.style.display = 'block';
      return;
    }

    // Пытаемся найти точное совпадение или частичное
    var found = null;
    var exactMatch = null;

    Object.keys(DATA).forEach(function(key) {
      if (key.toLowerCase() === query.toLowerCase()) {
        exactMatch = key;
      }
      if (!found && key.toLowerCase().indexOf(query.toLowerCase()) !== -1) {
        found = key;
      }
    });

    var matchKey = exactMatch || found;

    if (!matchKey) {
      results.style.display = 'none';
      placeholder.style.display = 'block';
      placeholder.innerHTML = '<div class="lab-alert lab-alert-warn">Данные для «' + query + '» пока не загружены. Попробуйте: <strong>Берешит 1:1</strong>, <strong>Теилим 23:1</strong>, <strong>Исайя 53:5</strong>, <strong>Шмот 20:2</strong>.</div>';
      return;
    }

    var entry = DATA[matchKey];
    document.getElementById('tc-tm').textContent = entry.tm;
    document.getElementById('tc-lxx').textContent = entry.lxx;
    document.getElementById('tc-synodal').textContent = entry.synodal;
    results.style.display = 'block';
    placeholder.style.display = 'none';

    // Обновляем заголовки
    var header = document.querySelector('#tc-results .lab-card-header');
    if (header) header.textContent = matchKey;
  }

  return {
    init: init,
    search: search
  };
})();
