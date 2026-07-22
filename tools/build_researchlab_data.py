from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
OUTPUT = ROOT / "products" / "website" / "apps" / "researchlab" / "data"

PALEO = {
    "א": "𐤀",
    "ב": "𐤁",
    "ג": "𐤂",
    "ד": "𐤃",
    "ה": "𐤄",
    "ו": "𐤅",
    "ז": "𐤆",
    "ח": "𐤇",
    "ט": "𐤈",
    "י": "𐤉",
    "כ": "𐤊",
    "ך": "𐤊",
    "ל": "𐤋",
    "מ": "𐤌",
    "ם": "𐤌",
    "נ": "𐤍",
    "ן": "𐤍",
    "ס": "𐤎",
    "ע": "𐤏",
    "פ": "𐤐",
    "ף": "𐤐",
    "צ": "𐤑",
    "ץ": "𐤑",
    "ק": "𐤒",
    "ר": "𐤓",
    "ש": "𐤔",
    "ת": "𐤕",
}

HEBREW = re.compile(r"[\u0590-\u05ff][\u0590-\u05ff\s־'\"״׳-]*")
HEBREW_MARKS = {unicodedata.category(chr(code)) for code in range(0x0590, 0x05ff)}
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def clean_title(value: str) -> str:
    value = re.sub(r"\s+", " ", value.strip())
    value = re.sub(r"^[^\w\u0590-\u05ff]+\s*", "", value)
    if "—" in value:
        sides = [part.strip() for part in value.split("—")]
        cyrillic = [part for part in sides if re.search(r"[А-Яа-яЁё]", part)]
        if cyrillic:
            value = cyrillic[0]
    value = value.split(":", 1)[0].strip()
    value = re.sub(r"\s+", " ", value)
    return value[:1].upper() + value[1:].lower() if value else value


def strip_markup(value: str) -> str:
    value = re.sub(r"\*\*(.*?)\*\*", r"\1", value)
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"^>\s*", "", value)
    return value.strip()


def compact_description(lines: list[str]) -> str:
    paragraphs: list[str] = []
    current: list[str] = []
    for line in lines:
        if not line.strip():
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
        else:
            current.append(strip_markup(line.strip()))
    if current:
        paragraphs.append(" ".join(current).strip())
    return "\n\n".join(part for part in paragraphs if part)


def unpoint(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(char for char in normalized if char in PALEO)


def paleo_for(hebrew: str) -> list[str]:
    return [PALEO[char] for char in unpoint(hebrew) if char in PALEO]


def source_word(left: str) -> str:
    left = left[1:].strip() if left.lstrip().startswith("-") else left.strip()
    bold = re.search(r"\*\*(.+?)\*\*", left)
    if bold:
        return strip_markup(bold.group(1))
    code = re.search(r"`([^`]+)`", left)
    if code:
        return code.group(1).strip()
    return strip_markup(left).strip(" -*")


def translation_for(rhs: str, end: int, next_start: int | None) -> tuple[str, str]:
    tail = rhs[end: next_start if next_start is not None else len(rhs)]
    translit_match = re.match(r"\s*\(([^)]*)\)", tail)
    translit = translit_match.group(1).strip() if translit_match else ""
    dash = tail.find("—")
    if dash < 0:
        return translit, translit
    restored = tail[dash + 1:].strip()
    restored = re.split(r"\.\s+(?:ТаНаХ|Подмена|Искажение|нет прямого аналога)", restored, maxsplit=1)[0]
    restored = restored.split(";", 1)[0].strip(" .;,:\t")
    restored = re.sub(r"\s+", " ", restored)
    return restored or translit, translit


def dictionary_terms(lines: list[str]) -> list[dict[str, object]]:
    terms: list[dict[str, object]] = []
    for line in lines:
        if "→" not in line or not line.lstrip().startswith("-"):
            continue
        left, rhs = line.split("→", 1)
        word = source_word(left)
        matches = list(HEBREW.finditer(rhs))
        if not word or not matches:
            continue
        for index, match in enumerate(matches):
            raw_hebrew = match.group(0)
            # "או" is the Hebrew word for "or" in several source entries.
            alternatives = re.split(r"\s+או\s+", raw_hebrew.strip())
            if any(alternatives):
                offset = match.start()
                for alternative in alternatives:
                    alternative = alternative.strip(" -־")
                    if not alternative or not unpoint(alternative):
                        continue
                    next_start = matches[index + 1].start() if index + 1 < len(matches) else None
                    restored, _ = translation_for(rhs, match.end(), next_start)
                    if len(alternatives) > 1 and alternative != alternatives[-1]:
                        # A split inside one match has one common translation tail;
                        # keep the source wording rather than inventing a meaning.
                        restored = restored or alternative
                    terms.append(
                        {
                            "word": word,
                            "hebrew": unpoint(alternative),
                            "paleo": paleo_for(alternative),
                            "restored": restored,
                        }
                    )
                    offset += len(alternative)
    return terms


def markdown_document(path: Path) -> tuple[str, str, list[dict[str, str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    headings = [(index, len(match.group(1)), match.group(2))
                for index, line in enumerate(lines)
                if (match := HEADING.match(line))]
    title = clean_title(headings[0][2]) if headings else path.stem
    sections: list[dict[str, str]] = []
    for position, (start, level, heading) in enumerate(headings):
        if level == 1:
            continue
        next_heading = next((item[0] for item in headings[position + 1:] if item[1] >= 2), len(lines))
        content = "\n".join(lines[start + 1:next_heading]).strip()
        sections.append({"title": clean_title(heading), "content": content})
    intro = next((section["content"] for section in sections
                  if "введ" in section["title"].lower() or section["title"].lower() in {"цель", "основа"}), "")
    return title, compact_description(intro.splitlines()), sections


def build_dictionaries() -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for path in sorted((ANALYSIS / "dictionaries").glob("*.md")):
        title, description, _ = markdown_document(path)
        result[path.stem.removeprefix("dictionaries-")] = {
            "title": title,
            "description": description,
            "terms": dictionary_terms(path.read_text(encoding="utf-8").splitlines()),
        }
    return result


def build_documents(directory: str, prefix: str) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for path in sorted((ANALYSIS / directory).glob("*.md")):
        title, description, sections = markdown_document(path)
        result[path.stem.removeprefix(prefix)] = {
            "title": title,
            "description": description,
            "sections": sections,
        }
    return result


def write_json(filename: str, value: object) -> None:
    output_path = OUTPUT / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    write_json("dictionaries.json", build_dictionaries())
    write_json("exposures/documents.json", build_documents("exposure", "exposure-"))
    write_json("methodology.json", build_documents("methodology", "methodology-"))
    dictionaries = build_dictionaries()
    print("dictionaries:", len(dictionaries), "files,", sum(len(item["terms"]) for item in dictionaries.values()), "terms")
    print("exposure:", len(build_documents("exposure", "exposure-")), "files")
    print("methodology:", len(build_documents("methodology", "methodology-")), "files")