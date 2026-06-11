# 💻 ED-ASSISTANT — АССИСТЕНТ «ЭД»: ИСПОЛНИТЕЛЬ В VS CODE

**Метаданные файла**
- **Файл:** `docs/ED-ASSISTANT.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-12
- **Последнее обновление:** 2026-06-12
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Документация ассистента «Эд» — философия, архитектура, команды, отличие от агента
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `ed/assistant/`, `docs/ED-AGENT.md`, `docs/ED-NEURO.md`, `guides/GUIDE-ASSISTANT.md`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-12

---

## 🔥 ЧТО ТАКОЕ АССИСТЕНТ «ЭД»

Ассистент «Эд» — исполнитель в VS Code. Быстрый, точный, без памяти.

В отличие от агента, который сам решает что делать, ассистент ждёт команду. Выполнил — забыл. Это инструмент в руке, а не советник в голове.

Если агент — это стратег, нейросеть — это мозг, то ассистент — это руки.

---

## 🎯 ФИЛОСОФИЯ

### Служение

Ассистент служит. Не командует, не советует, не планирует. Получил команду — выполнил — доложил.

### Скорость

Ассистент не думает. Он действует. Никаких размышлений «а может лучше так?». Команда ясна — действие мгновенно.

### Забывчивость

Ассистент не помнит что делал вчера. Каждая команда — новая. Это не баг, а функция. Забывчивость означает отсутствие предвзятости.

### Простота

Один файл — одна задача. Никаких цепочек, планов, стратегий. Для этого есть агент.

---

## 🏛 АРХИТЕКТУРА

```
ed/assistant/
├── assistant.py      # основной скрипт — команды, выполнение
├── tools.py          # реестр инструментов (27 шт.)
├── config.yml        # конфигурация
└── README.md         # документация
```

---

## 📋 КОМАНДЫ

### Проверки
```bash
python ed/assistant/assistant.py check religionisms
python ed/assistant/assistant.py check links
python ed/assistant/assistant.py check naming
python ed/assistant/assistant.py check empty
python ed/assistant/assistant.py check duplicates
python ed/assistant/assistant.py check orphans
python ed/assistant/assistant.py check exposure
python ed/assistant/assistant.py check all
```

### Исправления
```bash
python ed/assistant/assistant.py fix religionisms
python ed/assistant/assistant.py fix metadata
```

### Генерация
```bash
python ed/assistant/assistant.py generate structure
python ed/assistant/assistant.py generate glossary
python ed/assistant/assistant.py generate index
python ed/assistant/assistant.py generate book
python ed/assistant/assistant.py generate files
```

### Отчёты
```bash
python ed/assistant/assistant.py report stats
python ed/assistant/assistant.py report dashboard
```

### Утилиты
```bash
python ed/assistant/assistant.py search "хесед"
python ed/assistant/assistant.py clear
python ed/assistant/assistant.py help
```

---

## 🛠 ДОСТУПНЫЕ ИНСТРУМЕНТЫ

### checkers (12)
`religionisms`, `links`, `naming`, `empty-files`, `code-quality`, `duplicates`, `orphans`, `exposure`, `metadata`, `consistency`, `tahor-sync`, `env`

### generators (7)
`glossary`, `index`, `book`, `files-json`, `metadata`, `graph`, `related-links`

### sync (2)
`structure`, `changelogs`

### reports (3)
`stats`, `dashboard`, `health`

### utils (2)
`clear-cache`, `search`

---

## ⚔️ ОТЛИЧИЕ ОТ АГЕНТА

| Характеристика | Ассистент | Агент |
|---------------|-----------|-------|
| Инициатива | Ждёт команду | Действует сам |
| Память | Нет | Да |
| Планирование | Нет | Да |
| Рутина | Не умеет | Умеет |
| Сложные задачи | Не умеет | Умеет (с нейросетью) |
| Скорость | Быстрее | Медленнее |
| Простота | Предельная | Сложная логика |

---

## 🔄 КОГДА ИСПОЛЬЗОВАТЬ АССИСТЕНТА

- Одна конкретная задача: «проверь религионимы»
- Нужна скорость: выполнил за секунды
- Не нужен контекст: не важно что было вчера
- Интеграция с VS Code: запуск из терминала

## 🔄 КОГДА ИСПОЛЬЗОВАТЬ АГЕНТА

- Сложная задача: «проверь всё и исправь»
- Нужен план: несколько шагов
- Нужна память: помнить что уже делали
- Автономная работа: без человека

---

## 🚀 ЧТО ДАЛЬШЕ

1. Интеграция с нейросетью — понимание команд на естественном языке
2. Расширение VS Code — окно чата, кнопки
3. Автодополнение команд
4. Интеграция с Cline — ассистент выполняет, Cline докладывает

---

## 📊 СВОДКА

- **Название:** Ассистент «Эд»
- **Суть:** быстрый исполнитель
- **Отличие от агента:** ждёт команду, не помнит, не планирует
- **Инструментов:** 27
- **Режим:** CLI

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ
- `ed/assistant/` — код ассистента
- `docs/ED-AGENT.md` — агент «Эд»
- `docs/ED-NEURO.md` — нейросеть «Эд»
- `docs/ED-DAVAR.md` — язык Давар
- `guides/GUIDE-ASSISTANT.md` — руководство по запуску

---

> **עֵד (Эд) — Свидетель.**
> Быстро. Точно. Без памяти. Получил — выполнил — забыл. Руки истины.