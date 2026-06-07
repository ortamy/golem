```python
#!/usr/bin/env python3
# tanakh-validator.py — проверка утверждений по ТаНаХу

import sys
import re
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
TANAKH_DB = TOOLS_DIR / "tanakh.db"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
NC = "\033[0m"
BOLD = "\033[1m"


def init_db():
    """Создаёт базу данных ТаНаХа"""
    conn = sqlite3.connect(TANAKH_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY,
            book TEXT,
            chapter INTEGER,
            verse INTEGER,
            hebrew TEXT,
            transliteration TEXT,
            translation TEXT
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_book_chapter ON verses(book, chapter)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hebrew ON verses(hebrew)')
    
    conn.commit()
    return conn


def load_tanakh_from_files():
    """Загружает ТаНаХ из файлов репозитория (если есть)"""
    # TODO: парсить файлы с ивритскими стихами
    # Пока заглушка с базовыми стихами
    verses = [
        ("Берешит", 1, 1, "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ", 
         "Берешит бара Элоhим эт hа-шамаим вэ-эт hа-арец", 
         "В начале сотворил Всесильный небо и землю"),
        ("Дварим", 6, 4, "שְׁמַע יִשְׂרָאֵל יְהוָה אֱלֹהֵינוּ יְהוָה אֶחָד",
         "Шма Исраэль, Яхве Элоhейну, Яхве эхад",
         "Слушай, Исраэль: Яхве — Всесильный наш, Яхве един"),
        ("Шмот", 20, 2, "אָנֹכִי יְהוָה אֱלֹהֶיךָ אֲשֶׁר הוֹצֵאתִיךָ מֵאֶרֶץ מִצְרַיִם מִבֵּית עֲבָדִים",
         "Анохи Яхве Элоhеха ашер hоцеитиха ме-эрец Мицраим ми-бейт авадим",
         "Я — Яхве, Всесильный твой, который вывел тебя из земли Мицраим, из дома рабства"),
        ("Ваикра", 19, 18, "וְאָהַבְתָּ לְרֵעֲךָ כָּמוֹךָ",
         "Ве-аhавта ле-реаха камоха",
         "И люби ближнего твоего как самого себя"),
        ("Ваикра", 19, 11, "לֹא תִּגְנֹבוּ וְלֹא תְכַחֲשׁוּ וְלֹא תְשַׁקְּרוּ אִישׁ בַּעֲמִיתוֹ",
         "Ло тигневу ве-ло техахашу ве-ло тешакеру иш ба-амито",
         "Не крадите, не обманывайте, не лгите человеку ближнему своему"),
    ]
    
    conn = init_db()
    cursor = conn.cursor()
    
    for verse in verses:
        cursor.execute('''
            INSERT OR REPLACE INTO verses (book, chapter, verse, hebrew, transliteration, translation)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', verse)
    
    conn.commit()
    return conn


def find_verse(conn, book, chapter, verse):
    """Находит стих по ссылке"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM verses WHERE book = ? AND chapter = ? AND verse = ?', 
                   (book, chapter, verse))
    return cursor.fetchone()


def search_hebrew(conn, word):
    """Ищет слово в ивритском тексте"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM verses WHERE hebrew LIKE ?', (f'%{word}%',))
    return cursor.fetchall()


def check_statement(statement: str) -> dict:
    """Проверяет утверждение на соответствие ТаНаХу"""
    # Ищем ссылки на стихи
    pattern = r'([\u0590-\u05FFa-zA-Zа-яА-Я]+)\s+(\d+):(\d+)'
    matches = re.findall(pattern, statement)
    
    results = {
        'statement': statement,
        'verses': [],
        'is_valid': None,
        'errors': []
    }
    
    conn = load_tanakh_from_files()
    
    for book, chapter, verse in matches:
        result = find_verse(conn, book, int(chapter), int(verse))
        if result:
            results['verses'].append({
                'reference': f"{book} {chapter}:{verse}",
                'hebrew': result[4],
                'transliteration': result[5],
                'translation': result[6]
            })
        else:
            results['errors'].append(f"Стих {book} {chapter}:{verse} не найден в базе")
    
    return results


def validate_md_file(file_path: Path) -> list:
    """Проверяет все утверждения в md-файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем цитаты стихов
    verse_pattern = r'[（(]?([\u0590-\u05FFa-zA-Zа-яА-Я]+)\s+(\d+):(\d+)[）)]?'
    references = re.findall(verse_pattern, content)
    
    results = []
    conn = load_tanakh_from_files()
    
    for book, chapter, verse in set(references):
        result = find_verse(conn, book, int(chapter), int(verse))
        if result:
            results.append({
                'reference': f"{book} {chapter}:{verse}",
                'found': True,
                'hebrew': result[4],
                'translation': result[6]
            })
        else:
            results.append({
                'reference': f"{book} {chapter}:{verse}",
                'found': False,
                'error': f"Стих не найден в базе"
            })
    
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Проверка утверждений по ТаНаХу')
    parser.add_argument('--file', '-f', type=str, help='Проверить md-файл')
    parser.add_argument('--verse', '-v', type=str, help='Проверить конкретный стих (например: "Берешит 1:1")')
    parser.add_argument('--search', '-s', type=str, help='Поиск слова в ТаНаХе')
    parser.add_argument('--init-db', action='store_true', help='Инициализировать базу данных')
    args = parser.parse_args()
    
    if args.init_db:
        print("Инициализация базы данных ТаНаХа...")
        load_tanakh_from_files()
        print(f"✅ База создана: {TANAKH_DB}")
        return
    
    if args.search:
        conn = load_tanakh_from_files()
        results = search_hebrew(conn, args.search)
        print(f"\n🔍 ПОИСК: {args.search}")
        print("=" * 50)
        for r in results:
            print(f"\n📖 {r[1]} {r[2]}:{r[3]}")
            print(f"   {r[4]}")
            print(f"   {r[5]}")
            print(f"   {r[6]}")
        return
    
    if args.verse:
        parts = args.verse.split()
        if len(parts) >= 2:
            book = parts[0]
            chapter_verse = parts[1].split(':')
            if len(chapter_verse) == 2:
                chapter = int(chapter_verse[0])
                verse = int(chapter_verse[1])
                
                conn = load_tanakh_from_files()
                result = find_verse(conn, book, chapter, verse)
                
                if result:
                    print(f"\n📖 {book} {chapter}:{verse}")
                    print("=" * 50)
                    print(f"   Иврит: {result[4]}")
                    print(f"   Транслитерация: {result[5]}")
                    print(f"   Перевод: {result[6]}")
                else:
                    print(f"❌ Стих {args.verse} не найден в базе")
        return
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ Файл не найден: {args.file}")
            return
        
        results = validate_md_file(file_path)
        
        print(f"\n📋 ПРОВЕРКА ФАЙЛА: {file_path.name}")
        print("=" * 50)
        
        found = [r for r in results if r['found']]
        missing = [r for r in results if not r['found']]
        
        if found:
            print(f"\n✅ НАЙДЕНЫ СТИХИ ({len(found)}):")
            for r in found:
                print(f"   • {r['reference']}")
        
        if missing:
            print(f"\n❌ НЕ НАЙДЕНЫ В БАЗЕ ({len(missing)}):")
            for r in missing:
                print(f"   • {r['reference']} - {r['error']}")
        
        if not results:
            print("\n⚠️ В файле не найдено ссылок на стихи ТаНаХа")
        
        return
    
    print(__doc__)


if __name__ == "__main__":
    main()
```

Сохрани как tools/tanakh-validator.py и запусти:

```bash
# Инициализация базы
python tanakh-validator.py --init-db

# Проверить стих
python tanakh-validator.py --verse "Дварим 6:4"

# Поиск слова
python tanakh-validator.py --search "שְׁמַע"

# Проверить md-файл
python tanakh-validator.py --file ../researches/abstract-gods-vs-yhwh.md
```

Что умеет:

· инициализировать базу данных ТаНаХа
· проверять отдельный стих (иврит, транслитерация, перевод)
· искать слова в ивритском тексте
· проверять md-файл на наличие корректных ссылок на стихи

TODO: загрузить полный ТаНаХ в базу (сейчас только 5 стихов для примера).