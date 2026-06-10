#!/usr/bin/env python3
# tools/consistency-checker.py
import sys
import re
from pathlib import Path
from progress import show_progress, finish_progress

REPO_ROOT = Path(__file__).parent.parent
TERMINOLOGY_DIR = REPO_ROOT / "terminology"
IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__', 'reports'}


def find_all_md_files():
    files = {}
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        rel_path = str(md_file.relative_to(REPO_ROOT))
        parts = Path(rel_path).parts
        if parts and parts[0] in IGNORE_DIRS:
            continue
        files[rel_path] = md_file
    return files


def extract_links(content: str) -> set:
    links = set()
    pattern = re.compile(r'\]\(([^\)]+\.md)\)')
    matches = pattern.findall(content)
    for match in matches:
        if not match.startswith("http"):
            links.add(match)
    return links


def check_broken_links(files):
    broken = []
    total = len(files)
    for i, (rel_path, full_path) in enumerate(files.items(), 1):
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        links = extract_links(content)
        for link in links:
            target = REPO_ROOT / link
            if not target.exists():
                broken.append((rel_path, link))
        show_progress(i, total, "битые ссылки", len(broken))
    return broken


def check_orphan_files(files):
    linked_files = set()
    total = len(files)
    for i, (rel_path, full_path) in enumerate(files.items(), 1):
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        links = extract_links(content)
        for link in links:
            linked_files.add(link)
        show_progress(i, total, "поиск ссылок", len(linked_files))
    return [rel_path for rel_path in files if rel_path not in linked_files]


def check_transliteration():
    issues = []
    hebrew_to_russian = {
        "יְהוָה": "Яхве",
        "אֱמֶת": "эмет",
        "חֶסֶד": "хесед",
        "רוּחַ": "руах",
        "נֶפֶשׁ": "нэфеш",
    }

    term_files = list(TERMINOLOGY_DIR.glob("*.md"))
    total = len(term_files)

    for i, term_file in enumerate(term_files, 1):
        with open(term_file, "r", encoding="utf-8") as f:
            content = f.read()
        for hebrew, expected in hebrew_to_russian.items():
            if hebrew in content and expected.lower() not in content.lower():
                issues.append((term_file.name, hebrew, expected))
        show_progress(i, total, "транслитерация", len(issues))

    return issues


def check_file_naming(files):
    issues = []
    allowed_name = re.compile(r'^[a-z][a-z0-9\-]*\.md$')
    exceptions = {"README.md", "CHANGELOG.md", "BACKLOG.md", "CONTRIBUTORS.md",
                  "DECISIONS.md", "GLOSSARY.md", "RETROSPECTIVE.md", "ROADMAP.md",
                  "STRUCTURE.md", "TECHNICAL-DEBT.md", "STATS.md", "COMPLETED-TASKS.md"}

    total = len(files)
    for i, (rel_path, full_path) in enumerate(files.items(), 1):
        name = full_path.name
        if name not in exceptions and not allowed_name.match(name):
            issues.append((rel_path, name))
        show_progress(i, total, "именование", len(issues))

    return issues


def main():
    print("\n✅ ПРОВЕРКА СОГЛАСОВАННОСТИ")
    print("=" * 50)

    files = find_all_md_files()
    print(f"Найдено файлов: {len(files)}")
    print("")

    print("1. Проверка битых ссылок...")
    broken = check_broken_links(files)
    finish_progress()

    print("\n2. Проверка файлов-сирот...")
    orphans = check_orphan_files(files)
    finish_progress()

    print("\n3. Проверка транслитерации...")
    translit = check_transliteration()
    finish_progress()

    print("\n4. Проверка именования...")
    naming = check_file_naming(files)
    finish_progress()

    print("\n\n" + "=" * 50)

    total_issues = len(broken) + len(orphans) + len(translit) + len(naming)

    if total_issues == 0:
        print("\n✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ. ПРОЕКТ В ПОРЯДКЕ.")
        return 0
    else:
        print(f"\n❌ НАЙДЕНО {total_issues} НАРУШЕНИЙ:")
        if broken:
            print(f"   Битые ссылки: {len(broken)}")
        if orphans:
            print(f"   Файлы-сироты: {len(orphans)}")
        if translit:
            print(f"   Транслитерация: {len(translit)}")
        if naming:
            print(f"   Именование: {len(naming)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

