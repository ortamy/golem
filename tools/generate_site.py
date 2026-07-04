#!/usr/bin/env python3
"""
tools/generate_site.py — Генератор HTML страниц из Markdown файлов.
"""

import os
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    print("Ошибка: библиотека 'markdown' не установлена.", file=sys.stderr)
    print("Установите: pip install markdown", file=sys.stderr)
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BASE_DIR / "content"
OUTPUT_DIR = BASE_DIR / "products" / "website" / "content"


def get_html_template(title: str, content: str) -> str:
    """Генерирует HTML шаблон для страницы."""
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Golem</title>
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<article class="content">
{content}
</article>
</body>
</html>
"""


def convert_md_to_html(md_path: Path) -> str:
    """Конвертирует Markdown файл в HTML."""
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Конвертируем markdown в HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'toc'])
    
    # Извлекаем заголовок для title
    title = "Без названия"
    lines = md_content.split('\n')
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break
    
    return get_html_template(title, html_content)


def main():
    """Основная функция генерации сайта."""
    if not CONTENT_DIR.exists():
        print(f"Папка {CONTENT_DIR} не найдена", file=sys.stderr)
        sys.exit(1)
    
    # Создаём выходную папку если её нет
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Находим все .md файлы
    md_files = sorted(CONTENT_DIR.rglob("*.md"))
    
    converted = 0
    errors = 0
    
    for md_path in md_files:
        try:
            # Вычисляем относительный путь и меняем расширение
            rel_path = md_path.relative_to(CONTENT_DIR)
            html_path = OUTPUT_DIR / rel_path.with_suffix('.html')
            
            # Создаём подпапки если нужно
            html_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Конвертируем и сохраняем
            html_content = convert_md_to_html(md_path)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✓ {rel_path} → {html_path.relative_to(OUTPUT_DIR)}")
            converted += 1
        except Exception as e:
            print(f"✗ Ошибка при обработке {md_path}: {e}", file=sys.stderr)
            errors += 1
    
    print(f"\nГотово: {converted} файлов сконвертировано, {errors} ошибок")


if __name__ == "__main__":
    main()