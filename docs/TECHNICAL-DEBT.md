# 📋 ТЕХНИЧЕСКИЙ ДОЛГ — АВТОМАТИЗАЦИЯ

**Метаданные файла**
- **Файл:** `docs/TECHNICAL-DEBT.md`
- **Версия:** 3.0
- **Дата создания:** 2026-05-28
- **Последнее обновление:** 2026-06-16
- **Причина обновления:** Добавлены задачи по автоматизации, папка exposed, авто-обновление скриптов
- **Статус:** Активный
- **Тема:** Технический долг и задачи по автоматизации проекта
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `docs/TECHNICAL-DEBT.md`, `docs/IDEAS.md`, `docs/ROADMAP.md`
- **Хеш:** ожидает
- **Достоверность:** средняя
- **Последний аудит:** 2026-06-16

---

## 🤖 АВТОМАТИЗАЦИЯ — КРИТИЧЕСКОЕ

### Авто-обновление при создании новых папок

Система должна автоматически подхватывать новые папки в `content/` без ручного обновления кода.

**Что нужно сделать:**

- [ ] `server.js` — `SCAN_DIRS` должен сканировать `content/` рекурсивно, а не по жёстко заданному списку. Любая новая папка в `content/` → новая категория на сайте
- [ ] `generate-files-json.py` — то же самое. Сканировать `content/` целиком, а не по списку
- [ ] `SUBCATEGORY_LABELS` — вынести в отдельный JSON `tools/cache/cache-subcategories.json`, который можно редактировать без правки кода
- [ ] При создании новой папки в `content/` — `files.json` обновляется автоматически через GitHub Actions

### Авто-обновление golem.py

- [x] `auto_discover_scripts()` — уже сделано. Новые скрипты в `tools/checkers/`, `generators/`, `reports/` появляются в меню автоматически
- [ ] То же самое для `ed/assistant/tools.py` — чтобы новые скрипты появлялись в реестре инструментов ассистента
- [ ] То же самое для `ed/agent/tools.py` — чтобы агент знал о новых скриптах

### Авто-обновление dictionaries

- [ ] `check-tahor.py` — при `--rebuild` должен автоматически находить все новые `.md` файлы в `instructions/dictionaries/` и добавлять их в кэш
- [x] `build_tahor_cache()` — уже сканирует все файлы в `dictionaries/`. При добавлении нового словаря — перестроить кэш

---

## 📂 НОВАЯ ПАПКА — content/exposed/

### Создать папку для разоблачений

- [x] Создать `content/exposed/`
- [ ] Перенести туда файлы разоблачений из `researches/`:
  - `enuma-exposed.md`
  - `erasmus-textus-receptus.md`
  - `antichrist-exposed.md`
  - `fallen-messengers.md`
  - `byzantine-pietism.md`
  - `orphan-consciousness.md`
  - `religion-energy-harvest.md`
  - `sigils-as-circuits.md`
  - `bluetooth.md`
  - `microprocessors-as-temples.md`
  - `cities-as-processors.md`
  - `serpent-healing.md`
- [ ] Обновить внутренние ссылки в перенесённых файлах
- [ ] Обновить `files.json`

### Автоматизация exposed

- [ ] `server.js` — после переноса на авто-сканирование, папка `exposed/` подхватится сама
- [ ] `SUBCATEGORY_LABELS` — добавить подкатегории если появятся

---

## 🔧 GOLEM.PY — ДОРАБОТКИ

- [x] `auto_discover_scripts()` — автоматическое сканирование
- [x] `LOG_FILE` → `TOOLS_DIR / "golem.log"`
- [x] `CONFIG_FILE` → `TOOLS_DIR / "golem-config.json"`
- [x] Меню: добавлен `rebuild_tahor`
- [x] `scan_dirs` → `["content", "instructions", "docs"]`
- [ ] Добавить `check-headers` в `run_all_checks`
- [ ] Добавить `check-countries` в меню
- [ ] Обновить dashboard — убрать несуществующие чекеры, добавить новые

---

## 🌐 ВЕБ-ИНТЕРФЕЙС

- [ ] Починить мобильную версию — поиск и категории
- [ ] Интегрировать иконки (заменить эмодзи)
- [ ] Хлебные крошки
- [ ] Прогресс чтения
- [ ] Размер шрифта
- [ ] CSS-дерево для учений (Tree-Health)
- [ ] Полнотекстовый поиск через `golem.db`
- [ ] PWA + офлайн-доступ

---

## 🧠 НЕЙРОСЕТЬ

- [ ] Запустить `ed/neuro/`
- [ ] Сгенерировать кэш знаний
- [ ] Fine-tune на терминах и исследованиях

---

## 📊 БАЗА ДАННЫХ

- [x] Создать `data/golem.db`
- [ ] Наполнить из `.md` файлов
- [ ] Интегрировать с веб-интерфейсом
- [ ] Интегрировать с нейросетью

---

## ✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ

- [x] 218 учений заполнены
- [x] `check-tahor.py` — проверка чистоты языка
- [x] 19 словарей в `instructions/dictionaries/`
- [x] Шаблоны для всех типов файлов
- [x] `auto_discover_scripts()` в `golem.py`
- [x] `build_tahor_cache()` — авто-парсинг словарей
- [x] `--file` и `--fix` для одного файла в `check-tahor.py`
- [x] Перенос `CONFIG_FILE` и `LOG_FILE` в `TOOLS_DIR`