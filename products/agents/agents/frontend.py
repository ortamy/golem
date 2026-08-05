"""Заглушка фронтенд-разработчика для будущего UI Research Lab."""
from .common import record


def prepare(data):
    return record(data, "frontend_developer", frontend={"status": "контракт данных подготовлен"})
