# 📜 ROUTINE — ЕЖЕДНЕВНАЯ РУТИНА АГЕНТА «ЭД»

**Метаданные файла**
- **Файл:** `instructions/agent/ROUTINE.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-11
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** П ервичное создание
- **Статус:** Активный
- **Тема:** Ежедневная рутина агента «Эд» — проверки, генерация, отчёт
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `instructions/agent/ROUTINE.md`, `instructions/agent/AGENT-PROMPT.md`, `ed-agent/agent.py`, `tools/`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-11

---

## 🔥 НАЗНАЧЕНИЕ

Ежедневная рутина агента «Эд». Агент выполняет её автоматически при запуске или по расписанию. Пять этапов: от проверки репозитория до отчёта.

---

## 🔄 5 ЭТАПОВ

### Этап 1: Проверка репозитория

```bash
python tools/checkers/check-naming.py
python tools/checkers/check-links.py
python tools/checkers/check-orphans.py
python tools/checkers/check-empty-files.py
python tools/checkers/check-code-quality.py
```

**Действие:** запустить все чекеры. Если ошибки — зафиксировать в `AGENT-RETROSPECTIVE.md`.

---

### Этап 2: Проверка религионимов

```bash
python tools/checkers/check-religionisms.py
```

**Действие:** проверить все файлы на религионимы.

**Если найдены:**
```bash
python tools/checkers/check-religionisms.py --fix
```

**Действие:** исправить автоматически. Зафиксировать количество замен в `AGENT-RETROSPECTIVE.md`.

---

### Этап 3: Обновление структуры и метаданных

```bash
python tools/generators/generate-structure.py
python tools/generators/generate-metadata.py --fix
python tools/generators/generate-glossary.py
python tools/generators/generate-index.py
```

**Действие:** обновить `STRUCTURE.md`, `GLOSSARY.md`, `INDEX.md`. Привести метаданные к единому шаблону.

---

### Этап 4: Генерация файлов для веба

```bash
python tools/generators/generate-files-json.py
python tools/generators/generate-book.py
python tools/reports/report-dashboard.py
```

**Действие:** обновить `web/files.json`, сгенерировать книгу и дашборд.

---

### Этап 5: Отчёт и фиксация

**Действие:** записать в `AGENT-RETROSPECTIVE.md`:
- Дату выполнения
- Какие этапы пройдены
- Какие ошибки возникли
- Статистику: сколько файлов проверено, сколько исправлено

**Если были изменения:**
```bash
git add . && git commit -m "Ежедневная рутина агента: [дата]"
```

---

## ⚡ БЫСТРЫЙ ЗАПУСК

```bash
python ed-agent/agent.py --auto "выполни ежедневную рутину"
```

---

## ⚠️ ОШИБКИ

| Ошибка | Решение |
|--------|---------|
| `name 're' is not defined` | Добавить `import re` в скрипт |
| `addwstr() returned ERR` | Ошибка curses на Windows, не критично |
| Файл не найден | Проверить `sys.path` в скрипте |
| Кэш устарел | `python tools/utils/clear-cache.py` |

---

> **עֵד (Эд) — Свидетель.**
> Рутина — не ритуал. Это проверка чистоты. Каждый день.