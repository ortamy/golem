# Развёртывание проекта «Голем»

**Файл:** `docs/09-GUIDES/DEPLOY.md`
**Статус:** актуальный
**Опора:** `docs/01-ARCHITECTURE/ARCHITECTURE.md`

## Что разворачивается

- публичный статический сайт `products/website/`;
- Research Lab SPA в `products/website/apps/researchlab/`;
- производный слой `products/website/build/`;
- опциональный локальный Flask API `products/agents/server.py`.

## Сборка

```bash
cd products/website
npm install
bash tools/build.sh
```

Скрипт пересоздаёт `build/`, копирует сайт, Research Lab, assets и данные, затем выполняет frontend-сборку.

## Локальный просмотр

```bash
cd products/website/build
python -m http.server 8000
```

- `http://localhost:8000/` — публичный сайт;
- `http://localhost:8000/apps/researchlab/index.html#dashboard` — Research Lab.

HTTP-сервер нужен для загрузки JSON через `fetch`; `file://` для smoke-проверки не использовать.

## Агентный API

```bash
python products/agents/server.py
```

Основные endpoints: `/api/health`, `/api/info`, `/api/pipelines`, `/api/pipeline-results`, `/api/pipelines/<id>/run` и `/api/pipelines/<id>/results`.

Тесты:

```bash
python -m unittest discover -s products/agents/tests -p "test_*.py"
```

## GitHub Pages

Push в `main` запускает `.github/workflows/deploy.yml`, который вызывает `products/website/tools/build.sh` и публикует `products/website/build/`.

## Перед deploy

```bash
node --check products/website/app.js
node --check products/website/apps/researchlab/js/router.js
node --check products/website/apps/researchlab/js/page-controller.js
cd products/website
bash tools/build.sh
cd ../..
git diff --check
```

Старые `web/`, `ed-neural/`, `ed-agent/`, `tools/checkers/` и `tools/generators/` не входят в текущий deploy-контур.