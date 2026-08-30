"""Пайплайн: Аудит исследования.

Цепочка: Ревьюер → Критик → Проверяющий → Редактор → Сборщик.
"""
from agents.common import packet
from agents.code_reviewer import review
from agents.critic import critique
from agents.verifier import verify
from agents.editor import edit
from agents.collector import collect
from pipelines.core import run_steps


def run(query):
    data = packet(query, term=query.strip())
    data["verify_targets"] = ["query", "critique", "verification"]
    return run_steps(data, (review, critique, verify, edit, collect))