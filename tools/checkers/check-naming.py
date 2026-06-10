#!/usr/bin/env python3
# tools/checkers/check-naming.py — проверка имён md-файлов + автофикс
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import (
    progress_bar, finish_progress, print_header, print_success, print_error, print_warning, print_hint,
    ask_yes_no, REPO_ROOT
)

IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__', 'reports', 'neural', 'docs'}
IGNORE_FILES = {'README.md', 'CHANGELOG.md', 'BACKLOG.md', 'CONTRIBUTORS.md',
                'DECISIONS.md', 'GLOSSARY.md', 'RETROSPECTIVE.md', 'ROADMAP.md',
                'STRUCTURE.md', 'TECHNICAL-DEBT.md', 'STATS.md', 'COMPLETED-TASKS.md'}
ALLOWED_PATTERN = re.compile(r'^[a-z][a-z0-9\-]*\.md$')

# Транслитерация для автофикса
RU_TO_LAT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def transliterate(text: str) -> str:
    result = []
    for char in text.lower():
        if char in RU_TO_LAT:
            result.append(RU_TO_LAT[char])
        elif char in 'abcdefghijklmnopqrstuvwxyz0123456789-':
            result.append(char)
        elif char == ' ':
            result.append('-')
    clean = re.sub(r'-+', '-', ''.join(result)).strip('-')
    return clean if ALLOWED_PATTERN.match(clean + '.md') else ''


def get_all_md_files():
    files = []
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        rel_path = md_file.relative_to(REPO_ROOT)
        if rel_path.parts[0] in IGNORE_DIRS:
            continue
        if md_file.name in IGNORE_FILES:
            continue
        files.append((rel_path, md_file))
    return files


def check_name(name: str) -> tuple:
    """Проверяет имя файла. Возвращает (ок, ошибка, suggestion)."""
    if not ALLOWED_PATTERN.match(name):
        suggestion = transliterate(name)
        if suggestion:
            return False, f"неверный формат: {name}", suggestion + '.md'
        return False, f"неверный формат: {name}", ''

    if name != name.lower():
        suggestion = name.lower()
        return False, f"заглавные буквы: {name}", suggestion

    if re.search(r'[а-яё]', name, re.IGNORECASE):
        suggestion = transliterate(name)
        if suggestion:
            return False, f"русские буквы: {name}", suggestion + '.md'
        return False, f"русские буквы: {name}", ''

    if re.search(r'[\s_&?%=+!@#$^()\[\]{}]', name):
        suggestion = re.sub(r'[\s_&?%=+!@#$^()\[\]{}]+', '-', name).strip('-')
        suggestion = re.sub(r'-+', '-', suggestion)
        return False, f"недопустимые символы: {name}", suggestion

    return True, '', ''


def main():
    fix_mode = "--fix" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print_header("ПРОВЕРКА ИМЁН ФАЙЛОВ", "📛")

    files = get_all_md_files()
    total = len(files)
    print(f"🔍 Файлов: {total}")

    errors = []
    suggestions = {}
    type_counts = {}

    for i, (rel_path, md_file) in enumerate(files, 1):
        is_valid, error_msg, suggestion = check_name(md_file.name)
        if not is_valid:
            errors.append((rel_path, error_msg))
            if suggestion:
                suggestions[str(rel_path)] = suggestion

            # Тип ошибки
            if "заглавные" in error_msg:
                type_counts["заглавные буквы"] = type_counts.get("заглавные буквы", 0) + 1
            elif "русские" in error_msg:
                type_counts["русские буквы"] = type_counts.get("русские буквы", 0) + 1
            elif "недопустимые символы" in error_msg:
                type_counts["недопустимые символы"] = type_counts.get("недопустимые символы", 0) + 1
            else:
                type_counts["неверный формат"] = type_counts.get("неверный формат", 0) + 1

        progress_bar(i, total, extra=f"ошибок: {len(errors)}")

    finish_progress()

    if not errors:
        print_success(f"🎉 Все {total} файлов названы корректно")
        return 0

    print_error(f"\n📛 НАРУШЕНИЙ: {len(errors)}")
    print(f"💡 Предложений по переименованию: {len(suggestions)}")

    if type_counts:
        print("\n📊 По типам:")
        for t, c in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {t}: {c}")

    print(f"\n📋 Файлы:")
    for rel_path, error_msg in (errors if verbose else errors[:20]):
        sugg = f" → {suggestions[str(rel_path)]}" if str(rel_path) in suggestions else ""
        print(f"  {rel_path}: {error_msg}{sugg}")
    if len(errors) > 20 and not verbose:
        print(f"  ... и ещё {len(errors) - 20}")

    if fix_mode:
        if not suggestions:
            print_warning("Нет файлов для переименования")
            return 1

        if not ask_yes_no(f"\n🔧 Переименовать {len(suggestions)} файлов?"):
            return 1

        renamed = 0
        for i, (rel_path_str, new_name) in enumerate(suggestions.items(), 1):
            filepath = REPO_ROOT / rel_path_str
            new_path = filepath.parent / new_name

            if new_path.exists():
                continue

            try:
                filepath.rename(new_path)
                renamed += 1
            except:
                pass

            progress_bar(i, len(suggestions), extra=f"переименовано: {renamed}")

        finish_progress()
        print_success(f"✅ Переименовано: {renamed}")

    elif suggestions:
        print_hint(f"\nПредложений: {len(suggestions)}")
        print_hint("--fix — автоматически переименовать")

    print()
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())