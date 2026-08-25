"""Пайплайн: Компаратор → Критик → Редактор → Сборщик."""
from agents.common import packet
from agents.comparator import compare
from agents.critic import critique
from agents.editor import edit
from agents.collector import collect


def run(query):
    data = packet(query)
    for step in (compare, critique, edit, collect):
        data = step(data)
    return data
