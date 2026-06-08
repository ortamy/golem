# 📜 ТЕХНИЧЕСКИЙ ДОЛГ

**Метаданные файла**
- **Файл:** `docs/TECHNICAL-DEBT.md`
- **Версия:** 1.5
- **Дата создания:** 2026-05-28
- **Последнее обновление:** 2026-06-09
- **Причина обновления:** Переписаны все задачи в формате «глагол + объект»
- **Статус:** Активный

---

## 📋 АКТИВНЫЕ ЗАДАЧИ

### Конфликты слияния Git

- [x] Убрать `<<<<<<< HEAD` / `>>>>>>>` в `instructions/image-map.md`
- [x] Убрать `<<<<<<< HEAD` / `>>>>>>>` в `instructions/images-catalogue.md`
- [x] Убрать `<<<<<<< HEAD` / `>>>>>>>` в `instructions/methodology/archeology-methodology.md`
- [x] Убрать `<<<<<<< HEAD` / `>>>>>>>` в `instructions/methodology/hebrew-reconstruction.md`
- [x] Убрать `<<<<<<< HEAD` / `>>>>>>>` в `instructions/methodology/translation-methodology.md`
- [x] Убрать `<<<<<<< HEAD` / `>>>>>>>` в `instructions/methodology/transliteration-distortions.md`
- [x] Убрать `<<<<<<< HEAD` / `>>>>>>>` в `instructions/methodology/tree-method.md`
- [x] Убрать `<<<<<<< HEAD` / `>>>>>>>` в `instructions/checkers/bdikah-checker.md`
- [x] Убрать `<<<<<<< HEAD` / `>>>>>>>` в `instructions/checkers/factcheck.md`
- [x] Убрать `<<<<<<< HEAD` / `>>>>>>>` в `instructions/checkers/mivdak.md`

### Унифицировать папку checkers

- [ ] Выбрать единую папку для чекеров: `tools/checkers/` или `instructions/checkers/`
- [ ] Перенести `.md`-чекеры в выбранную папку
- [ ] Обновить ссылки на чекеры в `chat-prompt.md`, `workflow.md`, `startup-checklist.md`

### Сократить chat-prompt.md

- [ ] Вынести детали из `chat-prompt.md` в отдельные файлы
- [ ] Оставить в `chat-prompt.md` только ядро: источник, имя, запреты, процесс, тон

### Создать новые файлы терминов

- [ ] Создать `terminology/midbar.md` — מִדְבָּר (пустыня как экзамен)
- [ ] Создать `terminology/levad.md` — לְבַד (один как свобода)
- [ ] Создать `terminology/arum.md` — עָרוּם (хитрый, проницательный)
- [ ] Создать `terminology/nachash.md` — נָּחָשׁ (змей)
- [ ] Создать `terminology/pachad.md` — פַּחַד (страх порабощающий)
- [ ] Создать `researches/galatim-two-systems.md` — Галатим: война двух систем
- [ ] Создать `researches/substitution-of-the-name.md` — кража Имени

### Заполнить пустые файлы

- [ ] Заполнить содержимым `researches/galatim-two-systems.md`
- [ ] Заполнить содержимым `terminology/yetzer-lev.md`
- [ ] Заполнить содержимым `terminology/erech-apayim.md`

### Системные проблемы

- [ ] Исправить путь в метаданных `immanu-el.md` (указано `researches/`, лежит в `terminology/`)
- [ ] Проверить все файлы `terminology/` на правильность папки в метаданных
- [ ] Создать `requirements.txt` для Python-инструментов в `tools/`
- [ ] Проверить дубликаты: `or-tam.md`, `sheerit.md`, `platform-idea.md`, `davar-language.md`
- [ ] Проверить работоспособность всех скриптов в подпапках `tools/`

### Обновить существующие файлы

- [ ] Обновить ссылки в `chat-prompt.md`
- [ ] Обновить статистику в `README.md`

---

## ✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ (2026-06-07 — 2026-06-09)

- [x] Перенести документацию в `docs/`
- [x] Реорганизовать `tools/` по подпапкам
- [x] Починить `check-links.py`, `find-orphans.py`
- [x] Создать `check-religionisms.py`, `check-code-quality.py`, `clear-cache.py`
- [x] Создать `check-metadata-consistency.py`, `check-empty-files.py`, `check-tahor-sync.py`
- [x] Создать `consistency-checker.py`, `check-merge-conflicts.py`, `fix-metadata-fields.py`
- [x] Создать `unify-metadata.py`, `validate-external-links.py`, `check-file-sizes.py`
- [x] Создать `tools/lib/utils.py`
- [x] Обновить `golem.py` до v3.9
- [x] Удалить `SCTRUCTURE.md`, `substitution-of-the-name` без `.md`, `COMPLETED-TASKS.*`
- [x] Обновить `docs/CHANGELOG.md`, `docs/BACKLOG.md`, `docs/DECISIONS.md`, `docs/RETROSPECTIVE.md`, `docs/ROADMAP.md`
- [x] Исправить `sync-structure.py`, `generate-glossary.py` (убрать `progress`)
- [x] Исправить `task-manager.py` (путь к `docs/TECHNICAL-DEBT.md`)

---

## ✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ (ранние)

### 2026-05-28

- [x] Разделить `exposure-principles.md` на три файла
- [x] Создать папку `instructions/exposure/`
- [x] Обновить `README.md`, `structure.md`, `chat-prompt.md`

### 2026-06-01

- [x] Создать `exposure-distortions.md`
- [x] Создать `checkers/mivdak.md`

### 2026-06-02

- [x] Создать `researches/yehoshua-research.md`, `derech-ha-gever.md`, `derech-ha-nachash.md`
- [x] Создать термины `yetzer-lev.md`, обновить `cherut.md`

### 2026-06-06

- [x] Исправить метаданные, имена файлов, транслитерацию, битые ссылки