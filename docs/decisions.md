# Архитектурные решения (ADR)

### ADR-001: Ребрендинг GOLEM → ALEPHY
- Дата: 2026-09-11
- Статус: accepted
- Контекст: решение о переименовании бренда проекта во всех слоях (сайт, лаборатория, документы, docker, агенты, видео).
- Решение: регистро-сохраняющая замена golem/GOLEM/Golem → alephy/ALEPHY/Alephy и кириллических брендовых форм («Голем»/«ГОЛЕМ» со склонениями → «Алефи»/«АЛЕФИ») кодмодом `tools/rebrand-alephy.mjs`. Переименованы ассеты (golem-logo/symbol → alephy-*), `docs/14-APPS/GOLEM.md` → `ALEPHY.md`, docker-сервис/сеть/volume, ключи localStorage (`golem_theme` → `alephy_theme` и др.), идентификаторы `GolemState/GolemUI/GolemParser/GolemAPI`.
- Альтернативы: оставить исторические упоминания в docs/99-HISTORICAL (отвергнуто — требуется полная консистентность бренда).
- Последствия и защищённые зоны:
  - Термин גֹּלֶם/«голем» как объект исследования НЕ переименован: `docs/05-DICTIONARIES/`, `products/neuro/training-data/`, словарная страница `terminology/golem.md`, анкер `roots.json#golem`, внешние training-данные.
  - `HF_REPO="golem/ed-v1"` в `products/neuro/models/download.sh` — внешний репозиторий HuggingFace, не тронут.
  - Ссылки `github.com/ortamy/golem` и `ortamy.github.io/golem` заменены на `/alephy` — требуют переименования GitHub-репозитория и настройки Pages.
  - Пользовательские данные: старые localStorage-ключи (`golem_*`) будут проигнорированы — сохранённые темы/настройки сбросятся.
