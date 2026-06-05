# 🛠️ ИНСТРУМЕНТЫ АВТОМАТИЗАЦИИ

**Метаданные файла**
- **Файл:** `tools/README.md`
- **Версия:** 1.1
- **Дата создания:** 2026-06-05
- **Последнее обновление:** 2026-06-05
- **Причина обновления:** Замена таблиц на списки
- **Статус:** Активный
- **Тема:** Полная инструкция по использованию инструментов автоматизации проекта

---

## 📋 СПИСОК ИНСТРУМЕНТОВ

- `check-naming.py` — проверка именования файлов
- `add-metadata.py` — массовое добавление метаданных
- `validate-metadata.py` — проверка корректности метаданных
- `update-versions.py` — обновление версий и дат
- `sync-structure.py` — синхронизация structure.md
- `find-duplicates.py` — поиск дубликатов
- `find-orphans.py` — поиск файлов-сирот
- `check-links.py` — проверка битых ссылок
- `generate-glossary.py` — генерация глоссария
- `generate-nav.py` — генерация навигации для README
- `stats-report.py` — статистика по репозиторию
- `export-repo.sh` — выгрузка всех md в один файл
- `backup.sh` — бэкап репозитория
- `create-backup-scheduled.sh` — автоматический бэкап (cron)

---

## 🚀 БЫСТРЫЙ СТАРТ

```bash
cd tools

chmod +x *.sh

python3 check-naming.py
python3 validate-metadata.py
python3 check-links.py
python3 generate-glossary.py
python3 sync-structure.py
./backup.sh
```

---

## 🔧 ИНСТРУКЦИИ

### 1. CHECK-NAMING.PY

Проверяет имена всех md-файлов по правилам.

```bash
python3 check-naming.py
```

**Правила:**
- только латиница (a-z)
- дефис между словами
- расширение .md
- нижний регистр
- без русских букв

### 2. ADD-METADATA.PY

Добавляет блоки метаданных в файлы.

```bash
python3 add-metadata.py --dry-run
python3 add-metadata.py
```

### 3. VALIDATE-METADATA.PY

Проверяет корректность метаданных.

```bash
python3 validate-metadata.py
```

**Проверяет:**
- наличие всех обязательных полей
- формат версии (X.Y)
- формат даты (ГГГГ-ММ-ДД)
- корректность статуса
- соответствие пути файла

### 4. UPDATE-VERSIONS.PY

Обновляет версии и даты.

```bash
python3 update-versions.py --dry-run
python3 update-versions.py --type minor
python3 update-versions.py --type major
python3 update-versions.py --all
```

### 5. SYNC-STRUCTURE.PY

Синхронизирует structure.md с файловой системой.

```bash
python3 sync-structure.py
```

### 6. FIND-DUPLICATES.PY

Ищет дублирующиеся файлы.

```bash
python3 find-duplicates.py
```

**Находит:**
- точные дубликаты
- похожие имена
- потенциальные дубликаты по ключевым словам

### 7. FIND-ORPHANS.PY

Ищет файлы, на которые никто не ссылается.

```bash
python3 find-orphans.py
```

### 8. CHECK-LINKS.PY

Проверяет битые ссылки между файлами.

```bash
python3 check-links.py
```

### 9. GENERATE-GLOSSARY.PY

Генерирует GLOSSARY.md из терминов.

```bash
python3 generate-glossary.py
```

### 10. GENERATE-NAV.PY

Генерирует навигацию и вставляет в README.md.

```bash
python3 generate-nav.py
```

### 11. STATS-REPORT.PY

Генерирует статистику по репозиторию в STATS.md.

```bash
python3 stats-report.py
```

### 12. EXPORT-REPO.SH

Выгружает все md-файлы в один файл export.txt.

```bash
./export-repo.sh
```

### 13. BACKUP.SH

Создаёт бэкап репозитория.

```bash
./backup.sh
```

### 14. CREATE-BACKUP-SCHEDULED.SH

Для настройки автоматического бэкапа через cron.

```bash
chmod +x create-backup-scheduled.sh
crontab -e
# добавить: 0 2 * * * /путь/к/golem/tools/create-backup-scheduled.sh
```

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

**ПЕРЕД ЗАПУСКОМ ADD-METADATA.PY**
- сделайте бэкап: `./backup.sh`
- запустите `--dry-run` сначала
- проверьте результат на нескольких файлах

**ПЕРЕД ЗАПУСКОМ UPDATE-VERSIONS.PY**
- всегда используйте `--dry-run` первым
- убедитесь, что изменения нужны
- делайте коммит после обновления

**ПРИ ОБНАРУЖЕНИИ ОШИБОК**
- `check-naming.py` — переименуйте файлы вручную
- `validate-metadata.py` — исправьте метаданные
- `check-links.py` — обновите битые ссылки
- `find-duplicates.py` — удалите или объедините дубликаты

---

## 🔄 РЕКОМЕНДУЕМЫЙ ПОРЯДОК РАБОТЫ

**ПЕРЕД КОММИТОМ**
- `python3 check-naming.py`
- `python3 validate-metadata.py`
- `python3 check-links.py`

**ПЕРИОДИЧЕСКИ (РАЗ В НЕДЕЛЮ)**
- `python3 find-duplicates.py`
- `python3 find-orphans.py`
- `python3 stats-report.py`

**ПОСЛЕ ДОБАВЛЕНИЯ НОВЫХ ФАЙЛОВ**
- `python3 sync-structure.py`
- `python3 generate-glossary.py`
- `python3 generate-nav.py`

**ПЕРЕД РЕЛИЗОМ**
- `python3 update-versions.py --type minor`
- `python3 stats-report.py`
- `./backup.sh`

---

## 📊 ПРИМЕРЫ ВЫВОДА

**CHECK-NAMING.PY**
```
✅ Все 150 файлов названы корректно
```

**VALIDATE-METADATA.PY**
```
❌ ОШИБКИ:
  📄 terminology/emet.md
     • отсутствует поле: Статус:
     • поле 'Версия': неверный формат: 1
```

**CHECK-LINKS.PY**
```
❌ БИТЫЕ ССЫЛКИ:
  📄 README.md
     • строка 42: structure.md → файл не существует
```

**FIND-DUPLICATES.PY**
```
⚠️ ПОТЕНЦИАЛЬНЫЕ ДУБЛИКАТЫ:
  • terminology/emet.md
    ↔ terminology/truth.md
    схожесть: 85%
```

---

## 🛠️ УСТРАНЕНИЕ ПРОБЛЕМ

- `permission denied` → `chmod +x *.sh`
- `python3: command not found` → установите Python 3
- `SyntaxError` → проверьте версию Python (нужен 3.6+)
- файл не найден → убедитесь, что вы в папке `tools/`
