"""Пайплайн: Самокритика (цикл).

Виток: Редактор → Критик → Проверяющий → [Сход].
Остановка: валидный виток без новых замечаний («Шаббат»).
"""
from agents.common import packet
from agents.editor import edit
from agents.critic import critique
from agents.verifier import verify
from agents.convergence import converge
from agents.collector import collect
from pipelines.core import run_loop


def run(query):
    data = packet(query, term=query.strip())
    data["verify_targets"] = ["query", "critique", "editorial_note"]
    data = run_loop(data, cycle_steps=(edit, critique, verify),
                    converge_step=converge, max_iterations=5)
    return collect(data)