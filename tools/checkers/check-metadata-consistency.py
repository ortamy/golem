# tools/checkers/check-metadata-consistency.py — сверка папки в метаданных с реальным путём
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_error, print_warning, print_hint, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions", "davar", "ideas", "drafts"]


def extract_metadata_path(content: str) -> str:
    """Извлекает путь из поля 'Файл:' в метаданных."""
    match = re.search(r'[-*]\s*\*\*Файл:\*\*\s*`([^`]+)`', content)
    if match:
        return match.group(1).strip()
    return ""


def check_file(filepath: Path) -> dict:
    """Проверяет один файл. Возвращает словарь с результатом или None если всё ок."""
    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
    content = read_file_safe(filepath)

    if not content:
        return {"path": rel_path, "error": "не удалось прочитать"}

    if '**Метаданные файла**' not in content:
        return {"path": rel_path, "error": "нет блока метаданных"}

    metadata_path = extract_metadata_path(content)
    if not metadata_path:
        return {"path": rel_path, "error": "не указано поле 'Файл:'"}

    # Нормализуем
    metadata_path = metadata_path.replace('\\', '/')
    if metadata_path != rel_path:
        return {
            "path": rel_path,
            "error": f"указано '{metadata_path}' вместо '{rel_path}'",
            "metadata": metadata_path,
            "real": rel_path
        }

    return None


def main():
    fix_mode = "--fix" in sys.argv

    print_header("ПРОВЕРКА ПУТЕЙ В МЕТАДАННЫХ", "🏷️")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    print(f"Найдено файлов: {total}")

    issues = []
    no_metadata = []
    fixed = 0

    for i, filepath in enumerate(all_files, 1):
        result = check_file(filepath)
        if result:
            if "нет блока метаданных" in result["error"] or "не указано поле" in result["error"]:
                no_metadata.append(result)
            else:
                issues.append(result)

                if fix_mode:
                    content = read_file_safe(filepath)
                    if content and result.get("metadata"):
                        old = f"`{result['metadata']}`"
                        new = f"`{result['real']}`"
                        if old in content:
                            content = content.replace(old, new, 1)
                            with open(filepath, "w", encoding="utf-8") as f:
                                f.write(content)
                            fixed += 1

        progress_bar(i, total, extra=f"ошибок: {len(issues)}")

    finish_progress()

    # Вывод
    if no_metadata:
        print_warning(f"Файлов без метаданных: {len(no_metadata)}")
        for item in no_metadata[:5]:
            print(f"   • {item['path']}: {item['error']}")
        if len(no_metadata) > 5:
            print(f"   ... и ещё {len(no_metadata) - 5}")

    if issues:
        print_error(f"Несовпадений путей: {len(issues)}")
        for item in issues[:15]:
            print(f"   • {item['path']}")
            print(f"     метаданные: {item['metadata']}")
            print(f"     реальный:   {item['real']}")
        if len(issues) > 15:
            print(f"   ... и ещё {len(issues) - 15}")
    else:
        print_success("Все пути в метаданных корректны")

    if fix_mode:
        print_success(f"Исправлено: {fixed} файлов")
    else:
        if issues:
            print_hint("Для автофикса: python tools/checkers/check-metadata-consistency.py --fix")

    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())

