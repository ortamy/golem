"""Сборщик: формирует единый результат пайплайна."""
from .common import record


def collect(data):
    return record(data, "collector", result={
        "title": f"Исследование: {data.get('term', data['query'])}",
        "summary": data.get("critique") or data.get("editorial_note", "Материал собран."),
        "trace": data.get("trace", []),
        "data": {key: value for key, value in data.items() if key not in ("result", "trace")},
    })
