#!/usr/bin/env python3
# tools/checkers/check-metadata-consistency.py — сверка метаданных с реальными путями + автофикс
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
import argparse
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_error, print_warning, print_hint,
    ask_yes_no, REPO_ROOT
)

SCAN_DIRS = ["terminology", "researches", "instructions", "davar", "ideas", "drafts"]

METADATA_TEMPLATE = """**Метаданные файла**
- **Файл:** `{path}`
- **Версия:** 1.0
- **Дата создания:** {date}
- **Последнее обновление:** {date}
- **Причина обновления:** Первичное создание
- **Статус:** Активный
- **Тема:** TODO
- **Аудит:** bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳
- **Язык:** русский
- **Связанные файлы:** TODO
- **Хеш:** ожидает
- **Достоверность:** средняя
- **Последний аудит:** {date}
"""


def extract_metadata_field(content: str, field: str) -> str:
    """Извлекает значение поля из метаданных."""
    match = re.search(rf'[-*]\s*\*\*{field}:\*\*\s*`?([^`\n]+)`?', content)
    return match.group(1).strip() if match else ""


def check_file(filepath: Path, existing_paths: set) -> dict:
    """Проверяет один файл."""
    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
    content = read_file_safe(filepath)

    if not content:
        return {"path": rel_path, "issues": ["не удалось прочитать"]}

    has_metadata = '**Метаданные файла**' in content
    issues = []

    if not has_metadata:
        issues.append("нет блока метаданных")
        return {"path": rel_path, "issues": issues, "fix_type": "add_metadata"}

    # Проверка поля "Файл:"
    metadata_path = extract_metadata_field(content, "Файл:")
    if not metadata_path:
        issues.append("не указано поле 'Файл:'")
    else:
        metadata_path = metadata_path.replace('\\', '/')
        if metadata_path != rel_path:
            issues.append(f"путь: '{metadata_path}' → '{rel_path}'")

    # Проверка "Связанных файлов:"
    related_match = re.search(r'[-*]\s*\*\*Связанные файлы:\*\*\s*(.+?)(?:\n\n|\n[-*]|\Z)', content, re.DOTALL)
    if related_match:
        related_section = related_match.group(1)
        broken_related = []
        for m in re.finditer(r'`([^`]+\.md)`', related_section):
            link = m.group(1)
            if link not in existing_paths:
                broken_related.append(link)
        if broken_related:
            issues.append(f"битые связанные файлы: {', '.join(broken_related[:5])}")

    if not issues:
        return None

    result = {"path": rel_path, "issues": issues}
    if has_metadata and any("путь:" in i for i in issues):
        result["fix_type"] = "fix_path"
    return result


def add_metadata(filepath: Path) -> bool:
    """Добавляет блок метаданных в файл."""
    content = read_file_safe(filepath)
    if not content:
        return False

    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
    today = datetime.now().strftime('%Y-%m-%d')

    metadata = METADATA_TEMPLATE.format(path=rel_path, date=today)

    # Вставляем после первого заголовка H1 и разделителя ---
    h1_match = re.search(r'^#\s+.+$', content, re.MULTILINE)
    if h1_match:
        insert_pos = h1_match.end()
        # Ищем --- после заголовка
        next_sep = content.find('---', insert_pos)
        if next_sep != -1 and next_sep < insert_pos + 200:
            insert_pos = content.find('\n', next_sep) + 1
        else:
            insert_pos = content.find('\n', insert_pos) + 1

        new_content = content[:insert_pos] + '\n' + metadata + '\n---\n\n' + content[insert_pos:]
    else:
        new_content = content + '\n' + metadata + '\n---\n\n'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True


def fix_metadata_path(filepath: Path, old_path: str, new_path: str) -> bool:
    """Исправляет путь в метаданных."""
    content = read_file_safe(filepath)
    if not content:
        return False

    old = f"`{old_path}`"
    new = f"`{new_path}`"
    if old in content:
        new_content = content.replace(old, new, 1)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def main():
    fix_mode = "--fix" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    save_mode = "--save" in sys.argv

    print_header("ПРОВЕРКА ПУТЕЙ В МЕТАДАННЫХ", "🏷️")

    # Строим множество существующих путей
    all_files = []
    existing_paths = set()
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            for f in sorted(dir_path.rglob("*.md")):
                all_files.append(f)
                existing_paths.add(str(f.relative_to(REPO_ROOT)).replace('\\', '/'))

    total = len(all_files)
    print(f"🔍 Файлов: {total}")

    no_metadata = []
    path_issues = []
    link_issues = []
    fixed = 0
    total_issues_count = 0

    for i, filepath in enumerate(all_files, 1):
        result = check_file(filepath, existing_paths)
        if result:
            total_issues_count += len(result["issues"])

            if result.get("fix_type") == "add_metadata":
                no_metadata.append(result)
                if fix_mode and add_metadata(filepath):
                    fixed += 1
            elif result.get("fix_type") == "fix_path":
                path_issues.append(result)
                if fix_mode:
                    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
                    old = extract_metadata_field(read_file_safe(filepath) or "", "Файл:")
                    if old and fix_metadata_path(filepath, old, rel_path):
                        fixed += 1
            else:
                link_issues.append(result)

        progress_bar(i, total, extra=f"проблем: {total_issues_count}")

    finish_progress()

    if fix_mode:
        print_success(f"🔧 Исправлено: {fixed}")

    # Вывод
    if no_metadata:
        print_warning(f"\n📝 БЕЗ МЕТАДАННЫХ: {len(no_metadata)}")
        for item in (no_metadata if verbose else no_metadata[:5]):
            print(f"   • {item['path']}")
        if len(no_metadata) > 5 and not verbose:
            print(f"   ... и ещё {len(no_metadata) - 5}")

    if path_issues:
        print_error(f"\n📍 НЕСОВПАДЕНИЙ ПУТЕЙ: {len(path_issues)}")
        for item in (path_issues if verbose else path_issues[:10]):
            print(f"   • {item['path']}: {item['issues'][0]}")
        if len(path_issues) > 10 and not verbose:
            print(f"   ... и ещё {len(path_issues) - 10}")

    if link_issues:
        print_warning(f"\n🔗 БИТЫЕ СВЯЗАННЫЕ ФАЙЛЫ: {len(link_issues)}")
        for item in (link_issues if verbose else link_issues[:10]):
            print(f"   • {item['path']}: {', '.join(item['issues'])}")
        if len(link_issues) > 10 and not verbose:
            print(f"   ... и ещё {len(link_issues) - 10}")

    if not no_metadata and not path_issues and not link_issues:
        print_success("\n🎉 Все метаданные корректны")
    else:
        total = len(no_metadata) + len(path_issues) + len(link_issues)
        print(f"\n📝 Всего проблемных файлов: {total}")

    if save_mode:
        report = REPO_ROOT / "reports" / "metadata-consistency-report.md"
        lines = [
            "# 🏷️ ОТЧЁТ О МЕТАДАННЫХ",
            f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
        ]
        if no_metadata:
            lines.append(f"## Без метаданных ({len(no_metadata)})")
            for item in no_metadata:
                lines.append(f"- `{item['path']}`")
        if path_issues:
            lines.append(f"## Несовпадения путей ({len(path_issues)})")
            for item in path_issues:
                lines.append(f"- `{item['path']}`: {item['issues'][0]}")
        if link_issues:
            lines.append(f"## Битые связанные файлы ({len(link_issues)})")
            for item in link_issues:
                lines.append(f"- `{item['path']}`: {', '.join(item['issues'])}")
        report.parent.mkdir(exist_ok=True)
        report.write_text("\n".join(lines) + "\n", encoding='utf-8')
        print_success(f"Отчёт сохранён: {report}")

    if not fix_mode and (no_metadata or path_issues):
        print_hint("\n--fix — исправить пути и добавить метаданные")
    if link_issues:
        print_hint("Битые связанные файлы исправляются через check-links.py --fix")

    print()
    return 0 if not (no_metadata or path_issues) else 1


if __name__ == "__main__":
    sys.exit(main())