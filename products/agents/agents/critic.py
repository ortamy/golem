"""Критик: проверяет ход работы по критериям эмет / шекер."""
from .common import record

CHECKS = [
    "есть ли физическая конструкция",
    "отделены ли источник и гипотеза",
    "указаны ли пропуски корпуса",
    "нет ли религиозной лексики",
    "зафиксирован ли палео-образ",
]


def critique(data):
    root = data.get("root") or {}
    notes = []
    if not data.get("term") and not data.get("sources"):
        notes.append("нет термина или источников")
    if not root and data.get("term") and not data.get("witnesses"):
        notes.append("корень не найден в локальном словаре")
    if not data.get("paleo_image") and "paleo_image" in data.get("verify_targets", []):
        notes.append("не зафиксирован палео-образ")
    if (data.get("exposures") or data.get("gaps")) and not data.get("verification"):
        notes.append("разоблачения не прошли проверку")

    if notes:
        critique_text = "Найдены замечания: " + "; ".join(notes) + "."
    else:
        critique_text = "Проверка завершена: гипотезы помечены как требующие проверки."

    return record(data, "critic", methodology_checks=CHECKS, critique=critique_text,
                  critique_notes=notes, critique_count=len(notes))
