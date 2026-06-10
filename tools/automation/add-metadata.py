#!/usr/bin/env python3
# add-metadata.py — массовое добавление метаданных в файлы

# import os  # TODO: проверить, используется ли
import re
import argparse
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent

METADATA_TEMPLATE = '''**Метаданные файла**
- **Файл:** `{file_path}`
- **Версия:** 1.0
- **Дата создания:** {date}
- **Последнее обновление:** {date}
- **Причина обновления:** Добавлены метаданные
- **Статус:** Активный
- **Тема:** {topic}

'''

def extract_topic(content: str, file_name: str) -> str:
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            clean = re.sub(r'^# [^\w]+\s*', '', line)
            return clean[:100]
    name = file_name.replace('-', ' ').replace('.md', '')
    return name.capitalize()

def has_metadata(content: str) -> bool:
    return '**Метаданные файла**' in content

def add_metadata_to_file(file_path: Path, dry_run: bool = False):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if has_metadata(content):
        return False

    topic = extract_topic(content, file_path.name)
    rel_path = file_path.relative_to(REPO_ROOT)
    today = datetime.now().strftime("%Y-%m-%d")

    metadata = METADATA_TEMPLATE.format(
        file_path=rel_path,
        date=today,
        topic=topic
    )

    lines = content.split('\n')
    if lines and lines[0].startswith('# '):
        new_content = lines[0] + '\n\n' + metadata + '\n' + '\n'.join(lines[1:])
    else:
        new_content = metadata + content

    if not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, help='Папка для обработки')
    parser.add_argument('--dry-run', action='store_true', help='Пробный запуск')
    args = parser.parse_args()

    if args.dir:
        target_dir = REPO_ROOT / args.dir
        files = list(target_dir.glob('*.md'))
    else:
        files = []
        for d in ['terminology', 'researches', 'instructions', 'checkers', 'davar', 'ideas', 'drafts']:
            target_dir = REPO_ROOT / d
            if target_dir.exists():
                files.extend(target_dir.glob('*.md'))

    print(f"📁 Найдено файлов: {len(files)}")
    print(f"🔧 Режим: {'DRY-RUN (без записи)' if args.dry_run else 'РЕАЛЬНЫЙ'}")
    print("")

    updated = 0
    for file_path in files:
        if has_metadata(file_path.read_text(encoding='utf-8')):
            continue
        rel_path = file_path.relative_to(REPO_ROOT)
        print(f"  {'🔵' if args.dry_run else '✅'} {rel_path}")
        add_metadata_to_file(file_path, args.dry_run)
        updated += 1

    print("")
    print(f"📊 Файлов без метаданных: {updated}")
    if args.dry_run:
        print("   Уберите --dry-run для реального добавления")

if __name__ == "__main__":
    main()

