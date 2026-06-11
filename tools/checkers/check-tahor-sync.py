#!/usr/bin/env python3
# tools/checkers/check-tahor-sync.py — сверка словарей tahor/ с forbidden-words.md + автофикс
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
import argparse
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_warning, print_error, print_hint,
    ask_yes_no, REPO_ROOT
)

TAHOR_DIR = REPO_ROOT / "instructions" / "tahor"
FORBIDDEN_FILE = REPO_ROOT / "instructions" / "forbidden-words.md"

# Категории для автофикса
CATEGORIES = {
    "religionims.md": "Религионимы",
    "grecisms.md": "Грецизмы",
    "slavicisms.md": "Церковнославянизмы",
    "latinisms.md": "Латинизмы",
    "names.md": "Имена и названия",
}


def parse_tahor_files():
    """Извлекает слова из всех файлов tahor/."""
    words = {}
    for tahor_file in sorted(TAHOR_DIR.glob("*.md")):
        if tahor_file.name == "phrases.md":
            continue
        content = read_file_safe(tahor_file)
        if not content:
            continue
        for match in re.finditer(r'`([^`]+)`\s*→\s*\S+\s*\(([^)]+)\)', content):
            word = match.group(1).strip()
            if word and re.search(r'[а-яё]', word, re.IGNORECASE):
                words[word] = tahor_file.name
    return words


def parse_forbidden_index():
    """Извлекает слова из forbidden-words.md."""
    words = {}
    content = read_file_safe(FORBIDDEN_FILE)
    if not content:
        return words
    for match in re.finditer(r'-\s+([А-ЯЁа-яё\s]+?)\s*→\s*\S+\s*\(([^)]+)\)', content):
        word = match.group(1).strip()
        if word:
            words[word] = "forbidden-words.md"
    return words


def add_to_forbidden_index(missing_words: dict):
    """Добавляет недостающие слова в forbidden-words.md."""
    content = read_file_safe(FORBIDDEN_FILE)
    if not content:
        return 0

    # Группируем по файлам-источникам
    by_source = {}
    for word, source in missing_words.items():
        by_source.setdefault(source, []).append(word)

    added = 0
    # Ищем разделы категорий в forbidden-words.md
    for source, words in by_source.items():
        category = CATEGORIES.get(source, "Религионимы")
        section = f"### {category}"

        if section not in content:
            continue

        # Ищем позицию для вставки: после заголовка секции, перед следующим ###
        section_pos = content.find(section)
        next_section = content.find("\n###", section_pos + len(section))
        if next_section == -1:
            next_section = content.find("\n---", section_pos + len(section))
        if next_section == -1:
            next_section = len(content)

        insert_pos = next_section

        new_entries = []
        for word in sorted(words):
            entry = f"- {word} → ... (...)"
            if entry not in content and word + " →" not in content:
                new_entries.append(entry)

        if new_entries:
            new_text = "\n" + "\n".join(new_entries) + "\n"
            content = content[:insert_pos] + new_text + content[insert_pos:]
            added += len(new_entries)

    if added > 0:
        with open(FORBIDDEN_FILE, "w", encoding="utf-8") as f:
            f.write(content)

    return added


def add_to_tahor_file(missing_words: dict):
    """Добавляет недостающие слова в соответствующие файлы tahor/."""
    added = 0
    for word in sorted(missing_words.keys()):
        # Определяем категорию по первой букве или оставляем religionims.md
        target_file = TAHOR_DIR / "religionims.md"
        filepath = target_file if target_file.exists() else None
        if not filepath:
            continue

        content = read_file_safe(filepath)
        if not content or word in content:
            continue

        # Добавляем в конец файла перед связанными исследованиями
        entry = f"- {word} → ... (...)\n"
        insert_pos = content.rfind("---")
        if insert_pos == -1:
            content += entry
        else:
            content = content[:insert_pos] + entry + content[insert_pos:]

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        added += 1

    return added


def main():
    fix_mode = "--fix" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print_header("СВЕРКА СЛОВАРЕЙ tahor/ ↔ forbidden-words.md", "📖")

    tahor_words = parse_tahor_files()
    forbidden_words = parse_forbidden_index()

    print(f"📚 Слов в tahor/: {len(tahor_words)}")
    print(f"📋 Слов в forbidden-words.md: {len(forbidden_words)}")

    missing_in_index = {w: s for w, s in tahor_words.items() if w not in forbidden_words}
    missing_in_tahor = {w: s for w, s in forbidden_words.items() if w not in tahor_words}

    # Дубликаты
    duplicates = {}
    seen = {}
    for word, source in tahor_words.items():
        wl = word.lower()
        if wl in seen:
            if wl not in duplicates:
                duplicates[wl] = [seen[wl]]
            duplicates[wl].append(source)
        else:
            seen[wl] = source

    # Группировка по источникам
    by_source = {}
    for word, source in missing_in_index.items():
        by_source.setdefault(source, []).append(word)

    # Вывод
    if missing_in_index:
        print_warning(f"\n📝 В tahor/ есть, но нет в forbidden-words.md: {len(missing_in_index)}")
        print("   По файлам:")
        for source, words in sorted(by_source.items()):
            print(f"     {source}: {len(words)} слов")
            if verbose:
                for w in sorted(words)[:10]:
                    print(f"       • {w}")
                if len(words) > 10:
                    print(f"       ... и ещё {len(words) - 10}")
        if not verbose:
            for source, words in sorted(by_source.items()):
                print(f"     {source}: {', '.join(sorted(words)[:5])}...")

    if missing_in_tahor:
        print_warning(f"\n📝 В forbidden-words.md есть, но нет в tahor/: {len(missing_in_tahor)}")
        for word in (sorted(missing_in_tahor.keys()) if verbose else sorted(missing_in_tahor.keys())[:10]):
            print(f"   • «{word}»")
        if not verbose and len(missing_in_tahor) > 10:
            print(f"   ... и ещё {len(missing_in_tahor) - 10}")

    dups_found = {k: v for k, v in duplicates.items() if len(v) > 1}
    if dups_found:
        print_warning(f"\n📋 Дубликаты между файлами tahor/: {len(dups_found)}")
        for word, sources in sorted(dups_found.items())[:5]:
            print(f"   • «{word}» — в {', '.join(sources)}")

    total = len(missing_in_index) + len(missing_in_tahor) + len(dups_found)
    if total == 0:
        print_success("\n🎉 Словари синхронизированы")
        return 0

    if fix_mode:
        print()
        print_header("АВТОФИКС", "🔧")
        total_fixed = 0

        if missing_in_index:
            if ask_yes_no(f"Добавить {len(missing_in_index)} слов в forbidden-words.md?"):
                added = add_to_forbidden_index(missing_in_index)
                print_success(f"Добавлено в forbidden-words.md: {added}")
                total_fixed += added

        if missing_in_tahor:
            if ask_yes_no(f"Добавить {len(missing_in_tahor)} слов в tahor/?"):
                added = add_to_tahor_file(missing_in_tahor)
                print_success(f"Добавлено в tahor/: {added}")
                total_fixed += added

        print(f"\n✅ Всего исправлено: {total_fixed}")
    else:
        print_hint("\n--fix — добавить недостающие слова")

    print()
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())