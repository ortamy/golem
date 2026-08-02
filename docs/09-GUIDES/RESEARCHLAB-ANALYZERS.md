# Анализаторы Research Lab

**Метаданные файла**

- **Заголовок:** Анализаторы Research Lab
- **Описание:** веб-модуль для слоя, ИИ- и диалект-анализа
- **Версия:** 1.0.0
- **Дата создания:** 2026-08-02
- **Методологическая основа:** [`docs/00-START/MANIFEST.md`](../00-START/MANIFEST.md)
- **Архитектурная основа:** [`docs/01-ARCHITECTURE/ARCHITECTURE.md`](../01-ARCHITECTURE/ARCHITECTURE.md)

## Где находится модуль

- `products/website/apps/researchlab/js/analyzers.js` — рендеринг экранов, mock-анализ и адаптер API.
- `products/website/apps/researchlab/css/analyzers.css` — стили карточек, форм, процентов и результатов.
- `products/website/apps/researchlab/index.html` — подключение ресурсов и пункты sidebar.
- `products/website/apps/researchlab/js/router.js` — hash-маршруты.
- `products/website/apps/researchlab/js/page-controller.js` — регистрация экранов в SPA-контроллере.

## Маршруты

- `.../apps/researchlab/index.html#analyzers` — обзор трёх карточек.
- `.../apps/researchlab/index.html#layer-analyzer` — процентный слой-анализ по восьми слоям.
- `.../apps/researchlab/index.html#ai-analyzer` — смысловой ИИ-анализ с выбором модели и режима.
- `.../apps/researchlab/index.html#dialect-analyzer` — поиск грецизмов и латинизмов с предложениями замен.

Открыть локально:

```bash
cd products/website
python -m http.server 8765
```

Затем открыть `http://127.0.0.1:8765/apps/researchlab/index.html#analyzers`.

## Источник результатов

`GolemAnalyzers.adapter` сначала отправляет запрос на `POST /api/analyzers/analyze`:

```json
{
  "text": "текст",
  "kind": "layer | ai | dialect",
  "settings": {"model": "golem-local", "mode": "local"}
}
```

Если endpoint недоступен, интерфейс автоматически использует автономный mock. Поэтому все три экрана можно демонстрировать без Flask/API и без ключей внешних моделей. Для подключения реального backend достаточно реализовать endpoint с совместимым JSON-контрактом или заменить `AnalyzerAdapter.analyze`; компоненты UI менять не нужно.

## Как добавить новый анализатор

1. Добавьте описание карточки в `renderOverview` и маршрут с понятным `data-module` в sidebar.
2. Добавьте route в массив `routedModules` файла `js/router.js`.
3. Добавьте ветку в `PageController` и новый тип в `GolemAnalyzers.render`.
4. Вынесите маркеры и настройки в отдельный каталог или endpoint, если анализатор должен обновляться без изменения UI.
5. Добавьте responsive-правила в `css/analyzers.css` и smoke-тест маршрута.

Для слоя-анализатора канонический CLI уже находится в `tools/analyzers/`. Веб-адаптер намеренно не выполняет командную строку из браузера: браузер не имеет безопасного прямого доступа к процессу Python; связка выполняется через HTTP API или автономный mock.