# tools/validate-metadata.py
import sys
import re
from pathlib import Path
from progress import show_progress, finish_progress

REPO_ROOT = Path(__file__).parent.parent
TARGET_DIRS = ['terminology', 'researches', 'instructions', 'checkers', 'davar', 'ideas', 'drafts']
IGNORE_FILES = {'README.md', 'STRUCTURE.md', 'GLOSSARY.md', 'STATS.md', 'CHANGELOG.md', 
                'CONTRIBUTORS.md', 'BACKLOG.md', 'DECISIONS.md', 'ROADMAP.md', 
                'TECHNICAL-DEBT.md', 'RETROSPECTIVE.md'}

REQUIRED_FIELDS = ['Файл:', 'Версия:', 'Дата создания:', 'Статус:', 'Тема:']
STATUS_VALUES = {'Активный', 'Черновик', 'Завершён', 'Активен'}


def has_metadata_block(content: str) -> bool:
    return '**Метаданные файла**' in content


def validate_file_path(file_path: str, actual_path: str) -> tuple:
    expected = file_path.replace('\\', '/')
    actual = str(actual_path).replace('\\', '/')
    if expected == actual:
        return True, ""
    return False, f"ожидалось: {expected}"


def validate_version(version: str) -> tuple:
    if re.match(r'^\d+\.\d+$', version):
        return True, ""
    return False, f"неверный формат: {version}"


def validate_status(status: str) -> tuple:
    clean_status = re.sub(r'\s*\([^)]*\)', '', status).strip()
    if clean_status in STATUS_VALUES:
        return True, ""
    return False, f"неверный статус: {status}"


def validate_topic(topic: str) -> tuple:
    if not topic:
        return False, "тема не указана"
    if len(topic) > 200:
        return False, f"тема слишком длинная ({len(topic)} символов)"
    return True, ""


def check_file(file_path: Path) -> dict:
    rel_path = file_path.relative_to(REPO_ROOT)
    result = {'path': str(rel_path), 'errors': []}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not has_metadata_block(content):
        result['errors'].append("отсутствует блок метаданных")
        return result
    
    fields = {}
    patterns = {
        'Файл:': r'[-*]\s*\*\*Файл:\*\*\s*`([^`]+)`',
        'Версия:': r'[-*]\s*\*\*Версия:\*\*\s*([^\n]+)',
        'Дата создания:': r'[-*]\s*\*\*Дата создания:\*\*\s*([^\n]+)',
        'Статус:': r'[-*]\s*\*\*Статус:\*\*\s*([^\n]+)',
        'Тема:': r'[-*]\s*\*\*Тема:\*\*\s*([^\n]+)',
    }
    for field, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            fields[field] = match.group(1).strip()
    
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
    print("\n📋 ПРОВЕРКА МЕТАДАННЫХ")
    print("=" * 50)
    
    all_files = []
    for target_dir in TARGET_DIRS:
        dir_path = REPO_ROOT / target_dir
        if dir_path.exists():
            for md_file in dir_path.rglob('*.md'):
                if md_file.name not in IGNORE_FILES:
                    all_files.append(md_file)
    
    total = len(all_files)
    results = []
    
    print(f"Найдено файлов: {total}")
    print("Сканирование...\n")
    
    for i, file_path in enumerate(all_files, 1):
        result = check_file(file_path)
        if result['errors']:
            results.append(result)
        show_progress(i, total, "метаданные", len(results))
    
    finish_progress()
    print("\n\n" + "=" * 50)
    
    if results:
        print(f"\n❌ НАРУШЕНИЯ: {len(results)}")
        for result in results[:20]:
            print(f"\n  📄 {result['path']}")
            for err in result['errors'][:3]:
                print(f"     • {err}")
        if len(results) > 20:
            print(f"\n   ... и ещё {len(results) - 20} файлов с ошибками")
        return 1
    else:
        print(f"\n✅ Все {total} файлов имеют корректные метаданные")
        return 0


if __name__ == "__main__":
    sys.exit(main())