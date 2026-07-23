(function(window, document) {
  'use strict';

  var ROOT_SELECTOR = '#labContent';
  var TARGETS = {
    'dashboard': {
      kicker: 'ГОЛЕМ · РАБОЧИЙ СТОЛ',
      title: 'Рабочий стол исследователя',
      subtitle: 'Сводка текущего поля: корни, дела, словари и переходы между слоями исследования.',
      icon: 'archaeology/testtube.png'
    },
    'learn': {
      kicker: 'ГОЛЕМ · ОБУЧЕНИЕ',
      title: 'Обучение',
      subtitle: 'Возвращение к предметному образу буквы: от знака к действию, от наблюдения к собранному смыслу.',
      icon: 'ui/book.png'
    },
    'researches': {
      kicker: 'ГОЛЕМ · РАЗОБЛАЧЕНИЯ',
      title: 'Разоблачения',
      subtitle: 'Разбор подмен смысла в языке, истории, экономике и других сферах — через восстановление ивритских корней ТаНаХа.',
      icon: 'scribe/scrolls.png'
    },
    'root-dictionary': {
      kicker: 'ГОЛЕМ · КОРНЕВОЙ СЛОВАРЬ',
      title: 'Корневой словарь',
      subtitle: 'Поиск по корням иврита: форма, значение и восстановленная физика слова.',
      icon: 'ui/book.png'
    },
    'heraldry': {
      kicker: 'ГОЛЕМ · ГЕРБОВНИК',
      title: 'Гербовник',
      subtitle: 'Знаки, образы и связки смыслов, собранные в палео-образную систему.',
      icon: 'scribe/scrolls.png'
    },
    'cartography': {
      kicker: 'ГОЛЕМ · КАРТОГРАФИЯ',
      title: 'Картография',
      subtitle: 'Карта смысловых территорий, переходов и подмен, которые формируют Свиву.',
      icon: 'ui/web.png'
    },
    'states': {
      kicker: 'ГОЛЕМ · КАРТА СОСТОЯНИЙ',
      title: 'Карта состояний',
      subtitle: 'Наблюдение за состояниями системы и переходами между ними.',
      icon: 'ui/web.png'
    },
    'paleo-mechanics': {
      kicker: 'ГОЛЕМ · ПАЛЕО-МЕХАНИКА',
      title: 'Палео-механика',
      subtitle: 'Механика действия: как корень собирает движение, форму и результат.',
      icon: 'crafts/hammer-and-chisel.png'
    },
    'paleo-linguistics': {
      kicker: 'ГОЛЕМ · ПАЛЕО-ЛИНГВИСТИКА',
      title: 'Палео-лингвистика',
      subtitle: 'Эволюция письма и языка через форму букв, корни и физику образа.',
      icon: 'scribe/scroll.png'
    },
    'prompt-generator': {
      kicker: 'ГОЛЕМ · ГЕНЕРАТОР ПРОМПТОВ',
      title: 'Генератор промптов',
      subtitle: 'Сборка точного исследовательского запроса из фрагментов, методов и ограничений.',
      icon: 'ui/question.png'
    },
    'board': {
      kicker: 'ГОЛЕМ · ИССЛЕДОВАТЕЛЬСКАЯ ДОСКА',
      title: 'Исследовательская доска',
      subtitle: 'Связывайте наблюдения, источники и гипотезы в едином поле Хук / Свива.',
      icon: 'crafts/hammer-and-chisel.png'
    },
    'translation-comparator': {
      kicker: 'ГОЛЕМ · КОМПАРАТОР',
      title: 'Компаратор',
      subtitle: 'Сопоставление переводов для обнаружения сдвигов, потерь и смысловых подмен.',
      icon: 'ui/scales.png'
    },
    'board-library': {
      kicker: 'ГОЛЕМ · БИБЛИОТЕКА',
      title: 'Библиотека',
      subtitle: 'Архив исследовательских досок, к которым можно вернуться и продолжить сборку.',
      icon: 'scribe/scrolls.png'
    },
    'religionism-checker': {
      kicker: 'ГОЛЕМ · ЧЕКЕРЫ',
      title: 'Чекеры',
      subtitle: 'Проверка текста на устойчивые подмены и расхождения между словом и его конструкцией.',
      icon: 'ui/question.png'
    },
    'davar-checker': {
      kicker: 'ГОЛЕМ · ЧЕКЕРЫ',
      title: 'Чекеры',
      subtitle: 'Проверка слова: обозначает ли оно конструкцию с физическим эквивалентом или остаётся пустым звуком.',
      icon: 'ui/question.png'
    },
    'word-analyzer': {
      kicker: 'ГОЛЕМ · РАЗБОР СЛОВ',
      title: 'Разбор слов',
      subtitle: 'Переход от формы слова к корню, образу и карте смысловых сдвигов.',
      icon: 'archaeology/testtube.png'
    },
    'paleo-images': {
      kicker: 'ГОЛЕМ · ПАЛЕО-ОБРАЗЫ',
      title: 'Палео-образы',
      subtitle: 'Буквы как предметные образы: форма, движение и собранное значение.',
      icon: 'paleo/track.png'
    },
    'etymology-lab': {
      kicker: 'ГОЛЕМ · ЭТИМОЛОГИЯ',
      title: 'Этимологическая лаборатория',
      subtitle: 'Исследование слова через корень, родственные формы и восстановленную физику.',
      icon: 'archaeology/testtube.png'
    },
    'scripture-reader': {
      kicker: 'ГОЛЕМ · КНИГОЧТЕНИЕ',
      title: 'Книгочтение',
      subtitle: 'Чтение текста по слоям: строка, корень, образ и действие.',
      icon: 'ui/book.png'
    },
    'research-generator': {
      kicker: 'ГОЛЕМ · ГЕНЕРАТОР ИССЛЕДОВАНИЙ',
      title: 'Генератор исследований',
      subtitle: 'Сборка исследовательского маршрута из темы, источников, корней и методов.',
      icon: 'crafts/hammer-and-chisel.png'
    },
    'board-generator': {
      kicker: 'ГОЛЕМ · ГЕНЕРАТОР ДОСОК',
      title: 'Генератор исследовательских досок',
      subtitle: 'Создание рабочего поля для связки наблюдений, источников и гипотез.',
      icon: 'scribe/scroll.png'
    },
    'investigation': {
      kicker: 'ГОЛЕМ · РАССЛЕДОВАНИЕ',
      title: 'Расследование',
      subtitle: 'Пошаговое движение от наблюдения к источнику, сдвигу и восстановленному выводу.',
      icon: 'ui/question.png'
    },
    'religionisms': {
      kicker: 'ГОЛЕМ · РЕЛИГИОНИЗМЫ',
      title: 'Религионизмы',
      subtitle: 'Карта устойчивых формул и слоёв, через которые смысл отрывается от конструкции.',
      icon: 'ui/question.png'
    },
    'vision': {
      kicker: 'ГОЛЕМ · АНАЛИЗ ИЗОБРАЖЕНИЙ',
      title: 'Визуальный анализатор',
      subtitle: 'Чтение изображения как поля знаков, форм и связей.',
      icon: 'archaeology/lamp.png'
    },
    'ai-agents': {
      kicker: 'ГОЛЕМ · АГЕНТЫ',
      title: 'AI-Агенты',
      subtitle: 'Исследовательские роли для сбора, проверки и связывания материала.',
      icon: 'crafts/hammer-and-chisel.png'
    },
    'ed-chat': {
      kicker: 'ГОЛЕМ · НЕЙРОЧАТ',
      title: 'Нейрочат',
      subtitle: 'Диалоговое поле для уточнения наблюдений и сборки следующего шага.',
      icon: 'crafts/hammer-and-chisel.png'
    },
    'paleo-keyboard': {
      kicker: 'ГОЛЕМ · ПАЛЕО-КЛАВИАТУРА',
      title: 'Палео-ивритская клавиатура',
      subtitle: 'Набор палео-формы и переход к разбору слова через знак и действие.',
      icon: 'paleo/track.png'
    },
    'dictionaries': {
      kicker: 'ГОЛЕМ · СЛОВАРИ',
      title: 'Словари',
      subtitle: 'Словарные карты подмен с ивритским соответствием и палео-формой.',
      icon: 'ui/book.png'
    },
    'exposure': {
      kicker: 'ГОЛЕМ · ПРИНЦИПЫ',
      title: 'Принципы',
      subtitle: 'Материалы о подменах, их механизмах и переходах между слоями смысла.',
      icon: 'archaeology/lamp.png'
    },
    'methodology': {
      kicker: 'ГОЛЕМ · МЕТОДОЛОГИЯ',
      title: 'Методология',
      subtitle: 'Манифест, принципы, методы разоблачения и механизмы подмены — в едином интерфейсе с карточками.',
      icon: 'crafts/hammer-and-chisel.png'
    },
    'language-map': {
      kicker: 'ГОЛЕМ · КАРТА ЯЗЫКОВ',
      title: 'Карта языков',
      subtitle: 'Сравнение живых языков по способности собирать Давар и переводить речь между состояниями.',
      icon: 'paleo/track.png'
    },
    'admin-settings': {
      kicker: 'ГОЛЕМ · НАСТРОЙКИ',
      title: 'Настройки / Администрирование',
      subtitle: 'Управление моделями, кэшем, агентами и состоянием исследовательской системы.',
      icon: 'ui/settings.png'
    },
    'exposure-editor': {
      kicker: 'ГОЛЕМ · РЕДАКТОР',
      title: 'Редактор разоблачений',
      subtitle: 'Сборка материала, источников и выводов в единое исследовательское дело.',
      icon: 'archaeology/lamp.png'
    }
  };

  var observedContainers = [];
  var documentObserver = null;
  var scheduled = false;

  function createElement(tag, className, text) {
    var element = document.createElement(tag);
    element.className = className;
    if (text) element.textContent = text;
    return element;
  }

  function createHero(moduleId, config) {
    var hero = createElement('section', 'lab-hero', '');
    hero.setAttribute('aria-labelledby', 'lab-hero-title-' + moduleId);
    hero.setAttribute('data-lab-hero', moduleId);

    var icon = document.createElement('img');
    icon.className = 'lab-hero__icon';
    icon.src = '../../assets/icons/32/' + config.icon;
    icon.alt = '';
    icon.setAttribute('aria-hidden', 'true');

    var body = createElement('div', 'lab-hero__body', '');
    body.appendChild(createElement('p', 'lab-hero__kicker', config.kicker));

    var title = createElement('h1', 'lab-hero__title', config.title);
    title.id = 'lab-hero-title-' + moduleId;
    body.appendChild(title);
    body.appendChild(createElement('p', 'lab-hero__subtitle', config.subtitle));

    hero.appendChild(icon);
    hero.appendChild(body);
    return hero;
  }

  function mount(container) {
    if (!container || !container.id || !TARGETS[container.id]) return;
    var moduleId = container.id;
    var hero = null;
    for (var i = 0; i < container.children.length; i++) {
      if (container.children[i].classList.contains('lab-hero') &&
          container.children[i].getAttribute('data-lab-hero') === moduleId) {
        hero = container.children[i];
        break;
      }
    }
    if (!hero) {
      hero = createHero(moduleId, TARGETS[moduleId]);
      container.insertBefore(hero, container.firstChild);
    } else if (container.firstChild !== hero) {
      container.insertBefore(hero, container.firstChild);
    }
    container.classList.add('lab-hero-module', 'lab-hero-module--' + moduleId);
  }

  function scan() {
    var root = document.querySelector(ROOT_SELECTOR) || document.body;
    Object.keys(TARGETS).forEach(function(moduleId) {
      var container = document.getElementById(moduleId);
      if (!container) return;
      mount(container);
      if (observedContainers.indexOf(container) === -1) {
        observedContainers.push(container);
        if (window.MutationObserver) {
          new MutationObserver(function() { scheduleScan(); }).observe(container, { childList: true });
        }
      }
    });
    if (root && !documentObserver && window.MutationObserver) {
      documentObserver = new MutationObserver(function() { scheduleScan(); });
      documentObserver.observe(root, { childList: true, subtree: true });
    }
  }

  function scheduleScan() {
    if (scheduled) return;
    scheduled = true;
    window.setTimeout(function() {
      scheduled = false;
      scan();
    }, 0);
  }

  window.LabHero = {
    targets: TARGETS,
    mount: mount,
    mountAll: scan,
    observe: function() {
      scan();
      return this;
    }
  };
})(window, document);