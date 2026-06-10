#!/usr/bin/env python3
# tools/checkers/check-file-names-clarity.py — проверка ясности имён файлов и переименование с обновлением ссылок
import sys
import re
import json
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import (
    read_file_safe, progress_bar, finish_progress,
    print_header, print_success, print_warning, print_hint,
    ask_yes_no, REPO_ROOT
)

SCAN_DIRS = ["terminology", "researches", "instructions", "davar", "ideas", "drafts"]
IGNORE_FILES = {"README.md", "STRUCTURE.md", "GLOSSARY.md", "STATS.md", "CHANGELOG.md",
                "CONTRIBUTORS.md", "BACKLOG.md", "DECISIONS.md", "ROADMAP.md",
                "TECHNICAL-DEBT.md", "RETROSPECTIVE.md", "COMPLETED-TASKS.md"}

MAX_WORDS = 3
MAX_LENGTH = 50
GOOD_NAME = re.compile(r'^[a-z][a-z0-9\-]+$')

# Имена, которые считаются хорошими (иврит латиницей)
KNOWN_GOOD_NAMES = {
    'emet', 'chesed', 'torah', 'shabbat', 'moed', 'brit', 'kohen', 'melech',
    'navi', 'tzom', 'pesach', 'shavuot', 'sukkot', 'yovel', 'shmitah',
    'el', 'elohim', 'yhwh', 'ruach', 'nefesh', 'neshamah', 'mashiah',
    'tefilah', 'tzedek', 'mishpat', 'hesed', 'emuna', 'avodah', 'derech',
    'kodesh', 'sheol', 'olam', 'chayim', 'shalom', 'ahava', 'yir-at-yhwh',
    'yetzer-lev', 'avar-atid', 'tchiyat-hametim', 'shema-yhwh-echad',
}

# Частые слова для перевода
COMMON_WORDS = {
    'исследование': 'research',
    'разоблачение': 'exposure',
    'система': 'system',
    'термин': 'term',
    'язык': 'language',
    'имя': 'shem',
    'слово': 'davar',
    'чистый': 'tahor',
    'речь': 'dibur',
    'праздник': 'moed',
    'сегодня': 'hayom',
    'закон': 'torah',
    'вера': 'emuna',
    'любовь': 'ahava',
    'истина': 'emet',
    'путь': 'derech',
    'мир': 'shalom',
    'жизнь': 'chayim',
    'смерть': 'mavet',
    'знание': 'daat',
    'время': 'zeman',
}


def transliterate(text: str) -> str:
    """Упрощённая транслитерация русских слов в латиницу."""
    # Проверяем частые слова
    if text.lower() in COMMON_WORDS:
        return COMMON_WORDS[text.lower()]

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


def extract_title(content: str) -> str:
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_topic(content: str) -> str:
    match = re.search(r'[-*]\s*\*\*Тема:\*\*\s*(.+?)(?:\n|$)', content)
    return match.group(1).strip() if match else ""


def suggest_name(filepath: Path, content: str, existing_names: set) -> str:
    stem = filepath.stem

    if stem in KNOWN_GOOD_NAMES:
        return ""
    if GOOD_NAME.match(stem) and len(stem.split('-')) <= MAX_WORDS and len(stem) <= MAX_LENGTH:
        return ""

    # Из темы
    topic = extract_topic(content)
    if topic:
        words = topic.lower().split()
        key_words = [w for w in words if len(w) > 2 and not w.startswith('«')][:MAX_WORDS]
        if key_words:
            suggested = transliterate('-'.join(key_words))
            if suggested and suggested != stem and suggested not in existing_names:
                return suggested

    # Из заголовка
    title = extract_title(content)
    if title:
        clean = re.sub(r'[📜🔥🛡️⚔️📖🎯🧭💻👑❤️⭐🙏✝️☦️✡️🔯🕎]', '', title)
        clean = re.sub(r'[«»"„"]', '', clean)
        stop_words = {'для', 'как', 'что', 'это', 'его', 'она', 'они', 'или', 'уже',
                      'ещё', 'под', 'над', 'при', 'про', 'без', 'перед', 'между'}
        words = clean.lower().split()
        key_words = [w for w in words if len(w) > 3 and w not in stop_words][:MAX_WORDS]
        if key_words:
            suggested = transliterate('-'.join(key_words))
            if suggested and suggested != stem and suggested not in existing_names:
                return suggested

    return ""


def check_name(filepath: Path) -> list:
    issues = []
    name = filepath.stem

    if not GOOD_NAME.match(name):
        issues.append(f"неверный формат: '{name}' (допустимы: a-z, 0-9, дефис)")
    if len(name) > MAX_LENGTH:
        issues.append(f"слишком длинное: {len(name)} символов (макс: {MAX_LENGTH})")
    if len(name.split('-')) > MAX_WORDS:
        issues.append(f"слишком много слов: {len(name.split('-'))} (макс: {MAX_WORDS})")
    if re.search(r'[а-яё]', name, re.IGNORECASE):
        issues.append("содержит русские буквы")
    for word in name.split('-'):
        if len(word) > 25:
            issues.append(f"длинное слово: '{word}' ({len(word)} символов)")

    return issues


def update_references(old_path: str, new_path: str):
    """Обновляет ссылки во всех md-файлах после переименования."""
    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(dir_path.rglob("*.md"))

    old_rel = old_path.replace('\\', '/')
    new_rel = new_path.replace('\\', '/')
    count = 0

    for filepath in all_files:
        content = read_file_safe(filepath)
        if not content or old_rel not in content:
            continue
        new_content = content.replace(old_rel, new_rel)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        count += 1

    return count


def update_files_json(old_path: str, new_path: str):
    """Обновляет пути в web/files.json."""
    json_path = REPO_ROOT / "web" / "files.json"
    if not json_path.exists():
        return 0
    try:
        data = json.loads(json_path.read_text(encoding='utf-8'))
        count = 0
        for item in data:
            if item.get("path") == old_path:
                item["path"] = new_path
                count += 1
        if count:
            json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        return count
    except:
        return 0


def main():
    fix_mode = "--fix" in sys.argv
    dry_run = "--dry-run" in sys.argv
    save_mode = "--save" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    label = "DRY-RUN" if dry_run else ("ОПТИМИЗАЦИЯ" if fix_mode else "ПРОВЕРКА")
    print_header(f"ПРОВЕРКА ЯСНОСТИ ИМЁН ФАЙЛОВ — {label}", "📛")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    existing_names = {f.stem for f in all_files}
    total = len(all_files)
    print(f"🔍 Файлов: {total}")

    files_with_issues = []
    suggestions = {}
    total_issues = 0

    for i, filepath in enumerate(all_files, 1):
        if filepath.name in IGNORE_FILES:
            continue

        content = read_file_safe(filepath)
        if not content:
            continue

        issues = check_name(filepath)
        if issues:
            rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
            files_with_issues.append((filepath, rel_path, issues))
            total_issues += len(issues)
            suggestion = suggest_name(filepath, content, existing_names)
            if suggestion:
                suggestions[rel_path] = suggestion

        progress_bar(i, total, extra=f"проблем: {total_issues}")

    finish_progress()

    if not files_with_issues:
        print_success("🎉 Все имена файлов ясные и краткие")
        return 0

    print(f"\n📁 Файлов с проблемами: {len(files_with_issues)}")
    print(f"📝 Всего проблем: {total_issues}")
    print(f"💡 Предложений по переименованию: {len(suggestions)}\n")

    # Типы проблем
    issue_types = Counter()
    for _, _, issues in files_with_issues:
        for issue in issues:
            for prefix in ["неверный формат", "слишком длинное", "слишком много слов",
                           "содержит русские", "длинное слово"]:
                if issue.startswith(prefix):
                    issue_types[prefix] += 1
                    break

    print("📊 По типам:")
    for itype, count in issue_types.most_common():
        print(f"  • {itype}: {count}")

    # Список файлов
    print(f"\n📋 Файлы ({len(files_with_issues)}):")
    for filepath, path, issues in (files_with_issues[:30] if not verbose else files_with_issues):
        short = '; '.join(issues)
        sugg = f" → {suggestions[path]}.md" if path in suggestions else ""
        print(f"  📄 {path}: {short}{sugg}")
    if len(files_with_issues) > 30 and not verbose:
        print(f"  ... и ещё {len(files_with_issues) - 30}")

    if fix_mode or dry_run:
        if not suggestions:
            print_warning("Нет файлов для переименования (нет предложений)")
            return 0

        if not ask_yes_no(f"\n{'[DRY-RUN] ' if dry_run else ''}Переименовать {len(suggestions)} файлов?"):
            return 0

        renamed = 0
        refs_updated = 0
        json_updated = 0

        for i, (filepath, rel_path, _) in enumerate(files_with_issues, 1):
            if rel_path not in suggestions:
                continue

            new_stem = suggestions[rel_path]
            new_path = filepath.parent / (new_stem + ".md")
            new_rel = str(new_path.relative_to(REPO_ROOT)).replace('\\', '/')

            if new_path.exists() and new_path != filepath:
                continue

            if not dry_run:
                filepath.rename(new_path)
                refs = update_references(rel_path, new_rel)
                refs_updated += refs
                json_upd = update_files_json(rel_path, new_rel)
                json_updated += json_upd

            renamed += 1
            progress_bar(i, len(files_with_issues),
                         extra=f"переименовано: {renamed} | ссылок: {refs_updated}")

        finish_progress()

        if dry_run:
            print_success(f"[DRY-RUN] Будет переименовано: {renamed} файлов")
        else:
            print_success(f"✅ Переименовано: {renamed} файлов")
            if refs_updated:
                print_success(f"🔗 Обновлено ссылок в: {refs_updated} файлах")
            if json_updated:
                print_success(f"📋 Обновлено в files.json: {json_updated} записей")
            print_hint("Запустите sync-structure.py для обновления STRUCTURE.md")

    elif save_mode:
        report = REPO_ROOT / "reports" / "file-names-report.md"
        lines = ["# 📛 ОТЧЁТ ОБ ИМЕНАХ ФАЙЛОВ", "", f"**Проблемных файлов:** {len(files_with_issues)}", ""]
        for _, path, issues in files_with_issues:
            lines.append(f"- **{path}**: {', '.join(issues)}")
            if path in suggestions:
                lines.append(f"  → {suggestions[path]}.md")
        report.parent.mkdir(exist_ok=True)
        report.write_text("\n".join(lines) + "\n", encoding='utf-8')
        print_success(f"Отчёт сохранён: {report}")
    else:
        print_hint(f"\nПредложений: {len(suggestions)}")
        print_hint("Запустите --fix для переименования")
        print_hint("Запустите --dry-run для предпросмотра")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())