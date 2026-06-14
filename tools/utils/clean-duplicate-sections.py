#!/usr/bin/env python3
# tools/utils/clean-duplicate-sections.py — clean duplicate sections
"""
Скрипт для удаления дублирующих секций ## 🔗 СВЯЗАННЫЕ ИССЛЕДОВАНИЯ в конце .md файлов.
Связанные файлы в блоке метаданных (поле "Связанные файлы:") не трогает.
Запуск: python tools/remove-duplicate-links.py terminology/
"""

import re
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def remove_duplicate_section(text: str) -> str:
    """
    Удаляет секцию ## 🔗 СВЯЗАННЫЕ ИССЛЕДОВАНИЯ или ## 🔗 СВЯЗАННЫЕ ФАЙЛЫ
    в конце файла, включая все ссылки под ней до конца файла.
    """
    # Паттерн: ## 🔗 СВЯЗАННЫЕ ИССЛЕДОВАНИЯ или ## 🔗 СВЯЗАННЫЕ ФАЙЛЫ
    # и всё до конца файла
    pattern = r'\n{1,2}## 🔗 СВЯЗАННЫЕ (ИССЛЕДОВАНИЯ|ФАЙЛЫ).*$'
    result = re.sub(pattern, '', text, count=1, flags=re.DOTALL)
    
    # Убираем лишние пустые строки в конце
    result = result.rstrip('\n') + '\n'
    
    return result


def process_directory(dir_path: str):
    path = ROOT / dir_path
    if not path.exists() or not path.is_dir():
        print(f"❌ Папка не найдена: {path}")
        return
    
    md_files = sorted(path.rglob('*.md'))
    
    total = 0
    changed = 0
    
    for filepath in md_files:
        total += 1
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = remove_duplicate_section(content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            changed += 1
            print(f"  ✂️  {filepath.relative_to(ROOT)}")
    
    print(f"\n✅ Обработано: {total} файлов, изменено: {changed}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python tools/remove-duplicate-links.py <папка>")
        print("Пример: python tools/remove-duplicate-links.py terminology/")
        sys.exit(1)
    
    process_directory(sys.argv[1])