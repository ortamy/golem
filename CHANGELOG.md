# 📜 CHANGELOG: ЖУРНАЛ ИЗМЕНЕНИЙ

**Метаданные файла**
- **Файл:** `CHANGELOG.md`
- **Версия:** 2.0
- **Дата создания:** 2026-06-02
- **Последнее обновление:** 2026-06-05
- **Причина обновления:** Объединение с новыми изменениями (нейросеть, инструменты, идеи)
- **Статус:** Активный
- **Тема:** Журнал всех значимых изменений в проекте «Голем». Что создано, обновлено, изменено. От начала до сегодня.

---

## 2026-06-05 — НЕЙРОСЕТЬ, ИНСТРУМЕНТЫ, РЕСТРУКТУРИЗАЦИЯ

### ДОБАВЛЕНО

**НЕЙРОСЕТЬ (neural/)**
- `neural/` — папка для локальной модели Свидетеля
- `neural/training-data/prompts.json` — коллекция промптов для обучения
- `neural/training-data/responses.json` — ожидаемые ответы
- `neural/training-data/config.json` — параметры обучения
- `neural/models/download.sh` — скрипт скачивания модели
- `neural/inference/server.py` — сервер для инференса
- `neural/inference/client.py` — клиент для API
- `neural/inference/requirements.txt` — зависимости Python
- `neural/inference/Dockerfile` — контейнеризация
- `neural/inference/config.yml` — настройки сервера
- `neural/scripts/prepare_data.py` — подготовка данных из репозитория
- `neural/scripts/train.py` — обучение модели
- `neural/scripts/quantize.py` — квантизация в GGUF
- `neural/eval/benchmark.py` — тесты скорости и точности
- `neural/eval/test_responses.json` — тестовые промпты
- `neural/docs/architecture.md` — архитектура нейросети
- `neural/docs/training-guide.md` — инструкция по обучению
- `neural/docs/inference-guide.md` — инструкция по запуску
- `neural/README.md` — общая инструкция

**НОВЫЕ ИНСТРУМЕНТЫ (tools/)**
- `tools/menu.py` — единое CLI-меню для всех инструментов
- `tools/check-links.py` — проверка битых ссылок
- `tools/find-duplicates.py` — поиск дубликатов
- `tools/find-orphans.py` — поиск файлов-сирот
- `tools/validate-metadata.py` — проверка корректности метаданных
- `tools/update-versions.py` — обновление версий и дат
- `tools/sync-structure.py` — синхронизация structure.md с файловой системой
- `tools/generate-glossary.py` — генерация GLOSSARY.md
- `tools/generate-nav.py` — генерация навигации для README
- `tools/stats-report.py` — статистика по репозиторию
- `tools/create-backup-scheduled.sh` — автоматический бэкап (cron)
- `tools/agent/` — папка для ИИ-агента (в разработке)

**НОВЫЕ ИДЕИ (ideas/)**
- `ideas/web-interface.md` — веб-интерфейс
- `ideas/visualization-tool.md` — визуализация связей
- `ideas/gamification.md` — геймификация обучения
- `ideas/database-schema.md` — схема базы данных
- `ideas/search-engine.md` — поисковый движок
- `ideas/api-design.md` — дизайн REST API

**НОВЫЕ ИНСТРУКЦИИ (instructions/)**
- `instructions/workflow.md` — рабочий процесс
- `instructions/coding-standards.md` — стандарты кода
- `instructions/collaboration-guide.md` — руководство для контрибьюторов
- `instructions/release-process.md` — процесс выпуска версий
- `instructions/security-policy.md` — политика безопасности
- `instructions/troubleshooting.md` — устранение проблем

**НОВЫЕ ЧЕКЕРЫ (instructions/checkers/)**
- `instructions/checkers/consistency-checker.md` — проверка согласованности

**НОВЫЕ ТЕРМИНЫ (terminology/)**
- `terminology/ahava.md` — любовь

**ДОКУМЕНТАЦИЯ**
- `CONTRIBUTORS.md` — список участников проекта
- `neural/docs/` — три руководства по нейросети

### ОБНОВЛЕНО

- `README.md` — версия 3.3, полная реструктуризация, убрана дублирующая структура
- `structure.md` — версия 2.3, добавлены пояснения для всех файлов, добавлена папка neural/
- `.gitignore` — добавлены исключения для neural/models/*.gguf и training-data/raw/
- `CHANGELOG.md` — версия 2.0, объединение с историей от 2026-06-02

### ИСПРАВЛЕНО

- `research-princilples.md` → `research-principles.md`
- `SCTRUCTURE.md` → `STRUCTURE.md`
- `substitution-of-the-name` → `substitution-of-the-name.md`

### ТЕХНИЧЕСКИЙ ДОЛГ (НЕ ЗАКРЫТО)

- создать папку `instructions/methodology/` и перенести методологические файлы
- перенести `neural-network-plan.md` из `instructions/` в `ideas/`
- перенести содержимое `drafts/davar-language.md` в `davar/`
- добавить метаданные в 85% файлов
- создать `davar/README.md`

---

## 2026-06-02 — ОЧИЩЕНИЕ И МАСШТАБИРОВАНИЕ

### ДОБАВЛЕНО

- папка `instructions/tahor/` с 6 файлами: religionims, grecisms, slavicisms, latinisms, names, phrases
- `instructions/retrospective.md` — инструкция по ретроспективам
- папка `src/retrospectives/`
- исследования: `allopathy.md`, `microplastics.md`, `g-generations.md`, `pyramid-bunker.md`, `slavs.md`, `new-year.md`, `gerewol.md`
- книги: `machiavelli-the-prince.md`, `kissinger-world-order.md`
- термины: `shmitah.md`

### ОБНОВЛЕНО

- `forbidden-words.md` до v2.0 — индекс с ссылками
- `research-principles.md` до v2.2 (+принципы 33–38)
- `chat-prompt.md` до v1.9 (+маркировка фактов, +фактчек)
- `exposure-methods.md` до v1.2 (+методы 19–20)
- `structure.md` до v1.3
- `README.md` до v3.1

### ИЗМЕНЕНО

- исследования разделены на 7 подпапок: systems, history, tanakh, books, culture, practice, other
- `russia-third-rome.md` → `russia-empire.md`
- `drevo-yazykov.md` → `language-tree.md`

### УДАЛЕНО

- дублирующиеся чекеры
- старый `exposure-principles.md`

---

## 2026-06-01 — СИСТЕМАТИЗАЦИЯ

### ДОБАВЛЕНО

- папка `instructions/exposure/` — разделение principles, methods, mechanisms, distortions
- папка `checkers/`
- `checkers/mivdak.md` — полный цикл аудита
- `checkers/tikun-fix.md` — шаблон задач по обновлению
- `checkers/factcheck.md` — проверка фактов
- `drafts/technical-debt.md`
- `drafts/platform-idea.md`

### ОБНОВЛЕНО

- `exposure-methods.md` до v1.1 (+3 метода)
- `exposure-mechanisms.md` до v1.2 (+дуализация, комбинации, remedies)
- `chat-prompt.md` до v1.5
- `forbidden-words.md` до v1.2
- `cherut.md` до v2.0 — свобода для верности

### СОЗДАНО

- `exposure-distortions.md` v1.0

---

## 2026-05-30 — ИСТОРИИ И РАЗОБЛАЧЕНИЯ

### ДОБАВЛЕНО

- истории: `history-of-banks.md`, `history-of-religion.md`, `history-of-medicine.md`, `history-of-politics.md`, `history-of-economy.md`, `history-of-school.md`, `history-of-prison.md`, `history-of-languages.md`
- `terminology/avar-atid.md` — время в иврите
- `researches/russia-empire.md` — Россия как Третий Рим
- примеры Давара: `davar/examples/01-social-network.md`

---

## 2026-05-29 — РАСШИРЕНИЕ

### ДОБАВЛЕНО (ТЕРМИНЫ)

`golem.md`, `mene-tekel.md`, `shlem-avon.md`, `nefilim.md`, `gibor.md`, `pachad.md`, `erech-apayim.md`, `yetzer-lev.md`, `shabbat.md`, `tohu-va-vohu.md`, `elilim.md`, `tefilah.md`, `davar.md`, `mishkan.md`, `asur.md`, `karet.md`

### ДОБАВЛЕНО (ИССЛЕДОВАНИЯ)

`purpose-of-tanakh.md`, `talmud-judaism.md`, `karaism.md`, `red-mitzraim.md`, `ha-mashchit.md`, `yehoshua-research.md`, `vatican.md`, `minecraft-tanakh.md`, `derech-ha-gever.md`, `derech-ha-nachash.md`

---

## 2026-05-28 — ФУНДАМЕНТ

### ДОБАВЛЕНО (ИНСТРУКЦИИ)

`tree-method.md`, `forbidden-words.md`, `research-template.md`, `self-learning-template.md`, `neural-network-plan.md`, `archeology-methodology.md`, `translation-methodology.md`, `templates/concept-analysis-template.md`

### ДОБАВЛЕНО (ТЕРМИНЫ — ПЕРВЫЕ)

`immanu-el.md`, `etz-ha-daat.md`, `yir-at-yhwh.md`, `ktav-ivri.md`, `cherut.md`, `shekel.md`, `bavel.md`, `ivri.md`, `naaf.md`, `beit-ha-mikdash.md`, `neshamah.md`, `lashon-ha-kodesh.md`, `arur.md`, `olam.md`

### ДОБАВЛЕНО (ИССЛЕДОВАНИЯ — ПЕРВЫЕ)

`mitzraim-system.md`, `morashat-israel.md`

### ДОБАВЛЕНО (ДАВАР)

`davar/` с README, manifest, structure, roadmap, spec/grammar.md, spec/types.md, spec/semantics.md, spec/limits.md, spec/shabbat.md, spec/growth.md

### ДОБАВЛЕНО (ЧЕРНОВИКИ)

`drafts/ideas.md`, `drafts/questions.md`, `drafts/notes.md`, `drafts/optimization-log.md`

### ОСНОВНЫЕ ФАЙЛЫ

`README.md` v1.0, `structure.md` v1.0

---

## 2026-05-27 — ЗАПУСК ПРОЕКТА

### СОЗДАНО (ПЕРВЫЕ ФАЙЛЫ)

- `chat-prompt.md` v1.0 — первый промпт для нейросети
- `check-log-template.md` — шаблон лога проверки
- `useful-log-template.md` — шаблон лога полезности
- `exposure-principles.md` v1.0 — принципы разоблачения
- `manifest.md` v1.0 — манифест восстановления
- `research-principles.md` v1.0 — принципы исследований
- `transliteration-distortions.md` — транслитерации
- `image-map-template.md` — шаблон карты образов

---

## 🚀 ПЛАНИРУЕМЫЕ ИЗМЕНЕНИЯ (ВЕРСИЯ 2.1)

- создать папку `instructions/methodology/` и перенести методологические файлы
- перенести `neural-network-plan.md` из `instructions/` в `ideas/`
- перенести содержимое `drafts/davar-language.md` в `davar/`
- добавить метаданные во все файлы
- создать `davar/README.md`
- создать `davar/examples/hello-world.dvr`

---

## 🔄 ВЕРСИОНИРОВАНИЕ

Формат: `MAJOR.MINOR`

- MAJOR — большие изменения, пересмотр структуры
- MINOR — добавление файлов, исправления, обновления

Релизы репозитория: `MAJOR.MINOR.PATCH` (теги Git)

---

## 🛡️ ВОЗВРАЩЕНИЕ

Каждое изменение — шаг вперёд к истине.

История показывает путь. Путь продолжается.

---

הַדֶּרֶךְ יְהוָה — hа-Де́рех Яхве — Путь Яхве
