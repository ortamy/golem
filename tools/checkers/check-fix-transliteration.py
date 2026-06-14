# tools/checkers/check-fix-transliteration.py — автоматическое исправление транслитерации

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TERMINOLOGY_DIR = REPO_ROOT / "terminology"

FIXES = {
    r"й[eе]гова": "Яхве",
    r"й[eе]хова": "Яхве",
    r"YHWH": "Яхве",
    r"йhwh": "Яхве",
    r"руах̣": "руах",
    r"эмэт": "эмет",
    r"хэсэд": "хесед",
    r"хесэд": "хесед",
}

def fix_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    for pattern, replacement in FIXES.items():
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

    if content != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False

def main():
    print("🔧 ИСПРАВЛЕНИЕ ТРАНСЛИТЕРАЦИИ")
    print("=" * 50)
    print("")

    fixed = 0
    for md_file in TERMINOLOGY_DIR.glob("*.md"):
        if fix_file(md_file):
            print(f"✅ {md_file.name}")
            fixed += 1

    print("")
    print(f"📊 Исправлено файлов: {fixed}")

if __name__ == "__main__":
    main()

