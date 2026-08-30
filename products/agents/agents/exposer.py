"""Разоблачитель: отмечает сдвиги между образом и переводом, копит карту пропусков."""
from .common import record


def expose(data):
    root = data.get("root") or {}
    meaning = root.get("meaning", "")
    term = data.get("term", data["query"])
    exposures = [{
        "source": term,
        "translation": meaning or "не найдено в локальном словаре",
        "status": "требует проверки" if not root else "сопоставить с палео-образом",
    }]

    gaps = list(data.get("gaps") or [])
    if not root:
        gaps.append({"source": term, "cause": "нет записи в roots.json"})
    sources = data.get("sources") or []
    for path in sources:
        if not str(path).strip():
            gaps.append({"source": term, "cause": "источник пуст"})
    # Разоблачение уникальных пропусков, чтобы карантин не задваивал карту.
    unique_gaps = []
    seen = set()
    for gap in gaps:
        key = (gap.get("source"), gap.get("cause"))
        if key not in seen:
            unique_gaps.append(gap)
            seen.add(key)

    return record(data, "exposer", exposures=exposures, gaps=unique_gaps,
                  fresh_gap_count=len(unique_gaps))
