# 📜 СТРУКТУРА ПРОЕКТА — ЭТАЛОН РЕСТРУКТУРИЗАЦИИ

**Метаданные файла**
- **Файл:** `docs/STRUCTURE-REFERENCE.md`
- **Версия:** 1.0
- **Дата создания:** 2026-07-04
- **Статус:** Активный
- **Тема:** Эталонная структура проекта «Голем» для аудита, реструктуризации и размещения новых файлов.
- **Связанные файлы:** `docs/ARCHITECTURE.md`, `instructions/products/website.md`, `instructions/products/webapp.md`, `instructions/products/research-lab.md`

---

## 🔥 ПРИНЦИПЫ

- **Сайт (`products/website/`)** — статический портал. Всё, что видит пользователь, идёт отсюда.
- **Приложение (`products/webapp/`)** — инструменты, редакторы, чат, лаборатория.
- **Контент (`content/`)** — все md-файлы (исследования, термины, ТаНаХ, разоблачения).
- **Данные (`data/`)** — все JSON-файлы и кэш.
- **Инструкции (`instructions/`)** — методология, шаблоны, промпты, описания продуктов, инструкции для агентов.
- **Документация (`docs/`)** — для человека: архитектура, структура, роадмап, глоссарий.
- **Инструменты (`tools/`)** — скрипты (Python, JS) для проверок, генерации, автоматизации.

---

## 🏛 ЭТАЛОННАЯ СТРУКТУРА

```
golem/
  docs/
    ARCHITECTURE.md
    STRUCTURE.md
    ROADMAP.md
    CHANGELOG.md
    GLOSSARY.md
    STRUCTURE-REFERENCE.md

  content/
    researches/
    terminology/
    tanakh/
    exposed/
    bashah/
    foundations/

  instructions/
    methodology/
    templates/
    exposure/
    tahor/
    products/
    agents/

  data/
    tanakh-cache/
    religious-dictionary.json
    tanakh-books.json

  tools/
    checkers/
    generators/
    reports/
    automation/

  products/
    website/
      pages/
      tools/
      assets/
        images/
        icons/
        fonts/
      css/
      js/
      ru/
      en/
      he/

    webapp/
      modules/
      css/
      js/
      index.html

  README.md
```

---

## 🔍 КРИТЕРИИ ПРОВЕРКИ (для нейросети)

При каждом аудите проверять:

1. **Папки:** все ли папки из эталона существуют.
2. **Файлы:** не лежат ли файлы не в своих папках (например, .md в корне `products/website/`).
3. **Дубликаты:** нет ли одинаковых или похожих файлов в разных папках.
4. **Пустоты:** нет ли папок, которые должны быть наполнены, но пусты.
5. **Языки:** синхронизированы ли `ru/`, `en/`, `he/`.

---

## 🛠 КАК ИСПОЛЬЗОВАТЬ

**Для Cline/агента:**
- Запускать аудит по команде: `проверить структуру по STRUCTURE-REFERENCE.md`
- Выдавать отчёт: что не совпадает, что нужно переместить, что удалить.

**Для человека:**
- Использовать как карту, чтобы знать, куда класть новые файлы.
- Сверяться при реструктуризации.

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ

- `docs/ARCHITECTURE.md`
- `instructions/products/website.md`
- `instructions/products/webapp.md`
- `instructions/products/research-lab.md`