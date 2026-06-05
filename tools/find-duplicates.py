#!/usr/bin/env python3
# find-duplicates.py — поиск дублирующихся файлов в репозитории

import os
import re
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

REPO_ROOT = Path(__file__).parent.parent
TARGET_DIRS = ['terminology', 'researches']
SIMILARITY_THRESHOLD = 0.7  # 70% совпадения


def extract_title(content: str) -> str:
    """Извлекает заголовок из файла"""
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            title = re.sub(r'^[^\w]+', '', title)
            return title.lower()
    return ""


def extract_keywords(content: str, file_name: str) -> set:
    """Извлекает ключевые слова из файла"""
    keywords = set()
    
    name = Path(file_name).stem.replace('-', ' ').lower()
    keywords.add(name)
    
    title = extract_title(content)
    if title:
        keywords.add(title)
    
    lines = content.split('\n')
    for line in lines[:100]:
        if 'корень' in line.lower() or 'root' in line.lower():
            words = re.findall(r'[а-яa-z]{3,}', line.lower())
            keywords.update(words)
    
    return keywords


def read_file(file_path: Path) -> str:
    """Читает файл с обработкой ошибок"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Ошибка чтения {file_path}: {e}")
        return ""


def similarity(a: str, b: str) -> float:
    """Вычисляет схожесть двух строк"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_duplicates_by_keywords(files: dict) -> list:
    """Находит дубликаты по ключевым словам"""
    duplicates = []
    
    for name1, data1 in files.items():
        for name2, data2 in files.items():
            if name1 >= name2:
                continue
            
            common = data1['keywords'] & data2['keywords']
            if len(common) >= 2:
                duplicates.append({
                    'file1': name1,
                    'file2': name2,
                    'common_keywords': common,
                    'similarity': similarity(data1['content'][:2000], data2['content'][:2000])
                })
    
    return duplicates


def find_exact_duplicates(files: dict) -> list:
    """Находит точные дубликаты (100% совпадение)"""
    content_map = defaultdict(list)
    
    for name, data in files.items():
        content_hash = hash(data['content'])
        content_map[content_hash].append(name)
    
    duplicates = []
    for hash_val, names in content_map.items():
        if len(names) > 1:
            duplicates.append(names)
    
    return duplicates


def find_similar_by_name(files: dict) -> list:
    """Находит похожие имена файлов"""
    names = list(files.keys())
    similar = []
    
    for i, name1 in enumerate(names):
        for name2 in names[i+1:]:
            sim = similarity(name1, name2)
            if sim > 0.7:
                similar.append({
                    'file1': name1,
                    'file2': name2,
                    'similarity': sim
                })
    
    return similar


def find_potential_duplicates_by_keyword(keyword: str, files: dict) -> list:
    """Ищет файлы, содержащие ключевое слово"""
    result = []
    keyword_lower = keyword.lower()
    
    for name, data in files.items():
        if keyword_lower in data['content'].lower():
            result.append(name)
    
    return result


def main():
    print("🔍 ПОИСК ДУБЛИКАТОВ")
    print("===================")
    print("")
    
    files = {}
    
    for target_dir in TARGET_DIRS:
        dir_path = REPO_ROOT / target_dir
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.rglob('*.md'):
            content = read_file(md_file)
            if content:
                rel_path = str(md_file.relative_to(REPO_ROOT))
                files[rel_path] = {
                    'content': content,
                    'keywords': extract_keywords(content, md_file.name),
                    'title': extract_title(content)
                }
    
    print(f"📊 Просканировано файлов: {len(files)}")
    print("")
    
    # 1. Точные дубликаты
    exact = find_exact_duplicates(files)
    if exact:
        print("❌ ТОЧНЫЕ ДУБЛИКАТЫ:")
        for group in exact:
            print(f"  • {', '.join(group)}")
        print("")
    
    # 2. Похожие имена
    similar_names = find_similar_by_name(files)
    if similar_names:
        print("⚠️ ПОХОЖИЕ ИМЕНА ФАЙЛОВ:")
        for item in similar_names:
            print(f"  • {item['file1']} ↔ {item['file2']} (схожесть: {item['similarity']:.0%})")
        print("")
    
    # 3. Дубликаты по ключевым словам
    dup_by_keywords = find_duplicates_by_keywords(files)
    if dup_by_keywords:
        print("⚠️ ПОТЕНЦИАЛЬНЫЕ ДУБЛИКАТЫ (по ключевым словам):")
        for item in dup_by_keywords:
            if item['similarity'] > SIMILARITY_THRESHOLD:
                print(f"  • {item['file1']}")
                print(f"    ↔ {item['file2']}")
                print(f"    общие ключи: {', '.join(list(item['common_keywords'])[:5])}")
                print(f"    схожесть: {item['similarity']:.0%}")
                print("")
    
    # 4. Проверка по конкретному слову (интерактивно)
    print("📝 ПОИСК ПО КЛЮЧЕВОМУ СЛОВУ")
    print("Введите слово для поиска (или 'exit' для выхода):")
    
    while True:
        keyword = input("> ").strip()
        if keyword == 'exit':
            break
        if not keyword:
            continue
        
        found = find_potential_duplicates_by_keyword(keyword, files)
        if found:
            print(f"Найдено в {len(found)} файлах:")
            for f in found:
                print(f"  • {f}")
        else:
            print("Не найдено")
        print("")


if __name__ == "__main__":
    main()
