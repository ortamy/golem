"""Исследователь: извлекает слово, корень и локальные источники."""
import re
from .common import record
from utils.context import find_root, find_term_files


def research(data):
    query = data["query"]
    match = re.search(r"(?:слово|корень)\s+(.+)$", query, re.I)
    term = (match.group(1) if match else query).strip()
    root = find_root(term)
    return record(data, "researcher", term=term, root=root,
                  sources=[str(path) for path in find_term_files(term)])
