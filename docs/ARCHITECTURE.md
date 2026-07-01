# 🏛 АРХИТЕКТУРА ПРОЕКТА «ГОЛЕМ»

**Метаданные файла**
- **Файл:** `docs/ARCHITECTURE.md`
- **Версия:** 2.0
- **Дата создания:** 2026-06-09
- **Последнее обновление:** 2026-07-01
- **Причина обновления:** Обновление структуры под реальную файловую систему
- **Статус:** Активный
- **Тема:** Архитектура проекта — структура, связи, поток данных

---

## 🔥 ОБЩАЯ СХЕМА

```
golem/                          # корень репозитория
├── README.md                   # лицо проекта
├── requirements.txt            # зависимости Python
├── .gitignore                  # исключения Git
│
├── docs/                       # 📚 документация проекта
│   ├── CHANGELOG.md            # история изменений
│   ├── STRUCTURE.md            # структура репозитория
│   ├── BACKLOG.md              # текущие задачи
│   ├── ROADMAP.md              # дорожная карта
│   ├── TECHNICAL-DEBT.md       # технический долг
│   ├── DECISIONS.md            # журнал решений
│   ├── RETROSPECTIVE.md        # ретроспектива
│   ├── GLOSSARY.md             # глоссарий терминов
│   ├── ARCHITECTURE.md         # этот файл
│   ├── INDEX.md                # индекс всех файлов
│   └── [другие .md файлы]
│
├── content/                    # 📦 основной контент
│   ├── terminology/            # 📖 разбор ивритских терминов (100+)
│   ├── tanakh/                 # 📜 Танах (книги, события, личности)
│   ├── bashah/                 # ✝️ Башах (Брита Хадаша)
│   ├── hebrew/                 # 🔤 ивритский язык
│   ├── researches/             # 🔬 исследования по темам
│   ├── teachings/              # 📚 учения, религии, философии (250+)
│   ├── practices/              # ✅ практики
│   ├── exposed/                # ⚠️ разоблачения
│   └── tzel/                   # 🎭 тзель (типы, parallelism)
│
├── products/                   # 🚀 продукты
│   ├── agent/                  # агент
│   ├── assistant/              # ассистент
│   ├── davar/                  # язык Давар
│   ├── neuro/                  # нейросеть Эд
│   ├── tanakh/                 # Танах-продукт
│   ├── telegram-bot/           # Telegram бот
│   ├── webapp/                 # веб-приложение
│   ├── website/                # веб-сайт
│   └── golem-os/               # Golem OS
│
├── tools/                      # 🛠 инструменты
│   ├── golem.py                # главное меню
│   ├── checkers/               # скрипты проверок
│   ├── generators/             # генерация файлов
│   ├── reports/                # отчёты
│   ├── automation/             # автоматизация
│   ├── backup/                 # бэкап
│   ├── lib/                    # общие утилиты
│   ├── utils/                  # вспомогательные утилиты
│   ├── data/                   # данные для инструментов
│   ├── sync/                   # синхронизация
│   └── [отдельные .py скрипты]
│
├── instructions/               # 📜 методология и инструкции
│   ├── manifest.md             # манифест проекта
│   ├── research-principles.md  # 38 принципов исследований
│   ├── image-map.md            # карта изображений
│   ├── images-catalogue.md     # каталог изображений
│   ├── release-process.md      # процесс релиза
│   ├── agent/                  # инструкции для агента
│   ├── assistant/              # инструкции для ассистента
│   ├── checkers/               # инструкции чекеров
│   ├── dictionaries/           # словари (экономинимы, грецизмы и т.д.)
│   ├── exposure/               # методы разоблачения
│   ├── methodology/            # методология исследований
│   ├── templates/              # шаблоны файлов
│   └── tools/                  # инструкции для инструментов
│
├── guides/                     # 📖 руководства пользователя
│   ├── GUIDE-AGENT.md
│   ├── GUIDE-ASSISTANT.md
│   ├── GUIDE-AUDIT.md
│   ├── GUIDE-CHECKERS.md
│   ├── GUIDE-CLINE.md
│   ├── GUIDE-CODING.md
│   ├── GUIDE-COLLABORATION.md
│   ├── GUIDE-CONTRIBUTING.md
│   ├── GUIDE-DAVAR.md
│   ├── GUIDE-DEPLOY.md
│   ├── GUIDE-EXPOSURE.md
│   ├── GUIDE-FAQ.md
│   ├── GUIDE-GIT.md
│   ├── GUIDE-ICONS.md
│   ├── GUIDE-NEURO.md
│   ├── GUIDE-ONBOARDING.md
│   ├── GUIDE-SCRIPTS.md
│   ├── GUIDE-SEARCH.md
│   ├── GUIDE-SECURITY.md
│   ├── GUIDE-SETUP.md
│   ├── GUIDE-TERMINOLOGY.md
│   ├── GUIDE-TESTING.md
│   ├── GUIDE-TROUBLESHOOTING.md
│   ├── GUIDE-WORKFLOW-RESEARCH.md
│   └── GUIDE-WRITTING.md
│
├── ideas/                      # 💡 идеи и предложения
│   ├── additional-files.md
│   ├── api-design.md
│   ├── bashah-project.md
│   ├── cli-checkers.md
│   ├── countries-checker.md
│   ├── database-schema.md
│   ├── gamification.md
│   ├── neural-network-plan.md
│   ├── paleo-hebrew-dictionary.md
│   ├── platform-idea.md
│   ├── project-agent.md
│   ├── scripts-idea.md
│   ├── search-engine.md
│   ├── tree-visualization.md
│   ├── ux-ui-improvements.md
│   ├── visualization-tool.md
│   └── web-interface.md
│
├── data/                       # 🗄️ данные
│   ├── lxx.json                # Септуагинта
│   ├── qumran.json             # Мёртвое море
│   ├── tanakh-books.json       # книги Танаха
│   ├── translation.json        # переводы
│   └── tanakh-cache/           # кэш Танаха
│
├── backlog/                    # 📋 задачи и идеи
│   ├── ideas.md
│   ├── notes.md
│   └── questions.md
│
├── archive/                    # 🗄️ архив
│   └── digital-web.png
│
└── reports/                    # 📊 отчёты
    └── researches-report.txt
```

---

## 🔄 ПОТОК ДАННЫХ

### Путь исследования
```
Идея → ideas/ → drafts/ → content/researches/ → проверка чекерами → публикация
```

### Путь термина
```
Ивритское слово → content/terminology/ → docs/GLOSSARY.md → перекрёстные ссылки
```

### Полный цикл проверки одного файла
```
Новый файл
  ↓
check-naming.py          (имя корректно?)
  ↓
validate-metadata.py     (метаданные в порядке?)
  ↓
check-religionisms.py    (религионимы исправлены?)
  ↓
check-links.py           (ссылки не битые?)
  ↓
unify-metadata.py        (метаданные по шаблону?)
  ↓
sync-structure.py        (STRUCTURE.md обновлён?)
  ↓
✅ Файл готов
```

---

## 🗂 СВЯЗИ МЕЖДУ ПАПКАМИ

```
content/terminology/  ←────────────── content/researches/
(термины)                    (ссылаются на термины)
    │                              │
    └──────────┬───────────────────┘
                ↓
         instructions/exposure/
         (методы разоблачения)
                ↓
         instructions/dictionaries/
         (словари для проверок)
                ↓
         tools/checkers/
         (скрипты используют словари)
                ↓
         docs/
         (документация по скриптам)
```

---

## ⚙️ КЛЮЧЕВЫЕ КОМПОНЕНТЫ

### Метаданные
Каждый md-файл содержит блок метаданных. Обязательные поля: Файл, Версия, Дата создания, Последнее обновление, Причина обновления, Статус, Тема. Дополнительные: Аудит (статус 4 проверок), Хеш (для отслеживания изменений), Связанные файлы, Проверок на религионизмы, Достоверность.

### Словари `instructions/dictionaries/`
Центральный источник запрещённых слов. Используются скриптами: `check-religionisms.py` для замены, `check-tahor-sync.py` для синхронизации, `check-exposure.py` для маркеров искажений.

### Меню
`tools/golem.py` автоматически находит все скрипты в подпапках `checkers/`, `generators/`, `reports/`, `automation/`. Новый скрипт в любой из этих папок появляется в меню без правки кода.

### Продукты
Папка `products/` содержит рабочие продукты проекта:
- **agent/** - автономный агент
- **assistant/** - ассистент
- **davar/** - язык программирования Давар
- **neuro/** - нейросеть Эд
- **tanakh/** - продукт по Танаху
- **telegram-bot/** - Telegram бот
- **webapp/** - веб-приложение
- **website/** - статический сайт
- **golem-os/** - операционная система Голем

### Данные
Папка `data/` содержит структурированные данные в JSON:
- **lxx.json** - Септуагинта
- **qumran.json** - Мёртвое море
- **tanakh-books.json** - книги Танаха
- **translation.json** - переводы
- **tanakh-cache/** - кэш данных Танаха

---

## 🔐 ПРИНЦИПЫ АРХИТЕКТУРЫ

1. **Единый источник истины:** словари `instructions/dictionaries/` — все проверки берут данные оттуда
2. **Автоматическое обнаружение:** новые скрипты автоматически появляются в меню
3. **Монолитность:** каждый md-файл — один блок, копируется одним нажатием
4. **Разделение ответственности:** чекеры проверяют, генераторы создают, автоматизация управляет
5. **Модульность:** продукты изолированы в папке `products/`
6. **Данные отдельно:** структурированные данные хранятся в `data/` отдельно от контента

---

## 📋 СТРУКТУРА КОНТЕНТА

### content/
Основной контент проекта organised по типам:

- **terminology/** - 100+ ивритских терминов с разбором
- **tanakh/** - Танах (книги, события, личности, учения)
- **bashah/** - Брита Хадаша (Новый Завет)
- **hebrew/** - изучение иврита
- **researches/** - исследования по различным темам
- **teachings/** - 250+ файлов с разбором учений, религий, философий
- **practices/** - практики
- **exposed/** - разоблачения
- **tzel/** - тзель (типы, параллелизм)

### products/
Рабочие продукты, которые можно деплоить:

- **agent/** - автономный агент
- **assistant/** - ассистент
- **davar/** - язык Давар
- **neuro/** - нейросеть Эд
- **tanakh/** - веб-продукт по Танаху
- **telegram-bot/** - бот для Telegram
- **webapp/** - веб-приложение
- **website/** - статический сайт
- **golem-os/** - операционная система

---

## 🛠 ИНСТРУМЕНТЫ

### tools/
Скрипты для работы с проектом:

- **golem.py** - главное меню
- **checkers/** - 19+ скриптов проверок
- **generators/** - 10+ генераторов файлов
- **reports/** - 4+ генератора отчётов
- **automation/** - 5+ скриптов автоматизации
- **backup/** - 2+ скрипта бэкапа
- **lib/** - общие утилиты
- **utils/** - вспомогательные утилиты
- **data/** - данные для инструментов
- **sync/** - синхронизация

---

## 📖 ДОКУМЕНТАЦИЯ

### docs/
Техническая документация проекта:

- **ARCHITECTURE.md** - архитектура (этот файл)
- **STRUCTURE.md** - полная структура репозитория
- **CHANGELOG.md** - история изменений
- **BACKLOG.md** - текущие задачи
- **ROADMAP.md** - дорожная карта
- **TECHNICAL-DEBT.md** - технический долг
- **DECISIONS.md** - журнал решений
- **RETROSPECTIVE.md** - ретроспектива
- **GLOSSARY.md** - глоссарий терминов
- **INDEX.md** - индекс всех файлов

### guides/
Руководства пользователя:

- **GUIDE-ONBOARDING.md** - быстрое начало
- **GUIDE-SETUP.md** - установка
- **GUIDE-CONTRIBUTING.md** - контрибьюция
- **GUIDE-GIT.md** - работа с Git
- **GUIDE-TESTING.md** - тестирование
- **GUIDE-DEPLOY.md** - деплой
- **GUIDE-SECURITY.md** - безопасность
- **GUIDE-FAQ.md** - частые вопросы
- **GUIDE-TROUBLESHOOTING.md** - решение проблем
- **и другие...**

---

## 📜 МЕТОДОЛОГИЯ

### instructions/
Методологические материалы:

- **manifest.md** - манифест проекта
- **research-principles.md** - 38 принципов исследований
- **exposure/** - методы разоблачения (29 методов, 5 механизмов, 60+ приёмов)
- **dictionaries/** - словари (экономинимы, грецизмы, латинизмы, славянизмы и др.)
- **methodology/** - методология исследований
- **templates/** - шаблоны файлов
- **checkers/** - инструкции для чекеров

---

## 💡 ИДЕИ

### ideas/
Будущие идеи и предложения:

- **api-design.md** - дизайн API
- **database-schema.md** - схема базы данных
- **neural-network-plan.md** - план нейросети
- **search-engine.md** - поисковый движок
- **tree-visualization.md** - визуализация дерева
- **ux-ui-improvements.md** - улучшения UI/UX
- **web-interface.md** - веб-интерфейс
- **и другие...**

---

## 🔗 НАВИГАЦИЯ

### Быстрый доступ

- [README.md](../README.md) - главная страница
- [STRUCTURE.md](STRUCTURE.md) - полная структура
- [BACKLOG.md](BACKLOG.md) - текущие задачи
- [ROADMAP.md](ROADMAP.md) - дорожная карта
- [CHANGELOG.md](CHANGELOG.md) - история изменений

### По папкам

- [content/](../content/) - основной контент
- [products/](../products/) - продукты
- [tools/](../tools/) - инструменты
- [instructions/](../instructions/) - методология
- [guides/](../guides/) - руководства
- [ideas/](../ideas/) - идеи
- [data/](../data/) - данные
- [backlog/](../backlog/) - задачи

---

## 📝 ПРИМЕЧАНИЯ

1. **Папки `ed/` и `web/`** были удалены из ARCHITECTURE.md, так как не существуют в файловой системе. Контент перемещён в `products/`.
2. **Папка `tools/cache/`** удалена из документации, кэш управляется автоматически.
3. **Папка `instructions/tahor/`** заменена на `instructions/dictionaries/` с более детальной структурой.
4. **Папка `instructions/guides/`** удалена, так как дублирует `guides/`.
5. **Папки `products/`, `data/`, `backlog/`, `archive/`** добавлены в документацию.

---

## 🔄 ИСТОРИЯ ОБНОВЛЕНИЙ

- **v2.0** (2026-07-01) - Полное обновление под реальную структуру
- **v1.0** (2026-06-09) - Первичное создание