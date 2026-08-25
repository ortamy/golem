"""Архитектор потока: задаёт порядок этапов исследования."""
from .common import record


def design(data):
    return record(data, "flow_architect", flow=["question", "evidence", "paleo_image", "critique", "report"])
