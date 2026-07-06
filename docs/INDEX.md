# 📑 ИНДЕКС DOCS

**Описание:** Индекс всей документации проекта «ГОЛЕМ»

---

## 📊 СТАТИСТИКА

- **Всего файлов:** 20+
- **Папок:** 1
- **Последнее обновление:** 2026-07-01

---

## 📚 ОСНОВНАЯ ДОКУМЕНТАЦИЯ

### Архитектура и структура
- [ARCHITECTURE.md](ARCHITECTURE.md) - архитектура проекта
- [STRUCTURE.md](STRUCTURE.md) - полная структура репозитория
- [INDEX.md](INDEX.md) - этот файл

### Управление проектом
- [BACKLOG.md](BACKLOG.md) - текущие задачи
- [ROADMAP.md](ROADMAP.md) - дорожная карта
- [TECHNICAL-DEBT.md](TECHNICAL-DEBT.md) - технический долг
- [DECISIONS.md](DECISIONS.md) - журнал решений
- [RETROSPECTIVE.md](RETROSPECTIVE.md) - ретроспектива

### Контент и изменения
- [CHANGELOG.md](CHANGELOG.md) - история изменений
- [CONTRIBUTORS.md](CONTRIBUTORS.md) - контрибьюторы
- [GLOSSARY.md](GLOSSARY.md) - глоссарий терминов
- [GLOSSARY-DEVELOPMENT.md](GLOSSARY-DEVELOPMENT.md) - глоссарий разработки

### Специальные документы
- [GRAPH.md](GRAPH.md) - граф проекта
- [IDEAS.md](IDEAS.md) - идеи проекта
- [STATS.md](STATS.md) - статистика
- [STRATEGY.md](STRATEGY.md) - стратегия
- [CONTROL.md](CONTROL.md) - контроль проекта

---

## 📂 КАТЕГОРИИ

### Проектная документация
- ARCHITECTURE.md - архитектура
- STRUCTURE.md - структура
- ROADMAP.md - дорожная карта
- BACKLOG.md - задачи
- DECISIONS.md - решения
- RETROSPECTIVE.md - ретроспектива

### Техническая документация
- TECHNICAL-DEBT.md - технический долг
- CHANGELOG.md - изменения
- CONTRIBUTORS.md - контрибьюторы
- GLOSSARY.md - глоссарий
- GRAPH.md - граф

### Продуктовая документация
> Документация продуктов находится в `products/` и `instructions/products/`.

### Методологическая документация
- STRATEGY.md - стратегия
- IDEAS.md - идеи
- STATS.md - статистика
- CONTROL.md - контроль

---

## 🔗 СВЯЗИ

### Внешние связи
- [README.md](../README.md) - главная страница
- [content/](../content/) - контент
- [products/](../products/) - продукты
- [tools/](../tools/) - инструменты
- [instructions/](../instructions/) - методология
- [guides/](../guides/) - руководства

---

## 📝 ПРАВИЛА

1. **Метаданные:** каждый файл должен иметь метаданные
2. **Версионирование:** изменения фиксировать в CHANGELOG.md
3. **Ссылки:** использовать относительные пути
4. **Согласованность:** документация должна соответствовать ARCHITECTURE.md

---

## 🛠 ИСПОЛЬЗОВАНИЕ

### Для разработчиков
```bash
# Начать с ARCHITECTURE.md
# Затем STRUCTURE.md
# Затем ROADMAP.md
```

### Для контрибьюторов
```bash
# Прочитать CONTRIBUTORS.md
# Изучить DECISIONS.md
# Проверить BACKLOG.md
```

### Для пользователей
```bash
# Начать с README.md
# Затем GLOSSARY.md
# Затем guides/
```

---

## 📊 СТАТИСТИКА

- **Всего документов:** 20+
- **Архитектура:** 3 файла
- **Управление:** 5 файлов
- **Контент:** 4 файла
- **Продукты:** 5 файлов
- **Методология:** 3 файла

---

## 🔗 НАВИГАЦИЯ

- [README.md](../README.md) - главная страница
- [ARCHITECTURE.md](ARCHITECTURE.md) - архитектура проекта
- [STRUCTURE.md](STRUCTURE.md) - полная структура

### По категориям
- [ARCHITECTURE.md](ARCHITECTURE.md) - архитектура
- [STRUCTURE.md](STRUCTURE.md) - структура
- [CHANGELOG.md](CHANGELOG.md) - изменения
- [BACKLOG.md](BACKLOG.md) - задачи
- [ROADMAP.md](ROADMAP.md) - дорожная карта
- [TECHNICAL-DEBT.md](TECHNICAL-DEBT.md) - технический долг
- [DECISIONS.md](DECISIONS.md) - решения
- [RETROSPECTIVE.md](RETROSPECTIVE.md) - ретроспектива
- [GLOSSARY.md](GLOSSARY.md) - глоссарий
- [CONTRIBUTORS.md](CONTRIBUTORS.md) - контрибьюторы
- [STRATEGY.md](STRATEGY.md) - стратегия
- [IDEAS.md](IDEAS.md) - идеи
- [STATS.md](STATS.md) - статистика
- [GRAPH.md](GRAPH.md) - граф
- [CONTROL.md](CONTROL.md) - контроль
- [GLOSSARY-DEVELOPMENT.md](GLOSSARY-DEVELOPMENT.md) - глоссарий разработки

---

## 📝 ПРИМЕЧАНИЯ

1. **Полнота:** индекс содержит все документы docs/
2. **Актуальность:** обновляется при добавлении новых документов
3. **Структура:** organised по категориям
4. **Ссылки:** все ссылки рабочие
5. **Поиск:** использовать Ctrl+F для быстрого поиска

---

## 🛠 ОБНОВЛЕНИЕ ИНДЕКСА

```bash
# Автоматическое обновление индекса
python tools/generators/generate-index.py --docs