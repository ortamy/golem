# 💉 CODE INJECTOR — РУКОВОДСТВО

**Метаданные файла**
- **Файл:** `instructions/tools/code-injector.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-11
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Руководство по использованию Code Injector — инструмента для программного редактирования кода
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `instructions/tools/code-injector.md`, `tools/code-injector.py`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-11

---

## 🔥 ЧТО ТАКОЕ CODE INJECTOR

Code Injector — это инструмент для программного редактирования файлов из командной строки. Он позволяет вставлять, заменять, удалять код в любых файлах без ручного открытия редактора.

**Зачем это нужно:**
- Массовое обновление скриптов (добавить аргумент во все чекеры)
- Автоматическое исправление ошибок (заменить устаревший импорт)
- Удаление отладочного кода (убрать все TODO)
- Вставка шаблонов (добавить метаданные в файлы)
- CI/CD пайплайны (авто-фиксы при деплое)

**Где лежит:** `tools/code-injector.py`

---

## 📜 КОМАНДЫ

### Обязательные аргументы

`--file` / `-f` — путь к файлу для редактирования.

### Действия (выбрать одно)

`--after N` — вставить код после строки N.

`--before N` — вставить код перед строкой N.

`--after-pattern "regex"` — найти строку по паттерну и вставить после неё.

`--before-pattern "regex"` — найти строку по паттерну и вставить перед ней.

`--replace "regex"` — заменить строки, соответствующие паттерну, на новый код.

`--delete "regex"` — удалить все строки, соответствующие паттерну.

`--append` — добавить код в конец файла.

### Данные

`--code "..."` / `-c "..."` — код для вставки или замены. Может быть многострочным.

### Поиск

`--find "regex"` — найти строку по паттерну и показать её номер. Не изменяет файл.

### Опции

`--dry-run` — показать что будет сделано, без реальных изменений.

`--no-backup` — не создавать бэкап файла перед изменением.

---

## 📖 ПРИМЕРЫ

### Поиск

```bash
# Найти где объявлен SCAN_DIRS
python tools/code-injector.py -f tools/checkers/check-naming.py --find "SCAN_DIRS"
# → Строка 23: SCAN_DIRS = ["terminology", "researches"]
```

### Вставка по номеру строки

```bash
# Вставить import после 15 строки
python tools/code-injector.py -f tools/checkers/check-naming.py --after 15 --code "import argparse"
```

### Вставка по паттерну

```bash
# Найти "sys.path.insert" и вставить import перед ним
python tools/code-injector.py -f tools/checkers/check-naming.py --before-pattern "sys.path.insert" --code "import argparse"
```

### Замена кода

```bash
# Заменить объявление SCAN_DIRS на новое
python tools/code-injector.py -f tools/checkers/check-naming.py \
  --replace 'SCAN_DIRS = \[.*\]' \
  --code 'SCAN_DIRS = sys.argv[2:] if len(sys.argv) > 2 else ["terminology", "researches"]'
```

### Удаление кода

```bash
# Удалить все строки с TODO
python tools/code-injector.py -f tools/checkers/check-naming.py --delete "TODO"
```

### Добавление в конец

```bash
# Добавить код в конец файла
python tools/code-injector.py -f tools/checkers/check-naming.py --append --code "parser.add_argument('--path')"
```

### Многострочный код

```bash
# В PowerShell (многострочный)
python tools/code-injector.py -f test.py --after 10 --code "def new_func():\n    pass\n"

# В Bash
python tools/code-injector.py -f test.py --after 10 --code $'def new_func():\n    pass\n'
```

### Предпросмотр

```bash
# Посмотреть что будет без реальных изменений
python tools/code-injector.py -f test.py --replace "old" --code "new" --dry-run
```

---

## 🔄 ПАКЕТНОЕ ОБНОВЛЕНИЕ

Code Injector можно использовать в цикле для массового обновления файлов.

### Добавить import во все чекеры

```bash
for f in tools/checkers/check-*.py; do
    python tools/code-injector.py -f "$f" --after-pattern "sys.path.insert" --code "import argparse"
done
```

### Заменить SCAN_DIRS во всех чекерах

```bash
for f in tools/checkers/check-*.py; do
    python tools/code-injector.py -f "$f" \
        --replace 'SCAN_DIRS = \[.*\]' \
        --code 'SCAN_DIRS = [args.path] if args.path else ["terminology", "researches"]'
done
```

### Удалить все TODO из проекта

```bash
for f in $(find . -name "*.py"); do
    python tools/code-injector.py -f "$f" --delete "TODO" --no-backup
done
```

---

## 💾 БЭКАПЫ

Перед каждым изменением Code Injector создаёт бэкап файла в `tools/cache/backups/`.

Имя бэкапа: `{имя_файла}.{дата_время}.bak`

**Отключить бэкап:** `--no-backup`

**Восстановить из бэкапа:**

```bash
cp tools/cache/backups/check-naming.py.20260611_120000.bak tools/checkers/check-naming.py
```

---

## ⚠️ ПРАВИЛА БЕЗОПАСНОСТИ

1. **Всегда сначала --dry-run** — проверь что будет изменено
2. **Не отключай бэкапы** без необходимости
3. **Проверяй паттерны** через `--find` перед заменой
4. **Не используй на бинарных файлах** — только текстовые
5. **После массовых изменений** — запусти `check-code-quality.py`

---

## 🛠️ ТЕХНИЧЕСКИЕ ДЕТАЛИ

- Кодировка: UTF-8
- Паттерны: стандартные regex Python
- Нумерация строк: с 1
- Пустые строки в коде сохраняются
- Отступы в коде сохраняются как есть

---


---
