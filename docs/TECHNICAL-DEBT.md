# 📋 ТЕХНИЧЕСКИЙ ДОЛГ

**Метаданные файла**
- **Файл:** `docs/TECHNICAL-DEBT.md`
- **Версия:** 2.2
- **Дата создания:** 2026-05-28
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Добавлены задачи по наполнению новых категорий контентом
- **Статус:** Активный
- **Тема:** Технический долг и задачи по развитию проекта
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `docs/TECHNICAL-DEBT.md`, `docs/IDEAS.md`, `docs/ROADMAP.md`
- **Хеш:** ожидает
- **Достоверность:** средняя
- **Последний аудит:** 2026-06-11

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

### БаШаХ — перенести из researches/tanakh/

- [ ] `brit-hadashah.md` → `content/bashah/concepts/brit-hadashah.md`
- [ ] `drashat-hahar.md` → `content/bashah/teachings/drashat-hahar.md`
- [ ] `tfilat-yeshua.md` → `content/bashah/teachings/tfilat-yeshua.md`
- [ ] `sifrei-bashakh.md` → `content/bashah/books/sifrei-bashah.md`
- [ ] `psychikos-pneumatikos.md` → `content/bashah/concepts/psychikos-pneumatikos.md`
- [ ] `nicham-keifa.md` → `content/bashah/persons/nicham-keifa.md`
- [ ] `shaul-victim.md` → `content/bashah/persons/shaul.md`

### БаШаХ — создать новые

- [x] `content/bashah/concepts/besorah.md` ✅
- [x] `content/bashah/concepts/kehillah.md` ✅
- [x] `content/bashah/persons/keifa.md` ✅
- [ ] `content/bashah/persons/yohanan-matbil.md` — Йоханан Погружатель
- [ ] `content/bashah/events/seudat-aharon.md` — Последняя трапеза
- [ ] `content/bashah/events/shavuot-ruach.md` — Шавуот — дарование Дыхания
- [ ] `content/bashah/events/tvilat-yeshua.md` — Погружение Йешуа
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

## ✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ (2026-06-11)

- [x] Реорганизация архитектуры: `content/`, `ed/`, `guides/`, `dictionaries/`
- [x] Переименование всех скриптов с префиксами
- [x] `tahor/` → `dictionaries/`
- [x] `philosophemes.md` → `exposure/`
- [x] `drafts/` → `backlog/`
- [x] `instructions/` → чистая методология
- [x] 20 руководств в `guides/`
- [x] Шаблон исследования v4.0
- [x] Словарь философем (35)
- [x] Словарь латинизмов (180+)
- [x] Веб-интерфейс v9.2 — подкатегории для всех категорий
- [x] 6 категорий контента в веб-интерфейсе
- [x] `learn-hebrew/` — 5 файлов
- [x] `bashah/` — 3 новых файла
- [x] `GUIDE-CODING.md` v2.0
- [x] `CONTROL.md` v3.0
- [x] `STRATEGY.md` v1.0
- [x] `WEB-INTERFACE.md` v1.0