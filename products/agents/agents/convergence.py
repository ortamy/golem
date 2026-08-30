"""Агент «Сход»: фиксирует, сходится ли цикл (эмет) или крутится впустую (Мавет)."""
import hashlib
import json

from .common import record


# Поля, по которым строится подпись витка. Палео-образ сравнивается без
# поля depth — иначе бесконечная рекурсия никогда бы не сошлась.
# context_wave намеренно не входит в подпись: он содержит iteration
# и меняется каждый виток даже при полностью стабильном контексте.
_SIGNATURE_FIELDS = (
    "term", "root", "exposures", "critique", "editorial_note", "verification",
    "sources", "semitic_parallels", "witnesses", "horizon", "gaps",
)


def _signature(data):
    """Компактная подпись витка по ключевым исследовательским полям."""
    payload = {}
    for key in _SIGNATURE_FIELDS:
        if key in data:
            payload[key] = data[key]
    paleo = data.get("paleo_image") or {}
    payload["paleo_image"] = {"letters": paleo.get("letters"), "meaning": paleo.get("meaning")}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def converge(data):
    iteration = data.get("iteration", 1)
    history = data.get("convergence_history") or []
    signature = _signature(data)

    previous = history[-1].get("_signature") if history else None
    changed = previous is not None and previous != signature
    fresh = changed or previous is None      # пришли новые улики
    stale = not changed and previous is not None  # повтор без изменений

    verification = data.get("verification") or {}
    valid = bool(verification.get("valid", True))

    if previous is None:
        # Первый виток не может быть «сошедшимся»: нужна минимум одна сверка.
        converged = False
    else:
        converged = valid and not changed

    if converged:
        status, note = "эмет", "Виток не принёс новых данных; поток сошёлся."
    elif stale and not valid:
        status, note = "Мавет", "Виток повторяется без валидности; нужен ручной разбор."
    elif fresh and changed:
        status, note = "поток", "Виток принёс свежие данные; продолжаем."
    else:
        status, note = "Тоху", "Неопределённое состояние; продолжаем наблюдение."

    return record(data, "convergence", convergence={
        "iteration": iteration,
        "converged": converged,
        "stalled": False,  # признак «Мавет»; в run_loop может стать True
        "delta": 0 if not changed else 1,
        "fresh_evidence_count": 1 if fresh and changed else 0,
        "status": status,
        "notes": note,
        "_signature": signature,
    }, converged=converged)