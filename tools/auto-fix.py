#!/usr/bin/env python3
# auto-fix.py — автоматическое выполнение задач с интеграцией идей

import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
TECH_DEBT_FILE = REPO_ROOT / "TECHNICAL-DEBT.md"
CHANGELOG_FILE = REPO_ROOT / "CHANGELOG.md"
IDEAS_DIR = REPO_ROOT / "ideas"

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


def parse_tasks() -> list:
    tasks = []
    if not TECH_DEBT_FILE.exists():
        return tasks
    
    with open(TECH_DEBT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for line in lines:
        match = re.match(r'^- \[( |x)\] (.+)$', line)
        if match and match.group(1) == " ":
            tasks.append(match.group(2).strip())
    
    return tasks


def create_term_file(name: str, title: str, topic: str) -> bool:
    term_file = REPO_ROOT / "terminology" / f"{name}.md"
    if term_file.exists():
        return False
    
    today = datetime.now().strftime("%Y-%m-%d")
    content = f"""# 📜 {title.upper()}

**Метаданные файла**
- **Файл:** `terminology/{name}.md`
- **Версия:** 1.0
- **Дата создания:** {today}
- **Статус:** Черновик
- **Тема:** {topic}

---

## 🔥 ВВЕДЕНИЕ

TODO: {topic}

## 📜 ОРИГИНАЛ

TODO: ивритский текст

## 🛡️ ВОЗВРАЩЕНИЕ

TODO: выводы
"""
    with open(term_file, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def create_research_file(name: str, title: str) -> bool:
    research_file = REPO_ROOT / "researches" / f"{name}.md"
    if research_file.exists():
        return False
    
    today = datetime.now().strftime("%Y-%m-%d")
    content = f"""# 📖 {title.upper()}

**Метаданные файла**
- **Файл:** `researches/{name}.md`
- **Версия:** 1.0
- **Дата создания:** {today}
- **Статус:** Черновик
- **Тема:** {title}

---

## 🔥 ВВЕДЕНИЕ

TODO

## 🛡️ ВОЗВРАЩЕНИЕ

TODO
"""
    with open(research_file, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def execute_auto_tasks(tasks: list) -> list:
    """Выполняет автоматические задачи"""
    completed = []
    
    terms = [
        ("midbar", "МИДБАР", "пустыня"),
        ("levad", "ЛЕВАД", "один"),
        ("arum", "АРУМ", "хитрый"),
        ("nachash", "НАХАШ", "змей"),
        ("pachad", "ПАХАД", "страх"),
        ("erech-apayim", "ЭРЕХ АПАЙИМ", "долгое дыхание"),
        ("yetzer-lev", "ЙЕЦЕР ЛЕВ", "помышление сердца"),
        ("gibor", "ГИБОР", "сильный"),
        ("shabbat", "ШАББАТ", "покой"),
        ("tohu-va-vohu", "ТОХУ ВА-ВОХУ", "пустота"),
    ]
    
    for name, title, topic in terms:
        if create_term_file(name, title, topic):
            completed.append(f"Создан термин: {name}")
    
    researches = [
        ("galatim-two-systems", "ГАЛАТИМ: ВОЙНА ДВУХ СИСТЕМ"),
        ("substitution-of-the-name", "КРАЖА ИМЕНИ"),
    ]
    
    for name, title in researches:
        if create_research_file(name, title):
            completed.append(f"Создано исследование: {name}")
    
    return completed


def update_chat_prompt():
    """Обновляет chat-prompt.md (запускает generate-nav.py)"""
    nav_script = REPO_ROOT / "tools" / "generate-nav.py"
    if nav_script.exists():
        subprocess.run([sys.executable, str(nav_script)], cwd=REPO_ROOT / "tools")
        return True
    return False


def mark_tasks_done(tasks: list, completed: list):
    """Отмечает выполненные задачи в TECHNICAL-DEBT.md"""
    if not TECH_DEBT_FILE.exists() or not completed:
        return
    
    with open(TECH_DEBT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        match = re.match(r'^- \[( |x)\] (.+)$', line)
        if match and match.group(1) == " ":
            desc = match.group(2)
            for comp in completed:
                if comp.split(":")[1].strip() in desc:
                    line = line.replace("- [ ]", "- [x]")
                    break
        new_lines.append(line)
    
    with open(TECH_DEBT_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def main():
    log(f"\n{BOLD}{BLUE}🔧 АВТОМАТИЧЕСКОЕ ВЫПОЛНЕНИЕ ЗАДАЧ{NC}")
    log("=" * 50)
    
    tasks = parse_tasks()
    log(f"📋 Найдено задач: {len(tasks)}")
    
    log("\n📝 Выполнение...")
    completed = execute_auto_tasks(tasks)
    
    if update_chat_prompt():
        completed.append("Обновлён chat-prompt.md")
    
    mark_tasks_done(tasks, completed)
    
    log(f"\n{GREEN}✅ Выполнено задач: {len(completed)}{NC}")
    for task in completed:
        log(f"   • {task}", GREEN)
    
    log(f"\n💡 Запустите 'python golem.py' для проверки", CYAN)


if __name__ == "__main__":
    main()