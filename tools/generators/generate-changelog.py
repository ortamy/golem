#!/usr/bin/env python3
# tools/generators/generate-changelog.py — генерация CHANGELOG из git-коммитов

import sys
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"

TYPES = {
    "feat": "Добавлено",
    "fix": "Исправлено",
    "docs": "Документация",
    "refactor": "Изменено",
    "remove": "Удалено",
    "tools": "Инструменты",
    "style": "Стиль",
    "test": "Тесты",
}


def get_version():
    """Получает версию из git-тегов или генерирует автоматически."""
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        if tag:
            return tag
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return datetime.now().strftime("0.0.%Y%m%d")


def get_commits():
    """Получает коммиты с последнего тега или все."""
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        if tag:
            log = subprocess.check_output(
                ["git", "log", f"{tag}..HEAD", "--pretty=format:%s"],
                cwd=ROOT, text=True, stderr=subprocess.DEVNULL
            )
        else:
            log = subprocess.check_output(
                ["git", "log", "--pretty=format:%s"],
                cwd=ROOT, text=True, stderr=subprocess.DEVNULL
            )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    
    return [c.strip() for c in log.strip().split("\n") if c.strip()]


def parse_commits(commits):
    """Группирует коммиты по типам."""
    grouped = {v: [] for v in TYPES.values()}
    grouped["Прочее"] = []
    
    for commit in commits:
        found = False
        for prefix, category in TYPES.items():
            if commit.lower().startswith(f"{prefix}:"):
                msg = commit[len(prefix) + 1:].strip()
                grouped[category].append(msg)
                found = True
                break
        if not found:
            grouped["Прочее"].append(commit)
    
    return {k: v for k, v in grouped.items() if v}


def build_entry(version, grouped):
    """Строит запись для CHANGELOG."""
    date = datetime.now().strftime("%Y-%m-%d")
    lines = [f"## [{version}] - {date}\n"]
    
    for category in TYPES.values():
        items = grouped.get(category, [])
        if not items:
            continue
        lines.append(f"### {category}")
        for item in sorted(set(items)):
            lines.append(f"- {item}")
        lines.append("")
    
    if grouped.get("Прочее"):
        lines.append("### Прочее")
        for item in sorted(set(grouped["Прочее"])):
            lines.append(f"- {item}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    print("📝 Генерация CHANGELOG...")
    
    version = get_version()
    commits = get_commits()
    
    if not commits:
        print("⚠️ Нет новых коммитов")
        return 0
    
    print(f"   Версия: {version}")
    print(f"   Коммитов: {len(commits)}")
    
    grouped = parse_commits(commits)
    
    for category, items in grouped.items():
        print(f"   {category}: {len(items)}")
    
    entry = build_entry(version, grouped)
    
    # Вставляем после заголовка
    if CHANGELOG.exists():
        existing = CHANGELOG.read_text(encoding="utf-8")
        # Найти первую строку после заголовка
        parts = existing.split("\n", 1)
        header = parts[0] + "\n" if len(parts) > 1 else ""
        rest = parts[1] if len(parts) > 1 else ""
        new_content = header + entry + "\n" + rest
    else:
        new_content = f"# 📜 CHANGELOG\n\n{entry}"
    
    CHANGELOG.write_text(new_content, encoding="utf-8")
    
    print(f"\n✅ CHANGELOG обновлён")
    print(f"   Файл: {CHANGELOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())