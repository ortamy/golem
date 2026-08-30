"""Пайплайн: Реконструкция стиха.

Цепочка: Компаратор → Переводчик палео → Разоблачитель → Проверяющий → Сборщик.
"""
from agents.common import packet
from agents.comparator import compare
from agents.paleo_translator import translate
from agents.exposer import expose
from agents.verifier import verify
from agents.collector import collect
from pipelines.core import run_steps


def run(query):
    data = packet(query)
    data["verify_targets"] = ["query", "witnesses", "paleo_image", "exposures"]
    return run_steps(data, (compare, translate, expose, verify, collect))