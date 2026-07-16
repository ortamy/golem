# 📋 ТЕХНИЧЕСКИЙ ДОЛГ

**Метаданные файла**
- **Файл:** `docs/TECHNICAL-DEBT.md`
- **Версия:** 2.3
- **Дата создания:** 2026-05-28
- **Последнее обновление:** 2026-06-17
- **Причина обновления:** Добавлены 25 тем для исследований из сессии 2026-06-17
- **Статус:** Активный
- **Тема:** Технический долг и задачи по развитию проекта
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `docs/TECHNICAL-DEBT.md`, `docs/IDEAS.md`, `docs/ROADMAP.md`
- **Хеш:** ожидает
- **Достоверность:** средняя
- **Последний аудит:** 2026-06-17

---

## 📋 АКТИВНЫЕ ЗАДАЧИ

### 🤖 Автономный агент «Эд»

- [ ] Запустить `ed/neuro/inference/server.py` локально
- [ ] Дообучить `ed/agent/agent.py` — добавить планировщик
- [ ] Интеграция с Cline — Эд создаёт файлы задач, Cline читает и выполняет
- [ ] Память агента — контекст между сессиями через `memory.py`
- [ ] Режим «автономный стратег»

### 🆕 Новые скрипты

- [ ] `check-md-quality.py` — проверка качества .md файлов
- [ ] `generate-sitemap.py` — sitemap.xml
- [ ] `generate-search-index.py` — полнотекстовый индекс для веб-интерфейса
- [ ] `generate-rss.py` — RSS новых исследований
- [ ] `watch-changes.py` — следит за файлами и запускает чекеры
- [ ] `deploy.sh` — деплой одной командой
- [ ] `backup-rotation.py` — ротация старых бэкапов

### База ТаНаХа

- [ ] Загрузить полный ТаНаХ в `tanakh.db`
- [ ] Интегрировать `check-tanakh-references.py` с `check-links.py`

### Веб-интерфейс

- [ ] Языковые версии (RU, EN, HE)
- [ ] Полнотекстовый поиск по содержимому файлов
- [ ] Подсветка иврита (rtl, шрифт)
- [ ] PWA — установка на телефон
- [ ] Офлайн-доступ через Service Worker
- [ ] Хлебные крошки в ПК-версии
- [ ] Режим чтения — скрыть сайдбар
- [ ] Подвал с цитатой дня

### Контент — заполнить пустые файлы

- [ ] `content/terminology/yetzer-lev.md`
- [ ] `content/terminology/erech-apayim.md`

---

## 📝 НОВЫЕ ФАЙЛЫ ДЛЯ НАПОЛНЕНИЯ КАТЕГОРИЙ

### Темы из сессии 2026-06-17

- [ ] Рахав — `content/tanakh/persons/rachav.md` — хесед без религиозной системы, язычница в родословии Машиаха
- [ ] Сдвиг акцента с Яхве на Йешуа — `content/researches/language/shift-yhwh-to-yeshua.md` — как греческий язык и Никея сместили фокус
- [ ] Энума Элиш vs Берешит — `content/researches/history/enuma-elish-vs-bereshit.md` — не заимствование, а разоблачение
- [ ] Канон ТаНаХа — `content/researches/tanakh/canon-formation.md` — как определили, что от Яхве, а что нет. Критерии, Явне, почему Маккавеи не вошли
- [ ] Микдаш меат — `content/terminology/mikdash-meat.md` — малое святилище в изгнании, Йехезкель 11:16
- [ ] Сахир — `content/terminology/sachir.md` — наёмный работник в Торе, защита Яхве
- [ ] Мехалелеhа — `content/terminology/mechaleleha.md` — осквернение Шаббата, сознательное vs вынужденное
- [ ] Мусар — `content/terminology/musar.md` — наставление, а не наказание. Йешаяhу 53:5
- [ ] Коhэн гадоль — `content/terminology/kohen-gadol.md` — великий священник, не «первосвященник»
- [ ] Йоханан Погружатель — `content/bashah/persons/yohanan-matbil.md` — последний пророк старого порядка, мост к Машиаху
- [ ] Последняя трапеза — `content/bashah/events/seudat-aharon.md` — Песах, маца, чаша, смысл
- [ ] Шавуот и дарование Руах — `content/bashah/events/shavuot-ruach.md` — исполнение Йоеля
- [ ] Шломо — `content/tanakh/persons/shlomo.md` — машиах, но не эвед Яхве. Почему
- [ ] Ктав Ашшури — `content/researches/language/ktav-ashuri.md` — происхождение квадратного письма, цепочка заимствований
- [ ] Иудаизм как продукт плена — `content/researches/history/judaism-after-exile.md` — когда вера Яхве стала иудаизмом
- [ ] Ашам — `content/terminology/asham.md` — повинная жертва, отличие от хатат, связь с Эвед Яхве
- [ ] Малки-Цедек — `content/tanakh/persons/malki-tsedek.md` — священник Всесильного Вышнего до Аhарона, прообраз Машиаха
- [ ] Два Машиаха — `content/researches/tanakh/two-mashiahs.md` — Машиах бен Йосеф и Машиах бен Давид, страдающий и царствующий
- [ ] Талмуд vs Тора — `content/researches/systems/talmud-vs-torah.md` — как устная традиция подменила письменную
- [ ] Никейский собор — `content/researches/history/nicaea-325.md` — что именно произошло, кто стоял за решениями
- [ ] Шаббат в истории — `content/researches/practices/shabbat-history.md` — от Торы до воскресенья, кто и когда перенёс
- [ ] Имя Яхве в тексте — `content/researches/tanakh/shem-yhwh-in-text.md` — сколько раз, где впервые, как прятали
- [ ] Септуагинта — `content/researches/manuscripts/septuagint-analysis.md` — первый перевод, что исказили, почему
- [ ] Акеда — `content/tanakh/events/akedat-itzchak.md` — жертвоприношение Ицхака как прообраз
- [ ] Десять речений — `content/tanakh/concepts/aseret-hadvarim.md` — не «заповеди», а «речения». Разбор каждого

### БаШаХ — перенести из researches/tanakh/

- [ ] `brit-hadashah.md` → `content/bashah/concepts/brit-hadashah.md`
- [ ] `drashat-hahar.md` → `content/bashah/teachings/drashat-hahar.md`
- [ ] `tfilat-yeshua.md` → `content/bashah/teachings/tfilat-yeshua.md`
- [ ] `sifrei-bashakh.md` → `content/bashah/books/sifrei-bashah.md`
- [ ] `psychikos-pneumatikos.md` → `content/bashah/concepts/psychikos-pneumatikos.md`
- [ ] `nicham-keifa.md` → `content/bashah/persons/nicham-keifa.md`
- [ ] `shaul-victim.md` → `content/bashah/persons/shaul.md`

### БаШаХ — создать новые

- [x] `content/bashah/concepts/besorah.md` ✅ — 2026-06-14
- [x] `content/bashah/concepts/kehillah.md` ✅ — 2026-06-14
- [x] `content/bashah/persons/keifa.md` ✅ — 2026-06-14
- [ ] `content/bashah/persons/yohanan-matbil.md` — Йоханан Погружатель
- [ ] `content/bashah/events/seudat-aharon.md` — Последняя трапеза
- [ ] `content/bashah/events/shavuot-ruach.md` — Шавуот — дарование Дыхания
- [ ] `content/bashah/events/tvilat-yeshua.md` — Погружение Йешуа
- [x] `content/bashah/events/tvilat-yeshua.md` ✅ — 2026-06-17
- [ ] `content/bashah/chronology/timeline.md` — Хронология событий БаШаХа
- [ ] `content/bashah/books/besorah-yohanan.md` — Бсора от Йоханана
- [ ] `content/bashah/books/iggrot-shaul.md` — Послания Шауля
- [ ] `content/bashah/books/hitgalut.md` — Откровение Йоханана
- [ ] `content/bashah/manuscripts/peshitta.md` — Пешитта
- [ ] `content/bashah/manuscripts/greek-manuscripts.md` — Греческие рукописи

### ТаНаХ — создать новые

- [ ] `content/tanakh/books/` — обзоры книг ТаНаХа
- [ ] `content/tanakh/books/bereshit.md` — Берешит
- [ ] `content/tanakh/books/shmot.md` — Шмот
- [ ] `content/tanakh/books/tehillim.md` — Теhиллим
- [ ] `content/tanakh/books/yeshayahu.md` — Йешаяhу
- [ ] `content/tanakh/manuscripts/masoretic-text.md` — Масоретский текст
- [ ] `content/tanakh/manuscripts/qumran.md` — Кумранские рукописи
- [ ] `content/tanakh/manuscripts/septuaginta.md` — Септуагинта
- [ ] `content/tanakh/translations/synodal.md` — Синодальный перевод
- [ ] `content/tanakh/translations/vulgata.md` — Вульгата
- [ ] `content/tanakh/chronology/timeline.md` — Хронология ТаНаХа
- [ ] `content/tanakh/persons/avraham.md` — Авраhам
- [ ] `content/tanakh/persons/moshe.md` — Моше
- [ ] `content/tanakh/persons/david.md` — Давид
- [ ] `content/tanakh/persons/eliyahu.md` — Элияhу
- [ ] `content/tanakh/events/yetziat-mitzraim.md` — Исход
- [ ] `content/tanakh/events/matan-torah.md` — Дарование Торы
- [ ] `content/tanakh/events/galut-bavel.md` — Вавилонский плен
- [ ] `content/tanakh/concepts/brit.md` — Союз
- [ ] `content/tanakh/concepts/korban.md` — Приближение
- [ ] `content/tanakh/concepts/shabbat.md` — Шаббат
- [ ] `content/tanakh/prophecies/mashiach.md` — Пророчества о Машиахе
- [ ] `content/tanakh/prophecies/yom-yhwh.md` — День Яхве
- [ ] `content/tanakh/prophecies/new-yerushalaim.md` — Новый Йерушалаим
- [ ] `content/tanakh/geography/yerushalaim.md` — Йерушалаим
- [ ] `content/tanakh/geography/mitzraim.md` — Мицраим
- [ ] `content/tanakh/geography/bavel.md` — Бавэль
- [ ] `content/tanakh/poetry/tehillim.md` — Псалмы
- [ ] `content/tanakh/poetry/mishlei.md` — Притчи

### Изучение иврита

- [ ] `content/learn-hebrew/paleo-hebrew.md` — Палео-иврит подробно
- [ ] `content/learn-hebrew/verbs.md` — Глагольная система
- [ ] `content/learn-hebrew/syntax.md` — Синтаксис
- [ ] `content/learn-hebrew/reading-practice.md` — Практика чтения
- [ ] `content/learn-hebrew/common-roots.md` — 50 частых корней

### Терминология — из ideas/TERMINOLOGY-BACKLOG.md

- [ ] `yeho-shua.md` — יְהוֹשֻׁעַ
- [ ] `shem-yhwh.md` — שֵׁם יְהֹוָה
- [ ] `ruach-ha-kodesh.md` — רוּחַ הַקֹּדֶשׁ
- [ ] `nefilim.md` — נְּפִלִים
- [ ] `davar.md` — דָּבָר
- [ ] `mishkan.md` — מִשְׁכָּן
- [ ] `tzelem-elohim.md` — צֶלֶם אֱלֹהִים
- [ ] `goyim.md` — גּוֹיִם

---

## ✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ (2026-06-17)

- [x] `content/terminology/eved-yhwh.md` — Эвед Яхве: полное исследование — 2026-06-17
- [x] `content/terminology/ruach-yhwh.md` — Руах Яхве / Руах Кодеш / Руах Элоhим — одно дыхание, три имени — 2026-06-17
- [x] `content/bashah/events/tvilat-yeshua.md` — Твила Йешуа: посвящение, а не покаяние — 2026-06-17 (v1.1)
- [x] `content/researches/systems/gematria.md` — Гематрия: разоблачение системы числового контроля — 2026-06-17
- [x] `instructions/agent/AGENT-PROMPT.md` v3.2 — обновлён с иконками, без эмодзи — 2026-06-17
- [x] `instructions/agent/AGENT-RETROSPECTIVE.md` v1.1 — заполнена ретроспектива — 2026-06-17
- [x] `guides/GUIDE-DAVAR.md` v1.0 — создан с нуля — 2026-06-17
- [x] `tools/generators/generate-bashah-templates.py` — скрипт генерации шаблонов БаШаХа — 2026-06-17
- [x] 85+ шаблонов в `content/bashah/` — 2026-06-17

## ✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ (2026-06-11)

- [x] Реорганизация архитектуры: `content/`, `ed/`, `guides/`, `dictionaries/` — 2026-06-14
- [x] Переименование всех скриптов с префиксами — 2026-06-14
- [x] `tahor/` → `dictionaries/` — 2026-06-14
- [x] `philosophemes.md` → `exposure/` — 2026-06-14
- [x] `drafts/` → `backlog/` — 2026-06-14
- [x] `instructions/` → чистая методология — 2026-06-14
- [x] 20 руководств в `guides/` — 2026-06-14
- [x] Шаблон исследования v4.0 — 2026-06-14
- [x] Словарь философем (35) — 2026-06-14
- [x] Словарь латинизмов (180+) — 2026-06-14
- [x] Веб-интерфейс v9.2 — подкатегории для всех категорий — 2026-06-14
- [x] 6 категорий контента в веб-интерфейсе — 2026-06-14
- [x] `learn-hebrew/` — 5 файлов — 2026-06-14
- [x] `bashah/` — 3 новых файла — 2026-06-14
- [x] `GUIDE-CODING.md` v2.0 — 2026-06-14
- [x] `CONTROL.md` v3.0 — 2026-06-14
- [x] `STRATEGY.md` v1.0 — 2026-06-14
- [x] `WEB-INTERFACE.md` v1.0 — 2026-06-14