# tools/utils/search.py — search
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_hint, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions", "docs", "drafts", "ideas"]
SNIPPET_LENGTH = 120
TOP_RESULTS = 20


def search(query: str, limit: int = TOP_RESULTS) -> list:
    """Ищет запрос по всем md-файлам. Возвращает список (файл, сниппет, релевантность)."""
    results = []
    query_lower = query.lower()
    query_words = query_lower.split()

    # Собираем все файлы
    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    print(f"🔍 Ищу «{query}» в {total} файлах...")

    for i, filepath in enumerate(all_files, 1):
        content = read_file_safe(filepath)
        if not content:
            continue

        content_lower = content.lower()

        # Быстрая проверка — есть ли хоть одно слово
        if not any(w in content_lower for w in query_words):
            progress_bar(i, total, extra=f"найдено: {len(results)}")
            continue

        rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
        score = 0

        # Ищем все слова запроса
        file_matches = []
        for word in query_words:
            for match in re.finditer(re.escape(word), content_lower):
                start = max(0, match.start() - SNIPPET_LENGTH // 2)
                end = min(len(content), match.end() + SNIPPET_LENGTH // 2)
                snippet = content[start:end].replace('\n', ' ').strip()
                file_matches.append(snippet)
                score += 1

        if file_matches:
            # Уникальные сниппеты (первые 3)
            unique_snippets = list(dict.fromkeys(file_matches))[:3]
            results.append({
                "file": rel_path,
                "snippets": unique_snippets,
                "score": score,
                "matches": len(file_matches)
            })

        progress_bar(i, total, extra=f"найдено: {len(results)}")

    finish_progress()

    # Сортируем по релевантности
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:limit]


def highlight(text: str, query: str) -> str:
    """Подсвечивает слова запроса в тексте."""
    words = query.lower().split()
    for word in words:
        text = re.sub(
            re.escape(word),
            lambda m: f"\033[93m{m.group()}\033[0m",
            text,
            flags=re.IGNORECASE
        )
    return text


def main():
    if len(sys.argv) < 2:
        print_header("ПОИСК ПО РЕПОЗИТОРИЮ", "🔍")
        print("Использование: python tools/search.py <запрос> [--limit N] [--verbose]")
        print("Примеры:")
        print("  python tools/search.py машиах")
        print("  python tools/search.py 'преданная любовь' --limit 5")
        print("  python tools/search.py банк --verbose")
        print("")
        print("Опции:")
        print("  --limit N    Показать только N результатов (по умолчанию 20)")
        print("  --verbose    Показать все сниппеты для каждого файла")
        return 0

    # Парсим аргументы
    limit = TOP_RESULTS
    verbose = False
    query_parts = []

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--verbose":
            verbose = True
            i += 1
        else:
            query_parts.append(sys.argv[i])
            i += 1

    query = ' '.join(query_parts)

    print_header(f"ПОИСК: «{query}»", "🔍")

    results = search(query, limit)

    if not results:
        print_warning(f"Ничего не найдено по запросу «{query}»")
        print_hint("Попробуйте другое слово или более короткий запрос")
        return 0

    # Группируем по файлам
    by_file = defaultdict(list)
    for r in results:
        by_file[r["file"]].append(r)

    total_matches = sum(r["matches"] for r in results)
    print(f"\n📊 Найдено: {total_matches} вхождений в {len(by_file)} файлах (показано {len(results)})\n")

    for i, (filepath, items) in enumerate(by_file.items(), 1):
        item = items[0]  # Все элементы для одного файла одинаковые
        count = item["matches"]
        score = item["score"]

        print(f"{i:2}. 📄 {filepath}")
        print(f"    {count} вхожд. | релевантность: {score}")

        if verbose:
            for snippet in item["snippets"]:
                print(f"    ── {highlight(snippet[:150], query)}")
        else:
            # Показываем только первый сниппет
            first = item["snippets"][0] if item["snippets"] else ""
            print(f"    ── {highlight(first[:150], query)}")
            if len(item["snippets"]) > 1:
                print(f"    ... ещё {len(item['snippets']) - 1} сниппетов (--verbose для всех)")

        print()

    print_hint("Поиск по ивриту: python tools/search.py 'אֱמוּנָה'")

    return 0


if __name__ == "__main__":
    sys.exit(main())