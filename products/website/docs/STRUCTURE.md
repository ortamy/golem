# Структура сайта Golem

## Текущая организация

```
products/website/
├── index.html                    # Редирект по языку (автоопределение)
├── style.css                     # Общие стили
├── js/                           # Общие скрипты
│   ├── burger-menu.js           # Бургер-меню (навигация)
│   ├── parser.js                # Парсер контента
│   ├── state.js                 # Управление состоянием
│   ├── api.js                   # API клиент
│   └── ui.js                    # UI компоненты
├── favicon.svg                  # Фавикон
├── robots.txt                   # Для поисковиков
├── sitemap.xml                  # Карта сайта
│
├── ru/                          # Русская версия
│   ├── index.html               # Лендинг (главная)
│   ├── about/                   # О проекте
│   │   └── index.html
│   ├── research/                # Исследования
│   │   ├── index.html
│   │   ├── methods.html
│   │   ├── methodology.html
│   │   └── dictionaries.html
│   ├── tanakh/                  # Чтение ТаНаХа
│   │   └── index.html
│   └── interlinear/             # Подстрочник
│       └── index.html
│
├── en/                          # Английская версия
│   ├── index.html               # Лендинг (главная)
│   ├── about/                   # About
│   │   └── index.html
│   ├── research/                # Research
│   │   ├── index.html
│   │   ├── methods.html
│   │   ├── methodology.html
│   │   └── dictionaries.html
│   └── (tanakh/, interlinear/ — в разработке)
│
├── he/                          # Ивритская версия
│   ├── index.html               # Лендинг (главная)
│   ├── about/                   # אודות
│   │   └── index.html
│   └── research/                # מחקר
│       └── index.html
│
├── research-board/              # 🆕 Генератор исследовательских досок
│   ├── generator.html           # Основная страница
│   ├── generator.css            # Стили доски
│   └── generator.js             # Логика генерации
│
├── content/                     # Исходный контент (Markdown)
│   ├── hebrew/                  # Уроки иврита
│   ├── paleo-hebrew/            # Палео-иврит
│   ├── tanakh/                  # Тексты ТаНаХа
│   ├── researches/              # Исследования
│   ├── terminology/             # Терминология
│   ├── exposed/                 # Разоблачения
│   └── teachings/               # Учения
│
├── tools/                       # Вспомогательные инструменты
│   ├── golem.py                 # Основной скрипт
│   ├── fetch-sefaria.py         # Загрузка из Сефарии
│   ├── interlinear-generator.py # Генератор подстрочника
│   └── ...
│
├── docs/                        # Документация
├── guides/                      # Руководства
├── instructions/                # Инструкции
├── products/                    # Другие продукты
│   ├── agent/
│   ├── assistant/
│   ├── davar/
│   ├── neuro/
│   ├── tanakh/
│   ├── telegram-bot/
│   └── webapp/
│
└── [конфигурационные файлы]
    ├── package.json
    ├── tailwind.config.js
    ├── postcss.config.js
    └── purgecss.config.js
```

## Принципы организации

### 1. Языковые папки (ru/, en/, he/)
- **Назначение:** Локализованные версии сайта
- **Структура:** Каждая папка содержит полную копию структуры страниц на своём языке
- **Связи:** Все ссылки внутри папки относительные (../ для выхода в корень)
- **Доступ:** `https://golem-project.org/ru/index.html`

### 2. Общие ресурсы (корень)
- **style.css** — единые стили для всех языков
- **js/** — общие скрипты (burger-menu, parser, state, api, ui)
- **favicon.svg** — общий фавикон
- **index.html** — редирект по языку (определяет browser language)

### 3. Инструменты (research-board/, tools/)
- **research-board/** — веб-инструменты для пользователей
- **tools/** — скрипты для разработки и обработки контента

### 4. Контент (content/)
- **Назначение:** Исходные Markdown-файлы
- **Обработка:** Преобразуются в HTML через tools/
- **Языки:** Смешанные (иврит, русский, палео-иврит)

## Навигация

### Бургер-меню (burger-menu.js)
Генерируется динамически для всех страниц:
- Главная (index.html)
- Чтение ТаНаХа (tanakh/index.html)
- Исследования (research/index.html)
- Методы разоблачения (research/methods.html)
- Словари (research/dictionaries.html)
- Методология (research/methodology.html)
- **Инструменты** (research-board/generator.html) 🆕
- О проекте (about/index.html)

### Переключатель языков
В бургер-меню:
- RU → ru/index.html
- EN → en/index.html
- HE → he/index.html

## Связи между языками

### Hreflang
Каждая страница содержит:
```html
<link rel="alternate" hreflang="ru" href="https://golem-project.org/ru/page.html">
<link rel="alternate" hreflang="en" href="https://golem-project.org/en/page.html">
<link rel="alternate" hreflang="he" href="https://golem-project.org/he/page.html">
<link rel="alternate" hreflang="x-default" href="https://golem-project.org/">
```

### Авторедирект
`index.html` (корень) определяет язык браузера и редиректит:
```javascript
var lang = navigator.language || navigator.userLanguage || 'ru';
var map = { 'ru': 'ru/index.html', 'en': 'en/index.html', 'he': 'he/index.html' };
var target = map[lang.split('-')[0]] || 'ru/index.html';
setTimeout(function() { window.location.href = target; }, 1200);
```

## Политика ссылок

### Внутри языковой папки
```html
<!-- От ru/research/methods.html -->
<a href="index.html">Главная</a>                    <!-- → ru/index.html -->
<a href="../tanakh/index.html">ТаНаХ</a>            <!-- → ru/tanakh/index.html -->
<a href="../../index.html">Корень</a>               <!-- → ru/index.html -->
```

### Между языками
```html
<!-- Переключатель в бургер-меню -->
<a href="../en/index.html">EN</a>   <!-- Из ru/ → en/ -->
<a href="../he/index.html">HE</a>   <!-- Из ru/ → he/ -->
```

### К общим ресурсам
```html
<link rel="stylesheet" href="../style.css">     <!-- Из ru/ → style.css -->
<script src="../js/burger-menu.js"></script>     <!-- Из ru/ → js/ -->
```

## Разработка

### Добавление новой страницы
1. Создайте HTML в каждой языковой папке (ru/, en/, he/)
2. Добавьте ссылку в `js/burger-menu.js` в `menuTexts`
3. Обновите `sitemap.xml`
4. Добавьте hreflang ссылки

### Добавление нового инструмента
1. Создайте папку в `research-board/` или `tools/`
2. Добавьте пункт в бургер-меню
3. Ссылайтесь из всех языковых версий

### Изменение стилей
1. Общие стили → `style.css`
2. Специфичные для инструмента → `research-board/generator.css`
3. Лендинговые стили → внутри HTML (inline)

## Миграция с текущей структуры

### Что уже сделано
✅ Корень: index.html (редирект), style.css, js/, favicon
✅ ru/: index.html, about/, research/, tanakh/, interlinear/
✅ en/: index.html, about/, research/
✅ he/: index.html, about/, research/
✅ research-board/: generator.html, generator.css, generator.js
✅ burger-menu.js: добавлен пункт "Инструменты"

### Что можно улучшить (опционально)
- [ ] Синхронизировать структуру en/ и he/ с ru/ (добавить tanakh/, interlinear/)
- [ ] Вынести общие стили лендинга в отдельный CSS
- [ ] Создать tools/index.html для каталога инструментов
- [ ] Добавить robots.txt и sitemap.xml для research-board/

## Проверка

### Тестовые сценарии
1. **Редирект:** `https://golem-project.org/` → определяет язык → редирект
2. **Навигация:** Все ссылки в бургер-меню работают
3. **Переключатель языков:** Меняет язык, сохраняет текущую страницу
4. **Инструменты:** research-board/generator.html доступен из всех языков
5. **Адаптивность:** Мобильная версия работает на всех страницах

### Известные проблемы
- ⚠️ en/ и he/ не имеют полной структуры (tanakh/, interlinear/ в разработке)
- ⚠️ Нет центрального каталога инструментов (только research-board/)
- ⚠️ Общие стили лендинга дублируются в ru/ и en/

## Контакты

- **GitHub:** https://github.com/ortamy/golem
- **Сайт:** https://golem-project.org
- **Документация:** docs/, guides/, instructions/