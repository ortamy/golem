"""Пайплайн: Шмита-сброс (цикл).

Виток: Редактор → Критик → Проверяющий → [Сход].
Каждые 2 витка — «шмита»: накопленный шум прощается, ключевые поля
сохраняются. Циклы освобождения вместо вечного повторения (MECHANISMS.md).
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
                    converge_step=converge, max_iterations=6,
                    shmita_every=2, reset_fields=["gaps", "exposures", "horizon"])
    return collect(data)