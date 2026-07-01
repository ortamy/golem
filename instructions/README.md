# 📜 ПАПКА INSTRUCTIONS

**Описание:** Методология и инструкции проекта «ГОЛЕМ»

---

## 📂 СТРУКТУРА

### Корневые файлы
- `manifest.md` - манифест проекта
- `research-principles.md` - 38 принципов исследований
- `image-map.md` - карта изображений
- `images-catalogue.md` - каталог изображений
- `release-process.md` - процесс релиза

### Подпапки

#### agent/ - 🤖 Инструкции для агента
Инструкции и промпты для автономного агента

**Файлы:**
- `AGENT-PROMPT.md` - промпт для агента
- `AGENT-ROUTINE.md` - рутина агента
- `AGENT-RETROSPECTIVE.md` - ретроспектива агента
- `AUDIT-SYSTEM.md` - система аудита
- `AUDIT-REPORT.md` - отчёт аудита

**Назначение:** Документация и инструкции для работы автономного агента

---

#### assistant/ - 💬 Инструкции для ассистента
Инструкции для ассистента проекта

**Файлы:**
- `ASSISTANT-CHAT-PROMPT.md` - чат-промпт
- `ASSISTANT-ROUTINE.md` - рутина ассистента
- `ASSISTANT-RETROSPECTIVE.md` - ретроспектива ассистента

**Назначение:** Документация для ассистента проекта

---

#### checkers/ - ✅ Инструкции чекеров
Инструкции для скриптов проверок

**Файлы:**
- `check-bdikah.md` - проверка бдительности
- `check-consistency.md` - проверка консистентности
- `check-fact.md` - проверка фактов
- `check-mivdak.md` - проверка мивдака
- `check-startup.md` - проверка стартапа
- `check-tahor.md` - проверка тахора
- `check-tikun.md` - проверка тикуна

**Назначение:** Методологические инструкции для чекеров

---

#### dictionaries/ - 📚 Словари
Словари для проверок (запрещённые слова)

**Файлы:**
- `dictionaries-economisms.md` - экономинимы
- `dictionaries-estethisms.md` - эстетизмы
- `dictionaries-gastronomisms.md` - гастрономизмы
- `dictionaries-grecisms.md` - грецизмы
- `dictionaries-juridisms.md` - юридизмы
- `dictionaries-latinisms.md` - латинизмы
- `dictionaries-marketisms.md` - маркетингизмы
- `dictionaries-mediasms.md` - медиасмы
- `dictionaries-medicinisms.md` - медицинизмы
- `dictionaries-militarisms.md` - милитаризмы
- `dictionaries-modernisms.md` - модернизмы
- `dictionaries-names.md` - имена
- `dictionaries-newageisms.md` - нью-эйджизмы
- `dictionaries-phrases.md` - фразы
- `dictionaries-politisms.md` - политизмы
- `dictionaries-psychologisms.md` - психологизмы
- `dictionaries-religionims.md` - религионимы
- `dictionaries-scientisms.md` - scientизмы
- `dictionaries-slavicisms.md` - славянизмы
- `dictionaries-sportisms.md` - спортизмы
- `dictionaries-technologisms.md` - технологизмы

**Назначение:** Центральный источник запрещённых слов для проверок

---

#### exposure/ - ⚠️ Методы разоблачения
Методы разоблачения систем и искажений

**Файлы:**
- `exposure-principles.md` - принципы разоблачения
- `exposure-methods.md` - 29 методов
- `exposure-mechanisms.md` - 5 механизмов
- `exposure-techniques.md` - 60+ приёмов
- `exposure-distortions.md` - 7 типов искажений
- `exposure-language.md` - язык контроля
- `exposure-linguistic-methods.md` - лингвистические методы
- `exposure-dictionary.md` - словарь
- `exposure-philosophemes.md` - философемы
- `exposure-religionism-theory.md` - теория религионизма
- `exposure-system-architecture.md` - архитектура систем
- `exposure-bavel.md` - Вавилон

**Назначение:** Методология разоблачения систем контроля

---

#### methodology/ - 📐 Методология
Методология исследований

**Файлы:**
- `methodology-archeology.md` - археология
- `methodology-hebrew-reconstruction.md` - реконструкция иврита
- `methodology-translation.md` - перевод
- `methodology-transliteration.md` - транслитерация
- `methodology-tree.md` - дерево знаний

**Назначение:** Методологические принципы исследований

---

#### templates/ - 📄 Шаблоны
Шаблоны файлов проекта

**Файлы:**
- `TEMPLATE-BOOK.md` - шаблон книги
- `TEMPLATE-CONCEPT-ANALYSIS.md` - шаблон анализа концепции
- `TEMPLATE-EVENT.md` - шаблон события
- `TEMPLATE-EXPOSURE.md` - шаблон разоблачения
- `TEMPLATE-LEARN.md` - шаблон обучения
- `TEMPLATE-PERSON.md` - шаблон личности
- `TEMPLATE-PRACTICE.md` - шаблон практики
- `TEMPLATE-RESEARCH.md` - шаблон исследования
- `TEMPLATE-SELF-LEARNING.md` - шаблон самообучения
- `TEMPLATE-TEACHING.md` - шаблон учения
- `TEMPLATE-TERM.md` - шаблон термина
- `TEMPLATE-TZEL.md` - шаблон тзель

**Назначение:** Стандартизация формата файлов

---

#### tools/ - 🛠 Инструкции для инструментов
Инструкции для работы с инструментами

**Назначение:** Документация по инструментам проекта

---

## 🔗 СВЯЗИ

### Внутренние связи
- `dictionaries/` → `tools/checkers/` - словари используются чекерами
- `exposure/` → `content/exposed/` - методы применяются в контенте
- `templates/` → `content/` - шаблоны для создания контента
- `methodology/` → `content/researches/` - методология для исследований

### Внешние связи
- `docs/` - документация
- `tools/` - инструменты
- `content/` - контент

---

## 📝 ПРАВИЛА

1. **Метаданные:** все инструкции должны иметь метаданные
2. **Версионирование:** изменения фиксировать в истории
3. **Ссылки:** использовать относительные пути
4. **Согласованность:** инструкции должны соответствовать ARCHITECTURE.md

---

## 🛠 ИСПОЛЬЗОВАНИЕ

### Для чекеров
```bash
# Чекеры используют dictionaries/ для проверок
python tools/checkers/check-religionisms.py
```

### Для создания контента
```bash
# Использовать templates/ для новых файлов
cp instructions/templates/TEMPLATE-RESEARCH.md content/researches/new-research.md
```

### Для методологии
```bash
# Следовать methodology/ при проведении исследований
```

---

## 📊 СТАТИСТИКА

- **Корневых файлов:** 5
- **agent/:** 5 файлов
- **assistant/:** 3 файла
- **checkers/:** 7 файлов
- **dictionaries/:** 21 файл
- **exposure/:** 12 файлов
- **methodology/:** 5 файлов
- **templates/:** 12 файлов
- **tools/:** инструкции

---

## 🔗 НАВИГАЦИЯ

- [README.md](../README.md) - главная страница
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - архитектура проекта
- [docs/STRUCTURE.md](../docs/STRUCTURE.md) - полная структура

### По подпапкам
- [agent/](agent/) - инструкции для агента
- [assistant/](assistant/) - инструкции для ассистента
- [checkers/](checkers/) - инструкции чекеров
- [dictionaries/](dictionaries/) - словари
- [exposure/](exposure/) - методы разоблачения
- [methodology/](methodology/) - методология
- [templates/](templates/) - шаблоны
- [tools/](tools/) - инструкции для инструментов