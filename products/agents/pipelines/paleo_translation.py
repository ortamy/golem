"""Пайплайн: Обратный перевод.

Цепочка: Исследователь → Переводчик палео → Семитолог → Проверяющий → Редактор → Сборщик.
"""
from agents.common import packet
from agents.researcher import research
from agents.paleo_translator import translate
from agents.semitologist import compare as semitic_compare
from agents.verifier import verify
from agents.editor import edit
from agents.collector import collect
from pipelines.core import run_steps


def run(query):
    data = packet(query)
    data["verify_targets"] = ["term", "root", "paleo_image", "semitic_parallels"]
    return run_steps(data, (research, translate, semitic_compare, verify, edit, collect))