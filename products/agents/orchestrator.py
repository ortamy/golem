"""Оркестратор: маршрутизирует запрос в один из трёх пайплайнов."""
from pipelines.word_analyzer import run as run_word_analyzer
from pipelines.verse_comparator import run as run_verse_comparator
from pipelines.research_builder import run as run_research_builder


ROUTES = {
    "разбери слово": run_word_analyzer,
    "сравни стих": run_verse_comparator,
    "собери исследование": run_research_builder,
}


def select_pipeline(query: str):
    normalized = query.strip().lower()
    for phrase, pipeline in ROUTES.items():
        if normalized.startswith(phrase):
            return pipeline
    return run_research_builder


def dispatch(query: str):
    """Запускает выбранный пайплайн и возвращает JSON-совместимый словарь."""
    if not query or not query.strip():
        raise ValueError("Запрос не может быть пустым")
    return select_pipeline(query)(query)
