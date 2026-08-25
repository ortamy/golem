"""Общие контракты для простых, тестируемых агентов."""
from typing import Any, Dict


def packet(query: str, **values: Any) -> Dict[str, Any]:
    result = {"query": query, "trace": []}
    result.update(values)
    return result


def record(data: Dict[str, Any], agent: str, **values: Any) -> Dict[str, Any]:
    data.update(values)
    data.setdefault("trace", []).append(agent)
    return data
