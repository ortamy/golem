#!/usr/bin/env python3
# tools/generators/generate-book.py — генератор HTML-книги из терминов и исследований
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_error, print_hint,
    REPO_ROOT
)

OUTPUT_DIR = REPO_ROOT / "web" / "export"
SOURCE_DIRS = ["terminology", "researches"]
IGNORE_FILES = {"README.md", "STRUCTURE.md", "GLOSSARY.md", "CHANGELOG.md", "INDEX.md"}

# Ивритские паттерны для автоопределения
HEBREW_PATTERN = re.compile(r'[\u0590-\u05FF]{3,}')


def extract_title(content: str) -> str:
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        title = re.sub(r'[\U0001F000-\U0001FFFF]', '', title).strip()
        return title
    return ""


def extract_body(content: str) -> str:
    """Извлекает тело без метаданных, навигации, связанных файлов."""
    body = re.sub(r'\*\*Метаданные файла\*\*.*?\n---\n', '', content, flags=re.DOTALL)
    body = re.sub(r'<!-- NAVIGATION.*?-->', '', body, flags=re.DOTALL)
    body = re.sub(r'\n---\n\n## 🔗 СВЯЗАННЫЕ ФАЙЛЫ.*$', '', body, flags=re.DOTALL)
    body = re.sub(r'^#\s+.*$', '', body, flags=re.MULTILINE)
    return body.strip()


def wrap_hebrew(text: str) -> str:
    """Оборачивает ивритские фрагменты в span с RTL."""
    return HEBREW_PATTERN.sub(r'<span class="hebrew">\g<0></span>', text)


def markdown_to_html(text: str) -> str:
    """Конвертирует Markdown в HTML (улучшенная версия)."""
    lines = text.split('\n')
    html_lines = []
    in_list = False
    in_ordered_list = False

    for line in lines:
        stripped = line.strip()

        # Пустые строки
        if not stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if in_ordered_list:
                html_lines.append('</ol>')
                in_ordered_list = False
            continue

        # Заголовки
        if stripped.startswith('#### '):
            if in_list: html_lines.append('</ul>'); in_list = False
            html_lines.append(f'<h4>{stripped[5:]}</h4>')
            continue
        if stripped.startswith('### '):
            if in_list: html_lines.append('</ul>'); in_list = False
            html_lines.append(f'<h3>{stripped[4:]}</h3>')
            continue
        if stripped.startswith('## '):
            if in_list: html_lines.append('</ul>'); in_list = False
            html_lines.append(f'<h2>{stripped[3:]}</h2>')
            continue

        # Цитаты
        if stripped.startswith('> '):
            if in_list: html_lines.append('</ul>'); in_list = False
            html_lines.append(f'<blockquote>{stripped[2:]}</blockquote>')
            continue

        # Горизонтальная линия
        if stripped == '---':
            if in_list: html_lines.append('</ul>'); in_list = False
            html_lines.append('<hr>')
            continue

        # Списки
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = stripped[2:]
            html_lines.append(f'<li>{content}</li>')
            continue

        if re.match(r'^\d+\.\s', stripped):
            if not in_ordered_list:
                html_lines.append('<ol>')
                in_ordered_list = True
            content = re.sub(r'^\d+\.\s', '', stripped)
            html_lines.append(f'<li>{content}</li>')
            continue

        # Обычный текст
        if in_list:
            html_lines.append('</ul>')
            in_list = False
        if in_ordered_list:
            html_lines.append('</ol>')
            in_ordered_list = False

        html_lines.append(f'<p>{stripped}</p>')

    # Закрываем открытые списки
    if in_list:
        html_lines.append('</ul>')
    if in_ordered_list:
        html_lines.append('</ol>')

    html = '\n'.join(html_lines)

    # Инлайн-форматирование
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # Оборачиваем иврит
    html = wrap_hebrew(html)

    # Убираем пустые параграфы
    html = re.sub(r'<p>\s*</p>', '', html)

    return html


def export_html(files: dict) -> str:
    """Генерирует HTML-книгу."""
    today = datetime.now().strftime("%Y-%m-%d")

    html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Golem Book — {today}</title>
<style>
body {{ font-family: 'Georgia', serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.7; color: #1a1a1a; background: #fff; }}
h1 {{ font-size: 24px; margin-top: 40px; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
h2 {{ font-size: 18px; margin-top: 30px; }}
h3 {{ font-size: 15px; margin-top: 25px; }}
h4 {{ font-size: 13px; margin-top: 20px; color: #c7512e; }}
p {{ margin: 10px 0; }}
blockquote {{ border-left: 3px solid #c7512e; padding: 10px 15px; margin: 15px 0; background: #f9f6f3; font-style: italic; }}
code {{ background: #f5f5f5; padding: 2px 5px; font-size: 13px; color: #c7512e; }}
strong {{ color: #c7512e; }}
em {{ color: #555; }}
a {{ color: #c7512e; text-decoration: none; border-bottom: 1px solid #c7512e; }}
a:hover {{ opacity: 0.7; }}
ul, ol {{ margin: 10px 0 10px 20px; }}
li {{ margin: 5px 0; }}
hr {{ border: none; border-top: 1px solid #ddd; margin: 20px 0; }}
.hebrew {{ font-family: 'Times New Roman', serif; direction: rtl; unicode-bidi: embed; font-size: 16px; }}
.toc {{ background: #f9f6f3; padding: 20px; margin: 20px 0; border-radius: 5px; }}
.toc a {{ display: block; padding: 3px 0; border-bottom: none; }}
.page-break {{ page-break-before: always; }}
.source {{ font-size: 11px; color: #999; margin-bottom: 20px; }}
.footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #999; text-align: center; }}
@media print {{ body {{ font-size: 12px; }} h1 {{ page-break-before: always; }} }}
</style>
</head>
<body>
<h1>📜 GOLEM BOOK</h1>
<p>Собрание терминов и исследований проекта «Голем»</p>
<p><strong>Дата:</strong> {today}</p>
<p><strong>Файлов:</strong> {len(files)}</p>

<div class="toc">
<h2>Содержание</h2>
'''

    # Оглавление
    for i, (filepath, content) in enumerate(files.items(), 1):
        title = extract_title(content) or filepath
        anchor = f"section-{i}"
        html += f'<a href="#{anchor}">{i}. {title}</a>\n'

    html += '</div>\n'

    # Содержание
    for i, (filepath, content) in enumerate(files.items(), 1):
        title = extract_title(content) or filepath
        anchor = f"section-{i}"
        body = extract_body(content)
        body_html = markdown_to_html(body)

        html += f'<div class="page-break"></div>\n'
        html += f'<h1 id="{anchor}">{title}</h1>\n'
        html += f'<p class="source">📄 {filepath}</p>\n'
        html += body_html + '\n'

    html += f'<div class="footer">Golem Book — {today} — {len(files)} файлов</div>\n</body>\n</html>'

    return html


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 0

    print_header("ЭКСПОРТ КНИГИ", "📖")

    files = {}
    for sd in SOURCE_DIRS:
        dp = REPO_ROOT / sd
        if dp.exists():
            for f in sorted(dp.rglob("*.md")):
                if f.name in IGNORE_FILES:
                    continue
                content = read_file_safe(f)
                if content and len(content) > 200:
                    rel = str(f.relative_to(REPO_ROOT)).replace('\\', '/')
                    files[rel] = content

    total = len(files)
    print(f"📁 Файлов: {total}")

    if total == 0:
        print_error("Файлы не найдены")
        return 1

    if limit and limit < total:
        # Берём первые N файлов
        files = dict(list(files.items())[:limit])
        print(f"📏 Ограничение: {limit} файлов")

    print("📝 Генерация HTML...")
    html = export_html(files)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Версия с датой
    output_file = OUTPUT_DIR / f"golem-book-{datetime.now().strftime('%Y%m%d')}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    # Последняя версия
    latest = OUTPUT_DIR / "golem-book.html"
    with open(latest, 'w', encoding='utf-8') as f:
        f.write(html)

    size_kb = output_file.stat().st_size / 1024
    print_success(f"Книга сохранена: {output_file} ({size_kb:.0f} КБ)")
    print_success(f"Последняя версия: {latest}")
    print_hint(f"Открыть: http://localhost:8080/export/{latest.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())