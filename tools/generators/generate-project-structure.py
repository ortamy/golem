#!/usr/bin/env python3
# tools/generators/generate-project-structure.py — генератор STRUCTURE.md (карта проекта)

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import print_header, print_success, print_error, REPO_ROOT

EXCLUDE_DIRS = {
    ".git", ".venv", "__pycache__", ".vscode", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "node_modules", ".idea",
    ".vs", ".history", ".sass-cache", ".tox", "eggs", "egg-info",
    ".gitattributes", ".gitignore", ".DS_Store",
}

EXCLUDE_DIR_PREFIXES = (".", "_")

STRUCTURE_FILE = REPO_ROOT / "STRUCTURE.md"

# Папки для сканирования в порядке отображения
SCAN_DIRS = [
    "terminology",
    "researches",
    "instructions",
    "tools",
    "ed-neural",
    "ed-agent",
    "web",
    "docs",
    "drafts",
    "ideas",
    "davar",
    "reports",
]


def should_exclude_dir(name: str) -> bool:
    if name in EXCLUDE_DIRS:
        return True
    if name.startswith(EXCLUDE_DIR_PREFIXES):
        return True
    return False


def should_exclude_file(name: str) -> bool:
    if name in EXCLUDE_DIRS:
        return True
    if name.startswith("."):
        return True
    return False


def has_files(path: Path) -> bool:
    """Проверяет, есть ли в папке файлы (не учитывая служебные)."""
    if not path.exists():
        return False
    try:
        for item in path.iterdir():
            if item.is_file() and not should_exclude_file(item.name):
                return True
    except PermissionError:
        pass
    return False


def count_files(path: Path) -> int:
    """Считает количество файлов в директории (нерекурсивно)."""
    count = 0
    if not path.exists():
        return 0
    try:
        for item in path.iterdir():
            if item.is_file() and not should_exclude_file(item.name):
                count += 1
    except PermissionError:
        pass
    return count


def count_files_recursive(path: Path) -> int:
    """Считает количество файлов в директории рекурсивно."""
    count = 0
    if not path.exists():
        return 0
    try:
        for item in path.rglob("*"):
            if item.is_file() and not should_exclude_file(item.name):
                exclude = False
                for parent in item.parents:
                    if should_exclude_dir(parent.name):
                        exclude = True
                        break
                if not exclude:
                    count += 1
    except PermissionError:
        pass
    return count


def format_size(n: int) -> str:
    """Форматирует число файлов с единицей (русский язык)."""
    if n == 0:
        return ""
    last_digit = n % 10
    if 11 <= n % 100 <= 19:
        suffix = "файлов"
    elif last_digit == 1:
        suffix = "файл"
    elif 2 <= last_digit <= 4:
        suffix = "файла"
    else:
        suffix = "файлов"
    return f" ({n} {suffix})"


def generate_tree(path: Path, indent: str = "", depth: int = 0, max_depth: int = 3) -> list[str]:
    """Генерирует дерево подпапок с подсчётом файлов в каждой."""
    lines = []
    if not path.exists() or not path.is_dir():
        return lines

    try:
        items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return lines

    items = [p for p in items if p.is_dir() and not should_exclude_dir(p.name)]

    for i, item in enumerate(items):
        is_last = (i == len(items) - 1)
        connector = "└── " if is_last else "├── "
        line_prefix = indent + connector

        file_count = count_files(item)
        count_str = format_size(file_count)
        lines.append(f"{line_prefix}{item.name}/{count_str}")

        if depth < max_depth:
            extension = "    " if is_last else "│   "
            sub_lines = generate_tree(item, indent + extension, depth + 1, max_depth)
            lines.extend(sub_lines)

    return lines


def generate_structure() -> str:
    """Генерирует содержимое STRUCTURE.md."""
    lines = []
    lines.append("# 🗂️ СТРУКТУРА ПРОЕКТА (STRUCTURE.MD)")
    lines.append("")
    lines.append("**Автоматически сгенерировано.** Обновляй через:")
    lines.append("```bash")
    lines.append("python tools/generators/generate-project-structure.py")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")

    total_all = 0

    for dir_name in SCAN_DIRS:
        dir_path = REPO_ROOT / dir_name
        if not dir_path.exists() or not dir_path.is_dir():
            continue

        file_count = count_files_recursive(dir_path)
        total_all += file_count
        count_str = format_size(file_count)

        lines.append(f"## 📁 {dir_name}/{count_str}")
        lines.append("")

        # Показываем дерево подпапок
        tree_lines = generate_tree(dir_path, max_depth=2)

        if tree_lines:
            lines.extend(tree_lines)
        else:
            # Нет подпапок — скажем сколько файлов в корне
            root_files = count_files(dir_path)
            if root_files > 0:
                lines.append(f"   *{root_files} файлов в корне*")
            else:
                lines.append("_пусто_")
        lines.append("")

    lines.append("---")
    lines.append("")
    total_str = format_size(total_all)
    lines.append(f"**Всего: {total_str}**")
    lines.append("")

    return "\n".join(lines)


def main():
    print_header("🗂️ ГЕНЕРАЦИЯ STRUCTURE.MD")

    try:
        content = generate_structure()
        STRUCTURE_FILE.write_text(content, encoding="utf-8")
        print_success(f"✅ STRUCTURE.md создан: {STRUCTURE_FILE}")
        print(f"   Файлов просканировано: {len(SCAN_DIRS)} папок")
    except Exception as e:
        print_error(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()