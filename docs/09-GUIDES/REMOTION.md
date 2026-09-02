# Remotion: создание видео в проекте «Голем»

**Файл:** `docs/09-GUIDES/REMOTION.md`
**Статус:** актуальный рабочий гайд
**Продукт:** `products/video/`
**Опора:** `docs/00-START/MANIFEST.md`, `docs/01-ARCHITECTURE/ARCHITECTURE.md`

## Назначение

Remotion — отдельный видеопродукт проекта «Голем». Он создаёт видео из React-композиций, где каждый кадр вычисляется программно. Видеопродукт изолирован от публичного сайта, Research Lab, Python-агентов, `tasks/` и `docs/`.

Рабочая директория:

```text
products/video/
```

Не размещай файлы Remotion в `products/website/`, `products/website/apps/researchlab/` или `products/website/build/`.

## Требования

- Node.js 18 или новее;
- npm;
- зависимости из `products/video/package.json`;
- Chromium для первого серверного рендера Remotion.

Проверка Node.js из корня репозитория:

```powershell
node -v
```

Если версия ниже 18, сначала обнови Node.js. Установку и разработку до этого не продолжай.

## Установка зависимостей

Из корня репозитория:

```powershell
cd products/video
npm install
```

Если npm сообщает `ECONNRESET`, `ENOTCACHED` или обрывает загрузку tarball, это проблема сети или npm-кэша. Не удаляй исходники композиции. Проверь proxy/registry и повтори `npm install` после восстановления соединения.

## Структура видеопродукта

- `src/Root.tsx` — регистрация композиций;
- `src/WordOfTheDay.tsx` — композиция шаблона «Слово дня»;
- `src/data/words.json` — данные слов;
- `src/index.ts` — точка регистрации Remotion;
- `src/index.css` — глобальные стили;
- `public/` — статические ресурсы;
- `out/` — локальные результаты рендера, не коммитить;
- `remotion.config.ts` — настройки Remotion;
- `package.json` — команды и версии зависимостей.

Производные видео хранятся только в `products/video/out/`.

## Запуск Remotion Studio

```powershell
cd C:\Users\DELL\Desktop\golem-main\products\video
npm run dev
```

Открой адрес, который напечатает Remotion Studio, обычно `http://localhost:3000`.

В списке композиций должна быть:

```text
WordOfTheDay
```

Проверь в Studio:

- размер `1920 × 1080`;
- частоту `30 fps`;
- длительность `450 frames`, то есть 15 секунд;
- последовательное появление глифов;
- переход к буквенным колонкам;
- финальную фразу и плашку `GOLEM`.

Для остановки Studio нажми `Ctrl+C` в терминале.

## Регистрация композиции

Каждая композиция регистрируется в `src/Root.tsx` через `Composition`:

```tsx
<Composition
  id="WordOfTheDay"
  component={WordOfTheDay}
  durationInFrames={450}
  fps={30}
  width={1920}
  height={1080}
/>
```

Значение `id` используется в команде рендера. Оно должно быть уникальным в пределах продукта.

## Анимации

Для шаблона разрешены только встроенные средства Remotion:

- `useCurrentFrame()` — текущий кадр;
- `useVideoConfig()` — fps, ширина и высота;
- `interpolate()` — преобразование диапазона кадров в значение свойства;
- `spring()` — физическое появление и движение.

Пример появления элемента:

```tsx
const progress = spring({
  frame: frame - delay,
  fps,
  config: {damping: 14, stiffness: 110},
});

<div
  style={{
    opacity: progress,
    transform: `translateY(${interpolate(progress, [0, 1], [40, 0])}px)`,
  }}
>
  Содержимое
</div>
```

Не подключай сторонние библиотеки анимации для шаблона «Слово дня».

## Данные слов

Файл данных:

```text
products/video/src/data/words.json
```

Каждое слово должно соответствовать схеме тренажёра:

```json
{
  "id": "padah",
  "hebrew": "פדה",
  "paleo": "𐤐𐤃𐤄",
  "translit": "padah",
  "gloss": "выведение наружу",
  "letters": [
    {
      "glyph": "𐤐",
      "name": "Пе",
      "picture": "рот",
      "meaning": "речь"
    }
  ],
  "synthesis": "речь открывает дверь к откровению",
  "keywords": ["выход", "освобождение"],
  "confidence": 0.91
}
```

Для новых слов:

1. проверь существующие данные в Research Lab;
2. возьми глифы и образы из канонического алфавита;
3. сохрани все обязательные поля;
4. проверь валидность JSON;
5. открой композицию в Studio и проверь длину текста.

Текущий шаблон выбирает первое слово из массива. Для параметризации используй `defaultProps` или metadata-функцию Remotion, не меняя исходный формат данных.

## Стиль GOLEM

Для видео используются значения, согласованные с Research Lab:

- пергаментный фон: `#ede0c8`;
- светлая бумажная панель: `#faf3e0`;
- тёмно-коричневый текст: `#2c1810`;
- золото для глифов и акцентов: `#b8860b`;
- основной текст: `EB Garamond`, затем `Georgia`;
- палео-глифы: `Noto Sans Phoenician` с системным fallback.

Если понадобится локальный файл шрифта, скопируй только необходимый ресурс в `products/video/public/` и подключи его внутри видеопродукта. Не импортируй CSS из сайта или Research Lab напрямую.

## Проверка кода

Из каталога `products/video`:

```powershell
npm run lint
```

Команда запускает ESLint и TypeScript-проверку.

Быстрая проверка JSON:

```powershell
node -e "JSON.parse(require('fs').readFileSync('src/data/words.json','utf8')); console.log('words.json: valid')"
```

## Рендер MP4

Из каталога `products/video`:

```powershell
npx remotion render WordOfTheDay out/slovo-dnya.mp4
```

Результат:

```text
C:\Users\DELL\Desktop\golem-main\products\video\out\slovo-dnya.mp4
```

Первый рендер может скачать headless Chromium. Это нормальная часть установки Remotion и может занять несколько минут.

Проверка файла:

```powershell
Test-Path .\out\slovo-dnya.mp4
Get-Item .\out\slovo-dnya.mp4 | Select-Object FullName,Length
```

Если Chromium не запускается, прочитай полный текст ошибки, не удаляй `src/` и `public/`, проверь системные зависимости и повтори рендер после устранения причины.

## Типовой цикл изменения

1. Проверь состояние репозитория:

   ```powershell
   git status --short
   ```

2. Измени только файлы в `products/video/`.
3. Запусти `npm run lint`.
4. Открой `npm run dev` и проверь композицию в Studio.
5. Выполни рендер в `out/`.
6. Проверь результат через `Test-Path` и размер файла.
7. Выполни `git diff --check` и `git status --short`.
8. Убедись, что изменения не попали в `products/website/`, Research Lab, `products/agents/`, `tasks/` или `docs/`.

## Частые проблемы

### Композиция не видна в Studio

Проверь импорт компонента и наличие регистрации `Composition` в `src/Root.tsx`. Затем перезапусти Studio.

### Ошибка `Cannot find module`

Выполни из `products/video`:

```powershell
npm install
```

Если npm завершается с `ECONNRESET`, восстанови сетевое соединение и повтори установку.

### Ошибка TypeScript для JSON

Проверь расширение файла `.json`, валидность JSON без комментариев и параметр `resolveJsonModule` в `tsconfig.json`.

### Ошибка рендера

Проверь точный `id` композиции, наличие папки `out/` и доступность Chromium. Не исправляй проблему через изменения в `website` или Research Lab.