# 📜 ТЕХНИЧЕСКИЙ ДОЛГ

**Метаданные файла**
- **Файл:** `TECHNICAL-DEBT.md`
- **Версия:** 1.3
- **Дата создания:** 2026-05-28
- **Последнее обновление:** 2026-06-08
- **Причина обновления:** Добавлены задачи по анализу репозитория: конфликты слияния, унификация checkers, системные проблемы
- **Статус:** Активный

---

## 📋 АКТИВНЫЕ ЗАДАЧИ

### Вычистить конфликты слияния Git (10 файлов)

- [ ] `instructions/image-map.md` — убрать `<<<<<<< HEAD` / `>>>>>>>`
- [ ] `instructions/images-catalogue.md` — убрать конфликт
- [ ] `instructions/methodology/archeology-methodology.md` — убрать конфликт
- [ ] `instructions/methodology/hebrew-reconstruction.md` — убрать конфликт
- [ ] `instructions/methodology/translation-methodology.md` — убрать конфликт
- [ ] `instructions/methodology/transliteration-distortions.md` — убрать конфликт
- [ ] `instructions/methodology/tree-method.md` — убрать конфликт
- [ ] `instructions/checkers/bdikah-checker.md` — убрать конфликт
- [ ] `instructions/checkers/factcheck.md` — убрать конфликт
- [ ] `instructions/checkers/mivdak.md` — убрать конфликт
- [ ] `CHANGELOG.md` — убрать конфликт в конце файла

### Унифицировать папку checkers

- [ ] Выбрать единую папку: `checkers/` или `instructions/checkers/`
- [ ] Перенести все чекеры в выбранную папку
- [ ] Обновить ссылки на чекеры в `chat-prompt.md`, `workflow.md`, `startup-checklist.md`
- [ ] Обновить `STRUCTURE.md`

### Сократить chat-prompt.md

- [ ] Вынести детали в отдельные файлы
- [ ] Оставить только ядро: источник, имя, запреты, процесс, тон
- [ ] Обновить ссылки на новые файлы

### Создать новые файлы

- [ ] `terminology/midbar.md` — מִדְבָּר (пустыня). Пустыня как экзамен, а не наказание.
- [ ] `terminology/levad.md` — לְבַד (один). Способность быть одному как признак свободы.
- [ ] `terminology/arum.md` — עָרוּם (хитрый, проницательный). Связь с эйром.
- [ ] `terminology/nachash.md` — נָּחָשׁ (змей). Мудрость, которая действует тихо.
- [ ] `terminology/pachad.md` — פַּחַד (страх). Создать файл.
- [ ] `terminology/erech-apayim.md` — אֶרֶךְ אַפַּיִם (долгое дыхание). Создать файл.
- [ ] `terminology/yetzer-lev.md` — יֵצֶר לֵב (помышление сердца). Создать файл.
- [ ] `terminology/gibor.md` — גִּבּוֹר (сильный). Создать файл.
- [ ] `terminology/shabbat.md` — שַׁבָּת (Шаббат). Создать файл.
- [ ] `terminology/tohu-va-vohu.md` — תֹּהוּ וָבֹהוּ (пустота и безвидность). Создать файл.
- [ ] `researches/galatim-two-systems.md` — Галатим: война двух систем
- [ ] `researches/substitution-of-the-name.md` — кража Имени

### Заполнить пустые файлы

- [ ] `researches/galatim-two-systems.md` — убрать TODO
- [ ] `terminology/yetzer-lev.md` — убрать TODO
- [ ] `terminology/erech-apayim.md` — убрать TODO

### Системные проблемы

- [ ] Исправить `immanu-el.md` — в метаданных `researches/`, файл в `terminology/`
- [ ] Проверить все файлы `terminology/` на правильность папки в метаданных
- [ ] Создать `requirements.txt` для Python-инструментов в `tools/`
- [ ] Удалить `SCTRUCTURE.md` (опечатка, дубликат `STRUCTURE.md`)
- [ ] Удалить файл `substitution-of-the-name` без расширения `.md`
- [ ] Проверить дубликаты: `or-tam.md`, `sheerit.md`, `platform-idea.md`, `davar-language.md`, `RETROSPECTIVE.md`
- [ ] Обновить `STRUCTURE.md`

### Обновить существующие файлы

- [ ] `chat-prompt.md` — обновить ссылки на новые файлы
- [ ] `README.md` — обновить количество файлов

---

## ✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ

### 2026-05-28

- [x] Разделить `exposure-principles.md` на три файла
- [x] Создать папку `instructions/exposure/`
- [x] Создать `exposure/exposure-principles.md`
- [x] Создать `exposure/exposure-methods.md`
- [x] Создать `exposure/exposure-mechanisms.md`
- [x] Убрать `channel/` из структуры репозитория
- [x] Обновить `README.md` (v2.1)
- [x] Обновить `structure.md` (v1.2)
- [x] Создать `drafts/ideas.md`
- [x] Создать `drafts/questions.md`
- [x] Создать `drafts/notes.md`
- [x] Обновить `chat-prompt.md` (v1.3)
- [x] Создать `image-map-template.md` (v1.1)
- [x] Создать `self-learning-template.md` (v1.0)
- [x] Создать `neural-network-plan.md` (v1.0)

### 2026-06-01

- [x] Разделить `exposure-principles.md` на три файла: принципы, методы, механизмы
- [x] Создать папку `instructions/exposure/`
- [x] Создать `exposure/exposure-principles.md`
- [x] Создать `exposure/exposure-methods.md`
- [x] Создать `exposure/exposure-mechanisms.md`
- [x] Обновить `exposure-methods.md` до v1.1 (+3 метода)
- [x] Обновить `exposure-mechanisms.md` до v1.1 (+9 приёмов)
- [x] Обновить `exposure-mechanisms.md` до v1.2 (+дуализация, комбинации, remedies)
- [x] Создать `exposure-distortions.md` — 7 типов искажений с приёмами
- [x] Удалить старый `instructions/exposure-principles.md`
- [x] Создать `instructions/templates/` и `concept-analysis-template.md`
- [x] Создать `archeology-methodology.md`
- [x] Создать `drafts/technical-debt.md`
- [x] Создать `checkers/mivdak.md` — полный цикл аудита
- [x] Обновить `chat-prompt.md` до v1.5
- [x] Обновить `forbidden-words.md` до v1.2

### 2026-06-02

- [x] Создать `researches/yehoshua-research.md` — историческое расследование
- [x] Создать `terminology/yetzer-lev.md` — помышление сердца
- [x] Создать `researches/derech-ha-gever.md` — путь мужчины
- [x] Создать `researches/derech-ha-nachash.md` — путь змея
- [x] Обновить `terminology/cherut.md` до v2.0 — свобода для верности

### 2026-06-06 — Автоматические исправления

- [x] Исправить метаданные во всех файлах
- [x] Исправить имена файлов (строчные буквы, дефисы)
- [x] Исправить транслитерацию (Яхве, эмет, хесед, руах, нэфеш)
- [x] Исправить битые ссылки
- [x] Создать `COMPLETED-TASKS.md`
- [x] Обновить `CHANGELOG.md`