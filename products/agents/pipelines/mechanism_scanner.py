"""Пайплайн: Сканер подмен.

Цепочка: Исследователь → Разоблачитель → Критик → Сборщик.
"""
from agents.common import packet
from agents.researcher import research
from agents.exposer import expose
from agents.critic import critique
from agents.collector import collect
from pipelines.core import run_steps


def run(query):
    data = packet(query)
    return run_steps(data, (research, expose, critique, collect))