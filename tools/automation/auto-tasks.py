# tools/automation/auto-tasks.py — управление задачами из TECHNICAL-DEBT.md

import re
import sys
from pathlib import Path
# from datetime import datetime  # TODO: проверить, используется ли

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, REPO_ROOT

TECH_DEBT_FILE = REPO_ROOT / "docs" / "TECHNICAL-DEBT.md"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
NC = "\033[0m"
BOLD = "\033[1m"


def log(message: str, color: str = BLUE, end: str = "\n"):
    print(f"{color}{message}{NC}", end=end)
    sys.stdout.flush()


def load_tasks() -> list:
    if not TECH_DEBT_FILE.exists():
        log(f"❌ {TECH_DEBT_FILE} не найден", RED)
        return []

    content = read_file_safe(TECH_DEBT_FILE)
    if not content:
        return []

    tasks = []
    for line in content.split('\n'):
        match = re.match(r'^- \[( |x)\] (.+)$', line)
        if match:
            tasks.append({
                "description": match.group(2).strip(),
                "done": match.group(1) == "x"
            })
    return tasks


def save_tasks(tasks: list):
    content = read_file_safe(TECH_DEBT_FILE)
    if not content:
        return

    lines = content.split('\n')
    new_lines = []
    task_idx = 0

    for line in lines:
        if re.match(r'- \[[ x]\]', line) and task_idx < len(tasks):
            task = tasks[task_idx]
            checkbox = "x" if task["done"] else " "
            new_line = re.sub(r'- \[[ x]\]', f'- [{checkbox}]', line)
            new_lines.append(new_line)
            task_idx += 1
        else:
            new_lines.append(line)

    with open(TECH_DEBT_FILE, "w", encoding="utf-8") as f:
        f.write('\n'.join(new_lines))


def complete_task(tasks: list, idx: int):
    task = tasks[idx]
    if task["done"]:
        log(f"   ⏭️ Задача уже выполнена", YELLOW)
        return False

    log(f"\n✅ {task['description']}", GREEN)
    task["done"] = True
    save_tasks(tasks)
    log(f"   📦 Задача отмечена как выполненная", CYAN)
    return True


def show_tasks(tasks: list):
    active = [t for t in tasks if not t["done"]]
    completed = [t for t in tasks if t["done"]]

    print(f"\n{BOLD}{BLUE}{'=' * 70}{NC}")
    print(f"{BOLD}{BLUE}📋 ТЕХНИЧЕСКИЙ ДОЛГ{NC}")
    print(f"{BOLD}{BLUE}{'=' * 70}{NC}")

    print(f"\n{BOLD}📌 АКТИВНЫЕ ЗАДАЧИ ({len(active)}){NC}")
    if active:
        for i, task in enumerate(active, 1):
            print(f"   {i:2}. {task['description'][:80]}")
    else:
        print(f"   {GREEN}✅ Нет активных задач!{NC}")

    if completed:
        print(f"\n{BOLD}✅ ВЫПОЛНЕННЫХ: {len(completed)}{NC}")

    print(f"\n{BOLD}{BLUE}{'=' * 70}{NC}")


def main():
    tasks = load_tasks()

    if not tasks:
        log(f"❌ Нет задач в {TECH_DEBT_FILE}", RED)
        return

    while True:
        show_tasks(tasks)

        print(f"\n  {BOLD}1{NC}   - Выполнить задачу по номеру")
        print(f"  {BOLD}a{NC}   - Выполнить все активные задачи")
        print(f"  {BOLD}c{NC}   - Показать только активные")
        print(f"  {BOLD}q{NC}   - Выход")

        choice = input(f"\n{BOLD}👉 Выберите действие: {NC}").strip().lower()

        if choice == 'q':
            log(f"\n👋 До свидания!", GREEN)
            break

        elif choice == 'a':
            active_indices = [i for i, t in enumerate(tasks) if not t["done"]]
            if not active_indices:
                log(f"\n✅ Нет активных задач", GREEN)
                continue

            log(f"\n🚀 Выполнение всех активных задач...", CYAN)
            completed_count = 0
            for idx in active_indices:
                if complete_task(tasks, idx):
                    completed_count += 1
            log(f"\n✅ Выполнено {completed_count} задач", GREEN)

        elif choice == 'c':
            active = [t for t in tasks if not t["done"]]
            if not active:
                log(f"\n✅ Нет активных задач", GREEN)
            else:
                print(f"\n📌 АКТИВНЫЕ ЗАДАЧИ:")
                for i, task in enumerate(active, 1):
                    print(f"   {i:2}. {task['description']}")
            input(f"\n{BOLD}Нажмите Enter для продолжения...{NC}")

        elif choice.isdigit():
            active_indices = [i for i, t in enumerate(tasks) if not t["done"]]
            if not active_indices:
                log(f"\n✅ Нет активных задач", GREEN)
                continue

            num_idx = int(choice) - 1
            if 0 <= num_idx < len(active_indices):
                complete_task(tasks, active_indices[num_idx])
            else:
                log(f"❌ Неверный номер", RED)
        else:
            log(f"❌ Неверный выбор", RED)


if __name__ == "__main__":
    main()

