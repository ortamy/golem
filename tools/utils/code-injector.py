# tools/utils/code-injector.py — вставка, замена, удаление кода в файлах
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from lib.utils import print_header, print_success, print_error, print_warning, print_hint, ask_yes_no

BACKUP_DIR = Path(__file__).parent.parent / "tools" / "cache" / "backups"


def backup_file(filepath: Path):
    """Создаёт бэкап файла перед изменением."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{filepath.name}.{timestamp}.bak"
    shutil.copy2(filepath, backup_path)
    return backup_path


def read_file(filepath: Path) -> list:
    """Читает файл и возвращает список строк."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.readlines()


def write_file(filepath: Path, lines: list):
    """Записывает строки в файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def insert_after(lines: list, line_num: int, code: str) -> list:
    """Вставляет код после указанной строки."""
    if line_num < 1 or line_num > len(lines):
        print_error(f"Номер строки {line_num} вне диапазона (1-{len(lines)})")
        return lines
    code_lines = [l + '\n' for l in code.split('\n')]
    for i, cl in enumerate(code_lines):
        lines.insert(line_num + i, cl)
    return lines


def insert_before(lines: list, line_num: int, code: str) -> list:
    """Вставляет код перед указанной строкой."""
    if line_num < 1 or line_num > len(lines):
        print_error(f"Номер строки {line_num} вне диапазона (1-{len(lines)})")
        return lines
    code_lines = [l + '\n' for l in code.split('\n')]
    for i, cl in enumerate(code_lines):
        lines.insert(line_num - 1 + i, cl)
    return lines


def replace_pattern(lines: list, pattern: str, code: str) -> list:
    """Заменяет строки, соответствующие паттерну, на новый код."""
    regex = re.compile(pattern)
    new_lines = []
    replaced = False
    for line in lines:
        if not replaced and regex.search(line):
            for cl in code.split('\n'):
                new_lines.append(cl + '\n')
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        print_warning(f"Паттерн не найден: {pattern}")
    return new_lines


def delete_pattern(lines: list, pattern: str) -> list:
    """Удаляет строки, соответствующие паттерну."""
    regex = re.compile(pattern)
    new_lines = [l for l in lines if not regex.search(l)]
    if len(new_lines) == len(lines):
        print_warning(f"Паттерн не найден: {pattern}")
    return new_lines


def append_to_end(lines: list, code: str) -> list:
    """Добавляет код в конец файла."""
    if lines and not lines[-1].endswith('\n'):
        lines[-1] += '\n'
    for cl in code.split('\n'):
        lines.append(cl + '\n')
    return lines


def find_line_by_pattern(lines: list, pattern: str) -> int:
    """Находит номер строки по паттерну. Возвращает 0 если не найдено."""
    regex = re.compile(pattern)
    for i, line in enumerate(lines, 1):
        if regex.search(line):
            return i
    return 0


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Вставка, замена, удаление кода в файлах")
    parser.add_argument("--file", "-f", required=True, help="Файл для редактирования")
    parser.add_argument("--code", "-c", help="Код для вставки/замены")
    parser.add_argument("--after", type=int, help="Вставить после строки N")
    parser.add_argument("--before", type=int, help="Вставить перед строкой N")
    parser.add_argument("--replace", help="Заменить строки по паттерну (regex)")
    parser.add_argument("--delete", help="Удалить строки по паттерну (regex)")
    parser.add_argument("--append", action="store_true", help="Добавить код в конец файла")
    parser.add_argument("--find", help="Найти строку по паттерну и показать номер")
    parser.add_argument("--after-pattern", help="Вставить после строки, найденной по паттерну")
    parser.add_argument("--before-pattern", help="Вставить перед строкой, найденной по паттерну")
    parser.add_argument("--dry-run", action="store_true", help="Показать что будет сделано без реальных изменений")
    parser.add_argument("--no-backup", action="store_true", help="Не создавать бэкап")

    args = parser.parse_args()
    filepath = Path(args.file)

    if not filepath.exists():
        print_error(f"Файл не найден: {args.file}")
        return 1

    # Режим поиска
    if args.find:
        lines = read_file(filepath)
        line_num = find_line_by_pattern(lines, args.find)
        if line_num:
            print(f"Строка {line_num}: {lines[line_num-1].rstrip()}")
        else:
            print_warning(f"Паттерн не найден: {args.find}")
        return 0

    # Проверяем что есть действие
    action = args.after or args.before or args.replace or args.delete or args.append or args.after_pattern or args.before_pattern
    if not action:
        print_error("Укажите действие: --after, --before, --replace, --delete, --append, --after-pattern, --before-pattern")
        return 1

    if not args.code and not args.delete:
        print_error("Укажите --code для вставки/замены")
        return 1

    print_header("CODE INJECTOR", "💉")
    print(f"📄 Файл: {filepath}")

    lines = read_file(filepath)
    original_len = len(lines)

    # Обработка --after-pattern и --before-pattern
    if args.after_pattern:
        line_num = find_line_by_pattern(lines, args.after_pattern)
        if line_num:
            args.after = line_num
            print(f"  Найдена строка {line_num}: {lines[line_num-1].rstrip()[:80]}")
        else:
            print_error(f"Паттерн не найден: {args.after_pattern}")
            return 1

    if args.before_pattern:
        line_num = find_line_by_pattern(lines, args.before_pattern)
        if line_num:
            args.before = line_num
            print(f"  Найдена строка {line_num}: {lines[line_num-1].rstrip()[:80]}")
        else:
            print_error(f"Паттерн не найден: {args.before_pattern}")
            return 1

    # Выполняем действие
    if args.after:
        print(f"  Действие: вставить после строки {args.after}")
        lines = insert_after(lines, args.after, args.code)
    elif args.before:
        print(f"  Действие: вставить перед строкой {args.before}")
        lines = insert_before(lines, args.before, args.code)
    elif args.replace:
        print(f"  Действие: заменить по паттерну '{args.replace[:60]}'")
        lines = replace_pattern(lines, args.replace, args.code)
    elif args.delete:
        print(f"  Действие: удалить по паттерну '{args.delete[:60]}'")
        lines = delete_pattern(lines, args.delete)
    elif args.append:
        print(f"  Действие: добавить в конец файла")
        lines = append_to_end(lines, args.code)

    changed = len(lines) - original_len
    print(f"  Строк: {original_len} → {len(lines)} ({'+' if changed > 0 else ''}{changed})")

    if args.dry_run:
        print_warning("\n[DRY RUN] Изменения не сохранены")
        # Показываем что изменилось
        if args.code:
            print(f"\nКод для вставки:\n{args.code[:200]}...")
        return 0

    # Бэкап
    if not args.no_backup:
        backup_path = backup_file(filepath)
        print(f"  💾 Бэкап: {backup_path.name}")

    # Сохраняем
    write_file(filepath, lines)
    print_success("✅ Файл обновлён")

    return 0


if __name__ == "__main__":
    sys.exit(main())