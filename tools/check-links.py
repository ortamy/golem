# tools/check-links.py
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


def extract_links(content: str) -> list:
    links = []
    pattern = re.compile(r'\]\(([^\)]+\.md)\)')
    matches = pattern.findall(content)
    for match in matches:
        if not match.startswith("http"):
            links.append(match)
    return links


def main():
    print("\n🔗 ПРОВЕРКА ССЫЛОК")
    print("=" * 50)
    
    files = find_all_md_files()
    total = len(files)
    
    print(f"Найдено файлов: {total}")
    print("Проверка ссылок...\n")
    
    broken = []
    
    for i, (rel_path, full_path) in enumerate(files.items(), 1):
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        links = extract_links(content)
        for link in links:
            target = REPO_ROOT / link
            if not target.exists():
                broken.append((rel_path, link))
        show_progress(i, total, "ссылки", len(broken))
    
    finish_progress()
    print("\n\n" + "=" * 50)
    
    if broken:
        print(f"\n❌ БИТЫХ ССЫЛОК: {len(broken)}")
        for file_path, link in broken[:15]:
            print(f"   • {file_path} → {link}")
        if len(broken) > 15:
            print(f"   ... и ещё {len(broken) - 15}")
        return 1
    else:
        print(f"\n✅ Все ссылки корректны")
        return 0


if __name__ == "__main__":
    sys.exit(main())