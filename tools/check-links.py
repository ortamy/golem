#!/usr/bin/env python3
# check-links.py — проверка битых ссылок в md-файлах

import re
from pathlib import Path
from typing import Dict, List, Tuple, Set

REPO_ROOT = Path(__file__).parent.parent
IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__'}
IGNORE_FILES = {'export.txt', 'structure.txt'}


def find_all_md_files() -> Dict[str, Path]:
    """Находит все md-файлы в репозитории"""
    files = {}
    for md_file in REPO_ROOT.rglob('*.md'):
        rel_path = md_file.relative_to(REPO_ROOT)
        parts = rel_path.parts
        
        if parts[0] in IGNORE_DIRS:
            continue
        if md_file.name in IGNORE_FILES:
            continue
        
        files[str(rel_path)] = md_file
    return files


def extract_links(content: str, source_file: str) -> List[Tuple[str, int]]:
    """Извлекает все внутренние ссылки из файла"""
    links = []
    
    patterns = [
        r'\[[^\]]+\]\(([^\)]+\.md)\)',
        r'→\s+\[[^\]]+\]\(([^\)]+\.md)\)',
        r'подробнее\]\(([^\)]+\.md)\)',
    ]
    
    for line_num, line in enumerate(content.split('\n'), 1):
        for pattern in patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                if not match.startswith('http'):
                    links.append((match, line_num))
    
    return links


def resolve_link(link: str, source_file: str) -> bool:
    """Проверяет, существует ли целевой файл"""
    if link.startswith('/'):
        target = REPO_ROOT / link.lstrip('/')
    else:
        source_dir = Path(source_file).parent
        if source_dir == Path('.'):
            source_dir = Path('')
        target = REPO_ROOT / source_dir / link
    
    target = target.resolve()
    return target.exists() and target.is_file()


def check_links(files: Dict[str, Path]) -> Dict[str, List[Tuple[str, int]]]:
    """Проверяет все ссылки во всех файлах"""
    broken = {}
    
    for rel_path, full_path in files.items():
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        links = extract_links(content, rel_path)
        
        for link, line_num in links:
            if not resolve_link(link, rel_path):
                if rel_path not in broken:
                    broken[rel_path] = []
                broken[rel_path].append((link, line_num))
    
    return broken


def main():
    print("🔗 ПРОВЕРКА ССЫЛОК")
    print("==================")
    print("")
    
    files = find_all_md_files()
    print(f"📊 Найдено файлов: {len(files)}")
    print("")
    
    broken = check_links(files)
    
    if broken:
        print("❌ БИТЫЕ ССЫЛКИ:")
        print("")
        
        total = 0
        for source, links in broken.items():
            print(f"  📄 {source}")
            for link, line_num in links:
                print(f"     • строка {line_num}: {link}")
                total += 1
            print("")
        
        print(f"📊 ИТОГО: {total} битых ссылок в {len(broken)} файлах")
    else:
        print("✅ Все ссылки корректны")
    
    print("")


if __name__ == "__main__":
    main()
