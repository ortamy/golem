#!/usr/bin/env python3
# ed/assistant/assistant.py — assistant
# assistant.py — ассистент «Эд» для VS Code (v1.0)

import os
import sys
import subprocess
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
CONFIG_FILE = Path(__file__).resolve().parent / "config.yml"


def load_config():
    import yaml
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_tool(tool_name, args=None):
    tool_map = {
        "check_religionisms": TOOLS_DIR / "checkers" / "check-religionisms.py",
        "check_links": TOOLS_DIR / "checkers" / "check-links.py",
        "check_naming": TOOLS_DIR / "checkers" / "check-naming.py",
        "check_empty_files": TOOLS_DIR / "checkers" / "check-empty-files.py",
        "check_code_quality": TOOLS_DIR / "checkers" / "check-code-quality.py",
        "check_duplicates": TOOLS_DIR / "checkers" / "check-duplicates.py",
        "check_orphans": TOOLS_DIR / "checkers" / "check-orphans.py",
        "check_exposure": TOOLS_DIR / "checkers" / "check-exposure.py",
        "check_metadata": TOOLS_DIR / "checkers" / "check-metadata.py",
        "generate_structure": TOOLS_DIR / "sync" / "sync-structure.py",
        "generate_glossary": TOOLS_DIR / "generators" / "generate-glossary.py",
        "generate_index": TOOLS_DIR / "generators" / "generate-index.py",
        "generate_book": TOOLS_DIR / "generators" / "generate-book.py",
        "generate_files_json": TOOLS_DIR / "generators" / "generate-files-json.py",
        "report_stats": TOOLS_DIR / "reports" / "report-stats.py",
        "report_dashboard": TOOLS_DIR / "reports" / "report-dashboard.py",
        "clear_cache": TOOLS_DIR / "utils" / "clear-cache.py",
        "search": TOOLS_DIR / "utils" / "search.py",
    }
    tool_path = tool_map.get(tool_name)
    if not tool_path or not tool_path.exists():
        return False, f"Инструмент не найден: {tool_name}"
    try:
        cmd = [sys.executable, str(tool_path)] + (args or [])
        result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        return True, result.stdout if result.stdout else result.stderr
    except Exception as e:
        return False, str(e)


def execute_command(command):
    parts = command.strip().split()
    if not parts:
        return "Пустая команда."
    action = parts[0]
    if action == "check":
        what = parts[1] if len(parts) > 1 else "all"
        if what == "religionisms":
            ok, out = run_tool("check_religionisms")
        elif what == "links":
            ok, out = run_tool("check_links")
        elif what == "naming":
            ok, out = run_tool("check_naming")
        elif what == "empty":
            ok, out = run_tool("check_empty_files")
        elif what == "duplicates":
            ok, out = run_tool("check_duplicates")
        elif what == "orphans":
            ok, out = run_tool("check_orphans")
        elif what == "exposure":
            ok, out = run_tool("check_exposure")
        elif what == "all":
            ok, out = run_tool("check_religionisms")
            ok2, out2 = run_tool("check_links")
            out += "\n" + out2
        else:
            return f"Неизвестная проверка: {what}"
        return out if ok else f"Ошибка: {out}"
    elif action == "fix":
        what = parts[1] if len(parts) > 1 else "religionisms"
        if what == "religionisms":
            ok, out = run_tool("check_religionisms", ["--fix"])
        elif what == "metadata":
            ok, out = run_tool("check_metadata", ["--fix"])
        else:
            return f"Неизвестное исправление: {what}"
        return out if ok else f"Ошибка: {out}"
    elif action == "generate":
        what = parts[1] if len(parts) > 1 else "structure"
        if what == "structure":
            ok, out = run_tool("generate_structure")
        elif what == "glossary":
            ok, out = run_tool("generate_glossary")
        elif what == "index":
            ok, out = run_tool("generate_index")
        elif what == "book":
            ok, out = run_tool("generate_book")
        elif what == "files":
            ok, out = run_tool("generate_files_json")
        else:
            return f"Неизвестная генерация: {what}"
        return out if ok else f"Ошибка: {out}"
    elif action == "report":
        what = parts[1] if len(parts) > 1 else "stats"
        if what == "stats":
            ok, out = run_tool("report_stats")
        elif what == "dashboard":
            ok, out = run_tool("report_dashboard")
        else:
            return f"Неизвестный отчёт: {what}"
        return out if ok else f"Ошибка: {out}"
    elif action == "search":
        query = " ".join(parts[1:])
        ok, out = run_tool("search", [query])
        return out if ok else f"Ошибка: {out}"
    elif action == "clear":
        ok, out = run_tool("clear_cache")
        return out if ok else f"Ошибка: {out}"
    elif action == "help":
        return """Доступные команды:
  check [religionisms|links|naming|empty|duplicates|orphans|exposure|all]
  fix [religionisms|metadata]
  generate [structure|glossary|index|book|files]
  report [stats|dashboard]
  search <запрос>
  clear
  help"""
    else:
        return f"Неизвестная команда: {action}\nНапиши 'help' для списка команд."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python assistant.py <команда>")
        print("Пример: python assistant.py check religionisms")
        sys.exit(1)
    command = " ".join(sys.argv[1:])
    print(execute_command(command))