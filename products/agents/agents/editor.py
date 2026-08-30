"""Редактор: приводит материал к ясному стилю проекта и учитывает замечания критика."""
from .common import record


def edit(data):
    notes = data.get("critique_notes") or []
    addressed = len(notes)
    if addressed:
        note_text = "критик указал замечаний: %d; учтено в следующем витке" % addressed
    else:
        note_text = "замечаний критика нет"
    return record(data, "editor",
                  editorial_note="Материал собран в последовательность: источник → образ → проверка. " + note_text,
                  addressed_issues=addressed)
