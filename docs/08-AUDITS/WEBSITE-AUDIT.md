# Аудит `products/website`

**Дата:** 2026-07-12  
**Область:** структура, архитектура, JavaScript, сервер, сборка, производительность, SEO, доступность и безопасность.  
**Статус:** статический аудит; production-код не изменялся.

## 1. Краткий итог

Проект представляет собой гибрид статического сайта, динамического Markdown-каталога и набора исследовательских инструментов. Фактическая структура уже отличается от прежней версии этого документа: используются `pages/`, `assets/`, `data/`, `build/`, `webapp/`, `researchlab/` и `tanakh/`. Поэтому прежние рекомендации о безусловном удалении `webapp/`, переносе каталогов и массовом обновлении ссылок нельзя выполнять без dependency-map и проверки всех маршрутов.

Критические зоны: потенциальный path traversal в API чтения файлов, некорректное HTML-экранирование в `js/parser.js`, большое количество `innerHTML` и inline-обработчиков, рассинхрон `sitemap.xml` с фактическими URL, отсутствие минификации JavaScript и наличие `node_modules` внутри website.

## 2. Фактическая структура и масштаб

```text
products/website/
├── index.html, app.js, style.css, files.json
├── pages/                 # основные страницы
├── content/               # контент
├── assets/                # иконки, изображения, шрифты
├── data/                  # данные ТаНаХа и навигация
├── js/                    # API, state, UI, parser, i18n
├── locales/               # ru/en/he
├── webapp/                # отдельные инструменты
├── researchlab/           # исследовательские данные
├── tanakh/                # тестовый interlinear
├── build/                 # Node server и build-конфигурация
└── node_modules/          # зависимости
```

По инвентаризации: около **5 599 файлов / 53,5 MB** вместе с зависимостями; без `node_modules` — около **1 735 файлов / 16,3 MB**. `files.json` занимает примерно 579 KB, крупные PNG-иконки — до 112 KB.

## 3. Приоритеты

| Приоритет | Проблема | Файлы | Действие |
|---|---|---|---|
| P0 | Неочевидная защита API-путей | `build/server.js` | canonical path, проверка выхода из `ROOT`, whitelist каталогов, лимит ответа |
| P0 | Сломано HTML-экранирование | `js/parser.js` | исправить `escHtml`, считать Markdown недоверенным |
| P0 | SEO URL не совпадают со структурой | `index.html`, `sitemap.xml`, `robots.txt` | сверить реальные маршруты, убрать задержанный JS-redirect |
| P1 | `innerHTML` и inline events | `app.js`, `js/ui.js`, `webapp/js/*` | DOM API, `textContent`, `addEventListener`, санитизация |
| P1 | Несколько Markdown-рендереров | `js/parser.js`, `pages/research/index.html`, `build/server.js` | единый parser и тесты |
| P1 | JS minify — заглушка | `build/package.json` | подключить esbuild или terser |
| P1 | `node_modules` внутри website | `products/website/node_modules` | исключить из репозитория и deploy-artifact |
| P1 | Неполная SEO-разметка | HTML-п страницы | уникальные title/description/canonical/hreflang |
| P2 | Полная перерисовка списка | `js/ui.js` | индексация, `DocumentFragment`, virtual list или pagination |
| P2 | Внешний `@import` шрифтов | CSS-файлы | self-host WOFF2 или preconnect |

## 4. Безопасность

### 4.1 API чтения файлов

В `build/server.js` query-параметр `path` участвует в построении пути через `path.join`. Нужна проверка после `path.resolve`:

```js
const requested = url.searchParams.get('path') || '';
const candidate = path.resolve(ROOT, requested);
const root = path.resolve(ROOT) + path.sep;
if (!candidate.startsWith(root) || !candidate.endsWith('.md')) {
  res.writeHead(400);
  res.end('Invalid path');
  return;
}
```

Дополнительно: whitelist разрешённых каталогов, запрет symlink escape, rate limit и лимит размера файла.

### 4.2 XSS и HTML injection

В `js/parser.js` текущая функция фактически не экранирует HTML:

```js
function escHtml(s) {
    return s.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
}
```

Исправить:

```js
function escHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
```

В `js/ui.js` заменить генерацию inline-handler:

```js
span.setAttribute('onclick', "openFile('" + path + "')");
```

на обработчик:

```js
span.addEventListener('click', () => openFile(path));
```

Проверить все места `innerHTML` в `webapp/js/*`, Markdown через `marked` и URL изображений/ссылок. HTML допустим только после строгой санитизации.

### 4.3 localStorage

`js/state.js` и `webapp/js/vision*.js` используют `localStorage`. Нужно проверять типы после `JSON.parse`, ограничить историю, валидировать пути по `FILES` и не хранить секретные API-ключи в браузере в production. Предпочтительно использовать серверный proxy.

## 5. Архитектура и качество кода

- Объединить реализации Markdown из `js/parser.js`, `pages/research/index.html` и `build/server.js`.
- Перейти в `js/api.js` с callbacks на `async/await`; проверять `response.ok` в `fetchJSON`.
- Убрать глобальные функции `window.Golem*` и inline-обработчики в пользу ES modules.
- В `app.js` убрать повторную инициализацию `setFontSize` и двойной вызов `addToHistory`.
- Разделить исходный контент, generated HTML и runtime data; закрепить правила в `docs/STRUCTURE.md`.
- Не удалять `webapp/`, `researchlab/` или `tanakh/` без проверки их ссылок и назначения.

## 6. Производительность и сборка

- `files.json` загружается целиком (~579 KB): добавить build-time индекс, pagination или search endpoint.
- Кэшировать нормализованные поля поиска; использовать `DocumentFragment`; для больших списков применить virtual list.
- Оптимизировать PNG и подготовить WebP/AVIF; добавить `width`, `height`, `loading="lazy"`, `decoding="async"`.
- Убрать блокирующий Google Fonts `@import`, self-host WOFF2 либо добавить `preconnect`.
- В `build/package.json` заменить заглушку:

```json
"build:js:minify": "echo 'js minify skipped'"
```

на реальную сборку esbuild/terser с sourcemap и hash-именами.
- Расширить `tailwind.config.js` путями `pages/**/*.html`, `webapp/**/*`, `js/**/*` либо удалить неиспользуемый Tailwind pipeline.
- Не публиковать `node_modules`; deploy должен содержать только build-artifact.

## 7. SEO и доступность

`index.html` вычисляет язык, но всегда отправляет в `pages/index.html` через 1,2 секунды. Использовать HTTP redirect или мгновенную навигацию на реальные locale URL. `sitemap.xml` указывает `/ru/`, `/en/`, `/he/`, тогда как фактическая структура содержит `pages/`; все URL надо проверить на HTTP 200.

Многие content HTML имеют `<title>Без названия — Golem`; отсутствуют description, canonical и hreflang. Нужны шаблон метаданных и генерация sitemap из route manifest. Не запрещать в `robots.txt` CSS/JS, необходимые для рендеринга; `Disallow: /api/` оставить.

Для accessibility:

- использовать `<main>`, `<nav>`, `<header>`, `<article>`;
- интерактивные элементы сделать `<button>`/`<a>`, а не `div[onclick]`;
- добавить `:focus-visible`, `aria-label`, `aria-live` для загрузки и ошибок;
- проверить контраст золотого текста;
- для иврита добавить `dir="rtl"` и проверить sidebar/breadcrumbs;
- всем содержательным изображениям назначить осмысленный `alt`.

## 8. План исправлений

### Этап 1 — P0

1. Закрыть path traversal и ограничить API.
2. Исправить `escHtml`.
3. Проверить `innerHTML` с контентными данными.
4. Сверить routes, `sitemap.xml` и `robots.txt`.

### Этап 2 — P1

1. Вынести единый Markdown parser.
2. Добавить production-сборку JS/CSS.
3. Убрать `node_modules` из deploy.
4. Ввести шаблон SEO-метаданных и semantic HTML.

### Этап 3 — P2

1. Оптимизировать JSON, изображения и шрифты.
2. Внедрить virtual list/индексацию.
3. Добавить automated checks ссылок, HTML, accessibility и security.

## 9. Чек-лист приёмки

- [ ] `npm run build` реально создаёт production CSS/JS.
- [ ] API не отдаёт `..`, абсолютные пути, symlink targets и не-Markdown.
- [ ] Markdown с `<script>`, атрибутами и опасными URL безопасен.
- [ ] Все sitemap URL возвращают 200 и соответствуют canonical.
- [ ] Нет console errors на desktop/mobile/RTL.
- [ ] Поиск и открытие файла работают при пустом/повреждённом JSON.
- [ ] Клавиатурой доступны поиск, список, закладки и модальные окна.
- [ ] Lighthouse/axe и проверка ссылок выполняются в CI.

## 10. Ограничения аудита

Аудит выполнен статически по файлам репозитория. Lighthouse, axe, нагрузочные тесты, браузерное E2E и production reverse-proxy не проверялись. Эксплуатируемость API и Core Web Vitals нужно подтвердить отдельным тестовым прогоном.