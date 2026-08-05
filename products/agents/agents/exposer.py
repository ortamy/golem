"""Разоблачитель: отмечает возможные сдвиги между образом и переводом."""
from .common import record


def expose(data):
    root = data.get("root") or {}
    meaning = root.get("meaning", "")
    return record(data, "exposer", exposures=[{
        "source": data.get("term", data["query"]),
        "translation": meaning or "не найдено в локальном словаре",
        "status": "требует проверки" if not root else "сопоставить с палео-образом",
    }])
