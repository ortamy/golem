"""Связной: передаёт контекст и расширяет горизонт (спираль Хук Свива)."""
from .common import record

WAVES = [
    "следующий корень по словарю",
    "следующий перевод",
    "следующий источник",
]


def relay(data):
    iteration = data.get("iteration", 1)
    if iteration <= len(WAVES):
        wave = WAVES[iteration - 1]
    else:
        wave = "горизонт исчерпан"

    sources = data.get("sources") or []
    added = wave == "горизонт исчерпан" or bool(sources) or "следующий источник" not in wave
    horizon = list(data.get("horizon") or [])
    # Сатурация: не дублируем одинаковые волны — когда горизонт исчерпан,
    # подпись витка стабилизируется и цикл честно объявляет Шаббат.
    if not horizon or horizon[-1].get("wave") != wave:
        horizon.append({"iteration": iteration, "wave": wave, "added": added})

    return record(data, "liaison", context_wave={"iteration": iteration, "wave": wave, "added": added},
                  horizon=horizon, handoff={"ready": True, "fields": sorted(data.keys())})
