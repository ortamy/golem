# 📜 CONTROL — ПУЛЬТ УПРАВЛЕНИЯ ПРОЕКТОМ «ГОЛЕМ»

**Метаданные файла**
- **Файл:** `CONTROL.md`
- **Версия:** 4.0
- **Дата создания:** 2026-05-28
- **Последнее обновление:** 2026-06-14
- **Причина обновления:** Обновлены пути, инструменты, добавлены новые словари и чекеры
- **Статус:** Активный
- **Тема:** Пульт управления проектом — команда, конвейеры, быстрый доступ, регулярные задачи
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `CONTROL.md`, `docs/ROADMAP.md`, `docs/TECHNICAL-DEBT.md`, `docs/BACKLOG.md`, `STRUCTURE.md`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-14

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
- **Нейросеть (products/neuro/)** — отвечает на вопросы, анализирует exposure
- **Агент (products/agent/)** — автономное выполнение цепочек задач

---

## 🔄 КОНВЕЙЕРЫ

### Новое исследование
- Ты: даёшь тему
- Cline: читает `WORKFLOW-RESEARCH.md`, пишет черновик
- Эд: проверяет через 4 этапа аудита
- Cline: исправляет замечания
- Ты: подтверждаешь
- Cline: перемещает файл, обновляет структуру, коммитит

### Проверка всего проекта
- Ты: «проверь проект»
- Cline: запускает `python tools/golem.py` → Запустить все проверки
- Или: `python tools/checkers/check-tahor.py --fix`
- Cline: докладывает результаты

### Деплой сайта
- Cline: `python tools/generators/generate-files-json.py`
- Cline: `git add . && git commit -m "..." && git push`
- GitHub Actions: авто-деплой на GitHub Pages

### Обновление кэша словарей
- Cline: `python tools/generators/generate-tahor-cache.py`
- Или: `python tools/checkers/check-tahor.py --rebuild`
- Словари обновлены, проверка работает с актуальными данными

---

## 🗺 БЫСТРЫЙ ДОСТУП

### Управление
- Пульт управления: `CONTROL.md` (этот файл)
- Технический долг: `docs/02-MANAGEMENT/TECHNICAL-DEBT.md`
- Идеи: `docs/02-MANAGEMENT/IDEAS.md`
- Бэклог: `docs/02-MANAGEMENT/BACKLOG.md`
- Дорожная карта: `docs/02-MANAGEMENT/ROADMAP.md`
- Журнал решений: `docs/02-MANAGEMENT/DECISIONS.md`
- Ретроспектива: `docs/02-MANAGEMENT/RETROSPECTIVE.md`

### Структура
- Структура проекта: `docs/INDEX.md`
- Архитектура: `docs/01-ARCHITECTURE/ARCHITECTURE.md`
- Индекс файлов: `docs/INDEX.md`
- Глоссарий: `docs/04-STANDARD/TERMINOLOGY.md`
- Статистика: `docs/02-MANAGEMENT/STATS.md`

### Методология
- Exposure-система: `docs/06-METHODOLOGY/`
- Словари языковых подмен: `docs/05-DICTIONARIES/`
- Принципы исследований: `docs/06-METHODOLOGY/RESEARCH-PRINCIPLES.md`
- Манифест: `docs/00-START/MANIFEST.md`
- Правила языка: `docs/04-STANDARD/TERMINOLOGY.md`

### Инструменты
- Главное меню: `python tools/golem.py`
- Поиск по проекту: `python tools/utils/search.py "запрос"`
- Проверка языковых подмен: `python tools/checkers/check-tahor.py --fix`
- Проверка заголовков: `python tools/checkers/check-headers.py`
- Аудит полезности: `python tools/checkers/check-mivdak.py`
- Генерация files.json: `python tools/generators/generate-files-json.py`
- Генерация кэша словарей: `python tools/generators/generate-tahor-cache.py`

### Веб
- Локальный сервер: `cd products/website && node server.js`
- Продакшн: GitHub Pages (авто-деплой)
- Документация интерфейса: `products/website/`

### Руководства
- Все руководства: `guides/`
- Быстрый старт: `guides/ONBOARDING.md`
- Как писать: `guides/GUIDE-WRITING.md`
- Аудит: `guides/AUDIT.md`
- Терминология: `guides/TERMINOLOGY.md`

---

## 📋 РЕГУЛЯРНЫЕ ЗАДАЧИ

### Каждый день
- Открыть `CONTROL.md`
- Проверить что Cline делает
- Проверить что Эд проверил

### Раз в неделю
- Прогнать все чекеры через `golem.py`
- Обновить `files.json`
- Обновить кэш словарей

### Раз в месяц
- Обновить `STRUCTURE.md`
- Обновить `ROADMAP.md`
- Провести ретроспективу

---

## 🛠 ОСНОВНЫЕ КОМАНДЫ

```bash
# Проверка языковых подмен
python tools/checkers/check-tahor.py --fix

# Проверка заголовков
python tools/checkers/check-headers.py

# Аудит полезности
python tools/checkers/check-mivdak.py

# Генерация кэша словарей
python tools/generators/generate-tahor-cache.py

# Проверка всего
python tools/golem.py

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
cd products/website && node server.js
