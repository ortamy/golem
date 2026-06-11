#!/usr/bin/env python3
# idea-manager.py — управление идеями с автоматической синхронизацией

import sys
import re
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
IDEAS_DIR = REPO_ROOT / "ideas"
CHANGELOG_FILE = REPO_ROOT / "CHANGELOG.md"
TECH_DEBT_FILE = REPO_ROOT / "TECHNICAL-DEBT.md"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
NC = "\033[0m"
BOLD = "\033[1m"


def log(message: str, color: str = BLUE):
    print(f"{color}{message}{NC}")
    sys.stdout.flush()


def parse_ideas_from_file(file_path: Path) -> list:
    ideas = []
    if not file_path.exists():
        return ideas

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    for line in lines:
        match = re.match(r'^- \[( |x)\] (.+)$', line)
        if match:
            ideas.append({
                "description": match.group(2).strip(),
                "done": (match.group(1) == "x"),
                "source": file_path.name
            })
    return ideas


def parse_all_ideas() -> list:
    all_ideas = []
    for md_file in IDEAS_DIR.glob("*.md"):
        if md_file.name == "idea-template.md":
            continue
        all_ideas.extend(parse_ideas_from_file(md_file))
    return all_ideas


def sync_ideas_with_tasks():
    """Автоматически синхронизирует идеи с TECHNICAL-DEBT.md"""
    ideas = parse_all_ideas()
    active_ideas = [i for i in ideas if not i["done"]]

    if not TECH_DEBT_FILE.exists():
        log(f"❌ {TECH_DEBT_FILE} не найден", RED)
        return 0

    with open(TECH_DEBT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    added = 0
    for idea in active_ideas:
        task_line = f"- [ ] {idea['description']} (из идей: {idea['source']})"
        if task_line not in content:
            with open(TECH_DEBT_FILE, "a", encoding="utf-8") as f:
                f.write(f"{task_line}\n")
            added += 1

    return added


def show_ideas_with_numbers(ideas: list):
    active = [i for i in ideas if not i["done"]]
    if not active:
        print(f"\n{GREEN}✅ Нет активных идей{NC}")
        return []

    print(f"\n{BOLD}{CYAN}💡 АКТИВНЫЕ ИДЕИ{NC}")
    print("=" * 70)
    for i, idea in enumerate(active, 1):
        print(f"   {BOLD}{i:3}{NC}. {idea['description'][:60]} [{idea['source']}]")
    print("=" * 70)
    return active


def mark_idea_done(ideas: list, idx: int):
    active = [i for i in ideas if not i["done"]]
    if idx < 0 or idx >= len(active):
        log("❌ Неверный номер", RED)
        return

    idea = active[idx]
    source_file = IDEAS_DIR / idea["source"]

    if source_file.exists():
        with open(source_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            if idea["description"] in line and "- [ ]" in line:
                line = line.replace("- [ ]", "- [x]")
            new_lines.append(line)

        with open(source_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    today = datetime.now().strftime("%Y-%m-%d")
    if CHANGELOG_FILE.exists():
        with open(CHANGELOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"- {idea['description']}\n")

    log(f"✅ Отмечено: {idea['description'][:60]}", GREEN)


def main():
    while True:
        print(f"\n{BOLD}{CYAN}💡 УПРАВЛЕНИЕ ИДЕЯМИ{NC}")
        print("=" * 40)
        print(f"  {BOLD}1{NC}   Показать идеи")
        print(f"  {BOLD}2{NC}   Отметить идею выполненной")
        print(f"  {BOLD}3{NC}   Синхронизировать с задачами")
        print(f"  {BOLD}0{NC}   Выход")

        choice = input(f"\n{BOLD}👉 Выберите: {NC}").strip()

        if choice == "0":
            break
        elif choice == "1":
            ideas = parse_all_ideas()
            show_ideas_with_numbers(ideas)
        elif choice == "2":
            ideas = parse_all_ideas()
            active = show_ideas_with_numbers(ideas)
            if active:
                num = input("Номер: ")
                if num.isdigit():
                    mark_idea_done(ideas, int(num) - 1)
        elif choice == "3":
            added = sync_ideas_with_tasks()
            log(f"✅ Добавлено {added} идей в TECHNICAL-DEBT.md", GREEN)
        else:
            log("❌ Неверный выбор", RED)

        input("\nНажмите Enter...")


if __name__ == "__main__":
    main()

