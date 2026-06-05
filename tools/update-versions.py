#!/usr/bin/env python3
# update-versions.py — массовое обновление версий и дат в файлах

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).parent.parent
TARGET_DIRS = ['terminology', 'researches', 'instructions', 'checkers']
IGNORE_FILES = {'README.md', 'structure.md', 'GLOSSARY.md'}

VERSION_PATTERN = re.compile(r'^(\d+)\.(\d+)$')


def parse_version(version: str) -> Tuple[int, int]:
    """Разбирает версию на major и minor"""
    match = VERSION_PATTERN.match(version)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0


def bump_minor(version: str) -> str:
    """Увеличивает minor версию"""
    major, minor = parse_version(version)
    return f"{major}.{minor + 1}"


def bump_major(version: str) -> str:
    """Увеличивает major версию"""
    major, _ = parse_version(version)
    return f"{major + 1}.0"


def update_file_metadata(file_path: Path, bump_type: str = 'minor', dry_run: bool = True) -> bool:
    """Обновляет метаданные файла"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '**Метаданные файла**' not in content:
        return False
    
    today = datetime.now().strftime("%Y-%m-%d")
    new_content = content
    changes = []
    
    version_match = re.search(r'-\s*\*\*Версия:\*\*\s*(\d+\.\d+)', content)
    if version_match:
        old_version = version_match.group(1)
        if bump_type == 'major':
            new_version = bump_major(old_version)
        else:
            new_version = bump_minor(old_version)
        
        new_content = re.sub(
            r'(-\s*\*\*Версия:\*\*\s*)\d+\.\d+',
            rf'\g<1>{new_version}',
            new_content
        )
        changes.append(f"версия: {old_version} → {new_version}")
    
    date_match = re.search(r'-\s*\*\*Последнее обновление:\*\*\s*(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        old_date = date_match.group(1)
        new_content = re.sub(
            r'(-\s*\*\*Последнее обновление:\*\*\s*)\d{4}-\d{2}-\d{2}',
            rf'\g<1>{today}',
            new_content
        )
        changes.append(f"дата: {old_date} → {today}")
    else:
        new_content = re.sub(
            r'(-\s*\*\*Дата создания:\*\*\s*\d{4}-\d{2}-\d{2})',
            rf'\g<1>\n- **Последнее обновление:** {today}',
            new_content
        )
        changes.append(f"добавлено поле: последнее обновление ({today})")
    
    reason_match = re.search(r'-\s*\*\*Причина обновления:\*\*\s*(.+)', content)
    if reason_match:
        old_reason = reason_match.group(1)
        if old_reason.strip() == '' or old_reason == 'Создание файла':
            new_content = re.sub(
                r'(-\s*\*\*Причина обновления:\*\*\s*).+',
                rf'\g<1>Автоматическое обновление версии',
                new_content
            )
            changes.append("причина обновления: обновлено")
    
    if not dry_run and changes:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    return changes


def find_affected_files() -> List[Path]:
    """Находит файлы, требующие обновления"""
    files = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    for target_dir in TARGET_DIRS:
        dir_path = REPO_ROOT / target_dir
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.rglob('*.md'):
            if md_file.name in IGNORE_FILES:
                continue
            
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '**Метаданные файла**' not in content:
                continue
            
            last_update_match = re.search(r'-\s*\*\*Последнее обновление:\*\*\s*(\d{4}-\d{2}-\d{2})', content)
            if last_update_match:
                last_update = last_update_match.group(1)
                if last_update != today:
                    files.append(md_file)
            else:
                files.append(md_file)
    
    return files


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Массовое обновление версий файлов')
    parser.add_argument('--type', choices=['minor', 'major'], default='minor', help='Тип обновления версии')
    parser.add_argument('--dry-run', action='store_true', help='Пробный запуск (без записи)')
    parser.add_argument('--all', action='store_true', help='Обновить все файлы, не только устаревшие')
    args = parser.parse_args()
    
    print("🔄 ОБНОВЛЕНИЕ ВЕРСИЙ")
    print("====================")
    print(f"Тип: {'MAJOR' if args.type == 'major' else 'minor'}")
    print(f"Режим: {'пробный' if args.dry_run else 'реальный'}")
    print("")
    
    if args.all:
        files = []
        for target_dir in TARGET_DIRS:
            dir_path = REPO_ROOT / target_dir
            if dir_path.exists():
                files.extend(dir_path.rglob('*.md'))
    else:
        files = find_affected_files()
    
    print(f"📊 Найдено файлов для обновления: {len(files)}")
    print("")
    
    updated = 0
    for file_path in files:
        changes = update_file_metadata(file_path, args.type, args.dry_run)
        if changes:
            rel_path = file_path.relative_to(REPO_ROOT)
            print(f"  📄 {rel_path}")
            for change in changes:
                print(f"     • {change}")
            updated += 1
            print("")
    
    if args.dry_run:
        print(f"✅ Пробный запуск: {updated} файлов будет обновлено")
        print("   Уберите --dry-run для реального обновления")
    else:
        print(f"✅ Обновлено файлов: {updated}")


if __name__ == "__main__":
    main()
