#!/usr/bin/env python3
# tools/checkers/check-encoding.py — конвертация Windows-1251 → UTF-8
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import argparse
# from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, ask_yes_no, REPO_ROOT  # TODO: проверить, используется ли

SCAN_DIRS = ["researches/religionizmes", "researches/teachings"]


def fix_file(filepath: Path) -> bool:
    """Конвертирует файл в UTF-8 если он в другой кодировке."""
    try:
        # Пробуем прочитать как UTF-8
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        # Проверяем, нет ли кракозябр
        if 'Рџ' not in content and 'СЂ' not in content:
            return False  # Уже UTF-8
    except UnicodeDecodeError:
        pass

    # Пробуем Windows-1251
    try:
        with open(filepath, 'r', encoding='cp1251') as f:
            content = f.read()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False


def main():
    print_header("КОНВЕРТАЦИЯ КОДИРОВКИ → UTF-8", "📝")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    print(f"Найдено файлов: {total}")

    if total == 0:
        print_warning("Папки не найдены")
        return 0

    fixed = 0
    for i, filepath in enumerate(all_files, 1):
        if fix_file(filepath):
            fixed += 1
        progress_bar(i, total, extra=f"исправлено: {fixed}")

    finish_progress()
    print_success(f"Конвертировано в UTF-8: {fixed} файлов")
    return 0


if __name__ == "__main__":
    sys.exit(main())

