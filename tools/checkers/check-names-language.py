#!/usr/bin/env python3
# tools/checkers/check-names-language.py — проверка чистоты языка имён файлов
import sys
import re
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_warning, print_hint,
    ask_yes_no, REPO_ROOT
)

SCAN_DIRS = ["terminology", "researches", "drafts", "ideas"]

# Папки, где должны быть ивритские имена
HEBREW_REQUIRED_DIRS = {"terminology"}
HEBREW_REQUIRED_SUBDIRS = {"tanakh"}

# Папки, где иврит не нужен (технические, языковые, системные)
NON_HEBREW_SUBDIRS = {"language", "systems", "practices", "sociology", "psychology",
                       "economy", "media", "medicine", "science", "history",
                       "sport", "companies", "names", "books", "archive",
                       "teachings", "slavery", "roman-law", "languages"}

# =============================================================================
# ИВРИТСКИЕ СЛОВА — строится динамически из terminology/
# =============================================================================
def load_hebrew_words():
    """Загружает ивритские слова из имён файлов в terminology/."""
    words = set()
    term_dir = REPO_ROOT / "terminology"
    if term_dir.exists():
        for f in term_dir.glob("*.md"):
            words.add(f.stem)
    # Добавляем известные ивритские паттерны
    patterns = {
        "ha", "va", "be", "ba", "la", "le", "ka", "ke", "ve", "u",
        "me", "mi", "she", "et", "al", "el", "ad", "im", "lo",
        "ch", "sh", "tz", "ah", "eh", "ih", "oh", "uh", "kh",
        "yah", "yahu", "yir", "elohim", "adonai",
    }
    words.update(patterns)
    return words


HEBREW_WORDS = load_hebrew_words()


def part_is_hebrew(part: str) -> bool:
    """Проверяет, является ли часть имени ивритским словом."""
    if part in HEBREW_WORDS:
        return True
    # Проверяем окончания
    for suffix in ["ah", "eh", "ih", "oh", "uh", "im", "ot", "ut", "av", "ev"]:
        if part.endswith(suffix) and len(part) >= 4:
            return True
    # Начинается с ивритского префикса
    for prefix in ["ha", "va", "be", "ba", "la", "le", "ka", "ke", "ve", "me", "mi", "she"]:
        if part.startswith(prefix) and len(part) >= 4:
            return True
    return False


def analyze_name(stem: str, rel_path: str) -> dict:
    """Анализирует имя файла."""
    # Русские буквы
    if re.search(r'[а-яё]', stem, re.IGNORECASE):
        return {"type": "russian", "clean": False}

    parts = stem.split('-')
    hebrew_parts = []
    other_parts = []

    for part in parts:
        if part_is_hebrew(part):
            hebrew_parts.append(part)
        else:
            other_parts.append(part)

    if hebrew_parts and other_parts:
        return {
            "type": "mixed",
            "hebrew": hebrew_parts,
            "other": other_parts,
            "clean": False,
            "suggestion": "-".join(hebrew_parts) if len(hebrew_parts) >= 1 else "-".join(other_parts)
        }
    elif hebrew_parts:
        return {"type": "hebrew", "clean": True}
    else:
        return {"type": "other", "clean": True}


def check_file(filepath: Path) -> dict:
    """Проверяет файл."""
    stem = filepath.stem
    rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
    parts = rel_path.split('/')

    # Определяем контекст
    is_terminology = parts[0] == "terminology"
    subdir = parts[1] if len(parts) > 2 else ""

    requires_hebrew = is_terminology or (parts[0] == "researches" and subdir in HEBREW_REQUIRED_SUBDIRS)
    allows_other = parts[0] in ("drafts", "ideas") or (parts[0] == "researches" and subdir in NON_HEBREW_SUBDIRS)

    analysis = analyze_name(stem, rel_path)
    issues = []

    if requires_hebrew:
        if analysis["type"] == "other":
            issues.append(f"должен быть иврит, а не '{stem}'")
        elif analysis["type"] == "mixed":
            issues.append(f"смесь: иврит ({', '.join(analysis['hebrew'])}) + ({', '.join(analysis['other'])})")
        elif analysis["type"] == "russian":
            issues.append(f"русские буквы в имени")
    elif not allows_other:
        if analysis["type"] == "hebrew":
            issues.append(f"иврит в не-танахической папке: '{stem}'")
        elif analysis["type"] == "mixed":
            issues.append(f"смесь в не-танахической папке")
        elif analysis["type"] == "russian":
            issues.append(f"русские буквы в имени")

    if issues:
        result = {"path": rel_path, "issues": issues, "type": analysis["type"]}
        if "suggestion" in analysis:
            result["suggestion"] = analysis["suggestion"]
        return result

    return None


def fix_file(filepath: Path, suggestion: str) -> bool:
    """Переименовывает файл, убирая не-ивритские части."""
    new_path = filepath.parent / (suggestion + ".md")
    if new_path.exists():
        return False
    filepath.rename(new_path)
    return True


def main():
    fix_mode = "--fix" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print_header("ПРОВЕРКА ЧИСТОТЫ ЯЗЫКА ИМЁН", "🏷️")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    clean_count = 0
    issues_found = []
    suggestions = {}

    print(f"🔍 Файлов: {total}")
    print(f"📚 Ивритских слов загружено: {len(HEBREW_WORDS)}")

    for i, filepath in enumerate(all_files, 1):
        result = check_file(filepath)
        if result:
            issues_found.append(result)
            if "suggestion" in result:
                suggestions[result["path"]] = result["suggestion"]
        else:
            clean_count += 1

        progress_bar(i, total, extra=f"проблем: {len(issues_found)}")

    finish_progress()

    if not issues_found:
        print_success("🎉 Все имена файлов чистые")
        return 0

    print(f"\n📁 Файлов с проблемами: {len(issues_found)}")
    print(f"✅ Чистых файлов: {clean_count} ({clean_count * 100 // total}%)")

    stats = Counter()
    for result in issues_found:
        for issue in result["issues"]:
            if "русские" in issue:
                stats["русские буквы"] += 1
            elif "смесь" in issue:
                stats["смесь языков"] += 1
            elif "должен быть иврит" in issue:
                stats["должен быть иврит"] += 1
            elif "иврит в не-танах" in issue:
                stats["иврит в не-танах"] += 1
            else:
                stats[issue] += 1

    print("\n📊 Типы проблем:")
    for t, c in stats.most_common():
        print(f"  • {t}: {c}")

    print(f"\n📋 Файлы ({len(issues_found)}):")
    for result in (issues_found[:25] if not verbose else issues_found):
        sugg = f" → {result['suggestion']}" if "suggestion" in result else ""
        print(f"  📄 {result['path']}: {'; '.join(result['issues'])}{sugg}")
    if len(issues_found) > 25 and not verbose:
        print(f"  ... и ещё {len(issues_found) - 25}")

    if fix_mode:
        if not suggestions:
            print_warning("Нет файлов для переименования")
            return 0
        if not ask_yes_no(f"\n🔧 Переименовать {len(suggestions)} файлов?"):
            return 0

        renamed = 0
        for i, (rel_path, suggestion) in enumerate(suggestions.items(), 1):
            filepath = REPO_ROOT / rel_path
            if fix_file(filepath, suggestion):
                renamed += 1
            progress_bar(i, len(suggestions), extra=f"переименовано: {renamed}")

        finish_progress()
        print_success(f"✅ Переименовано: {renamed}")
    else:
        if suggestions:
            print_hint(f"\nПредложений по переименованию: {len(suggestions)}")
        print_hint("Запустите --fix для исправления смешанных имён")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())