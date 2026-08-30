"""Пайплайн: Карантин пропусков (цикл).

Виток: Исследователь → Разоблачитель → Проверяющий → [Сход].
Пропуски корпуса не отбрасываются, а копятся в карту до сатурации.
"""
from agents.common import packet
from agents.researcher import research
from agents.exposer import expose
from agents.verifier import verify
from agents.convergence import converge
from agents.collector import collect
from pipelines.core import run_loop


def run(query):
    data = packet(query, gaps=[])
    data["verify_targets"] = ["query"]
    data = run_loop(data, cycle_steps=(research, expose, verify),
                    converge_step=converge, max_iterations=4)
    return collect(data)