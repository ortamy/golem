#!/usr/bin/env python3
# generate-nav.py — генерация навигации по репозиторию для README.md

import re
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent
README_PATH = REPO_ROOT / "README.md"
NAV_START_MARKER = "<!-- NAVIGATION_START -->"
NAV_END_MARKER = "<!-- NAVIGATION_END -->"

TARGET_DIRS = {
    'instructions': '📖 Инструкции',
    'checkers': '✅ Чекеры',
    'terminology': '📚 Терминология',
    'researches': '🔬 Исследования',
    'tools': '🛠️ Инструменты',
    'ideas': '💡 Идеи',
    'drafts': '📝 Черновики'
}


def extract_title(file_path: Path) -> str:
    """Извлекает заголовок из файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if first_line.startswith('# '):
                title = first_line[2:].strip()
                title = re.sub(r'^[\U00010000-\U0010FFFF]\s*', '', title)
                return title[:60]
    except:
        pass
    return file_path.stem.replace('-', ' ').title()


def scan_directory(dir_path: Path, max_files: int = 20) -> list:
    """Сканирует папку и возвращает список файлов"""
    files = []
    if not dir_path.exists():
        return files
    
    for md_file in sorted(dir_path.glob('*.md')):
        if md_file.name in ['README.md', 'structure.md', 'GLOSSARY.md', 'STATS.md']:
            continue
        rel_path = md_file.relative_to(REPO_ROOT)
        title = extract_title(md_file)
        files.append((title, str(rel_path)))
    
    return files[:max_files]


def generate_navigation() -> str:
    """Генерирует HTML-комментарий с навигацией"""
    lines = [NAV_START_MARKER, "", "# 🧭 НАВИГАЦИЯ ПО РЕПОЗИТОРИЮ", ""]
    
    for folder, display_name in TARGET_DIRS.items():
        dir_path = REPO_ROOT / folder
        files = scan_directory(dir_path)
        
        if files:
            lines.append(f"## {display_name}")
            lines.append("")
            for title, path in files:
                lines.append(f"- [{title}]({path})")
            lines.append("")
    
    lines.append(f"📊 **Всего файлов:** {sum(len(scan_directory(REPO_ROOT / f)) for f in TARGET_DIRS)}")
    lines.append("")
    lines.append(NAV_END_MARKER)
    
    return '\n'.join(lines)


def update_readme():
    """Обновляет README.md, заменяя секцию навигации"""
    if not README_PATH.exists():
        print(f"❌ {README_PATH} не найден")
        return False
    
    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_nav = generate_navigation()
    
    if NAV_START_MARKER in content and NAV_END_MARKER in content:
        pattern = f"{NAV_START_MARKER}.*?{NAV_END_MARKER}"
        new_content = re.sub(pattern, new_nav, content, flags=re.DOTALL)
    else:
        new_content = content + "\n\n" + new_nav
    
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


def main():
    print("🧭 ГЕНЕРАЦИЯ НАВИГАЦИИ")
    print("======================")
    print("")
    
    if update_readme():
        print(f"✅ Навигация добавлена в {README_PATH}")
        print("📝 Проверьте результат и сделайте git commit")
    else:
        print("❌ Ошибка обновления README.md")


if __name__ == "__main__":
    main()
