# 💻 СТАНДАРТЫ КОДА (CODING STANDARDS)

**Метаданные файла**
- **Файл:** `instructions/CODING-STANDARDS.md`
- **Версия:** 1.1
- **Дата создания:** 2026-06-05
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Актуализирована структура tools/, исправлены имена файлов
- **Статус:** Активный
- **Тема:** Стандарты оформления кода для инструментов и языка Давар
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `instructions/coding-standards.md`, `instructions/exposure/exposure-language.md`, `instructions/exposure/exposure-methods.md`, `instructions/exposure/exposure-system-architecture.md`, `instructions/tahor/names.md`
- **Хеш:** ожидает
- **Достоверность:** средняя
- **Последний аудит:** 2026-06-11

---

## 🔥 ВВЕДЕНИЕ

Этот документ описывает стандарты написания кода для:
- Python-инструментов в папке `tools/`
- Bash-скриптов в папке `tools/`
- Языка программирования Давар (`davar/`)

Все участники следуют этим стандартам для обеспечения читаемости и согласованности.

---

## 🐍 PYTHON СТАНДАРТЫ

### ОБЩИЕ ПРАВИЛА

- версия Python: 3.6 и выше
- кодировка: UTF-8
- отступы: 4 пробела (не табуляция)
- максимальная длина строки: 79 символов
- пустая строка в конце файла

### ЗАГОЛОВОК ФАЙЛА

```python
#!/usr/bin/env python3
# имя-файла.py — краткое описание

import sys
import os
```

### ИМЕНОВАНИЕ

- переменные: `snake_case`
- функции: `snake_case`
- константы: `UPPER_SNAKE_CASE`
- классы: `PascalCase`
- приватные методы: `_leading_underscore`

### ФУНКЦИИ

```python
def calculate_checksum(data: str, algorithm: str = "md5") -> str:
    """Вычисляет контрольную сумму.

    Аргументы:
        data: входная строка
        algorithm: алгоритм хеширования (md5, sha1, sha256)

    Возвращает:
        хеш-строку в нижнем регистре
    """
    pass
```

### ОБРАБОТКА ОШИБОК

```python
try:
    result = risky_operation()
except ValueError as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)
```

### ВЫВОД

- ошибки: `❌ Текст ошибки`
- предупреждения: `⚠️ Текст предупреждения`
- успех: `✅ Текст успеха`
- информация: `📊 Текст информации`

---

## 📜 BASH СТАНДАРТЫ

### ОБЩИЕ ПРАВИЛА

- первая строка: `#!/bin/bash`
- отступы: 2 пробела
- кавычки: двойные для переменных
- проверка ошибок после каждой важной команды

### ЗАГОЛОВОК ФАЙЛА

```bash
#!/bin/bash
# имя-файла.sh — краткое описание

set -e  # выход при ошибке
set -u  # ошибка при неопределённой переменной
```

### ПЕРЕМЕННЫЕ

```bash
# правильно
VAR_NAME="значение"
local var_name="значение"

# неправильно
VAR_NAME=значение
```

### ФУНКЦИИ

```bash
function do_something() {
    local param1="$1"
    echo "Processing: $param1"
}
```

### ПРОВЕРКА ОШИБОК

```bash
if ! command; then
    echo "❌ Ошибка выполнения команды"
    exit 1
fi
```

---

## 🎯 DAVAR СТАНДАРТЫ (ПЛАНИРУЕМЫЕ)

### ОБЩИЕ ПРАВИЛА

- расширение файла: `.dvr`
- кодировка: UTF-8
- отступы: 4 пробела
- комментарии: `//` для строки

### ИМЕНОВАНИЕ

- переменные: `lowercase` (без пробелов)
- функции: `actionName()` (верблюжий регистр)
- константы: `UPPERCASE`

### ПРИМЕР (КОНЦЕПЦИЯ)

```
// программа на Даваре
определить имя = "Исраэль"
действие приветствие(имя) {
    вернуть "Мир тебе, " + имя
}

вызвать приветствие(имя)
```

---

## 🛠️ СТРУКТУРА ПРОЕКТА

```
tools/
├── golem.py                    # главный CLI-интерфейс
├── checkers/                   # префикс: check-
│   ├── check-code-quality.py
│   ├── check-consistency.py
│   ├── check-duplicates.py
│   ├── check-empty-files.py
│   ├── check-env.py
│   ├── check-exposure.py
│   ├── check-external-links.py
│   ├── check-fix-encoding.py
│   ├── check-fix-metadata.py
│   ├── check-fix-transliteration.py
│   ├── check-links.py
│   ├── check-metadata-paths.py
│   ├── check-names-clarity.py
│   ├── check-names-language.py
│   ├── check-naming.py
│   ├── check-orphans.py
│   ├── check-religionisms.py
│   ├── check-sizes.py
│   ├── check-sort-files.py
│   ├── check-tahor-sync.py
│   ├── check-tanakh-references.py
│   └── check-validate-metadata.py
├── generators/                 # префикс: generate-
│   ├── generate-book.py
│   ├── generate-changelog.py
│   ├── generate-exposure-suggestions.py
│   ├── generate-files-json.py
│   ├── generate-fill-empty.py
│   ├── generate-glossary.py
│   ├── generate-graph.py
│   ├── generate-index.py
│   ├── generate-metadata.py
│   ├── generate-nav.py
│   ├── generate-related-links.py
│   ├── generate-retrospective.py
│   ├── generate-training-data.py
│   └── generate-web.py
├── reports/                    # префикс: report-
│   ├── report-daily.py
│   ├── report-dashboard.py
│   ├── report-health.py
│   └── report-stats.py
├── automation/                 # префикс: auto-
│   ├── auto-add-metadata.py
│   ├── auto-clear-cache.py
│   ├── auto-doc.py
│   ├── auto-fix.py
│   ├── auto-ideas.py
│   ├── auto-tasks.py
│   └── auto-versions.py
├── sync/                       # префикс: sync-
│   ├── sync-changelogs.py
│   └── sync-structure.py
├── utils/                      # утилиты
│   ├── code-injector.py
│   ├── rename-script.py
│   └── search.py
├── backup/                     # бэкапы
│   ├── backup.sh
│   ├── create-backup-scheduled.sh
│   └── export-repo.sh
├── lib/                        # библиотеки
│   ├── ui.py
│   └── utils.py
└── cache/                      # кэши
    ├── dirty-files.json
    ├── golem-config.json
    ├── religionisms-cache.json
    ├── scan-cache.json
    ├── tanakh.json
    └── neural-cache/

ed-agent/                       # ИИ-агент «Эд»
├── agent.py
├── memory.py
├── tools.py
├── config.yml
└── README.md

ed-neural/                      # нейросеть «Эд»
├── README.md
├── docs/
├── eval/
├── inference/
├── models/
├── scripts/
└── training-data/

davar/                          # язык Давар
├── davar-architecture.md
├── davar-language.md
├── README.md
├── STRUCTURE.md
└── examples/
```

---

## ✅ ЧЕК-ЛИСТ ПЕРЕД КОММИТОМ

**PYTHON**
- [ ] работает на Python 3.6+
- [ ] отступы — 4 пробела
- [ ] есть docstring у функций
- [ ] переменные названы snake_case
- [ ] нет лишних импортов

**BASH**
- [ ] есть `set -e` или `set -u`
- [ ] переменные в кавычках
- [ ] проверка ошибок
- [ ] права на выполнение (`chmod +x`)

---

## 🚫 ЗАПРЕЩЕНО

- использовать `eval()` (Python)
- использовать без кавычек переменные (Bash)
- хардкодить пути без `Path(__file__).parent`
- писать функции длиннее 50 строк
- использовать `;` для объединения команд без необходимости

---

## 📋 РЕКОМЕНДАЦИИ

- используй `argparse` для CLI-аргументов
- используй `pathlib` для работы с путями
- добавляй `--dry-run` для опасных операций
- выноси повторяющийся код в функции
- пиши осмысленные имена переменных

---

## 🔄 ОБНОВЛЕНИЕ СТАНДАРТОВ

Предложения по изменению стандартов — через `ideas/`.