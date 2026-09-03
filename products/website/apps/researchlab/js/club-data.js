/**
 * club-data.js — адаптер данных Палео-клуба.
 * В production читает Supabase, локально использует MOCK и localStorage.
 */
const ClubData = (function () {
  'use strict';
  var STORAGE_KEY = 'golem_club_posts';
  var MOCK = {
    profiles: [
      { handle: 'маскиль_а', level: 3, color: '#b8860b', initial: 'М' },
      { handle: 'ор_ищет', level: 2, color: '#8b6914', initial: 'О' },
      { handle: 'собиратель', level: 5, color: '#d4a017', initial: 'С' },
      { handle: 'наблюдатель', level: 1, color: '#6b4a10', initial: 'Н' },
      { handle: 'свидетель', level: 4, color: '#c9a227', initial: 'С' },
      { handle: 'связующий', level: 2, color: '#a08050', initial: 'С' }
    ],
    cards: [
      { id: 'shabbat', type: 'word', ref: 'שבת', title: 'Шаббат — остановка в потоке', synthesis: 'Корень 𐤔𐤁𐤕: шаббат — точка возврата в цикл творения.', participants: 0, posts_count: 7, emet: 12, questions: 3, confidence: 'рабочая карта', attachment: { route: '#learn/paleo-trainer', params: 'shabbat', label: 'Тренажёр' } },
      { id: 'mitsraim', type: 'word', ref: 'מצרים', title: 'Мицраим — сужение потока', synthesis: 'Корень 𐤌𐤑𐤓: узость и сужение как форма потока.', participants: 1, posts_count: 4, emet: 8, questions: 2, confidence: 'рабочая гипотеза', attachment: { route: '#root-dictionary', params: 'mitsraim', label: 'Словарь' } },
      { id: 'sheol', type: 'state', ref: 'שאול', title: 'Состояние Шеол', synthesis: 'Тень жизни: отсутствие потока и возможность выхода.', participants: 2, posts_count: 5, emet: 6, questions: 4, confidence: 'требует проверки', attachment: { route: '#states', params: 'sheol', label: 'Состояния' } },
      { id: 'board-avraam', type: 'board', ref: 'אברהם', title: 'Доска: Авраам — отец множества', synthesis: 'Разбор имени: 𐤀𐤁𐤓𐤄𐤌. Сила дома движется к множеству.', participants: 6, posts_count: 11, emet: 15, questions: 5, confidence: 'подтверждается', attachment: { route: '#board', params: 'avraam', label: 'Доска' } }
    ],
    comments: {
      shabbat: [
        { id: 'c1', author: 0, body: 'Шаббат — точка возврата в цикле.', emet: 3, questions: 1 },
        { id: 'c2', author: 1, body: 'Корень שבת можно прочитать как возвращение в дом.', emet: 2, questions: 0 },
        { id: 'c3', author: 2, body: 'Шав и бет: возвращение домой каждую неделю.', emet: 5, questions: 0, attachment: { route: '#root-dictionary', params: 'shabat', label: 'שבת' } }
      ],
      mitsraim: [{ id: 'c4', author: 3, body: 'Узость — форма, которая сжимает поток.', emet: 1, questions: 0 }, { id: 'c5', author: 4, body: 'Интересно сравнить эту механику с другими культурами.', emet: 2, questions: 1 }],
      sheol: [{ id: 'c6', author: 5, body: 'Шеол — отсутствие потока, а не окончательная точка.', emet: 4, questions: 2 }],
      'board-avraam': [{ id: 'c7', author: 0, body: 'Авраам: сила дома движется к множеству.', emet: 6, questions: 0 }, { id: 'c8', author: 1, body: 'Доска помогает увидеть связи.', emet: 3, questions: 0 }]
    }
  };
  function localComments(id) { var comments = (MOCK.comments[id] || []).slice(); try { comments = comments.concat(JSON.parse(localStorage.getItem(STORAGE_KEY + '_' + id) || '[]')); } catch (e) {} return comments; }
  function getCards() { var client = window.supabase || window.supabaseClient; if (client && client.from) return client.from('research_threads').select('*').order('created_at', { ascending: false }).then(function (r) { if (r.error || !r.data || !r.data.length) throw r.error || Error('empty'); return r.data; }).catch(function () { return MOCK.cards; }); return Promise.resolve(MOCK.cards); }
  function getCard(id) { return getCards().then(function (cards) { return cards.find(function (card) { return card.id === id; }); }); }
  function getComments(id) { var client = window.supabase || window.supabaseClient; if (client && client.from) return client.from('research_comments').select('*').eq('thread_id', id).order('created_at', { ascending: true }).then(function (r) { if (r.error || !r.data) throw r.error || Error('empty'); return r.data; }).catch(function () { return localComments(id); }); return Promise.resolve(localComments(id)); }
  function addComment(id, comment) { comment.id = 'local_' + Date.now(); comment.emet = 0; comment.questions = 0; try { var key = STORAGE_KEY + '_' + id; var saved = JSON.parse(localStorage.getItem(key) || '[]'); saved.push(comment); localStorage.setItem(key, JSON.stringify(saved)); } catch (e) {} return Promise.resolve(comment); }
  function getProfile(index) { return MOCK.profiles[index % MOCK.profiles.length]; }
  function getWordOfDay() { return fetch('data/roots/roots.json').then(function (r) { return r.json(); }).then(function (roots) { var root = roots[0]; return { hebrew: root.root, paleo: root.paleo, translit: root.translit, gloss: root.meaning, image: root.image }; }).catch(function () { return { hebrew: 'אב', paleo: ['𐤀', '𐤁'], translit: 'AV', gloss: 'отец, источник', image: 'сила дома' }; }); }
  return { getCards: getCards, getCard: getCard, getComments: getComments, addComment: addComment, getProfile: getProfile, getWordOfDay: getWordOfDay, MOCK: MOCK };
}());
window.ClubData = ClubData;