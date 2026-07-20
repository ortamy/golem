#!/usr/bin/env python3
"""
migrate-exposures.py — TASK-060, шаг 0.

Сливает два несовместимых источника «Разоблачений»:
  - products/website/apps/researchlab/data/researches.json (плоский markdown body)
  - products/website/apps/researchlab/data/research/*.json (структурированные дела)
в единую схему products/website/apps/researchlab/data/exposures/index.json.

Разово, вручную запускаемый скрипт. Не удаляет исходные файлы.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAB = ROOT / "products" / "website" / "apps" / "researchlab"
RESEARCHES_JSON = LAB / "data" / "researches.json"
RESEARCH_DIR = LAB / "data" / "research"
OUT_DIR = LAB / "data" / "exposures"
OUT_FILE = OUT_DIR / "index.json"

CONFIDENCE_MAP_KEYWORDS = [
    (("гипотеза", "предполож"), "hypothesis"),
    (("спорн",), "disputed"),
    (("требует", "не подтвержд", "низк"), "needs-review"),
    (("высок", "достоверно", "подтвержд"), "verified"),
]


def slugify(raw_id):
    slug = raw_id.strip().lower()
    slug = slug.replace("/", "-").replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]+", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "case"


def normalize_confidence(text):
    if not text:
        return "needs-review", text or ""
    low = text.lower()
    for keywords, enum_value in CONFIDENCE_MAP_KEYWORDS:
        if any(k in low for k in keywords):
            return enum_value, text
    return "needs-review", text


def split_markdown_sections(body):
    """Разбивает markdown body на {heading, body} по заголовкам '## '."""
    if not body:
        return "", []
    lines = body.split("\n")
    intro_lines = []
    sections = []
    current_heading = None
    current_lines = []

    def flush():
        if current_heading is not None:
            sections.append({
                "heading": current_heading,
                "body": "\n".join(current_lines).strip()
            })

    for line in lines:
        m = re.match(r"^##\s+(.*)$", line)
        if m:
            flush()
            current_heading = m.group(1).strip()
            current_lines = []
        elif current_heading is None:
            intro_lines.append(line)
        else:
            current_lines.append(line)
    flush()

    thesis = "\n".join(intro_lines).strip()
    return thesis, sections


def migrate_researches_json():
    if not RESEARCHES_JSON.exists():
        print(f"skip: {RESEARCHES_JSON} not found", file=sys.stderr)
        return []
    items = json.loads(RESEARCHES_JSON.read_text(encoding="utf-8"))
    out = []
    for item in items:
        slug = slugify(item.get("id", ""))
        thesis, sections = split_markdown_sections(item.get("body", ""))
        confidence, confidence_note = normalize_confidence(item.get("confidence", ""))
        out.append({
            "id": slug,
            "slug": slug,
            "title": item.get("title", ""),
            "summary": item.get("summary", ""),
            "tags": [],
            "category": item.get("category", ""),
            "distortionType": "",
            "method": "",
            "period": "",
            "status": "published",
            "confidence": confidence,
            "confidenceNote": confidence_note,
            "sources": [],
            "related": [],
            "roots": [],
            "updatedAt": item.get("date", ""),
            "createdAt": item.get("date", ""),
            "author": "",
            "changelog": [{"date": item.get("date", ""), "note": "Мигрировано из researches.json"}],
            "sections": {
                "thesis": thesis or item.get("summary", ""),
                "original": None,
                "shift": "",
                "transmissionChain": [],
                "content": sections,
                "evidence": [],
                "reconstruction": "",
                "caveats": [],
                "relatedMaterials": []
            }
        })
    return out


def migrate_research_dir():
    if not RESEARCH_DIR.exists():
        print(f"skip: {RESEARCH_DIR} not found", file=sys.stderr)
        return []
    out = []
    for path in sorted(RESEARCH_DIR.glob("*.json")):
        if path.stem == "template":
            continue
        item = json.loads(path.read_text(encoding="utf-8"))
        slug = slugify(item.get("id", path.stem))
        confidence, confidence_note = normalize_confidence("")
        evidence = [{
            "type": "ТаНаХ",
            "ref": q.get("ref", ""),
            "hebrew": q.get("hebrew", ""),
            "translit": q.get("translit", ""),
            "literal": q.get("literal", "")
        } for q in item.get("quotes", [])]
        chain = [{
            "layer": s.get("layer", ""),
            "word": s.get("word", ""),
            "meaning": s.get("meaning", "")
        } for s in item.get("substitutionChain", [])]
        out.append({
            "id": slug,
            "slug": slug,
            "title": item.get("title", ""),
            "summary": item.get("summary", ""),
            "tags": item.get("tags", []),
            "category": {"root": "Корень", "term": "Термин", "verse": "Стих", "substitution": "Подмена"}.get(item.get("type", ""), item.get("type", "")),
            "distortionType": "",
            "method": "",
            "period": "",
            "status": "published",
            "confidence": confidence,
            "confidenceNote": confidence_note,
            "sources": [],
            "related": [slugify(r) for r in item.get("related", [])],
            "roots": [],
            "updatedAt": item.get("date", ""),
            "createdAt": item.get("date", ""),
            "author": "",
            "changelog": [{"date": item.get("date", ""), "note": "Мигрировано из data/research/" + path.name}],
            "sections": {
                "thesis": item.get("summary", ""),
                "original": {"paleo": item.get("paleo", [])} if item.get("paleo") else None,
                "shift": "",
                "transmissionChain": chain,
                "content": item.get("content", []),
                "evidence": evidence,
                "reconstruction": "",
                "caveats": [],
                "relatedMaterials": []
            }
        })
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    from_researches = migrate_researches_json()
    from_library = migrate_research_dir()

    by_slug = {}
    for entry in from_researches + from_library:
        # data/research/*.json — более богатая структура, приоритет при совпадении slug
        if entry["slug"] not in by_slug or entry["sections"]["content"]:
            by_slug[entry["slug"]] = entry

    merged = list(by_slug.values())
    merged.sort(key=lambda e: (e["category"], e["title"]))

    OUT_FILE.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"written {len(merged)} cases -> {OUT_FILE}")


if __name__ == "__main__":
    main()
