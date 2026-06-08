#!/usr/bin/env python3
# generate-nav.py — генерация навигации для README.md

import sys
import re
from pathlib import Path
from progress import show_progress, finish_progress

REPO_ROOT = Path(__file__).parent.parent
README_PATH = REPO_ROOT / "README.md"
NAV_START_MARKER = "<!-- NAVIGATION_START -->"
NAV_END_MARKER = "<!-- NAVIGATION_END -->"

TARGET_DIRS = {
    'instructions': 'Инструкции',
    'checkers': 'Чекеры',
    'terminology': 'Терминология',
    'researches': 'Исследования',
    'tools': 'Инструменты',
    'ideas': 'Идеи',
    'drafts': 'Черновики'
}


def extract_title(file_path: Path) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line.startswith('# '):
                title = first_line[2:].strip()
                title = re.sub(r'^[\U00010000-\U0010FFFF]\s*', '', title)
                return title[:60]
    except:
        pass
    return file_path.stem.replace('-', ' ').title()


def scan_directory(dir_path: Path, max_files: int = 20) -> list:
    files = []
    if not dir_path.exists():
        return files

    for md_file in sorted(dir_path.glob('*.md')):
        if md_file.name in ['README.md', 'STRUCTURE.md', 'GLOSSARY.md', 'STATS.md']:
            continue
        rel_path = md_file.relative_to(REPO_ROOT)
        title = extract_title(md_file)
        files.append((title, str(rel_path)))

    return files[:max_files]


def generate_navigation() -> str:
    lines = [NAV_START_MARKER, "", "# НАВИГАЦИЯ ПО РЕПОЗИТОРИЮ", ""]

    dirs_list = list(TARGET_DIRS.items())
    total_dirs = len(dirs_list)

    for i, (folder, display_name) in enumerate(dirs_list):
        show_progress(i + 1, total_dirs, folder)
        dir_path = REPO_ROOT / folder
        files = scan_directory(dir_path)

        if files:
            lines.append(f"## {display_name}")
            lines.append("")
            for title, path in files:
                lines.append(f"- [{title}]({path})")
            lines.append("")

    finish_progress()

    total = sum(len(scan_directory(REPO_ROOT / f)) for f in TARGET_DIRS)
    lines.append(f"**Всего файлов:** {total}")
    lines.append("")
    lines.append(NAV_END_MARKER)

    return '\n'.join(lines)


def escape_replacement(s: str) -> str:
    """Экранирует спецсимволы в строке замены для re.sub"""
    return s.replace('\\', '\\\\')


def main():
    print("\n🧭 ГЕНЕРАЦИЯ НАВИГАЦИИ")
    print("=" * 50)

    if not README_PATH.exists():
        print(f"❌ README.md не найден")
        return 1

    print("Сканирование папок...")
    new_nav = generate_navigation()

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    if NAV_START_MARKER in content and NAV_END_MARKER in content:
        # Экранируем спецсимволы в строке замены
        escaped_nav = escape_replacement(new_nav)
        pattern = f"{re.escape(NAV_START_MARKER)}.*?{re.escape(NAV_END_MARKER)}"
        new_content = re.sub(pattern, f"{NAV_START_MARKER}\n{escaped_nav}\n{NAV_END_MARKER}", content, flags=re.DOTALL)
    else:
        new_content = content + "\n\n" + new_nav

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"\n✅ Навигация обновлена в {README_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

