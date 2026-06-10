#!/usr/bin/env python3
# tools/stats-report.py
# import sys  # TODO: проверить, используется ли
# import os  # TODO: проверить, используется ли
import re
# import json  # TODO: проверить, используется ли
# import subprocess  # TODO: проверить, используется ли
from pathlib import Path
from datetime import datetime
from collections import Counter
from progress import show_progress, finish_progress

REPO_ROOT = Path(__file__).parent.parent
REPORT_DIR = REPO_ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

TARGET_DIRS = ['terminology', 'researches', 'instructions', 'checkers', 'davar', 'ideas', 'drafts', 'tools']


def count_files() -> dict:
    stats = {}
    for dir_name in TARGET_DIRS:
        dir_path = REPO_ROOT / dir_name
        if dir_path.exists():
            count = len(list(dir_path.rglob('*.md')))
            stats[dir_name] = count
        else:
            stats[dir_name] = 0

    root_md = len(list(REPO_ROOT.glob('*.md'))) - 1
    stats['root'] = root_md
    return stats


def count_lines() -> dict:
    lines = 0
    files = 0

    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        with open(md_file, 'r', encoding='utf-8') as f:
            lines += len(f.readlines())
            files += 1

    return {'files': files, 'lines': lines, 'avg_lines': round(lines / files) if files else 0}


def count_hebrew_words() -> int:
    hebrew_pattern = re.compile(r'[\u0590-\u05FF]+')
    total = 0

    all_files = list(REPO_ROOT.rglob('*.md'))
    total_files = len([f for f in all_files if '.git' not in str(f)])
    processed = 0

    for md_file in all_files:
        if '.git' in str(md_file):
            continue
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            total += len(hebrew_pattern.findall(content))
        processed += 1
        show_progress(processed, total_files, "ивритские слова", total)

    finish_progress()
    return total


def find_newest_files(limit: int = 10) -> list:
    files = []
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        mtime = md_file.stat().st_mtime
        files.append((md_file.relative_to(REPO_ROOT), mtime))

    files.sort(key=lambda x: x[1], reverse=True)
    return [(str(f), datetime.fromtimestamp(t).strftime('%Y-%m-%d')) for f, t in files[:limit]]


def count_metadata_completeness() -> dict:
    total = 0
    has_metadata = 0

    all_files = list(REPO_ROOT.rglob('*.md'))
    total_files = len([f for f in all_files if '.git' not in str(f)])
    processed = 0

    for md_file in all_files:
        if '.git' in str(md_file):
            continue
        total += 1
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if '**Метаданные файла**' in content:
                has_metadata += 1
        processed += 1
        show_progress(processed, total_files, "метаданные", has_metadata)

    finish_progress()
    return {'total': total, 'has_metadata': has_metadata, 'percent': round(has_metadata / total * 100) if total else 0}


def count_emojis_in_titles() -> dict:
    total = 0
    has_emoji = 0

    all_files = []
    for dir_name in ['terminology', 'researches']:
        dir_path = REPO_ROOT / dir_name
        if dir_path.exists():
            for md_file in dir_path.rglob('*.md'):
                all_files.append(md_file)

    total_files = len(all_files)
    processed = 0

    for md_file in all_files:
        total += 1
        with open(md_file, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if re.match(r'^# [\U00010000-\U0010FFFF]', first_line):
                has_emoji += 1
        processed += 1
        show_progress(processed, total_files, "эмодзи", has_emoji)

    finish_progress()
    return {'total': total, 'has_emoji': has_emoji, 'percent': round(has_emoji / total * 100) if total else 0}


def count_forbidden_words() -> dict:
    forbidden = ['Бог', 'Господь', 'грех', 'душа', 'Христос', 'Иисус', 'церковь']
    counts = Counter()

    all_files = list(REPO_ROOT.rglob('*.md'))
    total_files = len([f for f in all_files if '.git' not in str(f) and 'forbidden-words.md' not in str(f)])
    processed = 0

    for md_file in all_files:
        if '.git' in str(md_file):
            continue
        if 'forbidden-words.md' in str(md_file):
            continue

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            for word in forbidden:
                count = content.count(word)
                if count > 0:
                    counts[word] += count
        processed += 1
        show_progress(processed, total_files, "запрещённые слова", sum(counts.values()))

    finish_progress()
    return dict(counts)


def generate_report() -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"# 📊 СТАТИСТИКА РЕПОЗИТОРИЯ",
        "",
        f"**Дата генерации:** {timestamp}",
        "",
        "---",
        "",
        "## 📁 ФАЙЛЫ ПО ПАПКАМ",
        ""
    ]

    file_stats = count_files()
    for folder, count in file_stats.items():
        lines.append(f"- **{folder}/** — {count} файлов")

    lines.extend([
        "",
        "---",
        "",
        "## 📝 ОБЩАЯ СТАТИСТИКА",
        ""
    ])

    line_stats = count_lines()
    lines.append(f"- **Всего md-файлов:** {line_stats['files']}")
    lines.append(f"- **Всего строк:** {line_stats['lines']:,}")
    lines.append(f"- **Средняя длина файла:** {line_stats['avg_lines']} строк")

    print("\nПодсчёт ивритских слов...")
    hebrew = count_hebrew_words()
    lines.append(f"- **Ивритских слов:** {hebrew:,}")

    lines.extend([
        "",
        "---",
        "",
        "## ✅ КАЧЕСТВО МЕТАДАННЫХ",
        ""
    ])

    print("\nПроверка метаданных...")
    meta = count_metadata_completeness()
    lines.append(f"- **Файлов с метаданными:** {meta['has_metadata']} / {meta['total']} ({meta['percent']}%)")

    print("Проверка эмодзи в заголовках...")
    emoji = count_emojis_in_titles()
    lines.append(f"- **Заголовков с эмоджи:** {emoji['has_emoji']} / {emoji['total']} ({emoji['percent']}%)")

    lines.extend([
        "",
        "---",
        "",
        "## 🚫 ЗАПРЕЩЁННЫЕ СЛОВА",
        ""
    ])

    print("Поиск запрещённых слов...")
    forbidden = count_forbidden_words()
    if forbidden:
        for word, count in forbidden.items():
            lines.append(f"- **{word}** — {count} раз")
    else:
        lines.append("- ✅ Запрещённые слова не найдены")

    lines.extend([
        "",
        "---",
        "",
        "## 🆕 ПОСЛЕДНИЕ ОБНОВЛЕНИЯ",
        ""
    ])

    newest = find_newest_files(10)
    for path, date in newest:
        lines.append(f"- **{path}** — {date}")

    lines.extend([
        "",
        "---",
        "",
        "## 💾 РАЗМЕР РЕПОЗИТОРИЯ",
        ""
    ])

    total_size = 0
    for item in REPO_ROOT.rglob('*'):
        if item.is_file() and '.git' not in str(item):
            total_size += item.stat().st_size

    size_mb = total_size / 1024 / 1024
    lines.append(f"- **Общий размер:** {size_mb:.2f} MB")

    lines.append("")

    return '\n'.join(lines)


def main():
    print("\n📊 ГЕНЕРАЦИЯ СТАТИСТИКИ")
    print("=" * 50)

    report = generate_report()

    # Сохраняем в корневой STATS.md
    root_stats = REPO_ROOT / "STATS.md"
    with open(root_stats, 'w', encoding='utf-8') as f:
        f.write(report)

    # Сохраняем архивную копию
    archive_file = REPORT_DIR / f"STATS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(archive_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✅ Отчёт сохранён: {root_stats}")
    print(f"✅ Архив: {archive_file}")


if __name__ == "__main__":
    main()

