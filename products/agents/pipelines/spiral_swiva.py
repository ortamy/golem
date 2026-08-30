"""Пайплайн: Хук Свива (спираль расширения).

Виток: Связной → Исследователь → Переводчик палео → Проверяющий → [Сход].
Каждый виток добавляет следующий контекст; остановка — сатурация,
когда горизонт исчерпан и новый виток не приносит улик.
"""
from agents.common import packet
from agents.liaison import relay
from agents.researcher import research
from agents.paleo_translator import translate
from agents.verifier import verify
from agents.convergence import converge
from agents.collector import collect
from pipelines.core import run_loop


def run(query):
    data = packet(query, horizon=[])
    data["verify_targets"] = ["query", "horizon"]
    data = run_loop(data, cycle_steps=(relay, research, translate, verify),
                    converge_step=converge, max_iterations=6)
    return collect(data)