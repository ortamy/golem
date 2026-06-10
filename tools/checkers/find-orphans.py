#!/usr/bin/env python3
# tools/find-orphans.py — поиск файлов-сирот (на которые нет ссылок)
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, REPO_ROOT

IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__', 'reports', 'neural'}

SYSTEM_FILES = {
    'BACKLOG.md', 'CHANGELOG.md', 'COMPLETED-TASKS.md', 'CONTRIBUTORS.md',
    'DECISIONS.md', 'GLOSSARY.md', 'README.md', 'RETROSPECTIVE.md',
    'ROADMAP.md', 'STATS.md', 'STRUCTURE.md', 'SCTRUCTURE.md', 'TECHNICAL-DEBT.md'
}

SYSTEM_DIRS = {'davar', 'instructions'}


def find_all_md_files():
    files = {}
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        rel_path = str(md_file.relative_to(REPO_ROOT))
        parts = Path(rel_path).parts

        if parts[0] in IGNORE_DIRS:
            continue
        if parts[0] in SYSTEM_DIRS:
            continue
        if rel_path in SYSTEM_FILES:
            continue

        files[rel_path] = md_file
    return files


def extract_links(content: str) -> set:
    links = set()
    for match in re.findall(r'\]\(([^\)]+\.md)\)', content):
        if not match.startswith("http"):
            links.add(match)
    return links


def main():
    print_header("ПОИСК ФАЙЛОВ-СИРОТ", "👻")

    files = find_all_md_files()
    total = len(files)
    print(f"Найдено файлов (без системных): {total}")

    linked_files = set()
    encoding_issues = []

    for i, (rel_path, full_path) in enumerate(files.items(), 1):
        try:
            content = read_file_safe(full_path)
        except Exception as e:
            encoding_issues.append((rel_path, str(e)))
            continue

        for link in extract_links(content):
            linked_files.add(link)

        progress_bar(i, total, extra=f"ссылок: {len(linked_files)}")

    finish_progress()

    orphans = [rel_path for rel_path in files if rel_path not in linked_files]

    if encoding_issues:
        print_warning(f"Проблемы с кодировкой: {len(encoding_issues)}")
        for file_path, error in encoding_issues[:5]:
            print(f"   • {file_path} — {error}")

    if orphans:
        print_warning(f"ФАЙЛОВ-СИРОТ: {len(orphans)}")
        for orphan in orphans[:15]:
            print(f"   • {orphan}")
        if len(orphans) > 15:
            print(f"   ... и ещё {len(orphans) - 15}")
    else:
        print_success("Файлов-сирот не найдено")

    return 0


if __name__ == "__main__":
    sys.exit(main())

