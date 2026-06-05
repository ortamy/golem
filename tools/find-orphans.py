#!/usr/bin/env python3
# find-orphans.py — поиск файлов, на которые никто не ссылается

import re
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent
TARGET_DIRS = ['terminology', 'researches', 'instructions', 'checkers', 'davar']
IGNORE_FILES = {'README.md', 'structure.md', 'GLOSSARY.md', 'STATS.md'}


def find_all_md_files() -> dict:
    """Находит все md-файлы в репозитории"""
    files = {}
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        rel_path = str(md_file.relative_to(REPO_ROOT))
        files[rel_path] = md_file
    return files


def extract_all_links() -> set:
    """Извлекает все ссылки из всех файлов"""
    links = set()
    
    link_pattern = re.compile(r'\]\(([^\)]+\.md)\)')
    
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = link_pattern.findall(content)
        for match in matches:
            if match.startswith('http'):
                continue
            if match.startswith('/'):
                match = match[1:]
            links.add(match)
    
    return links


def normalize_path(link: str, source_file: str = "") -> str:
    """Нормализует путь ссылки"""
    if link.startswith('./'):
        link = link[2:]
    if link.startswith('../'):
        parts = link.split('/')
        link = '/'.join(parts[1:])
    return link


def is_ignored(file_path: str) -> bool:
    """Проверяет, нужно ли игнорировать файл"""
    if file_path in IGNORE_FILES:
        return True
    for ignore in IGNORE_FILES:
        if file_path.endswith(ignore):
            return True
    return False


def main():
    print("🔍 ПОИСК ФАЙЛОВ-СИРОТ")
    print("=====================")
    print("")
    
    all_files = find_all_md_files()
    all_links = extract_all_links()
    
    referenced = set()
    for link in all_links:
        normalized = normalize_path(link)
        referenced.add(normalized)
    
    orphans = []
    for file_path in all_files:
        if is_ignored(file_path):
            continue
        if file_path not in referenced:
            orphans.append(file_path)
    
    if orphans:
        print("❌ ФАЙЛЫ-СИРОТЫ (на них нет ссылок):")
        print("")
        for orphan in sorted(orphans):
            print(f"  • {orphan}")
        print("")
        print(f"📊 ИТОГО: {len(orphans)} файлов-сирот из {len(all_files)}")
        print("")
        print("💡 Совет: добавьте ссылки на эти файлы или удалите их")
    else:
        print("✅ Все файлы имеют хотя бы одну ссылку")
        print(f"📊 Всего файлов: {len(all_files)}")


if __name__ == "__main__":
    main()
