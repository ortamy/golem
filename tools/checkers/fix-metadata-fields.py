# tools/checkers/fix-metadata-fields.py — исправление полей метаданных (русский → правильный)
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_hint, ask_yes_no, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions", "davar", "ideas", "drafts", "docs"]

# Правильные названия полей
CORRECT_FIELDS = {
    "Файл:": ["Файл:", "файл:", "File:", "file:"],
    "Версия:": ["Версия:", "версия:", "Version:", "version:"],
    "Дата создания:": ["Дата создания:", "дата создания:", "Created:", "created:"],
    "Последнее обновление:": ["Последнее обновление:", "последнее обновление:", "Last updated:", "last updated:"],
    "Причина обновления:": ["Причина обновления:", "причина обновления:", "Reason:", "reason:"],
    "Статус:": ["Статус:", "статус:", "Status:", "status:"],
    "Тема:": ["Тема:", "тема:", "Topic:", "topic:"],
}

# Ивритские искажения → правильные поля
HEBREW_DISTORTIONS = {
    "итхадшут": "Последнее обновление:",
    "hитхадшут": "Последнее обновление:",
    "хидшут": "Последнее обновление:",
    "маамад": "Статус:",
    "носэ": "Тема:",
    "носе": "Тема:",
    "гуф": "Тема:",
    "шем": "Файл:",
    "гирса": "Версия:",
    "таарих": "Дата создания:",
    "таарих идун": "Последнее обновление:",
    "сиба": "Причина обновления:",
    "сманут": "Статус:",
}


def fix_metadata_fields(content: str) -> tuple:
    """Исправляет искажённые названия полей в метаданных. Возвращает (исправленный_текст, количество_исправлений)."""
    if '**Метаданные файла**' not in content:
        return content, 0

    fixed = content
    count = 0

    # 1. Исправляем искажённые русские поля
    for correct_field, variants in CORRECT_FIELDS.items():
        for variant in variants:
            if variant == correct_field:
                continue
            pattern = re.compile(r'([-*]\s*\*\*)' + re.escape(variant) + r'(\*\*\s*)', re.IGNORECASE)
            matches = pattern.findall(fixed)
            if matches:
                fixed = pattern.sub(r'\1' + correct_field + r'\2', fixed)
                count += len(matches)

    # 2. Исправляем ивритские искажения
    for heb_word, correct_field in HEBREW_DISTORTIONS.items():
        pattern = re.compile(r'([-*]\s*\*\*)' + re.escape(heb_word) + r'(\*\*\s*)', re.IGNORECASE)
        matches = pattern.findall(fixed)
        if matches:
            fixed = pattern.sub(r'\1' + correct_field + r'\2', fixed)
            count += len(matches)

    return fixed, count


def check_file(filepath: Path) -> dict:
    """Проверяет файл на искажения в метаданных."""
    content = read_file_safe(filepath)
    if not content:
        return None

    if '**Метаданные файла**' not in content:
        return None

    # Ищем все поля с нестандартными названиями
    issues = []
    field_pattern = re.compile(r'[-*]\s*\*\*([^*]+)\*\*\s*')
    for match in field_pattern.finditer(content):
        field_name = match.group(1).strip()
        # Проверяем, является ли поле стандартным
        is_standard = False
        for correct_field, variants in CORRECT_FIELDS.items():
            if field_name in variants or field_name == correct_field:
                is_standard = True
                break
        if not is_standard:
            issues.append(field_name)

    if issues:
        rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
        return {"path": rel_path, "issues": issues}

    return None


def main():
    fix_mode = "--fix" in sys.argv

    print_header("ИСПРАВЛЕНИЕ ПОЛЕЙ МЕТАДАННЫХ" if fix_mode else "ПРОВЕРКА ПОЛЕЙ МЕТАДАННЫХ",
                 "🔧" if fix_mode else "🔍")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    print(f"Найдено файлов: {total}")

    files_with_issues = []
    total_fixes = 0

    for i, filepath in enumerate(all_files, 1):
        if fix_mode:
            content = read_file_safe(filepath)
            if content:
                fixed_content, fixes = fix_metadata_fields(content)
                if fixes > 0:
                    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
                    files_with_issues.append((rel_path, fixes))
                    total_fixes += fixes
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
        else:
            result = check_file(filepath)
            if result:
                files_with_issues.append((result["path"], result["issues"]))

        progress_bar(i, total, extra=f"проблем: {len(files_with_issues)}")

    finish_progress()

    if not files_with_issues:
        print_success("Все поля метаданных корректны")
        return 0

    if fix_mode:
        print_warning(f"Исправлено полей: {total_fixes} в {len(files_with_issues)} файлах")
        for path, fixes in files_with_issues[:15]:
            print(f"  • {path} — {fixes} исправлений")
    else:
        print_warning(f"Файлов с искажёнными полями: {len(files_with_issues)}")
        for path, issues in files_with_issues[:15]:
            if isinstance(issues, list):
                print(f"  • {path}: {', '.join(issues[:3])}")
            else:
                print(f"  • {path} — {issues} полей")
        if len(files_with_issues) > 15:
            print(f"  ... и ещё {len(files_with_issues) - 15}")
        print_hint("Для исправления: python tools/checkers/fix-metadata-fields.py --fix")

    return 0


if __name__ == "__main__":
    sys.exit(main())

