# 🔧 GUIDE-GIT — РАБОТА С GIT В ПРОЕКТЕ «ГОЛЕМ»

**Метаданные файла**
- **Файл:** `guides/GUIDE-GIT.md`
- **Версия:** 1.0
- **Дата создания:** 2026-06-11
- **Последнее обновление:** 2026-06-11
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** Как работать с git — коммиты, ветки, пуши, откат
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** `guides/GUIDE-TESTING.md`, `guides/GUIDE-CONTRIBUTING.md`
- **Хеш:** ожидает
- **Достоверность:** высокая
- **Последний аудит:** 2026-06-11

---

## 🔥 ОСНОВНЫЕ ПРАВИЛА

- Коммиты на русском
- Один коммит — одна задача
- Перед коммитом — проверки
- Не коммитить логи, кэш, временные файлы
- Не пушить сломанные скрипты

---

## 📋 ЕЖЕДНЕВНЫЙ ЦИКЛ

### Начало работы

```bash
git pull
```

### Проверки перед коммитом

```bash
python tools/checkers/check-religionisms.py
python tools/checkers/check-links.py
python tools/checkers/check-naming.py
```

### Коммит

```bash
git add .
git commit -m "Описание изменений"
```

### Пуш

```bash
git push
```

---

## 📝 ФОРМАТ КОММИТОВ

### Структура

```
[тип]: Краткое описание

Подробности (если нужно)
```

### Типы коммитов

- `feat:` — новая функция, файл, скрипт
- `fix:` — исправление ошибки
- `docs:` — документация
- `style:` — оформление, форматирование
- `refactor:` — переработка кода
- `test:` — тесты
- `chore:` — рутина, обновление зависимостей

### Примеры

```
feat: Добавлен скрипт check-exposure.py
fix: Исправлен UnicodeDecodeError в check-links.py
docs: Обновлён GUIDE-AUDIT.md
refactor: Переименованы скрипты с префиксами
chore: Обновлён files.json
```

---

## ⚠️ ЧТО НЕ КОММИТИТЬ

- `tools/cache/` — кэш (автоматически генерируется)
- `*.log` — логи
- `*.pyc` — скомпилированные Python
- `.venv/` — виртуальное окружение
- `node_modules/` — зависимости Node.js
- `golem.log` — логи golem.py

Всё это в `.gitignore`.

---

## 🔄 ОТКАТ ИЗМЕНЕНИЙ

### Откатить незакоммиченные изменения

```bash
git checkout -- .
```

### Откатить конкретный файл

```bash
git checkout -- terminology/yhwh.md
```

### Откатить последний коммит

```bash
git reset --soft HEAD~1
```

### Откатить пуш

```bash
git reset --soft HEAD~1
git push --force
```

---

## 🌿 ВЕТКИ

### Создать ветку

```bash
git checkout -b feature/new-script
```

### Переключиться

```bash
git checkout main
```

### Слить ветку

```bash
git checkout main
git merge feature/new-script
git push
```

---

## 💡 СОВЕТЫ

- Перед большой правкой — коммит. Легко откатить
- После `--fix` скриптов — проверь diff: `git diff`
- Если Cline удалил не то — `git checkout -- .`
- Коммить часто. Мельче коммит — легче откат
- Перед слиянием веток — прогнать все чекеры

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ
- `guides/GUIDE-TESTING.md`
- `guides/GUIDE-CONTRIBUTING.md`
- `.gitignore`