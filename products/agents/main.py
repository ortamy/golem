#!/usr/bin/env python3
# products/agents/main.py — точка входа: запуск цепочки researcher → exposer → collector
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from crewai import Crew, Process

from agents.context import CONTENT_DIR, slugify
from agents.researcher import build_researcher_agent, build_researcher_task
from agents.exposer import build_exposer_agent, build_exposer_task
from agents.collector import assemble_markdown, save_output

DEFAULT_OUTPUT_DIR = CONTENT_DIR / "researches" / "agent-drafts"


def run_pipeline(query: str, output_dir: Path = DEFAULT_OUTPUT_DIR) -> Path:
    """Запускает цепочку researcher → exposer → collector для заданного корня/стиха/термина."""
    researcher = build_researcher_agent()
    research_task = build_researcher_task(researcher, query)

    exposer = build_exposer_agent()
    exposure_task = build_exposer_task(exposer, query)

    crew = Crew(
        agents=[researcher, exposer],
        tasks=[research_task, exposure_task],
        process=Process.sequential,
        verbose=True,
    )
    crew.kickoff()

    research_result = str(research_task.output) if research_task.output else ""
    exposure_result = str(exposure_task.output) if exposure_task.output else ""

    markdown = assemble_markdown(query, research_result, exposure_result)
    slug = slugify(query)
    return save_output(markdown, output_dir, slug)


def main():
    parser = argparse.ArgumentParser(
        description="Мульти-агентная система Голема: researcher → exposer → collector"
    )
    parser.add_argument(
        "task", help="Задача: корень (напр. 'אמן'), стих (напр. 'Берешит 1:1') или термин (напр. 'хесед')"
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Папка для сохранения результата (по умолчанию content/researches/agent-drafts)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    result_path = run_pipeline(args.task, output_dir)
    print(f"\nГотово. Результат сохранён: {result_path}")


if __name__ == "__main__":
    main()
