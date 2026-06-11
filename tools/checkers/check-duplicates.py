#!/usr/bin/env python3
# tools/checkers/check-duplicates.py — быстрый поиск дубликатов среди md-файлов
import sys
import re
import hashlib
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

sys.path.insert(0, str(Path(__file__).parent.parent))
import argparse
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_error, print_warning, print_hint,
    ask_yes_no, REPO_ROOT
)

TARGET_DIRS = ['terminology', 'researches']
SIMILARITY_THRESHOLD = 0.85
MIN_CONTENT_LENGTH = 200


def extract_title(content: str) -> str:
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    return match.group(1).strip().lower() if match else ""


def extract_body(content: str) -> str:
    body = re.sub(r'\*\*Метаданные файла\*\*.*?(?=\n---|\n# |\Z)', '', content, flags=re.DOTALL)
    body = re.sub(r'^#.*$', '', body, flags=re.MULTILINE)
    return body.strip()


def content_hash(content: str) -> str:
    body = extract_body(content)
    return hashlib.md5(body.encode('utf-8')).hexdigest()


def similarity(a: str, b: str) -> float:
    """Сравнивает первые 500 символов тела."""
    body_a = extract_body(a)[:500].lower()
    body_b = extract_body(b)[:500].lower()
    if not body_a or not body_b:
        return 0
    if abs(len(body_a) - len(body_b)) > 200:
        return 0
    try:
        return SequenceMatcher(None, body_a, body_b).ratio()
    except:
        return 0


def main():
    fix_mode = "--fix" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print_header("ПОИСК ДУБЛИКАТОВ", "📋")

    files = {}
    for target_dir in TARGET_DIRS:
        dir_path = REPO_ROOT / target_dir
        if dir_path.exists():
            for md_file in dir_path.rglob('*.md'):
                content = read_file_safe(md_file)
                if content and len(content) > MIN_CONTENT_LENGTH:
                    files[str(md_file.relative_to(REPO_ROOT))] = content

    total = len(files)
    print(f"🔍 Файлов: {total}")

    # Этап 1: точные дубликаты по хешу
    print("📊 Этап 1: точные дубликаты...")
    hash_groups = defaultdict(list)
    for i, (name, content) in enumerate(files.items(), 1):
        h = content_hash(content)
        hash_groups[h].append(name)
        progress_bar(i, total)

    finish_progress()

    exact_duplicates = {h: names for h, names in hash_groups.items() if len(names) > 1}
    print(f"  Точных дубликатов: {len(exact_duplicates)} групп")

    # Фильтруем оставшиеся
    remaining = {}
    for name, content in files.items():
        h = content_hash(content)
        if h not in exact_duplicates:
            remaining[name] = content

    # Этап 2: похожие файлы (по папке и заголовку)
    similar = []
    if len(remaining) > 1:
        print(f"📊 Этап 2: похожие файлы ({len(remaining)} файлов)...")

        by_folder_title = defaultdict(list)
        for name, content in remaining.items():
            folder = str(Path(name).parent)
            title = extract_title(content)
            key_words = ' '.join(title.split()[:2]) if title else ''
            key = f"{folder}|{key_words}"
            by_folder_title[key].append((name, content))

        groups = [(k, v) for k, v in by_folder_title.items() if len(v) > 1]
        total_groups = len(groups)
        print(f"  Групп для сравнения: {total_groups}")

        for i, (key, group) in enumerate(groups, 1):
            for j, (name1, c1) in enumerate(group):
                for name2, c2 in group[j+1:]:
                    sim = similarity(c1, c2)
                    if sim >= SIMILARITY_THRESHOLD:
                        similar.append((name1, name2, sim))
            if i % 20 == 0:
                progress_bar(i, total_groups, extra=f"похожих: {len(similar)}")

        finish_progress()
        print(f"  Похожих пар: {len(similar)}")

    # Вывод
    total_duplicates = len(exact_duplicates) + len(similar)

    if total_duplicates == 0:
        print_success("\n🎉 Дубликатов не найдено")
        return 0

    if exact_duplicates:
        total_files = sum(len(v) for v in exact_duplicates.values())
        print_error(f"\n📋 ТОЧНЫЕ ДУБЛИКАТЫ: {len(exact_duplicates)} групп ({total_files} файлов)")
        for h, names in sorted(exact_duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"  Группа ({len(names)} файлов):")
            for name in names:
                print(f"    • {name}")

    if similar:
        print_warning(f"\n📝 ПОХОЖИЕ ФАЙЛЫ: {len(similar)} пар")
        for name1, name2, sim in sorted(similar, key=lambda x: x[2], reverse=True)[:10]:
            print(f"  • {name1} ↔ {name2} ({sim:.0%})")

    if fix_mode:
        print()
        print_header("АВТОФИКС", "🔧")

        to_delete = []
        for h, names in exact_duplicates.items():
            sorted_names = sorted(names, key=lambda n: (len(n), n))
            to_delete.extend(sorted_names[1:])

        if to_delete and ask_yes_no(f"Удалить {len(to_delete)} файлов-дубликатов?"):
            deleted = 0
            for name in to_delete:
                try:
                    (REPO_ROOT / name).unlink()
                    deleted += 1
                except:
                    pass
            print_success(f"Удалено: {deleted}")

        if similar and ask_yes_no(f"Пометить {len(similar)} похожих пар комментариями?"):
            marked = 0
            for name1, name2, _ in similar:
                for name in (name1, name2):
                    filepath = REPO_ROOT / name
                    content = read_file_safe(filepath)
                    if content and "⚠️ ДУБЛИКАТ" not in content:
                        comment = f"\n<!-- ⚠️ ДУБЛИКАТ: похож на {name2 if name == name1 else name1} -->\n"
                        h1_match = re.search(r'^#\s+.+$', content, re.MULTILINE)
                        if h1_match:
                            pos = h1_match.end() + 1
                            new_content = content[:pos] + comment + content[pos:]
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            marked += 1
            print_success(f"Помечено: {marked} файлов")
    else:
        print_hint("\n--fix — удалить точные дубликаты, пометить похожие")

    print()
    return 1 if total_duplicates else 0


if __name__ == "__main__":
    sys.exit(main())