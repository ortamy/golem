"""Заглушка AI-инженера: провайдер подключается только при наличии ключа."""
from .common import record


def prepare(data):
    return record(data, "ai_engineer", ai={"provider": "local", "status": "детерминированный режим"})
