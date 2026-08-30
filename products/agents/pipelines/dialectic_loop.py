"""Пайплайн: Диалектическая петля.

Виток: Компаратор (тезис) → Критик (антитезис) → Проверяющий → [Сход].
Остановка: расхождения перестали расти — фиксируется либо эмет,
либо задокументированное неустранимое противоречие (Шеол).
"""
from agents.common import packet
from agents.comparator import compare
from agents.critic import critique
from agents.verifier import verify
from agents.convergence import converge
from agents.collector import collect
from pipelines.core import run_loop


def run(query):
    data = packet(query, term=query.strip())
    data["verify_targets"] = ["query", "witnesses", "critique"]
    data = run_loop(data, cycle_steps=(compare, critique, verify),
                    converge_step=converge, max_iterations=4)
    return collect(data)