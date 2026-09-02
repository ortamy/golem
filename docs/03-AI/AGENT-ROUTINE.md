# Рутина AI-агента «Эд»

**Файл:** `docs/03-AI/AGENT-ROUTINE.md`
**Статус:** актуальный рабочий протокол
**Опора:** `docs/00-START/MANIFEST.md`, `docs/01-ARCHITECTURE/ARCHITECTURE.md`

## Перед началом

1. Прочитать `docs/00-START/MANIFEST.md`.
2. Прочитать `docs/01-ARCHITECTURE/ARCHITECTURE.md`.
3. Проверить `git status`.
4. Определить слой: документация, сайт, Research Lab, агенты или инструменты.

## Для документации

1. Найти существующий документ и проверить дубликаты.
2. Сверить путь с `docs/INDEX.md`.
3. Изменить канонический файл.
4. Проверить локальные ссылки, H1 и metadata.
5. Запустить `git diff --check`.
6. Обновить отчёт аудита при изменении структуры.

## Для публичного сайта

1. Найти исходник в `products/website/index.html`, `app.js` или `src/`.
2. Проверить desktop/mobile.
3. Выполнить `node --check products/website/app.js`.
4. Пересобрать сайт: `bash products/website/tools/build.sh`.
5. Проверить производный `build/` через HTTP-сервер.

## Для Research Lab

1. Проверить маршрут в `apps/researchlab/js/router.js`.
2. Проверить renderer в `page-controller.js` или профильном модуле.
3. Проверить `LabHero`, breadcrumbs и повторный переход.
4. Проверить локальный JSON fallback.
5. Пересобрать сайт после frontend-изменений.

Основные маршруты контроля:

- `#dashboard`;
- `#root-dictionary`;
- `#learn/paleo-trainer`;
- `#pipelines`;
- `#pipelines/<id>`;
- `#workbench`.

## Для агентов

```bash
python -m unittest discover -s products/agents/tests -p "test_*.py"
python products/agents/server.py
```

Проверить API, trace, сохранение результатов и fallback при недоступности Ollama.

## Завершение

- Проверить `git diff --check`.
- Убедиться, что `build/` получен сборкой.
- Не коммитить временные результаты и секреты.
- Записать изменённые файлы, проверки и ограничения.