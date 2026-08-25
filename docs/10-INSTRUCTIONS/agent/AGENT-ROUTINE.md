# 📜 ROUTINE — ЕЖЕДНЕВНАЯ РУТИНА АГЕНТА «ЭД»

**Метаданные файла**
- **Файл:** `instructions/agent/ROUTINE.md`
- **Версия:** 2.0
- **Дата создания:** 2026-06-11
- **Последнее обновление:** 2026-06-12
- **Причина обновления:** Добавлены шаблоны метаданных, tree-health, проверка headers
- **Статус:** Активный
- **Тема:** Ежедневная рутина агента «Эд» — проверки, генерация, отчёт
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `instructions/agent/AGENT-PROMPT.md`, `tools/cache/cache-metadata-templates.json`, `ed/agent/agent.py`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-12

---

## 🔥 НАЗНАЧЕНИЕ

Ежедневная рутина агента «Эд». Выполняется автоматически при запуске или по расписанию. Шесть этапов: от проверки репозитория до отчёта.

---

## 🔄 6 ЭТАПОВ

### Этап 1: Проверка репозитория

```bash
python tools/checkers/check-naming.py
python tools/checkers/check-links.py
python tools/checkers/check-orphans.py
python tools/checkers/check-empty-files.py
python tools/checkers/check-code-quality.py
python tools/checkers/check-headers.py
```

**Действие:** запустить все чекеры. Если ошибки — зафиксировать в `AGENT-RETROSPECTIVE.md`.

---

### Этап 2: Проверка религионимов

```bash
python tools/checkers/check-religionisms.py
```

**Если найдены:**
```bash
python tools/checkers/check-religionisms.py --fix
```

**Действие:** исправить автоматически. Зафиксировать количество замен.

---

### Этап 3: Обновление метаданных и структуры

```bash
python tools/sync/sync-structure.py
python tools/generators/generate-metadata.py --fix
python tools/generators/generate-glossary.py
python tools/generators/generate-index.py
```

**Действие:** обновить `STRUCTURE.md`, `GLOSSARY.md`, `INDEX.md`. Привести метаданные к шаблонам из `cache-metadata-templates.json`.

---

### Этап 4: Проверка шаблонов метаданных

**Действие:** проверить что все новые файлы используют правильные метаданные из `tools/cache/cache-metadata-templates.json`. Если файл создан не по шаблону — обновить метаданные.

Особое внимание:
- `content/teachings/` — поле `Tree-Health` обязательно
- `ideas/` — поле `Статус идеи` обязательно

---

### Этап 5: Генерация файлов для веба

```bash
python tools/generators/generate-files-json.py
python tools/generators/generate-book.py
python tools/reports/report-dashboard.py
```

**Действие:** обновить `web/files.json`, сгенерировать книгу и дашборд.

---

### Этап 6: Отчёт и фиксация

**Действие:** записать в `AGENT-RETROSPECTIVE.md`:
- Дату выполнения
- Какие этапы пройдены
- Какие ошибки возникли
- Статистику: сколько файлов проверено, сколько исправлено

**Если были изменения:**
```bash
git add . && git commit -m "chore: ежедневная рутина агента [дата]"
```

---

## ⚡ БЫСТРЫЙ ЗАПУСК

```bash
python ed/agent/agent.py --auto "выполни ежедневную рутину"
```

---

## ⚠️ ОШИБКИ И РЕШЕНИЯ

| Ошибка | Решение |
|--------|---------|
| `name 're' is not defined` | Добавить `import re` в скрипт |
| `addwstr() returned ERR` | Ошибка curses на Windows, не критично |
| Файл не найден | Проверить `sys.path` в скрипте |
| Кэш устарел | `python tools/utils/clear-cache.py` |
| Метаданные не по шаблону | Сверить с `cache-metadata-templates.json` |

---

## 📋 ЧЕК-ЛИСТ

- [ ] Чекеры пройдены
- [ ] Религионимы исправлены
- [ ] Структура обновлена
- [ ] Метаданные по шаблонам
- [ ] Tree-Health заполнен для teachings
- [ ] Статус идеи заполнен для ideas
- [ ] files.json обновлён
- [ ] Отчёт записан