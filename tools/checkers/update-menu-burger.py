#!/usr/bin/env python3
# tools/checkers/update-burger-menu.py — обновление бургер-меню на всех страницах

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
WEBSITE_DIR = REPO_ROOT / "products" / "website"

NEW_BURGER_LINKS = """            <a href="../index.html">Главная</a>
            <a href="index.html">Исследования</a>
            <a href="methods.html">Методы разоблачения</a>
            <a href="dictionaries.html">Словари</a>
            <a href="methodology.html">Методология</a>
            <a href="checkers.html">Чекеры</a>
            <a href="../../content/hebrew">Иврит</a>
            <a href="../about/index.html">О проекте</a>"""

OLD_PATTERNS = [
    '            <a href="../index.html">Главная</a>',
    '            <a href="index.html">Исследования</a>',
    '            <a href="../../content/hebrew">Иврит</a>',
    '            <a href="../about/index.html">О проекте</a>',
]


def update_burger_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'side-panel-links' not in content:
        return False

    if 'Методы разоблачения' in content and 'Словари' in content and 'Методология' in content and 'Чекеры' in content:
        return False

    import re
    pattern = re.compile(r'(<div class="side-panel-links">)(.*?)(</div>)', re.DOTALL)
    match = pattern.search(content)
    if not match:
        return False

    new_block = f'<div class="side-panel-links">\n{NEW_BURGER_LINKS}\n        </div>'
    content = pattern.sub(new_block, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True


def main():
    updated = 0
    for filepath in sorted(WEBSITE_DIR.rglob("*.html")):
        if update_burger_in_file(filepath):
            rel = filepath.relative_to(REPO_ROOT)
            print(f"✅ {rel}")
            updated += 1

    print(f"\nОбновлено файлов: {updated}")


if __name__ == "__main__":
    main()