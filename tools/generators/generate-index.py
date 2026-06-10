#!/usr/bin/env python3
# tools/generators/generate-index.py — генерация индексов папок
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions"]
OUTPUT_FILE = REPO_ROOT / "docs" / "INDEX.md"


def extract_title(content: str) -> str:
    for line in content.split('\n'):
        if line.startswith('# '):
            return line[2:].strip()
    return ""


def extract_topic(content: str) -> str:
    import re
    match = re.search(r'[-*]\s*\*\*Тема:\*\*\s*(.+?)(?:\n|$)', content)
    return match.group(1).strip() if match else ""


def main():
    print_header("ГЕНЕРАЦИЯ ИНДЕКСА", "📑")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    print(f"Найдено файлов: {total}")

    # Группируем по папкам
    index = {}
    for i, filepath in enumerate(all_files, 1):
        content = read_file_safe(filepath)
        if not content:
            continue

        folder = str(filepath.parent.relative_to(REPO_ROOT)).replace('\\', '/')
        rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
        title = extract_title(content)
        topic = extract_topic(content)

        if folder not in index:
            index[folder] = []
        index[folder].append({
            "path": rel_path,
            "name": filepath.stem,
            "title": title or filepath.stem,
            "topic": topic,
        })

        progress_bar(i, total, extra=f"папок: {len(index)}")

    finish_progress()

    # Генерируем INDEX.md
    today = datetime.now().strftime('%Y-%m-%d')
    lines = [
        "# ИНДЕКС РЕПОЗИТОРИЯ",
        "",
        "**Метаданные файла**",
        f"- **Файл:** `docs/INDEX.md`",
        f"- **Версия:** 1.0",
        f"- **Дата создания:** {today}",
        f"- **Последнее обновление:** {today}",
        f"- **Причина обновления:** Автоматическая генерация",
        f"- **Статус:** Активный",
        f"- **Тема:** Индекс всех файлов репозитория",
        "",
        "---",
        "",
    ]

    for folder in sorted(index.keys()):
        lines.append(f"## {folder}/")
        lines.append("")
        for item in index[folder]:
            topic_str = f" — {item['topic'][:80]}" if item.get('topic') else ""
            lines.append(f"- **{item['title']}**{topic_str} → [{item['path']}]({item['path']})")
        lines.append("")

    lines.append("---")
    lines.append(f"*Сгенерировано автоматически: {today}*")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print_success(f"Индекс сохранён: {OUTPUT_FILE} ({len(index)} папок)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

