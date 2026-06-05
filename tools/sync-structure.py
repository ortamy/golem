#!/usr/bin/env python3
# sync-structure.py — синхронизирует structure.md с реальной файловой системой

import os
import re
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
STRUCTURE_FILE = REPO_ROOT / "structure.md"
IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__'}
IGNORE_FILES = {'structure.md', 'structure.txt', 'README.md', 'BACKLOG.md', 'CHANGELOG.md', 'DECISIONS.md', 'ROADMAP.md', 'TECHNICAL-DEBT.md', 'GLOSSARY.md', 'RETROSPECTIVE.md'}

def scan_files(path: Path, prefix: str = "") -> list:
    """Сканирует репозиторий и возвращает список строк для structure.md"""
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
    """Генерирует новое содержимое structure.md"""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""# 📂 СТРУКТУРА РЕПОЗИТОРИЯ

**Метаданные файла**
- **Файл:** `structure.md`
- **Версия:** 3.0
- **Дата создания:** 2026-05-28
- **Последнее обновление:** {timestamp}
- **Причина обновления:** Автоматическая синхронизация с файловой системой
- **Статус:** Активный
- **Тема:** Полная структура репозитория «Голем»

---

## 📂 КОРЕНЬ

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
    
    for d in sorted(REPO_ROOT.iterdir()):
        if d.is_dir() and d.name not in IGNORE_DIRS:
            content += f"\n## 📁 {d.name}/\n\n"
            files = scan_files(d, "    ")
            content += "\n".join(files) + "\n"
    
    return content

def main():
    print("🔄 Синхронизация structure.md...")
    new_content = generate_structure()
    
    with open(STRUCTURE_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Обновлено: {STRUCTURE_FILE}")
    print("📝 Проверьте изменения и сделайте git commit")

if __name__ == "__main__":
    main()
