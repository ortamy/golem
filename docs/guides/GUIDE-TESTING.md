# 🧪 TESTING — ТЕСТИРОВАНИЕ СКРИПТОВ

**Метаданные файла**
- **Файл:** `docs/TESTING.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-11
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Как тестировать скрипты перед пушем
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `docs/TESTING.md`, `tools/checkers/`, `tools/generators/`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-11

---

## 🎯 ПРАВИЛО

Перед каждым коммитом прогнать:

```bash
python tools/checkers/check-code-quality.py
```

---

## 📋 ЧЕК-ЛИСТ ДЛЯ НОВОГО СКРИПТА

- [ ] `#!/usr/bin/env python3` в первой строке
- [ ] `sys.path.insert` правильный (utils — parent.parent, остальные — parent)
- [ ] Docstring у каждой функции
- [ ] `if __name__ == "__main__"` блок
- [ ] Аргументы через `argparse`
- [ ] `--help` показывает описание
- [ ] `--verbose` для подробного вывода
- [ ] `--dry-run` для опасных операций
- [ ] `--fix` для автоисправления
- [ ] Прогресс-бар для долгих операций

---

## 🧪 ТЕСТИРОВАНИЕ ЧЕКЕРА

```bash
# 1. Проверка без изменений
python tools/checkers/check-NAME.py

# 2. Проверка одного файла (если поддерживает)
python tools/checkers/check-NAME.py --file path/to/file.md

# 3. Dry-run (если есть)
python tools/checkers/check-NAME.py --fix --dry-run

# 4. Реальный запуск
python tools/checkers/check-NAME.py --fix

# 5. Проверить что не сломалось
python tools/checkers/check-NAME.py
```

---

## 🧪 ТЕСТИРОВАНИЕ ГЕНЕРАТОРА

```bash
# 1. Тестовая генерация (с лимитом)
python tools/generators/generate-NAME.py --limit 10

# 2. Проверить выходной файл
ls -la web/export/   # или tools/cache/

# 3. Полная генерация
python tools/generators/generate-NAME.py
```

---

## 🔧 ТЕСТИРОВАНИЕ CODE-INJECTOR

```bash
# Всегда сначала dry-run
python tools/utils/code-injector.py -f test.py --replace "old" --code "new" --dry-run

# С бэкапом
python tools/utils/code-injector.py -f test.py --replace "old" --code "new"

# Проверить результат
cat test.py
```

---

## 📦 ТЕСТИРОВАНИЕ ПЕРЕД ПУШЕМ

```bash
# 1. Качество кода
python tools/checkers/check-code-quality.py

# 2. Имена файлов
python tools/checkers/check-naming.py

# 3. Ссылки
python tools/checkers/check-links.py

# 4. Быстрый прогон религионизмов
python tools/checkers/check-religionisms.py

# Если всё чисто — коммит
git add . && git commit -m "Описание изменений"
```

---

## ⚠️ ЧТО ДЕЛАТЬ ЕСЛИ СКРИПТ СЛОМАЛСЯ

1. **Посмотреть лог:** `cat golem.log`
2. **Запустить с подробным выводом:** `python script.py --verbose`
3. **Проверить sys.path:** `python -c "import sys; print(sys.path)"`
4. **Проверить что файл на месте:** `ls -la tools/checkers/check-NAME.py`
5. **Восстановить из бэкапа:** `cp tools/cache/backups/file.py.bak tools/path/file.py`

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ
- `tools/checkers/check-code-quality.py`
- `tools/checkers/check-env.py`
- `docs/SCRIPTS-OVERVIEW.md`