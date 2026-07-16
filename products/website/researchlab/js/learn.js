/* Обучение: 22 буквы, четыре шага урока и игра «Угадай образ». */
(function(root) {
  'use strict';

  var PROGRESS_KEY = 'golem_learn_progress';
  var RECORD_KEY = 'golem_guess_record';
  var LETTER_KEYS = ['א','ב','ג','ד','ה','ו','ז','ח','ט','י','כ','ל','מ','נ','ס','ע','פ','צ','ק','ר','ש','ת'];
  var fallback = [
    ['א','𐤀','Алеф','бык','сила'],['ב','𐤁','Бет','дом','вместилище'],['ג','𐤂','Гимель','верблюд','движение'],['ד','𐤃','Далет','дверь','вход'],['ה','𐤄','Хе','дыхание','откровение'],['ו','𐤅','Вав','крюк','соединение'],['ז','𐤆','Заин','оружие','инструмент'],['ח','𐤇','Хет','ограда','отделение'],['ט','𐤈','Тет','змея','оборачивание'],['י','𐤉','Йод','рука','действие'],['כ','𐤊','Каф','ладонь','удержание'],['ל','𐤋','Ламед','посох','направление'],['מ','𐤌','Мем','вода','течение'],['נ','𐤍','Нун','рыба','жизнь'],['ס','𐤎','Самех','опора','поддержка'],['ע','𐤏','Аин','глаз','видение'],['פ','𐤐','Пе','рот','речь'],['צ','𐤑','Цаде','крюк','цель'],['ק','𐤒','Коф','игла','окружение'],['ר','𐤓','Реш','голова','начало'],['ש','𐤔','Шин','зуб','разрушение'],['ת','𐤕','Тав','знак','печать']
  ];
  var letters = [];
  var state = { view:'home', lesson:null, game:null, timer:null };

  function esc(value) { var div = document.createElement('div'); div.textContent = String(value == null ? '' : value); return div.innerHTML; }
  function now() { return new Date().toISOString(); }
  function read(key, fallbackValue) { try { var value = JSON.parse(localStorage.getItem(key)); return value == null ? fallbackValue : value; } catch (e) { return fallbackValue; } }
  function write(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) {} }
  function progress() { var value = read(PROGRESS_KEY, {letters:{}, lastActivity:''}); if (!value.letters) value.letters = {}; return value; }
  function record() { var value = Number(localStorage.getItem(RECORD_KEY)); return isFinite(value) && value > 0 ? value : 0; }
  function touch(p) { p.lastActivity = now(); write(PROGRESS_KEY, p); }
  function shuffle(list) { return list.slice().sort(function() { return Math.random() - .5; }); }
  function byKey(key) { return letters.filter(function(item) { return item.hebrew === key; })[0]; }
  function distractors(item, field) { return shuffle(letters.filter(function(x) { return x.hebrew !== item.hebrew; })).slice(0,3).concat(item).sort(function() { return Math.random() - .5; }); }
  function inputMatch(value, expected) { return String(value || '').trim().toLocaleLowerCase('ru-RU').replace(/[ё]/g,'е') === String(expected).toLocaleLowerCase('ru-RU').replace(/[ё]/g,'е'); }
  function getContainer() { return document.getElementById('learn-app'); }
  function setView(view) { state.view = view; render(); }

  function loadLetters() {
    var source = root.PaleoLetters && root.PaleoLetters.byHebrew;
    LETTER_KEYS.forEach(function(key, index) {
      var entry = source && source[key];
      letters.push(entry ? {hebrew:key,paleo:entry.paleo,name:entry.name,image:entry.image,meaning:entry.meaning} : {hebrew:fallback[index][0],paleo:fallback[index][1],name:fallback[index][2],image:fallback[index][3],meaning:fallback[index][4]});
    });
  }

  function statsMarkup() {
    var p = progress(), completed = letters.filter(function(item) { return p.letters[item.hebrew] && p.letters[item.hebrew].status === 'complete'; }).length;
    var last = p.lastActivity ? new Date(p.lastActivity).toLocaleDateString('ru-RU') : 'Пока нет';
    return '<div class="learn-stats"><div class="learn-stat"><span class="learn-stat-label">Прогресс по буквам</span><strong class="learn-stat-value">' + completed + '/22</strong></div><div class="learn-stat"><span class="learn-stat-label">Рекорд в игре</span><strong class="learn-stat-value">' + record() + ' очков</strong></div><div class="learn-stat"><span class="learn-stat-label">Последняя активность</span><strong class="learn-stat-value" style="font-size:21px">' + esc(last) + '</strong></div></div>';
  }

  function renderHome() {
    var p = progress(), completed = letters.filter(function(item) { return p.letters[item.hebrew] && p.letters[item.hebrew].status === 'complete'; }).length;
    return '<div class="learn-hero"><div><h1><img src="../assets/icons/32/ui/book.png" class="lab-icon" alt="">Обучение</h1><p class="subtitle">Верните глазу древнего читателя предметный образ буквы: от знака к действию.</p></div><div class="learn-hero-mark" aria-hidden="true">𐤀𐤁𐤂</div></div>' + statsMarkup() + '<div class="learn-mode-grid"><button class="learn-mode-card" type="button" onclick="LearnLab.openLessons()"><span class="learn-mode-icon" aria-hidden="true">𐤀</span><h2>Изучение иврита</h2><p>22 урока по буквам: название, образ, значение и обратное узнавание символа.</p><div class="learn-mode-meta"><span>' + completed + '/22 уроков</span><span>→</span></div><div class="learn-progress-bar" aria-label="Прогресс ' + completed + ' из 22"><span style="width:' + (completed / 22 * 100) + '%"></span></div></button><button class="learn-mode-card" type="button" onclick="LearnLab.openGame()"><span class="learn-mode-icon" aria-hidden="true">𐤔</span><h2>Угадай образ</h2><p>Игровой раунд на скорость: увидьте знак, выберите предметный образ и соберите серию.</p><div class="learn-mode-meta"><span>Рекорд: ' + record() + ' очков</span><span>→</span></div></button></div><div class="learn-section-head" style="margin-top:32px"><h2>Состояние Свивы</h2><button type="button" class="lab-btn lab-btn-secondary learn-danger" onclick="LearnLab.reset()">Сбросить прогресс</button></div><p class="text-muted">Результаты уроков и рекорд сохраняются только в этом браузере.</p>';
  }

  function renderLessons() {
    var p = progress();
    var cards = letters.map(function(item, index) { var status = p.letters[item.hebrew] && p.letters[item.hebrew].status || 'new'; return '<button type="button" class="learn-letter-card ' + (status === 'complete' ? 'is-complete' : status === 'progress' ? 'is-progress' : '') + '" style="animation-delay:' + index * 25 + 'ms" onclick="LearnLab.openLesson(\'' + item.hebrew + '\')"><span class="learn-letter-status" aria-label="' + (status === 'complete' ? 'завершено' : status === 'progress' ? 'в процессе' : 'не начато') + '"></span><span class="learn-letter-paleo" lang="hbo">' + item.paleo + '</span><span class="learn-letter-name">' + esc(item.name) + '</span><span class="learn-letter-image">' + esc(item.image) + '</span><span class="learn-letter-meaning">' + esc(item.meaning) + '</span></button>'; }).join('');
    return '<button type="button" class="lab-btn lab-btn-secondary learn-back" onclick="LearnLab.home()">← К обучению</button><div class="learn-section-head"><div><h1>Изучение иврита</h1><p class="subtitle">Выберите букву. Серый — не начат, золотой — в процессе, зелёный — завершён.</p></div></div><div class="learn-legend"><span>не начат</span><span class="progress">в процессе</span><span class="complete">завершён</span></div><div class="learn-letter-grid">' + cards + '</div>';
  }

  function renderLesson() {
    var item = state.lesson.item, step = state.lesson.step, choices, prompt, body;
    if (step === 1 || step === 3) { prompt = step === 1 ? 'Введите название буквы' : 'Введите значение образа'; body = '<label for="learn-answer">' + prompt + '</label><input id="learn-answer" class="learn-answer-input" autocomplete="off" autofocus placeholder="Ваш ответ">'; }
    else { choices = distractors(item); prompt = step === 2 ? 'Выберите правильный образ' : 'Выберите правильный символ'; body = '<div class="learn-options">' + choices.map(function(option) { var label = step === 2 ? option.image : option.paleo; var value = step === 2 ? option.hebrew : option.hebrew; return '<button type="button" class="learn-option" data-answer="' + esc(value) + '" onclick="LearnLab.answer(\'' + esc(value).replace(/'/g,"\\'") + '\')">' + esc(label) + '</button>'; }).join('') + '</div>'; }
    return '<div class="learn-lesson"><button type="button" class="lab-btn lab-btn-secondary learn-back" onclick="LearnLab.openLessons()">← К буквам</button><div class="learn-lesson-top"><h1>' + esc(item.name) + '</h1><span class="learn-step-label">Шаг ' + step + ' из 4</span></div><div class="learn-step-track">' + [1,2,3,4].map(function(n) { return '<span class="' + (n <= step ? 'active' : '') + '"></span>'; }).join('') + '</div><section class="learn-question"><div class="learn-question-symbol" lang="hbo">' + item.paleo + '</div><p>' + prompt + '</p><div class="learn-question-body">' + body + '</div><div id="learn-feedback" class="learn-feedback" role="status" aria-live="polite"></div>' + ((step === 1 || step === 3) ? '<div class="learn-answer-actions"><button type="button" class="lab-btn lab-btn-primary" onclick="LearnLab.submitText()">Проверить</button></div>' : '') + '</section></div>';
  }

  function renderGame() {
    var game = state.game;
    if (game.done) return '<div class="learn-game"><button type="button" class="lab-btn lab-btn-secondary learn-back" onclick="LearnLab.home()">← К обучению</button><div class="learn-result"><h1>Раунд завершён</h1><div class="learn-result-score">' + game.score + '</div><p>Очков набрано. Рекорд: <strong>' + record() + '</strong>.</p><button type="button" class="lab-btn lab-btn-primary" onclick="LearnLab.openGame()">Играть снова</button></div></div>';
    var choices = game.choices; return '<div class="learn-game"><button type="button" class="lab-btn lab-btn-secondary learn-back" onclick="LearnLab.home()">← К обучению</button><div class="learn-game-bar"><div class="learn-game-metric">Раунд <strong>' + game.round + '/10</strong></div><div class="learn-game-metric">Счёт <strong>' + game.score + '</strong></div><div class="learn-game-metric learn-timer ' + (game.time <= 8 ? 'is-low' : '') + '">Время <strong>' + game.time + 'с</strong></div></div><div class="learn-game-symbol"><small>Какой образ несёт этот знак?</small><span class="symbol" lang="hbo">' + game.item.paleo + '</span></div><div class="learn-options learn-game-options">' + choices.map(function(option) { return '<button type="button" class="learn-option" data-answer="' + esc(option.hebrew) + '" onclick="LearnLab.gameAnswer(\'' + option.hebrew + '\')">' + esc(option.image) + '</button>'; }).join('') + '</div><div id="learn-game-feedback" class="learn-game-feedback" role="status" aria-live="polite"></div></div>';
  }

  function render() { var container = getContainer(); if (!container || !letters.length) return; if (state.view === 'lessons') container.innerHTML = renderLessons(); else if (state.view === 'lesson') container.innerHTML = renderLesson(); else if (state.view === 'game') container.innerHTML = renderGame(); else container.innerHTML = renderHome(); }
  function markStarted(item) { var p = progress(); if (!p.letters[item.hebrew] || p.letters[item.hebrew].status !== 'complete') p.letters[item.hebrew] = {status:'progress',score:0}; touch(p); }
  function feedback(text, ok) { var el = document.getElementById('learn-feedback'); if (el) { el.textContent = text; el.className = 'learn-feedback ' + (ok ? 'is-correct' : 'is-wrong'); } }
  function advance(ok) { if (!ok) return; state.lesson.score++; if (state.lesson.step < 4) { state.lesson.step++; render(); } else { var p = progress(); p.letters[state.lesson.item.hebrew] = {status:'complete',score:state.lesson.score,attempts:(p.letters[state.lesson.item.hebrew] && p.letters[state.lesson.item.hebrew].attempts || 0) + 1,lastActivity:now()}; touch(p); state.view = 'lesson'; state.lesson.done = true; render(); } }

  var api = {
    init: function() { if (!letters.length) loadLetters(); render(); },
    home: function() { state.view='home'; state.lesson=null; stopTimer(); render(); },
    openLessons: function() { state.view='lessons'; stopTimer(); render(); },
    openLesson: function(key) { var item = byKey(key); if (!item) return; markStarted(item); state.lesson={item:item,step:1,score:0,done:false}; state.view='lesson'; render(); },
    submitText: function() { var input = document.getElementById('learn-answer'), step = state.lesson.step, expected = step === 1 ? state.lesson.item.name : state.lesson.item.meaning; if (!input) return; var ok = inputMatch(input.value, expected); if (ok) advance(true); else feedback('Пока не совпало. Попробуйте ещё раз.', false); },
    answer: function(key) { var ok = key === state.lesson.item.hebrew; if (ok) advance(true); else feedback('Это другой образ. Попробуйте ещё раз.', false); },
    openGame: function() { stopTimer(); state.view='game'; state.game={round:1,score:0,streak:0,time:30,done:false}; nextRound(); startTimer(); },
    gameAnswer: function(key) { var game=state.game; if (!game || game.locked) return; game.locked=true; var ok=key===game.item.hebrew, earned=0; if(ok){game.streak++; earned=10*(game.streak >= 3 ? 3 : game.streak === 2 ? 2 : 1); game.score+=earned;} else {game.streak=0; game.score=Math.max(0,game.score-5);} render(); var feedbackEl=document.getElementById('learn-game-feedback'); if(feedbackEl){feedbackEl.textContent=ok ? 'Верно! +' + earned + ' очков' : 'Неверно. Правильный образ: ' + game.item.image; feedbackEl.className='learn-game-feedback ' + (ok?'correct':'wrong');} setTimeout(function(){ if(!state.game || state.game !== game) return; if(game.round >= 10) finishGame(); else {game.round++; nextRound();} },700); },
    reset: function() { if (!window.confirm('Сбросить весь прогресс обучения и рекорд игры?')) return; localStorage.removeItem(PROGRESS_KEY); localStorage.removeItem(RECORD_KEY); state.view='home'; render(); }
  };
  function nextRound() { var item=letters[Math.floor(Math.random()*letters.length)]; state.game.item=item; state.game.choices=distractors(item); state.game.locked=false; render(); }
  function finishGame() { stopTimer(); state.game.done=true; var best=Math.max(record(),state.game.score); localStorage.setItem(RECORD_KEY,String(best)); render(); }
  function stopTimer() { if(state.timer){clearInterval(state.timer);state.timer=null;} }
  function startTimer() { stopTimer(); state.timer=setInterval(function(){ if(!state.game || state.game.done) return stopTimer(); state.game.time--; if(state.game.time<=0){state.game.time=0; finishGame();} else render(); },1000); }
  root.LearnLab = api;
}(typeof window !== 'undefined' ? window : this));