# Design Inspiration — техники «современного манускрипта»

**Статус:** Этап A (задача 3, код не менялся)
**Дата:** 2026-09-04
**Источник постановки:** `tasks/GOL-002-REDESIGN.md`, пайплайн `tasks/tasks.md` (задача 3)
**Правило:** каждая техника — с источником и способом применения в токенах GOLEM. Скриншоты чужих сайтов не собирались: вместо них — техника + ссылка; скриншоты делаем только для GOLEM (before/after, этап C).

## Проверенные источники (fetch выполнен)

| Источник | Что подтверждено фетчем |
|---|---|
| ui.shadcn.com (Card) | Анатомия Card: Header/Title/Description/Action/Content/Footer; радиус `xl`, рамка `1px ring-foreground/10` вместо тени-борда; **переменная `--card-spacing`** с пресетами 16/20/24/32px; контент «в край» через отрицательные margin |
| heropatterns.com | Паттерны = inline SVG data-URI в `background-image`; настраиваются foreground/background цвет + opacity; лицензия CC BY 4.0 |
| transparenttextures.com | Каталог PNG-тайлов (3px repeat), категории noise/paper/fabric; подключение — CSS с base64/URL тайла; для пергамента релевантны «Beige Paper», «Rice Paper», «Textured Paper», «Vintage Speckles» |
| magicui.design | Подтверждён компонентный состав (marquee, shimmer и др., 150+ компонентов на CSS+Motion); конкретные параметры мержим с общедоступной документацией компонент (ниже) |

## Источники по документации (fetch недоступен, техники канонические)

- **ui.aceternity.com** (таймаут фетча): Spotlight (radial-gradient, позиция через CSS-переменные `--x/--y` по mousemove), Border Beam (conic-gradient, анимация угла), Aurora Background (размытые градиентные пятна + blur), Animated Gradient Text (`background-clip: text` + анимация `background-position`).
- **tremor.so** (таймаут): Stat-карточки — крупное число + caps-подпись + delta-бейдж; сетка с равным ритмом.
- **hypercolor.dev** (таймаут): градиентные пресеты; ниже — адаптации в палитре GOLEM.
- **21st.dev** (таймаут): hero-паттерны — kicker → заголовок → подзаголовок, stagger-появление, крупный whitespace.

---

## Техники (20) и применение в GOLEM

### A. Hero-секции

1. **Пергаментный градиент hero** — hypercolor (адаптация). `linear-gradient(135deg, var(--bg-secondary), var(--bg-primary) 55%, var(--bg-tertiary))` для светлых hero; для тёмных — `linear-gradient(160deg, var(--bg-dark), var(--bg-dark-hover))`. Новые токены `--grad-parchment`, `--grad-dark`.
2. **Noise-текстура пергамента** — transparenttextures («Beige Paper», 3px tile). PNG-тайл → data-URI; overlay `opacity: 0.03–0.05`, `mix-blend-mode: multiply` (светлая) / `screen` (тёмная). Токен `--texture-noise` + класс-модификатор.
3. **Aurora-пятно на тёмном hero** — Aceternity Aurora (упрощённо): 1–2 radial-gradient пятна золотого тона `rgba(212,160,48,0.14)`, `filter: blur(60px)`, только тёмная тема, `::before`, без JS.
4. **Глиф-монограмма в hero** — концепция «глифы как искусство»: крупный палео-глиф у заголовка, `clamp(4rem,10vw,8rem)`, золотой, мягкий `text-shadow`; в тёмной теме + glow (№18).
5. **Spotlight по курсору** — Aceternity Spotlight. Только лаб-hero: JS mousemove пишет `--x/--y`, radial-gradient 600px, `opacity 0.5`; отключён при `prefers-reduced-motion`. Опционально, этап C.
6. **Gradient text на 1–2 словах заголовка** — Aceternity Animated Gradient Text: `background: linear-gradient(90deg, gold-1, gold-2, gold-1); background-clip: text; background-size: 200%` + анимация позиции 6s.

### B. Карточки и статы

7. **Анатомия карточки по shadcn**: Header (kicker + title + description + Action справа) / Content / Footer; единый **`--card-spacing`** (16px базовый, 24px для «герой»-карточек) вместо разнобоя паддингов модулей.
8. **Рамка-ring вместо грубого бордера**: `border: 1px solid color-mix(in srgb, var(--text-primary) 10%, transparent)` + радиус `--radius-lg (14px)`; тень отдельно (№9).
9. **Hover-подъём**: `transform: translateY(-4px)` + `box-shadow: var(--shadow-hover)`, `transition: 300ms cubic-bezier(0.4,0,0.2,1)`; активный элемент — без lift, только золотая рамка.
10. **Gradient border на hover** — Aceternity Border Beam (статичная версия): `background: linear-gradient(var(--bg-card), var(--bg-card)) padding-box, linear-gradient(135deg, var(--accent-gold), transparent 60%) border-box; border: 1px solid transparent`. Только «герой»-карточки (круг клуба, CTA-блоки).

11. **Stagger entrance** — паттерн 21st.dev/magicui, CSS-эквивалент anime.js: класс `.reveal` (opacity 0, translateY(16px)) + `.is-visible` (переход 480ms `--ease-out`) + `transition-delay: calc(var(--i) * 90ms)`; `--i` проставляет разметка или `:nth-child`. Триггер — IntersectionObserver (паттерн уже принят в кодовой базе: `exposure-case.js`).
12. **Stat-тайл** — Tremor: число `--text-3xl` serif золотое, подпись caps `--text-xs` `--tracking-caps`, delta-бейдж pill; фон `--bg-card` + `--shadow-card`; единая регистрация подписей (CAPS или lower — выбрать одну на всю систему).

### C. Типографика

13. **Fluid-шкала заголовков**: h1 `clamp(2.25rem, 5vw, 3.5rem)`; h2 секции `clamp(1.75rem, 3vw, 2.5rem)`; body `1.0625–1.125rem`, `line-height: var(--leading-read)` в читаемых зонах (токен уже есть). Семейства шрифтов не меняем (EB Garamond/Cormorant соответствуют концепции; Playfair не вводим).
14. **Kicker-капитель как класс**: `.lab-kicker` = caps, `--tracking-caps`, `--text-xs`, золотой; сейчас каждый модуль рисует капитель по-своему.
15. **Бейджи confidence как pill-градиенты**: «проверено» — зелёная заливка 10% + зелёный текст; «гипотеза» — золотая; «спорно» — красная; `font-weight: 600`, `--radius-pill`. Семантика методологии (эмет/шекер) читается уровнем уверенности.
16. **Палео-глиф в строке текста**: `.glyph-inline` = `font-size: 1.35em; vertical-align: -0.12em; color: var(--text-gold)`; стандартизировать (сейчас точечные стили в модулях).

### D. Motion

17. **Shimmer на primary CTA** — magicui: `::after` с диагональным золотым бликом, `translateX(-150% → 150%)`, 1.8s, пауза 4s; только одна главная кнопка на экран; выключен при reduced-motion.
18. **Glow в тёмной теме** — промпт + приём aceternity: `text-shadow: 0 0 24px rgb(var(--accent-gold-rgb)/0.35)` на глифах hero; `box-shadow: 0 0 0 1px rgb(var(--accent-gold-rgb)/0.25), var(--shadow-card)` на активных элементах сайдбара.
19. **Press-микро**: `:active { transform: scale(0.97) }` на `--dur-1` — единое для всех кнопок.
20. **prefers-reduced-motion**: глобальный блок — отключить reveal/marquee/shimmer/spotlight (оставить только opacity-появление без сдвига). Обязательный критерий приёмки этапов B/C.

### E. Что НЕ делаем (фиксируем, чтобы не спорить позже)

- Не добавляем anime.js / GSAP / Framer Motion / Lottie: CSS закрывает те же требования без веса и отказоустойчивых рисков (анимационных либ в кодовой базе нет — правило «только подтверждённые библиотеки»).
- Не меняем шрифты (Playfair не вводим: Cormorant Garamond уже несёт «манускрипт»-характер).
- Не делаем React-компоненты; только токены + классы в существующем CSS.
- Marquee-лента глифов — отложена: эффект спорный для читаемого инструмента; вернуться в этапе C, только если hero останется «пустым».

## Карта применения по экранам (для этапа C)

| Экран | Техники |
|---|---|
| Рабочий стол (hero + метрики) | 1, 2, 3, 4, 7, 9, 12, 14 |
| Лаб-hero / манифест | 1, 2, 5, 6, 13, 14 |
| Обучение / тренажёр | 4, 9, 12, 16, 19 |
| Исследования (карточки) | 7, 8, 9, 11, 15 |
| Палео-клуб | 7, 10, 11, 17, 18 |
