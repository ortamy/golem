#!/usr/bin/env python3
# generate-index.py — генерация README.md для папок

import sys
import re
from pathlib import Path
from progress import show_progress, finish_progress

REPO_ROOT = Path(__file__).parent.parent

TARGET_DIRS = {
    'terminology': 'Термины',
    'researches': 'Исследования',
    'tools': 'Инструменты',
    'ideas': 'Идеи',
    'drafts': 'Черновики'
}


def extract_emoji_and_title(file_path: Path) -> tuple:
    """Извлекает эмодзи и заголовок из файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line.startswith('# '):
                header = first_line[2:].strip()
                emoji_match = re.match(r'^([\U00010000-\U0010FFFF])\s+(.+)$', header)
                if emoji_match:
                    return emoji_match.group(1), emoji_match.group(2)
                return "", header
    except:
        pass
    return "", file_path.stem.replace('-', ' ').title()


def generate_index_for_folder(folder: str, display_name: str) -> str:
    """Генерирует README.md для конкретной папки"""
    folder_path = REPO_ROOT / folder
    if not folder_path.exists():
        return f"# {display_name}\n\nПапка не существует.\n"

    md_files = list(folder_path.glob('*.md'))
    md_files = [f for f in md_files if f.name not in ['README.md', 'STRUCTURE.md']]

    lines = [
        f"# {display_name}",
        "",
        f"**Всего файлов:** {len(md_files)}",
        "",
        "---",
        "",
        "## Список файлов",
        ""
    ]

    for i, md_file in enumerate(md_files, 1):
        emoji, title = extract_emoji_and_title(md_file)
        emoji_str = f"{emoji} " if emoji else ""
        lines.append(f"{i}. {emoji_str}[{title if title else md_file.stem}]({md_file.name})")

    lines.extend([
        "",
        "---",
        f"*Автоматически сгенерировано: `python tools/generate-index.py`*"
    ])

    return '\n'.join(lines)


def main():
    print("\n📚 ГЕНЕРАЦИЯ ИНДЕКСОВ ДЛЯ ПАПОК")
    print("=" * 50)

    for i, (folder, display_name) in enumerate(TARGET_DIRS.items(), 1):
        show_progress(i, len(TARGET_DIRS), folder)

        content = generate_index_for_folder(folder, display_name)
        index_file = REPO_ROOT / folder / "README.md"

        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\n   ✅ {folder}/README.md")

    finish_progress()
    print("\n" + "=" * 50)
    print(f"{'✅' if '✅' in str(locals()) else ''} Все индексы сгенерированы")
    return 0


if __name__ == "__main__":
    sys.exit(main())

