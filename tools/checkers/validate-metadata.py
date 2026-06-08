# tools/validate-metadata.py — проверка метаданных в md-файлах
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_error, REPO_ROOT

TARGET_DIRS = ['terminology', 'researches', 'instructions', 'checkers', 'davar', 'ideas', 'drafts']
IGNORE_FILES = {'README.md', 'STRUCTURE.md', 'GLOSSARY.md', 'STATS.md', 'CHANGELOG.md',
                'CONTRIBUTORS.md', 'BACKLOG.md', 'DECISIONS.md', 'ROADMAP.md',
                'TECHNICAL-DEBT.md', 'RETROSPECTIVE.md'}

REQUIRED_FIELDS = ['Файл:', 'Версия:', 'Дата создания:', 'Статус:', 'Тема:']
STATUS_VALUES = {'Активный', 'Черновик', 'Завершён', 'Активен'}


def check_file(file_path: Path) -> list:
    rel_path = file_path.relative_to(REPO_ROOT)
    errors = []

    content = read_file_safe(file_path)
    if content is None:
        return [f"{rel_path}: ошибка чтения"]

    if '**Метаданные файла**' not in content:
        return [f"{rel_path}: отсутствует блок метаданных"]

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
            errors.append(f"отсутствует поле: {field}")

    if 'Файл:' in fields:
        expected = str(rel_path).replace('\\', '/')
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

    return [f"{rel_path}: {err}" for err in errors]


def main():
    print_header("ПРОВЕРКА МЕТАДАННЫХ", "📋")

    all_files = []
    for target_dir in TARGET_DIRS:
        dir_path = REPO_ROOT / target_dir
        if dir_path.exists():
            for md_file in dir_path.rglob('*.md'):
                if md_file.name not in IGNORE_FILES:
                    all_files.append(md_file)

    total = len(all_files)
    all_errors = []
    print(f"Найдено файлов: {total}")

    for i, file_path in enumerate(all_files, 1):
        errors = check_file(file_path)
        all_errors.extend(errors)
        progress_bar(i, total, extra=f"ошибок: {len(all_errors)}")

    finish_progress()

    if all_errors:
        print_error(f"НАРУШЕНИЯ: {len(all_errors)}")
        for err in all_errors[:20]:
            print(f"   • {err}")
        if len(all_errors) > 20:
            print(f"   ... и ещё {len(all_errors) - 20}")
        return 1
    else:
        print_success(f"Все {total} файлов имеют корректные метаданные")

    return 0


if __name__ == "__main__":
    sys.exit(main())