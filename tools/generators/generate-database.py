#!/usr/bin/env python3
# tools/generators/generate-database.py — создание базы знаний проекта «Голем»

import sqlite3
import re
import hashlib
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT = ROOT / "content"
DB_PATH = ROOT / "tools" / "data" / "golem.db"

def create_tables(cursor):
    """Создаёт все таблицы базы данных."""
    
    # Основная таблица файлов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            title TEXT,
            category TEXT,
            subcategory TEXT,
            status TEXT DEFAULT 'Активный',
            version TEXT DEFAULT '1.0',
            topic TEXT,
            level TEXT DEFAULT '🟡 Средний',
            hash TEXT,
            created TEXT,
            updated TEXT,
            content_preview TEXT
        )
    """)
    
    # Учения (метод дерева)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER UNIQUE NOT NULL,
            seed TEXT,
            soil TEXT,
            roots TEXT,
            trunk TEXT,
            branches TEXT,
            fruits TEXT,
            verdict TEXT,
            key_verse TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    """)
    
    # Терминология
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS terminology (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER UNIQUE NOT NULL,
            hebrew_word TEXT,
            transliteration TEXT,
            root_letters TEXT,
            meaning TEXT,
            first_occurrence TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    """)
    
    # Личности
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER UNIQUE NOT NULL,
            name_hebrew TEXT,
            name_meaning TEXT,
            period TEXT,
            role TEXT,
            key_events TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    """)
    
    # События
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER UNIQUE NOT NULL,
            name_hebrew TEXT,
            date_period TEXT,
            location TEXT,
            participants TEXT,
            result TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    """)
    
    # Книги
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER UNIQUE NOT NULL,
            name_hebrew TEXT,
            author TEXT,
            chapters INTEGER,
            section TEXT,
            key_themes TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    """)
    
    # Связи между файлами
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file_id INTEGER NOT NULL,
            target_file_id INTEGER,
            target_path TEXT,
            link_type TEXT DEFAULT 'related',
            FOREIGN KEY (source_file_id) REFERENCES files(id)
        )
    """)
    
    # Стихи ТаНаХа (извлечённые из файлов)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            reference TEXT NOT NULL,
            book TEXT,
            chapter INTEGER,
            verse INTEGER,
            text_hebrew TEXT,
            text_transliteration TEXT,
            text_russian TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    """)
    
    # Религионимы (найденные в файлах)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS religionisms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            replacement TEXT,
            count INTEGER DEFAULT 1,
            last_check TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id)
        )
    """)
    
    # Индексы для быстрого поиска
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_category ON files(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_status ON files(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_teachings_verdict ON teachings(verdict)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_teachings_fruits ON teachings(fruits)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_verses_reference ON verses(reference)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_verses_book ON verses(book)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_file_id)")


def parse_metadata(content):
    """Извлекает метаданные из .md файла."""
    meta = {}
    
    patterns = {
        "title": r'^#\s+(.+?)$',
        "status": r'\*\*Статус:\*\*\s*(.+?)(?:\n|$)',
        "version": r'\*\*Версия:\*\*\s*(.+?)(?:\n|$)',
        "topic": r'\*\*Тема:\*\*\s*(.+?)(?:\n|$)',
        "level": r'\*\*Уровень:\*\*\s*(.+?)(?:\n|$)',
        "created": r'\*\*Дата создания:\*\*\s*(.+?)(?:\n|$)',
        "updated": r'\*\*Последнее обновление:\*\*\s*(.+?)(?:\n|$)',
        "hash": r'\*\*Хеш:\*\*\s*(.+?)(?:\n|$)',
        "tree_health": r'\*\*Tree-Health:\*\*\s*(.+?)(?:\n|$)',
        "related": r'\*\*Связанные файлы:\*\*\s*(.+?)(?:\n|$)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            meta[key] = match.group(1).strip()
    
    return meta


def parse_hebrew_word(content):
    """Извлекает ивритское слово из заголовка термина."""
    match = re.search(r'^#\s+[^\s]*\s+([\u0590-\u05FF]{2,})', content, re.MULTILINE)
    if match:
        return match.group(1)
    
    match = re.search(r'[\u0590-\u05FF]{2,}', content)
    if match:
        return match.group(0)
    
    return None


def parse_verses(content):
    """Извлекает ссылки на стихи из текста."""
    verses = []
    
    # Паттерны: Берешит 1:1, Йешаяhу 53:5, Теhиллим 23:1
    pattern = r'([א-תA-Za-z]+)\s+(\d+):(\d+)'
    
    for match in re.finditer(pattern, content):
        book = match.group(1)
        chapter = int(match.group(2))
        verse = int(match.group(3))
        reference = f"{book} {chapter}:{verse}"
        verses.append({
            "reference": reference,
            "book": book,
            "chapter": chapter,
            "verse": verse,
        })
    
    return verses


def fill_database(cursor, rebuild=False):
    """Наполняет базу данных из .md файлов."""
    
    if rebuild:
        cursor.execute("DELETE FROM links")
        cursor.execute("DELETE FROM religionisms")
        cursor.execute("DELETE FROM verses")
        cursor.execute("DELETE FROM teachings")
        cursor.execute("DELETE FROM terminology")
        cursor.execute("DELETE FROM persons")
        cursor.execute("DELETE FROM events")
        cursor.execute("DELETE FROM books")
        cursor.execute("DELETE FROM files")
    
    stats = {
        "files": 0,
        "teachings": 0,
        "terminology": 0,
        "persons": 0,
        "events": 0,
        "books": 0,
        "verses": 0,
        "links": 0,
    }
    
    all_files = sorted(CONTENT.rglob("*.md"))
    total = len(all_files)
    
    for i, md_file in enumerate(all_files, 1):
        if md_file.name in ["README.md", "STRUCTURE.md", "GLOSSARY.md", "CHANGELOG.md"]:
            continue
        
        rel_path = str(md_file.relative_to(ROOT)).replace("\\", "/")
        
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        
        meta = parse_metadata(content)
        
        # Определяем категорию из пути
        parts = rel_path.split("/")
        category = parts[1] if len(parts) > 1 else ""
        subcategory = parts[2] if len(parts) > 2 else ""
        
        # Вставляем файл
        cursor.execute("""
            INSERT OR REPLACE INTO files (path, filename, title, category, subcategory, status, version, topic, level, hash, created, updated, content_preview)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rel_path,
            md_file.stem,
            meta.get("title", md_file.stem.replace("-", " ")),
            category,
            subcategory,
            meta.get("status", "Активный"),
            meta.get("version", "1.0"),
            meta.get("topic", ""),
            meta.get("level", "🟡 Средний"),
            meta.get("hash", ""),
            meta.get("created", ""),
            meta.get("updated", ""),
            content[content.find("---\n") + 4:content.find("---\n") + 200] if "---\n" in content else content[:200],
        ))
        
        file_id = cursor.lastrowid
        stats["files"] += 1
        
        # Заполняем специфичные таблицы
        if category == "teachings" or subcategory == "teachings":
            tree = meta.get("tree_health", "")
            tree_parts = {}
            for part in tree.split(","):
                part = part.strip()
                if "=" in part:
                    key, val = part.split("=")
                    tree_parts[key.strip()] = val.strip()
            
            cursor.execute("""
                INSERT OR REPLACE INTO teachings (file_id, seed, soil, roots, trunk, branches, fruits, verdict, key_verse)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_id,
                tree_parts.get("seed", "black"),
                tree_parts.get("soil", "black"),
                tree_parts.get("roots", "black"),
                tree_parts.get("trunk", "black"),
                tree_parts.get("branches", "black"),
                tree_parts.get("fruits", "black"),
                None,
                None,
            ))
            stats["teachings"] += 1
        
        elif category == "terminology":
            hebrew = parse_hebrew_word(content)
            cursor.execute("""
                INSERT OR REPLACE INTO terminology (file_id, hebrew_word)
                VALUES (?, ?)
            """, (file_id, hebrew))
            stats["terminology"] += 1
        
        elif category == "tanakh" and subcategory == "persons":
            cursor.execute("""
                INSERT OR REPLACE INTO persons (file_id)
                VALUES (?)
            """, (file_id,))
            stats["persons"] += 1
        
        elif category == "tanakh" and subcategory == "events":
            cursor.execute("""
                INSERT OR REPLACE INTO events (file_id)
                VALUES (?)
            """, (file_id,))
            stats["events"] += 1
        
        elif category == "tanakh" and subcategory == "books":
            cursor.execute("""
                INSERT OR REPLACE INTO books (file_id)
                VALUES (?)
            """, (file_id,))
            stats["books"] += 1
        
        # Извлекаем стихи
        for verse_data in parse_verses(content):
            cursor.execute("""
                INSERT INTO verses (file_id, reference, book, chapter, verse)
                VALUES (?, ?, ?, ?, ?)
            """, (
                file_id,
                verse_data["reference"],
                verse_data["book"],
                verse_data["chapter"],
                verse_data["verse"],
            ))
            stats["verses"] += 1
        
        # Извлекаем связанные файлы
        related = meta.get("related", "")
        for related_path in re.findall(r'`([^`]+)`', related):
            if related_path.endswith(".md"):
                cursor.execute("""
                    INSERT INTO links (source_file_id, target_path, link_type)
                    VALUES (?, ?, 'related')
                """, (file_id, related_path))
                stats["links"] += 1
        
        if i % 100 == 0:
            print(f"  Обработано: {i}/{total}")
    
    return stats


def main():
    import sys
    rebuild = "--rebuild" in sys.argv
    
    print("🗄️ Генерация базы данных проекта «Голем»...")
    
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    create_tables(cursor)
    conn.commit()
    
    print("📊 Наполнение базы...")
    stats = fill_database(cursor, rebuild=rebuild)
    conn.commit()
    
    print(f"\n✅ База данных создана: {DB_PATH}")
    print(f"📊 Статистика:")
    print(f"   Файлов: {stats['files']}")
    print(f"   Учений: {stats['teachings']}")
    print(f"   Терминов: {stats['terminology']}")
    print(f"   Личностей: {stats['persons']}")
    print(f"   Событий: {stats['events']}")
    print(f"   Книг: {stats['books']}")
    print(f"   Стихов: {stats['verses']}")
    print(f"   Связей: {stats['links']}")
    
    # Тестовый запрос
    print(f"\n🔍 Тестовый запрос: учения с красными плодами")
    cursor.execute("""
        SELECT f.title, t.fruits, t.verdict 
        FROM teachings t 
        JOIN files f ON t.file_id = f.id 
        WHERE t.fruits = 'red' 
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"   🔴 {row[0]}: плоды={row[1]}, вердикт={row[2]}")
    
    conn.close()


if __name__ == "__main__":
    main()