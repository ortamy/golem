"""Переводчик палео-иврита: собирает буквы в образ; на повторе перечитывает образ как термин."""
from .common import record
from utils.context import find_root


def translate(data):
    root = data.get("root") or {}
    iteration = data.get("iteration", 1)
    source = data.get("term", data["query"])

    if data.get("recursive") and iteration > 1:
        # Мидраш-рекурсия: входим в собственный вывод и ищем в нём новый корень.
        previous = data.get("paleo_image") or {}
        source = (previous.get("meaning") or "").strip() or source
        found = find_root(source)
        if found:
            root = found
            source = found.get("root", source)

    return record(data, "paleo_translator", paleo_image={
        "letters": root.get("letters", ""),
        "meaning": root.get("meaning", "образ не найден; нужна ручная сборка"),
        "method": "последовательность функций букв",
        "depth": iteration if data.get("recursive") and iteration > 1 else 0,
        "source": source,
    })
