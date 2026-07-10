#!/usr/bin/env python3
# products/agents/agents/exposer.py — агент-разоблачитель: поиск подмен в переводах
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from crewai import Agent, Task
from crewai.tools import tool

from agents.context import load_instruction, DATA_DIR
import json

EXPOSER_MODEL = os.environ.get("EXPOSER_MODEL", "openai/gpt-4o-mini")
DISTORTIONS_TEXT = load_instruction("exposure/exposure-distortions.md")
DICTIONARY_TEXT = load_instruction("exposure/exposure-dictionary.md")


@tool("Найти запись в словаре разоблачений")
def lookup_exposure_dictionary(term: str) -> str:
    """Ищет слово в instructions/exposure/exposure-dictionary.md — словаре
    восстановленных ивритских терминов (26+ слов: ангел, вера, жертва и др.).
    Возвращает найденный фрагмент словаря или сообщение об отсутствии."""
    if not DICTIONARY_TEXT:
        return "Файл exposure-dictionary.md не найден."
    term_low = term.strip().lower()
    blocks = DICTIONARY_TEXT.split("\n### ")
    hits = [b for b in blocks if term_low in b.lower()[:200]]
    if not hits:
        return f"Слово '{term}' не найдено в exposure-dictionary.md."
    return "\n### ".join(hits[:2])[:4000]


@tool("Найти известные подмены в data/exposures.json")
def lookup_known_exposures(query: str) -> str:
    """Ищет уже зафиксированные разоблачения в data/exposures.json по названию
    или ивритскому термину. Возвращает найденные записи (title, hebrew_term,
    substitution, chain) или сообщение об отсутствии."""
    path = DATA_DIR / "exposures.json"
    if not path.exists():
        return "data/exposures.json не найден."
    data = json.loads(path.read_text(encoding="utf-8"))
    query_low = query.strip().lower()
    hits = [
        e for e in data.get("exposures", [])
        if query_low in e.get("title", "").lower()
        or query_low in e.get("hebrew_term", "").lower()
    ]
    if not hits:
        return f"Подмены по запросу '{query}' не найдены в data/exposures.json."
    return json.dumps(hits, ensure_ascii=False, indent=2)


def build_exposer_agent() -> Agent:
    return Agent(
        role="Агент-разоблачитель Голема",
        goal=(
            "Найти подмены в переводах заданного стиха: сравнить масоретский текст "
            "(ТМ), Септуагинту (LXX) и Синодальный перевод, выявить греческие и "
            "латинские философемы, предложить ивритскую замену для каждой подмены."
        ),
        backstory=(
            "Ты — разоблачитель системы подмен смыслов ТаНаХа. Ты знаешь 9 типов "
            "искажений (подмена категории, юридизация, психологизация, сдвиг от "
            "действия к эмоции, абстракция, сужение смысла, дуализация, кастрация "
            "смысла, вавилонизация) и работаешь строго по словарю восстановленных "
            "терминов. Твои инструкции:\n\n"
            + DISTORTIONS_TEXT[:5000] + "\n\n" + DICTIONARY_TEXT[:3000]
        ),
        tools=[lookup_exposure_dictionary, lookup_known_exposures],
        llm=EXPOSER_MODEL,
        verbose=True,
    )


def build_exposer_task(agent: Agent, verse_ref: str) -> Task:
    return Task(
        description=(
            f"Стих: «{verse_ref}».\n\n"
            "Найди подмены в переводах этого стиха:\n"
            "1. Приведи масоретский текст (ТМ) на иврите, если знаешь его точно.\n"
            "2. Сравни с Септуагинтой (LXX) и Синодальным переводом — какие слова "
            "заменены, какой тип искажения применён (из 9).\n"
            "3. Используй инструмент lookup_exposure_dictionary для каждого "
            "подозрительного слова, чтобы найти восстановленный ивритский термин.\n"
            "4. Используй lookup_known_exposures, чтобы проверить, есть ли уже "
            "зафиксированная подмена по этой теме.\n"
            "5. Для каждой найденной подмены укажи: слово в Синодальном → "
            "ивритский оригинал → правильное значение → тип искажения."
        ),
        expected_output=(
            "Список подмен в формате: 'Синодальное слово → иврит (транслит) → "
            "восстановленное значение → тип искажения (из 9)'. Минимум 1 подмена, "
            "если стих короткий — может быть меньше."
        ),
        agent=agent,
    )
