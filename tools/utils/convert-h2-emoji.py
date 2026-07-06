#!/usr/bin/env python3
"""
Заменяет эмодзи в заголовках H2 (##) во всех .md файлах content/
на ![icon](icons/32/...).

Не трогает H1 (#).
Неизвестные эмодзи удаляет без замены.
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"

# Маппинг эмодзи → иконка
EMOJI_TO_ICON = {
    "\U0001F525": "scroll.png",      # 🔥
    "\U0001F4D6": "scroll.png",      # 📖
    "\U0001F524": "scroll.png",      # 🔤
    "\U0001F4DC": "scroll.png",      # 📜
    "\U0001F3DB": "book.png",        # 🏛
    "\U0001F504": "hourglass.png",   # 🔄
    "\u2694": "sword.png",           # ⚔️
    "\U0001F9E9": "anchor.png",      # 🧩
    "\u2753": "question.png",        # ❓
    "\U0001F4A1": "lamp.png",        # 💡
    "\U0001F4CA": "scales.png",      # 📊
    "\U0001F6E1": "shield.png",      # 🛡
    "\U0001F333": "vase.png",        # 🌳
    "\U0001F331": "vase.png",        # 🌱
    "\U0001F3DC": "makom.png",       # 🏜
    "\U0001F33F": "vase.png",        # 🌿
    "\U0001F34E": "vase.png",        # 🍎
    "\U0001F578": "anchor.png",      # 🕸
    "\U0001F54C": "makom.png",       # 🕌
    "\U0001F50D": "book.png",        # 🔍
    "\u23F3": "hourglass.png",       # ⏳
    "\u2705": "shield.png",          # ✅
    "\U0001F6AB": "alert.png",       # 🚫
    "\U0001F5E3": "scroll.png",      # 🗣
    "\U0001F9E0": "lamp.png",        # 🧠
    "\U0001F465": "person.png",      # 👥
    "\U0001F4B0": "scales.png",      # 💰
    "\U0001F3E6": "scales.png",      # 🏦
    "\U0001F523": "anchor.png",      # 🔣
    "\U0001F52E": "torch.png",       # 🔮
    "\U0001F30D": "geography.png",   # 🌍
    "\U0001F3AF": "track.png",       # 🎯
    "\U0001F3B5": "scroll.png",      # 🎵
    "\u2709": "scrolls.png",         # ✉️
    "\U0001F5FA": "geography.png",   # 🗺
}

# Собираем все символы эмодзи, которые есть в маппинге, для regex
KNOWN_EMOJI_PATTERN = "|".join(re.escape(e) for e in EMOJI_TO_ICON.keys())

# Общий regex для ЛЮБЫХ эмодзи (включая вариационные селекторы FE0F)
# Используем диапазоны Unicode
ANY_EMOJI_RE = re.compile(
    '[\U0001F300-\U0001F9FF'
    '\u2600-\u27BF'
    '\u2300-\u23FF'
    '\uFE00-\uFE0F'
    '\U0001FA00-\U0001FA6F'
    '\U0001F780-\U0001F7FF'
    '\U0001F800-\U0001F8FF'
    '\U0001F900-\U0001F9FF'
    '\U0001FA70-\U0001FAFF'
    '\U0001F1E0-\U0001F1FF'
    '\u2702-\u27B0'
    '\u2934-\u2935'
    '\u25AA-\u25AB'
    '\u25FB-\u25FE'
    '\u2B05-\u2B07'
    '\u2B1B-\u2B1C'
    '\u2B50'
    '\u2764'
    '\u2714'
    '\u2716'
    '\u303D'
    '\u2122'
    '\u00A9'
    '\u00AE'
    '\u2194-\u2199'
    '\u21A9-\u21AA'
    '\u231A-\u231B'
    '\u2328'
    '\u23CF'
    '\u23E9-\u23F3'
    '\u23F8-\u23FA'
    '\u24C2'
    '\u25B6'
    '\u25C0'
    '\u3030'
    '\u3297'
    '\u3299'
    ']'
    '\uFE0F?'  # опциональный вариационный селектор
)


def replace_h2_emoji(line: str) -> tuple[str, int, int]:
    """
    Обрабатывает строку заголовка H2.
    Возвращает (обработанная_строка, заменено_известных, удалено_неизвестных).
    """
    if not line.startswith("## "):
        return line, 0, 0

    # Отделяем "## " от содержимого
    content = line[3:]

    known_replaced = 0
    unknown_removed = 0

    # 1. Сначала заменяем известные эмодзи
    for emoji, icon in EMOJI_TO_ICON.items():
        # Эмодзи может идти с вариационным селектором \uFE0F
        pattern = re.escape(emoji) + '\uFE0F?'
        count = len(re.findall(pattern, content))
        if count:
            known_replaced += count
            content = re.sub(pattern, f"![icon](icons/32/{icon})", content)

    # 2. Удаляем оставшиеся неизвестные эмодзи
    remaining = ANY_EMOJI_RE.findall(content)
    unknown_removed += len(remaining)
    content = ANY_EMOJI_RE.sub('', content)

    # 3. Очищаем лишние пробелы
    content = ' '.join(content.split())

    if known_replaced == 0 and unknown_removed == 0:
        return line, 0, 0

    return f"## {content}\n", known_replaced, unknown_removed


def process_file(filepath: Path) -> dict:
    """Обрабатывает один .md файл. Возвращает статистику."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  ❌ Ошибка чтения {filepath}: {e}")
        return {"modified": False, "known": 0, "unknown": 0}

    modified = False
    total_known = 0
    total_unknown = 0
    new_lines = []

    for line in lines:
        new_line, known, unknown = replace_h2_emoji(line)
        new_lines.append(new_line)
        if known > 0 or unknown > 0:
            modified = True
            total_known += known
            total_unknown += unknown

    if not modified:
        return {"modified": False, "known": 0, "unknown": 0}

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    except Exception as e:
        print(f"  ❌ Ошибка записи {filepath}: {e}")
        return {"modified": False, "known": 0, "unknown": 0}

    return {"modified": True, "known": total_known, "unknown": total_unknown}


def main():
    if not CONTENT_DIR.exists():
        print(f"❌ Папка {CONTENT_DIR} не найдена")
        sys.exit(1)

    md_files = sorted(CONTENT_DIR.rglob("*.md"))
    print(f"🔍 Найдено .md файлов: {len(md_files)}")

    total_modified = 0
    total_known = 0
    total_unknown = 0
    modified_files = []

    for filepath in md_files:
        result = process_file(filepath)
        if result["modified"]:
            total_modified += 1
            total_known += result["known"]
            total_unknown += result["unknown"]
            modified_files.append(filepath)
            print(f"  📝 {filepath.relative_to(REPO_ROOT)} — заменено: {result['known']}, удалено: {result['unknown']}")

    print(f"\n{'='*50}")
    print(f"✅ Статистика:")
    print(f"   Файлов изменено:   {total_modified}")
    print(f"   Эмодзи заменено:   {total_known}")
    print(f"   Эмодзи удалено:    {total_unknown}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()