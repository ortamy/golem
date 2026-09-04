ЗАДАЧА: Дизайн-аудит + модернизация GOLEM в стиле "современного манускрипта"

КОНТЕКСТ
- Текущая эстетика: пергамент, золото, палео-глифы (древность)
- Проблема: выглядит "дёшево" — нет глубины, ритма, современных паттернов
- Концепция: "современный манускрипт" — лучшие UI-практики 2025 + древняя эстетика

=== 1. РЕФЕРЕНСЫ ДЛЯ ИЗУЧЕНИЯ (открыть и проанализировать) ===

КОМПОНЕНТНЫЕ БИБЛИОТЕКИ (визуальные паттерны):
* https://21st.dev/components — современные hero, cards, pricing, бейджи
* https://ui.aceternity.com — glow-эффекты, gradient borders, spotlight
* https://magicui.design — анимированные компоненты (marquee, shimmer)
* https://tremor.so/components — data visualization, cards, metrics
* https://ui.shadcn.com/docs/components — Tailwind-компоненты (адаптировать)
* https://www.hyperui.dev — free Tailwind компоненты
* https://cruip.com — landing pages с сильной типографикой

АНИМАЦИИ И ИНТЕРАКЦИИ:
* https://animejs.com — плавные анимации, stagger, easing curves
* https://www.framer.com/motion — spring physics, layout animations
* https://gsap.com — scroll-triggered, timeline animations
* https://lottiefiles.com — vector animations (лёгкие SVG)
* https://useanimations.com — micro-interactions

HERO-СЕКЦИИ И LANDING:
* https://hero.ui — hero patterns с микро-взаимодействиями
* https://www.heropatterns.com — CSS-паттерны для backgrounds
* https://ui.land — коллекция hero-секций
* https://mobbin.com — UI patterns от реальных продуктов

ТИПОГРАФИКА И МИНИМАЛИЗМ:
* https://www.awwwards.com/websites/minimal — минимализм с характером
* https://minimal.gallery — curated minimal sites
* https://typography.com/examples — как крупные шрифты создают вес
* https://fonts.google.com/specimen/Playfair+Display — serif для заголовков

ЦВЕТОВЫЕ СИСТЕМЫ И ГРАДИЕНТЫ:
* https://hypercolor.dev — gradient палитры
* https://uigradients.com — готовые градиенты
* https://colorhunt.co — цветовые схемы
* https://www.colorion.co — curated color palettes

ТЕКСТУРЫ И ПАТТЕРНЫ:
* https://www.transparenttextures.com — subtle textures (noise, paper)
* https://heropatterns.com — SVG patterns
* https://patternpad.com — custom pattern generator

=== 2. АНАЛИЗ РЕФЕРЕНСОВ ===
2.1. Открыть каждый референс, проанализировать:
     - Hero-секции: как создают "wow" через typography + whitespace
     - Cards: shadows, hover-эффекты, группировка контента
     - Анимации: entrance, scroll-triggered, micro-interactions
     - Typography: hierarchy, tracking, line-height
     - Цвета: как используют градиенты, глубину, акценты
2.2. Выписать 20-30 конкретных техник, которые можно применить к GOLEM
2.3. Создать tasks/design-inspiration.md с примерами и скриншотами

=== 3. АУДИТ ТЕКУЩЕГО ДИЗАЙНА ===
3.1. Скриншоты ключевых экранов (desktop + mobile):
     - Главная страница hero
     - Лаб hero + сайдбар
     - Тренажёр (палео-глифы)
     - Scripture reader
     - Клуб (лента + карточки)
     - Модуль исследований (карточки)
3.2. Для каждого: что "дёшево" (плоско, хаотично, мелко, без ритма)
3.3. Создать tasks/design-audit.md с приоритетами P0/P1/P2

=== 4. КОНЦЕПЦИЯ "СОВРЕМЕННЫЙ МАНУСКРИПТ" ===

HERO-СЕКЦИИ (референсы: hero.ui, 21st.dev, Aceternity):
- Палео-глифы: clamp(8rem, 16vw, 16rem), subtle text-shadow, 
  fade-in + scale с anime.js stagger
- Заголовки: clamp(3rem, 6vw, 5rem), font-weight 800, letter-spacing -0.02em
- CTA кнопки: gold gradient, hover: translateY(-2px) + shadow increase
- Background: subtle parchment texture (noise 0.03) + radial gradient
- Spotlight effect: radial gradient following cursor (Aceternity)

КАРТОЧКИ (референсы: shadcn, Tremor, HyperUI):
- Padding: clamp(2rem, 4vw, 3rem)
- Border: 1px solid var(--parchment-dark), border-radius 12px
- Shadow: 0 4px 12px rgba(0,0,0,0.08) → hover: 0 8px 24px rgba(0,0,0,0.12)
- Hover transform: translateY(-4px) с transition 300ms cubic-bezier(0.4, 0, 0.2, 1)
- Stagger entrance: anime.js с delay 100ms между карточками
- Glow border: gradient border на hover (Aceternity)

ТИПОГРАФИКА (референсы: minimal.gallery, typography.com):
- Body: 1.125rem, line-height 1.7 (больше = читается как книга)
- Заголовки секций: clamp(2rem, 4vw, 3rem), margin-bottom 2rem
- Playfair Display или Cormorant Garamond для заголовков (serif с характером)
- Палео-глифы в тексте: font-size 2em, vertical-align middle
- Бейджи confidence: gradient backgrounds, pill shape, font-weight 600

АНИМАЦИИ (референсы: anime.js, Framer Motion, GSAP):
- Scroll-triggered: элементы fade-in + translateY(20px) при появлении
- Hero glyphs: stagger appearance (каждый глиф с задержкой 200ms)
- Card hover: smooth transform + shadow transition
- Button click: scale(0.95) → scale(1) с spring easing
- Marquee для палео-глифов (magicui) — непрерывная лента
- Shimmer effect на CTA кнопках (magicui)
- Respect prefers-reduced-motion: отключить все анимации

ЦВЕТА И ГЛУБИНА (референсы: hypercolor, uigradients):
- Добавить subtle noise texture на пергамент (base64 или SVG)
- Градиенты для hero: linear-gradient(135deg, var(--parchment), var(--parchment-dark))
- Gold accents: linear-gradient(45deg, #D4AF37, #F4E5C2, #D4AF37)
- Gradient borders на карточках (Aceternity)
- Dark mode: усилить контраст, добавить subtle glow на глифах

ТЕКСТУРЫ (референсы: transparenttextures, heropatterns):
- Parchment texture: subtle noise overlay, opacity 0.03-0.05
- Subtle paper grain для backgrounds
- SVG patterns для декоративных элементов

=== 5. ПРИМЕНЕНИЕ ===
5.1. Обновить DESIGN-SYSTEM.md с новыми токенами и паттернами:
     - Цветовые градиенты
     - Shadow tokens (subtle, elevated, deep)
     - Animation durations и easings
     - Typography scale
     - Component variants (cards, buttons, badges)
5.2. Обновить lab.css: внедрить новые стили
5.3. Применить к ключевым модулям (в порядке приоритета):
     - Главная страница hero
     - Лаб hero
     - Тренажёр (палео-глифы)
     - Карточки исследований
     - Клуб (лента)
5.4. Добавить библиотеки (если нужно):
     - anime.js для сложных анимаций
     - Или CSS animations для простоты
     - Или GSAP для scroll-triggered

=== 6. BEFORE/AFTER ===
6.1. Для каждого изменённого экрана сделать скриншоты до/после
6.2. Аннотировать: что изменилось и почему (какой референс использован)

=== НЕ ЛОМАТЬ ===
- функциональность, данные, маршруты
- mobile-first: все улучшения работают на 360px+
- производительность: анимации через transform/opacity, не layout
- accessibility: prefers-reduced-motion, contrast ratios
- размер бандла: не добавлять тяжёлые библиотеки без необходимости

=== ПРОВЕРКА ===
- DESIGN-SYSTEM.md обновлён с новыми паттернами
- tasks/design-inspiration.md с анализом референсов
- before/after скриншоты для 5+ экранов
- mobile версии ок
- анимации плавные, не лагают
- тёмная тема работает

=== ОТЧЁТ ===
- tasks/design-inspiration.md (что взял из каждого референса)
- tasks/design-audit.md
- список применённых техник с указанием источника
- обновлённый DESIGN-SYSTEM.md (diff)
- 6-10 before/after пар скриншотов
- список модулей с улучшениями
- какие библиотеки добавлены (если есть)