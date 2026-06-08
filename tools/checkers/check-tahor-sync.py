# tools/checkers/check-tahor-sync.py — сверка словарей tahor/ с forbidden-words.md
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, print_header, print_success, print_warning, print_error, REPO_ROOT

TAHOR_DIR = REPO_ROOT / "instructions" / "tahor"
FORBIDDEN_FILE = REPO_ROOT / "instructions" / "forbidden-words.md"


def parse_tahor_files():
    """Извлекает все запрещённые слова из всех файлов tahor/."""
    words = {}  # слово → файл-источник

    for tahor_file in sorted(TAHOR_DIR.glob("*.md")):
        if tahor_file.name == "phrases.md":
            continue

        content = read_file_safe(tahor_file)
        if not content:
            continue

        # Ищем строки вида: `Слово` → иврит (замена)
        for match in re.finditer(r'`([^`]+)`\s*→\s*\S+\s*\(([^)]+)\)', content):
            word = match.group(1).strip()
            if word and re.search(r'[а-яё]', word, re.IGNORECASE):
                words[word] = tahor_file.name

    return words


def parse_forbidden_index():
    """Извлекает все слова из forbidden-words.md."""
    words = {}

    content = read_file_safe(FORBIDDEN_FILE)
    if not content:
        return words

    for match in re.finditer(r'-\s+([А-ЯЁа-яё\s]+?)\s*→\s*\S+\s*\(([^)]+)\)', content):
        word = match.group(1).strip()
        if word:
            words[word] = "forbidden-words.md"

    return words


def main():
    print_header("СВЕРКА СЛОВАРЕЙ tahor/ ↔ forbidden-words.md", "📖")

    tahor_words = parse_tahor_files()
    forbidden_words = parse_forbidden_index()

    print(f"Слов в tahor/: {len(tahor_words)}")
    print(f"Слов в forbidden-words.md: {len(forbidden_words)}")

    # В tahor/ но не в forbidden-words.md
    missing_in_index = {w: s for w, s in tahor_words.items() if w not in forbidden_words}

    # В forbidden-words.md но не в tahor/
    missing_in_tahor = {w: s for w, s in forbidden_words.items() if w not in tahor_words}

    # Дубликаты между файлами tahor/
    duplicates = {}
    seen = {}
    for word, source in tahor_words.items():
        word_lower = word.lower()
        if word_lower in seen:
            if word_lower not in duplicates:
                duplicates[word_lower] = [seen[word_lower]]
            duplicates[word_lower].append(source)
        else:
            seen[word_lower] = source

    if missing_in_index:
        print_warning(f"В tahor/ есть, но нет в forbidden-words.md: {len(missing_in_index)}")
        for word, source in sorted(missing_in_index.items())[:15]:
            print(f"   • «{word}» — из {source}")
        if len(missing_in_index) > 15:
            print(f"   ... и ещё {len(missing_in_index) - 15}")
        print_hint("Добавьте эти слова в forbidden-words.md")

    if missing_in_tahor:
        print_warning(f"В forbidden-words.md есть, но нет в tahor/: {len(missing_in_tahor)}")
        for word, source in sorted(missing_in_tahor.items())[:15]:
            print(f"   • «{word}»")
        if len(missing_in_tahor) > 15:
            print(f"   ... и ещё {len(missing_in_tahor) - 15}")
        print_hint("Добавьте эти слова в соответствующий файл tahor/")

    if duplicates:
        dups_found = {k: v for k, v in duplicates.items() if len(v) > 1}
        if dups_found:
            print_warning(f"Дубликаты между файлами tahor/: {len(dups_found)}")
            for word, sources in sorted(dups_found.items())[:10]:
                print(f"   • «{word}» — в {', '.join(sources)}")

    total_issues = len(missing_in_index) + len(missing_in_tahor) + len(duplicates)
    if total_issues == 0:
        print_success("Словари полностью синхронизированы")
    else:
        print(f"\n📝 Всего расхождений: {total_issues}")

    return 0


if __name__ == "__main__":
    sys.exit(main())