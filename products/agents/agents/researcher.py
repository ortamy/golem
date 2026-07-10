#!/usr/bin/env python3
# products/agents/agents/researcher.py — агент-исследователь: разбор корней, стихов, терминов
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from crewai import Agent, Task
from crewai.tools import tool

from agents.context import (
    find_root,
    find_term_files,
    find_tanakh_verse_context,
    load_instruction,
)

RESEARCHER_MODEL = os.environ.get("RESEARCHER_MODEL", "anthropic/claude-3-5-sonnet-latest")
METHODS_TEXT = load_instruction("exposure/exposure-linguistic-methods.md")


@tool("Найти корень в data/roots.json")
def lookup_root(query: str) -> str:
    """Ищет трёхбуквенный корень в data/roots.json по корню, буквам или значению.
    Возвращает найденную запись (корень, буквы, палео-образы, значение, термины,
    пример стиха, примечание) или сообщение, что корень не найден."""
    entry = find_root(query)
    if not entry:
        return f"Корень '{query}' не найден в data/roots.json."
    return (
        f"root={entry.get('root')} letters={entry.get('letters')} "
        f"paleo={entry.get('paleo')} meaning={entry.get('meaning')} "
        f"terms={entry.get('terms')} example={entry.get('example')} "
        f"note={entry.get('note')}"
    )


@tool("Найти статьи термина в content/terminology")
def lookup_terminology(query: str) -> str:
    """Ищет .md файлы в content/terminology/ по имени слова или содержимому.
    Возвращает содержимое найденных файлов (до 3) или сообщение об отсутствии."""
    paths = find_term_files(query, limit=3)
    if not paths:
        return f"Файлы термина '{query}' не найдены в content/terminology/."
    chunks = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        chunks.append(f"### {path.name}\n{text[:4000]}")
    return "\n\n---\n\n".join(chunks)


@tool("Найти контекст стиха в content/tanakh")
def lookup_verse_context(ref: str) -> str:
    """Ищет упоминания ссылки на стих (например 'Берешит 1:1') в файлах content/tanakh/.
    Возвращает список файлов, где стих упоминается."""
    paths = find_tanakh_verse_context(ref)
    if not paths:
        return f"Упоминания стиха '{ref}' не найдены в content/tanakh/."
    return "Найдено в файлах: " + "; ".join(str(p) for p in paths[:10])


def build_researcher_agent() -> Agent:
    return Agent(
        role="Агент-исследователь Голема",
        goal=(
            "Разобрать заданный корень, стих или термин по методологии Голема: "
            "палео-образы → трёхбуквенный корень → смысл, с опорой на 10 методов "
            "разоблачения (этимологическая хирургия, палеографическая экспертиза, "
            "сравнительная семитология и др.)."
        ),
        backstory=(
            "Ты — исследователь ТаНаХа на иврите, работающий строго по методологии "
            "проекта «Голем»: ТаНаХ на иврите — единственный источник, палео-иврит "
            "первичен, все переводы — цепочка подмен. Ты пишешь черновики исследований "
            "без религионимов, без греческих философем, без таблиц — только списки. "
            "Твои инструкции по методам разоблачения:\n\n" + METHODS_TEXT[:6000]
        ),
        tools=[lookup_root, lookup_terminology, lookup_verse_context],
        llm=RESEARCHER_MODEL,
        verbose=True,
    )


def build_researcher_task(agent: Agent, query: str) -> Task:
    return Task(
        description=(
            f"Задание: «{query}» (корень, стих или термин ТаНаХа).\n\n"
            "Проведи разбор по методологии Голема:\n"
            "1. Найди корень в data/roots.json (инструмент lookup_root) или, если "
            "дан стих/термин — соответствующие файлы (lookup_terminology, "
            "lookup_verse_context).\n"
            "2. Разбери палео-образы букв корня (буква = образ, не звук).\n"
            "3. Собери 3-5 стихов ТаНаХа, подтверждающих смысл (иврит + "
            "транслитерация + буквальный перевод).\n"
            "4. Укажи, какой метод разоблачения (из 10) применён и почему.\n"
            "5. Не используй религионимы и греческие философемы в собственной речи.\n\n"
            "Выведи готовый черновик в формате Markdown с разделами: "
            "## ЭТИМОЛОГИЯ, ## ПАЛЕО-ИВРИТ, ## КОНТЕКСТ ТАНАХА, ## ВЫВОД."
        ),
        expected_output=(
            "Черновик исследования в Markdown с разделами ЭТИМОЛОГИЯ, ПАЛЕО-ИВРИТ, "
            "КОНТЕКСТ ТАНАХА (минимум 3 стиха с ивритом/транслитерацией/переводом), "
            "ВЫВОД."
        ),
        agent=agent,
    )
