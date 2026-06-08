# tools/sync-structure.py
import sys
from pathlib import Path
from datetime import datetime
from progress import show_progress, finish_progress

REPO_ROOT = Path(__file__).parent.parent
STRUCTURE_FILE = REPO_ROOT / "STRUCTURE.md"
IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__', 'reports', 'neural'}
IGNORE_FILES = {'STRUCTURE.md', 'structure.txt', 'README.md', 'BACKLOG.md', 'CHANGELOG.md', 
                'DECISIONS.md', 'ROADMAP.md', 'TECHNICAL-DEBT.md', 'GLOSSARY.md', 
                'RETROSPECTIVE.md', 'STATS.md', 'CONTRIBUTORS.md', 'COMPLETED-TASKS.md'}


def scan_files(path: Path, prefix: str = "") -> list:
    lines = []
    items = sorted([p for p in path.iterdir() if p.name not in IGNORE_DIRS])
    
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
- **Файл:** `STRUCTURE.md`
- **Версия:** 2.4
- **Дата создания:** 2026-05-28
- **Последнее обновление:** {today}
- **Статус:** Активный
- **Тема:** Полная структура репозитория «Голем»

---

## КОРЕНЬ

"""
    
    root_items = []
    for item in sorted(REPO_ROOT.iterdir()):
        name = item.name
        if name in IGNORE_DIRS or name in IGNORE_FILES:
            continue
        if item.is_dir():
            root_items.append(f"- `{name}/`")
        elif item.is_file() and item.suffix == '.md':
            root_items.append(f"- `{name}`")
    
    content += "\n".join(root_items) + "\n"
    
    # Собираем все папки для сканирования
    dirs_to_scan = [d for d in sorted(REPO_ROOT.iterdir()) 
                    if d.is_dir() and d.name not in IGNORE_DIRS and d.name not in IGNORE_FILES]
    
    for i, d in enumerate(dirs_to_scan):
        show_progress(i + 1, len(dirs_to_scan), f"сканирование {d.name}")
        content += f"\n## {d.name}/\n\n"
        files = scan_files(d, "    ")
        content += "\n".join(files) + "\n"
    
    finish_progress()
    return content


def main():
    print("\n🔄 СИНХРОНИЗАЦИЯ STRUCTURE.MD")
    print("=" * 50)
    
    print("Генерация структуры...")
    new_content = generate_structure()
    
    with open(STRUCTURE_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n✅ Обновлено: {STRUCTURE_FILE}")


if __name__ == "__main__":
    main()