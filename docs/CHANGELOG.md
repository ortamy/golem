# ИСТОРИЯ ИЗМЕНЕНИЙ

**Метаданные файла**
- **Файл:** `docs/CHANGELOG.md`
- **Версия:** 2.2
- **Дата создания:** 2026-06-02
- **Последнее обновление:** 2026-06-08
- **Причина обновления:** Перенос документации в docs/, добавлен раздел [3.0.0]
- **Статус:** Активный
- **Тема:** Журнал всех значимых изменений в проекте «Голем»
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Хеш:** eab5669a
- **Достоверность:** средняя
- **Последний аудит:** 2026-06-09
---

## [4.1.0] - 2026-06-09

### Проект

**Документация:**
- Создан `docs/CHECKERS-GUIDE.md` — полный справочник 19 чекеров
- Создан `docs/SCRIPTS-GUIDE.md` — справочник всех скриптов (40+)
- Создан `docs/ONBOARDING.md` — быстрое начало для новых участников
- Создан `docs/ARCHITECTURE.md` — архитектура проекта
- Создан `docs/FAQ.md` — частые вопросы
- Создан `docs/SETUP.md` — настройка рабочего окружения
- Создан `docs/GRAPH.md` — визуальная карта связей (Mermaid)
- Удалён `docs/CHANGELOG.md` — объединён с глобальным

**Exposure (разоблачение):**
- Создан `exposure-system-architecture.md` — архитектура системы: 9 компонентов, 4 этапа вербовки, 5 стадий жизни
- Создан `exposure-language-control.md` — язык как инструмент контроля
- Расширен `exposure-religionism-theory.md` — добавлены медицина, наука, военное дело, 7 этапов подмены
- Создан `exposure-techniques.md` — полный каталог 60+ приёмов подмены
- Обновлён `exposure-methods.md` — добавлены методы 24-29 (этимологическое разоблачение, юридическая археология, архитектурное разоблачение, исторический слой, проверка символа, финансовое разоблачение)
- Обновлён `exposure-mechanisms.md` — добавлены 2 новых механизма (подмена живого на структуру, подмена прощения на накопление)

**Исследования:**
- Создан `researches/history/alchemy.md` — алхимия как религионизм
- Создан `researches/economy/banks-and-financial-dynasties.md` — банки и финансовые династии
- Создан `researches/economy/mortgage-dead-pledge.md` — ипотека как мёртвый залог
- Создан `researches/tanakh/gog-and-magog.md` — Гог и Магог: проверка через ТаНаХ
- Создан `researches/language/heretic-meaning.md` — еретик: от «выбирающего» до «отступника»
- Создан `researches/tanakh/magen-david.md` — Маген Давид: щит, которого не было

**Метаданные:**
- Добавлены поля: Аудит, Язык, Ключевые слова, Связанные файлы, Хеш, Достоверность, Последний аудит, Проверок на религионизмы
- Связанные ссылки перенесены из тела файла в метаданные
- Добавлен авто-хеш содержимого для отслеживания изменений

### Инструменты

**Новые скрипты (9):**
- `check-exposure.py` — полная проверка по 10 категориям и 70+ маркерам
- `fix-encoding.py` — конвертация Windows-1251 в UTF-8
- `generate-graph.py` — генерация визуальной карты связей (Mermaid)
- `add-related-links.py` — автоматическое добавление перекрёстных ссылок
- `check-file-names-language.py` — проверка языка имён файлов (иврит/английский)
- `check-file-names-clarity.py` — проверка ясности и краткости имён
- `fill-empty-files.py` — заполнение пустых файлов шаблонами
- `sync-changelogs.py` — объединение глобального и локального CHANGELOG
- `fix-metadata-fields.py` — исправление искажённых названий полей

**Обновления скриптов:**
- `golem.py` v4.1 — авто-сканирование скриптов в подпапках, меню обновляется автоматически при добавлении новых скриптов
- `check-religionisms.py` v3.1 — белый список ивритских слов (100+), счётчик проверок в метаданных, защита метаданных от замен, фильтр «forbidden ≠ correct»
- `unify-metadata.py` v2.0 — 10 обязательных полей, хеш содержимого, авто-извлечение связанных файлов, адаптивные поля по категориям
- `sort-files.py` v4.5 — автоопределение ивритских имён, папка `tanakh/`, 300+ жёстких правил, архив для неопределённых

**Исправления:**
- Починен `check-religionisms.py` — больше нет ложных срабатываний на «Тора», «ТаНаХ», «Машиах»
- Починен `sync-structure.py` — убран `progress`, путь обновлён на `docs/STRUCTURE.md`
- Починен `generate-glossary.py` — убран `progress`, путь на `docs/GLOSSARY.md`
- Починен `generate-nav.py` — убран `progress`
- Удалён `docs/CHANGELOG.md` — дублировал глобальный

## [3.0.0] - 2026-06-08

### СТРУКТУРА

- документация перенесена из корня в `docs/`
- папка `tools/` реорганизована: `checkers/`, `generators/`, `reports/`, `automation/`, `backup/`, `lib/`, `cache/`
- `golem.py` обновлён до v3.5 — древовидное меню, анимация запуска, все пути исправлены

### ДОБАВЛЕНО

**ИНСТРУМЕНТЫ**
- `tools/checkers/check-religionisms.py` — поиск религионимов с мега-regex и многопоточностью
- `tools/checkers/check-code-quality.py` — проверка качества Python-кода
- `tools/checkers/clear-cache.py` — сброс всего кэша
- `tools/lib/utils.py` — общие утилиты (read_file_safe, progress_bar, print_header и др.)
- `tools/generators/generate-changelog.py` — генерация CHANGELOG из git-коммитов
- `tools/automation/move-to-docs.py` — перенос документации в docs/

### ИСПРАВЛЕНО

- `check-links.py` — починен UnicodeDecodeError, добавлен read_file_safe
- `find-orphans.py` — починен UnicodeDecodeError, добавлены исключения system_files
- все скрипты в подпапках — исправлен sys.path (parent → parent.parent)
- `golem.py` — убраны несуществующие скрипты, добавлены реальные пути
- удалён `SCTRUCTURE.md` (опечатка)
- удалён `substitution-of-the-name` без расширения .md
- `religionisms.md` — обновлён до 400+ слов

---

## [2.0.0] - 2026-06-05

### СИСТЕМА ВЕРСИОНИРОВАНИЯ

- репозиторий переведён на `MAJOR.MINOR.PATCH`
- текущая версия: `2.0.0`
- структура: `2.0` (в `docs/STRUCTURE.md`)
- метаданные файлов: `MAJOR.MINOR`

### ДОБАВЛЕНО

**НЕЙРОСЕТЬ (neural/)**
- полная инфраструктура для локальной модели Свидетеля
- `training-data/` — промпты, ответы, конфиг
- `models/download.sh` — скрипт скачивания
- `inference/` — сервер, клиент, Docker, конфиг
- `scripts/` — подготовка данных, обучение, квантизация
- `eval/` — бенчмарки и тесты
- `docs/` — архитектура, обучение, запуск, вводный курс

**ИНСТРУМЕНТЫ (tools/)**
- `golem.py` — единое CLI-меню
- `check-links.py` — проверка битых ссылок
- `find-duplicates.py` — поиск дубликатов
- `find-orphans.py` — поиск файлов-сирот
- `validate-metadata.py` — проверка метаданных
- `update-versions.py` — обновление версий
- `sync-structure.py` — синхронизация структуры
- `generate-glossary.py` — генерация глоссария
- `generate-nav.py` — генерация навигации
- `stats-report.py` — статистика

**ИДЕИ (ideas/)**
- `web-interface.md`, `visualization-tool.md`, `gamification.md`, `database-schema.md`, `search-engine.md`, `api-design.md`

**ИНСТРУКЦИИ (instructions/)**
- `workflow.md`, `coding-standards.md`, `collaboration-guide.md`, `release-process.md`, `security-policy.md`, `troubleshooting.md`
- `methodology/` — 5 методологических файлов

**ТЕРМИНЫ (terminology/)**
- `ahava.md` — любовь

### ИСПРАВЛЕНО (2026-06-06)

- `religionims.md` → `religionisms.md` (опечатка)
- обновлены ссылки в `STRUCTURE.md`, `forbidden-words.md`, `chat-prompt.md`

---

## [1.0.0] - 2026-05-28

### ДОБАВЛЕНО (ПЕРВЫЙ РЕЛИЗ)

- создан репозиторий «Голем»
- `instructions/` — 38 принципов, 23 метода, карты очищения, чекеры
- `terminology/` — 35+ терминов
- `researches/` — 25+ исследований
- `drafts/`, `ideas/`
- `tools/export-repo.sh`, `tools/backup.sh`
- `README.md` v1.0
- `docs/` — STRUCTURE, BACKLOG, CHANGELOG, DECISIONS, ROADMAP, TECHNICAL-DEBT, GLOSSARY, RETROSPECTIVE