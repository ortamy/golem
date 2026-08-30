"""Общие контракты для простых, тестируемых агентов."""
from copy import deepcopy
from typing import Any, Dict


def packet(query: str, **values: Any) -> Dict[str, Any]:
    result = {"query": query, "trace": [], "agentTrace": []}
    result.update(values)
    return result


def record(data: Dict[str, Any], agent: str, **values: Any) -> Dict[str, Any]:
    input_data = {key: value for key, value in data.items() if key not in ("trace", "agentTrace", "result")}
    data.update(values)
    data.setdefault("trace", []).append(agent)
    data.setdefault("agentTrace", []).append({
        "agentId": agent,
        "iteration": data.get("iteration", 0),  # номер витка: 0 — линейная цепочка, 1..N — цикл
        "status": "done",
        "input": deepcopy(input_data),
        "observations": [{"field": key, "value": deepcopy(value)} for key, value in values.items()],
        "decisions": [],
        "hypotheses": [],
        "limitations": [],
        "output": deepcopy(values),
    })
    return data
