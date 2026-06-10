#!/usr/bin/env python3
# tools/checkers/check-file-sizes.py — анализ размеров md-файлов
import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import (
    progress_bar, finish_progress, print_header, print_success,
    print_warning, print_hint, ask_yes_no, REPO_ROOT
)

SCAN_DIRS = ["terminology", "researches", "instructions", "davar", "ideas", "drafts", "docs"]
IGNORE_FILES = {"README.md", "STRUCTURE.md", "GLOSSARY.md", "STATS.md", "CHANGELOG.md"}

# Пороги по умолчанию
TOO_SMALL = 100
SUSPICIOUS_SMALL = 300
TOO_LARGE = 100_000
SUSPICIOUS_LARGE = 50_000

# Диапазоны для гистограммы
SIZE_BUCKETS = [
    (0, 100, "0–100 Б"),
    (100, 500, "100–500 Б"),
    (500, 1_000, "0.5–1 КБ"),
    (1_000, 5_000, "1–5 КБ"),
    (5_000, 10_000, "5–10 КБ"),
    (10_000, 25_000, "10–25 КБ"),
    (25_000, 50_000, "25–50 КБ"),
    (50_000, 100_000, "50–100 КБ"),
    (100_000, 1_000_000, ">100 КБ"),
]


def format_size(size: int) -> str:
    if size < 1024:
        return f"{size} Б"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} КБ"
    else:
        return f"{size / (1024 * 1024):.1f} МБ"


def add_to_techdebt(files: list):
    """Добавляет пустые файлы в TECHNICAL-DEBT.md."""
    techdebt_path = REPO_ROOT / "docs" / "TECHNICAL-DEBT.md"
    if not techdebt_path.exists():
        return False

    from lib.utils import read_file_safe
    content = read_file_safe(techdebt_path)
    if not content:
        return False

    section = "### Заполнить пустые файлы"
    new_entries = []
    for path, size in files:
        entry = f"- [ ] Заполнить содержимым `{path}` ({format_size(size)})"
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


def main():
    # Аргументы
    fix_mode = "--fix" in sys.argv
    save_mode = "--save" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    global TOO_SMALL, SUSPICIOUS_SMALL, TOO_LARGE, SUSPICIOUS_LARGE
    if "--too-small" in sys.argv:
        TOO_SMALL = int(sys.argv[sys.argv.index("--too-small") + 1])
    if "--too-large" in sys.argv:
        TOO_LARGE = int(sys.argv[sys.argv.index("--too-large") + 1])

    print_header("АНАЛИЗ РАЗМЕРОВ ФАЙЛОВ", "📊")
    print(f"Пороги: пустой <{format_size(TOO_SMALL)}, большой >{format_size(SUSPICIOUS_LARGE)}, аномальный >{format_size(TOO_LARGE)}")

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

    total = len(all_files)
    print(f"\n🔍 Обрабатываю файлов: {total}")

    # Собираем статистику
    file_stats = []
    by_folder = defaultdict(list)
    size_distribution = Counter()

    for i, md_file in enumerate(all_files, 1):
        size = md_file.stat().st_size
        rel_path = str(md_file.relative_to(REPO_ROOT)).replace('\\', '/')
        file_stats.append((rel_path, size))

        # По папкам
        folder = rel_path.split('/')[0]
        by_folder[folder].append((rel_path, size))

        # Распределение
        for low, high, label in SIZE_BUCKETS:
            if low <= size < high:
                size_distribution[label] += 1
                break

        progress_bar(i, total)

    finish_progress()

    file_stats.sort(key=lambda x: x[1])
    sizes = [s for _, s in file_stats]
    total_size = sum(sizes)
    avg_size = total_size / len(sizes) if sizes else 0

    # Общая статистика
    print(f"\n📊 ОБЩАЯ СТАТИСТИКА")
    print(f"  Файлов: {len(file_stats)}")
    print(f"  Общий размер: {format_size(total_size)}")
    print(f"  Средний: {format_size(int(avg_size))}")
    print(f"  Минимальный: {format_size(min(sizes))}")
    print(f"  Медиана: {format_size(sorted(sizes)[len(sizes)//2])}")
    print(f"  Максимальный: {format_size(max(sizes))}")

    # Распределение
    print(f"\n📊 РАСПРЕДЕЛЕНИЕ РАЗМЕРОВ")
    max_count = max(size_distribution.values()) if size_distribution else 1
    for _, _, label in SIZE_BUCKETS:
        count = size_distribution.get(label, 0)
        bar = "█" * min(count * 30 // max_count, 30) if max_count > 0 else ""
        print(f"  {label:12} {count:4}  {bar}")

    # По папкам
    print(f"\n📊 ПО ПАПКАМ")
    for folder in sorted(by_folder.keys()):
        folder_sizes = [s for _, s in by_folder[folder]]
        print(f"  {folder:20} {len(folder_sizes):4} файлов  {format_size(sum(folder_sizes)):>10}  (средн. {format_size(int(sum(folder_sizes)/len(folder_sizes)))})")

    # Пустые файлы
    empty_files = [(p, s) for p, s in file_stats if s < TOO_SMALL]
    small_files = [(p, s) for p, s in file_stats if TOO_SMALL <= s < SUSPICIOUS_SMALL]
    large_files = [(p, s) for p, s in file_stats if s > SUSPICIOUS_LARGE]
    huge_files = [(p, s) for p, s in file_stats if s > TOO_LARGE]

    if empty_files:
        print_warning(f"\n👻 ПУСТЫЕ ФАЙЛЫ (<{format_size(TOO_SMALL)}): {len(empty_files)}")
        for path, size in (empty_files if verbose else empty_files[:10]):
            print(f"   • {path} — {format_size(size)}")
        if len(empty_files) > 10 and not verbose:
            print(f"   ... и ещё {len(empty_files) - 10}")

    if small_files:
        print_warning(f"\n📝 ОЧЕНЬ МАЛЕНЬКИЕ (<{format_size(SUSPICIOUS_SMALL)}): {len(small_files)}")
        for path, size in (small_files if verbose else small_files[:10]):
            print(f"   • {path} — {format_size(size)}")
        if len(small_files) > 10 and not verbose:
            print(f"   ... и ещё {len(small_files) - 10}")

    if huge_files:
        print_warning(f"\n🚨 АНОМАЛЬНО БОЛЬШИЕ (>{format_size(TOO_LARGE)}): {len(huge_files)}")
        for path, size in huge_files:
            print(f"   • {path} — {format_size(size)}")
    elif large_files:
        print(f"\n📊 БОЛЬШИЕ (>{format_size(SUSPICIOUS_LARGE)}): {len(large_files)}")
        for path, size in (large_files if verbose else large_files[:10]):
            print(f"   • {path} — {format_size(size)}")
        if len(large_files) > 10 and not verbose:
            print(f"   ... и ещё {len(large_files) - 10}")

    # Дубликаты по размеру
    size_groups = defaultdict(list)
    for path, size in file_stats:
        size_groups[size].append(path)
    duplicates = {s: ps for s, ps in size_groups.items() if len(ps) > 1 and s > 100}
    if duplicates:
        print(f"\n📋 ДУБЛИКАТЫ ПО РАЗМЕРУ ({len(duplicates)} размеров):")
        for size, paths in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"  {format_size(size)}: {len(paths)} файлов — {', '.join(paths[:3])}")

    # Топ-10
    print(f"\n📊 ТОП-10 САМЫХ БОЛЬШИХ:")
    for path, size in sorted(file_stats, key=lambda x: x[1], reverse=True)[:10]:
        bar = "█" * min(int(size / max(sizes) * 25), 25)
        print(f"  {format_size(size):>8}  {bar}  {path}")

    # Автофикс
    total_issues = len(empty_files) + len(huge_files)
    if total_issues == 0:
        print_success("\n🎉 Все размеры в норме")
    else:
        if fix_mode:
            if empty_files and ask_yes_no(f"\n🔧 Добавить {len(empty_files)} пустых файлов в техдолг?"):
                if add_to_techdebt(empty_files):
                    print_success(f"Добавлено: {len(empty_files)}")
        else:
            print_hint(f"\nПустых: {len(empty_files)}, аномальных: {len(huge_files)}")
            print_hint("--fix — добавить пустые в техдолг")

    if save_mode:
        report = REPO_ROOT / "reports" / "file-sizes-report.md"
        lines = [
            "# 📊 ОТЧЁТ О РАЗМЕРАХ ФАЙЛОВ",
            "",
            f"**Файлов:** {len(file_stats)}",
            f"**Общий размер:** {format_size(total_size)}",
            f"**Средний:** {format_size(int(avg_size))}",
            "",
            "## 📊 По папкам",
        ]
        for folder in sorted(by_folder.keys()):
            fs = [s for _, s in by_folder[folder]]
            lines.append(f"- **{folder}**: {len(fs)} файлов, {format_size(sum(fs))}")
        if empty_files:
            lines.append(f"\n## 👻 Пустые ({len(empty_files)})")
            for p, s in empty_files:
                lines.append(f"- `{p}` — {format_size(s)}")
        report.parent.mkdir(exist_ok=True)
        report.write_text("\n".join(lines) + "\n", encoding='utf-8')
        print_success(f"Отчёт сохранён: {report}")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())