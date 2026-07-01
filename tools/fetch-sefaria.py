#!/usr/bin/env python3
"""
tools/fetch-sefaria.py — Получение текста ТаНаХа через Sefaria API.

Использование:
  py tools/fetch-sefaria.py Genesis 1
  py tools/fetch-sefaria.py Genesis 1:1
  py tools/fetch-sefaria.py bereshit 1-5
"""

import json
import os
import re
import sys
import argparse
import ssl
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "data" / "tanakh-cache"
SEFARIA_BASE_URL = "https://www.sefaria.org/api/v3/texts/"

BOOK_MAP = {
    "bereshit": "Genesis", "shmot": "Exodus", "vayikra": "Leviticus", "bemidbar": "Numbers", "dvarim": "Deuteronomy",
    "yehoshua": "Joshua", "shoftim": "Judges", "shmuel-alef": "1 Samuel", "shmuel-bet": "2 Samuel",
    "melachim-alef": "1 Kings", "melachim-bet": "2 Kings", "yeshayahu": "Isaiah", "yirmeyahu": "Jeremiah",
    "yehezkel": "Ezekiel", "hoshea": "Hosea", "yoel": "Joel", "amos": "Amos", "ovadyah": "Obadiah",
    "yonah": "Jonah", "mikhah": "Micah", "nachum": "Nahum", "chavakuk": "Habakkuk", "tsefanyah": "Zephaniah",
    "chaggai": "Haggai", "zechariah": "Zechariah", "malakhi": "Malachi", "tehillim": "Psalms",
    "mishlei": "Proverbs", "iyov": "Job", "shir-hashirim": "Song of Songs", "rut": "Ruth",
    "eikhah": "Lamentations", "kohelet": "Ecclesiastes", "ester": "Esther", "daniel": "Daniel",
    "ezra": "Ezra", "nechemyah": "Nehemiah", "divrei-hayamim-alef": "1 Chronicles", "divrei-hayamim-bet": "2 Chronicles",
}


def get_english_book_name(book_input):
    if book_input in BOOK_MAP:
        return BOOK_MAP[book_input]
    if book_input in BOOK_MAP.values():
        return book_input
    lower_input = book_input.lower()
    for k, v in BOOK_MAP.items():
        if k.lower() == lower_input or v.lower() == lower_input:
            return v
    return book_input


def create_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_from_sefaria(book_en, chapter=None, verse=None):
    if chapter is not None and verse is not None:
        ref = f"{book_en} {chapter}:{verse}"
    elif chapter is not None:
        ref = f"{book_en} {chapter}"
    else:
        ref = book_en

    url = f"{SEFARIA_BASE_URL}{urllib.parse.quote(ref)}"
    print(f"Запрос к Sefaria: {url}", file=sys.stderr)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Golem-Interlinear/1.0"})
        with urllib.request.urlopen(req, timeout=30, context=create_ssl_context()) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Ошибка запроса: {e}", file=sys.stderr)
        return None

    hebrew_text = ""
    english_text = ""
    ref_result = data.get("ref", ref)

    versions = data.get("versions", [])
    if isinstance(versions, list):
        for version in versions:
            if not isinstance(version, dict):
                continue
            lang = version.get("language", "")
            text = version.get("text", [])
            if lang == "he" and isinstance(text, list):
                hebrew_text = " ".join(str(t) for t in text if t)
            elif lang == "en" and isinstance(text, list):
                english_text = " ".join(str(t) for t in text if t)

    if not hebrew_text:
        hebrew_text = data.get("he", "")
    if not english_text:
        english_text = data.get("english", data.get("en", ""))

    niqqud_chars = set(range(0x0591, 0x05C8))
    hebrew_plain = "".join(ch for ch in hebrew_text if ord(ch) not in niqqud_chars)
    hebrew_plain = " ".join(hebrew_plain.split())
    hebrew_text = " ".join(hebrew_text.split())

    return {
        "hebrew": hebrew_text,
        "hebrew_plain": hebrew_plain,
        "english": english_text.strip(),
        "ref": ref_result,
    }


def save_to_cache(book_en, chapter, data):
    if chapter is None:
        return
    cache_path = CACHE_DIR / book_en / f"{chapter}.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Сохранено в кэш: {cache_path}", file=sys.stderr)


def load_from_cache(book_en, chapter, verse=None):
    if chapter is None:
        return None
    cache_path = CACHE_DIR / book_en / f"{chapter}.json"
    if not cache_path.exists():
        return None
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if verse is not None:
            verses = data.get("verses", [])
            if isinstance(verses, list) and len(verses) >= verse:
                return verses[verse - 1]
            return None
        return data
    except Exception as e:
        print(f"Ошибка чтения кэша: {e}", file=sys.stderr)
        return None


def parse_ref(ref_str):
    ref_str = ref_str.strip()
    match = re.match(r'^(\S+)\s+(\d+)(?::(\d+))?(?:-(\d+))?$', ref_str)
    if not match:
        raise ValueError(f"Неверный формат: {ref_str}")
    book_input = match.group(1)
    chapter = int(match.group(2))
    verse = int(match.group(3)) if match.group(3) else None
    end_chapter = int(match.group(4)) if match.group(4) else None
    book_en = get_english_book_name(book_input)
    return book_en, chapter, verse, end_chapter


def fetch_chapter(book_en, chapter):
    cached = load_from_cache(book_en, chapter)
    if cached:
        print(f"Загружено из кэша: {book_en} {chapter}", file=sys.stderr)
        return cached

    url = f"{SEFARIA_BASE_URL}{urllib.parse.quote(book_en + ' ' + str(chapter))}"
    print(f"Запрос к Sefaria: {url}", file=sys.stderr)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Golem-Interlinear/1.0"})
        with urllib.request.urlopen(req, timeout=30, context=create_ssl_context()) as resp:
            api_data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Ошибка запроса: {e}", file=sys.stderr)
        return None

    # Извлекаем текст из versions
    hebrew_verses = []
    english_verses = []
    versions = api_data.get("versions", [])
    if isinstance(versions, list):
        for version in versions:
            if not isinstance(version, dict):
                continue
            lang = version.get("language", "")
            text = version.get("text", [])
            if lang == "he" and isinstance(text, list):
                hebrew_verses = [re.sub(r'<[^>]+>', '', str(t)) if t else "" for t in text]
            elif lang == "en" and isinstance(text, list):
                english_verses = [re.sub(r'<[^>]+>', '', str(t)) if t else "" for t in text]

    # Fallback
    if not hebrew_verses:
        hebrew_verses = [api_data.get("he", "")]

    verses = []
    for i, hebrew_verse in enumerate(hebrew_verses):
        hebrew_verse = hebrew_verse.strip()
        if not hebrew_verse:
            continue

        niqqud_chars = set(range(0x0591, 0x05C8))
        hebrew_plain = "".join(ch for ch in hebrew_verse if ord(ch) not in niqqud_chars)
        hebrew_plain = " ".join(hebrew_plain.split())

        english_verse = english_verses[i].strip() if i < len(english_verses) else ""

        verses.append({
            "verse": i + 1,
            "hebrew": hebrew_verse,
            "hebrew_plain": hebrew_plain,
            "english": english_verse,
            "ref": f"{book_en} {chapter}:{i + 1}",
        })

    result = {
        "book": book_en,
        "chapter": chapter,
        "ref": f"{book_en} {chapter}",
        "verses": verses,
    }

    save_to_cache(book_en, chapter, result)
    return result


def fetch_verse(book_en, chapter, verse):
    chapter_data = load_from_cache(book_en, chapter)
    if chapter_data and "verses" in chapter_data:
        for v in chapter_data["verses"]:
            if v.get("verse") == verse:
                return v

    chapter_data = fetch_chapter(book_en, chapter)
    if chapter_data is None:
        return None

    for v in chapter_data.get("verses", []):
        if v.get("verse") == verse:
            return v
    return None


def main():
    parser = argparse.ArgumentParser(description="Получение текста ТаНаХа через Sefaria API")
    parser.add_argument("ref", type=str, help="Ссылка: 'Genesis 1' или 'Genesis 1:1' или 'bereshit 1-5'")
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--cache-only", action="store_true")

    args = parser.parse_args()

    try:
        book_en, chapter, verse, end_chapter = parse_ref(args.ref)
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    if end_chapter is not None:
        results = []
        for ch in range(chapter, end_chapter + 1):
            data = load_from_cache(book_en, ch) if args.cache_only else fetch_chapter(book_en, ch)
            if data:
                results.append(data)
        output_data = {"chapters": results}
    elif verse is not None:
        data = load_from_cache(book_en, chapter, verse) if args.cache_only else fetch_verse(book_en, chapter, verse)
        output_data = data if data else {}
    else:
        data = load_from_cache(book_en, chapter) if args.cache_only else fetch_chapter(book_en, chapter)
        output_data = data if data else {}

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"Сохранено в {output_path}")
    else:
        print(json.dumps(output_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()