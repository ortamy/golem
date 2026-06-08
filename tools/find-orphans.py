# tools/find-orphans.py
import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__', 'reports', 'neural'}

# Системные файлы и папки — не участвуют в проверке на сиротство
SYSTEM_FILES = {
    'BACKLOG.md', 'CHANGELOG.md', 'COMPLETED-TASKS.md', 'CONTRIBUTORS.md',
    'DECISIONS.md', 'GLOSSARY.md', 'README.md', 'RETROSPECTIVE.md',
    'ROADMAP.md', 'STATS.md', 'STRUCTURE.md', 'SCTRUCTURE.md', 'TECHNICAL-DEBT.md'
}

SYSTEM_DIRS = {'davar'}


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
    pattern = re.compile(r'\]\(([^\)]+\.md)\)')
    matches = pattern.findall(content)
    for match in matches:
        if not match.startswith("http"):
            links.add(match)
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
    print("\n👻 ПОИСК ФАЙЛОВ-СИРОТ")
    print("=" * 50)
    
    files = find_all_md_files()
    total = len(files)
    
    print(f"Найдено файлов (без системных): {total}")
    print("Анализ ссылок...\n")
    
    linked_files = set()
    encoding_issues = []
    
    for i, (rel_path, full_path) in enumerate(files.items(), 1):
        try:
            content = read_file_safe(full_path)
        except Exception as e:
            encoding_issues.append((rel_path, str(e)))
            continue
        
        links = extract_links(content)
        for link in links:
            linked_files.add(link)
        
        if i % 20 == 0 or i == total:
            print(f"  [{i}/{total}] проанализировано... ссылок: {len(linked_files)}", end='\r')
    
    orphans = [rel_path for rel_path in files if rel_path not in linked_files]
    
    print("\n\n" + "=" * 50)
    
    if encoding_issues:
        print(f"\n⚠️ ПРОБЛЕМЫ С КОДИРОВКОЙ: {len(encoding_issues)}")
        for file_path, error in encoding_issues[:5]:
            print(f"   • {file_path} — {error}")
    
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