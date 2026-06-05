#!/usr/bin/env python3
# stats-report.py — генерация статистики по репозиторию

import os
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

REPO_ROOT = Path(__file__).parent.parent
TARGET_DIRS = ['terminology', 'researches', 'instructions', 'checkers', 'davar', 'ideas', 'drafts', 'tools']


def count_files() -> dict:
    """Считает количество файлов по папкам"""
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
    """Считает количество строк в md-файлах"""
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
    """Считает количество ивритских слов в репозитории"""
    hebrew_pattern = re.compile(r'[\u0590-\u05FF]+')
    total = 0
    
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            total += len(hebrew_pattern.findall(content))
    
    return total


def find_newest_files(limit: int = 10) -> list:
    """Находит самые новые файлы по дате обновления"""
    files = []
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        mtime = md_file.stat().st_mtime
        files.append((md_file.relative_to(REPO_ROOT), mtime))
    
    files.sort(key=lambda x: x[1], reverse=True)
    return [(str(f), datetime.fromtimestamp(t).strftime('%Y-%m-%d')) for f, t in files[:limit]]


def count_metadata_completeness() -> dict:
    """Проверяет наличие метаданных в файлах"""
    total = 0
    has_metadata = 0
    
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        total += 1
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if '**Метаданные файла**' in content:
                has_metadata += 1
    
    return {'total': total, 'has_metadata': has_metadata, 'percent': round(has_metadata / total * 100) if total else 0}


def count_emojis_in_titles() -> dict:
    """Считает заголовки с эмоджи в terminology/ и researches/"""
    total = 0
    has_emoji = 0
    
    for dir_name in ['terminology', 'researches']:
        dir_path = REPO_ROOT / dir_name
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.rglob('*.md'):
            total += 1
            with open(md_file, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if re.match(r'^# [\U00010000-\U0010FFFF]', first_line):
                    has_emoji += 1
    
    return {'total': total, 'has_emoji': has_emoji, 'percent': round(has_emoji / total * 100) if total else 0}


def count_forbidden_words() -> dict:
    """Считает использование запрещённых слов (приблизительно)"""
    forbidden = ['Бог', 'Господь', 'грех', 'душа', 'Христос', 'Иисус', 'церковь']
    counts = Counter()
    
    for md_file in REPO_ROOT.rglob('*.md'):
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
    
    return dict(counts)


def generate_report() -> str:
    """Генерирует полный отчёт"""
    lines = [
        "# 📊 СТАТИСТИКА РЕПОЗИТОРИЯ",
        "",
        f"**Дата генерации:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
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
    
    hebrew = count_hebrew_words()
    lines.append(f"- **Ивритских слов:** {hebrew:,}")
    
    lines.extend([
        "",
        "---",
        "",
        "## ✅ КАЧЕСТВО МЕТАДАННЫХ",
        ""
    ])
    
    meta = count_metadata_completeness()
    lines.append(f"- **Файлов с метаданными:** {meta['has_metadata']} / {meta['total']} ({meta['percent']}%)")
    
    emoji = count_emojis_in_titles()
    lines.append(f"- **Заголовков с эмоджи:** {emoji['has_emoji']} / {emoji['total']} ({emoji['percent']}%)")
    
    lines.extend([
        "",
        "---",
        "",
        "## 🚫 ЗАПРЕЩЁННЫЕ СЛОВА",
        ""
    ])
    
    forbidden = count_forbidden_words()
    for word, count in forbidden.items():
        lines.append(f"- **{word}** — {count} раз")
    
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
    print("📊 ГЕНЕРАЦИЯ СТАТИСТИКИ")
    print("======================")
    print("")
    
    report = generate_report()
    output_file = REPO_ROOT / "STATS.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Отчёт сохранён: {output_file}")


if __name__ == "__main__":
    main()
