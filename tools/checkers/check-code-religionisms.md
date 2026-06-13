#!/usr/bin/env python3
# tools/checkers/check-code-religionisms.py — проверка Python/JS/CSS кода на религионизмы (v1.0)

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCAN_DIRS = ["tools", "ed", "web"]
EXTENSIONS = {".py", ".js", ".css", ".html", ".json", ".yml", ".yaml"}

# Словарь: слово → замена
RELIGIONISMS = {
    "Бог": "Элоhим",
    "Господь": "Яхве",
    "Господа": "Яхве",
    "Господу": "Яхве",
    "Господом": "Яхве",
    "Господе": "Яхве",
    "грех": "хэт",
    "греха": "хэт",
    "греху": "хэт",
    "грехом": "хэт",
    "грехе": "хэт",
    "душа": "нэфеш",
    "души": "нэфеш",
    "душе": "нэфеш",
    "душу": "нэфеш",
    "душой": "нэфеш",
    "дух": "руах",
    "духа": "руах",
    "духу": "руах",
    "духом": "руах",
    "духе": "руах",
    "вера": "эмуна",
    "веры": "эмуна",
    "вере": "эмуна",
    "веру": "эмуна",
    "верой": "эмуна",
    "покаяние": "тшува",
    "покаяния": "тшува",
    "спасение": "йешуа",
    "спасения": "йешуа",
    "милость": "хесед",
    "милости": "хесед",
    "благодать": "хэн",
    "благодати": "хэн",
    "святой": "кадош",
    "святая": "кадош",
    "святое": "кадош",
    "святые": "кадош",
    "святость": "кдуша",
    "церковь": "кеhила",
    "церкви": "кеhила",
    "церковью": "кеhила",
    "закон": "Тора",
    "закона": "Тора",
    "закону": "Тора",
    "законом": "Тора",
    "завет": "брит",
    "завета": "брит",
    "заповедь": "мицва",
    "заповеди": "мицва",
    "пророк": "нави",
    "пророка": "нави",
    "ангел": "малъах",
    "ангела": "малъах",
    "храм": "Дом",
    "храма": "Дом",
    "священник": "коhэн",
    "священника": "коhэн",
    "жертва": "корбан",
    "жертвы": "корбан",
    "молитва": "тфила",
    "молитвы": "тфила",
    "крещение": "твила",
    "крещения": "твила",
    "воскресение": "вставание",
    "ад": "шеол",
    "дьявол": "сатан",
    "дьявола": "сатан",
    "сатана": "сатан",
    "искупление": "выкуп",
    "искупления": "выкуп",
    "праведность": "цдака",
    "праведности": "цдака",
    "благословение": "браха",
    "благословения": "браха",
    "Христос": "Машиах",
    "Христа": "Машиах",
    "евангелие": "бсора",
    "евангелия": "бсора",
    "апостол": "шалиах",
    "апостола": "шалиах",
    "епископ": "пакид",
    "епископа": "пакид",
    "религия": "путь",
    "религии": "путь",
    "духовность": "руханийут",
    "духовный": "рухани",
    "религиозный": "дати",
}


def check_file(filepath):
    """Проверяет файл на религионимы."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    
    found = []
    lines = content.split("\n")
    
    for i, line in enumerate(lines, 1):
        # Пропускаем комментарии
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("/*") or stripped.startswith("*"):
            continue
        
        # Пропускаем строки
        if stripped.startswith('"') or stripped.startswith("'"):
            continue
        
        for word, replacement in RELIGIONISMS.items():
            # Ищем слово как отдельное слово
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, line, re.IGNORECASE):
                found.append({
                    "line": i,
                    "word": word,
                    "replacement": replacement,
                    "context": line.strip()[:80],
                })
    
    return found


def scan():
    total_files = 0
    total_found = 0
    files_with_issues = []
    
    for scan_dir in SCAN_DIRS:
        dir_path = ROOT / scan_dir
        if not dir_path.exists():
            continue
        
        for ext in EXTENSIONS:
            for file_path in dir_path.rglob(f"*{ext}"):
                # Пропускаем кэш и виртуальное окружение
                if "cache" in file_path.parts or ".venv" in file_path.parts or "node_modules" in file_path.parts:
                    continue
                if "cache-religionisms.json" in str(file_path):
                    continue
                
                total_files += 1
                found = check_file(file_path)
                
                if found:
                    total_found += len(found)
                    files_with_issues.append((file_path, found))
    
    return total_files, total_found, files_with_issues


def main():
    print("🔍 Проверка кода на религионизмы...")
    total_files, total_found, files_with_issues = scan()
    
    if not files_with_issues:
        print(f"✅ Проверено {total_files} файлов. Религионизмов не найдено.")
        return 0
    
    print(f"📁 Проверено: {total_files} файлов")
    print(f"❌ Найдено религионимов: {total_found} в {len(files_with_issues)} файлах\n")
    
    for file_path, found in files_with_issues:
        rel_path = file_path.relative_to(ROOT)
        print(f"📄 {rel_path} — {len(found)} шт.")
        for item in found[:3]:  # первые 3
            print(f"   строка {item['line']:4d}: «{item['word']}» → «{item['replacement']}»")
            print(f"   {item['context']}")
        if len(found) > 3:
            print(f"   ... и ещё {len(found) - 3}")
        print()
    
    print(f"💡 Для исправления .md файлов: python tools/checkers/check-religionisms.py --fix")
    print(f"💡 Код править вручную.")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())