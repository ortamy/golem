# Тестирование проекта «Голем»

**Файл:** `docs/09-GUIDES/TESTING.md`
**Статус:** актуальный минимум проверки
**Опора:** `docs/01-ARCHITECTURE/ARCHITECTURE.md`

## Перед изменением

```bash
git status
```

Определи слой: документация, публичный сайт, Research Lab, Python-агенты или сборка.

## Документы

```bash
git diff --check
```

Проверь локальные ссылки, H1, пути в metadata, старые каталоги и отсутствие секретов.

## JavaScript

```bash
node --check products/website/app.js
node --check products/website/apps/researchlab/js/router.js
node --check products/website/apps/researchlab/js/page-controller.js
```

Для изменённого модуля проверь прямой hash-маршрут, повторный переход, общую шапку, breadcrumbs, JSON и mobile overflow.

## Сайт

```bash
cd products/website
bash tools/build.sh
```

После сборки подними HTTP-сервер из `build/`:

```bash
cd build
python -m http.server 8000
```

Проверь ширины 360, 480, 720 и desktop, сквозную шапку, тему, reduced-motion, waitlist и интерактивы лендинга.

## Research Lab

Проверяй основные маршруты:

```text
#dashboard
#root-dictionary
#learn/paleo-trainer
#pipelines
#pipelines/<id>
#workbench
#workbench/run/<id>
```

Проверь локальный fallback при недоступном агентном сервере.

## Python-агенты

```bash
python -m unittest discover -s products/agents/tests -p "test_*.py"
```

Минимальные области: линейный/циклический trace, кастомный пайплайн, сохранение результатов, `/api/health` и ошибка Ollama.

## После проверки

```bash
git diff --check
git status
```

Производные файлы должны быть получены сборкой. Временные скриншоты и локальные результаты не добавляй без явного назначения.