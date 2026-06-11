#!/usr/bin/env python3
# tools/check-code-quality.py — проверка качества Python-кода
import sys
import ast
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))
import argparse
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_error, print_warning, print_hint,
    ask_yes_no, REPO_ROOT
)

SCAN_DIRS = ["tools", "neural"]
MAX_FUNCTION_LINES = 50
MAX_LINE_LENGTH = 100
MAX_COMPLEXITY = 10
IGNORE_FILES = {"__pycache__", ".pyc", ".venv"}

all_issues_found = False
total_fixed_issues = 0


def find_python_files():
    files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if not dir_path.exists():
            continue
        for py_file in sorted(dir_path.rglob("*.py")):
            path_str = str(py_file)
            if not any(ign in path_str for ign in IGNORE_FILES):
                files.append(py_file)
    return files


def get_all_names(node):
    """Собирает __all__ имена из модуля"""
    names = set()
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == '__all__':
                if isinstance(node.value, (ast.List, ast.Tuple)):
                    for elt in node.value.elts:
                        if isinstance(elt, ast.Constant):
                            names.add(elt.value)
    return names


def count_complexity(node):
    """Подсчитывает цикломатическую сложность функции"""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity


def count_meaningful_lines(lines, start, end):
    """Считает значимые строки (без пустых и комментариев)"""
    count = 0
    for i in range(start - 1, min(end, len(lines))):
        line = lines[i].strip()
        if line and not line.startswith('#'):
            count += 1
    return count


def check_file(filepath):
    issues = []
    source = read_file_safe(filepath)
    if source is None:
        return [("❌", "ОШИБКА ЧТЕНИЯ", "не удалось прочитать файл")]

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [("❌", "СИНТАКСИЧЕСКАЯ ОШИБКА", str(e))]

    lines = source.splitlines()

    used_names = set()
    all_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)
        elif isinstance(node, ast.Assign):
            all_names.update(get_all_names(node))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.split('.')[0]
                if name not in used_names and name not in all_names and name != "__future__":
                    issues.append(("⚠️", "НЕИСПОЛЬЗУЕМЫЙ ИМПОРТ", f"'{alias.name}'"))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.name or node.module
                if name and name not in used_names and name not in all_names and name != "__future__":
                    issues.append(("⚠️", "НЕИСПОЛЬЗУЕМЫЙ ИМПОРТ", f"'{name}'"))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not ast.get_docstring(node):
                issues.append(("⚠️", "НЕТ DOCSTRING", f"функция '{node.name}'"))

            meaningful = count_meaningful_lines(lines, node.lineno, getattr(node, 'end_lineno', node.lineno))
            if meaningful > MAX_FUNCTION_LINES:
                issues.append(("⚠️", "ДЛИННАЯ ФУНКЦИЯ",
                               f"'{node.name}' — {meaningful} значимых строк"))

            complexity = count_complexity(node)
            if complexity > MAX_COMPLEXITY:
                issues.append(("⚠️", "ВЫСОКАЯ СЛОЖНОСТЬ",
                               f"'{node.name}' — сложность {complexity} (макс {MAX_COMPLEXITY})"))

    for i, line in enumerate(lines, 1):
        stripped = line.rstrip("\n")
        if len(stripped) > MAX_LINE_LENGTH:
            issues.append(("💡", "ДЛИННАЯ СТРОКА", f"строка {i}: {len(stripped)} символов"))
        if line.endswith((" ", "\t")):
            issues.append(("💡", "ПРОБЕЛ В КОНЦЕ", f"строка {i}"))
        if "\t" in line and "    " in line:
            issues.append(("⚠️", "СМЕШАННЫЕ ОТСТУПЫ", f"строка {i}"))

    for i, line in enumerate(lines, 1):
        for marker in ['TODO', 'FIXME', 'HACK', 'XXX']:
            if marker in line and not line.strip().startswith('#'):
                issues.append(("💡", f"МАРКЕР {marker}", f"строка {i}: {line.strip()[:80]}"))
                break

    if "eval(" in source:
        issues.append(("❌", "НЕБЕЗОПАСНО", "использование eval()"))
    if "exec(" in source:
        issues.append(("❌", "НЕБЕЗОПАСНО", "использование exec()"))
    if "os.system(" in source or "os.popen(" in source:
        issues.append(("❌", "НЕБЕЗОПАСНО", "os.system() или os.popen()"))
    if "subprocess" in source and "shell=True" in source:
        issues.append(("❌", "НЕБЕЗОПАСНО", "subprocess с shell=True"))
    if "assert " in source:
        issues.append(("💡", "ASSERT В КОДЕ", "assert лучше заменить на явную проверку"))

    if source and not source.endswith("\n"):
        issues.append(("💡", "НЕТ ПУСТОЙ СТРОКИ", "файл должен заканчиваться пустой строкой"))

    if not source.startswith("#!/") and ('if __name__ == "__main__"' in source or "if __name__ == '__main__'" in source):
        issues.append(("💡", "НЕТ SHEBANG", "исполняемый файл без #!/usr/bin/env python3"))

    return issues


def auto_fix(filepath, issues):
    global total_fixed_issues
    source = read_file_safe(filepath)
    if source is None:
        return 0

    issue_types = {i[1] for i in issues}
    lines = source.splitlines()
    fixes = 0

    # Пробелы в конце
    if "ПРОБЕЛ В КОНЦЕ" in issue_types:
        lines = [line.rstrip() for line in lines]
        fixes += 1

    # Пустая строка в конце
    if "НЕТ ПУСТОЙ СТРОКИ" in issue_types:
        if lines and lines[-1] != "":
            lines.append("")
        fixes += 1

    # Shebang
    if "НЕТ SHEBANG" in issue_types and lines:
        if not lines[0].startswith("#!/"):
            lines.insert(0, "#!/usr/bin/env python3")
        fixes += 1

    # Неиспользуемые импорты — комментируем
    if "НЕИСПОЛЬЗУЕМЫЙ ИМПОРТ" in issue_types:
        unused_names = set()
        for _, itype, msg in issues:
            if itype == "НЕИСПОЛЬЗУЕМЫЙ ИМПОРТ":
                name = msg.strip("'")
                unused_names.add(name)

        new_lines = []
        for line in lines:
            stripped = line.strip()
            commented = False
            for name in unused_names:
                if name in stripped and (stripped.startswith("import ") or stripped.startswith("from ")):
                    if f"import {name}" in stripped or f"from {name}" in stripped:
                        new_lines.append("# " + line + "  # TODO: проверить, используется ли")
                        commented = True
                        fixes += 1
                        break
            if not commented:
                new_lines.append(line)
        lines = new_lines

    if fixes > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            if lines and not lines[-1].endswith("\n"):
                f.write("\n")

    total_fixed_issues += fixes
    return fixes


def scan_files(fix_mode=False, verbose=False):
    global all_issues_found
    files = find_python_files()
    total = len(files)
    clean_files = 0

    if total == 0:
        print_warning("Python-файлы не найдены")
        all_issues_found = False
        return False

    label = "🔧 Исправляю" if fix_mode else "🔍 Проверяю"
    print(f"{label} файлов: {total}\n")

    all_issues = {}
    total_issues = 0

    for i, filepath in enumerate(files, 1):
        rel_path = str(filepath.relative_to(REPO_ROOT))
        issues = check_file(filepath)

        if issues:
            if fix_mode:
                fixed = auto_fix(filepath, issues)
                if fixed:
                    # Проверяем повторно что осталось
                    remaining = check_file(filepath)
                    if remaining:
                        all_issues[rel_path] = remaining
                        total_issues += len(remaining)
                else:
                    all_issues[rel_path] = issues
                    total_issues += len(issues)
            else:
                all_issues[rel_path] = issues
                total_issues += len(issues)
        else:
            clean_files += 1

        progress_bar(i, total, extra=f"проблем: {total_issues}")

    finish_progress()

    if not all_issues:
        if fix_mode:
            print_success(f"🎉 Все проблемы исправлены! (исправлено: {total_fixed_issues})")
        else:
            print_success(f"🎉 Все {total} файлов в идеальном состоянии!")
        all_issues_found = False
        return False

    if fix_mode:
        print_success(f"🔧 Исправлено проблем: {total_fixed_issues}")

    type_counts = Counter()
    for issues in all_issues.values():
        for _, itype, _ in issues:
            type_counts[itype] += 1

    print(f"\n📁 Файлов с проблемами: {len(all_issues)} из {total}")
    print(f"✅ Чистых файлов: {clean_files} ({clean_files * 100 // total}%)")
    print(f"📝 Осталось проблем: {total_issues}\n")

    if total_issues > 0:
        print("📊 По типам:")
        for itype, count in type_counts.most_common():
            if itype.startswith(("НЕБЕЗОПАСНО", "СИНТАКСИЧЕСКАЯ")):
                emoji = "❌"
            elif itype in ("НЕТ DOCSTRING", "ДЛИННАЯ ФУНКЦИЯ", "ВЫСОКАЯ СЛОЖНОСТЬ",
                           "СМЕШАННЫЕ ОТСТУПЫ", "НЕИСПОЛЬЗУЕМЫЙ ИМПОРТ"):
                emoji = "⚠️"
            else:
                emoji = "💡"
            print(f"  {emoji} {itype}: {count}")

        print(f"\n📋 Файлы ({len(all_issues)}):")
        SHORT_NAMES = {
            "НЕИСПОЛЬЗУЕМЫЙ ИМПОРТ": "импорт",
            "НЕТ DOCSTRING": "docstring",
            "ДЛИННАЯ ФУНКЦИЯ": "длинная",
            "ВЫСОКАЯ СЛОЖНОСТЬ": "сложность",
            "ДЛИННАЯ СТРОКА": "строка",
            "НЕТ SHEBANG": "shebang",
            "НЕТ ПУСТОЙ СТРОКИ": "пусто",
            "НЕБЕЗОПАСНО": "опасно",
            "МАРКЕР TODO": "TODO",
            "МАРКЕР FIXME": "FIXME",
            "МАРКЕР HACK": "HACK",
            "МАРКЕР XXX": "XXX",
            "СИНТАКСИЧЕСКАЯ ОШИБКА": "синтаксис",
            "ПРОБЕЛ В КОНЦЕ": "пробел",
            "СМЕШАННЫЕ ОТСТУПЫ": "отступы",
            "ASSERT В КОДЕ": "assert",
        }
        for filepath, issues in sorted(all_issues.items()):
            issue_summary = Counter(i[1] for i in issues)
            parts = []
            for itype, count in sorted(issue_summary.items()):
                short = SHORT_NAMES.get(itype, itype.lower())
                parts.append(f"{short}×{count}")
            print(f"  📄 {filepath}: {', '.join(parts)}")

        if verbose:
            print(f"\n📋 Подробно по файлам:")
            for filepath, issues in all_issues.items():
                print(f"\n  📄 {filepath} ({len(issues)}):")
                for severity, itype, msg in issues:
                    print(f"    {severity} {itype}: {msg}")

    all_issues_found = True
    return True


def main():
    global all_issues_found, total_fixed_issues
    fix_mode = "--fix" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print_header("ПРОВЕРКА КАЧЕСТВА КОДА", "🔍")
    print()

    total_fixed_issues = 0
    all_issues_found = scan_files(fix_mode=False, verbose=verbose)

    if all_issues_found:
        if fix_mode or ask_yes_no("\n🔧 Запустить автофикс?"):
            print()
            print_header("АВТОФИКС", "🔧")
            print()
            scan_files(fix_mode=True, verbose=verbose)

            print()
            print_header("ПРОВЕРКА ПОСЛЕ ИСПРАВЛЕНИЯ", "✅")
            print()
            remaining = scan_files(fix_mode=False, verbose=verbose)

            if not remaining:
                print_success(f"🎉 Все проблемы исправлены! (исправлено: {total_fixed_issues})")
            else:
                print_warning(f"⚠️ Исправлено: {total_fixed_issues}. Остались проблемы, требующие ручного вмешательства")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

