# tools/checkers/check-file-names-clarity.py — проверка ясности и краткости имён файлов
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_hint, ask_yes_no, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions", "davar", "ideas", "drafts"]
IGNORE_FILES = {"README.md", "STRUCTURE.md", "GLOSSARY.md", "STATS.md", "CHANGELOG.md",
                "CONTRIBUTORS.md", "BACKLOG.md", "DECISIONS.md", "ROADMAP.md",
                "TECHNICAL-DEBT.md", "RETROSPECTIVE.md", "COMPLETED-TASKS.md"}

# Максимум слов в имени файла
MAX_WORDS = 3
# Минимум слов
MIN_WORDS = 1
# Максимальная длина имени
MAX_LENGTH = 50
# Шаблон правильного имени
GOOD_NAME = re.compile(r'^[a-z][a-z0-9\-]+$')


def extract_title(content: str) -> str:
    """Извлекает заголовок файла для предложения имени."""
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def extract_topic(content: str) -> str:
    """Извлекает тему из метаданных."""
    match = re.search(r'[-*]\s*\*\*Тема:\*\*\s*(.+?)(?:\n|$)', content)
    if match:
        return match.group(1).strip()
    return ""


def suggest_name(filepath: Path, content: str) -> str:
    """Предлагает оптимальное имя файла на основе содержимого."""
    stem = filepath.stem

    # Если имя уже хорошее — оставляем
    if GOOD_NAME.match(stem) and len(stem.split('-')) <= MAX_WORDS and len(stem) <= MAX_LENGTH:
        return ""

    # Пробуем взять тему из метаданных
    topic = extract_topic(content)
    if topic:
        # Транслитерируем русские слова латиницей (упрощённо)
        suggested = transliterate(topic)
        if suggested and GOOD_NAME.match(suggested) and len(suggested.split('-')) <= MAX_WORDS:
            if suggested != stem:
                return suggested
        # Берём ключевые слова из темы
        words = topic.lower().split()
        key_words = [w for w in words if len(w) > 3 and not w.startswith('«')][:MAX_WORDS]
        if key_words:
            suggested = transliterate('-'.join(key_words))
            if suggested != stem:
                return suggested

    # Пробуем заголовок
    title = extract_title(content)
    if title:
        clean_title = re.sub(r'[📜🔥🛡️⚔️📖🎯🧭💻👑❤️]', '', title).strip()
        clean_title = re.sub(r'[«»"„“]', '', clean_title)
        words = clean_title.lower().split()
        key_words = [w for w in words if len(w) > 3 and w not in ('для', 'как', 'что', 'это', 'его', 'она', 'они', 'или', 'уже', 'ещё', 'для', 'под', 'над', 'при', 'про')][:MAX_WORDS]
        if key_words:
            suggested = transliterate('-'.join(key_words))
            if suggested != stem:
                return suggested

    return ""


def transliterate(text: str) -> str:
    """Упрощённая транслитерация русских слов в латиницу."""
    mapping = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        ' ': '-', '_': '-', '.': '-', ',': '', ':': '', ';': '', '!': '', '?': '',
        '(': '', ')': '', '[': '', ']': '', '{': '', '}': '',
    }

    text = text.lower().strip()
    result = []
    for char in text:
        if char in mapping:
            result.append(mapping[char])
        elif char in 'abcdefghijklmnopqrstuvwxyz0123456789-':
            result.append(char)

    clean = re.sub(r'-+', '-', ''.join(result))
    clean = clean.strip('-')[:MAX_LENGTH]

    return clean if GOOD_NAME.match(clean) else ""


def check_name(filepath: Path, content: str) -> list:
    """Проверяет имя файла. Возвращает список проблем."""
    issues = []
    name = filepath.stem

    if not GOOD_NAME.match(name):
        issues.append(f"неверный формат: '{name}' (допустимы: a-z, 0-9, дефис)")

    if len(name) > MAX_LENGTH:
        issues.append(f"слишком длинное: {len(name)} символов (макс: {MAX_LENGTH})")

    words = name.split('-')
    if len(words) > MAX_WORDS:
        issues.append(f"слишком много слов: {len(words)} (макс: {MAX_WORDS})")

    if re.search(r'[а-яё]', name, re.IGNORECASE):
        issues.append(f"содержит русские буквы")

    # Длинные слова без дефисов
    for word in words:
        if len(word) > 25:
            issues.append(f"длинное слово: '{word}' ({len(word)} символов)")

    return issues


def main():
    fix_mode = "--fix" in sys.argv

    print_header("ПРОВЕРКА ЯСНОСТИ ИМЁН ФАЙЛОВ" if not fix_mode else "ОПТИМИЗАЦИЯ ИМЁН ФАЙЛОВ",
                 "📛" if not fix_mode else "🔧")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    print(f"Найдено файлов: {total}")

    files_with_issues = []
    suggestions = {}

    for i, filepath in enumerate(all_files, 1):
        if filepath.name in IGNORE_FILES:
            continue

        content = read_file_safe(filepath)
        if not content:
            continue

        issues = check_name(filepath, content)
        if issues:
            rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
            files_with_issues.append((filepath, rel_path, issues))
            suggestion = suggest_name(filepath, content)
            if suggestion:
                suggestions[rel_path] = suggestion

        progress_bar(i, total, extra=f"проблем: {len(files_with_issues)}")

    finish_progress()

    if not files_with_issues:
        print_success("Все имена файлов ясные и краткие")
        return 0

    print_warning(f"Файлов с проблемными именами: {len(files_with_issues)}")

    # Группируем по типам проблем
    for _, path, issues in files_with_issues[:20]:
        print(f"\n  📄 {path}")
        for issue in issues:
            print(f"    • {issue}")
        if path in suggestions:
            print(f"    💡 предложение: {suggestions[path]}.md")

    if len(files_with_issues) > 20:
        print(f"\n  ... и ещё {len(files_with_issues) - 20} файлов")

    if fix_mode:
        if not ask_yes_no(f"\nПереименовать {len(suggestions)} файлов?"):
            print("👋 Отменено.")
            return 0

        renamed = 0
        for i, (filepath, rel_path, _) in enumerate(files_with_issues, 1):
            if rel_path in suggestions:
                new_name = suggestions[rel_path] + ".md"
                new_path = filepath.parent / new_name

                # Не перезаписываем существующие
                if new_path.exists() and new_path != filepath:
                    continue

                filepath.rename(new_path)
                renamed += 1

            progress_bar(i, len(files_with_issues), extra=f"переименовано: {renamed}")

        finish_progress()
        print_success(f"Переименовано: {renamed} файлов")
        if renamed > 0:
            print_hint("Запустите sync-structure.py для обновления STRUCTURE.md")
            print_hint("Проверьте внутренние ссылки: check-links.py")
    else:
        with_suggestions = len(suggestions)
        if with_suggestions > 0:
            print_hint(f"Предложений по переименованию: {with_suggestions}")
        print_hint("Для переименования: python tools/checkers/check-file-names-clarity.py --fix")

    return 0


if __name__ == "__main__":
    sys.exit(main())

