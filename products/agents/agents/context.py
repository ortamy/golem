#!/usr/bin/env python3
# products/agents/agents/context.py — общие утилиты для агентов Голема
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = REPO_ROOT / "products" / "website" / "apps" / "researchlab" / "data"
CONTENT_DIR = REPO_ROOT / "content"
INSTRUCTIONS_DIR = REPO_ROOT / "instructions"

_cache = {}


def _load_json(path: Path) -> dict:
    key = str(path)
    if key not in _cache:
        if not path.exists():
            _cache[key] = {}
        else:
            with open(path, "r", encoding="utf-8") as f:
                _cache[key] = json.load(f)
    return _cache[key]


def load_roots() -> list:
    return _load_json(DATA_DIR / "roots" / "roots.json").get("roots", [])


def find_root(query: str):
    query = query.strip()
    for r in load_roots():
        if query in (r.get("root", ""), r.get("letters", "")):
            return r
    for r in load_roots():
        if query.lower() in r.get("meaning", "").lower():
            return r
    return None


def find_term_files(query: str, limit: int = 5) -> list:
    """Ищет .md файлы в content/terminology/ по имени или содержимому."""
    query_low = query.lower()
    hits = []
    term_dir = CONTENT_DIR / "terminology"
    if not term_dir.exists():
        return hits
    for path in term_dir.glob("*.md"):
        if query_low in path.stem.lower():
            hits.append(path)
    if not hits:
        for path in term_dir.glob("*.md"):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if query_low in text.lower():
                hits.append(path)
            if len(hits) >= limit:
                break
    return hits[:limit]


def find_tanakh_verse_context(ref: str) -> list:
    """Ищет упоминания ссылки на стих (напр. 'Берешит 1:1') в content/tanakh/."""
    hits = []
    tanakh_dir = CONTENT_DIR / "tanakh"
    if not tanakh_dir.exists():
        return hits
    for path in tanakh_dir.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if ref in text:
            hits.append(path)
    return hits


def load_instruction(rel_path: str) -> str:
    path = INSTRUCTIONS_DIR / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\-]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-") or "task"
