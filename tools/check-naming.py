# tools/check-naming.py
import sys
from pathlib import Path
from progress import show_progress, finish_progress

REPO_ROOT = Path(__file__).parent.parent
IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__', 'reports', 'neural'}
IGNORE_FILES = {'README.md', 'CHANGELOG.md', 'BACKLOG.md', 'CONTRIBUTORS.md', 
                'DECISIONS.md', 'GLOSSARY.md', 'RETROSPECTIVE.md', 'ROADMAP.md',
                'STRUCTURE.md', 'TECHNICAL-DEBT.md', 'STATS.md', 'COMPLETED-TASKS.md'}


def get_all_md_files():
    files = []
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        rel_path = md_file.relative_to(REPO_ROOT)
        parts = rel_path.parts
        if parts[0] in IGNORE_DIRS:
            continue
        if md_file.name in IGNORE_FILES:
            continue
        files.append((rel_path, md_file))
    return files


def check_name(name):
    import re
    allowed_pattern = re.compile(r'^[a-z][a-z0-9\-]*\.md$')
    if not allowed_pattern.match(name):
        return False, f"неверное имя: {name}"
    if re.search(r'[а-яА-Я]', name):
        return False, f"содержит русские буквы: {name}"
    return True, ""


def main():
    print("\n🔍 ПРОВЕРКА ИМЁН ФАЙЛОВ")
    print("=" * 50)
    
    files = get_all_md_files()
    total = len(files)
    errors = []
    
    print(f"Найдено файлов: {total}")
    print("Сканирование...\n")
    
    for i, (rel_path, md_file) in enumerate(files, 1):
        name = md_file.name
        is_valid, error_msg = check_name(name)
        
        if not is_valid:
            errors.append((rel_path, error_msg))
        
        show_progress(i, total, "проверка", len(errors))
    
    finish_progress()
    print("\n\n" + "=" * 50)
    
    if errors:
        print(f"\n❌ НАРУШЕНИЯ: {len(errors)}")
        for rel_path, error_msg in errors[:20]:
            print(f"   • {rel_path}: {error_msg}")
        if len(errors) > 20:
            print(f"   ... и ещё {len(errors) - 20}")
        return 1
    else:
        print(f"\n✅ Все {total} файлов названы корректно")
        return 0


if __name__ == "__main__":
    sys.exit(main())