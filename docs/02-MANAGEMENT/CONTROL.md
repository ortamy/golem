# Пульт управления проектом «Голем»

**Файл:** `docs/02-MANAGEMENT/CONTROL.md`
**Статус:** актуальный операционный вход
**Опора:** `docs/00-START/MANIFEST.md`, `docs/01-ARCHITECTURE/ARCHITECTURE.md`

## Быстрый доступ

- Архитектура: `docs/01-ARCHITECTURE/ARCHITECTURE.md`.
- Индекс документации: `docs/INDEX.md`.
- Задачи: `docs/02-MANAGEMENT/BACKLOG.md`.
- Дорожная карта: `docs/02-MANAGEMENT/ROADMAP.md`.
- Решения: `docs/02-MANAGEMENT/DECISIONS.md`.
- Технический долг: `docs/02-MANAGEMENT/TECHNICAL-DEBT.md`.
- Идеи: `docs/02-MANAGEMENT/IDEAS.md` и `docs/02-MANAGEMENT/LANDING-LAB-IDEAS.md`.
- Аудит документации: `docs/08-AUDITS/DOCS-AUDIT-2026-09-02.md`.

## Продукты

- Публичный сайт: `products/website/index.html`.
- Research Lab: `products/website/apps/researchlab/index.html`.
- Router: `products/website/apps/researchlab/js/router.js`.
- PageController: `products/website/apps/researchlab/js/page-controller.js`.
- Агентный сервер: `products/agents/server.py`.
- Пайплайны агентов: `products/agents/pipelines/`.

## Рабочие команды

### Frontend и Research Lab

```bash
cd products/website
npm install
npm run build
bash tools/build.sh
```

`npm run build` обновляет только общий `style.css`. Для полного deploy-артефакта всегда используй `tools/build.sh`.

### Проверка JavaScript

```bash
node --check products/website/app.js
node --check products/website/apps/researchlab/js/router.js
node --check products/website/apps/researchlab/js/page-controller.js
```

### Агентный сервер и тесты

```bash
python products/agents/server.py
python -m unittest discover -s products/agents/tests -p "test_*.py"
```

### Документы

```bash
git diff --check
```

Проверяй локальные ссылки, H1, пути metadata и отсутствие исторических команд в новых инструкциях.

## Операционный цикл

1. Прочитать `MANIFEST.md` и архитектуру.
2. Найти задачу в backlog или tasks.
3. Найти канонический исходник.
4. Изменить исходник, не `build/` и не cache.
5. Запустить релевантную проверку.
6. Пересобрать сайт, если менялся frontend.
7. Проверить diff и обновить документацию при изменении API, маршрута или структуры.
8. Зафиксировать результат в changelog или отчёте аудита.

## Правила

- Не коммитить секреты, `.env`, ключи и персональные данные.
- Не удалять словари и методологические документы только по совпадению имени.
- Не считать `archive/` активным источником без проверки.
- Рабочую гипотезу явно отделять от установленного факта.
- Исторические команды помечать как исторические, не выдавать их за рабочие.