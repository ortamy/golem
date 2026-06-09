# tools/search.py — поисковый движок по репозиторию
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, print_header, print_success, print_warning, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions", "docs"]
SNIPPET_LENGTH = 100


def search(query: str) -> list:
    """Ищет запрос по всем md-файлам. Возвращает список (файл, сниппет, позиция)."""
    results = []
    query_lower = query.lower()
    query_words = query_lower.split()

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    for filepath in all_files:
        content = read_file_safe(filepath)
        if not content:
            continue

        content_lower = content.lower()
        if query_lower not in content_lower and not all(w in content_lower for w in query_words):
            continue

        rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')

        # Находим все вхождения
        for match in re.finditer(re.escape(query_lower), content_lower):
            start = max(0, match.start() - SNIPPET_LENGTH // 2)
            end = min(len(content), match.end() + SNIPPET_LENGTH // 2)
            snippet = content[start:end].replace('\n', ' ').strip()
            # Подсвечиваем запрос в сниппете
            snippet = re.sub(
                re.escape(query),
                f"**{query}**",
                snippet,
                flags=re.IGNORECASE
            )
            results.append({
                "file": rel_path,
                "snippet": f"...{snippet}...",
                "position": match.start()
            })

    # Сортируем по релевантности: больше вхождений = выше
    results.sort(key=lambda r: r["position"])
    return results


def main():
    if len(sys.argv) < 2:
        print_header("ПОИСК ПО РЕПОЗИТОРИЮ", "🔍")
        print("Использование: python tools/search.py <запрос>")
        print("Примеры:")
        print("  python tools/search.py машиах")
        print("  python tools/search.py 'преданная любовь'")
        print("  python tools/search.py банк")
        return 0

    query = ' '.join(sys.argv[1:])
    print_header(f"ПОИСК: «{query}»", "🔍")

    results = search(query)

    if not results:
        print_warning(f"Ничего не найдено по запросу «{query}»")
        return 0

    # Группируем по файлам
    by_file = defaultdict(list)
    for r in results:
        by_file[r["file"]].append(r)

    print(f"Найдено вхождений: {len(results)} в {len(by_file)} файлах\n")

    for filepath, items in sorted(by_file.items()):
        count = len(items)
        print(f"📄 {filepath} ({count} вхожд.)")
        for item in items[:2]:
            print(f"   {item['snippet'][:120]}")
        if len(items) > 2:
            print(f"   ... и ещё {len(items) - 2}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())