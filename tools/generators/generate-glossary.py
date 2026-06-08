# tools/generate-glossary.py
import sys
import re
from pathlib import Path
from datetime import datetime
from progress import show_progress, finish_progress

REPO_ROOT = Path(__file__).parent.parent
TERMINOLOGY_DIR = REPO_ROOT / "terminology"
GLOSSARY_FILE = REPO_ROOT / "GLOSSARY.md"


def extract_emoji_and_title(content: str):
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            header = line[2:].strip()
            emoji_match = re.match(r'^([\U00010000-\U0010FFFF])\s+(.+)$', header)
            if emoji_match:
                return emoji_match.group(1), emoji_match.group(2)
            return "", header
    return "", ""


def extract_topic(content: str) -> str:
    match = re.search(r'- \*\*Тема:\*\* (.+?)(?:\n|$)', content)
    if match:
        return match.group(1).strip()
    return ""


def extract_definition(content: str) -> str:
    lines = content.split('\n')
    in_metadata = True

    for line in lines:
        if in_metadata:
            if line.strip() == "" or not line.startswith('-'):
                in_metadata = False
            continue

        if line.strip() and not line.startswith('#'):
            clean = re.sub(r'^[\*\-\–]\s*', '', line)
            clean = clean.strip()
            if len(clean) > 10:
                return clean[:200]

    return ""


def main():
    print("\n📚 ГЕНЕРАЦИЯ ГЛОССАРИЯ")
    print("=" * 50)

    if not TERMINOLOGY_DIR.exists():
        print(f"❌ Папка не найдена: {TERMINOLOGY_DIR}")
        return 1

    term_files = list(TERMINOLOGY_DIR.glob("*.md"))
    total = len(term_files)
    print(f"Найдено терминов: {total}")
    print("Обработка...\n")

    terms = []
    for i, md_file in enumerate(term_files, 1):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        emoji, title = extract_emoji_and_title(content)
        topic = extract_topic(content)
        definition = extract_definition(content)

        rel_path = md_file.relative_to(REPO_ROOT)

        terms.append({
            'name': title if title else md_file.stem,
            'emoji': emoji,
            'topic': topic if topic else definition[:50],
            'definition': definition,
            'path': str(rel_path),
            'file': md_file.name
        })

        show_progress(i, total, "термины", len(terms))

    finish_progress()

    lines = [
        "# ГЛОССАРИЙ",
        "",
        "**Метаданные файла**",
        f"- **Файл:** `GLOSSARY.md`",
        f"- **Версия:** 1.0",
        f"- **Дата создания:** {datetime.now().strftime('%Y-%m-%d')}",
        f"- **Статус:** Активный",
        f"- **Тема:** Краткий справочник всех терминов",
        "",
        "---",
        "",
        "## АЛФАВИТНЫЙ УКАЗАТЕЛЬ",
        "",
    ]

    prev_letter = ""
    for term in sorted(terms, key=lambda x: x['name']):
        name = term['name'].upper()
        first_letter = name[0] if name else "#"

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
        "Глоссарий обновляется автоматически: `python tools/generate-glossary.py`"
    ])

    with open(GLOSSARY_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"\n✅ Глоссарий сохранён: {GLOSSARY_FILE}")
    print(f"✅ Всего терминов: {len(terms)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

