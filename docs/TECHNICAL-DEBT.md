# 📋 ТЕХНИЧЕСКИЙ ДОЛГ

**Метаданные файла**
- **Файл:** `docs/TECHNICAL-DEBT.md`
- **Версия:** 2.0
- **Дата создания:** 2026-05-28
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Добавлены новые скрипты для разработки
- **Статус:** Активный
- **Тема:** ТЕХНИЧЕСКИЙ ДОЛГ
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `docs/TECHNICAL-DEBT.md`, `docs/IDEAS.md`, `docs/ROADMAP.md`
- **Хеш:** ожидает
- **Достоверность:** средняя
- **Последний аудит:** 2026-06-11

---

## 📋 АКТИВНЫЕ ЗАДАЧИ

### 🆕 Новые скрипты для разработки

#### Чекеры
- [ ] **`check-md-quality.py`** — проверка качества `.md` файлов (стили, структура, метаданные)
- [ ] **`check-footnotes.py`** — проверка перекрёстных ссылок между исследованиями

#### Генераторы
- [ ] **`generate-sitemap.py`** — sitemap.xml для поисковиков
- [ ] **`generate-search-index.py`** — полнотекстовый индекс (JSON) для веб-интерфейса
- [ ] **`generate-rss.py`** — RSS-лента новых исследований

#### Мониторинг
- [ ] **`watch-changes.py`** — следит за файлами и авто-запускает чекеры
- [ ] **`notify.py`** — уведомления при ошибках

#### Веб
- [ ] **`deploy.sh`** — одной командой: генерация + коммит + пуш
- [ ] **`serve.py`** — простой HTTP-сервер на Python (без Node.js)

#### Утилиты
- [ ] **`backup-rotation.py`** — ротация старых бэкапов
- [ ] **`clean-empty.py`** — интерактивное удаление пустых файлов

---

### 🏛 Реорганизация tools/ — префиксы по папкам

#### Переименовать
- [ ] `unify-metadata.py` → `generate-metadata.py` ✅
- [ ] `add-related-links.py` → `generate-related-links.py`
- [ ] `fill-empty-files.py` → `generate-fill-empty.py`
- [ ] `generate-node-web.py` → `generate-web.py`
- [ ] `dashboard.py` → `report-dashboard.py`
- [ ] `stats-report.py` → `report-stats.py`
- [ ] `daily-report.py` → `report-daily.py`
- [ ] `check-health.py` → `report-health.py`
- [ ] `autodoc.py` → `auto-doc.py`
- [ ] `update-versions.py` → `auto-versions.py`
- [ ] `task-manager.py` → `auto-tasks.py`
- [ ] `idea-manager.py` → `auto-ideas.py`
- [ ] `clear-cache.py` → `auto-clear-cache.py`

#### Перенести
- [ ] `sync-structure.py` → `tools/sync/`
- [ ] `sync-changelogs.py` → `tools/sync/`

#### Удалить
- [ ] `tools/progress.py` — дубликат `lib/utils.py`
- [ ] `tools/structure.txt` — дубликат `STRUCTURE.md`
- [ ] `tools/menu.py` ✅
- [ ] `tools/tahor-filter.py` ✅

#### Обновить ссылки
- [ ] Обновить `golem.py` — пути к скриптам
- [ ] Обновить `README.md` — список инструментов

---

### База ТаНаХа
- [ ] Загрузить полный ТаНаХ на иврите в `tanakh.db`
- [ ] Интегрировать `check-tanakh-references.py` с `check-links.py`

### Нейросеть «Эд»
- [ ] Запустить `client.py --analyze-exposure`
- [ ] Подготовить датасет для fine-tune
- [ ] Настроить локальный сервер
- [ ] Интеграция с веб-интерфейсом

### Веб-интерфейс
- [ ] Хлебные крошки
- [ ] Подсветка иврита
- [ ] Блок «Связанные файлы»
- [ ] PWA
- [ ] Поиск по содержимому
- [ ] Офлайн-доступ

### Контент
- [ ] Заполнить `terminology/yetzer-lev.md`
- [ ] Заполнить `terminology/erech-apayim.md`

---

## ✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ (2026-06-11)

- [x] Создать `docs/IDEAS.md`
- [x] Обновить `docs/ROADMAP.md` до v2.0
- [x] Создать исследование `shmot-ha-sfarim.md`
- [x] Обновить все exposure-файлы
- [x] Создать `generate-exposure-suggestions.py`
- [x] Создать `code-injector.py` + документация
- [x] Создать `neural/scripts/generate-knowledge-cache.py`
- [x] Обновить `client.py` (режим `--use-cache`)
- [x] Создать `docs/NEURAL.md`
- [x] Перенести `export/` в `web/export/`
- [x] Обновить `generate-book.py`, `dashboard.py`, `search.py`
- [x] Утвердить структуру `tools/` с префиксами
- [x] Создать `rename-script.py`
- [x] Удалить `menu.py`, `tahor-filter.py`
- [x] Найти `shmot-ha-sfarim.md` в резервной копии

## ✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ (ранние)

- [x] Создать веб-интерфейс
- [x] Настроить деплой на GitHub Pages
- [x] 14 новых исследований
- [x] Реорганизовать `tools/` по подпапкам
- [x] Создать чекеры и генераторы