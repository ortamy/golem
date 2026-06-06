#!/usr/bin/env python3
# task-manager.py — управление задачами из TECHNICAL-DEBT.md

import re
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
TECH_DEBT_FILE = REPO_ROOT / "TECHNICAL-DEBT.md"
CHANGELOG_FILE = REPO_ROOT / "CHANGELOG.md"
ARCHIVE_FILE = REPO_ROOT / "COMPLETED-TASKS.md"

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
    """Загружает задачи из TECHNICAL-DEBT.md"""
    tasks = []
    
    if not TECH_DEBT_FILE.exists():
        log(f"❌ {TECH_DEBT_FILE} не найден", RED)
        return tasks
    
    with open(TECH_DEBT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for line in lines:
        match = re.match(r'^- \[( |x)\] (.+)$', line)
        if match:
            status = match.group(1)
            description = match.group(2).strip()
            done = (status == "x")
            tasks.append({
                "description": description,
                "done": done
            })
    
    return tasks


def save_tasks(tasks: list):
    """Сохраняет задачи в TECHNICAL-DEBT.md"""
    with open(TECH_DEBT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    new_lines = []
    task_idx = 0
    
    for line in lines:
        if re.match(r'^- \[( |x)\]', line) and task_idx < len(tasks):
            task = tasks[task_idx]
            checkbox = "x" if task["done"] else " "
            new_line = re.sub(r'- \[[ x]\]', f'- [{checkbox}]', line)
            new_lines.append(new_line)
            task_idx += 1
        else:
            new_lines.append(line)
    
    with open(TECH_DEBT_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def archive_task(description: str):
    """Архивирует выполненную задачу"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if not ARCHIVE_FILE.exists():
        with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
            f.write(f"# Архив выполненных задач\n\n## {today}\n\n")
    
    with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    if f"## {today}" not in content:
        with open(ARCHIVE_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n## {today}\n\n")
    
    with open(ARCHIVE_FILE, "a", encoding="utf-8") as f:
        f.write(f"- {description}\n")


def add_to_changelog(description: str):
    """Добавляет задачу в CHANGELOG"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if not CHANGELOG_FILE.exists():
        with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"# CHANGELOG\n\n## {today}\n\n### Исправлено\n\n")
    
    with open(CHANGELOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    if f"## {today}" not in content:
        content = content.replace("# CHANGELOG\n\n", f"# CHANGELOG\n\n## {today}\n\n### Исправлено\n\n")
    
    if "### Исправлено" in content:
        lines = content.split("\n")
        new_lines = []
        inserted = False
        for line in lines:
            new_lines.append(line)
            if not inserted and line == "### Исправлено":
                new_lines.append("")
                new_lines.append(f"- {description}")
                inserted = True
        content = "\n".join(new_lines)
    else:
        content += f"\n### Исправлено\n\n- {description}\n"
    
    with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def complete_task(tasks: list, idx: int):
    """Отмечает задачу как выполненную"""
    task = tasks[idx]
    if task["done"]:
        log(f"   ⏭️ Задача уже выполнена", YELLOW)
        return False
    
    log(f"\n✅ {task['description']}", GREEN)
    archive_task(task['description'])
    add_to_changelog(task['description'])
    task["done"] = True
    save_tasks(tasks)
    log(f"   📦 Заархивировано и добавлено в CHANGELOG", CYAN)
    return True


def show_tasks(tasks: list):
    """Показывает список задач"""
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
    
    print(f"\n{BOLD}✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ ({len(completed)}){NC}")
    if completed and len(completed) <= 10:
        for task in completed[:10]:
            print(f"   • {task['description'][:70]}")
    elif completed:
        print(f"   • ... и ещё {len(completed)} выполненных задач")
    
    print(f"\n{BOLD}{BLUE}{'=' * 70}{NC}")


def main():
    tasks = load_tasks()
    
    if not tasks:
        log(f"❌ Нет задач в TECHNICAL-DEBT.md", RED)
        return
    
    while True:
        show_tasks(tasks)
        
        print(f"\n  {BOLD}1{NC}   - Выполнить задачу по номеру")
        print(f"  {BOLD}a{NC}   - Выполнить все активные задачи")
        print(f"  {BOLD}c{NC}   - Показать только активные задачи")
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
        
        elif choice == '1':
            active_indices = [i for i, t in enumerate(tasks) if not t["done"]]
            if not active_indices:
                log(f"\n✅ Нет активных задач", GREEN)
                continue
            
            print(f"\n📌 Активные задачи:")
            for i, idx in enumerate(active_indices, 1):
                print(f"   {i}. {tasks[idx]['description'][:70]}")
            
            num = input(f"\n{BOLD}👉 Введите номер задачи: {NC}").strip()
            if num.isdigit():
                num_idx = int(num) - 1
                if 0 <= num_idx < len(active_indices):
                    complete_task(tasks, active_indices[num_idx])
                else:
                    log(f"❌ Неверный номер", RED)
            else:
                log(f"❌ Введите число", RED)
        
        else:
            log(f"❌ Неверный выбор", RED)


if __name__ == "__main__":
    main()