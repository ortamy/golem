# Быстрый старт для нового участника

**Файл:** `docs/09-GUIDES/ONBOARDING.md`
**Статус:** актуальный
**Опора:** `docs/00-START/MANIFEST.md`, `docs/01-ARCHITECTURE/ARCHITECTURE.md`

## Сначала прочитать

1. `README.md` — общий вход.
2. `docs/00-START/MANIFEST.md` — методологическое поле.
3. `docs/01-ARCHITECTURE/ARCHITECTURE.md` — границы систем.
4. `docs/INDEX.md` — карта документации.
5. `docs/02-MANAGEMENT/ROADMAP.md` — направления развития.
6. `docs/02-MANAGEMENT/BACKLOG.md` — текущие задачи.
7. `docs/09-GUIDES/WRITING.md` — правила написания.

Для Research Lab дополнительно прочитать `docs/11-PRODUCTS/RESEARCH-LAB.md`.

## Проверка окружения

```bash
git status
python --version
node --version
```

Для сайта:

```bash
cd products/website
npm install
npm run build
```

Для агентного слоя:

```bash
python products/agents/server.py
```

## Карта исходников

- `products/website/index.html` — публичный лендинг.
- `products/website/apps/researchlab/` — SPA лаборатории.
- `products/website/apps/researchlab/js/router.js` — hash-маршруты.
- `products/website/apps/researchlab/js/page-controller.js` — рендеринг.
- `products/website/apps/researchlab/js/lab-hero.js` — общая шапка и крошки.
- `products/website/apps/researchlab/data/` — JSON-данные.
- `products/agents/server.py` — Flask API.
- `products/agents/pipelines/` — пайплайны.
- `tools/` — генераторы и Design Baseline.

## Первый рабочий цикл

1. Найди задачу в `docs/02-MANAGEMENT/BACKLOG.md` или `tasks/`.
2. Проверь архитектурные границы.
3. Найди существующий модуль или документ.
4. Измени канонический исходник, не `build/`.
5. Запусти релевантную проверку.
6. Для сайта пересобери `build/` через `products/website/tools/build.sh`.
7. Проверь diff и обнови документацию при изменении маршрута/API/структуры.

## Контроль перед коммитом

```bash
git diff --check
node --check products/website/app.js
node --check products/website/apps/researchlab/js/router.js
node --check products/website/apps/researchlab/js/page-controller.js
```

## Безопасность

- Не коммить `.env`, ключи и персональные данные.
- Не редактировать `build/` вручную.
- Не считать `archive/` активным источником без проверки.
- Не переносить в новые инструкции команды из исторических `tools/checkers/`, `instructions/` и `backlog/`.