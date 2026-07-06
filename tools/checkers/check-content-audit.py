#!/usr/bin/env python3
"""
tools/audit-content.py — Аудит папки content/ на пустые/неполные/повреждённые файлы.
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BASE_DIR / "content"

REQUIRED_META_FIELDS = ["Файл", "Версия", "Статус", "Тема"]
PLACEHOLDER_PATTERNS = ["[ВСТАВИТЬ]", "TODO", "FIXME", "...", "---", "===", "***"]

def check_metadata(content):
    """Проверяет наличие блока метаданных."""
    lines = content.split('\n')
    meta_fields = set()
    in_meta_section = False
    for line in lines:
        line = line.strip()
        if 'Метаданные файла' in line:
            in_meta_section = True
            continue
        if in_meta_section:
            if line.startswith('---'):
                break
            if line.startswith('## ') or line.startswith('### '):
                break
            if line.startswith('- **') and ':**' in line:
                key = line.split(':**')[0].replace('- **', '').strip()
                meta_fields.add(key)
    missing = [f for f in REQUIRED_META_FIELDS if f not in meta_fields]
    return missing

def check_placeholders(content):
    """Ищет шаблонные заглушки."""
    found = []
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern in content:
            found.append(pattern)
    return found

def audit_file(path):
    """Аудитирует один .md файл."""
    rel_path = path.relative_to(CONTENT_DIR)
    try:
        size = path.stat().st_size
    except Exception as e:
        return str(rel_path), "ОШИБКА", f"Не удалось прочитать: {e}"
    
    if size < 100:
        return str(rel_path), "ПУСТ", f"Размер {size} байт"
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return str(rel_path), "ПОВРЕЖДЁН", f"Ошибка чтения: {e}"
    
    # Проверка метаданных
    missing_meta = check_metadata(content)
    if missing_meta:
        return str(rel_path), "ОШИБКА МЕТАДАННЫХ", f"Отсутствуют поля: {', '.join(missing_meta)}"
    
    # Проверка заголовка H1
    if not content.lstrip().startswith('#'):
        return str(rel_path), "НЕПОЛНЫЙ", "Отсутствует заголовок первого уровня"
    
    # Проверка секций
    if '##' not in content and '###' not in content:
        return str(rel_path), "НЕПОЛНЫЙ", "Отсутствуют секции"
    
    # Проверка заглушек
    placeholders = check_placeholders(content)
    if placeholders:
        return str(rel_path), "НЕПОЛНЫЙ", f"Найдены заглушки: {', '.join(placeholders)}"
    
    return str(rel_path), "OK", ""

def main():
    if not CONTENT_DIR.exists():
        print(f"Папка {CONTENT_DIR} не найдена", file=sys.stderr)
        sys.exit(1)
    
    md_files = sorted(CONTENT_DIR.rglob("*.md"))
    results = []
    for path in md_files:
        results.append(audit_file(path))
    
    # Статистика
    stats = {
        "Всего файлов": len(results),
        "OK": sum(1 for r in results if r[1] == "OK"),
        "ПУСТ": sum(1 for r in results if r[1] == "ПУСТ"),
        "НЕПОЛНЫЙ": sum(1 for r in results if r[1] == "НЕПОЛНЫЙ"),
        "ПОВРЕЖДЁН": sum(1 for r in results if r[1] == "ПОВРЕЖДЁН"),
        "ОШИБКА МЕТАДАННЫХ": sum(1 for r in results if r[1] == "ОШИБКА МЕТАДАННЫХ"),
    }
    
    # Вывод отчёта
    print("# АУДИТ ПАПКИ content/\n")
    print("## Таблица файлов\n")
    print("| Файл | Статус | Примечание |")
    print("|------|--------|------------|")
    for rel_path, status, note in results:
        if status != "OK":
            print(f"| {rel_path} | {status} | {note} |")
    
    print("\n## Итоговая статистика\n")
    for key, value in stats.items():
        print(f"- **{key}**: {value}")
    
    # Неполные файлы детально
    incomplete = [r for r in results if r[1] != "OK"]
    if incomplete:
        print(f"\n## Проблемные файлы ({len(incomplete)})\n")
        for rel_path, status, note in incomplete:
            print(f"- `{rel_path}` — **{status}**: {note}")

if __name__ == "__main__":
    main()