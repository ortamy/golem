#!/usr/bin/env python3
# tools/checkers/check-empty-files.py — поиск и исправление пустых md-файлов
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_warning, print_hint, print_error,
    ask_yes_no, REPO_ROOT
)

SCAN_DIRS = ["terminology", "researches", "instructions", "davar", "ideas", "drafts"]
MIN_CONTENT_LENGTH = 200
TODO_PATTERN = re.compile(
    r'TODO|FIXME|ЗАПОЛНИТЬ|НАПИСАТЬ|ВСТАВИТЬ|ДОПИСАТЬ|'
    r'ОПИСАТЬ|ДОБАВИТЬ|РАСКРЫТЬ|УТОЧНИТЬ|'
    r'здесь будет|здесь должен|в разработке|coming soon|tbd|'
    r'ожидает|placeholder|заглушка|'
    r'будет добавлено|будет описано|будет раскрыто',
    re.IGNORECASE
)

TEMPLATE_BODY = """## 🔥 ВВЕДЕНИЕ

TODO: краткое введение — о чём этот файл, почему это важно.

---

## 📜 ОСНОВНАЯ ЧАСТЬ

TODO: раскрыть тему. Добавить стихи ТаНаХа, разбор корней, контекст.

---

## 📊 ИТОГО

TODO: краткий итог — что мы узнали, как это применить.

---

> **הַדֶּרֶךְ יְהוָה**
> **hа-Де́рех Яхве**
> *Путь Яхве*

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ
TODO: добавить ссылки на связанные файлы
"""


def find_all_md_files():
    """Находит все md-файлы в сканируемых папках."""
    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))
    return all_files


def build_file_set(all_files):
    """Строит множество относительных путей для проверки ссылок."""
    return {str(f.relative_to(REPO_ROOT)).replace('\\', '/') for f in all_files}


def check_file(filepath: Path, file_set: set) -> dict:
    """Проверяет файл на пустоту/незаполненность."""
    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
    content = read_file_safe(filepath)

    if not content:
        return {
            "path": rel_path,
            "issues": ["пустой файл (ошибка чтения)"],
            "category": "empty"
        }

    issues = []
    categories = set()

    body = re.sub(r'\*\*Метаданные файла\*\*.*?(?=\n#|\n---|\Z)', '', content, flags=re.DOTALL)
    body = re.sub(r'^#.*$', '', body, flags=re.MULTILINE)
    body = body.strip()

    if len(body) < 50:
        issues.append(f"почти пустой ({len(body)} символов содержания)")
        categories.add("empty")

    elif len(body) < MIN_CONTENT_LENGTH:
        issues.append(f"мало содержания ({len(body)} символов)")
        categories.add("small")

    todo_matches = TODO_PATTERN.findall(content)
    if todo_matches:
        unique = list(set(todo_matches))[:5]
        issues.append(f"маркеры: {', '.join(unique)}")
        categories.add("todo")

    last_lines = "\n".join(body.splitlines()[-3:])
    if re.search(r'\.{3,}|···|\.\.\.\s*$', last_lines):
        issues.append("обрывается на маркере пустоты")
        categories.add("todo")

    links = re.findall(r'`([^`]+\.md)`', content)
    broken = [l for l in links if l not in file_set]
    if broken:
        issues.append(f"битые ссылки: {', '.join(broken[:5])}")
        categories.add("broken")

    if not issues:
        return None

    return {
        "path": rel_path,
        "issues": issues,
        "category": "empty" if "empty" in categories else
                    "todo" if "todo" in categories else
                    "broken" if "broken" in categories else
                    "small",
        "broken_links": broken if broken else [],
    }


def find_duplicate_titles(all_files):
    """Находит файлы с одинаковыми H1."""
    titles = {}
    for fp in all_files:
        content = read_file_safe(fp)
        if not content:
            continue
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            title = match.group(1).strip().lower()
            rel = str(fp.relative_to(REPO_ROOT)).replace('\\', '/')
            titles.setdefault(title, []).append(rel)
    return {t: fs for t, fs in titles.items() if len(fs) > 1}


def fix_empty_file(filepath: Path):
    """Добавляет шаблон содержания в почти пустой файл."""
    content = read_file_safe(filepath)
    if not content:
        return False

    marker = "---\n"
    next_marker = content.find("\n---", len(marker))
    if next_marker == -1:
        next_marker = content.find("---", len(marker))

    if next_marker != -1:
        insert_pos = next_marker + 4
        new_content = content[:insert_pos] + "\n" + TEMPLATE_BODY + "\n" + content[insert_pos:]
    else:
        new_content = content.rstrip() + "\n" + TEMPLATE_BODY + "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def fix_broken_links(filepath: Path, broken_links: list):
    """Удаляет битые ссылки из файла."""
    content = read_file_safe(filepath)
    if not content:
        return 0

    fixed = 0
    for link in broken_links:
        escaped = re.escape(link)
        new_content = re.sub(rf'^.*`{escaped}`.*$\n?', '', content, flags=re.MULTILINE)
        if new_content != content:
            content = new_content
            fixed += 1

    if fixed > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    return fixed


def fix_duplicate_titles(duplicates: dict):
    """Добавляет комментарий в файлы с дублирующимися заголовками."""
    fixed = 0
    for title, files in duplicates.items():
        for rel_path in files:
            filepath = REPO_ROOT / rel_path
            content = read_file_safe(filepath)
            if not content:
                continue
            if "⚠️ ДУБЛИКАТ ЗАГОЛОВКА" not in content:
                comment = f"\n<!-- ⚠️ ДУБЛИКАТ ЗАГОЛОВКА: \"{title}\" также используется в других файлах -->\n"
                new_content = re.sub(
                    rf'(^#\s+{re.escape(title)}.*$\n)',
                    rf'\1{comment}',
                    content,
                    count=1,
                    flags=re.MULTILINE | re.IGNORECASE
                )
                if new_content != content:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    fixed += 1
    return fixed


def add_to_techdebt(empty_files):
    """Добавляет пустые файлы в TECHNICAL-DEBT.md."""
    techdebt_path = REPO_ROOT / "docs" / "TECHNICAL-DEBT.md"
    if not techdebt_path.exists():
        return False

    content = read_file_safe(techdebt_path)
    if not content:
        return False

    section = "### Заполнить пустые файлы"
    new_entries = []
    for item in empty_files:
        entry = f"- [ ] Заполнить содержимым `{item['path']}`"
        if entry not in content:
            new_entries.append(entry)

    if not new_entries:
        return False

    if section in content:
        lines = content.splitlines()
        new_lines = []
        added = False
        for line in lines:
            new_lines.append(line)
            if line.strip() == section and not added:
                for entry in new_entries:
                    new_lines.append(entry)
                added = True
        if added:
            with open(techdebt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines) + "\n")
            return True

    return False


def save_report(empty_files, small_files, todo_files, broken_files, duplicates):
    """Сохраняет отчёт в файл."""
    report_path = REPO_ROOT / "reports" / "empty-files-report.md"
    report_path.parent.mkdir(exist_ok=True)

    lines = [
        f"# 👻 ОТЧЁТ О ПУСТЫХ ФАЙЛАХ",
        f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    for title, items in [
        ("👻 ПУСТЫЕ ФАЙЛЫ", empty_files),
        ("📝 ФАЙЛЫ С МАРКЕРАМИ", todo_files),
        ("🔗 ФАЙЛЫ С БИТЫМИ ССЫЛКАМИ", broken_files),
        ("📊 ФАЙЛЫ С МАЛЫМ СОДЕРЖАНИЕМ", small_files),
    ]:
        if items:
            lines.append(f"## {title} ({len(items)})")
            for item in items:
                lines.append(f"- `{item['path']}` — {', '.join(item['issues'])}")
            lines.append("")

    if duplicates:
        lines.append(f"## 📋 ДУБЛИКАТЫ ЗАГОЛОВКОВ ({len(duplicates)})")
        for title, files in duplicates.items():
            lines.append(f"- **{title}**: {', '.join(f'`{f}`' for f in files)}")
        lines.append("")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return report_path


def main_fix(empty_files, todo_files, broken_files, duplicates):
    """Запускает все исправления с компактным прогресс-баром."""
    print()
    print_header("АВТОФИКС", "🔧")

    total_ops = len(empty_files) + len(broken_files) + (1 if duplicates else 0) + (1 if (empty_files or todo_files) else 0)
    current = 0
    stats = {"templates": 0, "links": 0, "duplicates": 0, "techdebt": 0}

    # Шаблоны в пустые файлы
    for item in empty_files:
        filepath = REPO_ROOT / item["path"]
        if fix_empty_file(filepath):
            stats["templates"] += 1
        current += 1
        progress_bar(current, total_ops, extra=f"шаблонов: {stats['templates']}")

    # Битые ссылки
    for item in broken_files:
        if item.get("broken_links"):
            filepath = REPO_ROOT / item["path"]
            fixed = fix_broken_links(filepath, item["broken_links"])
            stats["links"] += fixed
        current += 1
        progress_bar(current, total_ops, extra=f"ссылок: {stats['links']}")

    # Дубликаты
    if duplicates:
        stats["duplicates"] = fix_duplicate_titles(duplicates)
    current += 1
    progress_bar(current, total_ops, extra=f"дубликатов: {stats['duplicates']}")

    # Техдолг
    if empty_files or todo_files:
        if add_to_techdebt(empty_files + todo_files):
            stats["techdebt"] = len(empty_files) + len(todo_files)
    current += 1
    progress_bar(current, total_ops, extra=f"в техдолг: {stats['techdebt']}")

    finish_progress()

    total_fixed = sum(stats.values())
    print_success(f"\n✅ Исправлено: шаблонов {stats['templates']}, ссылок {stats['links']}, дубликатов {stats['duplicates']}, в техдолг {stats['techdebt']}")
    print(f"   Всего: {total_fixed}")

    return 0


def main():
    fix_mode = "--fix" in sys.argv
    save_mode = "--save" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print_header("ПОИСК ПУСТЫХ И НЕЗАПОЛНЕННЫХ ФАЙЛОВ", "👻")

    all_files = find_all_md_files()
    file_set = build_file_set(all_files)
    total = len(all_files)

    if total == 0:
        print_error("md-файлы не найдены")
        return 1

    print(f"🔍 Проверяю файлов: {total}\n")

    empty_files = []
    small_files = []
    todo_files = []
    broken_files = []

    for i, filepath in enumerate(all_files, 1):
        result = check_file(filepath, file_set)
        if result:
            cat = result["category"]
            if cat == "empty":
                empty_files.append(result)
            elif cat == "todo":
                todo_files.append(result)
            elif cat == "broken":
                broken_files.append(result)
            else:
                small_files.append(result)

        progress_bar(i, total, extra=f"проблем: {len(empty_files) + len(todo_files) + len(broken_files) + len(small_files)}")

    finish_progress()

    duplicates = find_duplicate_titles(all_files)

    sections = [
        ("👻 ПУСТЫЕ ФАЙЛЫ", empty_files),
        ("📝 ФАЙЛЫ С МАРКЕРАМИ", todo_files),
        ("🔗 ФАЙЛЫ С БИТЫМИ ССЫЛКАМИ", broken_files),
        ("📊 ФАЙЛЫ С МАЛЫМ СОДЕРЖАНИЕМ", small_files),
    ]

    for title, items in sections:
        if items:
            print(f"\n{title}: {len(items)}")
            for item in (items[:20] if not verbose else items):
                print(f"   • {item['path']} — {', '.join(item['issues'])}")
            if len(items) > 20 and not verbose:
                print(f"   ... и ещё {len(items) - 20}")

    if duplicates:
        print(f"\n📋 ДУБЛИКАТЫ ЗАГОЛОВКОВ: {len(duplicates)}")
        for title, files in list(duplicates.items())[:10]:
            print(f"   • \"{title}\": {', '.join(files[:3])}")

    total_issues = len(empty_files) + len(todo_files) + len(broken_files) + len(small_files)

    if total_issues == 0 and not duplicates:
        print_success("\n🎉 Все файлы заполнены!")
        return 0

    print(f"\n📝 Всего проблемных файлов: {total_issues}")
    if duplicates:
        print(f"📋 Дубликатов заголовков: {len(duplicates)}")

    if fix_mode:
        main_fix(empty_files, todo_files, broken_files, duplicates)

    if save_mode:
        report_path = save_report(empty_files, small_files, todo_files, broken_files, duplicates)
        print_success(f"Отчёт сохранён: {report_path}")

    if not fix_mode and not save_mode and total_issues > 0:
        if ask_yes_no("\n🔧 Запустить автофикс?"):
            main_fix(empty_files, todo_files, broken_files, duplicates)

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())