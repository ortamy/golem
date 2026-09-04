# Research Lab smoke bugs

- [x] P0 · #dashboard · массовая загрузка 25 книг в `dashboard.js:35` блокировала main-thread; загрузка книг исключена из overview, книга открывается в отдельном маршруте · закрыто после smoke/probe
- [ ] P1 · #manifest, #dashboard, #workbench, #ai-agents, #pipelines, #agent-server, #club · относительный `favicon.svg` запрашивается из `apps/researchlab/`, но файл отсутствует в каталоге · (не создан: smoke остановлен до скриншота)
- [ ] P1 · #manifest, #dashboard, #ai-agents · часть UI-иконок запрашивается по отсутствующим путям `assets/icons/32/ui/scroll.png` и `assets/icons/32/archaeology/testtube.png` · (не создан: smoke остановлен до скриншота)