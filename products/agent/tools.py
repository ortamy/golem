#!/usr/bin/env python3
# ed/agent/tools.py — tools
# ed-agent/tools.py — описание инструментов агента
import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

TOOLS = {
    # Проверки
    "check-religionisms": {
        "path": "tools/checkers/check-religionisms.py",
        "category": "checkers",
        "description": "Поиск и исправление религионимов",
        "flags": ["--fix", "--rebuild", "--verbose", "--save"],
        "example": "python tools/checkers/check-religionisms.py --fix",
        "dangerous": False,
    },
    "check-links": {
        "path": "tools/checkers/check-links.py",
        "category": "checkers",
        "description": "Проверка битых ссылок между файлами",
        "flags": ["--fix", "--verbose"],
        "example": "python tools/checkers/check-links.py --fix",
        "dangerous": False,
    },
    "check-empty-files": {
        "path": "tools/checkers/check-empty-files.py",
        "category": "checkers",
        "description": "Поиск пустых и незаполненных md-файлов",
        "flags": ["--fix", "--verbose", "--save"],
        "example": "python tools/checkers/check-empty-files.py --fix",
        "dangerous": False,
    },
    "check-naming": {
        "path": "tools/checkers/check-naming.py",
        "category": "checkers",
        "description": "Проверка имён файлов на соответствие правилам",
        "flags": ["--fix", "--verbose"],
        "example": "python tools/checkers/check-naming.py --fix",
        "dangerous": True,
    },
    "check-code-quality": {
        "path": "tools/checkers/check-code-quality.py",
        "category": "checkers",
        "description": "Проверка качества Python-кода (стиль, сложность)",
        "flags": ["--fix", "--verbose"],
        "example": "python tools/checkers/check-code-quality.py",
        "dangerous": False,
    },
    "check-exposure": {
        "path": "tools/checkers/check-exposure.py",
        "category": "checkers",
        "description": "Проверка текста по всем exposure-критериям",
        "flags": ["--fix", "--verbose", "--save"],
        "example": "python tools/checkers/check-exposure.py",
        "dangerous": False,
    },
    "check-duplicates": {
        "path": "tools/checkers/check-duplicates.py",
        "category": "checkers",
        "description": "Поиск точных и похожих дубликатов файлов",
        "flags": ["--fix", "--verbose"],
        "example": "python tools/checkers/check-duplicates.py",
        "dangerous": True,
    },
    "check-sizes": {
        "path": "tools/checkers/check-sizes.py",
        "category": "checkers",
        "description": "Анализ размеров md-файлов",
        "flags": ["--fix", "--verbose", "--save"],
        "example": "python tools/checkers/check-sizes.py",
        "dangerous": False,
    },
    "check-tanakh-references": {
        "path": "tools/checkers/check-tanakh-references.py",
        "category": "checkers",
        "description": "Проверка ссылок на стихи ТаНаХа",
        "flags": ["--init", "--rebuild", "--verbose"],
        "example": "python tools/checkers/check-tanakh-references.py",
        "dangerous": False,
    },
    # Генераторы
    "generate-book": {
        "path": "tools/generators/generate-book.py",
        "category": "generators",
        "description": "Генерация HTML-книги из всех терминов и исследований",
        "flags": ["--limit"],
        "example": "python tools/generators/generate-book.py",
        "dangerous": False,
    },
    "generate-files-json": {
        "path": "tools/generators/generate-files-json.py",
        "category": "generators",
        "description": "Генерация files.json для веб-интерфейса",
        "flags": [],
        "example": "python tools/generators/generate-files-json.py",
        "dangerous": False,
    },
    "generate-dashboard": {
        "path": "tools/reports/report-dashboard.py",
        "category": "reports",
        "description": "Генерация интерактивного дашборда",
        "flags": [],
        "example": "python tools/reports/report-dashboard.py",
        "dangerous": False,
    },
    "generate-exposure-suggestions": {
        "path": "tools/generators/generate-exposure-suggestions.py",
        "category": "generators",
        "description": "Поиск кандидатов на новые методы и приёмы",
        "flags": ["--verbose"],
        "example": "python tools/generators/generate-exposure-suggestions.py",
        "dangerous": False,
    },
    "generate-knowledge-cache": {
        "path": "ed-neural/scripts/generate-knowledge-cache.py",
        "category": "neural",
        "description": "Генерация кэша знаний для нейросети",
        "flags": ["--rebuild"],
        "example": "python ed-neural/scripts/generate-knowledge-cache.py",
        "dangerous": False,
    },
    # Утилиты
    "search": {
        "path": "tools/search.py",
        "category": "utils",
        "description": "Поиск по всем md-файлам репозитория",
        "flags": ["--limit", "--verbose"],
        "example": "python tools/search.py хесед",
        "dangerous": False,
    },
    "rename-script": {
        "path": "tools/rename-script.py",
        "category": "utils",
        "description": "Переименование скриптов с префиксами по папкам",
        "flags": ["--auto"],
        "example": "python tools/rename-script.py --auto",
        "dangerous": True,
    },
    "code-injector": {
        "path": "tools/code-injector.py",
        "category": "utils",
        "description": "Программное редактирование кода (вставка, замена, удаление)",
        "flags": ["--after", "--before", "--replace", "--delete", "--dry-run"],
        "example": "python tools/code-injector.py -f file.py --after 10 --code 'test'",
        "dangerous": True,
    },
    # Git
    "git-status": {
        "path": "git",
        "category": "git",
        "description": "Статус Git-репозитория",
        "flags": ["status", "diff", "add", "commit", "push"],
        "example": "git status",
        "dangerous": False,
    },
    "git-commit": {
        "path": "git",
        "category": "git",
        "description": "Создание коммита",
        "flags": [],
        "example": "git add . && git commit -m 'message'",
        "dangerous": True,
    },
}


def get_tool(name: str) -> dict | None:
    return TOOLS.get(name)


def get_tools_by_category(category: str) -> list:
    return [name for name, tool in TOOLS.items() if tool["category"] == category]


def get_safe_tools() -> list:
    return [name for name, tool in TOOLS.items() if not tool["dangerous"]]


def get_tool_names() -> list:
    return list(TOOLS.keys())


def run_tool(name: str, args: str = "") -> bool:
    tool = get_tool(name)
    if not tool:
        return False

    if tool["category"] == "git":
        cmd = ["git"] + (args.split() if args else ["status"])
    else:
        script_path = REPO_ROOT / tool["path"]
        if not script_path.exists():
            return False
        cmd = [sys.executable, str(script_path)] + (args.split() if args else [])

    try:
        result = subprocess.run(cmd, cwd=REPO_ROOT)
        return result.returncode == 0
    except Exception:
        return False