"""Собирает слой СП из открытого корпуса DT-UCPH/sp.

Источник хранит СП в Text-Fabric: диапазоны знаков привязаны к стихам,
а значения g_cons_utf8 — к словесным узлам. Палео-ряд получается только
механической заменой знаков, без реконструкции текста.
"""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/DT-UCPH/sp/main/tf/5.0.2/"
ROOT = Path(__file__).resolve().parents[1]
APP_DATA = ROOT / "products/website/apps/researchlab/data"
OUT = APP_DATA / "scripture/samaritan_paleo.json"

PALEO = dict(zip("אבגדהוזחטיכלמנסעפצקרשת", "𐤀𐤁𐤂𐤃𐤄𐤅𐤆𐤇𐤈𐤉𐤊𐤋𐤌𐤍𐤎𐤏𐤐𐤑𐤒𐤓𐤔𐤕"))
FINAL = dict(zip("ךםןףץ", "כמנפצ"))

def fetch(name: str) -> list[str]:
    text = urllib.request.urlopen(BASE + name, timeout=90).read().decode("utf-8")
    return [line.rstrip("\r") for line in text.splitlines()]

def values(lines: list[str]) -> list[str]:
    result = []
    for line in lines:
        if not line or line.startswith("@"):
            continue
        match = re.match(r"^\d+[ \t]+(.+)$", line)
        if match:
            result.append(match.group(1))
        else:
            result.append(line)
    return result

def ranges(lines: list[str], first: int, last: int) -> dict[int, tuple[int, int]]:
    vals = values(lines)
    result = {}
    for node, value in zip(range(first, last + 1), vals):
        numbers = [int(item) for item in re.findall(r"\d+", value)]
        if numbers:
            result[node] = (min(numbers), max(numbers))
    return result

def clean(value: str) -> str:
    value = re.sub(r"[\u0591-\u05c7\s\u05be\u05c0\u05c3\u05c4\u05c5\u05c6]", "", value)
    return "".join(FINAL.get(ch, ch) for ch in value)

def to_paleo(value: str) -> str:
    return "".join(PALEO.get(ch, ch) for ch in clean(value))

def load_mt() -> list[dict]:
    path = APP_DATA / "scripture/bereshit-1.json"
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> None:
    # Node ranges are documented in otype.tf: verse 399585–405425, word 405426–520314.
    verse_slots = ranges(fetch("oslots.tf"), 399585, 405425)
    word_slots = ranges(fetch("oslots.tf"), 405426, 520314)
    word_values = values(fetch("g_cons_utf8.tf"))
    word_text = {node: word_values[node - 405426] for node in word_slots}
    verses = values(fetch("verse.tf"))
    # Координаты книги и главы берём из локального MT-набора.
    mt = load_mt()
    output = []
    for index, verse in enumerate(mt):
        node = 399585 + index
        start, end = verse_slots[node]
        source_words = [word_text[n] for n, (a, b) in word_slots.items() if a >= start and b <= end]
        # Порядок слов сохраняется порядком узлов Text-Fabric.
        target_words = str(verse.get("hebrew", "")).split()
        # Preserve MT word boundaries while retaining only source tokens. Prefixes such as ו/ב
        # are combined with the following token by the deterministic character budget.
        grouped, cursor, review = [], 0, False
        for target in target_words:
            target_clean = clean(target)
            acc = ""
            begin = cursor
            while cursor < len(source_words) and len(acc) < len(target_clean):
                acc += clean(source_words[cursor]); cursor += 1
            if clean(acc) != target_clean:
                review = True
            grouped.append("".join(to_paleo(x) for x in source_words[begin:cursor]))
        if cursor < len(source_words):
            review = True
            grouped[-1] += "".join(to_paleo(x) for x in source_words[cursor:])
        output.append({
            "ref": verse.get("ref", f"Bereshit 1:{index + 1}"),
            "book": "bereshit",
            "chapter": verse.get("chapter", 1),
            "verse": verse.get("verse", index + 1),
            "paleo": " ".join(grouped),
            "words": grouped,
            "status": "Требуется проверка" if review else "verified-source-aligned",
            "source": "DT-UCPH/sp 5.0.2, g_cons_utf8 + oslots",
        })
    OUT.write_text(json.dumps({
        "meta": {
            "title": "Самаритянское Пятикнижие — палео-слой",
            "source_url": "https://github.com/DT-UCPH/sp",
            "license": "CC BY-NC 4.0",
            "manuscripts": "MS Dublin Chester Beatty Library 751; MS Garizim 1",
            "alignment": "Словесные границы СП сведены к границам МТ; расхождения помечены.",
        },
        "verses": output,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(output)} verses; review={sum(x['status'] != 'verified-source-aligned' for x in output)})")

if __name__ == "__main__":
    main()