# tools/checkers/check-tahor-sync.py — сверка словарей tahor/ с forbidden-words.md
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, print_header, print_success, print_warning, print_error, print_hint, REPO_ROOT

TAHOR_DIR = REPO_ROOT / "instructions" / "tahor"
FORBIDDEN_FILE = REPO_ROOT / "instructions" / "forbidden-words.md"


def parse_tahor_files():
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

    missing_in_index = {w: s for w, s in tahor_words.items() if w not in forbidden_words}
    missing_in_tahor = {w: s for w, s in forbidden_words.items() if w not in tahor_words}

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

    if missing_in_index:
        print_warning(f"В tahor/ есть, но нет в forbidden-words.md: {len(missing_in_index)}")
        for word, source in sorted(missing_in_index.items())[:10]:
            print(f"   • «{word}» — из {source}")
        if len(missing_in_index) > 10:
            print(f"   ... и ещё {len(missing_in_index) - 10}")

    if missing_in_tahor:
        print_warning(f"В forbidden-words.md есть, но нет в tahor/: {len(missing_in_tahor)}")
        for word in sorted(missing_in_tahor.keys())[:10]:
            print(f"   • «{word}»")
        if len(missing_in_tahor) > 10:
            print(f"   ... и ещё {len(missing_in_tahor) - 10}")

    dups_found = {k: v for k, v in duplicates.items() if len(v) > 1}
    if dups_found:
        print_warning(f"Дубликаты между файлами tahor/: {len(dups_found)}")
        for word, sources in sorted(dups_found.items())[:5]:
            print(f"   • «{word}» — в {', '.join(sources)}")

    total = len(missing_in_index) + len(missing_in_tahor) + len(dups_found)
    if total == 0:
        print_success("Словари синхронизированы")

    return 0


if __name__ == "__main__":
    sys.exit(main())

