#!/usr/bin/env python3
# ed-agent/agent.py — ИИ-агент «Эд» с нейросетевым планированием
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import print_header, print_success, print_error, print_warning, print_hint

REPO_ROOT = Path(__file__).parent.parent
AGENT_DIR = Path(__file__).parent
MEMORY_FILE = AGENT_DIR / "memory.json"
CLIENT_PATH = REPO_ROOT / "ed-neural" / "inference" / "client.py"

# Доступные инструменты
TOOLS = {
    "check-religionisms": {
        "path": "tools/checkers/check-religionisms.py",
        "description": "Поиск и исправление религионимов",
        "flags": ["--fix", "--rebuild", "--verbose", "--save"],
    },
    "check-links": {
        "path": "tools/checkers/check-links.py",
        "description": "Проверка битых ссылок",
        "flags": ["--fix", "--verbose"],
    },
    "check-empty-files": {
        "path": "tools/checkers/check-empty-files.py",
        "description": "Поиск пустых и незаполненных файлов",
        "flags": ["--fix", "--verbose", "--save"],
    },
    "check-naming": {
        "path": "tools/checkers/check-naming.py",
        "description": "Проверка имён файлов",
        "flags": ["--fix", "--verbose"],
    },
    "check-code-quality": {
        "path": "tools/checkers/check-code-quality.py",
        "description": "Проверка качества Python-кода",
        "flags": ["--fix", "--verbose"],
    },
    "check-exposure": {
        "path": "tools/checkers/check-exposure.py",
        "description": "Проверка текста по exposure-критериям",
        "flags": ["--fix", "--verbose", "--save"],
    },
    "check-duplicates": {
        "path": "tools/checkers/check-duplicates.py",
        "description": "Поиск дубликатов файлов",
        "flags": ["--fix", "--verbose"],
    },
    "check-sizes": {
        "path": "tools/checkers/check-sizes.py",
        "description": "Анализ размеров файлов",
        "flags": ["--fix", "--verbose", "--save"],
    },
    "check-tanakh-references": {
        "path": "tools/checkers/check-tanakh-references.py",
        "description": "Проверка ссылок на ТаНаХ",
        "flags": ["--init", "--rebuild", "--verbose"],
    },
    "generate-book": {
        "path": "tools/generators/generate-book.py",
        "description": "Генерация HTML-книги из терминов и исследований",
        "flags": ["--limit"],
    },
    "generate-files-json": {
        "path": "tools/generators/generate-files-json.py",
        "description": "Генерация files.json для веб-интерфейса",
        "flags": [],
    },
    "generate-dashboard": {
        "path": "tools/reports/report-dashboard.py",
        "description": "Генерация дашборда со статистикой",
        "flags": [],
    },
    "generate-exposure-suggestions": {
        "path": "tools/generators/generate-exposure-suggestions.py",
        "description": "Поиск кандидатов на новые методы/приёмы",
        "flags": ["--verbose"],
    },
    "generate-knowledge-cache": {
        "path": "ed-neural/scripts/generate-knowledge-cache.py",
        "description": "Генерация кэша знаний для нейросети",
        "flags": ["--rebuild"],
    },
    "search": {
        "path": "tools/search.py",
        "description": "Поиск по всем файлам репозитория",
        "flags": ["--limit", "--verbose"],
    },
    "rename-script": {
        "path": "tools/rename-script.py",
        "description": "Переименование скриптов",
        "flags": ["--auto"],
    },
    "code-injector": {
        "path": "tools/code-injector.py",
        "description": "Программное редактирование кода",
        "flags": ["--after", "--before", "--replace", "--delete", "--dry-run"],
    },
    "git-status": {
        "path": "git",
        "description": "Статус git-репозитория",
        "flags": ["status", "diff", "add", "commit", "push"],
    },
}


def load_memory() -> dict:
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"actions": [], "last_task": None, "stats": {"tasks_completed": 0}}


def save_memory(memory: dict):
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)


def ask_neural(task: str) -> dict | None:
    """Спрашивает нейросеть о плане действий."""
    if not CLIENT_PATH.exists():
        return None

    tools_desc = "\n".join([f"- {name}: {t['description']}" for name, t in sorted(TOOLS.items())])

    prompt = f"""Ты — ИИ-агент «Эд», управляешь проектом «Голем». Твоя задача — составить план действий.

Доступные инструменты:
{tools_desc}

Задача пользователя: {task}

Ответь СТРОГО в формате JSON без пояснений:
{{"tools": ["имя-инструмента-1", "имя-инструмента-2"], "flags": ["--флаг1", "--флаг2"], "reasoning": "почему выбрал эти инструменты"}}

Выбирай только из доступных инструментов. Не выдумывай новые."""

    try:
        result = subprocess.run(
            [sys.executable, str(CLIENT_PATH), "--prompt", prompt, "--temperature", "0.3", "--max-tokens", "256"],
            capture_output=True, text=True, timeout=60
        )
        response = result.stdout.strip()
        if response:
            # Извлекаем JSON из ответа
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
    except Exception:
        pass

    return None


def run_tool(tool_name: str, args: str = "") -> bool:
    if tool_name not in TOOLS:
        print_error(f"Инструмент не найден: {tool_name}")
        return False

    tool = TOOLS[tool_name]

    # Особая обработка git
    if tool_name == "git-status":
        cmd = ["git"] + (args.split() if args else ["status"])
    else:
        script_path = REPO_ROOT / tool["path"]
        if not script_path.exists():
            print_error(f"Скрипт не найден: {script_path}")
            return False
        cmd = [sys.executable, str(script_path)] + (args.split() if args else [])

    print(f"\n🔧 {tool_name} {' '.join(cmd[1:])}")

    try:
        result = subprocess.run(cmd, cwd=REPO_ROOT)
        return result.returncode == 0
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False


def show_tools():
    print("\n🧰 ДОСТУПНЫЕ ИНСТРУМЕНТЫ:")
    for name, tool in sorted(TOOLS.items()):
        print(f"  {name:32} — {tool['description']}")


def process_with_neural(task: str) -> dict | None:
    """Обрабатывает задачу через нейросеть."""
    print("🧠 Спрашиваю нейросеть...")
    plan = ask_neural(task)

    if plan:
        print(f"   План: {' → '.join(plan.get('tools', []))}")
        if plan.get("reasoning"):
            print(f"   Почему: {plan['reasoning']}")
        return plan

    return None


def process_with_rules(task: str) -> dict | None:
    """Обрабатывает задачу по правилам (запасной вариант)."""
    task_lower = task.lower()

    rules = [
        (["провер", "религион"], {"tools": ["check-religionisms"], "flags": ["--fix"]}),
        (["провер", "ссылк"], {"tools": ["check-links"], "flags": ["--fix"]}),
        (["провер", "пуст"], {"tools": ["check-empty-files"], "flags": ["--fix"]}),
        (["провер", "имён", "имен"], {"tools": ["check-naming"], "flags": ["--fix"]}),
        (["провер", "код"], {"tools": ["check-code-quality"], "flags": []}),
        (["провер", "exposure"], {"tools": ["check-exposure"], "flags": []}),
        (["дубликат"], {"tools": ["check-duplicates"], "flags": []}),
        (["размер"], {"tools": ["check-sizes"], "flags": []}),
        (["танах", "стих"], {"tools": ["check-tanakh-references"], "flags": []}),
        (["книг", "book"], {"tools": ["generate-book"], "flags": []}),
        (["files.json", "веб"], {"tools": ["generate-files-json"], "flags": []}),
        (["дашборд"], {"tools": ["generate-dashboard"], "flags": []}),
        (["переимен"], {"tools": ["rename-script"], "flags": ["--auto"]}),
        (["кэш", "знаний"], {"tools": ["generate-knowledge-cache"], "flags": []}),
        (["git", "коммит", "пуш"], {"tools": ["git-status"], "flags": []}),
        (["поиск", "найди", "ищи"], {"tools": ["search"], "flags": []}),
    ]

    for keywords, plan in rules:
        if all(kw in task_lower for kw in keywords):
            return plan

    return None


def execute_plan(plan: dict):
    """Выполняет план действий."""
    tools = plan.get("tools", [])
    flags = plan.get("flags", [])

    if not tools:
        print_warning("Нет инструментов для выполнения")
        return

    flags_str = ' '.join(flags)
    success_count = 0

    for i, tool in enumerate(tools, 1):
        print(f"\n[{i}/{len(tools)}] {tool}...")
        if run_tool(tool, flags_str):
            success_count += 1

    print(f"\n✅ Выполнено: {success_count}/{len(tools)}")


def interactive():
    print_header("ИИ-АГЕНТ «ЭД»", "🤖")
    print("Нейросетевое планирование + выполнение задач.\n")

    memory = load_memory()

    if memory["stats"]["tasks_completed"] > 0:
        print(f"📊 Выполнено задач: {memory['stats']['tasks_completed']}")
        if memory.get("last_task"):
            print(f"   Последняя: {memory['last_task']}")
        print()

    use_neural = CLIENT_PATH.exists()

    if not use_neural:
        print_warning("Нейросеть не найдена. Работаю по правилам.")
        print_hint("Для нейросетевого планирования запустите сервер ed-neural")

    while True:
        try:
            task = input("🤖 > ").strip()

            if not task:
                continue

            if task.lower() in ("выход", "exit"):
                save_memory(memory)
                print("👋 До свидания")
                break

            if task.lower() in ("инструменты", "tools"):
                show_tools()
                continue

            if task.lower() in ("справка", "help"):
                print("\nПримеры задач:")
                print("  «проверь всё и исправь ошибки»")
                print("  «найди дубликаты и проверь ссылки»")
                print("  «сгенерируй книгу и дашборд»")
                print("  «обнови files.json»")
                print("  «поиск хесед»")
                print("  «сделай коммит»")
                print("\nКоманды: инструменты, справка, выход")
                continue

            # Пробуем нейросеть
            plan = None
            if use_neural:
                plan = process_with_neural(task)

            # Если нейросеть не ответила — правила
            if not plan:
                print("⚙️ Использую правила...")
                plan = process_with_rules(task)

            if not plan:
                print_warning("Не понял задачу.")
                show_tools()
                print_hint("Попробуй: «проверь всё», «найди дубликаты», «поиск хесед»")
                continue

            # Выполняем план
            execute_plan(plan)

            # Обновляем память
            memory["actions"].append({
                "task": task,
                "plan": plan,
            })
            memory["last_task"] = task
            memory["stats"]["tasks_completed"] += 1

            print()

        except KeyboardInterrupt:
            save_memory(memory)
            print("\n👋 До свидания")
            break
        except EOFError:
            break


def main():
    if "--auto" in sys.argv:
        task = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if not task:
            print_error("Укажите задачу: python agent.py --auto 'проверь всё и исправь'")
            return 1
        memory = load_memory()
        plan = ask_neural(task) or process_with_rules(task)
        if plan:
            execute_plan(plan)
        return 0

    interactive()
    return 0


if __name__ == "__main__":
    sys.exit(main())