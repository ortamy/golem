"""Семитолог: фиксирует семитские параллели без подмены источников."""
from .common import record
from utils.context import root_letters


def compare(data):
    root = data.get("root") or {}
    letters = root_letters(root) or data.get("term", "")
    return record(data, "semitologist", semitic_parallels={
        "аккадский": "Требует сверки по словарю; автоматический вывод не выполняется.",
        "арамейский": "Требует сверки по корпусу; автоматический вывод не выполняется.",
        "letters": letters,
    })
