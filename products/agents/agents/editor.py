"""Редактор: приводит промежуточный материал к ясному стилю проекта."""
from .common import record


def edit(data):
    return record(data, "editor", editorial_note="Материал собран в последовательность: источник → образ → проверка.")
