#!/usr/bin/env python3
"""Общие утилиты для агентов Голема."""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "products" / "website" / "apps" / "researchlab" / "data"
CONTENT_DIR = REPO_ROOT / "products" / "website" / "src" / "content" / "md"
DOCS_DIR = REPO_ROOT / "docs"
_cache = {}

TERM_DIRS = (
    CONTENT_DIR / "bashah" / "terminology",
    CONTENT_DIR / "researches",
    CONTENT_DIR / "teachings",
)


def _load_json(path: Path):
    key = str(path)
    if key not in _cache:
        if not path.exists():
            _cache[key] = {}
        else:
            with path.open(encoding="utf-8") as handle:
                _cache[key] = json.load(handle)
    return _cache[key]


def root_letters(root: dict) -> str:
    """Буквы корня: поле letters либо склейка paleo-глифов."""
    letters = root.get("letters")
    if isinstance(letters, str) and letters.strip():
        return letters
    paleo = root.get("paleo")
    if isinstance(paleo, list):
        return "".join(str(item) for item in paleo if item)
    if isinstance(paleo, str):
        return paleo
    return str(root.get("root") or "")


def _normalize_root(root: dict) -> dict:
    if not isinstance(root, dict):
        return root
    normalized = dict(root)
    normalized["letters"] = root_letters(normalized)
    return normalized


def load_roots() -> list:
    payload = _load_json(DATA_DIR / "roots" / "roots.json")
    roots = payload if isinstance(payload, list) else payload.get("roots", [])
    return [_normalize_root(root) for root in roots]


def find_root(query: str):
    query = (query or "").strip()
    if not query:
        return None
    query_low = query.lower()
    roots = load_roots()
    for root in roots:
        haystack = (
            root.get("root", ""),
            root.get("letters", ""),
            root.get("translit", ""),
            "".join(root.get("paleo") or []) if isinstance(root.get("paleo"), list) else "",
        )
        if query in haystack or query_low in {str(item).lower() for item in haystack}:
            return root
    for root in roots:
        meaning = str(root.get("meaning") or "").lower()
        image = str(root.get("image") or "").lower()
        if query_low and (query_low in meaning or query_low in image):
            return root
    return None


def find_term_files(query: str, limit: int = 5) -> list:
    """Ищет терминологические Markdown-файлы по имени или содержимому."""
    query_low = (query or "").strip().lower()
    if not query_low:
        return []
    hits = []
    seen = set()
    for term_dir in TERM_DIRS:
        if not term_dir.exists():
            continue
        for path in term_dir.rglob("*.md"):
            if path.name.upper() in {"README.MD", "INDEX.MD"}:
                continue
            if query_low in path.stem.lower():
                key = str(path)
                if key not in seen:
                    hits.append(path)
                    seen.add(key)
            if len(hits) >= limit:
                return hits[:limit]
    if hits:
        return hits[:limit]
    for term_dir in TERM_DIRS:
        if not term_dir.exists():
            continue
        for path in term_dir.rglob("*.md"):
            try:
                if query_low in path.read_text(encoding="utf-8", errors="ignore").lower():
                    hits.append(path)
            except OSError:
                continue
            if len(hits) >= limit:
                return hits[:limit]
    return hits[:limit]


def find_tanakh_verse_context(ref: str) -> list:
    """Ищет файлы ТаНаХа, содержащие ссылку на стих."""
    tanakh_dir = CONTENT_DIR / "tanakh"
    if not tanakh_dir.exists() or not ref:
        return []
    hits = []
    for path in tanakh_dir.rglob("*.md"):
        try:
            if ref in path.read_text(encoding="utf-8", errors="ignore"):
                hits.append(path)
        except OSError:
            continue
    return hits


def load_instruction(rel_path: str) -> str:
    """Читает методологический документ из docs/ (исторический путь instructions/ больше не существует)."""
    rel = (rel_path or "").replace("\\", "/").lstrip("/")
    if not rel:
        return ""
    candidates = [
        DOCS_DIR / rel,
        DOCS_DIR / "06-METHODOLOGY" / Path(rel).name,
        DOCS_DIR / "04-STANDARD" / Path(rel).name,
        DOCS_DIR / "00-START" / Path(rel).name,
    ]
    for path in candidates:
        if path.is_file():
            return path.read_text(encoding="utf-8", errors="ignore")
    return ""


def slugify(text: str) -> str:
    text = re.sub(r"[^a-z0-9\-]+", "-", text.strip().lower())
    return re.sub(r"-+", "-", text).strip("-") or "task"
