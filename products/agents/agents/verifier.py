"""Проверяющий: валидирует обязательные поля результата."""
from .common import record

DEFAULT_REQUIRED = ["query", "trace"]


def verify(data):
    targets = data.get("verify_targets") or DEFAULT_REQUIRED
    missing = [key for key in targets if not data.get(key)]
    # Словарь verification намеренно не содержит iteration: подпись витка
    # должна оставаться стабильной, иначе цикл никогда не сойдётся.
    return record(data, "verifier", verification={
        "valid": not missing,
        "missing": missing,
    })
