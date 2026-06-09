# tools/generators/export-book.py — сборка исследований в книгу (PDF/HTML)
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_hint, ask_yes_no, REPO_ROOT

OUTPUT_DIR = REPO_ROOT / "docs" / "export"

# Категории для выбора
CATEGORIES = {
    "1": {"name": "Всё (terminology + researches + exposure)", "dirs": ["terminology", "researches", "instructions/exposure"]},
    "2": {"name": "Терминология (terminology/)", "dirs": ["terminology"]},
    "3": {"name": "Все исследования (researches/)", "dirs": ["researches"]},
    "4": {"name": "Методология разоблачения (instructions/exposure/)", "dirs": ["instructions/exposure"]},
    "5": {"name": "ТаНаХ (researches/tanakh/)", "dirs": ["researches/tanakh"]},
    "6": {"name": "Учения и религии (researches/teachings/)", "dirs": ["researches/teachings"]},
    "7": {"name": "Системы контроля (researches/systems/)", "dirs": ["researches/systems"]},
    "8": {"name": "Экономика и финансы (researches/economy/)", "dirs": ["researches/economy"]},
    "9": {"name": "История (researches/history/)", "dirs": ["researches/history"]},
    "10": {"name": "Социология и общество (researches/sociology/)", "dirs": ["researches/sociology"]},
    "11": {"name": "Психология и сознание (researches/psychology/)", "dirs": ["researches/psychology"]},
    "12": {"name": "Медицина и здоровье (researches/medicine/)", "dirs": ["researches/medicine"]},
    "13": {"name": "Наука (researches/science/)", "dirs": ["researches/science"]},
    "14": {"name": "Медиа и пропаганда (researches/media/)", "dirs": ["researches/media"]},
    "15": {"name": "Язык и лингвистика (researches/language/)", "dirs": ["researches/language"]},
    "16": {"name": "Политика (researches/politics/)", "dirs": ["researches/politics"]},
    "17": {"name": "Спорт (researches/sport/)", "dirs": ["researches/sport"]},
    "18": {"name": "Рабство и свобода (researches/slavery/)", "dirs": ["researches/slavery"]},
    "19": {"name": "Книги и разбор (researches/books/)", "dirs": ["researches/books"]},
    "20": {"name": "Компании (researches/companies/)", "dirs": ["researches/companies"]},
    "21": {"name": "Имена (researches/names/)", "dirs": ["researches/names"]},
    "22": {"name": "Практики (researches/practices/)", "dirs": ["researches/practices"]},
    "23": {"name": "Римское право (researches/roman-law/)", "dirs": ["researches/roman-law"]},
    "24": {"name": "Архив (researches/archive/)", "dirs": ["researches/archive"]},
    "25": {"name": "Прочее (researches/other/)", "dirs": ["researches/other"]},
    "26": {"name": "Карты очищения языка (instructions/tahor/)", "dirs": ["instructions/tahor"]},
    "27": {"name": "Методология исследований (instructions/methodology/)", "dirs": ["instructions/methodology"]},
    "28": {"name": "Инструкции (instructions/)", "dirs": ["instructions"]},
    "29": {"name": "Документация (docs/)", "dirs": ["docs"]},
    "30": {"name": "Своя папка (указать вручную)", "dirs": []},
}


def export_html(scan_dirs: list, title: str):
    """Собирает файлы из указанных папок в HTML-книгу."""
    today = datetime.now().strftime("%Y-%m-%d")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_files = []
    for scan_dir in scan_dirs:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    if not all_files:
        print_warning("Нет файлов для экспорта")
        return

    total = len(all_files)
    print(f"Файлов для экспорта: {total}")

    safe_title = title.replace(' ', '-').replace('"', '').replace("'", "")
    filename = f"golem-{safe_title}.html"

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Голем — {title}</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }}
h1 {{ border-bottom: 2px solid #333; page-break-before: always; }}
h2 {{ border-bottom: 1px solid #666; margin-top: 30px; }}
h3 {{ margin-top: 20px; }}
blockquote {{ background: #f4f4f4; padding: 10px; border-left: 4px solid #333; }}
code {{ background: #eee; padding: 2px 4px; border-radius: 3px; }}
.toc {{ background: #fafafa; padding: 15px; border: 1px solid #ddd; page-break-after: always; }}
.file {{ margin-top: 20px; }}
@media print {{ body {{ font-size: 12pt; }} }}
</style>
</head>
<body>
<h1>Голем — {title}</h1>
<p>Собрано: {today} | Файлов: {total}</p>
<div class="toc"><h3>Содержание</h3><ol>
"""

    # Содержание
    for filepath in all_files:
        rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
        content = read_file_safe(filepath)
        if not content:
            continue
        title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        file_title = title_match.group(1).strip() if title_match else filepath.stem
        html += f'<li><a href="#{rel_path}">{file_title}</a></li>\n'
    html += '</ol></div>\n'

    # Файлы
    for i, filepath in enumerate(all_files, 1):
        rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
        content = read_file_safe(filepath)
        if not content:
            continue

        html_content = content
        html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_content)
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
        html_content = re.sub(r'\n\n', '</p><p>', html_content)
        html_content = re.sub(r'^---$', '<hr>', html_content, flags=re.MULTILINE)

        html += f'<div class="file" id="{rel_path}">\n<p>{html_content}</p>\n</div>\n'
        progress_bar(i, total, extra=f"экспорт: {rel_path[:40]}")

    html += '\n</body>\n</html>'

    output_file = OUTPUT_DIR / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    finish_progress()
    print_success(f"Книга сохранена: {output_file}")
    print_hint("Откройте в браузере. Для печати: Ctrl+P → Сохранить как PDF")


def main():
    print_header("ЭКСПОРТ КНИГИ", "📚")

    # Выбор категории
    print("\nВыберите что экспортировать:")
    for key, cat in CATEGORIES.items():
        print(f"  {key}. {cat['name']}")

    choice = input("\n> ").strip()
    if choice not in CATEGORIES:
        print_warning("Неверный выбор")
        return 1

    cat = CATEGORIES[choice]
    scan_dirs = cat["dirs"]

    # Своя папка
    if choice == "9":
        custom = input("Укажите путь от корня (например: researches/sport): ").strip()
        scan_dirs = [custom]

    # Название книги
    print(f"\nТема: {cat['name']}")
    default_title = cat["name"].split("(")[0].strip()
    title = input(f"Название книги (Enter — «{default_title}»): ").strip()
    if not title:
        title = default_title

    print()
    export_html(scan_dirs, title)
    return 0


if __name__ == "__main__":
    sys.exit(main())