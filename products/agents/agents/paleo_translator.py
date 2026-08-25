"""Переводчик палео-иврита: собирает буквы в образ, не в абстракцию."""
from .common import record


def translate(data):
    root = data.get("root") or {}
    return record(data, "paleo_translator", paleo_image={
        "letters": root.get("letters", ""),
        "meaning": root.get("meaning", "образ не найден; нужна ручная сборка"),
        "method": "последовательность функций букв",
    })
