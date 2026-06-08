#!/usr/bin/env python3
# tahor-filter.py — автоматическая замена религионимов в текстах исследований

import os
import re
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
TAHOR_DIR = REPO_ROOT / "instructions" / "tahor"
RESEARCHES_DIR = REPO_ROOT / "researches"
TERMINOLOGY_DIR = REPO_ROOT / "terminology"
BACKUP_DIR = REPO_ROOT / "backups" / "tahor-filter"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
NC = "\033[0m"
BOLD = "\033[1m"


def load_replacements():
    """Загружает замены из всех файлов tahor/"""
    replacements = {}
    
    tahor_files = [
        "religionisms.md",
        "grecisms.md",
        "slavicisms.md",
        "latinisms.md",
        "names.md",
        "phrases.md"
    ]
    
    for filename in tahor_files:
        filepath = TAHOR_DIR / filename
        if not filepath.exists():
            continue
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        pattern = r'- \*\*([^*]+)\*\*.*?→ ([^—\n]+)'
        matches = re.findall(pattern, content)
        
        for religious_term, replacement in matches:
            religious_term = religious_term.strip()
            replacement = replacement.strip()
            replacements[religious_term] = replacement
    
    return replacements


def get_all_md_files():
    """Находит все md-файлы в researches/ и terminology/"""
    files = []
    for md_file in RESEARCHES_DIR.rglob("*.md"):
        files.append(md_file)
    for md_file in TERMINOLOGY_DIR.rglob("*.md"):
        files.append(md_file)
    return files


def backup_file(file_path: Path):
    """Создаёт бэкап файла перед изменением"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    rel_path = file_path.relative_to(REPO_ROOT)
    backup_path = BACKUP_DIR / f"{rel_path}.bak"
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "r", encoding="utf-8") as src:
        with open(backup_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())
    return backup_path


def replace_in_file(file_path: Path, replacements: dict, dry_run: bool = False) -> dict:
    """Заменяет религионимы в файле"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    for religious_term, replacement in replacements.items():
        if religious_term in content:
            count = content.count(religious_term)
            content = content.replace(religious_term, replacement)
            changes.append((religious_term, replacement, count))
    
    if content != original_content:
        if not dry_run:
            backup_file(file_path)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        
        return {
            "file": str(file_path.relative_to(REPO_ROOT)),
            "changes": changes,
            "modified": True
        }
    
    return {
        "file": str(file_path.relative_to(REPO_ROOT)),
        "changes": [],
        "modified": False
    }


def show_progress(current, total, file_name, changes_count):
    percent = int(current / total * 100)
    bar_len = 40
    filled = int(bar_len * current / total)
    bar = '█' * filled + '░' * (bar_len - filled)
    sys.stdout.write(f'\r[{bar}] {percent}% ({current}/{total}) | {file_name[:40]:40} | замен: {changes_count}')
    sys.stdout.flush()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Замена религионимов в исследованиях')
    parser.add_argument('--dry-run', action='store_true', help='Пробный запуск (без записи)')
    parser.add_argument('--file', '-f', type=str, help='Обработать только указанный файл')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробный вывод')
    args = parser.parse_args()
    
    print(f"\n{BOLD}{BLUE}🛡️ TAHOR-FILTER — АВТОМАТИЧЕСКАЯ ЗАМЕНА РЕЛИГИОНИЗМОВ{NC}")
    print("=" * 70)
    print(f"Режим: {'ПРОБНЫЙ (без записи)' if args.dry_run else 'РЕАЛЬНЫЙ'}")
    print("")
    
    print("📚 Загрузка замен из tahor/...")
    replacements = load_replacements()
    print(f"   Загружено замен: {len(replacements)}")
    print("")
    
    if args.file:
        files = [REPO_ROOT / args.file]
    else:
        files = get_all_md_files()
    
    print(f"📁 Найдено файлов: {len(files)}")
    print("")
    
    results = []
    total = len(files)
    
    for i, file_path in enumerate(files, 1):
        result = replace_in_file(file_path, replacements, args.dry_run)
        results.append(result)
        show_progress(i, total, file_path.name, len(result['changes']))
    
    print("\n\n" + "=" * 70)
    
    modified = [r for r in results if r['modified']]
    
    if modified:
        print(f"\n{GREEN}✅ ОБРАБОТАНО: {len(modified)} файлов с изменениями{NC}")
        
        total_changes = sum(len(r['changes']) for r in modified)
        print(f"   Всего замен: {total_changes}")
        
        if args.verbose:
            print("\n📝 ДЕТАЛИЗАЦИЯ:")
            for result in modified[:20]:
                print(f"\n   📄 {result['file']}")
                for term, replacement, count in result['changes'][:5]:
                    print(f"      • «{term}» → {replacement} ({count} раз)")
                if len(result['changes']) > 5:
                    print(f"      • ... и ещё {len(result['changes']) - 5} замен")
            if len(modified) > 20:
                print(f"\n   ... и ещё {len(modified) - 20} файлов")
    else:
        print(f"\n{YELLOW}⚠️ Файлов с изменениями не найдено{NC}")
    
    if args.dry_run and modified:
        print(f"\n{YELLOW}💡 Пробный запуск завершён. Уберите --dry-run для реального применения.{NC}")
    
    if not args.dry_run and modified:
        print(f"\n{GREEN}📦 Бэкапы сохранены в: {BACKUP_DIR}{NC}")
        print(f"💡 Для восстановления: cp -r {BACKUP_DIR}/* {REPO_ROOT}/")
    
    print("")


if __name__ == "__main__":
    main()