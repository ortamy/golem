#!/usr/bin/env python3
# tools/find-duplicates.py — поиск дубликатов среди md-файлов
import sys
from pathlib import Path
from difflib import SequenceMatcher

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_error, REPO_ROOT

TARGET_DIRS = ['terminology', 'researches']
SIMILARITY_THRESHOLD = 0.85


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a[:1000].lower(), b[:1000].lower()).ratio()


def main():
    print_header("ПОИСК ДУБЛИКАТОВ")

    files = {}
    for target_dir in TARGET_DIRS:
        dir_path = REPO_ROOT / target_dir
        if dir_path.exists():
            for md_file in dir_path.rglob('*.md'):
                content = read_file_safe(md_file)
                if content:
                    files[str(md_file.relative_to(REPO_ROOT))] = content

    total = len(files)
    total_checks = total * (total - 1) // 2
    print(f"Найдено файлов: {total}")
    print(f"Сравнений: {total_checks}")

    duplicates = []
    file_list = list(files.items())
    checked = 0

    for i, (name1, content1) in enumerate(file_list):
        for name2, content2 in file_list[i + 1:]:
            sim = similarity(content1, content2)
            if sim >= SIMILARITY_THRESHOLD:
                duplicates.append((name1, name2, sim))
            checked += 1
            if checked % 50 == 0 or checked == total_checks:
                progress_bar(checked, total_checks, extra=f"дубликатов: {len(duplicates)}")

    finish_progress()

    if duplicates:
        print_error(f"НАЙДЕНО ДУБЛИКАТОВ: {len(duplicates)}")
        for name1, name2, sim in sorted(duplicates, key=lambda x: x[2], reverse=True)[:10]:
            print(f"   • {name1} ↔ {name2} (схожесть: {sim:.0%})")
        if len(duplicates) > 10:
            print(f"   ... и ещё {len(duplicates) - 10}")
        return 1
    else:
        print_success("Дубликатов не найдено")

    return 0


if __name__ == "__main__":
    sys.exit(main())

