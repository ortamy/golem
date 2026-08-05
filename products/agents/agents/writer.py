"""Технический писатель: оформляет исследование для Markdown-документации."""
from .common import record


def write(data):
    return record(data, "writer", document={
        "heading": data.get("query", "Исследование"),
        "sections": ["Вопрос", "Источники", "Палео-образ", "Проверки", "Ограничения"],
    })
