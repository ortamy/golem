#!/usr/bin/env python3
# validate-metadata.py — проверка наличия и корректности метаданных в файлах

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).parent.parent
TARGET_DIRS = ['terminology', 'researches', 'instructions', 'checkers', 'davar']
IGNORE_FILES = {'README.md', 'structure.md', 'GLOSSARY.md'}

REQUIRED_FIELDS = ['Файл:', 'Версия:', 'Дата создания:', 'Статус:', 'Тема:'}
OPTIONAL_FIELDS = ['Последнее обновление:', 'Причина обновления:']

DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
VERSION_PATTERN = re.compile(r'^\d+\.\d+$')
STATUS_VALUES = {'Активный', 'Черновик', 'Завершён', 'Активен'}


def has_metadata_block(content: str) -> bool:
    """Проверяет наличие блока метаданных"""
    return '**Метаданные файла**' in content or '**Metadata**' in content


def extract_metadata_fields(content: str) -> Dict[str, str]:
    """Извлекает поля метаданных из файла"""
    fields = {}
    
    patterns = {
        'Файл:': r'[-*]\s*\*\*Файл:\*\*\s*`([^`]+)`',
        'Версия:': r'[-*]\s*\*\*Версия:\*\*\s*([^\n]+)',
        'Дата создания:': r'[-*]\s*\*\*Дата создания:\*\*\s*([^\n]+)',
        'Последнее обновление:': r'[-*]\s*\*\*Последнее обновление:\*\*\s*([^\n]+)',
        'Причина обновления:': r'[-*]\s*\*\*Причина обновления:\*\*\s*([^\n]+)',
        'Статус:': r'[-*]\s*\*\*Статус:\*\*\s*([^\n]+)',
        'Тема:': r'[-*]\s*\*\*Тема:\*\*\s*([^\n]+)',
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            fields[field] = match.group(1).strip()
    
    return fields


def validate_file_path(file_path: str, actual_path: str) -> Tuple[bool, str]:
    """Проверяет соответствие пути в метаданных"""
    expected = file_path.replace('\\', '/')
    actual = str(actual_path).replace('\\', '/')
    
    if expected == actual:
        return True, ""
    return False, f"ожидалось: {expected}, фактически: {actual}"


def validate_version(version: str) -> Tuple[bool, str]:
    """Проверяет формат версии"""
    if not VERSION_PATTERN.match(version):
        return False, f"неверный формат: {version} (должно быть X.Y)"
    return True, ""


def validate_date(date_str: str) -> Tuple[bool, str]:
    """Проверяет формат даты"""
    if not DATE_PATTERN.match(date_str):
        return False, f"неверный формат: {date_str} (должно быть ГГГГ-ММ-ДД)"
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, f"несуществующая дата: {date_str}"


def validate_status(status: str) -> Tuple[bool, str]:
    """Проверяет статус"""
    if status not in STATUS_VALUES:
        return False, f"неверный статус: {status} (допустимо: {', '.join(STATUS_VALUES)})"
    return True, ""


def validate_topic(topic: str) -> Tuple[bool, str]:
    """Проверяет тему (не пустая, не слишком длинная)"""
    if not topic:
        return False, "тема не указана"
    if len(topic) > 200:
        return False, f"тема слишком длинная ({len(topic)} символов)"
    return True, ""


def check_file(file_path: Path) -> Dict:
    """Проверяет один файл"""
    rel_path = file_path.relative_to(REPO_ROOT)
    result = {
        'path': str(rel_path),
        'has_metadata': False,
        'errors': [],
        'warnings': []
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not has_metadata_block(content):
        result['errors'].append("отсутствует блок метаданных")
        return result
    
    result['has_metadata'] = True
    fields = extract_metadata_fields(content)
    
    for field in REQUIRED_FIELDS:
        if field not in fields:
            result['errors'].append(f"отсутствует поле: {field}")
    
    if 'Файл:' in fields:
        is_valid, msg = validate_file_path(fields['Файл:'], rel_path)
        if not is_valid:
            result['errors'].append(f"поле 'Файл': {msg}")
    
    if 'Версия:' in fields:
        is_valid, msg = validate_version(fields['Версия:'])
        if not is_valid:
            result['errors'].append(f"поле 'Версия': {msg}")
    
    if 'Дата создания:' in fields:
        is_valid, msg = validate_date(fields['Дата создания:'])
        if not is_valid:
            result['errors'].append(f"поле 'Дата создания': {msg}")
    
    if 'Последнее обновление:' in fields:
        is_valid, msg = validate_date(fields['Последнее обновление:'])
        if not is_valid:
            result['warnings'].append(f"поле 'Последнее обновление': {msg}")
    
    if 'Статус:' in fields:
        is_valid, msg = validate_status(fields['Статус:'])
        if not is_valid:
            result['errors'].append(f"поле 'Статус': {msg}")
    
    if 'Тема:' in fields:
        is_valid, msg = validate_topic(fields['Тема:'])
        if not is_valid:
            result['errors'].append(f"поле 'Тема': {msg}")
    
    return result


def main():
    print("📋 ПРОВЕРКА МЕТАДАННЫХ")
    print("=====================")
    print("")
    
    all_results = []
    
    for target_dir in TARGET_DIRS:
        dir_path = REPO_ROOT / target_dir
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.rglob('*.md'):
            if md_file.name in IGNORE_FILES:
                continue
            
            result = check_file(md_file)
            if result['errors'] or result['warnings']:
                all_results.append(result)
    
    files_with_errors = [r for r in all_results if r['errors']]
    files_with_warnings = [r for r in all_results if r['warnings'] and not r['errors']]
    
    if files_with_errors:
        print("❌ ОШИБКИ (требуют исправления):")
        print("")
        for result in files_with_errors:
            print(f"  📄 {result['path']}")
            for err in result['errors']:
                print(f"     • {err}")
            print("")
    
    if files_with_warnings:
        print("⚠️ ПРЕДУПРЕЖДЕНИЯ (рекомендуется исправить):")
        print("")
        for result in files_with_warnings:
            print(f"  📄 {result['path']}")
            for warn in result['warnings']:
                print(f"     • {warn}")
            print("")
    
    total_files = sum(1 for d in TARGET_DIRS for _ in (REPO_ROOT / d).rglob('*.md') if _.name not in IGNORE_FILES)
    files_ok = total_files - len(all_results)
    
    print("📊 СТАТИСТИКА")
    print(f"  ✅ Файлов с корректными метаданными: {files_ok}")
    print(f"  ❌ Файлов с ошибками: {len(files_with_errors)}")
    print(f"  ⚠️ Файлов с предупреждениями: {len(files_with_warnings)}")
    print(f"  📁 Всего проверено: {total_files}")


if __name__ == "__main__":
    main()
