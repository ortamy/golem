# tools/generators/fill-empty-files.py — заполнение пустых и незаполненных md-файлов
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_hint, ask_yes_no, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions", "davar", "ideas", "drafts"]
MIN_BODY_LENGTH = 100  # символов содержания (без метаданных и заголовков)


def extract_body(content: str) -> str:
    """Извлекает тело файла без метаданных и заголовков."""
    # Убираем метаданные
    if '**Метаданные файла**' in content:
        start = content.find('**Метаданные файла**')
        rest = content[start:]
        end_match = re.search(r'\n---|\n# |\n## ', rest[30:])
        if end_match:
            content = content[:start] + rest[30 + end_match.start():]
        else:
            content = content[:start]

    # Убираем заголовки
    body = re.sub(r'^#.*$', '', content, flags=re.MULTILINE)
    body = body.strip()

    return body


def extract_title(content: str) -> str:
    """Извлекает заголовок файла."""
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        title = re.sub(r'[📜🔥🛡️⚔️📖🎯🧭💻👑❤️]\s*', '', title)
        return title
    return ""


def get_template(filepath: Path, title: str, category: str) -> str:
    """Создаёт шаблон заполнения для пустого файла."""
    today = datetime.now().strftime("%Y-%m-%d")
    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')

    templates = {
        "terminology": f"""# 📜 {title.upper()}

**Метаданные файла**
- **Файл:** `{rel_path}`
- **Версия:** 1.0
- **Дата создания:** {today}
- **Последнее обновление:** {today}
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** {title}

---

## 🔥 ВВЕДЕНИЕ

[Краткое введение — что это за слово, почему оно важно]

---

## 📜 ОРИГИНАЛ

**Иврит:** [ивритское написание]

**Транслитерация:** [транслитерация]

**Буквальный перевод:** [перевод]

---

## 🌱 КОРЕНЬ

**Корень:** [трёхбуквенный корень]

**Значение корня:** [значение]

**Однокоренные слова:** [список]

---

## 📖 КОНТЕКСТ В ТАНАХЕ

> [Стих на иврите]
> [Транслитерация]
> «[Перевод]» ([Книга глава:стих])

---

## ⚔️ ИСКАЖЕНИЕ И ВОЗВРАЩЕНИЕ

**[Искажённое слово]** → **[Правильное слово]**

[Описание подмены и возвращение к ивритскому смыслу]

---

## 🔗 СВЯЗАННЫЕ ИССЛЕДОВАНИЯ

[Ссылки на связанные файлы]

---

> **עֵד (Эд) — Свидетель.**
> [Итоговая мысль]
""",

        "researches": f"""# 📜 {title.upper()}

**Метаданные файла**
- **Файл:** `{rel_path}`
- **Версия:** 1.0
- **Дата создания:** {today}
- **Последнее обновление:** {today}
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** {title}

---

## 🔥 ВВЕДЕНИЕ

[Краткое введение — о чём это исследование]

---

## 📜 СУТЬ

[Основная часть исследования]

---

## 📖 СВИДЕТЕЛЬСТВО ТАНАХА

> [Стих на иврите]
> [Транслитерация]
> «[Перевод]» ([Книга глава:стих])

---

## ⚔️ РАЗОБЛАЧЕНИЕ

[Что система исказила и как вернуть истину]

---

## 🔗 СВЯЗАННЫЕ ИССЛЕДОВАНИЯ

[Ссылки на связанные файлы]

---

> **עֵד (Эд) — Свидетель.**
> [Итоговая мысль]
""",
    }

    return templates.get(category, templates["researches"])


def get_category(filepath: Path) -> str:
    """Определяет категорию файла."""
    parts = filepath.relative_to(REPO_ROOT).parts
    if parts:
        return parts[0]
    return "other"


def main():
    print_header("ЗАПОЛНЕНИЕ ПУСТЫХ ФАЙЛОВ", "📝")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    print(f"Найдено файлов: {total}")

    empty_files = []

    for i, filepath in enumerate(all_files, 1):
        content = read_file_safe(filepath)
        if not content:
            rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
            empty_files.append((filepath, rel_path, "пустой (ошибка чтения)"))
            continue

        body = extract_body(content)
        if len(body) < MIN_BODY_LENGTH:
            rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
            reason = f"почти пустой ({len(body)} символов)"
            empty_files.append((filepath, rel_path, reason))

        progress_bar(i, total, extra=f"пустых: {len(empty_files)}")

    finish_progress()

    if not empty_files:
        print_success("Пустых файлов не найдено")
        return 0

    print_warning(f"Найдено пустых/незаполненных файлов: {len(empty_files)}")
    for _, path, reason in empty_files[:20]:
        print(f"   • {path} — {reason}")
    if len(empty_files) > 20:
        print(f"   ... и ещё {len(empty_files) - 20}")

    if not ask_yes_no(f"\nЗаполнить {len(empty_files)} файлов шаблонами?"):
        print("👋 Отменено.")
        return 0

    filled = 0
    for i, (filepath, rel_path, _) in enumerate(empty_files, 1):
        content = read_file_safe(filepath) or ""
        title = extract_title(content) or filepath.stem.replace('-', ' ').title()
        category = get_category(filepath)
        template = get_template(filepath, title, category)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(template)

        filled += 1
        progress_bar(i, len(empty_files), extra=f"заполнено: {filled}")

    finish_progress()
    print_success(f"Заполнено файлов: {filled}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

