#!/usr/bin/env python3
# tools.py — инструменты ассистента «Эд» (v1.0)

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"

# Все доступные инструменты сгруппированы по категориям
AVAILABLE_TOOLS = {
    # Проверки
    "check_religionisms": {
        "path": "checkers/check-religionisms.py",
        "description": "Поиск и исправление религионимов",
        "flags": ["--fix", "--rebuild"],
        "category": "checkers",
    },
    "check_links": {
        "path": "checkers/check-links.py",
        "description": "Проверка внутренних ссылок в md-файлах",
        "flags": [],
        "category": "checkers",
    },
    "check_naming": {
        "path": "checkers/check-naming.py",
        "description": "Проверка имён md-файлов",
        "flags": [],
        "category": "checkers",
    },
    "check_empty_files": {
        "path": "checkers/check-empty-files.py",
        "description": "Поиск пустых и незаполненных файлов",
        "flags": [],
        "category": "checkers",
    },
    "check_code_quality": {
        "path": "checkers/check-code-quality.py",
        "description": "Проверка качества Python-кода",
        "flags": ["--fix"],
        "category": "checkers",
    },
    "check_duplicates": {
        "path": "checkers/check-duplicates.py",
        "description": "Поиск дубликатов файлов",
        "flags": [],
        "category": "checkers",
    },
    "check_orphans": {
        "path": "checkers/check-orphans.py",
        "description": "Поиск файлов-сирот без входящих ссылок",
        "flags": [],
        "category": "checkers",
    },
    "check_exposure": {
        "path": "checkers/check-exposure.py",
        "description": "Проверка текста по exposure-критериям",
        "flags": [],
        "category": "checkers",
    },
    "check_metadata": {
        "path": "checkers/check-metadata.py",
        "description": "Проверка метаданных md-файлов",
        "flags": ["--fix"],
        "category": "checkers",
    },
    "check_consistency": {
        "path": "checkers/check-consistency.py",
        "description": "Проверка согласованности терминов и ссылок",
        "flags": [],
        "category": "checkers",
    },
    "check_tahor_sync": {
        "path": "checkers/check-tahor-sync.py",
        "description": "Сверка словарей tahor/",
        "flags": [],
        "category": "checkers",
    },
    "check_env": {
        "path": "checkers/check-env.py",
        "description": "Проверка окружения",
        "flags": [],
        "category": "checkers",
    },

    # Генераторы
    "generate_glossary": {
        "path": "generators/generate-glossary.py",
        "description": "Генерация глоссария из terminology/",
        "flags": [],
        "category": "generators",
    },
    "generate_index": {
        "path": "generators/generate-index.py",
        "description": "Генерация индекса всех файлов",
        "flags": [],
        "category": "generators",
    },
    "generate_book": {
        "path": "generators/generate-book.py",
        "description": "Генерация HTML-книги из исследований",
        "flags": [],
        "category": "generators",
    },
    "generate_files_json": {
        "path": "generators/generate-files-json.py",
        "description": "Генерация files.json для веб-интерфейса",
        "flags": [],
        "category": "generators",
    },
    "generate_metadata": {
        "path": "generators/generate-metadata.py",
        "description": "Унификация метаданных md-файлов",
        "flags": ["--fix"],
        "category": "generators",
    },
    "generate_graph": {
        "path": "generators/generate-graph.py",
        "description": "Генерация визуальной карты связей",
        "flags": [],
        "category": "generators",
    },
    "generate_related_links": {
        "path": "generators/generate-related-links.py",
        "description": "Авто-добавление перекрёстных ссылок",
        "flags": ["--dry-run"],
        "category": "generators",
    },

    # Синхронизация
    "sync_structure": {
        "path": "sync/sync-structure.py",
        "description": "Синхронизация STRUCTURE.md",
        "flags": [],
        "category": "sync",
    },
    "sync_changelogs": {
        "path": "sync/sync-changelogs.py",
        "description": "Синхронизация CHANGELOG",
        "flags": [],
        "category": "sync",
    },

    # Отчёты
    "report_stats": {
        "path": "reports/report-stats.py",
        "description": "Статистика репозитория",
        "flags": [],
        "category": "reports",
    },
    "report_dashboard": {
        "path": "reports/report-dashboard.py",
        "description": "Генерация дашборда",
        "flags": [],
        "category": "reports",
    },
    "report_health": {
        "path": "reports/report-health.py",
        "description": "Проверка здоровья проекта",
        "flags": [],
        "category": "reports",
    },

    # Утилиты
    "clear_cache": {
        "path": "utils/clear-cache.py",
        "description": "Очистка кэша",
        "flags": [],
        "category": "utils",
    },
    "search": {
        "path": "utils/search.py",
        "description": "Поиск по файлам репозитория",
        "flags": ["--limit", "--verbose"],
        "category": "utils",
    },
}


def get_tool_path(tool_name):
    info = AVAILABLE_TOOLS.get(tool_name)
    if not info:
        return None
    return TOOLS_DIR / info["path"]


def get_tools_by_category(category=None):
    if category:
        return {k: v for k, v in AVAILABLE_TOOLS.items() if v["category"] == category}
    return AVAILABLE_TOOLS


def run_tool(tool_name, args=None):
    tool_path = get_tool_path(tool_name)
    if not tool_path or not tool_path.exists():
        return False, f"Инструмент не найден: {tool_name}"
    try:
        cmd = [sys.executable, str(tool_path)] + (args or [])
        result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        return True, result.stdout if result.stdout else result.stderr
    except Exception as e:
        return False, str(e)


def list_tools():
    categories = {}
    for name, info in AVAILABLE_TOOLS.items():
        cat = info["category"]
        if cat not in categories:
            categories[cat] = []
        flags = " ".join(info.get("flags", []))
        categories[cat].append(f"  {name} {flags} — {info['description']}")
    output = []
    for cat in ["checkers", "generators", "sync", "reports", "utils"]:
        if cat in categories:
            output.append(f"[{cat}]")
            output.extend(categories[cat])
            output.append("")
    return "\n".join(output)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(list_tools())
    elif sys.argv[1] == "list":
        print(list_tools())
    else:
        tool_name = sys.argv[1]
        args = sys.argv[2:] if len(sys.argv) > 2 else []
        ok, out = run_tool(tool_name, args)
        print(out)