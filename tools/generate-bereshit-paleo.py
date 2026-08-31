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
TARGET = ROOT / "products" / "website" / "apps" / "researchlab" / "data" / "scripture" / "bereshit-1.json"
SOURCE_URL = "https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Gen.xml"
NS = {"osis": "http://www.bibletechnologies.net/2003/OSIS/namespace"}
PALEO = str.maketrans({
    "א": "𐤀", "ב": "𐤁", "ג": "𐤂", "ד": "𐤃", "ה": "𐤄", "ו": "𐤅",
    "ז": "𐤆", "ח": "𐤇", "ט": "𐤈", "י": "𐤉", "כ": "𐤊", "ך": "𐤊",
    "ל": "𐤋", "מ": "𐤌", "ם": "𐤌", "נ": "𐤍", "ן": "𐤍", "ס": "𐤎",
    "ע": "𐤏", "פ": "𐤐", "ף": "𐤐", "צ": "𐤑", "ץ": "𐤑", "ק": "𐤒",
    "ר": "𐤓", "ש": "𐤔", "ת": "𐤕",
})
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


def load_existing() -> dict[tuple[int, int], dict]:
    existing = json.loads(TARGET.read_text(encoding="utf-8"))
    return {(item["chapter"], item["verse"]): item for item in existing}


def main() -> None:
    existing = load_existing()
    with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:
        root = ET.fromstring(response.read())

    rebuilt: list[dict] = []
    for node in root.findall(".//osis:verse", NS):
        ref = node.attrib.get("osisID", "")
        match = re.fullmatch(r"Gen\.(\d+)\.(\d+)", ref)
        if not match:
            continue
        chapter, verse = map(int, match.groups())
        hebrew = verse_surface(node)
        paleo = paleo_text(hebrew)
        if not hebrew or not paleo:
            raise ValueError(f"Пустой стих в источнике: {ref}")
        prior = existing.get((chapter, verse), {})
        item = dict(prior)
        item.update({
            "chapter": chapter,
            "verse": verse,
            "hebrew": hebrew,
            "paleo": paleo,
            "words": words_for(hebrew, paleo),
            "text_source": "WLC/OSHB Gen.xml (WLC text: Public Domain; morphology: CC BY 4.0)",
            "paleo_source": "Механическая реконструкция согласного слоя через таблицу 22 букв Research Lab; не факсимиле единой рукописи.",
            "witnesses": "Самаритянское Пятикнижие и кумранские фрагменты — отдельные свидетельства вариантов."
        })
        rebuilt.append(item)

    if len(rebuilt) != 1533:
        raise ValueError(f"Ожидалось 1533 стиха Берешит, получено {len(rebuilt)}")
    TARGET.write_text(json.dumps(rebuilt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Записано {len(rebuilt)} стихов: {TARGET}")


if __name__ == "__main__":
    main()