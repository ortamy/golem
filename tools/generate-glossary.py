#!/usr/bin/env python3
# generate-glossary.py — создаёт GLOSSARY.md из файлов terminology/

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).parent.parent
TERMINOLOGY_DIR = REPO_ROOT / "terminology"
GLOSSARY_FILE = REPO_ROOT / "GLOSSARY.md"


def extract_emoji_and_title(content: str) -> Tuple[str, str]:
    """Извлекает эмоджи и заголовок из первого заголовка"""
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
    """Извлекает тему из метаданных"""
    match = re.search(r'- \*\*Тема:\*\* (.+?)(?:\n|$)', content)
    if match:
        return match.group(1).strip()
    return ""


def extract_definition(content: str) -> str:
    """Извлекает краткое определение (первый абзац после метаданных)"""
    lines = content.split('\n')
    
    in_metadata = True
    definition_lines = []
    
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


def scan_terminology() -> List[Dict]:
    """Сканирует папку terminology и собирает данные"""
    terms = []
    
    if not TERMINOLOGY_DIR.exists():
        print(f"❌ Папка не найдена: {TERMINOLOGY_DIR}")
        return terms
    
    for md_file in sorted(TERMINOLOGY_DIR.glob("*.md")):
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
    
    return terms


def generate_glossary(terms: List[Dict]) -> str:
    """Генерирует содержимое GLOSSARY.md"""
    lines = [
        "# 📚 ГЛОССАРИЙ",
        "",
        "**Метаданные файла**",
        f"- **Файл:** `GLOSSARY.md`",
        f"- **Версия:** 1.0",
        f"- **Дата создания:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}",
        f"- **Статус:** Активный",
        f"- **Тема:** Краткий справочник всех терминов проекта",
        "",
        "---",
        "",
        "## 📖 АЛФАВИТНЫЙ УКАЗАТЕЛЬ",
        "",
    ]
    
    prev_letter = ""
    for term in terms:
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
        f"**📊 ИТОГО:** {len(terms)} терминов",
        "",
        "🔄 Глоссарий обновляется автоматически командой: `python3 tools/generate-glossary.py`"
    ])
    
    return '\n'.join(lines)


def main():
    print("📚 ГЕНЕРАЦИЯ ГЛОССАРИЯ")
    print("======================")
    print("")
    
    terms = scan_terminology()
    print(f"📊 Найдено терминов: {len(terms)}")
    
    if not terms:
        print("❌ Нет терминов для генерации")
        return
    
    glossary_content = generate_glossary(terms)
    
    with open(GLOSSARY_FILE, 'w', encoding='utf-8') as f:
        f.write(glossary_content)
    
    print(f"✅ Создан: {GLOSSARY_FILE}")
    print(f"📝 Проверьте результат и сделайте git commit")


if __name__ == "__main__":
    main()
