# 🗄️ СХЕМА БАЗЫ ДАННЫХ

**Метаданные файла**
- **Файл:** `ideas/database-schema.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-05
- **Последнее обновление:** 2026-06-05
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Схема базы данных для хранения ТаНаХа, терминов, исследований и пользовательских данных
---

## 🔥 ЧТО ЭТО

База данных для централизованного хранения всех данных проекта «Голем».

**Зачем нужна:**
- быстрый поиск по стихам ТаНаХа
- связи между терминами и стихами
- пользовательские прогрессы в геймификации
- API для веб-интерфейса
- замена парсинга md-файлов

---

## 📊 ТАБЛИЦЫ

**1. BOOKS (книги ТаНаХа)**

- id — первичный ключ
- name_ru — русское название
- name_he — ивритское название
- name_en — английское название
- chapters — количество глав
- category — раздел (Тора/Невиим/Ктувим)
- order — порядок в каноне

**2. VERSES (стихи)**

- id — первичный ключ
- book_id — внешняя ссылка на books.id
- chapter — номер главы
- verse — номер стиха
- text_he — ивритский текст (масоретский)
- transliteration — транслитерация
- translation_literal — буквальный перевод
- translation_synodal — синодальный перевод (для сверки)

**3. ROOTS (корни)**

- id — первичный ключ
- root_he — ивритский корень (3-4 буквы)
- transliteration — транслитерация
- meaning — основное значение
- paleo_images — образы палео-иврита

**4. WORDS (слова/термины)**

- id — первичный ключ
- word_he — ивритское слово
- transliteration — транслитерация
- title_ru — русский заголовок (КАПС)
- emoji — эмоджи для заголовка
- definition — краткое определение
- root_id — внешняя ссылка на roots.id
- status — статус (активный/черновик)
- file_path — путь к md-файлу

**5. WORD_VERSES (связь слов и стихов)**

- word_id — внешняя ссылка на words.id
- verse_id — внешняя ссылка на verses.id
- is_primary — основной пример (да/нет)

**6. DISTORTIONS (искажения)**

- id — первичный ключ
- word_id — внешняя ссылка на words.id
- language — язык (греческий/латынь/славянский/русский)
- term — термин на этом языке
- meaning — значение в этом языке
- shift — что потеряно/добавлено

**7. RESEARCHES (исследования)**

- id — первичный ключ
- title_ru — русский заголовок (КАПС)
- emoji — эмоджи
- description — краткое описание
- file_path — путь к md-файлу
- created_at — дата создания
- updated_at — дата обновления

**8. RESEARCH_WORDS (связь исследований и терминов)**

- research_id — внешняя ссылка на researches.id
- word_id — внешняя ссылка на words.id

**9. USERS (пользователи для геймификации)**

- id — первичный ключ
- username — имя пользователя
- created_at — дата регистрации
- total_points — общее количество очков
- level — уровень (1-10)

**10. QUIZ_QUESTIONS (вопросы для квиза)**

- id — первичный ключ
- type — тип (подмена/термин/стих)
- question — текст вопроса
- correct_answer — правильный ответ
- options — варианты ответов (JSON)
- explanation — объяснение
- word_id — внешняя ссылка на words.id (опционально)

**11. USER_ANSWERS (ответы пользователей)**

- id — первичный ключ
- user_id — внешняя ссылка на users.id
- question_id — внешняя ссылка на quiz_questions.id
- is_correct — правильно/неправильно
- answered_at — дата ответа

**12. ACHIEVEMENTS (достижения)**

- id — первичный ключ
- name — название достижения
- description — описание
- condition — условие получения (JSON)

**13. USER_ACHIEVEMENTS (достижения пользователей)**

- user_id — внешняя ссылка на users.id
- achievement_id — внешняя ссылка на achievements.id
- earned_at — дата получения

---

## 🔗 СХЕМА СВЯЗЕЙ

**ОСНОВНЫЕ СВЯЗИ:**

- books (1) ← (N) verses
- roots (1) ← (N) words
- words (1) ← (N) word_verses → (1) verses
- words (1) ← (N) distortions
- words (N) ↔ (N) researches (через research_words)
- users (1) ← (N) user_answers → (1) quiz_questions
- users (N) ↔ (N) achievements (через user_achievements)

---

## 📂 SQL СКРИПТ (ПРИМЕР)

```sql
-- создание таблицы книг
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ru TEXT NOT NULL,
    name_he TEXT NOT NULL,
    name_en TEXT NOT NULL,
    chapters INTEGER,
    category TEXT CHECK(category IN ('Тора', 'Невиим', 'Ктувим')),
    "order" INTEGER
);

-- создание таблицы стихов
CREATE TABLE verses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    text_he TEXT NOT NULL,
    transliteration TEXT,
    translation_literal TEXT,
    translation_synodal TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id)
);

-- создание таблицы корней
CREATE TABLE roots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    root_he TEXT NOT NULL UNIQUE,
    transliteration TEXT,
    meaning TEXT,
    paleo_images TEXT
);

-- создание таблицы слов
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_he TEXT NOT NULL,
    transliteration TEXT,
    title_ru TEXT NOT NULL,
    emoji TEXT,
    definition TEXT,
    root_id INTEGER,
    status TEXT CHECK(status IN ('активный', 'черновик', 'завершён')),
    file_path TEXT,
    FOREIGN KEY (root_id) REFERENCES roots(id)
);

-- создание индексов для быстрого поиска
CREATE INDEX idx_verses_book ON verses(book_id);
CREATE INDEX idx_verses_chapter ON verses(chapter);
CREATE INDEX idx_words_root ON words(root_id);
```

---

## 🔄 ИМПОРТ ИЗ MD-ФАЙЛОВ

```bash
python3 tools/import-to-db.py --from-md --output golem.db
```

**Что делает:**
- парсит все md-файлы
- извлекает термины и их определения
- извлекает стихи с переводами
- заполняет таблицы
- создаёт связи

---

## 📊 ПРИМЕРЫ ЗАПРОСОВ

**НАЙТИ ВСЕ СТИХИ С КОРНЕМ אהב:**

```sql
SELECT v.text_he, b.name_he, v.chapter, v.verse
FROM verses v
JOIN books b ON v.book_id = b.id
WHERE v.text_he LIKE '%אהב%'
```

**ВСЕ ТЕРМИНЫ С ИХ КОРНЯМИ И СТИХАМИ:**

```sql
SELECT w.title_ru, r.root_he, v.text_he
FROM words w
JOIN roots r ON w.root_id = r.id
JOIN word_verses wv ON w.id = wv.word_id
JOIN verses v ON wv.verse_id = v.id
LIMIT 10
```

**ТОП ПОЛЬЗОВАТЕЛЕЙ ПО ОЧКАМ:**

```sql
SELECT username, total_points, level
FROM users
ORDER BY total_points DESC
LIMIT 10
```

---

## ✅ ПРЕИМУЩЕСТВА

- быстрый поиск
- сложные запросы за миллисекунды
- централизованное хранение
- легче поддерживать актуальность
- основа для API

---

## ⚠️ СЛОЖНОСТИ

- нужно поддерживать синхронизацию с md-файлами
- первоначальный импорт (много данных)
- backup и миграции

---

## 🛡️ ВОЗВРАЩЕНИЕ

База данных — не замена md-файлам, а дополнение.

Md-файлы — для людей. База — для машин.

Путь Яхве — использовать правильные инструменты для правильных задач.

---

הַדֶּרֶךְ יְהוָה — hа-Де́рех Яхве — Путь Яхве
