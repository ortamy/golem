# tools/check-code-quality.py — проверка качества Python-кода
import sys
import ast
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_error, print_warning, print_hint, ask_yes_no, REPO_ROOT

SCAN_DIRS = ["tools"]
MAX_FUNCTION_LINES = 50
MAX_LINE_LENGTH = 100


def find_python_files():
    files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if not dir_path.exists():
            continue
        for py_file in sorted(dir_path.rglob("*.py")):
            if "__pycache__" not in str(py_file):
                files.append(py_file)
    return files


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
    used_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}

    # Импорты
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in used_names and alias.name != "__future__":
                    issues.append(("⚠️", "НЕИСПОЛЬЗУЕМЫЙ ИМПОРТ", f"'{alias.name}'"))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.name or node.module
                if name and name not in used_names and name != "__future__":
                    issues.append(("⚠️", "НЕИСПОЛЬЗУЕМЫЙ ИМПОРТ", f"'{name}'"))

    # Функции
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not ast.get_docstring(node):
                issues.append(("⚠️", "НЕТ DOCSTRING", f"функция '{node.name}'"))
            if hasattr(node, 'end_lineno'):
                func_lines = node.end_lineno - node.lineno + 1
                if func_lines > MAX_FUNCTION_LINES:
                    issues.append(("⚠️", "ДЛИННАЯ ФУНКЦИЯ", f"'{node.name}' — {func_lines} строк"))

    # Строки
    for i, line in enumerate(lines, 1):
        stripped = line.rstrip("\n")
        if len(stripped) > MAX_LINE_LENGTH:
            issues.append(("💡", "ДЛИННАЯ СТРОКА", f"строка {i}: {len(stripped)} символов"))
        if line.endswith((" ", "\t")):
            issues.append(("💡", "ПРОБЕЛ В КОНЦЕ", f"строка {i}"))
        if line.startswith("\t") and "    " in line:
            issues.append(("⚠️", "СМЕШАННЫЕ ОТСТУПЫ", f"строка {i}"))

    # Безопасность
    if "eval(" in source:
        issues.append(("❌", "НЕБЕЗОПАСНО", "использование eval()"))

    # Пустая строка в конце
    if source and not source.endswith("\n"):
        issues.append(("💡", "НЕТ ПУСТОЙ СТРОКИ", "файл должен заканчиваться пустой строкой"))

    # Shebang
    if not source.startswith("#!/") and ('if __name__ == "__main__"' in source or "if __name__ == '__main__'" in source):
        issues.append(("💡", "НЕТ SHEBANG", "исполняемый файл без #!/usr/bin/env python3"))

    return issues


def auto_fix(filepath, issues):
    source = read_file_safe(filepath)
    if source is None:
        return 0

    issue_types = {i[1] for i in issues}
    lines = source.splitlines()
    changed = False

    if "ПРОБЕЛ В КОНЦЕ" in issue_types:
        lines = [line.rstrip() for line in lines]
        changed = True

    if "НЕТ ПУСТОЙ СТРОКИ" in issue_types:
        lines.append("")
        changed = True

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return 1

    return 0


def scan_files(fix_mode=False):
    files = find_python_files()
    total = len(files)

    if total == 0:
        print_error("Python-файлы не найдены")
        return

    print(f"Найдено файлов: {total}")

    all_issues = {}
    total_issues = 0

    for i, filepath in enumerate(files, 1):
        issues = check_file(filepath)
        if issues:
            rel_path = str(filepath.relative_to(REPO_ROOT))
            all_issues[rel_path] = issues
            total_issues += len(issues)
            if fix_mode:
                fixed = auto_fix(filepath, issues)
                if fixed:
                    issues.append(("✅", "ИСПРАВЛЕНО", f"автофикс: {fixed} проблем(ы)"))

        progress_bar(i, total, extra=f"проблем: {total_issues}")

    finish_progress()

    if not all_issues:
        print_success("Код в идеальном состоянии!")
        return

    type_counts = Counter()
    for issues in all_issues.values():
        for _, itype, _ in issues:
            type_counts[itype] += 1

    print(f"📁 Файлов с проблемами: {len(all_issues)}")
    print(f"📝 Всего проблем: {total_issues}\n")

    print("📊 По типам:")
    for itype, count in type_counts.most_common():
        print(f"  {itype}: {count}")

    print(f"\n📋 Файлы:")
    for filepath, issues in all_issues.items():
        print(f"\n  📄 {filepath} ({len(issues)} проблем):")
        for severity, itype, msg in issues:
            print(f"    {severity} {itype}: {msg}")


def main():
    fix_mode = "--fix" in sys.argv

    print_header("ПРОВЕРКА КАЧЕСТВА КОДА" if not fix_mode else "ОПТИМИЗАЦИЯ КОДА",
                 "🔍" if not fix_mode else "🔧")

    if not fix_mode:
        scan_files(fix_mode=False)
        if ask_yes_no("\nЗапустить автофикс?"):
            print_header("АВТОФИКС", "🔧")
            scan_files(fix_mode=True)
    else:
        scan_files(fix_mode=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())