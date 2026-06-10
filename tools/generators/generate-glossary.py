#!/usr/bin/env python3
# tools/generators/generate-glossary.py — генерация глоссария
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_error, REPO_ROOT

TERMINOLOGY_DIR = REPO_ROOT / "terminology"
GLOSSARY_FILE = REPO_ROOT / "docs" / "GLOSSARY.md"


def extract_emoji_and_title(content: str):
    for line in content.split('\n'):
        if line.startswith('# '):
            header = line[2:].strip()
            emoji_match = re.match(r'^([^\w\s])\s+(.+)$', header)
            if emoji_match:
                return emoji_match.group(1), emoji_match.group(2)
            return "", header
    return "", ""


def extract_topic(content: str) -> str:
    match = re.search(r'[-*]\s*\*\*Тема:\*\*\s*(.+?)(?:\n|$)', content)
    return match.group(1).strip() if match else ""


def extract_definition(content: str) -> str:
    lines = content.split('\n')
    in_metadata = True
    for line in lines:
        if in_metadata:
            if not line.strip() or not line.startswith('-'):
                in_metadata = False
            continue
        if line.strip() and not line.startswith('#'):
            clean = re.sub(r'^[\*\-\–]\s*', '', line).strip()
            if len(clean) > 10:
                return clean[:200]
    return ""


def main():
    print_header("ГЕНЕРАЦИЯ ГЛОССАРИЯ", "📚")

    if not TERMINOLOGY_DIR.exists():
        print_error(f"Папка не найдена: {TERMINOLOGY_DIR}")
        return 1

    term_files = sorted(TERMINOLOGY_DIR.glob("*.md"))
    total = len(term_files)
    print(f"Найдено терминов: {total}")

    terms = []
    for i, md_file in enumerate(term_files, 1):
        content = read_file_safe(md_file)
        if not content:
            continue

        emoji, title = extract_emoji_and_title(content)
        topic = extract_topic(content)
        definition = extract_definition(content)
        rel_path = str(md_file.relative_to(REPO_ROOT)).replace('\\', '/')

        terms.append({
            'name': title or md_file.stem,
            'emoji': emoji,
            'topic': topic or definition[:50],
            'definition': definition,
            'path': rel_path,
        })

        progress_bar(i, total, extra=f"терминов: {len(terms)}")

    finish_progress()

    today = datetime.now().strftime('%Y-%m-%d')

    lines = [
        "# ГЛОССАРИЙ",
        "",
        "**Метаданные файла**",
        f"- **Файл:** `docs/GLOSSARY.md`",
        f"- **Версия:** 1.2",
        f"- **Дата создания:** 2026-06-08",
        f"- **Последнее обновление:** {today}",
        f"- **Причина обновления:** Автоматическая генерация",
        f"- **Статус:** Активный",
        f"- **Тема:** Краткий справочник всех терминов",
        "",
        "---",
        "",
        "## АЛФАВИТНЫЙ УКАЗАТЕЛЬ",
        "",
    ]

    prev_letter = ""
    for term in sorted(terms, key=lambda x: x['name'].upper()):
        name = term['name']
        first_letter = name[0].upper() if name else "#"

        if first_letter != prev_letter:
            lines.append(f"### {first_letter}")
            lines.append("")
            prev_letter = first_letter

        emoji_str = f"{term['emoji']} " if term['emoji'] else ""
        definition = term['definition'] if term['definition'] else term['topic']

        lines.append(f"- **{emoji_str}{name}** — {definition} → [подробнее]({term['path']})")

    lines.extend([
        "",
        "---",
        "",
        f"**Всего терминов:** {len(terms)}",
        "",
        "Глоссарий обновляется автоматически: `python tools/generators/generate-glossary.py`"
    ])

    GLOSSARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(GLOSSARY_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print_success(f"Сохранён: {GLOSSARY_FILE} ({len(terms)} терминов)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

