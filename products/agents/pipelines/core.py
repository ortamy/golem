"""Движок пайплайнов: линейные цепочки и циклы с обратной связью.

Контракт агента: функция `data -> data`. Агент обязан вернуть словарь.
Пустой результат (`None` или `{}`) останавливает цепочку — пайплайн
не молотит впустую. Циклы дополнительно управляются агентом сходимости:
он обязан положить `data["convergence"] = {"converged": bool, ...}`.
"""
from copy import deepcopy
from typing import Any, Callable, Dict, Iterable, Optional

Packet = Dict[str, Any]
Step = Callable[[Packet], Optional[Packet]]

# Поля, которые запрещено трогать даже «шмитой» (ядра цикла).
_PROTECTED = {
    "query", "term", "root", "trace", "agentTrace", "iteration",
    "convergence_history", "result", "shmita_resets",
}


def is_empty(data):
    """Пустой результат агента — признак остановки пайплайна."""
    return data is None or (isinstance(data, dict) and not data)


def run_steps(data: Packet, steps: Iterable[Step]) -> Packet:
    """Линейная цепочка. Останавливается, если шаг вернул пустой результат."""
    for step in steps:
        data = step(data)
        if is_empty(data):
            return data
    return data


def _shmita_reset(data: Packet, reset_fields: Iterable[str]) -> Packet:
    """Шмита-сброс: прощает накопленный «долг» цикла.

    Удаляет только поля из `reset_fields` (например, растущие карты
    `gaps`/`exposures`/`horizon`). Ключевые поля цикла сохраняются,
    поэтому подпись витка стабилизируется и цикл может сойтись.
    """
    for key in reset_fields:
        if key not in _PROTECTED:
            data.pop(key, None)
    data["shmita_resets"] = data.get("shmita_resets", 0) + 1
    return data


def run_loop(
    data: Packet,
    *,
    cycle_steps: Iterable[Step],
    converge_step: Step,
    max_iterations: int = 5,
    shmita_every: Optional[int] = None,
    reset_fields: Optional[Iterable[str]] = None,
) -> Packet:
    """Циклическая цепочка.

    `cycle_steps` — шаги одного витка; `converge_step` — агент сходимости,
    кладёт `data["convergence"]` и `data["converged"]`.
    `max_iterations` — защита от вечного круга: если сходимости нет,
    цикл честно помечается как «Мавет» (остановка потока без результата).
    `shmita_every` — каждые N витков выполняется «шмита-сброс»:
    прощаются поля из `reset_fields`, растущие без предела.
    """
    data["iteration"] = 0
    data["converged"] = False
    max_iterations = max(1, int(max_iterations))
    if not isinstance(cycle_steps, (tuple, list)):
        cycle_steps = [cycle_steps]
    reset_fields = tuple(reset_fields or ())

    history: list = []
    for iteration in range(1, max_iterations + 1):
        data["iteration"] = iteration
        if shmita_every and iteration > 1 and iteration % shmita_every == 0:
            data = _shmita_reset(data, reset_fields)
        for step in cycle_steps:
            data = step(data)
            if is_empty(data):
                return data
        data = converge_step(data)
        if is_empty(data):
            return data

        snapshot = deepcopy(data.get("convergence") or {})
        snapshot["iteration"] = iteration
        history.append(snapshot)
        data["convergence_history"] = history

        if data.get("converged"):
            break
    else:
        # Витки исчерпаны, сходимости нет — помечаем честно, без бесконечного круга.
        convergence = data.setdefault("convergence", {})
        convergence.update({
            "converged": False,
            "stalled": True,
            "notes": "Цикл не сошёлся за %d витков — Мавет. Требуется ручной разбор." % max_iterations,
        })
        data["converged"] = False
    return data