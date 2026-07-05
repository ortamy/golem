```markdown
# 📜 GUIDE-CHECKERS — СПРАВОЧНИК ЧЕКЕРОВ

**Метаданные файла**
- **Файл:** `guides/GUIDE-CHECKERS.md`
- **Версия:** 2.0
- **Дата создания:** 2026-06-09
- **Последнее обновление:** 2026-06-14
- **Причина обновления:** Полное обновление — добавлены новые чекеры, обновлены названия
- **Статус:** Активный
- **Тема:** Полный справочник по всем чекерам проекта — что делает, как запускать, какие флаги
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `tools/checkers/`, `guides/GUIDE-AUDIT.md`, `guides/GUIDE-CODING.md`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-14

---

## 🔥 ВВЕДЕНИЕ

Чекеры — скрипты проверки файлов проекта. Каждый чекер отвечает за свою область. Вместе они обеспечивают чистоту проекта по всем фронтам.

Все чекеры находятся в `tools/checkers/`. Запускать из корня репозитория.

---

## 📋 КАТАЛОГ ЧЕКЕРОВ

### check-tahor.py — Проверка языковых подмен

Главный чекер проекта. Проверяет тексты на наличие языковых подмен из 20 словарей: религионимы, грецизмы, латинизмы, модернизмы и другие.

```bash
python tools/checkers/check-tahor.py
python tools/checkers/check-tahor.py --fix
python tools/checkers/check-tahor.py --rebuild
python tools/checkers/check-tahor.py --verbose
```

- `--fix` — автоматически исправляет найденные подмены
- `--rebuild` — перестраивает кэш словарей из `instructions/dictionaries/`
- `--verbose` — подробный вывод всех файлов
- `--save` — сохранить отчёт в `reports/`

Первое упоминание заменяется на полную форму (с ивритом), последующие — на краткую. Заголовки заменяются КАПСОМ.

---

### check-headers.py — Проверка формата заголовков H1

Проверяет что все `.md` файлы имеют правильный формат заголовков: ивритское слово + русское название.

```bash
python tools/checkers/check-headers.py
```

Создаёт CSV с нарушениями в `tools/cache/headers-violations.csv`.

---

### check-mivdak.py — Аудит полезности текстов

Оценивает качество исследований: наличие обязательных разделов, применение методов exposure, обнаружение типов искажений.

```bash
python tools/checkers/check-mivdak.py
```

Показывает процент качества по типам файлов, топ лучших и худших.

---

### check-file-headers.py — Проверка заголовков файлов кода

Проверяет что все файлы кода имеют заголовок с путём и описанием в первой строке.

```bash
python tools/checkers/check-file-headers.py
python tools/checkers/check-file-headers.py --fix
```

Находит несовпадения между путём в заголовке и реальным путём файла.

---

### check-code-quality.py — Проверка качества кода

Проверяет Python-скрипты на соответствие стандартам.

```bash
python tools/checkers/check-code-quality.py
python tools/checkers/check-code-quality.py --fix
```

---

### check-links.py — Проверка внутренних ссылок

Проверяет все ссылки вида `[текст](путь)` в `.md` файлах.

```bash
python tools/checkers/check-links.py
```

---

### check-naming.py — Проверка имён файлов

Проверяет соответствие имён `.md` файлов правилам проекта.

```bash
python tools/checkers/check-naming.py
```

---

### check-duplicates.py — Поиск дубликатов

Находит файлы с похожим содержимым.

```bash
python tools/checkers/check-duplicates.py
```

---

### check-orphans.py — Поиск файлов-сирот

Находит файлы на которые нет ни одной ссылки.

```bash
python tools/checkers/check-orphans.py
```

---

### check-empty-files.py — Поиск пустых файлов

Находит файлы с телом меньше 100 символов или с маркерами незаполненности.

```bash
python tools/checkers/check-empty-files.py
```

---

### check-consistency.py — Проверка согласованности

Проверяет единообразие транслитерации, битые ссылки, соответствие путей.

```bash
python tools/checkers/check-consistency.py
```

---

### check-exposure.py — Проверка по exposure-критериям

Проверяет файлы на наличие 10 типов искажений по 70+ маркерам.

```bash
python tools/checkers/check-exposure.py
```

---

### check-env.py — Проверка окружения

Показывает что установлено, чего не хватает для работы проекта.

```bash
python tools/checkers/check-env.py
```

---

### check-scripts-usefulness.py — Аудит полезности скриптов

Анализирует все Python-скрипты и оценивает их полезность.

```bash
python tools/checkers/check-scripts-usefulness.py
```

---

### check-countries.py — Проверка стран по критериям ТаНаХа

Оценивает страны мира по 35 параметрам из 7 уровней.

```bash
python tools/checkers/check-countries.py
```

---

### check-external-links.py — Проверка внешних ссылок

Проверяет HTTP(S) ссылки на доступность.

```bash
python tools/checkers/check-external-links.py
```

---

### check-fix-encoding.py — Исправление кодировки

Конвертирует файлы из Windows-1251 в UTF-8.

```bash
python tools/checkers/check-fix-encoding.py
```

---

### check-fix-metadata.py — Исправление метаданных

Исправляет искажённые названия полей метаданных.

```bash
python tools/checkers/check-fix-metadata.py --fix
```

---

### check-file-sizes.py — Анализ размеров файлов

Показывает статистику по размерам `.md` файлов.

```bash
python tools/reports/check-file-sizes.py
```

---

## 🔄 ТИПОВОЙ ЦИКЛ ПРОВЕРКИ

### Ежедневно
```bash
python tools/checkers/check-tahor.py
python tools/checkers/check-links.py
python tools/checkers/check-headers.py
```

### Перед коммитом
```bash
python tools/checkers/check-tahor.py --fix
python tools/checkers/check-file-headers.py --fix
python tools/checkers/check-naming.py
```

### Раз в неделю
```bash
python tools/checkers/check-mivdak.py
python tools/checkers/check-orphans.py
python tools/checkers/check-duplicates.py
```

### Полный аудит
```bash
python tools/golem.py
```

