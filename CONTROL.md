# 📜 CONTROL — ПУЛЬТ УПРАВЛЕНИЯ ПРОЕКТОМ «ГОЛЕМ»

**Метаданные файла**
- **Файл:** `CONTROL.md`
- **Версия:** 3.0
- **Дата создания:** 2026-05-28
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Полная переработка — актуальная структура, команда, конвейеры, быстрый доступ
- **Статус:** Активный
- **Тема:** Пульт управления проектом — команда, конвейеры, быстрый доступ, регулярные задачи
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `CONTROL.md`, `docs/ROADMAP.md`, `docs/TECHNICAL-DEBT.md`, `docs/BACKLOG.md`, `STRUCTURE.md`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-11

---

## 🔥 НАЗНАЧЕНИЕ

Этот файл — пульт управления проектом. Открываешь его — видишь всё: кто чем занят, как запустить проверку, где что лежит. Не нужно помнить. Просто открой.

---

## 👥 КОМАНДА И РОЛИ

- **Ты** — цели, направление, финальное подтверждение
- **Эд (чат DeepSeek)** — стратегия, аудит (bdikah → mivdak → tikun → factcheck), промпты для Cline
- **Cline (VS Code)** — исполнение: пишет файлы, правит код, запускает скрипты
- **golem.py** — главное меню для запуска всех инструментов
- **Скрипты (tools/)** — массовые операции, проверки, генерация
- **Нейросеть (ed/neuro/)** — отвечает на вопросы, анализирует exposure
- **Агент (ed/agent/)** — автономное выполнение цепочек задач

---

## 🔄 КОНВЕЙЕРЫ

### Новое исследование

- Ты: даёшь тему
- Cline: читает `GUIDE-WORKFLOW-RESEARCH.md`, пишет черновик
- Эд: проверяет через 4 этапа аудита
- Cline: исправляет замечания
- Ты: подтверждаешь
- Cline: перемещает файл, обновляет структуру, коммитит

### Проверка всего проекта

- Ты: «проверь проект»
- Cline: запускает `python tools/golem.py` → Запустить все проверки
- Или: `python tools/checkers/check-religionisms.py --fix`
- Cline: докладывает результаты

### Деплой сайта

- Cline: `python tools/generators/generate-files-json.py`
- Cline: `git add . && git commit -m "..." && git push`
- GitHub Actions: авто-деплой на GitHub Pages

### Обновление знаний нейросети

- Cline: `python ed/neuro/scripts/generate-knowledge-cache.py --rebuild`
- Нейросеть: кэш обновлён, отвечает по свежим данным

### Автономная работа агента

- Ты: «проверь всё и исправь»
- `python ed/agent/agent.py --auto "проверь всё и исправь"`
- Агент сам выбирает инструменты, запускает, докладывает

---

## 🗺 БЫСТРЫЙ ДОСТУП

### Управление

- Пульт управления: `CONTROL.md` (этот файл)
- Технический долг: `docs/TECHNICAL-DEBT.md`
- Идеи: `docs/IDEAS.md`
- Бэклог (сегодня): `docs/BACKLOG.md`
- Дорожная карта: `docs/ROADMAP.md`
- Журнал решений: `docs/DECISIONS.md`
- Ретроспектива: `docs/RETROSPECTIVE.md`

### Структура

- Структура проекта: `STRUCTURE.md`
- Архитектура: `docs/ARCHITECTURE.md`
- Индекс файлов: `docs/INDEX.md`
- Глоссарий: `docs/GLOSSARY.md`
- Статистика: `docs/STATS.md`

### Методология

- Exposure-система: `instructions/exposure/`
- Словари замен: `instructions/dictionaries/`
- Принципы исследований: `instructions/RESEARCH-PRINCIPLES.md`
- Манифест: `instructions/MANIFEST.md`
- Запрещённые слова: `instructions/FORBIDDEN-WORDS.md`

### Инструменты

- Главное меню: `python tools/golem.py`
- Поиск по проекту: `python tools/utils/search.py "запрос"`
- Проверка религионимов: `python tools/checkers/check-religionisms.py --fix`
- Генерация files.json: `python tools/generators/generate-files-json.py`

### Веб

- Локальный сервер: `cd web && node server.js`
- Продакшн: GitHub Pages (авто-деплой)
- Документация интерфейса: `docs/WEB-INTERFACE.md`

### Руководства

- Все руководства: `guides/`
- Быстрый старт: `guides/GUIDE-ONBOARDING.md`
- Как писать: `guides/GUIDE-WRITING.md`
- Аудит: `guides/GUIDE-AUDIT.md`
- Терминология: `guides/GUIDE-TERMINOLOGY.md`

---

## 📋 РЕГУЛЯРНЫЕ ЗАДАЧИ

### Каждый день

- Открыть `CONTROL.md`
- Проверить что Cline делает
- Проверить что Эд проверил

### Раз в неделю

- Прогнать все чекеры через `golem.py`
- Обновить `files.json`
- Сгенерировать кэш знаний

### Раз в месяц

- Обновить `STRUCTURE.md`
- Обновить `ROADMAP.md`
- Провести ретроспективу: `python tools/generators/generate-retrospective.py`

---

## 🛠 ОСНОВНЫЕ КОМАНДЫ

```bash
# Проверка всего
python tools/golem.py

# Религионимы
python tools/checkers/check-religionisms.py --fix

# Ссылки
python tools/checkers/check-links.py

# Имена файлов
python tools/checkers/check-naming.py

# Генерация files.json
python tools/generators/generate-files-json.py

# Структура
python tools/sync/sync-structure.py

# Поиск
python tools/utils/search.py "запрос"

# Очистка кэша
python tools/utils/clear-cache.py

# Веб-сервер
cd web && node server.js