# tools/checkers/check-religionisms.py — поиск и исправление религионимов
import sys
import re
import json
import os
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_error, print_warning, print_hint, REPO_ROOT

TAHOR_DIR = REPO_ROOT / "instructions" / "tahor"
FORBIDDEN_FILE = REPO_ROOT / "instructions" / "forbidden-words.md"
CACHE_DIR = REPO_ROOT / "tools" / "cache"
CACHE_FILE = CACHE_DIR / "religionisms-cache.json"
SCAN_CACHE_FILE = CACHE_DIR / "scan-cache.json"
DIRTY_CACHE_FILE = CACHE_DIR / "dirty-files.json"

SCAN_DIRS = ["terminology", "researches"]
WORKERS = min(8, os.cpu_count() or 4)

CASES = {
    "male": {"gen": "а", "dat": "у", "acc": "а", "ins": "ом", "prep": "е",
             "nom_pl": "ы", "gen_pl": "ов", "dat_pl": "ам", "acc_pl": "ов", "ins_pl": "ами", "prep_pl": "ах"},
    "female_a": {"gen": "ы", "dat": "е", "acc": "у", "ins": "ой", "prep": "е",
                 "nom_pl": "ы", "gen_pl": "", "dat_pl": "ам", "acc_pl": "", "ins_pl": "ами", "prep_pl": "ах"},
    "female_soft": {"gen": "и", "dat": "и", "acc": "ь", "ins": "ью", "prep": "и",
                    "nom_pl": "и", "gen_pl": "ей", "dat_pl": "ям", "acc_pl": "ей", "ins_pl": "ями", "prep_pl": "ях"},
    "neuter": {"gen": "я", "dat": "ю", "acc": "е", "ins": "ем", "prep": "и",
               "nom_pl": "я", "gen_pl": "ий", "dat_pl": "ям", "acc_pl": "я", "ins_pl": "ями", "prep_pl": "ях"},
}

INDECLINABLE = {"хэн", "руах", "нэфеш", "тоху ва-воху"}


def parse_religionisms_md(filepath):
    pairs = {}
    if not filepath.exists():
        return pairs
    content = read_file_safe(filepath)
    for forbidden, correct in re.findall(r'`([^`]+)`\s*→\s*\S+\s*\(([^)]+)\)', content):
        forbidden, correct = forbidden.strip(), correct.strip().split(",")[0].strip()
        # Берём только русские слова как запрещённые
        if forbidden and correct and re.search(r'[а-яё]', forbidden, re.IGNORECASE):
            pairs[forbidden] = correct
    return pairs


def parse_forbidden_words(filepath):
    pairs = {}
    if not filepath.exists():
        return pairs
    content = read_file_safe(filepath)
    for forbidden, correct in re.findall(r'-\s+([А-ЯЁа-яё\s]+?)\s*→\s*\S+\s*\(([^)]+)\)', content):
        forbidden, correct = forbidden.strip(), correct.strip().split(",")[0].strip()
        if forbidden and correct and forbidden not in pairs:
            pairs[forbidden] = correct
    return pairs


def generate_declensions(word, base_form):
    forms = {word: base_form}
    if word.endswith(("а", "я")): case, stem = "female_a", word[:-1]
    elif word.endswith("ь"): case, stem = "female_soft", word[:-1]
    elif word.endswith(("о", "е")): case, stem = "neuter", word[:-1]
    else: case, stem = "male", word
    for suffix in CASES[case].values():
        forms[stem + suffix] = base_form
    return forms


def build_replacement_map():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if CACHE_FILE.exists():
        try:
            cache = json.loads(read_file_safe(CACHE_FILE))
            if cache.get("_version") == "2.4":
                return cache["replacements"], cache["fast_filter"], re.compile(cache["mega_regex"])
        except Exception:
            pass

    pairs = {}
    pairs.update(parse_forbidden_words(FORBIDDEN_FILE))
    for tahor_file in TAHOR_DIR.glob("*.md"):
        if tahor_file.name != "phrases.md":
            pairs.update(parse_religionisms_md(tahor_file))

    replacements = {}
    for word, correct in pairs.items():
        if correct.lower() in INDECLINABLE or " " in correct:
            replacements[word] = correct
        else:
            replacements.update(generate_declensions(word, correct))

    # Оставляем только русские слова для поиска
    ru_replacements = {w: c for w, c in replacements.items() if re.search(r'[а-яё]', w, re.IGNORECASE)}

    fast_filter = sorted({w[:4].lower() for w in ru_replacements if len(w) >= 4})

    # Мега-regex только из русских слов
    sorted_words = sorted(ru_replacements.keys(), key=len, reverse=True)
    mega_regex = re.compile(r'\b(' + '|'.join(re.escape(w) for w in sorted_words) + r')\b', re.IGNORECASE)

    cache_data = {
        "_version": "2.4",
        "replacements": ru_replacements,
        "fast_filter": fast_filter,
        "mega_regex": mega_regex.pattern
    }
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

    return ru_replacements, fast_filter, mega_regex


def load_scan_cache():
    if SCAN_CACHE_FILE.exists():
        try:
            return json.loads(read_file_safe(SCAN_CACHE_FILE))
        except Exception:
            pass
    return {}


def save_scan_cache(cache):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(SCAN_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def load_dirty_cache():
    if DIRTY_CACHE_FILE.exists():
        try:
            return set(json.loads(read_file_safe(DIRTY_CACHE_FILE)))
        except Exception:
            pass
    return set()


def save_dirty_cache(dirty_set):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(DIRTY_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(dirty_set), f, ensure_ascii=False, indent=2)


def find_religionisms_fast(text, mega_regex, replacements):
    """Один regex-проход. Ищет только русские слова."""
    found = Counter()
    clean = re.sub(r'«[^»]*»|"[^"]*"|\'[^\']*\'', ' ', text)
    for match in mega_regex.finditer(clean):
        word = match.group()
        # Дополнительная проверка: слово должно быть в словаре (регистронезависимо)
        if word.lower() in (w.lower() for w in replacements):
            found[word] += 1
    return dict(found)


def fix_religionisms(text, replacements, mega_regex):
    """Замена через один regex-проход."""
    count = 0
    quoted_map = {f"__Q{i}__": m.group() for i, m in enumerate(re.finditer(r'«[^»]*»|"[^"]*"|\'[^\']*\'', text))}
    for placeholder, original in quoted_map.items():
        text = text.replace(original, placeholder, 1)

    def replacer(match):
        nonlocal count
        count += 1
        word = match.group()
        # Ищем в словаре регистронезависимо
        word_lower = word.lower()
        for w, correct in replacements.items():
            if w.lower() == word_lower:
                return correct[0].upper() + correct[1:] if word[0].isupper() else correct
        return word

    text = mega_regex.sub(replacer, text)

    for placeholder, original in quoted_map.items():
        text = text.replace(placeholder, original, 1)
    return text, count


def check_one_file(md_file, replacements, fast_filter, mega_regex, scan_cache, check_only):
    """Проверка одного файла (для многопоточности)."""
    rel_path = str(md_file.relative_to(REPO_ROOT))
    mtime = md_file.stat().st_mtime

    if check_only and rel_path in scan_cache and scan_cache[rel_path].get("mtime") == mtime and scan_cache[rel_path].get("clean"):
        return None, None, True

    content = read_file_safe(md_file)
    if content is None:
        return None, None, True

    if not any(prefix in content.lower() for prefix in fast_filter):
        return rel_path, {"mtime": mtime, "clean": True}, True

    found = find_religionisms_fast(content, mega_regex, replacements)
    if found:
        result = {"mtime": mtime, "clean": False}
        if not check_only:
            fixed, reps = fix_religionisms(content, replacements, mega_regex)
            if reps > 0:
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(fixed)
                result = {"mtime": os.path.getmtime(md_file), "clean": False}
        return rel_path, result, found
    else:
        return rel_path, {"mtime": mtime, "clean": True}, True


def scan_files(replacements, fast_filter, mega_regex, check_only=True):
    total_found = Counter()
    files_with_issues = []
    total_replacements = 0
    scan_cache = load_scan_cache()
    dirty_set = load_dirty_cache()

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    if dirty_set and check_only:
        dirty_files = []
        clean_files = []
        for f in all_files:
            rel = str(f.relative_to(REPO_ROOT))
            if rel in dirty_set:
                dirty_files.append(f)
            else:
                mtime = f.stat().st_mtime
                if rel in scan_cache and scan_cache[rel].get("mtime") == mtime and scan_cache[rel].get("clean"):
                    clean_files.append(f)
                else:
                    dirty_files.append(f)
        skipped = len(clean_files)
        all_files = dirty_files
    else:
        skipped = 0

    total = len(all_files) + skipped
    if total == 0:
        return {}, [], 0

    completed = skipped
    new_dirty = set()

    if not check_only:
        for i, md_file in enumerate(all_files, 1):
            rel_path, result, found = check_one_file(md_file, replacements, fast_filter, mega_regex, scan_cache, check_only)
            if result:
                scan_cache[rel_path] = result
            if found and found is not True:
                files_with_issues.append((rel_path, found))
                for word, cnt in found.items():
                    total_found[word] += cnt
                new_dirty.add(rel_path)
                if not check_only:
                    total_replacements += 1
            elif found is True:
                new_dirty.discard(rel_path)
            completed += 1
            progress_bar(completed, total, extra=f"найдено: {len(files_with_issues)}")
    else:
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = {executor.submit(check_one_file, f, replacements, fast_filter, mega_regex, scan_cache, check_only): f for f in all_files}
            for future in as_completed(futures):
                rel_path, result, found = future.result()
                if result:
                    scan_cache[rel_path] = result
                if found and found is not True:
                    files_with_issues.append((rel_path, found))
                    for word, cnt in found.items():
                        total_found[word] += cnt
                    new_dirty.add(rel_path)
                elif found is True:
                    new_dirty.discard(rel_path)
                completed += 1
                progress_bar(completed, total, extra=f"потоков: {WORKERS} | найдено: {len(files_with_issues)}")

    finish_progress()
    save_scan_cache(scan_cache)
    save_dirty_cache(new_dirty)
    return dict(total_found), files_with_issues, total_replacements


def main():
    check_only = "--fix" not in sys.argv
    rebuild_cache = "--rebuild" in sys.argv

    if rebuild_cache:
        for f in (CACHE_FILE, SCAN_CACHE_FILE, DIRTY_CACHE_FILE):
            if f.exists():
                f.unlink()
        print("🗑️ Кэш удалён.")

    print_header("ЗАГРУЗКА СЛОВАРЯ ЗАМЕН", "📖")
    replacements, fast_filter, mega_regex = build_replacement_map()
    print(f"✅ Загружено русских слов: {len(replacements)}")
    print(f"⚡ Быстрый фильтр: {len(fast_filter)} префиксов")

    print_header("ПРОВЕРКА НА РЕЛИГИОНИЗМЫ" if check_only else "ИСПРАВЛЕНИЕ РЕЛИГИОНИЗМОВ",
                 "🔍" if check_only else "🔧")

    total_found, files_with_issues, total_replacements = scan_files(replacements, fast_filter, mega_regex, check_only)

    if not files_with_issues:
        print_success("Религионизмов не найдено")
        return 0

    print(f"📁 Файлов с религионимами: {len(files_with_issues)}")
    print(f"📝 Всего найдено слов: {sum(total_found.values())}\n")

    print("🔝 Самые частые:")
    for word, cnt in sorted(total_found.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {word:15} {cnt:4}  {'█' * min(cnt, 50)}")

    print(f"\n📋 Файлы (первые 15):")
    for file_path, found in files_with_issues[:15]:
        total = sum(found.values())
        top_word = max(found, key=found.get)
        print(f"  • {file_path} — {total} шт. (чаще: «{top_word}»)")

    if len(files_with_issues) > 15:
        print(f"  ... и ещё {len(files_with_issues) - 15} файлов")

    if check_only:
        print_hint("Для исправления: python tools/checkers/check-religionisms.py --fix")
        print_hint("Перестроить кэш:  python tools/checkers/check-religionisms.py --rebuild")
    else:
        print_success(f"Исправлено: {total_replacements} замен в {len(files_with_issues)} файлах")

    return 0


if __name__ == "__main__":
    sys.exit(main())