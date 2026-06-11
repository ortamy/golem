#!/usr/bin/env python3
# tools/checkers/check-tanakh-references.py — проверка ссылок на ТаНаХ + автофикс
import sys
import re
import json
import sqlite3
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
import argparse
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_error, print_warning, print_hint,
    REPO_ROOT
)

TANAKH_DB = REPO_ROOT / "tools" / "cache" / "tanakh.db"
TANAKH_JSON = REPO_ROOT / "tools" / "cache" / "tanakh.json"
INDEX_URL = "https://raw.githubusercontent.com/Sefaria/Sefaria-Export/master/books.json"

BOOK_NAMES = {
    "Genesis": "Берешит", "Exodus": "Шмот", "Leviticus": "Ваикра",
    "Numbers": "Бемидбар", "Deuteronomy": "Дварим",
    "Joshua": "Йеhошуа", "Judges": "Шофтим",
    "I Samuel": "Шмуэль I", "II Samuel": "Шмуэль II",
    "I Kings": "Мелахим I", "II Kings": "Мелахим II",
    "Isaiah": "Йешаяhу", "Jeremiah": "Йирмеяhу", "Ezekiel": "Йехезкэль",
    "Hosea": "Ошеа", "Joel": "Йоэль", "Amos": "Амос",
    "Obadiah": "Овадья", "Jonah": "Йона", "Micah": "Миха",
    "Nahum": "Нахум", "Habakkuk": "Хавакук", "Zephaniah": "Цефанья",
    "Haggai": "Хагай", "Zechariah": "Зехарья", "Malachi": "Малахи",
    "Psalms": "Теhилим", "Job": "Йов", "Proverbs": "Мишлей",
    "Ruth": "Рут", "Song of Songs": "Шир hа-Ширим",
    "Ecclesiastes": "Коhелет", "Lamentations": "Эйха",
    "Esther": "Эстер", "Daniel": "Даниэль",
    "Ezra": "Эзра", "Nehemiah": "Нехемья",
    "I Chronicles": "Диврей hа-Йамим I", "II Chronicles": "Диврей hа-Йамим II",
}

BOOK_ALIASES = {
    "берешит": "Берешит", "бытие": "Берешит",
    "шмот": "Шмот", "исход": "Шмот",
    "ваикра": "Ваикра", "левит": "Ваикра",
    "бемидбар": "Бемидбар", "числа": "Бемидбар",
    "дварим": "Дварим", "второзаконие": "Дварим",
    "йеhошуа": "Йеhошуа", "иисус навин": "Йеhошуа",
    "шофтим": "Шофтим", "судей": "Шофтим",
    "теhилим": "Теhилим", "псалмы": "Теhилим", "псалтирь": "Теhилим",
    "мишлей": "Мишлей", "притчи": "Мишлей",
    "коhелет": "Коhелет", "екклесиаст": "Коhелет",
    "йешаяhу": "Йешаяhу", "исаия": "Йешаяhу",
    "йирмеяhу": "Йирмеяhу", "иеремия": "Йирмеяhу",
    "йехезкэль": "Йехезкэль", "иезекииль": "Йехезкэль",
    "ошеа": "Ошеа", "осия": "Ошеа",
    "эстер": "Эстер", "эсфирь": "Эстер",
    "даниэль": "Даниэль", "даниил": "Даниэль",
    "йов": "Йов", "иов": "Йов",
    "рут": "Рут", "руфь": "Рут",
    "эйха": "Эйха", "плач иеремии": "Эйха",
    "эзра": "Эзра", "ездра": "Эзра",
    "нехемья": "Нехемья", "неемия": "Нехемья",
    "шмуэль": "Шмуэль I", "самуил": "Шмуэль I",
    "мелахим": "Мелахим I", "царств": "Мелахим I",
    "диврей hа-йамим": "Диврей hа-Йамим I",
}


def init_db():
    TANAKH_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(TANAKH_DB))
    conn.execute('''CREATE TABLE IF NOT EXISTS verses (
        id INTEGER PRIMARY KEY, book TEXT, chapter INTEGER, verse INTEGER,
        hebrew TEXT, translation TEXT)''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_ref ON verses(book, chapter, verse)')
    conn.commit()
    return conn


def download_tanakh():
    print("📥 Загрузка индекса книг из Sefaria...")
    try:
        with urllib.request.urlopen(INDEX_URL) as f:
            data = json.loads(f.read())
    except Exception as e:
        print_error(f"Ошибка загрузки: {e}")
        return False

    books_index = data.get("books", [])
    if not books_index:
        print_error("Книги не найдены")
        return False

    # Фильтруем: ТаНаХ + иврит + без комментариев
    tanakh_books = []
    for b in books_index:
        if not isinstance(b, dict):
            continue
        cats = b.get("categories", [])
        lang = b.get("language", "")
        title = b.get("title", "")
        url = b.get("json_url", "")
        if not url:
            continue
        if any("Tanakh" in c for c in cats) and lang == "Hebrew" and " on " not in title:
            tanakh_books.append(b)

    print(f"📚 Книг ТаНаХа (иврит): {len(tanakh_books)}")

    all_verses = []
    for i, book in enumerate(tanakh_books, 1):
        title = book.get("title", "?")
        raw_url = book.get("json_url", "")
        url = urllib.parse.quote(raw_url, safe=':/')

        print(f"  [{i}/{len(tanakh_books)}] {title[:60]}...", end=" ", flush=True)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Golem-Project/1.0'})
            with urllib.request.urlopen(req, timeout=30) as f:
                book_data = json.loads(f.read())
            texts = book_data.get("text", {})
            if isinstance(texts, list):
                for vn, vt in enumerate(texts, 1):
                    if isinstance(vt, str) and vt.strip():
                        all_verses.append({"book": title, "chapter": 1, "verse": vn, "hebrew": vt})
            elif isinstance(texts, dict):
                for cn, cd in texts.items():
                    if isinstance(cd, list):
                        for vn, vt in enumerate(cd, 1):
                            if isinstance(vt, str) and vt.strip():
                                all_verses.append({"book": title, "chapter": int(cn), "verse": vn, "hebrew": vt})
            print("✅")
        except Exception:
            print("⏭️")

    print_success(f"Загружено стихов: {len(all_verses)}")
    TANAKH_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(TANAKH_JSON, 'w', encoding='utf-8') as f:
        json.dump({"source": "Sefaria-Export", "date": datetime.now().isoformat(),
                    "total_verses": len(all_verses), "verses": all_verses}, f, ensure_ascii=False)
    return len(all_verses) > 0


def load_tanakh_to_db():
    if not TANAKH_JSON.exists() or TANAKH_JSON.stat().st_size < 1000:
        print("📥 Загрузка ТаНаХа...")
        if not download_tanakh():
            return None

    conn = init_db()
    cur = conn.execute('SELECT COUNT(*) FROM verses')
    if cur.fetchone()[0] > 100:
        return conn

    print("📊 Загрузка в базу...")
    with open(TANAKH_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    count = 0
    for v in data.get("verses", []):
        conn.execute('INSERT INTO verses (book, chapter, verse, hebrew, translation) VALUES (?,?,?,?,?)',
                     (BOOK_NAMES.get(v["book"], v["book"]), v["chapter"], v["verse"], v.get("hebrew", ""), ""))
        count += 1
    conn.commit()
    print_success(f"Загружено: {count}")
    return conn


def normalize_book(name: str) -> str:
    n = name.lower().strip().rstrip('.,')
    if n in BOOK_NAMES: return BOOK_NAMES[n]
    if n in BOOK_ALIASES: return BOOK_ALIASES[n]
    for alias, std in {**BOOK_NAMES, **BOOK_ALIASES}.items():
        if alias.lower().startswith(n) or n.startswith(alias.lower()):
            return std
    return name


def find_verse(conn, book: str, ch: int, vs: int):
    cur = conn.cursor()
    bn = normalize_book(book)
    cur.execute('SELECT * FROM verses WHERE book=? AND chapter=? AND verse=?', (bn, ch, vs))
    r = cur.fetchone()
    if not r:
        cur.execute('SELECT * FROM verses WHERE book LIKE ? AND chapter=? AND verse=?', (f'%{book}%', ch, vs))
        r = cur.fetchone()
    return r


def extract_refs(content: str) -> list:
    refs = []
    patterns = [
        r'([\u0590-\u05FF]+)\s+(\d+):(\d+)',
        r'([А-ЯЁ][а-яё]+(?:\s+(?:I|II|[а-яё]+))?)\s+(\d+)[,:.]\s*(\d+)',
        r'([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s+(\d+):(\d+)',
        r'\(([^)]+?)\s+(\d+)[,:.]\s*(\d+)\)',
    ]
    for p in patterns:
        for m in re.finditer(p, content):
            b, ch, vs = m.group(1).strip(), int(m.group(2)), int(m.group(3))
            if 0 < ch < 200 and 0 < vs < 200:
                refs.append((b, ch, vs, m.group()))
    return list(set(refs))


def check_file(fp: Path, conn) -> dict | None:
    rp = str(fp.relative_to(REPO_ROOT)).replace('\\', '/')
    content = read_file_safe(fp)
    if not content: return None
    refs = extract_refs(content)
    if not refs: return None
    missing = []
    for b, ch, vs, raw in refs:
        if not find_verse(conn, b, ch, vs):
            missing.append({"ref": f"{b} {ch}:{vs}", "raw": raw})
    return {"path": rp, "missing": missing} if missing else None


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    init_mode = "--init" in sys.argv
    rebuild = "--rebuild" in sys.argv

    if init_mode or rebuild:
        print_header("ИНИЦИАЛИЗАЦИЯ БАЗЫ ТАНАХА", "📚")
        if rebuild:
            for f in (TANAKH_JSON, TANAKH_DB):
                if f.exists(): f.unlink()
        conn = load_tanakh_to_db()
        if conn:
            cur = conn.execute('SELECT COUNT(*) FROM verses')
            print_success(f"Готово. Стихов: {cur.fetchone()[0]}")
        return 0

    print_header("ПРОВЕРКА ССЫЛОК НА ТАНАХ", "📖")
    conn = load_tanakh_to_db()
    if not conn:
        print_error("База не загружена")
        print_hint("python tools/checkers/check-tanakh-references.py --init")
        return 1

    cur = conn.execute('SELECT COUNT(*) FROM verses')
    total_verses = cur.fetchone()[0]

    all_files = []
    for sd in ["researches", "terminology"]:
        dp = REPO_ROOT / sd
        if dp.exists(): all_files.extend(sorted(dp.rglob("*.md")))

    total = len(all_files)
    print(f"📚 Стихов: {total_verses} | 🔍 Файлов: {total}")

    results = []
    by_book = defaultdict(int)

    for i, fp in enumerate(all_files, 1):
        r = check_file(fp, conn)
        if r:
            results.append(r)
            for m in r["missing"]:
                by_book[m["ref"].split()[0]] += 1
        progress_bar(i, total, extra=f"проблем: {len(results)}")

    finish_progress()

    if not results:
        print_success("🎉 Все ссылки корректны")
        return 0

    tm = sum(len(r["missing"]) for r in results)
    print_warning(f"\n📖 Файлов с ошибками: {len(results)} | 📝 Ненайденных ссылок: {tm}")

    if by_book:
        print("\n📊 Топ ошибок по книгам:")
        for b, c in sorted(by_book.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {b}: {c}")

    limit = None if verbose else 15
    print(f"\n📋 Файлы:")
    for r in results[:limit]:
        print(f"  📄 {r['path']}: {len(r['missing'])}")
        if verbose:
            for m in r["missing"][:3]:
                print(f"     ❌ {m['raw']}")
    if limit and len(results) > limit:
        print(f"  ... и ещё {len(results) - limit}")

    print_hint("\n--verbose для подробностей")
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main())