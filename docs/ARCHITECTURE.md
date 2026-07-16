# АРХИТЕКТУРА ПРОЕКТА «ГОЛЕМ»

## Общая схема

golem/
├── researchlab/          # Исследовательская лаборатория (SPA)
│   ├── index.html        # 53+ модуля, хеш-роутинг
│   ├── css/              # lab.css + модульные стили
│   ├── js/               # Скрипты модулей + router.js
│   └── data/             # roots.json (127+ корней)
├── analysis/             # Методички (41 .md файл)
│   ├── dictionaries/     # 21 словарь подмен
│   ├── exposure/         # 14 принципов разоблачения
│   └── methodology/      # 6 методологий
├── content/              # Исследования, терминология, БаШаХ
├── methodology/          # MANIFEST.md, RESEARCH-PRINCIPLES.md
├── products/
│   ├── website/          # Публичный сайт + researchlab
│   │   └── researchlab/  # Лаборатория (деплой)
│   └── agents/           # Python-агенты (CrewAI)
│       ├── server.py     # Flask API
│       ├── knowledge_base.py  # RAG
│       ├── main.py       # CLI для агентов
│       └── agents/       # researcher.py, exposer.py, collector.py
├── tools/                # Python-утилиты, чекеры, генераторы
├── tasks/                # current.md, backlog.md, prompts.md
└── docs/                 # ARCHITECTURE.md, ROADMAP.md, CHANGELOG.md

## Компоненты

### Research Lab (frontend)
- Статический SPA, Vanilla JS
- Хеш-роутинг (router.js)
- 53+ модулей в LabRenderer
- Пергаментный UI (lab.css)
- **Аккордеон-меню** (5 блоков: Данные, Инструменты, Исследование, AI, Система)

### Dify (AI-платформа)
- Мульти-агентная система
- Web UI: localhost:3000
- RAG на analysis/
- API: localhost:5001/v1

### Агенты (Python)
- Flask сервер: localhost:8000
- Эндпоинты: /api/run, /api/ask
- RAG поиск по методичкам
- CrewAI для сложных цепочек

### Данные
- roots.json — корни с палео-образами
- analysis/ — методички (.md)
- content/ — исследования

## Внешние интеграции

- 9Router: localhost:20128 (экономия токенов для Claude Code/Cline)
- Kiro AI: бесплатный Claude через 9Router
- GitHub Pages: деплой researchlab
- GitHub Actions: CI/CD

## Потоки данных

1. Пользователь → Research Lab → fetch → Flask API → CrewAI → ответ
2. Пользователь → Research Lab → RAG (knowledge_base.py) → методички → ответ
3. Пользователь → Dify Web UI → агенты → RAG → ответ
4. Разработчик → Claude Code/Cline → 9Router → Kiro/Claude API → код