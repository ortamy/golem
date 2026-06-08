# ИСТОРИЯ ИЗМЕНЕНИЙ

**Метаданные файла**
- **Файл:** `docs/CHANGELOG.md`
- **Версия:** 2.2
- **Дата создания:** 2026-06-02
- **Последнее обновление:** 2026-06-08
- **Причина обновления:** Перенос документации в docs/, добавлен раздел [3.0.0]
- **Статус:** Активный
- **Тема:** Журнал всех значимых изменений в проекте «Голем»

---

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

---

## СТАТУС ТЕКУЩЕЙ ВЕРСИИ

- **Релиз:** 3.0.0
- **Дата:** 2026-06-08
- **Состояние:** стабильный
- **Файлов:** 320+

---

## ВЕРСИОНИРОВАНИЕ

- **Релизы репозитория:** `MAJOR.MINOR.PATCH` (в `docs/CHANGELOG.md` и тегах Git)
- **Структура:** `MAJOR.MINOR` (в `docs/STRUCTURE.md`)
- **Файлы:** `MAJOR.MINOR` (в метаданных)

---

הַדֶּרֶךְ יְהוָה — hа-Де́рех Яхве — Путь Яхве