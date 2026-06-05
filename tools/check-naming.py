#!/usr/bin/env python3
# add-metadata.py — массовое добавление метаданных в файлы

import os
import re
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
TARGET_DIRS = ['terminology', 'researches']

METADATA_TEMPLATE = '''**Метаданные файла**
- **Файл:** `{file_path}`
- **Версия:** 1.0
- **Дата создания:** {date}
- **Последнее обновление:** {date}
- **Причина обновления:** Создание файла
- **Статус:** Активный
- **Тема:** {topic}

---

'''

def extract_topic(content: str, file_name: str) -> str:
    """Извлекает тему из содержимого или имени файла"""
    # Пробуем найти первый заголовок
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# ') and not line.startswith('# 📂'):
            # Убираем эмоджи
            clean = re.sub(r'^# [^\w]+\s*', '', line)
            return clean[:100]
    
    # Если нет заголовка, используем имя файла
    name = file_name.replace('-', ' ').replace('.md', '')
    return name.capitalize()

def has_metadata(content: str) -> bool:
    """Проверяет, есть ли уже метаданные в файле"""
    return '**Метаданные файла**' in content or 'Метаданные' in content[:500]

def add_metadata_to_file(file_path: Path):
    """Добавляет метаданные в файл"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if has_metadata(content):
        print(f"  ⏭️ Пропуск (уже есть метаданные): {file_path.name}")
        return
    
    # Извлекаем тему
    topic = extract_topic(content, file_path.name)
    rel_path = file_path.relative_to(REPO_ROOT)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Формируем метаданные
    metadata = METADATA_TEMPLATE.format(
        file_path=rel_path,
        date=today,
        topic=topic
    )
    
    # Вставляем после заголовка или в начало
    lines = content.split('\n')
    if lines and lines[0].startswith('# '):
        # Вставляем после первой строки
        new_content = lines[0] + '\n\n' + metadata + '\n' + '\n'.join(lines[1:])
    else:
        # Вставляем в начало
        new_content = metadata + content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✅ Добавлены метаданные: {file_path.name}")

def main():
    print("📝 Добавление метаданных в файлы...")
    
    count = 0
    for target_dir in TARGET_DIRS:
        dir_path = REPO_ROOT / target_dir
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.rglob('*.md'):
            if md_file.name in ['README.md', 'structure.md']:
                continue
            add_metadata_to_file(md_file)
            count += 1
    
    print(f"\n✅ Обработано файлов: {count}")

if __name__ == "__main__":
    main()
