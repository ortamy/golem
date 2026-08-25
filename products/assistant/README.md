# 🤖 АССИСТЕНТ «ЭД» — ДОКУМЕНТАЦИЯ

**Метаданные файла**
- **Файл:** `ed-assistant/README.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-11
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Документация ассистента «Эд» для VS Code — запуск, команды, архитектура
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `ed-assistant/assistant.py`, `ed-assistant/tools.py`, `ed-assistant/config.yml`, `ed-agent/`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-11

---

## 🔥 ЧТО ТАКОЕ АССИСТЕНТ «ЭД»

Ассистент «Эд» — помощник в VS Code. Ждёт команд пользователя и выполняет их, запуская скрипты из `tools/`. В отличие от агента, не работает автономно и не помнит контекст между сессиями.

**Ассистент vs Агент:**
- Ассистент — ждёт команду, выполняет, забывает
- Агент — сам решает что делать, строит план, помнит контекст

---

## 🏛 АРХИТЕКТУРА

```
ed-assistant/
├── README.md          # этот файл
├── config.yml         # конфигурация
├── assistant.py       # основной скрипт
└── tools.py           # реестр инструментов
```

---

## 🚀 ЗАПУСК

```bash
# Проверка религионимов
python ed-assistant/assistant.py check religionisms

# Исправление религионимов
python ed-assistant/assistant.py fix religionisms

# Генерация структуры
python ed-assistant/assistant.py generate structure

# Статистика
python ed-assistant/assistant.py report stats

# Поиск
python ed-assistant/assistant.py search "хесед"

# Очистка кэша
python ed-assistant/assistant.py clear

# Справка
python ed-assistant/assistant.py help
```

---

## 📋 КОМАНДЫ

### Проверки
- `check religionisms` — поиск религионимов во всех md-файлах
- `check links` — проверка внутренних ссылок
- `check naming` — проверка имён файлов
- `check empty` — поиск пустых и незаполненных файлов
- `check duplicates` — поиск дубликатов
- `check orphans` — поиск файлов без входящих ссылок
- `check exposure` — проверка текста по exposure-критериям
- `check all` — запустить все проверки

### Исправления
- `fix religionisms` — автоматически заменить религионимы во всех файлах
- `fix metadata` — привести метаданные к единому шаблону

### Генерация
- `generate structure` — обновить `STRUCTURE.md`
- `generate glossary` — обновить `GLOSSARY.md`
- `generate index` — обновить `INDEX.md`
- `generate book` — сгенерировать HTML-книгу
- `generate files` — обновить `web/files.json`

### Отчёты
- `report stats` — полная статистика репозитория
- `report dashboard` — дашборд проекта

### Утилиты
- `search <запрос>` — поиск по содержимому всех md-файлов
- `clear` — очистить кэш (`tools/cache/`)
- `help` — показать справку

---

## 🔧 КОНФИГУРАЦИЯ

Файл: `ed-assistant/config.yml`

```yaml
assistant:
  name: "Эд"
  version: "1.0"
  language: "ru"

tools:
  path: "../tools"
```

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ
- `ed-agent/` — автономный агент «Эд»
- `tools/` — скрипты проекта