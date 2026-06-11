# 📋 ТЕХНИЧЕСКИЙ ДОЛГ

**Метаданные файла**
- **Файл:** `docs/TECHNICAL-DEBT.md`
- **Версия:** 2.1
- **Дата создания:** 2026-05-28
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Добавлены задачи по автономному агенту «Эд» и интеграции с Cline
- **Статус:** Активный
- **Тема:** ТЕХНИЧЕСКИЙ ДОЛГ
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `docs/TECHNICAL-DEBT.md`, `docs/IDEAS.md`, `docs/ROADMAP.md`, `docs/CLINE-VS-SCRIPTS.md`
- **Хеш:** ожидает
- **Достоверность:** средняя
- **Последний аудит:** 2026-06-11

---

## 📋 АКТИВНЫЕ ЗАДАЧИ

### 🤖 Автономный агент «Эд» (управляет Cline)

- [ ] Запустить `ed-neural/inference/server.py` локально
- [ ] Дообучить `ed-agent/agent.py` — добавить планировщик (составляет план из нескольких шагов)
- [ ] Интеграция с Cline — Эд создаёт файлы задач, Cline читает и выполняет
- [ ] Память агента — контекст между сессиями через `memory.py`
- [ ] Режим «автономный стратег» — Эд сам решает ЧТО делать, Cline делает КАК

### 🆕 Новые скрипты

- [ ] `check-md-quality.py` — проверка качества .md файлов
- [ ] `check-footnotes.py` — проверка перекрёстных ссылок
- [ ] `generate-sitemap.py` — sitemap.xml
- [ ] `generate-search-index.py` — полнотекстовый индекс для веб-интерфейса
- [ ] `generate-rss.py` — RSS новых исследований
- [ ] `watch-changes.py` — следит за файлами и запускает чекеры
- [ ] `notify.py` — уведомления при ошибках
- [ ] `deploy.sh` — деплой одной командой
- [ ] `serve.py` — простой HTTP-сервер на Python
- [ ] `backup-rotation.py` — ротация старых бэкапов

### 🏛 Реорганизация tools/

- [x] Переименовать скрипты с префиксами по папкам
- [x] Обновить `golem.py` — пути к скриптам
- [ ] Обновить `ed-agent/tools.py` — пути к utils/
- [ ] Поправить `sys.path` в файлах utils/

### База ТаНаХа
- [ ] Загрузить полный ТаНаХ в `tanakh.db`
- [ ] Интегрировать `check-tanakh-references.py` с `check-links.py`

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
- [x] Создать `docs/NEURAL.md`
- [x] Создать `docs/ED-AGENT.md`
- [x] Создать `docs/CLINE-VS-SCRIPTS.md`
- [x] Обновить все exposure-файлы
- [x] Создать `generate-exposure-suggestions.py`
- [x] Создать `code-injector.py` + документация
- [x] Создать `generate-knowledge-cache.py`
- [x] Создать `rename-script.py`
- [x] Создать `ed-agent/agent.py` + tools.py + memory.py
- [x] Обновить `client.py` (режим --use-cache)
- [x] Обновить `search.py`
- [x] Перенести `export/` в `web/export/`
- [x] Обновить `generate-book.py` и `report-dashboard.py`
- [x] Обновить `instructions/chat-prompt.md`
- [x] Обновить `instructions/checkers/` (все 6 файлов)
- [x] Удалить `menu.py`, `tahor-filter.py`, `progress.py`
- [x] Переименовать все скрипты с префиксами
- [x] Обновить `golem.py` до v5.5
- [x] Установить и настроить Cline
- [x] Создать `docs/CLINE-VS-SCRIPTS.md`

## ✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ (ранние)

- [x] Создать веб-интерфейс
- [x] Настроить деплой на GitHub Pages
- [x] 14 новых исследований
- [x] Реорганизовать `tools/` по подпапкам
- [x] Создать чекеры и генераторы