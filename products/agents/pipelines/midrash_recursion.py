"""Пайплайн: Мидраш-рекурсия (цикл).

Виток: Исследователь → Переводчик палео → Проверяющий → [Сход].
Переводчик входит в собственный вывод и перечитывает образ как термин;
остановка — стабилизация палео-образа.
"""
from agents.common import packet
from agents.researcher import research
from agents.paleo_translator import translate
from agents.verifier import verify
from agents.convergence import converge
from agents.collector import collect
from pipelines.core import run_loop


def run(query):
    data = packet(query, recursive=True)
    data["verify_targets"] = ["query", "paleo_image"]
    data = run_loop(data, cycle_steps=(research, translate, verify),
                    converge_step=converge, max_iterations=4)
    return collect(data)