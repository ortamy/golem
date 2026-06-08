# tools/check-links.py
import sys
import re
from pathlib import Path

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


def read_file_safe(filepath: Path) -> str:
    encodings = ['utf-8', 'utf-16', 'cp1251', 'latin-1']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def main():
    print("\n🔗 ПРОВЕРКА ССЫЛОК")
    print("=" * 50)
    
    files = find_all_md_files()
    total = len(files)
    
    print(f"Найдено файлов: {total}")
    print("Проверка ссылок...\n")
    
    broken = []
    encoding_issues = []
    
    for i, (rel_path, full_path) in enumerate(files.items(), 1):
        try:
            content = read_file_safe(full_path)
        except Exception as e:
            encoding_issues.append((rel_path, str(e)))
            continue
        
        links = extract_links(content)
        for link in links:
            target = REPO_ROOT / link
            if not target.exists():
                broken.append((rel_path, link))
        
        if i % 20 == 0 or i == total:
            print(f"  [{i}/{total}] проверено... битых: {len(broken)}", end='\r')
    
    print("\n\n" + "=" * 50)
    
    if encoding_issues:
        print(f"\n⚠️ ПРОБЛЕМЫ С КОДИРОВКОЙ: {len(encoding_issues)}")
        for file_path, error in encoding_issues[:5]:
            print(f"   • {file_path} — {error}")
    
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