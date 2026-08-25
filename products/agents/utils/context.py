#!/usr/bin/env python3
"""Общие утилиты для агентов Голема."""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
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
            with path.open(encoding="utf-8") as handle:
                _cache[key] = json.load(handle)
    return _cache[key]


def load_roots() -> list:
    payload = _load_json(DATA_DIR / "roots" / "roots.json")
    # В проекте встречаются оба формата: массив корней и объект с полем roots.
    return payload if isinstance(payload, list) else payload.get("roots", [])


def find_root(query: str):
    query = query.strip()
    for root in load_roots():
        if query in (root.get("root", ""), root.get("letters", "")):
            return root
    for root in load_roots():
        if query.lower() in root.get("meaning", "").lower():
            return root
    return None


def find_term_files(query: str, limit: int = 5) -> list:
    """Ищет терминологические Markdown-файлы по имени или содержимому."""
    term_dir = CONTENT_DIR / "terminology"
    if not term_dir.exists():
        return []
    query_low = query.lower()
    hits = [path for path in term_dir.glob("*.md") if query_low in path.stem.lower()]
    if not hits:
        for path in term_dir.glob("*.md"):
            try:
                if query_low in path.read_text(encoding="utf-8", errors="ignore").lower():
                    hits.append(path)
            except OSError:
                continue
            if len(hits) >= limit:
                break
    return hits[:limit]


def find_tanakh_verse_context(ref: str) -> list:
    """Ищет файлы ТаНаХа, содержащие ссылку на стих."""
    tanakh_dir = CONTENT_DIR / "tanakh"
    if not tanakh_dir.exists():
        return []
    return [path for path in tanakh_dir.rglob("*.md")
            if ref in path.read_text(encoding="utf-8", errors="ignore")]


def load_instruction(rel_path: str) -> str:
    path = INSTRUCTIONS_DIR / rel_path
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def slugify(text: str) -> str:
    text = re.sub(r"[^a-z0-9\-]+", "-", text.strip().lower())
    return re.sub(r"-+", "-", text).strip("-") or "task"
