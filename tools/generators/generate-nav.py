#!/usr/bin/env python3
# tools/generators/generate-nav.py — генерация навигации для README.md

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_error, REPO_ROOT

README_PATH = REPO_ROOT / "README.md"
NAV_START = "<!-- NAVIGATION_START -->"
NAV_END = "<!-- NAVIGATION_END -->"

TARGET_DIRS = {
    'instructions': 'Инструкции',
    'terminology': 'Терминология',
    'researches': 'Исследования',
    'tools': 'Инструменты',
    'ideas': 'Идеи',
    'drafts': 'Черновики'
}


def extract_title(file_path: Path) -> str:
    content = read_file_safe(file_path)
    if content:
        first_line = content.split('\n')[0]
        if first_line.startswith('# '):
            title = first_line[2:].strip()
            title = re.sub(r'^[^\w\s]\s*', '', title)
            return title[:60]
    return file_path.stem.replace('-', ' ').title()


def scan_directory(dir_path: Path, max_files: int = 20) -> list:
    files = []
    if not dir_path.exists():
        return files
    for md_file in sorted(dir_path.glob('*.md')):
        if md_file.name in ['README.md', 'STRUCTURE.md', 'GLOSSARY.md', 'STATS.md']:
            continue
        rel_path = str(md_file.relative_to(REPO_ROOT)).replace('\\', '/')
        files.append((extract_title(md_file), rel_path))
    return files[:max_files]


def generate_navigation() -> str:
    lines = [NAV_START, "", "## НАВИГАЦИЯ ПО РЕПОЗИТОРИЮ", ""]

    dirs_list = list(TARGET_DIRS.items())
    total = len(dirs_list)

    for i, (folder, display_name) in enumerate(dirs_list, 1):
        files = scan_directory(REPO_ROOT / folder)
        if files:
            lines.append(f"### {display_name}")
            lines.append("")
            for title, path in files:
                lines.append(f"- [{title}]({path})")
            lines.append("")
        progress_bar(i, total, extra=folder)

    finish_progress()
    lines.append(NAV_END)
    return '\n'.join(lines)


def main():
    print_header("ГЕНЕРАЦИЯ НАВИГАЦИИ", "🧭")

    if not README_PATH.exists():
        print_error("README.md не найден")
        return 1

    new_nav = generate_navigation()

    content = read_file_safe(README_PATH) or ""

    if NAV_START in content and NAV_END in content:
        pattern = f"{re.escape(NAV_START)}.*?{re.escape(NAV_END)}"
        new_content = re.sub(pattern, new_nav.replace('\\', '\\\\'), content, flags=re.DOTALL)
    else:
        new_content = content + "\n\n" + new_nav

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print_success(f"Навигация обновлена: {README_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

