# tools/checkers/validate-metadata.py — проверка метаданных в md-файлах
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_error, print_warning, print_hint, ask_yes_no, REPO_ROOT

TARGET_DIRS = ['terminology', 'researches', 'instructions', 'checkers', 'davar', 'ideas', 'drafts', 'docs']
IGNORE_FILES = {'README.md', 'STRUCTURE.md', 'GLOSSARY.md', 'STATS.md', 'CHANGELOG.md',
                'CONTRIBUTORS.md', 'BACKLOG.md', 'DECISIONS.md', 'ROADMAP.md',
                'TECHNICAL-DEBT.md', 'RETROSPECTIVE.md', 'COMPLETED-TASKS.md'}

REQUIRED_FIELDS = ['Файл:', 'Версия:', 'Дата создания:', 'Статус:', 'Тема:']
STATUS_VALUES = {'Активный', 'Черновик', 'Завершён', 'Активен'}


def extract_metadata_block(content: str) -> tuple:
    """Извлекает блок метаданных. Возвращает (начало, конец, текст_блока)."""
    start = content.find('**Метаданные файла**')
    if start == -1:
        return -1, -1, ""

    # Ищем конец блока (следующий заголовок или разделитель)
    rest = content[start:]
    end_match = re.search(r'\n---|\n#|\n\*\*[^*]+\*\*', rest[30:])
    if end_match:
        end = start + 30 + end_match.start()
    else:
        end = len(content)

    return start, end, content[start:end]


def check_file(file_path: Path) -> dict:
    """Проверяет один файл. Возвращает словарь с ошибками или None."""
    rel_path = str(file_path.relative_to(REPO_ROOT)).replace('\\', '/')
    content = read_file_safe(file_path)

    if not content:
        return {"path": rel_path, "errors": ["ошибка чтения"], "content": None}

    if '**Метаданные файла**' not in content:
        return {"path": rel_path, "errors": ["отсутствует блок метаданных"], "content": content}

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

    errors = []

    for field in REQUIRED_FIELDS:
        if field not in fields:
            errors.append(f"отсутствует поле: {field}")

    if 'Файл:' in fields:
        expected = rel_path
        actual = fields['Файл:'].replace('\\', '/')
        if expected != actual:
            errors.append(f"Файл: ожидалось '{expected}'")

    if 'Версия:' in fields and not re.match(r'^\d+\.\d+$', fields['Версия:']):
        errors.append(f"Версия: неверный формат '{fields['Версия:']}'")

    if 'Статус:' in fields:
        clean = re.sub(r'\s*\([^)]*\)', '', fields['Статус:']).strip()
        if clean not in STATUS_VALUES:
            errors.append(f"Статус: '{clean}' не распознан")

    if 'Тема:' in fields and not fields['Тема:']:
        errors.append("Тема: не указана")

    if errors:
        return {"path": rel_path, "errors": errors, "content": content, "fields": fields}

    return None


def fix_file(filepath: Path, missing_fields: list, content: str) -> bool:
    """Добавляет отсутствующие поля в метаданные."""
    if not content:
        return False

    # Находим блок метаданных
    start = content.find('**Метаданные файла**')
    if start == -1:
        return False

    # Находим последнее поле метаданных
    field_pattern = re.compile(r'[-*]\s*\*\*[^*]+\*\*')
    matches = list(field_pattern.finditer(content, start))
    if not matches:
        return False

    last_field_end = matches[-1].end()
    # Ищем конец строки после последнего поля
    newline_pos = content.find('\n', last_field_end)
    if newline_pos == -1:
        newline_pos = len(content)

    insert_pos = newline_pos

    # Собираем новые поля
    new_fields = []
    if 'Статус:' in missing_fields:
        new_fields.append('- **Статус:** Активный')
    if 'Тема:' in missing_fields:
        # Пытаемся извлечь тему из заголовка
        title_match = re.search(r'^#\s+[📜🔥🛡️⚔️📖🎯🧭💻👑❤️]\s+(.+?)$', content, re.MULTILINE)
        topic = title_match.group(1).strip() if title_match else "Требует уточнения"
        new_fields.append(f'- **Тема:** {topic}')

    if not new_fields:
        return False

    # Вставляем новые поля перед последним полем (или в конец блока)
    insertion = '\n' + '\n'.join(new_fields)
    new_content = content[:insert_pos] + insertion + content[insert_pos:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True


def main():
    fix_mode = "--fix" in sys.argv

    print_header("ПРОВЕРКА МЕТАДАННЫХ" if not fix_mode else "ИСПРАВЛЕНИЕ МЕТАДАННЫХ",
                 "📋" if not fix_mode else "🔧")

    all_files = []
    for target_dir in TARGET_DIRS:
        dir_path = REPO_ROOT / target_dir
        if dir_path.exists():
            for md_file in dir_path.rglob('*.md'):
                if md_file.name not in IGNORE_FILES:
                    all_files.append(md_file)

    total = len(all_files)
    print(f"Найдено файлов: {total}")

    issues = []
    fixed_count = 0

    for i, file_path in enumerate(all_files, 1):
        result = check_file(file_path)
        if result:
            issues.append(result)

            if fix_mode:
                missing = [e.replace('отсутствует поле: ', '') for e in result["errors"] if 'отсутствует поле' in e]
                if missing and result.get("content"):
                    if fix_file(file_path, missing, result["content"]):
                        fixed_count += 1

        progress_bar(i, total, extra=f"ошибок: {len(issues)}")

    finish_progress()

    if not issues:
        print_success(f"Все {total} файлов имеют корректные метаданные")
        return 0

    print_error(f"НАРУШЕНИЯ: {len(issues)} файлов")

    # Статистика по типам ошибок
    error_types = {}
    for item in issues:
        for err in item["errors"]:
            err_type = err.split(':')[0] if ':' in err else err
            error_types[err_type] = error_types.get(err_type, 0) + 1

    print("\n📊 Типы ошибок:")
    for err_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {err_type}: {count}")

    print(f"\n📋 Файлы с ошибками (первые 15):")
    for item in issues[:15]:
        print(f"  • {item['path']}")
        for err in item["errors"][:3]:
            print(f"    - {err}")

    if len(issues) > 15:
        print(f"  ... и ещё {len(issues) - 15} файлов")

    if fix_mode:
        print_success(f"Исправлено: {fixed_count} файлов")
    else:
        print_hint("Для исправления: python tools/checkers/validate-metadata.py --fix")

    return 1


if __name__ == "__main__":
    sys.exit(main())