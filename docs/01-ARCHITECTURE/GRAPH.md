# Карта связей проекта «Голем»

**Файл:** `docs/01-ARCHITECTURE/GRAPH.md`
**Статус:** актуальная схема границ
**Опора:** `docs/01-ARCHITECTURE/ARCHITECTURE.md`

## Слои

```mermaid
flowchart TD
    User[Пользователь]
    Landing[products/website/index.html<br/>Публичный лендинг]
    Lab[Research Lab SPA<br/>apps/researchlab/index.html]
    Router[LabRouter<br/>js/router.js]
    Controller[PageController<br/>js/page-controller.js]
    Hero[LabHero<br/>js/lab-hero.js]
    Data[Локальные JSON<br/>apps/researchlab/data/]
    Storage[localStorage<br/>прогресс, черновики, waitlist]
    Server[products/agents/server.py<br/>Flask API]
    Agents[agents/ + pipelines/<br/>Python исполнение]
    Docs[docs/00-START + docs/06-METHODOLOGY<br/>контекст и методология]
    Build[products/website/build/<br/>производный deploy-слой]

    User --> Landing
    User --> Lab
    Landing --> Lab
    Lab --> Router
    Router --> Controller
    Controller --> Hero
    Controller --> Data
    Controller --> Storage
    Controller --> Server
    Server --> Agents
    Agents --> Data
    Docs --> Agents
    Landing --> Build
    Lab --> Build
```

## Research Lab: жизненный цикл маршрута

```text
location.hash
    ↓
LabRouter.parseHash()
    ↓
LabRouter.showModule()
    ↓
PageController.render(moduleId, container, parsed)
    ↓
профильный renderer модуля
    ↓
LabHero.setView() + renderBreadcrumbs()
    ↓
локальный JSON или products/agents/server.py
```

## Основные границы

- `docs/` объясняет систему и задаёт методологические ограничения.
- `products/website/index.html` — публичная точка входа, не Research Lab renderer.
- `products/website/apps/researchlab/` — статический SPA-интерфейс инструментов.
- `products/agents/` — серверное выполнение пайплайнов и API.
- `localStorage` — локальное состояние пользователя; не серверная база.
- `build/` — результат сборки; править только исходники.
- `archive/` — исторический контекст, не активная зависимость.

## Ключевые маршруты Research Lab

- `#dashboard` — рабочий стол.
- `#root-dictionary` — корневой словарь.
- `#learn/paleo-trainer` — палео-тренажёр.
- `#pipelines` — список пайплайнов.
- `#pipelines/<id>` — detail-страница пайплайна и результата.
- `#workbench` — мастерская.
- `#workbench/run/<id>` — запуск пайплайна.
- `#workbench/project/<id>` — проект и история результата.

## Данные и fallback

- Словари, корни, буквы, методология и корпус загружаются из `apps/researchlab/data/`.
- Пайплайны читаются из `data/pipelines.json`.
- Результаты читаются из API, затем из локального `data/pipeline-results.json`.
- При недоступном агентном сервере локальные экраны должны продолжать работать.
- Waitlist публичного лендинга использует Supabase только при наличии клиента; иначе — `localStorage.golem_waitlist`.

## Обновление схемы

При изменении структуры сначала обновить `ARCHITECTURE.md`, затем эту карту. Не восстанавливать старые узлы `instructions/`, `tools/checkers/`, `LabRenderer` и другие исторические слои без фактического кода.