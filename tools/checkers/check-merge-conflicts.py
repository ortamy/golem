# tools/checkers/check-merge-conflicts.py — поиск и исправление конфликтов слияния Git
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_error, print_warning, print_hint, ask_yes_no, REPO_ROOT

SCAN_DIRS = ["instructions", "terminology", "researches", "davar", "ideas", "drafts", "docs", "tools"]
CONFLICT_MARKERS = ["
def check_file(filepath: Path) -> list:
    """Проверяет файл на наличие маркеров конфликтов."""
    content = read_file_safe(filepath)
    if not content:
        return []

    issues = []
    for marker in CONFLICT_MARKERS:
        count = content.count(marker)
        if count > 0:
            issues.append(marker)

    return issues


def fix_file(filepath: Path) -> bool:
    """Удаляет блоки конфликтов из файла. Сохраняет HEAD-версию."""
    content = read_file_safe(filepath)
    if not content:
        return False

    changed = False
    start = 0  # ← добавить инициализацию

    while True:
        start = content.find("", start)
        if end == -1:
            break

        mid = content.find("", start, end)
        if mid == -1:
            content = content[:start] + content[end + 7:]
            changed = True
            continue

        head_start = content.find('\n', start) + 1
        head_content = content[head_start:mid].rstrip()

        end_line = content.find('\n', end) + 1
        if end_line == 0:
            end_line = len(content)

        content = content[:start] + head_content + content[end_line:]
        changed = True

    for marker in CONFLICT_MARKERS:
        content = content.replace(marker + '\n', '')
        content = content.replace('\n' + marker, '')
        content = content.replace(marker, '')

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False


def main():
    fix_mode = "--fix" in sys.argv

    print_header("ПОИСК КОНФЛИКТОВ СЛИЯНИЯ GIT" if not fix_mode else "ИСПРАВЛЕНИЕ КОНФЛИКТОВ", "⚠️" if not fix_mode else "🔧")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))
            all_files.extend(sorted(dir_path.rglob("*.py")))

    total = len(all_files)
    print(f"Проверено файлов: {total}")

    files_with_conflicts = []
    fixed = 0

    for i, filepath in enumerate(all_files, 1):
        issues = check_file(filepath)
        if issues:
            rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
            files_with_conflicts.append((filepath, rel_path, issues))

            if fix_mode:
                if fix_file(filepath):
                    fixed += 1

        progress_bar(i, total, extra=f"конфликтов: {len(files_with_conflicts)}")

    finish_progress()

    if not files_with_conflicts:
        print_success("Конфликтов слияния не найдено")
        return 0

    print_error(f"КОНФЛИКТЫ: {len(files_with_conflicts)} файлов")
    for _, filepath, issues in files_with_conflicts[:20]:
        markers_str = ", ".join(f"«{m}»" for m in issues)
        print(f"  • {filepath} — {markers_str}")

    if len(files_with_conflicts) > 20:
        print(f"  ... и ещё {len(files_with_conflicts) - 20} файлов")

    if fix_mode:
        print_success(f"Исправлено: {fixed} файлов")
    else:
        if ask_yes_no(f"\nИсправить {len(files_with_conflicts)} файлов?"):
            print_header("ИСПРАВЛЕНИЕ КОНФЛИКТОВ", "🔧")
            fixed = 0
            for i, (filepath, rel_path, _) in enumerate(files_with_conflicts, 1):
                if fix_file(filepath):
                    fixed += 1
                progress_bar(i, len(files_with_conflicts), extra=f"исправлено: {fixed}")
            finish_progress()
            print_success(f"Исправлено: {fixed} файлов")

    return 0


if __name__ == "__main__":
    sys.exit(main())