"""Связной: передаёт контекст между исследовательскими ролями."""
from .common import record


def relay(data):
    return record(data, "liaison", handoff={"ready": True, "fields": sorted(data.keys())})
