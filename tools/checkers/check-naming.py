#!/usr/bin/env python3
# tools/check-naming.py — проверка имён md-файлов
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import progress_bar, finish_progress, print_header, print_success, print_error, REPO_ROOT

IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__', 'reports', 'neural'}
IGNORE_FILES = {'README.md', 'CHANGELOG.md', 'BACKLOG.md', 'CONTRIBUTORS.md',
                'DECISIONS.md', 'GLOSSARY.md', 'RETROSPECTIVE.md', 'ROADMAP.md',
                'STRUCTURE.md', 'TECHNICAL-DEBT.md', 'STATS.md', 'COMPLETED-TASKS.md'}
ALLOWED_PATTERN = re.compile(r'^[a-z][a-z0-9\-]*\.md$')


def get_all_md_files():
    files = []
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        rel_path = md_file.relative_to(REPO_ROOT)
        if rel_path.parts[0] in IGNORE_DIRS:
            continue
        if md_file.name in IGNORE_FILES:
            continue
        files.append((rel_path, md_file))
    return files


def check_name(name):
    if not ALLOWED_PATTERN.match(name):
        return False, f"неверный формат: {name}"
    if re.search(r'[а-яё]', name, re.IGNORECASE):
        return False, f"русские буквы: {name}"
    return True, ""


def main():
    print_header("ПРОВЕРКА ИМЁН ФАЙЛОВ")

    files = get_all_md_files()
    total = len(files)
    errors = []
    print(f"Найдено файлов: {total}")

    for i, (rel_path, md_file) in enumerate(files, 1):
        is_valid, error_msg = check_name(md_file.name)
        if not is_valid:
            errors.append((rel_path, error_msg))
        progress_bar(i, total, extra=f"ошибок: {len(errors)}")

    finish_progress()

    if errors:
        print_error(f"НАРУШЕНИЯ: {len(errors)}")
        for rel_path, error_msg in errors[:20]:
            print(f"   • {rel_path}: {error_msg}")
        if len(errors) > 20:
            print(f"   ... и ещё {len(errors) - 20}")
        return 1
    else:
        print_success(f"Все {total} файлов названы корректно")

    return 0


if __name__ == "__main__":
    sys.exit(main())

