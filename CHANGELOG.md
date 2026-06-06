# ИСТОРИЯ ИЗМЕНЕНИЙ

**Метаданные файла**
- **Файл:** `CHANGELOG.md`
- **Версия:** 2.1
- **Дата создания:** 2026-06-02
- **Последнее обновление:** 2026-06-06
- **Причина обновления:** Полная переработка хронологии, приведение к единой системе версий
- **Статус:** Активный
- **Тема:** Журнал всех значимых изменений в проекте «Голем»

---

## [2.0.0] - 2026-06-05

### СИСТЕМА ВЕРСИОНИРОВАНИЯ

- репозиторий переведён на `MAJOR.MINOR.PATCH`
- текущая версия: `2.0.0`
- структура: `2.0` (в `STRUCTURE.md`)
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
- `README.md` — инструкция

**ИНСТРУМЕНТЫ (tools/)**
- `menu.py` — единое CLI-меню
- `check-links.py` — проверка битых ссылок
- `find-duplicates.py` — поиск дубликатов
- `find-orphans.py` — поиск файлов-сирот
- `validate-metadata.py` — проверка метаданных
- `update-versions.py` — обновление версий
- `sync-structure.py` — синхронизация структуры
- `generate-glossary.py` — генерация глоссария
- `generate-nav.py` — генерация навигации
- `stats-report.py` — статистика
- `create-backup-scheduled.sh` — автоматический бэкап
- `agent/` — ИИ-агент (в разработке)

**ИДЕИ (ideas/)**
- `web-interface.md`
- `visualization-tool.md`
- `gamification.md`
- `database-schema.md`
- `search-engine.md`
- `api-design.md`

**ИНСТРУКЦИИ (instructions/)**
- `workflow.md` — рабочий процесс
- `coding-standards.md` — стандарты кода
- `collaboration-guide.md` — руководство для контрибьюторов
- `release-process.md` — выпуск версий
- `security-policy.md` — политика безопасности
- `troubleshooting.md` — устранение проблем
- `consistency-checker.md` — проверка согласованности
- `methodology/` — 5 методологических файлов

**ДАВАР (davar/)**
- `README.md` — документация языка
- `STRUCTURE.md` — структура папки
- `davar-architecture.md` — архитектура

**ТЕРМИНЫ (terminology/)**
- `ahava.md` — любовь

**ДОКУМЕНТАЦИЯ**
- `CONTRIBUTORS.md` — список участников
- `neural/docs/intro-course.md` — вводный курс по нейросетям

### ОБНОВЛЕНО

- `README.md` — версия 3.3
- `STRUCTURE.md` — версия 2.0, добавлены пояснения
- `.gitignore` — исключены модели и временные файлы

### ИСПРАВЛЕНО (2026-06-06)

- `religionims.md` → `religionisms.md` (опечатка в имени)
- обновлены ссылки на файл в `STRUCTURE.md`, `forbidden-words.md`, `chat-prompt.md`
- заголовок: «РЕЛИГИОНИЗМЫ» (через «з»)
- добавлены слова «запрет», «наказание» в `religionisms.md`
- примечание о римско-юридическом подтексте перенесено в метаданные

---

## [1.0.0] - 2026-05-28

### ДОБАВЛЕНО (ПЕРВЫЙ РЕЛИЗ)

- создан репозиторий «Голем»
- `instructions/` — 38 принципов, 23 метода, карты очищения, чекеры
- `terminology/` — 35+ терминов
- `researches/` — 25+ исследований
- `drafts/` — черновики
- `ideas/` — начальные идеи
- `tools/export-repo.sh`, `tools/backup.sh`
- `README.md` v1.0
- `STRUCTURE.md` v1.0
- `BACKLOG.md`, `CHANGELOG.md`, `DECISIONS.md`, `ROADMAP.md`, `TECHNICAL-DEBT.md`, `GLOSSARY.md`, `RETROSPECTIVE.md`

---

## СТАТУС ТЕКУЩЕЙ ВЕРСИИ

- **Релиз:** 2.0.0
- **Дата:** 2026-06-06
- **Состояние:** стабильный
- **Структура:** 2.0
- **Файлов:** 250+

---

## ПЛАНИРУЕМЫЕ ИЗМЕНЕНИЯ (2.1.0)

- добавить метаданные во все файлы (85%)
- создать `davar/examples/hello-world.dvr`
- реализовать `consistency-checker.py`
- собрать 1000+ записей для обучения нейросети

---

## ВЕРСИОНИРОВАНИЕ

- **Релизы репозитория:** `MAJOR.MINOR.PATCH` (в `CHANGELOG.md` и тегах Git)
- **Структура:** `MAJOR.MINOR` (в `STRUCTURE.md`)
- **Файлы:** `MAJOR.MINOR` (в метаданных)

---

הַדֶּרֶךְ יְהוָה — hа-Де́рех Яхве — Путь Яхве