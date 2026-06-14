#!/usr/bin/env python3
# tools/generators/generate-changelog.py — генерация CHANGELOG из TECH-DEBT и git

import sys
import subprocess
import re
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent.parent
TECH_DEBT = ROOT / "docs" / "TECHNICAL-DEBT.md"
CHANGELOG_FILE = ROOT / "docs" / "CHANGELOG.md"
VERSION_FILE = ROOT / "VERSION"
TYPES_FILE = ROOT / "tools" / "cache" / "cache-changelog-types.json"


def load_types():
    """Загружает типы коммитов из JSON."""
    if TYPES_FILE.exists():
        try:
            with open(TYPES_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("types", {})
        except Exception:
            pass
    return {"feat": "Добавлено", "fix": "Исправлено"}


def get_version():
    """Читает текущую версию."""
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    return "1.0.0"


def bump_version(version, bump_type="patch"):
    """Увеличивает версию."""
    parts = version.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    
    if bump_type == "major":
        major += 1; minor = 0; patch = 0
    elif bump_type == "minor":
        minor += 1; patch = 0
    else:
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    VERSION_FILE.write_text(new_version, encoding="utf-8")
    return new_version


def get_completed_tasks():
    """Извлекает выполненные задачи из TECH-DEBT."""
    if not TECH_DEBT.exists():
        return []
    
    content = TECH_DEBT.read_text(encoding="utf-8")
    tasks = []
    
    for line in content.split("\n"):
        match = re.match(r'^[-*]\s*\[x\]\s*(.+?)(?:\s*—\s*(\d{4}-\d{2}-\d{2}))?\s*$', line.strip())
        if match:
            task = match.group(1).strip()
            date = match.group(2)
            tasks.append({"task": task, "date": date})
    
    return tasks


def mark_tasks_with_date():
    """Проставляет сегодняшнюю дату выполненным задачам без даты."""
    if not TECH_DEBT.exists():
        return 0
    
    content = TECH_DEBT.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")
    lines = content.split("\n")
    updated = 0
    
    for i, line in enumerate(lines):
        match = re.match(r'^([-*]\s*\[x\]\s*.+?)(\s*—\s*\d{4}-\d{2}-\d{2})?\s*$', line)
        if match and not match.group(2):
            lines[i] = f"{match.group(1)} — {today}"
            updated += 1
    
    if updated:
        TECH_DEBT.write_text("\n".join(lines), encoding="utf-8")
    
    return updated


def get_git_commits_today():
    """Получает коммиты за сегодня."""
    try:
        log = subprocess.check_output(
            ["git", "log", "--since=midnight", "--pretty=format:%s"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        )
        return [c.strip() for c in log.strip().split("\n") if c.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def build_entry(version, tasks, commits):
    """Строит запись для CHANGELOG."""
    TYPES = load_types()
    date = datetime.now().strftime("%Y-%m-%d")
    lines = [f"## [{version}] - {date}\n"]
    
    # Группируем коммиты по типам
    grouped = {}
    for commit in commits:
        found = False
        for prefix, category in TYPES.items():
            if commit.lower().startswith(f"{prefix}:"):
                msg = commit[len(prefix) + 1:].strip()
                grouped.setdefault(category, []).append(msg)
                found = True
                break
        if not found:
            grouped.setdefault("Прочее", []).append(commit)
    
    # Выводим категории
    for category in TYPES.values():
        items = grouped.get(category, [])
        if not items:
            continue
        lines.append(f"### {category}")
        for item in sorted(set(items)):
            lines.append(f"- {item}")
        lines.append("")
    
    # Выполненные задачи
    if tasks:
        lines.append("### Выполненные задачи")
        for task in tasks:
            date_str = f"({task['date']})" if task['date'] else ""
            lines.append(f"- {task['task']} {date_str}".strip())
        lines.append("")
    
    if grouped.get("Прочее"):
        lines.append("### Прочее")
        for item in sorted(set(grouped["Прочее"])):
            lines.append(f"- {item}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    bump_type = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("📝 Генерация CHANGELOG...")
    
    # Отмечаем выполненные задачи датой
    marked = mark_tasks_with_date()
    if marked:
        print(f"   📋 Задач с датой: {marked}")
    
    # Получаем данные
    tasks = get_completed_tasks()
    commits = get_git_commits_today()
    
    if not tasks and not commits:
        print("⚠️ Нет выполненных задач и коммитов за сегодня")
        return 0
    
    # Версия
    old_version = get_version()
    
    if bump_type:
        new_version = bump_version(old_version, bump_type)
    else:
        has_major = any(c.startswith(("feat!", "remove!")) for c in commits)
        has_minor = any(c.startswith("feat") for c in commits)
        
        if has_major:
            new_version = bump_version(old_version, "major")
            print("   Авто: major")
        elif has_minor:
            new_version = bump_version(old_version, "minor")
            print("   Авто: minor")
        else:
            new_version = bump_version(old_version, "patch")
            print("   Авто: patch")
    
    print(f"   Версия: {old_version} → {new_version}")
    print(f"   Задач: {len(tasks)}")
    print(f"   Коммитов: {len(commits)}")
    
    entry = build_entry(new_version, tasks, commits)
    
    if CHANGELOG_FILE.exists():
        existing = CHANGELOG_FILE.read_text(encoding="utf-8")
        parts = existing.split("\n", 1)
        header = parts[0] + "\n" if len(parts) > 1 else ""
        rest = parts[1] if len(parts) > 1 else ""
        new_content = header + entry + "\n" + rest
    else:
        new_content = f"# 📜 CHANGELOG\n\n{entry}"
    
    CHANGELOG_FILE.write_text(new_content, encoding="utf-8")
    
    print(f"\n✅ CHANGELOG обновлён")
    print(f"   Файл: {CHANGELOG_FILE}")
    print(f"   Версия: {new_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())