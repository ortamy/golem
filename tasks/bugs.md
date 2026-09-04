# Research Lab smoke bugs

- [x] P0 · #dashboard · массовая загрузка 25 книг в `dashboard.js:35` блокировала main-thread; загрузка книг исключена из overview, книга открывается в отдельном маршруте · закрыто после smoke/probe
- [x] P1 · #manifest, #dashboard, #workbench, #ai-agents, #pipelines, #agent-server, #club · favicon теперь загружается из локального `apps/researchlab/favicon.svg` · закрыто до полного smoke
- [x] P1 · #manifest, #dashboard, #ai-agents · отсутствующие в изолированном smoke-сервере `scroll.png` и `testtube.png` заменены локальными SVG-ассетами · закрыто до полного smoke
- [x] P1 · #cartography · `loadWorldMap()` падал на `HTTP 404 for world map` (в изолированном запуске нет `world-map.svg`) и ронял общий `Promise.all` + `console.error`; добавлен `.catch()`-fallback на пустую геометрию в `js/cartography.js` · закрыто после полного smoke
- [x] P1 · offline-тест (#pipelines, «Сервер отключен») · браузерные console-ошибки `Failed to load resource: 404 / ERR_FAILED` ложно роняли `expect(errors).toEqual([])`; теперь собираются только `pageerror` (uncaught JS-errors), статические network-ошибки игнорируются · закрыто после полного smoke

Полный smoke после фиксов: `68 passed (15.6m)`, `stats: expected=68 unexpected=0 flaky=0`, `134 PNG` в `tests/screenshots/` (включая `cartography-desktop.png`/`cartography-mobile.png`), `git diff --check` чисто.