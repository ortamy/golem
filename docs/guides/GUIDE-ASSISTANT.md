# 🤖 GUIDE-ASSISTANT — КАК РАБОТАТЬ С АССИСТЕНТОМ «ЭД»

**Метаданные файла**
- **Файл:** `guides/GUIDE-ASSISTANT.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-11
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Как работать с ассистентом «Эд» в VS Code — команды, инструменты, примеры
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `ed-assistant/README.md`, `ed-assistant/assistant.py`, `guides/GUIDE-AGENT.md`, `guides/GUIDE-NEURO.md`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-11

---

## 🔥 ЧТО ТАКОЕ АССИСТЕНТ «ЭД»

Ассистент — CLI-инструмент для запуска скриптов проекта одной командой. Работает в VS Code, в терминале, в скриптах CI/CD.

Не автономен. Не помнит контекст. Ждёт команду — выполняет — забывает.

Для автономной работы используй агента (`ed-agent/`).

---

## 🚀 ЗАПУСК

```bash
python ed-assistant/assistant.py <команда>
```

---

## 📋 КОМАНДЫ

### Проверки

```bash
python ed-assistant/assistant.py check religionisms
python ed-assistant/assistant.py check links
python ed-assistant/assistant.py check naming
python ed-assistant/assistant.py check empty
python ed-assistant/assistant.py check duplicates
python ed-assistant/assistant.py check orphans
python ed-assistant/assistant.py check exposure
python ed-assistant/assistant.py check all
```

### Исправления

```bash
python ed-assistant/assistant.py fix religionisms
python ed-assistant/assistant.py fix metadata
```

### Генерация

```bash
python ed-assistant/assistant.py generate structure
python ed-assistant/assistant.py generate glossary
python ed-assistant/assistant.py generate index
python ed-assistant/assistant.py generate book
python ed-assistant/assistant.py generate files
```

### Отчёты

```bash
python ed-assistant/assistant.py report stats
python ed-assistant/assistant.py report dashboard
```

### Утилиты

```bash
python ed-assistant/assistant.py search "хесед"
python ed-assistant/assistant.py clear
python ed-assistant/assistant.py help
```

---

## 🔧 ИНСТРУМЕНТЫ

Ассистент использует скрипты из `tools/`. Всего 27 инструментов в реестре `ed-assistant/tools.py`.

- `checkers/` — 12 скриптов проверки
- `generators/` — 7 скриптов генерации
- `sync/` — 2 скрипта синхронизации
- `reports/` — 3 скрипта отчётов
- `utils/` — 2 утилиты

---

## 💡 ПРИМЕРЫ

### Ежедневная проверка

```bash
python ed-assistant/assistant.py check religionisms
python ed-assistant/assistant.py check links
```

### Подготовка к коммиту

```bash
python ed-assistant/assistant.py fix religionisms
python ed-assistant/assistant.py fix metadata
python ed-assistant/assistant.py check naming
```

### Полный аудит

```bash
python ed-assistant/assistant.py check all
python ed-assistant/assistant.py generate structure
python ed-assistant/assistant.py generate files
python ed-assistant/assistant.py report stats
```

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ
- `ed-assistant/README.md`
- `ed-assistant/assistant.py`
- `ed-assistant/tools.py`
- `guides/GUIDE-AGENT.md`
- `guides/GUIDE-NEURO.md`