#!/usr/bin/env python3
# tools/generate-changelog.py
import sys
import subprocess
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

TYPES = {
    "feat": "Добавлено",
    "fix": "Исправлено",
    "docs": "Документация",
    "refactor": "Изменено",
    "remove": "Удалено",
    "terminology": "Терминология",
    "research": "Исследования",
    "tools": "Инструменты",
}


def get_commits_since_last_tag():
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=REPO_ROOT, text=True
        ).strip()
        log = subprocess.check_output(
            ["git", "log", f"{tag}..HEAD", "--pretty=format:%s"],
            cwd=REPO_ROOT, text=True
        )
    except subprocess.CalledProcessError:
        log = subprocess.check_output(
            ["git", "log", "--pretty=format:%s"],
            cwd=REPO_ROOT, text=True
        )
    return log.strip().split("\n") if log.strip() else []


def parse_commits(commits):
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


def read_existing_changelog():
    if CHANGELOG.exists():
        with open(CHANGELOG, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def build_entry(version, grouped):
    date = datetime.now().strftime("%Y-%m-%d")
    lines = [f"\n## [{version}] - {date}\n"]

    for category, items in grouped.items():
        lines.append(f"### {category}")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines)


def main():
    print("\n📝 ГЕНЕРАЦИЯ CHANGELOG")
    print("=" * 50)

    version = sys.argv[1] if len(sys.argv) > 1 else None
    if not version:
        print("❌ Укажи версию: python tools/generate-changelog.py 2.1.0")
        return 1

    commits = get_commits_since_last_tag()
    if not commits:
        print("⚠️ Нет коммитов для добавления")
        return 0

    print(f"Найдено коммитов: {len(commits)}")

    grouped = parse_commits(commits)

    print("\nГруппировка:")
    for category, items in grouped.items():
        print(f"  {category}: {len(items)}")

    entry = build_entry(version, grouped)

    existing = read_existing_changelog()

    with open(CHANGELOG, "w", encoding="utf-8") as f:
        f.write(entry + "\n" + existing)

    print(f"\n✅ CHANGELOG обновлён: v{version}")
    print(f"   Файл: {CHANGELOG}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

