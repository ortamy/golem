#!/usr/bin/env python3
# tools/checkers/check-religionisms.py — поиск и исправление религионимов (v4.1)
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
import argparse
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_error, print_warning, print_hint,
    ask_yes_no, REPO_ROOT
)

TAHOR_DIR = REPO_ROOT / "instructions" / "dictionaries"
FORBIDDEN_FILE = REPO_ROOT / "instructions" / "FORBIDDEN-WORDS.md"
CACHE_DIR = REPO_ROOT / "tools" / "cache"
CACHE_FILE = CACHE_DIR / "cache-religionisms.json"
SCAN_CACHE_FILE = CACHE_DIR / "cache-scan.json"
DIRTY_CACHE_FILE = CACHE_DIR / "cache-religionism-dirty.json"

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

FOREIGN_CHARS = re.compile(r'[α-ωΑ-Ωa-zA-Z]{3,}')

METADATA_FIELD = re.compile(r'^[-*]\s*\*\*[^*]+\*\*:')

HEBREW_WORDS_IN_LINE = re.compile(r'[\u0590-\u05FF]{2,}')


def load_hebrew_whitelist():
    words = {
        "тора", "танах", "машиах", "шаббат", "йешуа", "яхве", "yhwh",
        "элоhим", "эль", "руах", "нэфеш", "нефеш", "шеол", "сатан",
        "шалом", "брит", "кодеш", "мишпат", "цдака", "тшува", "эмуна",
        "эмет", "хесед", "кавод", "коhэн", "нави", "малъах", "микве",
        "мишкан", "корбан", "тефила", "тфила", "твила", "йовель", "шмита",
        "талмуд", "мишна", "гемара", "мидраш", "зоhар", "сефер",
        "синай", "цион", "йерушалаим", "израиль", "исраэль",
    }
    term_dir = REPO_ROOT / "content" / "terminology"
    if term_dir.exists():
        for f in term_dir.glob("*.md"):
            words.add(f.stem.lower())
    return words


HEBREW_WHITELIST = load_hebrew_whitelist()


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
            return expanded, fast_filter, mega_regex
        except Exception as e:
            print_warning(f"Ошибка загрузки JSON: {e}. Перестройте: --rebuild")
            return {}, [], None
    
    return {}, [], None


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
            f'- **Проверок на религионизмы:** {count}',
            content
        )
    
    content = re.sub(
        r'[-*]\s*\*\*Последняя проверка:\*\*\s*[^\n]+',
        f'- **Последняя проверка:** {today}',
        content
    )
    
    body_start = content.find('---\n', content.find('**Метаданные файла**'))
    if body_start != -1:
        body = content[body_start + 4:]
        new_hash = hashlib.md5(body.encode('utf-8')).hexdigest()[:8]
        if re.search(r'[-*]\s*\*\*Хеш:\*\*\s*\S+', content):
            content = re.sub(
                r'[-*]\s*\*\*Хеш:\*\*\s*\S+',
                f'- **Хеш:** {new_hash}',
                content
            )
    
    return content


def is_header_line(line):
    return bool(re.match(r'^#{1,4}\s', line))


def should_skip_line(line):
    """Пропустить строки которые нельзя заменять."""
    # Иностранный текст (греческий, латынь)
    if FOREIGN_CHARS.search(line):
        return True
    # Поля метаданных в теле текста
    if METADATA_FIELD.match(line):
        return True
    # Строки содержащие только иврит (цитаты)
    stripped = line.strip()
    if stripped and all(c in ' ־ְֲִֵֶָֹֻּׁׂ\u0590-\u05FF' for c in stripped):
        return True
    return False


def fix_religionisms(text, replacements, mega_regex):
    """Исправляет религионимы с учётом контекста."""
    protected, metadata = protect_metadata(text)
    
    # Защищаем цитаты (включая греческий текст в кавычках)
    quoted_map = {}
    quote_pattern = re.compile(r'«[^»]*»|"[^"]*"|\'[^\']*\'')
    for i, m in enumerate(quote_pattern.finditer(protected)):
        placeholder = f"__Q{i}__"
        quoted_map[placeholder] = m.group()
        protected = protected.replace(m.group(), placeholder, 1)
    
    # Защищаем строки с кодом (внутри `)
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
        elif should_skip_line(line):
            new_lines.append(line)
        else:
            new_lines.append(fix_body_line(line, replacements, mega_regex, replaced_in_file))
    
    protected = "\n".join(new_lines)
    
    # Восстанавливаем код
    for placeholder, original in code_map.items():
        protected = protected.replace(placeholder, original, 1)
    
    # Восстанавливаем цитаты
    for placeholder, original in quoted_map.items():
        protected = protected.replace(placeholder, original, 1)
    
    if metadata:
        protected = restore_metadata(protected, metadata)
    
    # Считаем замены
    total_count = sum(1 for v in replaced_in_file.values())
    
    if total_count > 0:
        protected = update_metadata_fields(protected)
    
    return protected, total_count


def fix_header_line(line, replacements, mega_regex, replaced_in_file):
    """Заменяет в заголовке — всегда полная форма КАПСОМ."""
    match = re.match(r'^(#{1,4}\s+)(.+)$', line)
    if not match:
        return line
    
    prefix = match.group(1)
    text = match.group(2)
    
    # Защищаем ивритские слова в заголовке
    hebrew_parts = []
    for m in HEBREW_WORDS_IN_LINE.finditer(text):
        hebrew_parts.append((m.start(), m.end(), m.group()))
    
    for match_word in mega_regex.finditer(text):
        word = match_word.group()
        wl = word.lower()
        
        # Проверяем что слово не внутри ивритского блока
        start = match_word.start()
        end = match_word.end()
        in_hebrew = any(start >= hs and end <= he for hs, he, _ in hebrew_parts)
        if in_hebrew:
            continue
        
        # Не часть другого слова
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
    """Заменяет в теле текста — первое упоминание полное, остальные краткое."""
    # Защищаем ивритские слова
    hebrew_parts = []
    for m in HEBREW_WORDS_IN_LINE.finditer(line):
        hebrew_parts.append((m.start(), m.end(), m.group()))
    
    for match_word in mega_regex.finditer(line):
        word = match_word.group()
        wl = word.lower()
        
        start = match_word.start()
        end = match_word.end()
        
        # Не часть ивритского слова
        in_hebrew = any(start >= hs and end <= he for hs, he, _ in hebrew_parts)
        if in_hebrew:
            continue
        
        # Не часть другого слова
        if start > 0 and line[start-1].isalpha():
            continue
        if end < len(line) and line[end].isalpha():
            continue
        
        for w, data in replacements.items():
            if w.lower() == wl:
                key = data["short"]
                
                if key not in replaced_in_file:
                    replacement = data["first"]
                    replaced_in_file[key] = True
                else:
                    replacement = data["short"]
                
                if word[0].isupper():
                    replacement = replacement[0].upper() + replacement[1:]
                
                line = line[:start] + replacement + line[end:]
                break
    
    return line


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
    
    # Проверяем тело (не заголовки, не метаданные, не цитаты)
    for line in body.split("\n"):
        if is_header_line(line) or should_skip_line(line):
            continue
        for match in mega_regex.finditer(line):
            word = match.group()
            start = match.start()
            end = match.end()
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
    
    if dirty_set and check_only:
        dirty_files, clean_files = [], []
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


def main():
    check_only = "--fix" not in sys.argv
    rebuild_cache = "--rebuild" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    save_mode = "--save" in sys.argv

    if rebuild_cache:
        for f in (CACHE_FILE, SCAN_CACHE_FILE, DIRTY_CACHE_FILE):
            if f.exists():
                f.unlink()
        print("🗑️ Кэш удалён.")

    print_header("ЗАГРУЗКА СЛОВАРЯ ЗАМЕН", "📖")
    replacements, fast_filter, mega_regex = build_replacement_map(rebuild=rebuild_cache)
    
    if not replacements:
        print_error("❌ Словарь замен пуст. Запустите с --rebuild или создайте cache-religionisms.json")
        return 1
    
    print(f"✅ Загружено терминов: {len(set(d['short'] for d in replacements.values()))}")
    print(f"📝 Всего форм (со склонениями): {len(replacements)}")
    print(f"🛡️ Защищены: цитаты, код, метаданные, иврит, греческий, латынь")
    print(f"🔄 Первое упоминание: полная форма, последующие: краткая")
    print(f"📋 Заголовки: КАПС с ивритом")

    label = "ПРОВЕРКА НА РЕЛИГИОНИЗМЫ" if check_only else "ИСПРАВЛЕНИЕ РЕЛИГИОНИЗМОВ"
    print_header(label, "🔍" if check_only else "🔧")

    total_found, files_with_issues, _ = scan_files(replacements, fast_filter, mega_regex, check_only)

    if not files_with_issues:
        print_success("🎉 Религионизмов не найдено")
        return 0

    print(f"\n📁 Файлов с религионимами: {len(files_with_issues)}")
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
        print_hint("\nДля исправления: python tools/checkers/check-religionisms.py --fix")
        print_hint("Перестроить кэш:  python tools/checkers/check-religionisms.py --rebuild")
    else:
        print_success(f"\n✅ Исправлено файлов: {len(files_with_issues)}")
        print_hint("Первое упоминание: полная форма с ивритом")
        print_hint("Заголовки: КАПС с ивритом")
        print_hint("Счётчик проверок и хеш обновлены в метаданных")

    if save_mode:
        report = REPO_ROOT / "reports" / f"religionisms-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        lines = [
            "# 📖 ОТЧЁТ О РЕЛИГИОНИЗМАХ",
            f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Файлов с религионимами:** {len(files_with_issues)}",
            f"**Всего найдено слов:** {sum(total_found.values())}",
            "",
            "## 🔝 Самые частые",
        ]
        for word, cnt in sorted(total_found.items(), key=lambda x: x[1], reverse=True)[:20]:
            lines.append(f"- **{word}**: {cnt}")
        lines.append("\n## 📋 Файлы")
        for file_path, found in files_with_issues:
            lines.append(f"- `{file_path}` — {sum(found.values())} шт.")
        report.parent.mkdir(exist_ok=True)
        report.write_text("\n".join(lines) + "\n", encoding='utf-8')
        print_success(f"Отчёт сохранён: {report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())