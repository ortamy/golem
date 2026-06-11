#!/usr/bin/env python3
# tools/generators/generate-sync-structure.py — синхронизация STRUCTURE.md
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import print_header, print_success, REPO_ROOT

STRUCTURE_FILE = REPO_ROOT / "docs" / "STRUCTURE.md"
IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__', 'reports', 'neural', '.venv', 'docs_backup'}
IGNORE_FILES = {'STRUCTURE.md', 'structure.txt', 'README.md', 'golem.log', '.gitignore', 'export-repo.sh'}


def scan_files(path: Path, prefix: str = "") -> list:
    lines = []
    items = sorted([p for p in path.iterdir() if p.name not in IGNORE_DIRS and not p.name.startswith('.')])

    dirs = [p for p in items if p.is_dir()]
    files = [p for p in items if p.is_file() and p.suffix == '.md' and p.name not in IGNORE_FILES]

    for d in dirs:
        lines.append(f"{prefix}- `{d.name}/`")
        lines.extend(scan_files(d, prefix + "    "))

    for f in files:
        lines.append(f"{prefix}- `{f.name}`")

    return lines


def generate_structure() -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    content = f"""# СТРУКТУРА РЕПОЗИТОРИЯ

**Метаданные файла**
- **Файл:** `docs/STRUCTURE.md`
- **Версия:** 2.5
- **Дата создания:** 2026-05-28
- **Последнее обновление:** {today}
- **Причина обновления:** Автоматическая синхронизация
- **Статус:** Активный
- **Тема:** Полная структура репозитория «Голем»

---

## КОРЕНЬ

"""

    root_items = []
    for item in sorted(REPO_ROOT.iterdir()):
        name = item.name
        if name in IGNORE_DIRS or name.startswith('.'):
            continue
        if item.is_dir():
            root_items.append(f"- `{name}/`")
        elif item.is_file() and item.suffix == '.md' and name not in IGNORE_FILES:
            root_items.append(f"- `{name}`")

    content += "\n".join(root_items) + "\n"

    dirs_to_scan = [d for d in sorted(REPO_ROOT.iterdir())
                    if d.is_dir() and d.name not in IGNORE_DIRS and not d.name.startswith('.')]

    for d in dirs_to_scan:
        content += f"\n## {d.name}/\n\n"
        files = scan_files(d, "    ")
        if files:
            content += "\n".join(files) + "\n"
        else:
            content += "    *(пусто)*\n"

    return content


def main():
    print_header("СИНХРОНИЗАЦИЯ STRUCTURE.MD", "🔄")

    new_content = generate_structure()

    STRUCTURE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STRUCTURE_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print_success(f"Обновлено: {STRUCTURE_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

