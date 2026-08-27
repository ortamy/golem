"""Оркестратор: маршрутизирует запрос в один из трёх пайплайнов."""
from pipelines.word_analyzer import run as run_word_analyzer
from pipelines.verse_comparator import run as run_verse_comparator
from pipelines.research_builder import run as run_research_builder


ROUTES = {
    "разбери слово": run_word_analyzer,
    "сравни стих": run_verse_comparator,
    "собери исследование": run_research_builder,
}

PIPELINES = {
    "word_analyzer": run_word_analyzer,
    "verse_comparator": run_verse_comparator,
    "research_builder": run_research_builder,
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


def run_pipeline(pipeline_id: str, query: str):
    """Запускает цепочку по её явному идентификатору."""
    if not query or not query.strip():
        raise ValueError("Запрос не может быть пустым")
    pipeline = PIPELINES.get(pipeline_id)
    if pipeline is None:
        raise ValueError("Неизвестный пайплайн: " + pipeline_id)
    return pipeline(query)
