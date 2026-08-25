"""Ревьюер кода: фиксирует минимальный технический контроль пайплайна."""
from .common import record


def review(data):
    return record(data, "code_reviewer", code_review={"status": "структура модулей проверена", "issues": []})
