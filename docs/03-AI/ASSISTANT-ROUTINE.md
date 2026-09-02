# Рутина ассистента проекта

**Файл:** `docs/03-AI/ASSISTANT-ROUTINE.md`
**Статус:** актуальный рабочий протокол
**Опора:** `docs/00-START/MANIFEST.md`, `docs/01-ARCHITECTURE/ARCHITECTURE.md`

Ассистент работает как слой постановки, проверки и фиксации задач. Он не подменяет кодовую проверку предположением и не выдаёт рабочую гипотезу за факт.

## Перед сессией

1. Прочитать `docs/00-START/MANIFEST.md`.
2. Прочитать `docs/01-ARCHITECTURE/ARCHITECTURE.md`.
3. Проверить `docs/02-MANAGEMENT/BACKLOG.md` и `tasks/`.
4. Проверить `git status`.

## Во время задачи

- Определить канонический исходник.
- Не редактировать `build/` вручную.
- Проверять существующие маршруты и API перед добавлением новых.
- Для документов проверять ссылки, H1 и metadata.
- Для JavaScript запускать `node --check`.
- Для сайта после правок запускать `products/website/tools/build.sh`.
- Для агентов запускать unittest из `products/agents/tests`.

## Минимальная проверка

```bash
git diff --check
node --check products/website/app.js
node --check products/website/apps/researchlab/js/router.js
node --check products/website/apps/researchlab/js/page-controller.js
```

## Отчёт

В конце сессии зафиксировать:

- что изменено;
- какие команды запущены;
- какие проверки прошли;
- какие ограничения остались;
- нужно ли обновить архитектуру, backlog или changelog.