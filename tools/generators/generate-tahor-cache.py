#!/usr/bin/env python3
# tools/generators/generate-tahor-cache.py — generate tahor cache
"""
tools/generators/generate-tahor-cache.py — генератор cache-tahor.json из словарей.

Читает все .md файлы из instructions/dictionaries/,
извлекает пары "слово → замена" и генерирует
tools/cache/cache-tahor.json в формате, который понимает check-tahor.py.
"""

import sys
import re
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
DICTIONARIES_DIR = REPO_ROOT / "instructions" / "dictionaries"
CACHE_DIR = REPO_ROOT / "tools" / "cache"
CACHE_FILE = CACHE_DIR / "cache-tahor.json"

# Common entry patterns: bold (**) or backtick (`) delimited, then → HEBREW (translit)
# Group 1: term text
# Group 2: hebrew word(s)
# Group 3: transliteration (optional, inside parens after hebrew)
ENTRY_RE = re.compile(
    r'^\s*-\s+(?:\*\*(.+?)\*\*|`(.+?)`)\s*(?:\([^)]*\)\s*)?[—–-]?\s*.+?→\s+([\u0590-\u05FF][\u0590-\u05FF\s]*[\u0590-\u05FF])\s*(?:\(([^)]*)\))?',
    re.UNICODE
)

# Phrase pattern (quoted term): "- **«Phrase»** → ... " or "- `«Phrase»` → ..."
PHRASE_RE = re.compile(
    r'^\s*-\s+(?:\*\*["\u00AB](.+?)["\u00BB]\*\*|`["\u00AB](.+?)["\u00BB]`)\s*[—–-]?\s*.+?→\s+([\u0590-\u05FF][\u0590-\u05FF\s]*[\u0590-\u05FF])\s*(?:\(([^)]*)\))?',
    re.UNICODE
)


def guess_case_type(word: str) -> str:
    """Угадывает тип склонения по окончанию слова."""
    word = word.strip().lower()
    if " " in word or "-" in word:
        return "indeclinable"
    if not word:
        return "male"
    last = word[-1]
    if last == "а":
        return "female_a"
    if last == "я":
        return "female_soft"
    if last == "ь":
        return "female_soft"
    if last in "ое":
        return "neuter"
    if last in "ий":
        # прилагательные — не склоняем по этой схеме
        return "indeclinable"
    # согласная → мужской род
    return "male"


def clean_hebrew_word(hw: str) -> str:
    """Очищает ивритское слово от лишних символов."""
    # Убираем знаки кантилляции и огласовки, оставляем только буквы
    cleaned = re.sub(r'[\u0591-\u05BD\u05BF\u05C1-\u05C2\u05C4-\u05C5\u05C7]', '', hw)
    return cleaned.strip()


def extract_transliteration(raw: str) -> str:
    """Извлекает транслитерацию — первый набор кириллических букв."""
    if not raw:
        return ""
    # Транслитерация — первая группа кириллицы
    m = re.search(r'[а-яА-ЯёЁ][а-яА-ЯёЁ\s]*', raw)
    if m:
        return m.group().strip()
    return ""


def parse_entry_term(term_raw: str) -> str:
    """Очищает термин: убирает кавычки, лишние пробелы."""
    term = term_raw.strip()
    term = term.strip('"«»''"')
    term = term.strip()
    return term


def parse_entry(line: str) -> dict | None:
    """Парсит одну строку словаря, возвращает {word, hebrew, translit} или None."""
    # Сначала пробуем фразовый шаблон (с кавычками)
    m = PHRASE_RE.match(line)
    if m:
        # Термин может быть в группе 1 (**«...»**) или группе 2 (`«...»`)
        term = parse_entry_term(m.group(1) or m.group(2) or "")
        # Иврит — в группе 3, транслитерация — в группе 4
        hebrew = clean_hebrew_word(m.group(3))
        translit_raw = m.group(4) if m.lastindex >= 4 else ""
        translit = extract_transliteration(translit_raw) or ""
        if term and hebrew:
            return {"word": term, "hebrew": hebrew, "translit": translit}

    # Пробуем обычный шаблон
    m = ENTRY_RE.match(line)
    if m:
        # Термин может быть в группе 1 (**...**) или группе 2 (`...`)
        term = parse_entry_term(m.group(1) or m.group(2) or "")
        # Иврит — в группе 3, транслитерация — в группе 4
        hebrew = clean_hebrew_word(m.group(3))
        translit_raw = m.group(4) if m.lastindex >= 4 else ""
        translit = extract_transliteration(translit_raw) or ""
        if term and hebrew:
            return {"word": term, "hebrew": hebrew, "translit": translit}

    return None


def should_skip_line(line: str) -> bool:
    """Пропускает строки, которые не являются записями словаря."""
    stripped = line.strip()
    if not stripped:
        return True
    # Метаданные
    if stripped.startswith("**Метаданные") or stripped == "---" or stripped.startswith("**Язык"):
        return True
    # Заголовки
    if stripped.startswith("#"):
        return True
    # Строки без ->
    if "→" not in stripped:
        return True
    return False


def generate_upper(word: str) -> str:
    """Генерирует КАПС форму."""
    return word.upper()


def generate_first(word: str, hebrew: str, translit: str) -> str:
    """Генерирует полную форму с ивритом."""
    if translit:
        return f"{hebrew} ({translit})"
    return hebrew


def generate_short(word: str, hebrew: str, translit: str) -> str:
    """Генерирует краткую форму — транслитерацию или первую часть."""
    if translit:
        return translit
    return hebrew


def process_dictionaries() -> dict:
    """Читает все .md файлы словарей и возвращает replacements dict."""
    replacements = {}

    md_files = sorted(DICTIONARIES_DIR.glob("*.md"))
    if not md_files:
        print(f"❌ Не найдено .md файлов в {DICTIONARIES_DIR}")
        return replacements

    for md_path in md_files:
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️  Ошибка чтения {md_path.name}: {e}")
            continue

        lines = content.split("\n")
        file_count = 0

        for line in lines:
            if should_skip_line(line):
                continue

            parsed = parse_entry(line)
            if parsed is None:
                continue

            word = parsed["word"]
            hebrew = parsed["hebrew"]
            translit = parsed["translit"]

            if not word or not hebrew:
                continue

            # Пропускаем дубликаты (первый встреченный — приоритет)
            word_lower = word.lower()
            if word_lower in replacements:
                continue

            case_type = guess_case_type(word)
            short = generate_short(word, hebrew, translit)
            first = generate_first(word, hebrew, translit)
            upper = generate_upper(word)

            replacements[word_lower] = {
                "short": short,
                "first": first,
                "upper": upper,
                "cases": case_type
            }

            file_count += 1

        print(f"  📄 {md_path.name}: {file_count} записей")

    return replacements


def main():
    print("🔧 Генератор cache-tahor.json")
    print(f"📂 Словари: {DICTIONARIES_DIR}")
    print()

    if not DICTIONARIES_DIR.exists():
        print(f"❌ Директория не найдена: {DICTIONARIES_DIR}")
        sys.exit(1)

    replacements = process_dictionaries()

    if not replacements:
        print("❌ Не извлечено ни одной записи.")
        sys.exit(1)

    # Создаём структуру, ожидаемую check-tahor.py
    cache_data = {
        "replacements": replacements,
        "meta": {
            "generated_by": "generate-tahor-cache.py",
            "total_entries": len(replacements),
            "sources": [str(f.name) for f in sorted(DICTIONARIES_DIR.glob("*.md"))]
        }
    }

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Сгенерировано {len(replacements)} записей")
    print(f"💾 Сохранено: {CACHE_FILE}")

    # Статистика по типам склонений
    case_stats = {}
    for v in replacements.values():
        ct = v["cases"]
        case_stats[ct] = case_stats.get(ct, 0) + 1
    print(f"\n📊 Типы склонений:")
    for ct, cnt in sorted(case_stats.items()):
        print(f"    {ct}: {cnt}")

    return 0


if __name__ == "__main__":
    sys.exit(main())