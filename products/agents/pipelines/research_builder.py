"""Пайплайн: Архитектор потока → Связной → Технический писатель → Сборщик."""
from agents.common import packet
from agents.flow_architect import design
from agents.liaison import relay
from agents.writer import write
from agents.collector import collect


def run(query):
    data = packet(query)
    for step in (design, relay, write, collect):
        data = step(data)
    return data
