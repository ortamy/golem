"""Семитолог: фиксирует семитские параллели без подмены источников."""
from .common import record


def compare(data):
    root = data.get("root") or {}
    letters = root.get("letters") or root.get("root") or data.get("term", "")
    return record(data, "semitologist", semitic_parallels={
        "аккадский": "Требует сверки по словарю; автоматический вывод не выполняется.",
        "арамейский": "Требует сверки по корпусу; автоматический вывод не выполняется.",
        "letters": letters,
    })
