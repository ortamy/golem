# tools/find-orphans.py
import sys
import re
from pathlib import Path
from progress import show_progress, finish_progress

REPO_ROOT = Path(__file__).parent.parent
IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__', 'reports', 'neural'}


def find_all_md_files():
    files = {}
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        rel_path = str(md_file.relative_to(REPO_ROOT))
        parts = Path(rel_path).parts
        if parts[0] in IGNORE_DIRS:
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


def main():
    print("\n👻 ПОИСК ФАЙЛОВ-СИРОТ")
    print("=" * 50)
    
    files = find_all_md_files()
    total = len(files)
    
    print(f"Найдено файлов: {total}")
    print("Анализ ссылок...\n")
    
    linked_files = set()
    for i, (rel_path, full_path) in enumerate(files.items(), 1):
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        links = extract_links(content)
        for link in links:
            linked_files.add(link)
        show_progress(i, total, "анализ", len(linked_files))
    
    finish_progress()
    
    orphans = [rel_path for rel_path in files if rel_path not in linked_files]
    
    print("\n\n" + "=" * 50)
    
    if orphans:
        print(f"\n⚠️ ФАЙЛОВ-СИРОТ: {len(orphans)}")
        for orphan in orphans[:15]:
            print(f"   • {orphan}")
        if len(orphans) > 15:
            print(f"   ... и ещё {len(orphans) - 15}")
    else:
        print(f"\n✅ Файлов-сирот не найдено")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())