# tools/utils/clear-cache.py — clear cache
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import print_header, print_success, print_warning, ask_yes_no, REPO_ROOT

CACHE_DIR = REPO_ROOT / "tools" / "cache"


def format_size(size: int) -> str:
    if size < 1024:
        return f"{size} Б"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} КБ"
    else:
        return f"{size / (1024 * 1024):.1f} МБ"


def main():
    all_mode = "--all" in sys.argv
    force = "--force" in sys.argv or "-f" in sys.argv

    if all_mode:
        print_header("СБРОС ВСЕГО КЭША", "🗑️")
    else:
        print_header("СБРОС КЭША", "🗑️")

    if not CACHE_DIR.exists():
        print_success("Кэш пуст, нечего сбрасывать")
        return 0

    if all_mode:
        files = list(CACHE_DIR.glob("*"))
    else:
        # Только известные файлы кэша
        known = [
            "religionisms-cache.json",
            "scan-cache.json",
            "dirty-files.json",
            "golem-config.json",
            "exposure-cache.json",
        ]
        files = [CACHE_DIR / f for f in known if (CACHE_DIR / f).exists()]
        # Плюс логи проверок
        files.extend(sorted(CACHE_DIR.glob("checks_*.log")))

    if not files:
        print_success("Кэш пуст, нечего сбрасывать")
        return 0

    total_size = sum(f.stat().st_size for f in files)
    print(f"📁 Файлов кэша: {len(files)}")
    print(f"📊 Общий размер: {format_size(total_size)}")
    print()

    for f in sorted(files, key=lambda x: x.stat().st_size, reverse=True):
        size = f.stat().st_size
        print(f"  • {f.name} ({format_size(size)})")

    if not force and not ask_yes_no(f"\n🗑️ Удалить {len(files)} файлов?"):
        print("👋 Отменено.")
        return 0

    removed = 0
    for f in files:
        try:
            f.unlink()
            removed += 1
        except:
            print_warning(f"Не удалось удалить: {f.name}")

    # Если папка пуста — удаляем и её
    if all_mode:
        try:
            remaining = list(CACHE_DIR.glob("*"))
            if not remaining:
                CACHE_DIR.rmdir()
        except:
            pass

    print_success(f"✅ Удалено: {removed} файлов ({format_size(total_size)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())