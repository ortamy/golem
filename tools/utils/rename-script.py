#!/usr/bin/env python3
# tools/rename-script.py — переименование скриптов (ручной + авто-режим)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.utils import print_header, print_success, print_error, print_warning, ask_yes_no

REPO_ROOT = Path(__file__).parent.parent

# Правила: папка → префикс
FOLDER_PREFIXES = {
    "checkers": "check",
    "generators": "generate",
    "reports": "report",
    "automation": "auto",
    "sync": "sync",
    "backup": "backup",
}

# Слова, которые заменяем в именах
WORD_MAP = {
    "node-web": "web",
    "fill-empty-files": "fill-empty",
    "add-related-links": "related-links",
    "unify-metadata": "metadata",
    "stats-report": "stats",
    "daily-report": "daily",
    "check-health": "health",
    "update-versions": "versions",
    "task-manager": "tasks",
    "idea-manager": "ideas",
    "clear-cache": "clear-cache",
    "autodoc": "doc",
    "dashboard": "dashboard",
}


def find_file(name: str) -> Path | None:
    """Ищет файл по имени во всех подпапках tools/ и neural/."""
    search_dirs = [
        REPO_ROOT / "tools",
        REPO_ROOT / "neural" / "scripts",
        REPO_ROOT / "neural" / "inference",
    ]
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        matches = list(search_dir.rglob(name))
        if matches:
            return matches[0]
        matches = list(search_dir.rglob(name + ".py"))
        if matches:
            return matches[0]
        matches = list(search_dir.rglob(f"*{name}*"))
        if matches:
            return matches[0]
    return None


def get_prefix(filepath: Path) -> str:
    """Определяет нужный префикс по папке."""
    rel = filepath.relative_to(REPO_ROOT)
    parts = rel.parts
    # Ищем папку с известным префиксом
    for i in range(len(parts) - 1, -1, -1):
        if parts[i] in FOLDER_PREFIXES:
            return FOLDER_PREFIXES[parts[i]]
    return ""


def suggest_name(filepath: Path) -> str | None:
    """Предлагает новое имя по правилам."""
    stem = filepath.stem
    prefix = get_prefix(filepath)

    if not prefix:
        return None

    # Проверяем, есть ли уже правильный префикс
    if stem.startswith(prefix + "-"):
        return None

    # Ищем что переименовать по словарю
    base = stem
    for old, new in WORD_MAP.items():
        if old in stem:
            base = new
            break

    # Убираем старый префикс если есть
    for p in FOLDER_PREFIXES.values():
        if base.startswith(p + "-"):
            base = base[len(p) + 1:]

    suggested = f"{prefix}-{base}"
    return suggested if suggested != stem else None


def scan_and_suggest():
    """Сканирует tools/ и предлагает переименования."""
    print("\n🔍 Сканирование tools/ и neural/...")

    suggestions = []
    search_dirs = [
        REPO_ROOT / "tools",
        REPO_ROOT / "neural" / "scripts",
    ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for f in sorted(search_dir.rglob("*.py")):
            suggested = suggest_name(f)
            if suggested:
                suggestions.append((f, suggested))

    if not suggestions:
        print_success("Все имена уже правильные")
        return []

    print(f"\n📋 Предложений: {len(suggestions)}\n")
    for i, (f, new_name) in enumerate(suggestions, 1):
        rel = f.relative_to(REPO_ROOT)
        print(f"  {i:2}. {rel}")
        print(f"      → {f.parent.relative_to(REPO_ROOT)}/{new_name}.py")

    return suggestions


def rename_one_manual():
    """Переименовывает один файл вручную."""
    search = input("\nИмя файла (или часть имени): ").strip()
    if not search:
        return False

    filepath = find_file(search)
    if not filepath:
        print_error(f"Файл не найден: {search}")
        return False

    rel_path = filepath.relative_to(REPO_ROOT)
    print(f"📄 Найден: {rel_path}")

    if not ask_yes_no("Это тот файл?"):
        return False

    # Предлагаем имя
    suggested = suggest_name(filepath)
    print(f"Текущее имя: {filepath.stem}")
    if suggested:
        print(f"Предложение: {suggested}")

    new_name = input("Новое имя (без .py, Enter = отмена): ").strip()
    if not new_name:
        return False

    new_file = filepath.parent / (new_name + ".py")
    if new_file.exists():
        print_error(f"Файл уже существует: {new_file.relative_to(REPO_ROOT)}")
        return False

    print(f"\n  {filepath.stem}.py → {new_name}.py")
    if ask_yes_no("Переименовать?"):
        filepath.rename(new_file)
        print_success(f"✅ {new_file.relative_to(REPO_ROOT)}")
        return True

    return False


def rename_auto(suggestions: list):
    """Переименовывает все предложенные файлы."""
    if not suggestions:
        return 0

    if not ask_yes_no(f"\nПереименовать все {len(suggestions)} файлов?"):
        # Выборочно
        renamed = 0
        for f, new_name in suggestions:
            rel = f.relative_to(REPO_ROOT)
            if ask_yes_no(f"  {rel} → {new_name}.py?"):
                new_file = f.parent / (new_name + ".py")
                if not new_file.exists():
                    f.rename(new_file)
                    print_success(f"    ✅ {new_name}.py")
                    renamed += 1
        return renamed

    renamed = 0
    for f, new_name in suggestions:
        new_file = f.parent / (new_name + ".py")
        if not new_file.exists():
            f.rename(new_file)
            renamed += 1

    print_success(f"✅ Переименовано: {renamed}")
    return renamed


def main():
    auto_mode = "--auto" in sys.argv

    print_header("ПЕРЕИМЕНОВАНИЕ СКРИПТОВ", "📛")

    if auto_mode:
        suggestions = scan_and_suggest()
        if suggestions:
            rename_auto(suggestions)
        return 0

    renamed = 0

    # Сначала предлагаем авто-режим
    suggestions = scan_and_suggest()
    if suggestions:
        if ask_yes_no("\n🤖 Запустить авто-переименование?"):
            renamed = rename_auto(suggestions)
            if renamed:
                print_success(f"\nПереименовано: {renamed}")
            return 0
    else:
        return 0

    # Ручной режим
    while True:
        if rename_one_manual():
            renamed += 1
        if not ask_yes_no("\nПереименовать ещё файл?"):
            break

    if renamed:
        print_success(f"\nПереименовано: {renamed}")
    print("👋 Выход")
    return 0


if __name__ == "__main__":
    sys.exit(main())