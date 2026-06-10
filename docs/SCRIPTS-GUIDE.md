# 🛠 СПРАВОЧНИК ПО СКРИПТАМ — SCRIPTS GUIDE

**Метаданные файла**
- **Файл:** `docs/SCRIPTS-GUIDE.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-09
- **Последнее обновление:** 2026-06-09
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Полный справочник по всем скриптам проекта «Голем»

---

## 🔥 ВВЕДЕНИЕ

Все скрипты находятся в `tools/` и разбиты по категориям:

- `checkers/` — проверки
- `generators/` — генерация файлов
- `reports/` — отчёты и статистика
- `automation/` — автоматизация
- `backup/` — бэкап и экспорт
- `lib/` — общие утилиты (не для запуска)
- `cache/` — кэш (автоматическое)

Главное меню: `tools/golem.py`.

---

## 🧭 ГЛАВНОЕ МЕНЮ

**Файл:** `tools/golem.py`

Древовидное меню для управления проектом. Автоматически находит все скрипты в подпапках.

**Запуск:**
```bash
cd tools
python golem.py
```

**Управление:** стрелки ↑↓ — выбор, Enter — вход, Esc — назад, q — выход.

---

## 🔍 ЧЕКЕРЫ (`tools/checkers/`)

### `check-naming.py`
Проверка имён md-файлов: латиница, дефисы, без русских букв.
```bash
python tools/checkers/check-naming.py
```

### `validate-metadata.py`
Проверка блока метаданных: наличие, формат, корректность.
```bash
python tools/checkers/validate-metadata.py
python tools/checkers/validate-metadata.py --fix
```

### `fix-metadata-fields.py`
Исправление искажённых названий полей (`hитхадшут` → `Последнее обновление`).
```bash
python tools/checkers/fix-metadata-fields.py
python tools/checkers/fix-metadata-fields.py --fix
```

### `check-metadata-consistency.py`
Сверка поля «Файл:» с реальным путём.
```bash
python tools/checkers/check-metadata-consistency.py
python tools/checkers/check-metadata-consistency.py --fix
```

### `check-links.py`
Проверка внутренних ссылок `[текст](docs/INDEX.md)`.
```bash
python tools/checkers/check-links.py
```

### `validate-external-links.py`
Проверка HTTP(S) ссылок на доступность.
```bash
python tools/checkers/validate-external-links.py
```

### `find-duplicates.py`
Поиск дубликатов по схожести содержимого (>85%).
```bash
python tools/checkers/find-duplicates.py
```

### `find-orphans.py`
Поиск файлов без входящих ссылок.
```bash
python tools/checkers/find-orphans.py
```

### `check-empty-files.py`
Поиск пустых файлов и файлов с TODO/FIXME.
```bash
python tools/checkers/check-empty-files.py
```

### `consistency-checker.py`
Проверка транслитерации, ссылок и путей в метаданных.
```bash
python tools/checkers/consistency-checker.py
```

### `check-religionisms.py`
Поиск и замена религионимов («Бог»→«Элоhим», «грех»→«промах»).
```bash
python tools/checkers/check-religionisms.py
python tools/checkers/check-religionisms.py --fix
python tools/checkers/check-religionisms.py --rebuild --fix
```

### `check-tahor-sync.py`
Сверка словарей `tahor/` с `forbidden-words.md`.
```bash
python tools/checkers/check-tahor-sync.py
```

### `check-code-quality.py`
Проверка Python-кода: импорты, docstring, длина строк.
```bash
python tools/checkers/check-code-quality.py
python tools/checkers/check-code-quality.py --fix
```

### `check-file-names-language.py`
Проверка языка имени файла (иврит для `tanakh/`, английский для остальных).
```bash
python tools/checkers/check-file-names-language.py
```

### `check-file-names-clarity.py`
Проверка краткости и понятности имён.
```bash
python tools/checkers/check-file-names-clarity.py
python tools/checkers/check-file-names-clarity.py --fix
```

### `check-file-sizes.py`
Анализ размеров файлов (в `tools/reports/`).
```bash
python tools/reports/check-file-sizes.py
```

### `check-exposure.py`
Полная проверка по 10 категориям искажений (70+ маркеров).
```bash
python tools/checkers/check-exposure.py
```

### `fix-encoding.py`
Конвертация Windows-1251 → UTF-8.
```bash
python tools/checkers/fix-encoding.py
```

### `clear-cache.py`
Очистка кэша.
```bash
python tools/checkers/clear-cache.py
```

---

## 📦 ГЕНЕРАТОРЫ (`tools/generators/`)

### `generate-glossary.py`
Генерация глоссария из `terminology/`.
```bash
python tools/generators/generate-glossary.py
```

### `generate-nav.py`
Генерация навигации для README.md.
```bash
python tools/generators/generate-nav.py
```

### `sync-structure.py`
Синхронизация STRUCTURE.md с реальной структурой папок.
```bash
python tools/generators/sync-structure.py
```

### `generate-retrospective.py`
Генерация ретроспективы на основе git-лога.
```bash
python tools/generators/generate-retrospective.py
```

### `generate-changelog.py`
Генерация CHANGELOG из git-коммитов.
```bash
python tools/generators/generate-changelog.py 2.1.0
```

### `generate-index.py`
Генерация индекса всех файлов по папкам.
```bash
python tools/generators/generate-index.py
```

### `unify-metadata.py`
Унификация метаданных — приведение к единому шаблону.
```bash
python tools/generators/unify-metadata.py
python tools/generators/unify-metadata.py --fix
python tools/generators/unify-metadata.py --add
```

### `fill-empty-files.py`
Заполнение пустых файлов шаблонами.
```bash
python tools/generators/fill-empty-files.py
```

### `add-related-links.py`
Автоматическое добавление перекрёстных ссылок.
```bash
python tools/generators/add-related-links.py
python tools/generators/add-related-links.py --dry-run
```

### `sync-changelogs.py`
Объединение глобального и локального CHANGELOG.
```bash
python tools/generators/sync-changelogs.py
```

---

## 📊 ОТЧЁТЫ (`tools/reports/`)

### `stats-report.py`
Полная статистика репозитория: файлы, строки, метаданные.
```bash
python tools/reports/stats-report.py
```

### `daily-report.py`
Ежедневный отчёт.
```bash
python tools/reports/daily-report.py
```

### `check-health.py`
Проверка здоровья проекта.
```bash
python tools/reports/check-health.py
```

### `check-file-sizes.py`
Анализ размеров файлов.
```bash
python tools/reports/check-file-sizes.py
```

---

## 🤖 АВТОМАТИЗАЦИЯ (`tools/automation/`)

### `add-metadata.py`
Добавление метаданных в файлы без них.
```bash
python tools/automation/add-metadata.py
```

### `auto-fix.py`
Автоматическое исправление задач из TECH-DEBT.
```bash
python tools/automation/auto-fix.py
```

### `task-manager.py`
Управление задачами из TECH-DEBT.md.
```bash
python tools/automation/task-manager.py
```

### `idea-manager.py`
Управление идеями из `ideas/`.
```bash
python tools/automation/idea-manager.py
```

### `update-versions.py`
Обновление версий во всех файлах.
```bash
python tools/automation/update-versions.py --dry-run
python tools/automation/update-versions.py --type minor
```

### `sort-files.py`
Автоматическая сортировка файлов по категориям.
```bash
python tools/automation/sort-files.py --dry-run
python tools/automation/sort-files.py
python tools/automation/sort-files.py --force
```

---

## 💾 БЭКАП (`tools/backup/`)

### `backup.sh`
Создание бэкапа репозитория.
```bash
bash tools/backup/backup.sh
```

### `export-repo.sh`
Экспорт репозитория без временных файлов.
```bash
bash tools/backup/export-repo.sh
```

### `create-backup-scheduled.sh`
Автоматический бэкап по расписанию.
```bash
bash tools/backup/create-backup-scheduled.sh
```

---

## 📚 БИБЛИОТЕКА (`tools/lib/`)

### `utils.py`
Общие утилиты: `read_file_safe`, `progress_bar`, `print_header`, `print_success`, `ask_yes_no`.

**Не для запуска напрямую.** Импортируется всеми скриптами.

---

## 🔄 ТИПОВЫЕ ЦЕПОЧКИ

### Добавление нового исследования
```bash
# 1. Создать файл в researches/
# 2. Добавить метаданные
python tools/generators/unify-metadata.py --fix

# 3. Проверить религионимы
python tools/checkers/check-religionisms.py --fix

# 4. Проверить ссылки
python tools/checkers/check-links.py
```

### Полный аудит
```bash
python tools/golem.py
# ДЕЙСТВИЯ → Запустить все проверки
```

### Исправление после обновления словарей
```bash
python tools/checkers/check-tahor-sync.py
python tools/checkers/clear-cache.py
python tools/checkers/check-religionisms.py --rebuild --fix
```

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ
- `docs/CHECKERS-GUIDE.md` — подробный справочник чекеров
- `docs/ONBOARDING.md` — быстрое начало
- `tools/` — все скрипты

---

> **עֵד (Эд) — Свидетель.**
> Каждый скрипт — инструмент. Знай свои инструменты.