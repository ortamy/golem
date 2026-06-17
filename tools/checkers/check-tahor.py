#!/usr/bin/env python3
# tools/checkers/check-tahor.py — полная проверка чистоты языка (v5.0)

import sys
import re
import json
import os
import hashlib
from pathlib import Path
from collections import Counter
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_error, print_warning, print_hint,
    REPO_ROOT
)

DICTS_DIR = REPO_ROOT / "instructions" / "dictionaries"
CACHE_DIR = REPO_ROOT / "tools" / "cache"
CACHE_FILE = CACHE_DIR / "cache-tahor.json"
SCAN_CACHE_FILE = CACHE_DIR / "cache-scan.json"
DIRTY_CACHE_FILE = CACHE_DIR / "cache-tahor-dirty.json"

SCAN_DIRS = ["content"]
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


def load_hebrew_whitelist():
    words = {
        "тора", "танах", "машиах", "шаббат", "йешуа", "яхве", "yhwh",
        "элоhим", "эль", "руах", "нэфеш", "нефеш", "шеол", "сатан",
        "шалом", "брит", "кодеш", "мишпат", "цдака", "тшува", "эмуна",
        "эмет", "хесед", "кавод", "коhэн", "нави", "малъах", "микве",
        "мишкан", "корбан", "тефила", "тфила", "твила", "йовель", "шмита",
    }
    term_dir = REPO_ROOT / "content" / "terminology"
    if term_dir.exists():
        for f in term_dir.glob("*.md"):
            words.add(f.stem.lower())
    return words


HEBREW_WHITELIST = load_hebrew_whitelist()


def build_tahor_cache():
    """Сканирует словари из instructions/dictionaries/ и создаёт cache-tahor.json"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    replacements = {}
    dict_dir = DICTS_DIR

    if not dict_dir.exists():
        print_warning(f"Папка словарей не найдена: {dict_dir}")
        return {}

    for dict_file in sorted(dict_dir.glob("*.md")):
        content = read_file_safe(dict_file)
        if not content:
            continue

        category = dict_file.stem

        for line in content.split("\n"):
            line = line.strip()
            if not line.startswith("- **"):
                continue

            match = re.search(r'\*\*(.+?)\*\*', line)
            if not match:
                continue

            forbidden = match.group(1).strip()

            replacement_match = re.search(r'[→—]\s*(.+?)$', line)
            if not replacement_match:
                continue

            replacement_text = replacement_match.group(1).strip()
            main_word = re.sub(r'\s*\(.*?\)', '', replacement_text).strip()
            main_word = main_word.split(",")[0].strip()

            translit_match = re.search(r'\((.+?)\)', replacement_text)
            translit = translit_match.group(1).split(",")[0].strip() if translit_match else main_word

            hebrew_match = re.search(r'[\u0590-\u05FF]{2,}', replacement_text)
            hebrew = hebrew_match.group(0) if hebrew_match else ""

            if not forbidden or not main_word or forbidden.lower() == main_word.lower():
                continue

            cases = "male"
            if forbidden.endswith("ость") or forbidden.endswith("сть"):
                cases = "female_a"
            elif forbidden.endswith("ие") or forbidden.endswith("ье"):
                cases = "neuter"
            elif forbidden.endswith("а") or forbidden.endswith("я"):
                cases = "female_a"
            elif forbidden.endswith("ь"):
                cases = "female_soft"

            first_form = f"{main_word} ({translit}"
            if hebrew:
                first_form += f", {hebrew}"
            first_form += ")"

            upper_form = first_form.upper()

            replacements[forbidden] = {
                "short": translit if translit != main_word else main_word,
                "first": first_form,
                "upper": upper_form,
                "note": category,
                "cases": cases,
            }

    cache_data = {
        "_version": "5.0",
        "_description": "Словарь замен для check-tahor.py — все категории",
        "_categories": [f.stem for f in sorted(dict_dir.glob("*.md"))],
        "replacements": replacements,
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

    return replacements


def generate_declensions(word, data):
    forms = {}
    case_type = data.get("cases", "male")
    if case_type == "indeclinable" or " " in word:
        forms[word] = data
        return forms
    case_endings = CASES.get(case_type, CASES["male"])
    stem = word[:-1] if word[-1] in "аяьое" else word
    for suffix_name, suffix in case_endings.items():
        if suffix:
            forms[stem + suffix] = data
        else:
            forms[stem] = data
    forms[word] = data
    return forms


def expand_declensions(replacements):
    expanded = {}
    for word, data in replacements.items():
        expanded.update(generate_declensions(word, data))
    return expanded


def build_replacement_map(rebuild=False):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if CACHE_FILE.exists() and not rebuild:
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            replacements = data.get("replacements", {})
            expanded = expand_declensions(replacements)
            sorted_words = sorted(expanded.keys(), key=len, reverse=True)
            mega_regex = re.compile(
                r'\b(' + '|'.join(re.escape(w) for w in sorted_words) + r')\b',
                re.IGNORECASE
            )
            fast_filter = sorted({w[:4].lower() for w in expanded if len(w) >= 4})
            print(f"✅ Загружено терминов: {len(set(d['short'] for d in replacements.values()))}")
            print(f"📝 Всего форм (со склонениями): {len(expanded)}")
            return expanded, fast_filter, mega_regex
        except Exception as e:
            print_warning(f"Ошибка загрузки JSON: {e}. Перестройте: --rebuild")
            return {}, [], None

    print("📖 Сканирование словарей...")
    replacements = build_tahor_cache()

    if not replacements:
        return {}, [], None

    print(f"✅ Создан cache-tahor.json: {len(replacements)} базовых терминов")
    print(f"📂 Категории: {len(set(d['note'] for d in replacements.values()))}")

    expanded = expand_declensions(replacements)
    sorted_words = sorted(expanded.keys(), key=len, reverse=True)
    mega_regex = re.compile(
        r'\b(' + '|'.join(re.escape(w) for w in sorted_words) + r')\b',
        re.IGNORECASE
    )
    fast_filter = sorted({w[:4].lower() for w in expanded if len(w) >= 4})

    return expanded, fast_filter, mega_regex


def extract_metadata_block(content: str) -> tuple:
    if '**Метаданные файла**' not in content:
        return -1, -1
    start = content.find('**Метаданные файла**')
    rest = content[start:]
    end_match = re.search(r'\n---|\n# |\n## ', rest[30:])
    end = start + 30 + end_match.start() if end_match else len(content)
    return start, end


def protect_metadata(content: str) -> tuple:
    start, end = extract_metadata_block(content)
    if start == -1:
        return content, ""
    original = content[start:end]
    placeholder = f"__METADATA_BLOCK_{hash(original) & 0x7FFFFFFF}__"
    return content[:start] + placeholder + content[end:], original


def restore_metadata(text: str, original_metadata: str) -> str:
    match = re.search(r'__METADATA_BLOCK_\d+__', text)
    if match:
        return text[:match.start()] + original_metadata + text[match.end():]
    return text


def update_metadata_fields(content: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    counter_match = re.search(r'[-*]\s*\*\*Проверок на религионизмы:\*\*\s*(\d+)', content)
    if counter_match:
        count = int(counter_match.group(1)) + 1
        content = re.sub(
            r'[-*]\s*\*\*Проверок на религионизмы:\*\*\s*\d+',
            f'- **Проверок на религионизмы:** {count}', content
        )
    content = re.sub(
        r'[-*]\s*\*\*Последняя проверка:\*\*\s*[^\n]+',
        f'- **Последняя проверка:** {today}', content
    )
    body_start = content.find('---\n', content.find('**Метаданные файла**'))
    if body_start != -1:
        body = content[body_start + 4:]
        new_hash = hashlib.md5(body.encode('utf-8')).hexdigest()[:8]
        if re.search(r'[-*]\s*\*\*Хеш:\*\*\s*\S+', content):
            content = re.sub(r'[-*]\s*\*\*Хеш:\*\*\s*\S+', f'- **Хеш:** {new_hash}', content)
    return content


def is_header_line(line):
    return bool(re.match(r'^#{1,4}\s', line))


def fix_religionisms(text, replacements, mega_regex):
    protected, metadata = protect_metadata(text)
    quoted_map = {}
    quote_pattern = re.compile(r'«[^»]*»|"[^"]*"|\'[^\']*\'')
    for i, m in enumerate(quote_pattern.finditer(protected)):
        placeholder = f"__Q{i}__"
        quoted_map[placeholder] = m.group()
        protected = protected.replace(m.group(), placeholder, 1)

    code_map = {}
    code_pattern = re.compile(r'`([^`]+)`')
    for i, m in enumerate(code_pattern.finditer(protected)):
        placeholder = f"__C{i}__"
        code_map[placeholder] = m.group()
        protected = protected.replace(m.group(), placeholder, 1)

    replaced_in_file = {}
    lines = protected.split("\n")
    new_lines = []

    for line in lines:
        if is_header_line(line):
            new_lines.append(fix_header_line(line, replacements, mega_regex, replaced_in_file))
        elif re.search(r'[α-ωΑ-Ω]', line):
            new_lines.append(line)
        elif re.match(r'^[-*]\s*\*\*[^*]+\*\*:', line):
            new_lines.append(line)
        else:
            new_lines.append(fix_body_line(line, replacements, mega_regex, replaced_in_file))

    protected = "\n".join(new_lines)

    for placeholder, original in code_map.items():
        protected = protected.replace(placeholder, original, 1)
    for placeholder, original in quoted_map.items():
        protected = protected.replace(placeholder, original, 1)

    if metadata:
        protected = restore_metadata(protected, metadata)

    total_count = sum(1 for v in replaced_in_file.values())
    if total_count > 0:
        protected = update_metadata_fields(protected)

    return protected, total_count


def fix_header_line(line, replacements, mega_regex, replaced_in_file):
    match = re.match(r'^(#{1,4}\s+)(.+)$', line)
    if not match:
        return line
    prefix = match.group(1)
    text = match.group(2)
    for match_word in mega_regex.finditer(text):
        word = match_word.group()
        wl = word.lower()
        start, end = match_word.start(), match_word.end()
        if start > 0 and text[start-1].isalpha():
            continue
        if end < len(text) and text[end].isalpha():
            continue
        for w, data in replacements.items():
            if w.lower() == wl:
                upper_form = data.get("upper", word.upper())
                replaced_in_file[data["short"]] = True
                text = text[:start] + upper_form + text[end:]
                break
    return prefix + text


def fix_body_line(line, replacements, mega_regex, replaced_in_file):
    result = []
    pos = 0
    for match in mega_regex.finditer(line):
        word = match.group()
        start, end = match.start(), match.end()
        
        if start > 0 and line[start-1].isalpha():
            continue
        if end < len(line) and line[end].isalpha():
            continue
        
        for w, data in replacements.items():
            if w.lower() == word.lower():
                key = data["short"]
                if key not in replaced_in_file:
                    replacement = data["first"]
                    replaced_in_file[key] = True
                else:
                    replacement = data["short"]
                if word[0].isupper():
                    replacement = replacement[0].upper() + replacement[1:]
                
                result.append(line[pos:start])
                result.append(replacement)
                pos = end
                break
    
    if pos == 0:
        return line
    
    result.append(line[pos:])
    return "".join(result)


def check_one_file(md_file, replacements, fast_filter, mega_regex, scan_cache, check_only):
    rel_path = str(md_file.relative_to(REPO_ROOT))
    mtime = md_file.stat().st_mtime
    if check_only and rel_path in scan_cache:
        cached = scan_cache[rel_path]
        if cached.get("mtime") == mtime and cached.get("clean"):
            return None, None, True

    content = read_file_safe(md_file)
    if content is None:
        return None, None, True
    if not any(prefix in content.lower() for prefix in fast_filter):
        return rel_path, {"mtime": mtime, "clean": True}, True

    found = {}
    body, _ = protect_metadata(content)
    for line in body.split("\n"):
        if is_header_line(line) or re.search(r'[α-ωΑ-Ω]', line) or re.match(r'^[-*]\s*\*\*[^*]+\*\*:', line):
            continue
        for match in mega_regex.finditer(line):
            word = match.group()
            start, end = match.start(), match.end()
            if start > 0 and line[start-1].isalpha():
                continue
            if end < len(line) and line[end].isalpha():
                continue
            if word.lower() in (w.lower() for w in replacements):
                found[word] = found.get(word, 0) + 1

    if found:
        result = {"mtime": mtime, "clean": False}
        if not check_only:
            fixed, reps = fix_religionisms(content, replacements, mega_regex)
            if reps > 0:
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(fixed)
                result = {"mtime": os.path.getmtime(md_file), "clean": False}
        return rel_path, result, found
    return rel_path, {"mtime": mtime, "clean": True}, True


def scan_files(replacements, fast_filter, mega_regex, check_only=True):
    total_found = Counter()
    files_with_issues = []
    scan_cache = load_scan_cache()
    dirty_set = load_dirty_cache()

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    if total == 0:
        return {}, [], 0

    completed = 0
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
    return dict(total_found), files_with_issues, 0


def check_single_file(file_path, replacements, fast_filter, mega_regex):
    """Проверить один файл с детальным отчётом."""
    md_file = REPO_ROOT / file_path
    if not md_file.exists():
        print(f"❌ Файл не найден: {file_path}")
        return

    content = read_file_safe(md_file)
    if content is None:
        print(f"❌ Не удалось прочитать: {file_path}")
        return

    found = {}
    body, _ = protect_metadata(content)

    for line_num, line in enumerate(body.split("\n"), 1):
        if is_header_line(line) or re.search(r'[α-ωΑ-Ω]', line) or re.match(r'^[-*]\s*\*\*[^*]+\*\*:', line):
            continue
        for match in mega_regex.finditer(line):
            word = match.group()
            start, end = match.start(), match.end()
            if start > 0 and line[start-1].isalpha():
                continue
            if end < len(line) and line[end].isalpha():
                continue
            if word.lower() in (w.lower() for w in replacements):
                if word not in found:
                    found[word] = []
                for w, data in replacements.items():
                    if w.lower() == word.lower():
                        found[word].append({
                            "line": line_num,
                            "context": line.strip()[:80],
                            "category": data.get("note", "неизвестно"),
                            "replacement": data.get("first", data.get("short", "")),
                        })
                        break

    if not found:
        print(f"✅ {file_path}: таhор — нарушений не найдено")
        return

    total = sum(len(v) for v in found.values())
    print(f"\n📄 Файл: {file_path}")
    print(f"❌ Нарушений: {total}\n")

    for word, occurrences in sorted(found.items(), key=lambda x: -len(x[1])):
        print(f"  «{word}» — {len(occurrences)} раз(а)")
        for occ in occurrences[:3]:
            print(f"    строка {occ['line']:4d}: ...{occ['context']}...")
            print(f"    → {occ['replacement']} ({occ['category']})")
        if len(occurrences) > 3:
            print(f"    ... и ещё {len(occurrences) - 3}")
        print()


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


# Замени функцию main() в check-tahor.py

def main():
    # Проверка одного файла
    file_path = None
    fix_mode = False
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg.startswith("--file="):
            file_path = arg.split("=", 1)[1]
        elif arg == "--file":
            if i < len(sys.argv[1:]):
                file_path = sys.argv[i + 1]
        elif arg == "--fix":
            fix_mode = True
    
    # Если указан файл — проверить или исправить один файл
    if file_path:
        replacements, fast_filter, mega_regex = build_replacement_map()
        if not replacements:
            print_error("❌ Словарь замен пуст. Запустите с --rebuild")
            return 1
        
        if fix_mode:
            # Исправить файл
            md_file = REPO_ROOT / file_path
            if not md_file.exists():
                print(f"❌ Файл не найден: {file_path}")
                return 1
            content = read_file_safe(md_file)
            if content is None:
                print(f"❌ Не удалось прочитать: {file_path}")
                return 1
            fixed, count = fix_religionisms(content, replacements, mega_regex)
            if count > 0:
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(fixed)
                print(f"✅ {file_path}: исправлено {count} нарушений")
            else:
                print(f"✅ {file_path}: нарушений не найдено, файл не изменён")
        else:
            # Только проверить
            check_single_file(file_path, replacements, fast_filter, mega_regex)
        return 0
    
    # Полная проверка
    check_only = not fix_mode
    rebuild_cache = "--rebuild" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    save_mode = "--save" in sys.argv

    if rebuild_cache:
        for f in (CACHE_FILE, SCAN_CACHE_FILE, DIRTY_CACHE_FILE):
            if f.exists():
                f.unlink()
        print("🗑️ Кэш удалён.")

    print_header("ПРОВЕРКА ЧИСТОТЫ ЯЗЫКА — טָהֳרָה", "🔍")
    replacements, fast_filter, mega_regex = build_replacement_map(rebuild=rebuild_cache)

    if not replacements:
        print_error("❌ Словарь замен пуст. Запустите с --rebuild")
        return 1

    total_found, files_with_issues, _ = scan_files(replacements, fast_filter, mega_regex, check_only)

    if not files_with_issues:
        print_success("🎉 Нарушений не найдено")
        return 0

    print(f"\n📁 Файлов с нарушениями: {len(files_with_issues)}")
    print(f"📝 Всего найдено слов: {sum(total_found.values())}\n")

    print("🔝 Самые частые:")
    for word, cnt in sorted(total_found.items(), key=lambda x: x[1], reverse=True)[:10]:
        bar = "█" * min(cnt, 50)
        print(f"  {word:15} {cnt:4}  {bar}")

    print(f"\n📋 Файлы:")
    for file_path, found in (files_with_issues if verbose else files_with_issues[:15]):
        total = sum(found.values())
        top_word = max(found, key=found.get)
        print(f"  • {file_path} — {total} шт. (чаще: «{top_word}»)")

    if len(files_with_issues) > 15 and not verbose:
        print(f"  ... и ещё {len(files_with_issues) - 15} файлов")

    if check_only:
        print_hint("\nДля исправления: python tools/checkers/check-tahor.py --fix")
        print_hint("Проверить один файл:  python tools/checkers/check-tahor.py --file путь")
        print_hint("Исправить один файл: python tools/checkers/check-tahor.py --file путь --fix")
    else:
        print_success(f"\n✅ Исправлено файлов: {len(files_with_issues)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())