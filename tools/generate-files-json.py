#!/usr/bin/env python3
"""Генерирует products/website/files.json для legacy-ридера (GolemAPI / GolemState).

Формат записи совпадает с products/website/config/server.js:
  path, title, topic, category, subcategory, related, icon.

Пути — относительно корня products/website/, как их отдаёт /api/files
и как их читает loadFile() при локальном запуске.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "products" / "website"
OUT = WEB / "files.json"

SCAN_DIRS = (
    ("src/content/md/terminology", "Терминология"),
    ("src/content/md/tanakh", "ТаНаХ"),
    ("src/content/md/bashah", "БаШаХ"),
    ("src/content/md/researches", "Исследования"),
    ("src/content/md/teachings", "Учения"),
    ("src/content/md/hebrew", "Изучение иврита"),
    ("src/content/md/paleo-hebrew", "Палео-иврит"),
)

IGNORE_FILES = {"README.md", "STRUCTURE.md", "GLOSSARY.md", "CHANGELOG.md"}

SUBCATEGORY_LABELS = {
    "archive": "Архив", "books": "Книги", "chronology": "Хронология",
    "companies": "Компании", "concepts": "Понятия", "economy": "Экономика",
    "events": "События", "history": "История", "language": "Язык",
    "languages": "Языки", "manuscripts": "Рукописи", "media": "Медиа",
    "medicine": "Медицина", "names": "Имена", "persons": "Личности",
    "physis": "Природа", "practices": "Практики", "psychology": "Психология",
    "roman-law": "Римское право", "science": "Наука", "simvolika": "Символика",
    "slavery": "Рабство", "sociology": "Общество", "sport": "Спорт",
    "systems": "Системы", "tanakh": "ТаНаХ", "teachings": "Учения",
    "anatomy": "Анатомия", "creation": "Творение", "elohim": "Элоhим",
    "geography": "География", "kehillah": "Кеhилла",
}

ICON_RULES = {
    "content/terminology": "scroll.png", "content/researches": "book.png",
    "content/teachings": "heart.png", "content/practices": "shield.png",
    "content/hebrew": "lamp.png", "content/exposed": "sword.png",
    "content/tanakh/books": "scrolls.png", "content/tanakh/persons": "scrolls.png",
    "content/tanakh/events": "scrolls.png", "content/bashah/books": "scrolls.png",
    "content/bashah/letters": "scales.png", "content/bashah/persons": "scrolls.png",
    "content/bashah/events": "scrolls.png", "content/bashah/teachings": "heart.png",
    "content/bashah/terminology": "scroll.png", "content/bashah/concepts": "anchor.png",
    "content/bashah/practices": "shield.png", "content/bashah/chronology": "hourglass.png",
    "content/bashah/manuscripts": "scrolls.png", "content/bashah/geography": "scrolls.png",
}

_H1 = re.compile(r"^#\s+(.+)$", re.M)
_TOPIC = re.compile(r"\*\*Тема:\*\*\s*(.+?)(?:\n|$)")
_RELATED_BLOCK = re.compile(r"\*\*Связанные файлы:\*\*[\s\S]*?(?=\n\n|$)")
_RELATED_ITEM = re.compile(r"`([^`]+)`")
_EMOJI = re.compile(
    r"[\U0001F000-\U0001FFFF\u2600-\u27BF\uFE00-\uFEFF\u200D\uFE0F]"
)


def resolve_icon(rel_path: str) -> str:
    variants = [rel_path]
    if rel_path.startswith("src/"):
        variants.append(rel_path[4:])
    variants.append(rel_path.replace("src/content/md/", "content/"))
    keys = sorted(ICON_RULES, key=len, reverse=True)
    for variant in variants:
        for key in keys:
            if variant.startswith(key):
                return ICON_RULES[key]
    return "scrolls.png"


def extract_title(content: str, filename: str) -> str:
    match = _H1.search(content)
    if match:
        title = _EMOJI.sub("", match.group(1)).strip()
        return title[:80]
    return filename.replace(".md", "").replace("-", " ")


def extract_topic(content: str) -> str:
    match = _TOPIC.search(content)
    return match.group(1).strip()[:100] if match else ""


def extract_related(content: str) -> list[str]:
    related: list[str] = []
    for block in _RELATED_BLOCK.findall(content):
        for item in _RELATED_ITEM.findall(block):
            if item not in related:
                related.append(item)
    return related


def subcategory_for(rel_from_scan: str) -> str:
    parts = Path(rel_from_scan).parts
    if len(parts) < 2:
        return ""
    key = parts[0]
    return SUBCATEGORY_LABELS.get(key, key)


def scan() -> list[dict]:
    files: list[dict] = []
    for folder, label in SCAN_DIRS:
        directory = WEB / folder
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.md")):
            if path.name in IGNORE_FILES:
                continue
            rel_path = path.relative_to(WEB).as_posix()
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel_from_scan = path.relative_to(directory).as_posix()
            files.append({
                "path": rel_path,
                "title": extract_title(content, path.name),
                "topic": extract_topic(content),
                "category": label,
                "subcategory": subcategory_for(rel_from_scan),
                "related": extract_related(content),
                "icon": resolve_icon(rel_path),
            })
    return files


def generate(out_path: Path | None = None) -> Path:
    target = out_path or OUT
    payload = scan()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Генератор products/website/files.json")
    parser.add_argument("--out", type=Path, default=None, help="путь записи (по умолчанию products/website/files.json)")
    parser.add_argument("--print-count", action="store_true", help="только число записей, файл не писать")
    args = parser.parse_args()
    if args.print_count:
        print(len(scan()))
        return
    path = generate(args.out)
    count = len(json.loads(path.read_text(encoding="utf-8")))
    print(f"✅ {path.relative_to(ROOT)}: {count} файлов")


if __name__ == "__main__":
    main()
