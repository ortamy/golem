# tools/checkers/check-file-sizes.py — анализ размеров md-файлов
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import progress_bar, finish_progress, print_header, print_success, print_warning, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions", "davar", "ideas", "drafts", "docs"]
IGNORE_FILES = {"README.md", "STRUCTURE.md", "GLOSSARY.md", "STATS.md"}

# Пороги в байтах
TOO_SMALL = 100       # меньше — пустышка
SUSPICIOUS_SMALL = 300  # подозрительно мало
TOO_LARGE = 100_000   # больше — аномально большой
SUSPICIOUS_LARGE = 50_000  # подозрительно много


def get_size_category(size: int) -> str:
    if size < TOO_SMALL:
        return "пустой"
    if size < SUSPICIOUS_SMALL:
        return "очень маленький"
    if size > TOO_LARGE:
        return "аномально большой"
    if size > SUSPICIOUS_LARGE:
        return "большой"
    return "нормальный"


def format_size(size: int) -> str:
    if size < 1024:
        return f"{size} Б"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} КБ"
    else:
        return f"{size / (1024 * 1024):.1f} МБ"


def main():
    print_header("АНАЛИЗ РАЗМЕРОВ ФАЙЛОВ", "📊")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            for md_file in dir_path.rglob("*.md"):
                if md_file.name not in IGNORE_FILES:
                    all_files.append(md_file)

    if not all_files:
        print("❌ Файлы не найдены")
        return 1

    # Собираем статистику
    file_stats = []
    for md_file in all_files:
        size = md_file.stat().st_size
        rel_path = str(md_file.relative_to(REPO_ROOT)).replace('\\', '/')
        file_stats.append((rel_path, size))

    file_stats.sort(key=lambda x: x[1])

    # Группируем
    empty_files = [(p, s) for p, s in file_stats if s < TOO_SMALL]
    small_files = [(p, s) for p, s in file_stats if TOO_SMALL <= s < SUSPICIOUS_SMALL]
    large_files = [(p, s) for p, s in file_stats if s > SUSPICIOUS_LARGE]
    huge_files = [(p, s) for p, s in file_stats if s > TOO_LARGE]

    # Общая статистика
    sizes = [s for _, s in file_stats]
    total_size = sum(sizes)
    avg_size = total_size / len(sizes) if sizes else 0

    print(f"Всего файлов: {len(file_stats)}")
    print(f"Общий размер: {format_size(total_size)}")
    print(f"Средний размер: {format_size(int(avg_size))}")
    print(f"Минимальный: {format_size(min(sizes))}")
    print(f"Максимальный: {format_size(max(sizes))}")

    # Самые маленькие
    if empty_files:
        print_warning(f"\nПУСТЫЕ ФАЙЛЫ (<{TOO_SMALL} Б): {len(empty_files)}")
        for path, size in empty_files:
            print(f"   • {path} — {format_size(size)}")

    if small_files:
        print_warning(f"\nОЧЕНЬ МАЛЕНЬКИЕ ФАЙЛЫ (<{SUSPICIOUS_SMALL} Б): {len(small_files)}")
        for path, size in small_files[:10]:
            print(f"   • {path} — {format_size(size)}")
        if len(small_files) > 10:
            print(f"   ... и ещё {len(small_files) - 10}")

    # Самые большие
    if huge_files:
        print_warning(f"\nАНОМАЛЬНО БОЛЬШИЕ ФАЙЛЫ (>{format_size(TOO_LARGE)}): {len(huge_files)}")
        for path, size in huge_files:
            print(f"   • {path} — {format_size(size)}")
    elif large_files:
        print(f"\n📊 БОЛЬШИЕ ФАЙЛЫ (>{format_size(SUSPICIOUS_LARGE)}): {len(large_files)}")
        for path, size in large_files[:10]:
            print(f"   • {path} — {format_size(size)}")
        if len(large_files) > 10:
            print(f"   ... и ещё {len(large_files) - 10}")

    # Топ-10 самых больших
    print(f"\n📊 ТОП-10 САМЫХ БОЛЬШИХ:")
    for path, size in sorted(file_stats, key=lambda x: x[1], reverse=True)[:10]:
        bar = "█" * min(int(size / max(sizes) * 30), 30)
        print(f"  {format_size(size):>8}  {bar}  {path}")

    total_issues = len(empty_files) + len(huge_files)
    if total_issues == 0:
        print_success("\nВсе размеры в норме")

    return 0


if __name__ == "__main__":
    sys.exit(main())

