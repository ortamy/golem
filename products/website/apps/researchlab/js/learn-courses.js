/* learn-courses.js — данные практических курсов раздела «Обучение».
   Контент в отдельном модуле (JSON-структура), без жёсткой привязки к JS. */
(function (root) {
  'use strict';

  // Уровни: from-zero / base / advanced
  var COURSES = [
    {
      id: 'paleo-engineering',
      title: 'Палео-инженерия: путь с нуля',
      level: 'с нуля',
      levelKey: 'from-zero',
      status: 'скоро',
      modules: 4,
      description: 'Буква как функция, 22 буквы, слово как конструкция, первые разборы.'
    },
    {
      id: 'states-transitions',
      title: 'Состояния и переходы',
      level: 'базовый',
      levelKey: 'basic',
      status: 'скоро',
      modules: 4,
      description: 'Карта состояний, Тоху/Боху/Хошех/Тхом, Мицраим → Эвр → Мидбар, Давар.'
    },
    {
      id: 'derekh-fathers',
      title: 'Дерех: путь отцов',
      level: 'продвинутый',
      levelKey: 'advanced',
      status: 'в разработке',
      modules: 4,
      description: 'Авраhам, Яаков, Моше, Йеhошуа, свой план выхода.'
    },
    {
      id: 'language-without-religionisms',
      title: 'Язык без религионимов',
      level: 'базовый',
      levelKey: 'basic',
      status: 'в разработке',
      modules: 4,
      description: 'Религионизмы, жертва → приближение, душа → нэфеш, закон → направление.'
    },
    {
      id: 'ai-paleo',
      title: 'ИИ + Палео',
      level: 'продвинутый',
      levelKey: 'advanced',
      status: 'в разработке',
      modules: 4,
      description: 'RAG по корням, агенты разбора, свой словарь, Harness.'
    }
  ];

  root.GolemCourses = { list: COURSES };
})(typeof window !== 'undefined' ? window : this);