#!/usr/bin/env python3
# generate-standardize-names.py — стандартизация имён файлов (v1.0)

import os
import re
import sys
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESEARCHES = ROOT / "researches"
TERMINOLOGY = ROOT / "terminology"
CSV_OUT = ROOT / "tools" / "cache" / "rename-map.csv"

# Словарь для автоматического перевода частых русских слов
WORD_MAP = {
    "исследование": "research",
    "разоблачение": "exposure",
    "подмена": "substitution",
    "система": "system",
    "история": "history",
    "происхождение": "origin",
    "учение": "teaching",
    "культ": "cult",
    "религия": "religion",
    "власть": "power",
    "контроль": "control",
    "деньги": "money",
    "война": "war",
    "рабство": "slavery",
    "свобода": "freedom",
    "закон": "law",
    "язык": "language",
    "текст": "text",
    "перевод": "translation",
    "обман": "deception",
    "ловушка": "trap",
    "оружие": "weapon",
    "знак": "sign",
    "символ": "symbol",
    "имя": "name",
    "кровь": "blood",
    "смерть": "death",
    "жизнь": "life",
    "мир": "peace",
    "правда": "truth",
    "ложь": "lie",
    "вера": "faith",
    "грех": "sin",
    "суд": "judgment",
    "храм": "temple",
    "церковь": "church",
    "крест": "cross",
    "дух": "spirit",
    "душа": "soul",
    "тело": "body",
    "сердце": "heart",
    "разум": "mind",
    "время": "time",
    "земля": "earth",
    "небо": "heaven",
    "огонь": "fire",
    "вода": "water",
    "народ": "nation",
    "царь": "king",
    "царство": "kingdom",
    "пророк": "prophet",
    "апостол": "apostle",
    "завет": "covenant",
    "спасение": "salvation",
    "покаяние": "repentance",
    "молитва": "prayer",
    "пост": "fasting",
    "праздник": "holiday",
    "суббота": "sabbath",
    "жертва": "sacrifice",
    "благодать": "grace",
    "милость": "mercy",
    "любовь": "love",
    "надежда": "hope",
    "страх": "fear",
    "радость": "joy",
    "мир": "world",
    "человек": "human",
    "женщина": "woman",
    "мужчина": "man",
    "ребёнок": "child",
    "семья": "family",
    "дом": "house",
    "город": "city",
    "страна": "country",
    "империя": "empire",
    "власть": "authority",
    "правительство": "government",
    "армия": "army",
    "полиция": "police",
    "тюрьма": "prison",
    "школа": "school",
    "больница": "hospital",
    "банк": "bank",
    "деньги": "currency",
    "золото": "gold",
    "серебро": "silver",
    "экономика": "economy",
    "рынок": "market",
    "торговля": "trade",
    "наука": "science",
    "медицина": "medicine",
    "технология": "technology",
    "интернет": "internet",
    "компьютер": "computer",
    "игра": "game",
    "спорт": "sport",
    "музыка": "music",
    "фильм": "film",
    "книга": "book",
    "газета": "newspaper",
    "телевидение": "television",
    "реклама": "advertising",
    "новости": "news",
    "социальный": "social",
    "сеть": "network",
    "цифровой": "digital",
    "искусственный": "artificial",
    "интеллект": "intelligence",
    "робот": "robot",
    "машина": "machine",
    "оружие": "arms",
    "ядерный": "nuclear",
    "космос": "space",
    "планета": "planet",
    "звезда": "star",
    "вселенная": "universe",
    "природа": "nature",
    "животное": "animal",
    "растение": "plant",
    "еда": "food",
    "напиток": "drink",
    "одежда": "clothing",
    "орудие": "tool",
    "оружие": "weaponry",
    "здание": "building",
    "мост": "bridge",
    "дорога": "road",
    "путь": "way",
    "река": "river",
    "море": "sea",
    "гора": "mountain",
    "лес": "forest",
    "пустыня": "desert",
    "сад": "garden",
    "дерево": "tree",
    "плод": "fruit",
    "хлеб": "bread",
    "вино": "wine",
    "масло": "oil",
    "соль": "salt",
    "свет": "light",
    "тьма": "darkness",
    "день": "day",
    "ночь": "night",
    "утро": "morning",
    "вечер": "evening",
    "год": "year",
    "месяц": "month",
    "неделя": "week",
    "час": "hour",
    "минута": "minute",
    "секунда": "second",
    "начало": "beginning",
    "конец": "end",
    "первый": "first",
    "последний": "last",
    "новый": "new",
    "старый": "old",
    "великий": "great",
    "малый": "small",
    "добрый": "good",
    "злой": "evil",
    "красивый": "beautiful",
    "уродливый": "ugly",
    "богатый": "rich",
    "бедный": "poor",
    "сильный": "strong",
    "слабый": "weak",
    "умный": "smart",
    "глупый": "stupid",
    "быстрый": "fast",
    "медленный": "slow",
    "горячий": "hot",
    "холодный": "cold",
    "сухой": "dry",
    "мокрый": "wet",
    "твёрдый": "hard",
    "мягкий": "soft",
    "острый": "sharp",
    "тупой": "blunt",
    "чистый": "clean",
    "грязный": "dirty",
    "святой": "holy",
    "грешный": "sinful",
    "праведный": "righteous",
    "нечестивый": "wicked",
    "верный": "faithful",
    "неверный": "unfaithful",
    "истинный": "true",
    "ложный": "false",
    "правильный": "correct",
    "неправильный": "wrong",
    "возможный": "possible",
    "невозможный": "impossible",
    "нужный": "necessary",
    "ненужный": "unnecessary",
    "важный": "important",
    "неважный": "unimportant",
    "интересный": "interesting",
    "скучный": "boring",
    "простой": "simple",
    "сложный": "complex",
    "лёгкий": "easy",
    "трудный": "difficult",
    "открытый": "open",
    "закрытый": "closed",
    "свободный": "free",
    "занятый": "busy",
    "живой": "alive",
    "мёртвый": "dead",
    "молодой": "young",
    "старый": "ancient",
    "большой": "big",
    "маленький": "little",
    "длинный": "long",
    "короткий": "short",
    "высокий": "high",
    "низкий": "low",
    "широкий": "wide",
    "узкий": "narrow",
    "глубокий": "deep",
    "мелкий": "shallow",
    "тяжёлый": "heavy",
    "лёгкий": "lightweight",
    "толстый": "thick",
    "тонкий": "thin",
    "полный": "full",
    "пустой": "empty",
    "целый": "whole",
    "сломанный": "broken",
    "мокрый": "damp",
    "сухой": "arid",
}


def has_russian(text):
    return bool(re.search(r'[а-яё]', text, re.IGNORECASE))


def extract_english_hint(filepath):
    """Извлечь подсказку для английского имени из H1 и темы."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return ""
    
    # H1
    h1_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    h1 = h1_match.group(1) if h1_match else ""
    
    # Тема
    topic_match = re.search(r'\*\*Тема:\*\*\s*(.+?)(?:\n|$)', content)
    topic = topic_match.group(1) if topic_match else ""
    
    # Ивритское слово из H1 (в скобках или отдельно)
    hebrew_match = re.search(r'[א-ת]{2,}', h1)
    hebrew_word = hebrew_match.group(0) if hebrew_match else ""
    
    return h1, topic, hebrew_word


def suggest_name(filepath):
    """Предложить английское имя на основе содержимого."""
    h1, topic, hebrew_word = extract_english_hint(filepath)
    current_name = filepath.stem
    
    # Если имя уже правильное — не трогаем
    if not has_russian(current_name) and ' ' not in current_name and '_' not in current_name:
        return None
    
    # Если есть ивритское слово — используем его как основу
    if hebrew_word:
        # Транслитерация иврита + английское слово из темы
        topic_words = topic.lower().split() if topic else []
        eng_topic = '_'.join([WORD_MAP.get(w, w) for w in topic_words[:2] if w in WORD_MAP])
        if eng_topic:
            return f"{current_name.split('-')[0]}-{eng_topic}" if '-' in current_name else f"{current_name}-{eng_topic}"
        return current_name  # не можем предложить — оставляем
    
    # Переводим русские слова через словарь
    parts = re.split(r'[-_\s]+', current_name.lower())
    eng_parts = []
    for part in parts:
        if has_russian(part):
            translated = WORD_MAP.get(part, part)
            eng_parts.append(translated)
        else:
            eng_parts.append(part)
    
    # Убираем дубликаты и обрезаем до 4 слов
    seen = set()
    unique = []
    for p in eng_parts:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    unique = unique[:4]
    
    return '-'.join(unique)


def scan_files():
    """Сканировать файлы и найти нарушения."""
    violations = []
    scan_dirs = [RESEARCHES, TERMINOLOGY]
    
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for md_file in sorted(scan_dir.rglob("*.md")):
            name = md_file.stem
            if has_russian(name) or ' ' in name or '_' in name:
                suggestion = suggest_name(md_file)
                violations.append({
                    'current': str(md_file.relative_to(ROOT)).replace('\\', '/'),
                    'suggested': suggestion or name,
                    'confirmed': '',
                })
    
    return violations


def update_links(old_path, new_path):
    """Обновить все ссылки в .md файлах."""
    md_files = []
    for d in ['researches', 'terminology', 'instructions', 'docs']:
        dp = ROOT / d
        if dp.exists():
            md_files.extend(dp.rglob("*.md"))
    
    old_rel = str(old_path).replace('\\', '/')
    new_rel = str(new_path).replace('\\', '/')
    
    count = 0
    for f in md_files:
        try:
            content = f.read_text(encoding='utf-8')
            if old_rel in content:
                content = content.replace(old_rel, new_rel)
                f.write_text(content, encoding='utf-8')
                count += 1
        except Exception:
            pass
    
    return count


def main():
    if '--apply' in sys.argv:
        # Применить переименования из CSV
        if not CSV_OUT.exists():
            print(f"❌ CSV не найден: {CSV_OUT}")
            print("Сначала запусти без --apply для генерации CSV")
            sys.exit(1)
        
        with open(CSV_OUT, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        renamed = 0
        links_updated = 0
        
        for row in rows:
            if row.get('confirmed', '').strip().lower() != 'yes':
                continue
            
            old_path = ROOT / row['current']
            new_name = row['suggested']
            
            if not old_path.exists():
                print(f"⚠️  Пропущен (не найден): {row['current']}")
                continue
            
            new_path = old_path.parent / f"{new_name}.md"
            
            if new_path.exists():
                print(f"⚠️  Пропущен (уже существует): {new_path.relative_to(ROOT)}")
                continue
            
            old_path.rename(new_path)
            renamed += 1
            print(f"✅ {row['current']} → {new_path.relative_to(ROOT)}")
            
            # Обновить ссылки
            links = update_links(
                Path(row['current']),
                Path(str(new_path.relative_to(ROOT)).replace('\\', '/'))
            )
            links_updated += links
        
        print(f"\n✅ Переименовано: {renamed} файлов")
        print(f"✅ Ссылок обновлено в: {links_updated} файлах")
    
    else:
        # Сканировать и создать CSV
        violations = scan_files()
        
        if not violations:
            print("✅ Все имена файлов соответствуют стандарту.")
            return
        
        print(f"🔍 Найдено нарушений: {len(violations)}\n")
        
        with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['current', 'suggested', 'confirmed'])
            writer.writeheader()
            
            for v in violations:
                writer.writerow({
                    'current': v['current'],
                    'suggested': v['suggested'],
                    'confirmed': '',
                })
                print(f"  {v['current']}")
                print(f"  → {v['suggested']}")
                print()
        
        print(f"📄 CSV создан: {CSV_OUT}")
        print("1. Отредактируй CSV — исправь предлагаемые имена")
        print("2. В колонке 'confirmed' напиши 'yes' для подтверждения")
        print("3. Запусти: python tools/generators/generate-standardize-names.py --apply")


if __name__ == "__main__":
    main()