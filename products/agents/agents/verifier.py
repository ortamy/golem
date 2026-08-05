"""Проверяющий: валидирует обязательные поля результата."""
from .common import record


def verify(data):
    required = ["query", "trace"]
    missing = [key for key in required if not data.get(key)]
    return record(data, "verifier", verification={"valid": not missing, "missing": missing})
