#!/usr/bin/env python3
# tools/checkers/clear-cache.py — сброс всего кэша проекта
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import print_header, print_success, ask_yes_no, REPO_ROOT

CACHE_DIR = REPO_ROOT / "tools" / "cache"
CACHE_FILES = [
    "religionisms-cache.json",
    "scan-cache.json",
    "dirty-files.json",
    "golem-config.json",
]


def main():
    print_header("СБРОС КЭША", "🗑️")

    if not CACHE_DIR.exists():
        print_success("Кэш пуст, нечего сбрасывать")
        return 0

    files = [f for f in CACHE_FILES if (CACHE_DIR / f).exists()]

    if not files:
        print_success("Кэш пуст, нечего сбрасывать")
        return 0

    print(f"Найдено файлов кэша: {len(files)}")
    for f in files:
        size = (CACHE_DIR / f).stat().st_size
        print(f"  • {f} ({size:,} байт)")

    if not ask_yes_no("\nУдалить все файлы кэша?"):
        print("👋 Отменено.")
        return 0

    for f in files:
        (CACHE_DIR / f).unlink()
        print(f"  ✓ {f} удалён")

    print_success(f"Удалено {len(files)} файлов кэша")
    return 0


if __name__ == "__main__":
    sys.exit(main())

