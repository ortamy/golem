
---

## 👥 КОМАНДА И РОЛИ

- **Ты** — цели, направление, финальное подтверждение
- **Эд (чат DeepSeek)** — стратегия, аудит (bdikah/mivdak/tikun/factcheck), промпты для Cline
- **Cline (VS Code)** — исполнение: пишет файлы, правит код, запускает скрипты
- **golem.py** — главное меню для запуска всех инструментов
- **Скрипты (tools/)** — массовые операции, проверки, генерация
- **Нейросеть (ed-neural/)** — отвечает на вопросы, анализирует exposure
- **Агент (ed-agent/)** — автономное выполнение цепочек задач

---

## 🔄 КОНВЕЙЕРЫ

### Новое исследование
- Ты: даёшь тему
- Cline: читает WORKFLOW-NEW-RESEARCH.md, пишет черновик
- Эд: проверяет через 4 этапа аудита
- Cline: исправляет замечания
- Ты: подтверждаешь
- Cline: перемещает файл, обновляет структуру, коммитит

### Проверка всего проекта
- Ты: «проверь проект»
- Cline: запускает `python tools/golem.py` → Run all checks
- Или: `python tools/checkers/check-religionisms.py --fix`
- Cline: докладывает результаты

### Деплой сайта
- Cline: `python tools/generators/generate-files-json.py`
- Cline: `git add . && git commit -m "..." && git push`
- GitHub Actions: авто-деплой на GitHub Pages

### Обновление знаний нейросети
- Cline: `python ed-neural/scripts/generate-knowledge-cache.py --rebuild`
- Нейросеть: кэш обновлён, отвечает по свежим данным

### Автономная работа агента
- Ты: «проверь всё и исправь»
- `python ed-agent/agent.py --auto "проверь всё и исправь"`
- Агент сам выбирает инструменты, запускает, докладывает

---

## 🗺 БЫСТРЫЙ ДОСТУП

- Пульт управления: `CONTROL.md` (этот файл)
- Техдолг: `docs/TECHNICAL-DEBT.md`
- Идеи: `docs/IDEAS.md`
- Бэклог (сегодня): `docs/BACKLOG.md`
- Дорожная карта: `docs/ROADMAP.md`
- Структура проекта: `STRUCTURE.md`
- Exposure-система: `instructions/exposure/`
- Все руководства: `docs/`
- Главное меню: `python tools/golem.py`
- Поиск по проекту: `python tools/utils/search.py "запрос"`
- Cline vs скрипты: `docs/CLINE-VS-SCRIPTS.md`

---

## 📋 РЕГУЛЯРНЫЕ ЗАДАЧИ

**Каждый день:**
- Открыть CONTROL.md
- Проверить что Cline делает
- Проверить что Эд проверил

**Раз в неделю:**
- Прогнать все чекеры через golem.py
- Обновить files.json
- Сгенерировать кэш знаний

**Раз в месяц:**
- Обновить STRUCTURE.md
- Обновить ROADMAP.md
- Провести ретроспективу (generate-retrospective.py)

---

> Этот файл — твой пульт. Не нужно помнить всё. Просто открой его.