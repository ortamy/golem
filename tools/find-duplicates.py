# tools/find-duplicates.py
import sys
from pathlib import Path
from difflib import SequenceMatcher
from progress import show_progress, finish_progress

REPO_ROOT = Path(__file__).parent.parent
TARGET_DIRS = ['terminology', 'researches']
SIMILARITY_THRESHOLD = 0.85


def read_file(file_path: Path) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a[:1000].lower(), b[:1000].lower()).ratio()


def main():
    print("\n🔍 ПОИСК ДУБЛИКАТОВ")
    print("=" * 50)
    
    files = {}
    for target_dir in TARGET_DIRS:
        dir_path = REPO_ROOT / target_dir
        if dir_path.exists():
            for md_file in dir_path.rglob('*.md'):
                content = read_file(md_file)
                if content:
                    rel_path = str(md_file.relative_to(REPO_ROOT))
                    files[rel_path] = content
    
    total = len(files)
    print(f"Найдено файлов: {total}")
    print("Сравнение файлов...\n")
    
    duplicates = []
    file_list = list(files.items())
    total_checks = total * (total - 1) // 2
    checked = 0
    
    for i, (name1, content1) in enumerate(file_list):
        for name2, content2 in file_list[i+1:]:
            sim = similarity(content1, content2)
            if sim >= SIMILARITY_THRESHOLD:
                duplicates.append((name1, name2, sim))
            checked += 1
            show_progress(checked, total_checks, "сравнение", len(duplicates))
    
    finish_progress()
    print("\n\n" + "=" * 50)
    
    if duplicates:
        print(f"\n❌ НАЙДЕНО ДУБЛИКАТОВ: {len(duplicates)}")
        for name1, name2, sim in duplicates[:10]:
            print(f"   • {name1} ↔ {name2} (схожесть: {sim:.0%})")
        if len(duplicates) > 10:
            print(f"   ... и ещё {len(duplicates) - 10}")
        return 1
    else:
        print(f"\n✅ Дубликатов не найдено")
        return 0


if __name__ == "__main__":
    sys.exit(main())