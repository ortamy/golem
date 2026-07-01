# 📑 ИНДЕКС TOOLS

**Описание:** Индекс всех инструментов проекта «ГОЛЕМ»

---

## 📊 СТАТИСТИКА

- **Всего скриптов:** 40+
- **Папок:** 10
- **Последнее обновление:** 2026-07-01

---

## 🛠 ГЛАВНЫЕ СКРИПТЫ

- [golem.py](golem.py) - главное меню проекта
- [audit-content.py](audit-content.py) - аудит контента
- [fetch-sefaria.py](fetch-sefaria.py) - загрузка данных с Sefaria
- [interlinear-generator.py](interlinear-generator.py) - генератор интерлинеарного текста
- [replace_emoji_with_icons.py](replace_emoji_with_icons.py) - замена эмодзи на иконки
- [replace_h2_emoji.py](replace_h2_emoji.py) - замена эмодзи в заголовках

---

## ✅ CHECKERS (19+ скриптов)

### Проверка структуры
- [check-naming.py](checkers/check-naming.py) - проверка имён файлов
- [validate-metadata.py](checkers/validate-metadata.py) - валидация метаданных
- [check-links.py](checkers/check-links.py) - проверка ссылок
- [check-structure.py](checkers/check-structure.py) - проверка структуры

### Проверка контента
- [check-religionisms.py](checkers/check-religionisms.py) - проверка религионимов
- [check-tahor-sync.py](checkers/check-tahor-sync.py) - синхронизация тахора
- [check-exposure.py](checkers/check-exposure.py) - проверка разоблачений
- [check-consistency.py](checkers/check-consistency.py) - проверка консистентности
- [check-fact.py](checkers/check-fact.py) - проверка фактов
- [check-bdikah.py](checkers/check-bdikah.py) - проверка бдительности
- [check-mivdak.py](checkers/check-mivdak.py) - проверка мивдака
- [check-startup.py](checkers/check-startup.py) - проверка стартапа
- [check-tikun.py](checkers/check-tikun.py) - проверка тикуна

### Специальные проверки
- [check-hebrew.py](checkers/check-hebrew.py) - проверка иврита
- [check-translation.py](checkers/check-translation.py) - проверка переводов
- [check-metadata-json.py](checkers/check-metadata-json.py) - проверка JSON метаданных
- [check-duplicates.py](checkers/check-duplicates.py) - проверка дубликатов
- [check-empty-files.py](checkers/check-empty-files.py) - проверка пустых файлов
- [check-encoding.py](checkers/check-encoding.py) - проверка кодировки

---

## 🔨 GENERATORS (10+ скриптов)

### Генерация контента
- [generate-index.py](generators/generate-index.py) - генерация индексов
- [generate-stats.py](generators/generate-stats.py) - генерация статистики
- [generate-report.py](generators/generate-report.py) - генерация отчётов
- [generate-template.py](generators/generate-template.py) - генерация по шаблону

### Генерация данных
- [generate-tanakh-data.py](generators/generate-tanakh-data.py) - генерация данных Танаха
- [generate-hebrew-data.py](generators/generate-hebrew-data.py) - генерация ивритских данных
- [generate-terminology.py](generators/generate-terminology.py) - генерация терминологии

### Специальные генераторы
- [generate-interlinear.py](generators/generate-interlinear.py) - генерация интерлинеара
- [generate-search-index.py](generators/generate-search-index.py) - генерация поискового индекса
- [generate-sitemap.py](generators/generate-sitemap.py) - генерация карты сайта

---

## 📊 REPORTS (4+ скрипта)

- [generate-stats.py](reports/generate-stats.py) - общая статистика
- [generate-content-report.py](reports/generate-content-report.py) - отчёт по контенту
- [generate-audit-report.py](reports/generate-audit-report.py) - отчёт аудита
- [generate-coverage-report.py](reports/generate-coverage-report.py) - отчёт покрытия

---

## ⚡ AUTOMATION (5+ скриптов)

### Синхронизация
- [sync-structure.py](automation/sync-structure.py) - синхронизация структуры
- [sync-content.py](automation/sync-content.py) - синхронизация контента
- [sync-docs.py](automation/sync-docs.py) - синхронизация документации

### Автоматизация
- [auto-fix-metadata.py](automation/auto-fix-metadata.py) - автоисправление метаданных
- [auto-format.py](automation/auto-format.py) - автоформатирование
- [auto-link.py](automation/auto-link.py) - автогенерация ссылок

---

## 💾 BACKUP (2+ скрипта)

- [backup-content.py](backup/backup-content.py) - бэкап контента
- [backup-database.py](backup/backup-database.py) - бэкап базы данных
- [restore-backup.py](backup/restore-backup.py) - восстановление из бэкапа

---

## 📚 LIB (Общие утилиты)

### Утилиты
- [file-utils.py](lib/file-utils.py) - работа с файлами
- [string-utils.py](lib/string-utils.py) - работа со строками
- [json-utils.py](lib/json-utils.py) - работа с JSON
- [md-utils.py](lib/md-utils.py) - работа с Markdown
- [hebrew-utils.py](lib/hebrew-utils.py) - ивритские утилиты

### Парсеры
- [md-parser.py](lib/md-parser.py) - парсер Markdown
- [json-parser.py](lib/json-parser.py) - парсер JSON
- [yaml-parser.py](lib/yaml-parser.py) - парсер YAML

---

## 🔧 UTILS (Вспомогательные утилиты)

- [logger.py](utils/logger.py) - логирование
- [config.py](utils/config.py) - конфигурация
- [cache.py](utils/cache.py) - кэширование
- [validator.py](utils/validator.py) - валидация
- [formatter.py](utils/formatter.py) - форматирование

---

## 📊 DATA (Данные для инструментов)

### Конфигурации
- [golem-config.json](data/golem-config.json) - конфигурация Golem
- [paleo-map.json](data/paleo-map.json) - палео-карта
- [checkers-config.json](data/checkers-config.json) - конфигурация чекеров

### Шаблоны
- [metadata-template.json](data/metadata-template.json) - шаблон метаданных
- [report-template.json](data/report-template.json) - шаблон отчёта

---

## 🔄 SYNC (Синхронизация)

- [update-tanakh-cache.py](sync/update-tanakh-cache.py) - обновление кэша Танаха
- [sync-with-sefaria.py](sync/sync-with-sefaria.py) - синхронизация с Sefaria
- [sync-structure.py](sync/sync-structure.py) - синхронизация структуры
- [sync-docs.py](sync/sync-docs.py) - синхронизация документации

---

## 📝 КАТЕГОРИИ

### По типу
- **Проверки:** 19+ скриптов
- **Генераторы:** 10+ скриптов
- **Отчёты:** 4+ скрипта
- **Автоматизация:** 5+ скриптов
- **Бэкап:** 2+ скрипта
- **Утилиты:** 15+ модулей

### По назначению
- **Контент:** проверка и генерация контента
- **Структура:** проверка и синхронизация структуры
- **Данные:** работа с данными
- **Документация:** генерация документации
- **Автоматизация:** автоматизация процессов

---

## 🔗 НАВИГАЦИЯ

- [README.md](../README.md) - главная страница
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - архитектура проекта
- [docs/STRUCTURE.md](../docs/STRUCTURE.md) - полная структура

### По категориям
- [checkers/](checkers/) - скрипты проверок
- [generators/](generators/) - генераторы файлов
- [reports/](reports/) - генераторы отчётов
- [automation/](automation/) - автоматизация
- [backup/](backup/) - бэкап
- [lib/](lib/) - общие утилиты
- [utils/](utils/) - вспомогательные утилиты
- [data/](data/) - данные
- [sync/](sync/) - синхронизация

---

## 🛠 ИСПОЛЬЗОВАНИЕ

### Главное меню
```bash
python tools/golem.py
```

### Отдельные скрипты
```bash
# Проверки
python tools/checkers/check-naming.py
python tools/checkers/validate-metadata.py
python tools/checkers/check-religionisms.py

# Генерация
python tools/generators/generate-index.py
python tools/generators/generate-stats.py

# Автоматизация
python tools/automation/sync-structure.py
python tools/automation/auto-fix-metadata.py
```

---

## 📝 ПРИМЕЧАНИЯ

1. **Автоматическое обнаружение:** новые скрипты автоматически появляются в меню
2. **Стандарты:** все скрипты следуют единым стандартам
3. **Документация:** каждый скрипт имеет docstring
4. **Тестирование:** тесты в папке tests/ рядом со скриптом