"""Компаратор текстовых свидетелей."""
from .common import record


def compare(data):
    return record(data, "comparator", witnesses={
        "LXX": "не загружен; нужен локальный корпус",
        "ТМ": "не загружен; нужен локальный корпус",
        "Кумран": "не загружен; нужен локальный корпус",
    })
