#!/usr/bin/env python3
# tools/generators/generate-researches-json.py — генерация data/researches.json
# для страницы «Разоблачения» в researchlab из готовых md-эссе content/researches/.

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / "content" / "researches"
OUTPUT_PATH = REPO_ROOT / "products" / "website" / "researchlab" / "data" / "researches.json"

# Файлы-заготовки по общему шаблону "образ" (adam/, anatomy/, elohim/, kehillah/, mikra/, geography/,
# creation/ и т.п.) содержат этот текст, пока раздел не написан руками.
STUB_MARKERS = (
    "Требует изучения в контексте ТаНаХа",
    "Требует исследования. Минимум 2 стиха",
    "Необходимо восстановить ивритское понимание и отбросить религиозные наслоения.",
)
MIN_LENGTH = 900

CATEGORY_LABELS = {
    "adam": "Адам",
    "anatomy": "Анатомия",
    "archive": "Архив",
    "books": "Книги",
    "companies": "Компании",
    "creation": "Творение",
    "economy": "Экономика",
    "elohim": "Элоhим",
    "geography": "География",
    "history": "История",
    "kehillah": "Кеhилла",
    "language": "Язык",
    "laws": "Законы",
    "media": "Медиа",
    "medicine": "Медицина",
    "mikra": "Микра",
    "moadim": "Моадим",
    "names": "Имена",
    "practices": "Практики",
    "psychology": "Психология",
    "science": "Наука",
    "slavery": "Рабство",
    "sociology": "Общество",
    "sports": "Спорт",
    "symbols": "Символика",
    "systems": "Системы",
    "tamid": "Тамид",
    "technologies": "Технологии",
}

HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
META_FIELD_RE = re.compile(r"-\s+\*\*([^*]+?):?\*\*:?\s*(.+)")


def is_stub(text: str) -> bool:
    if any(marker in text for marker in STUB_MARKERS):
        return True
    return len(text.strip()) < MIN_LENGTH


def clean_title(raw: str) -> str:
    title = re.sub(r"\s+", " ", raw.strip())
    return title


def extract_metadata(text: str) -> tuple:
    meta = {}
    marker = text.find("**Метаданные файла**")
    if marker == -1:
        return meta, -1
    block_end = text.find("\n---", marker)
    block = text[marker:block_end if block_end != -1 else marker + 2000]
    for line in block.splitlines():
        match = META_FIELD_RE.match(line.strip())
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip().strip("`")
            meta[key] = value
    return meta, (block_end if block_end != -1 else marker)


def strip_metadata_block(text: str, block_end: int) -> str:
    if block_end <= 0:
        return text
    return text[block_end:].lstrip("-\n ")


def build_entry(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    heading_match = HEADING_RE.search(text)
    title = clean_title(heading_match.group(1)) if heading_match else path.stem.replace("-", " ")

    meta, block_end = extract_metadata(text)
    body = strip_metadata_block(text, block_end)

    rel = path.relative_to(SOURCE_DIR).as_posix()
    category_key = rel.split("/")[0]

    return {
        "id": rel[:-3],
        "title": title,
        "category": CATEGORY_LABELS.get(category_key, category_key),
        "summary": meta.get("Тема", ""),
        "date": meta.get("Дата создания", ""),
        "confidence": meta.get("Достоверность", ""),
        "checksCount": meta.get("Проверок на религионизмы", ""),
        "body": body.strip(),
    }


def generate() -> list:
    entries = []
    for path in sorted(SOURCE_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if is_stub(text):
            continue
        entries.append(build_entry(path))
    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries


def main():
    entries = generate()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[OK] {OUTPUT_PATH} — {len(entries)} исследований")
    by_cat = {}
    for e in entries:
        by_cat[e["category"]] = by_cat.get(e["category"], 0) + 1
    for cat, count in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
