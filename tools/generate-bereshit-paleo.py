#!/usr/bin/env python3
"""Собирает полный корпус Берешит для Research Lab из WLC/OSHB.

База: Westminster Leningrad Codex в Open Scriptures Hebrew Bible (public domain).
Палео-строка — механическое отображение согласного слоя в 22 древнееврейских
Unicode-глифа. Самаритянский корпус и кумранские фрагменты не смешиваются с
базовым текстом: они остаются отдельными свидетелями вариантов.
"""
from __future__ import annotations

import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "products" / "website" / "apps" / "researchlab" / "data" / "scripture"
SOURCE_BASE = "https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/"
BOOKS = {
    "bereshit": [("Gen", "Gen")], "shmot": [("Exod", "Exod")], "vayikra": [("Lev", "Lev")],
    "bemidbar": [("Num", "Num")], "dvarim": [("Deut", "Deut")], "yehoshua": [("Josh", "Josh")],
    "shoftim": [("Judg", "Judg")], "shmuel-alef": [("1Sam", "1Sam")], "shmuel-bet": [("2Sam", "2Sam")],
    "melachim-alef": [("1Kgs", "1Kgs")], "melachim-bet": [("2Kgs", "2Kgs")], "yeshayahu": [("Isa", "Isa")],
    "yirmeyahu": [("Jer", "Jer")], "yehezkel": [("Ezek", "Ezek")],
    "the-twelve": [(x, x) for x in "Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal".split()],
    "tehillim": [("Ps", "Ps")], "mishlei": [("Prov", "Prov")], "iyov": [("Job", "Job")],
    "shir-hashirim": [("Song", "Song")], "rut": [("Ruth", "Ruth")], "eikhah": [("Lam", "Lam")],
    "kohelet": [("Eccl", "Eccl")], "daniel": [("Dan", "Dan")],
    "ezra-nechemyah": [("Ezra", "Ezra"), ("Neh", "Neh")], "divrei-hayamim": [("1Chr", "1Chr"), ("2Chr", "2Chr")]
}
NS = {"osis": "http://www.bibletechnologies.net/2003/OSIS/namespace"}
PALEO = str.maketrans({
    "א": "𐤀", "ב": "𐤁", "ג": "𐤂", "ד": "𐤃", "ה": "𐤄", "ו": "𐤅",
    "ז": "𐤆", "ח": "𐤇", "ט": "𐤈", "י": "𐤉", "כ": "𐤊", "ך": "𐤊",
    "ל": "𐤋", "מ": "𐤌", "ם": "𐤌", "נ": "𐤍", "ן": "𐤍", "ס": "𐤎",
    "ע": "𐤏", "פ": "𐤐", "ף": "𐤐", "צ": "𐤑", "ץ": "𐤑", "ק": "𐤒",
    "ר": "𐤓", "ש": "𐤔", "ת": "𐤕",
})
FUNCTIONS = {
    "א": "сила", "ב": "вместилище", "ג": "движение", "ד": "проход",
    "ה": "откровение", "ו": "связка", "ז": "защита", "ח": "отделение",
    "ט": "оборачивание", "י": "действие", "כ": "удержание", "ך": "удержание",
    "ל": "направление", "מ": "поток", "ם": "поток", "נ": "движение жизни",
    "ן": "движение жизни", "ס": "поддержка", "ע": "источник", "פ": "открытие",
    "ף": "открытие", "צ": "захват", "ץ": "захват", "ק": "отделение",
    "ר": "вершина", "ש": "разрушение", "ת": "фиксация",
}
HEBREW_MARKS = re.compile(r"[\u0591-\u05c7]")
NON_TEXT = re.compile(r"[^\u05d0-\u05ea\s\u05be]")
SPACE = re.compile(r"\s+")


def clean_word(value: str) -> str:
    """Убирает морфологические разделители OSHB, оставляя квадратное письмо."""
    return value.replace("/", "").replace("־", "־").strip()


def verse_surface(verse: ET.Element) -> str:
    parts: list[str] = []
    for child in verse:
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "w":
            word = clean_word("".join(child.itertext()))
            if word:
                parts.append(word)
        elif tag == "seg":
            marker = "".join(child.itertext()).strip()
            if marker == "־" and parts:
                parts[-1] += marker
    return " ".join(parts)


def consonants(hebrew: str) -> str:
    text = HEBREW_MARKS.sub("", hebrew).replace("־", "")
    text = NON_TEXT.sub("", text)
    return SPACE.sub(" ", text).strip()


def paleo_text(hebrew: str) -> str:
    return consonants(hebrew).translate(PALEO)


def words_for(hebrew: str, paleo: str) -> list[dict[str, str]]:
    hebrew_words = consonants(hebrew).split()
    paleo_words = paleo.split()
    return [
        {"hebrew": word, "paleo": paleo_words[index], "translit": "", "literal": ""}
        for index, word in enumerate(hebrew_words)
    ]


def draft_paleo_translation(hebrew: str) -> str:
    """Черновая сборка функций букв; это не литературный перевод."""
    groups = []
    for word in consonants(hebrew).split():
        functions = " → ".join(FUNCTIONS[letter] for letter in word if letter in FUNCTIONS)
        if functions:
            groups.append(functions)
    return "Черновая палео-сборка: " + " ; ".join(groups)


def draft_verse_function(hebrew: str) -> str:
    """Краткая уникальная функция стиха из наиболее частых палео-действий."""
    sequence = [FUNCTIONS[letter] for letter in consonants(hebrew) if letter in FUNCTIONS]
    unique = []
    for function in sequence:
        if function not in unique:
            unique.append(function)
        if len(unique) == 4:
            break
    return "Черновая функция стиха: " + " → ".join(unique) + "."


def load_existing(target: Path) -> dict[tuple[str, int, int], dict]:
    if not target.exists():
        return {}
    existing = json.loads(target.read_text(encoding="utf-8"))
    return {(item.get("source_book", "Gen"), item["chapter"], item["verse"]): item for item in existing}


def generate(book_id: str, sources: list[tuple[str, str]]) -> int:
    target = DATA_DIR / ("bereshit-1.json" if book_id == "bereshit" else book_id + ".json")
    existing = load_existing(target)
    rebuilt: list[dict] = []
    for source_book, filename in sources:
        with urllib.request.urlopen(SOURCE_BASE + filename + ".xml", timeout=60) as response:
            root = ET.fromstring(response.read())
        for node in root.findall(".//osis:verse", NS):
            ref = node.attrib.get("osisID", "")
            match = re.fullmatch(re.escape(source_book) + r"\.(\d+)\.(\d+)", ref)
            if not match:
                continue
            chapter, verse = map(int, match.groups())
            hebrew = verse_surface(node)
            paleo = paleo_text(hebrew)
            if not hebrew or not paleo:
                raise ValueError(f"Пустой стих в источнике: {ref}")
            prior = existing.get((source_book, chapter, verse), {})
            item = dict(prior)
            item.update({
                "chapter": chapter,
                "verse": verse,
                "source_book": source_book,
                "hebrew": hebrew,
                "paleo": paleo,
                "words": words_for(hebrew, paleo),
                "text_source": "WLC/OSHB " + filename + ".xml (WLC text: Public Domain; morphology: CC BY 4.0)",
                "paleo_source": "Механическая реконструкция согласного слоя через таблицу 22 букв Research Lab; не факсимиле единой рукописи.",
                "witnesses": "Самаритянское Пятикнижие и кумранские фрагменты — отдельные свидетельства вариантов.",
                "paleo_translation": draft_paleo_translation(hebrew),
                "paleo_translation_status": "draft",
                "paleo_function": draft_verse_function(hebrew),
                "verse_function": draft_verse_function(hebrew),
                "function": draft_verse_function(hebrew),
                "paleo_translation_basis": ["WLC/OSHB", "таблица 22 палео-функций Research Lab"],
                "paleo_translation_note": "Черновая сборка показывает последовательности функций букв и требует человеческой проверки; это не литературный перевод."
            })
            rebuilt.append(item)
    if not rebuilt:
        raise ValueError(f"Пустой корпус: {book_id}")
    target.write_text(json.dumps(rebuilt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{book_id}: {len(rebuilt)} стихов")
    return len(rebuilt)

def main() -> None:
    total = sum(generate(book_id, sources) for book_id, sources in BOOKS.items())
    print(f"Всего: {total} стихов")


if __name__ == "__main__":
    main()