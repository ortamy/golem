# tools/checkers/check-empty-files.py — поиск пустых и незаполненных md-файлов
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_hint, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions", "davar", "ideas", "drafts"]
MIN_CONTENT_LENGTH = 200  # меньше — подозрительно
TODO_PATTERN = re.compile(r'TODO|FIXME|ЗАПОЛНИТЬ|НАПИСАТЬ|ВСТАВИТЬ|ДОПИСАТЬ', re.IGNORECASE)


def check_file(filepath: Path) -> dict:
    """Проверяет файл на пустоту/незаполненность."""
    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
    content = read_file_safe(filepath)

    if not content:
        return {"path": rel_path, "issue": "пустой файл (ошибка чтения)"}

    # Убираем метаданные и заголовки — считаем только тело
    body = re.sub(r'\*\*Метаданные файла\*\*.*?(?=\n#|\n---|\Z)', '', content, flags=re.DOTALL)
    body = re.sub(r'^#.*$', '', body, flags=re.MULTILINE)
    body = body.strip()

    if len(body) < 50:
        return {"path": rel_path, "issue": f"почти пустой ({len(body)} символов содержания)"}

    if len(body) < MIN_CONTENT_LENGTH:
        return {"path": rel_path, "issue": f"мало содержания ({len(body)} символов)"}

    # Ищем маркеры незаполненности
    todo_matches = TODO_PATTERN.findall(content)
    if todo_matches:
        return {"path": rel_path, "issue": f"найдены маркеры: {', '.join(set(todo_matches))}"}

    # Проверяем, не кончается ли файл маркером незаполненности
    last_lines = "\n".join(body.splitlines()[-3:])
    if re.search(r'\.{3,}|···|\.\.\.\s*$', last_lines):
        return {"path": rel_path, "issue": "обрывается на маркере пустоты"}

    return None


def main():
    print_header("ПОИСК ПУСТЫХ И НЕЗАПОЛНЕННЫХ ФАЙЛОВ", "👻")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    print(f"Найдено файлов: {total}")

    empty_files = []
    small_files = []
    todo_files = []

    for i, filepath in enumerate(all_files, 1):
        result = check_file(filepath)
        if result:
            issue = result["issue"]
            if "пустой" in issue or "почти пустой" in issue:
                empty_files.append(result)
            elif "маркеры" in issue or "обрывается" in issue:
                todo_files.append(result)
            else:
                small_files.append(result)

        progress_bar(i, total, extra=f"проблем: {len(empty_files) + len(todo_files) + len(small_files)}")

    finish_progress()

    if empty_files:
        print_warning(f"ПУСТЫХ/ПОЧТИ ПУСТЫХ: {len(empty_files)}")
        for item in empty_files:
            print(f"   • {item['path']} — {item['issue']}")

    if todo_files:
        print_warning(f"С МАРКЕРАМИ НЕЗАПОЛНЕННОСТИ: {len(todo_files)}")
        for item in todo_files:
            print(f"   • {item['path']} — {item['issue']}")

    if small_files:
        print(f"\n📊 МАЛО СОДЕРЖАНИЯ: {len(small_files)}")
        for item in small_files[:10]:
            print(f"   • {item['path']} — {item['issue']}")
        if len(small_files) > 10:
            print(f"   ... и ещё {len(small_files) - 10}")

    total_issues = len(empty_files) + len(todo_files) + len(small_files)
    if total_issues == 0:
        print_success("Все файлы заполнены")
    else:
        print(f"\n📝 Всего проблемных файлов: {total_issues}")

    return 0


if __name__ == "__main__":
    sys.exit(main())