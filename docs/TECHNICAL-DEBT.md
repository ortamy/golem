# 📜 ТЕХНИЧЕСКИЙ ДОЛГ

**Метаданные файла**
- **Файл:** `docs/TECHNICAL-DEBT.md`
- **Версия:** 1.4
- **Дата создания:** 2026-05-28
- **Последнее обновление:** 2026-06-08
- **Причина обновления:** Перенос в docs/, удалены выполненные задачи, актуализирован список
- **Статус:** Активный
- **Тема:** ТЕХНИЧЕСКИЙ ДОЛГ
---

## 📋 АКТИВНЫЕ ЗАДАЧИ

### Вычистить конфликты слияния Git (10 файлов)

- [ ] `instructions/image-map.md`
- [ ] `instructions/images-catalogue.md`
- [ ] `instructions/methodology/archeology-methodology.md`
- [ ] `instructions/methodology/hebrew-reconstruction.md`
- [ ] `instructions/methodology/translation-methodology.md`
- [ ] `instructions/methodology/transliteration-distortions.md`
- [ ] `instructions/methodology/tree-method.md`
- [ ] `instructions/checkers/bdikah-checker.md`
- [ ] `instructions/checkers/factcheck.md`
- [ ] `instructions/checkers/mivdak.md`

### Унифицировать папку checkers

- [ ] Выбрать единую папку: `tools/checkers/` или `instructions/checkers/`
- [ ] Перенести `.md`-чекеры в выбранную папку
- [ ] Обновить ссылки в `chat-prompt.md`, `workflow.md`, `startup-checklist.md`

### Сократить chat-prompt.md

- [ ] Вынести детали в отдельные файлы
- [ ] Оставить только ядро: источник, имя, запреты, процесс, тон

### Создать новые файлы

- [ ] `terminology/midbar.md` — מִדְבָּר (пустыня)
- [ ] `terminology/levad.md` — לְבַד (один)
- [ ] `terminology/arum.md` — עָרוּם (хитрый)
- [ ] `terminology/nachash.md` — נָּחָשׁ (змей)
- [ ] `terminology/pachad.md` — פַּחַד (страх)
- [ ] `researches/galatim-two-systems.md` — Галатим: война двух систем
- [ ] `researches/substitution-of-the-name.md` — кража Имени

### Заполнить пустые файлы

- [ ] `researches/galatim-two-systems.md`
- [ ] `terminology/yetzer-lev.md`
- [ ] `terminology/erech-apayim.md`

### Системные проблемы

- [ ] Исправить `immanu-el.md` — в метаданных `researches/`, файл в `terminology/`
- [ ] Проверить все файлы `terminology/` на правильность папки в метаданных
- [ ] Создать `requirements.txt` для `tools/`
- [ ] Проверить дубликаты: `or-tam.md`, `sheerit.md`, `platform-idea.md`, `davar-language.md`
- [ ] Проверить работоспособность всех скриптов в подпапках `tools/`

### Обновить существующие файлы

- [ ] `chat-prompt.md` — обновить ссылки
- [ ] `README.md` — обновить статистику

---

## ✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ (2026-06-07 — 2026-06-08)

- [x] Перенести документацию в `docs/`
- [x] Реорганизовать `tools/` по подпапкам
- [x] Починить `check-links.py`, `find-orphans.py`
- [x] Создать `check-religionisms.py`, `check-code-quality.py`, `clear-cache.py`
- [x] Создать `tools/lib/utils.py`
- [x] Обновить `golem.py` до v3.5
- [x] Удалить `SCTRUCTURE.md`
- [x] Удалить `substitution-of-the-name` без `.md`
- [x] Удалить `COMPLETED-TASKS.md` и `COMPLETED-TASKS.json`
- [x] Обновить `docs/CHANGELOG.md`, `docs/BACKLOG.md`, `docs/DECISIONS.md`, `docs/RETROSPECTIVE.md`, `docs/ROADMAP.md`

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