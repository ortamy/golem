# tools/generators/generate-metadata.py — адаптивная унификация метаданных (v2.0)
import sys
import re
import hashlib
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_hint, ask_yes_no, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions", "davar", "ideas", "drafts", "docs"]

CORE_FIELDS_ORDER = [
    "Файл:", "Версия:", "Дата создания:", "Последнее обновление:",
    "Причина обновления:", "Статус:", "Тема:",
    "Аудит:", "Язык:", "Ключевые слова:",
    "Связанные файлы:", "Хеш:", "Достоверность:",
    "Последний аудит:", "Проверок на религионизмы:", "Последняя проверка:",
]

CATEGORY_FIELDS = {
    "terminology": ["Иврит:", "Транслитерация:", "Корень:", "Этимология:"],
    "researches": ["Источник:", "Метод:", "Тип искажения:", "Примечание:"],
    "instructions": ["Назначение:", "Примечание:"],
    "methodology": ["Метод:", "Инструменты:"],
    "tahor": ["Категория:", "Примечание:"],
    "exposure": ["Тип:", "Примечание:"],
    "davar": ["Статус разработки:", "Примечание:"],
    "docs": ["Назначение:"],
}

DEFAULTS = {
    "Версия:": "1.0",
    "Статус:": "Активный",
    "Причина обновления:": "Первичное создание",
    "Аудит:": "bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳",
    "Язык:": "русский",
    "Достоверность:": "средняя",
}

FIELD_ALIASES = {
    "Файл:": ["Файл:", "файл:", "File:", "file:"],
    "Версия:": ["Версия:", "версия:", "Version:", "version:", "Гирса:"],
    "Дата создания:": ["Дата создания:", "дата создания:", "Created:", "created:", "Таарих:"],
    "Последнее обновление:": ["Последнее обновление:", "последнее обновление:", "Last updated:", "last updated:", "Обновление:", "Итхадшут:", "hитхадшут:", "Хидшут:"],
    "Причина обновления:": ["Причина обновления:", "причина обновления:", "Reason:", "reason:", "Сиба:"],
    "Статус:": ["Статус:", "статус:", "Status:", "status:", "Маамад:", "Сманут:"],
    "Тема:": ["Тема:", "тема:", "Topic:", "topic:", "Носе:", "Носэ:"],
    "Аудит:": ["Аудит:", "аудит:", "Audit:", "audit:"],
    "Язык:": ["Язык:", "язык:", "Language:", "language:"],
    "Ключевые слова:": ["Ключевые слова:", "ключевые слова:", "Keywords:", "keywords:", "Tags:", "tags:"],
    "Связанные файлы:": ["Связанные файлы:", "связанные файлы:", "Related:", "related:", "See also:", "see also:"],
    "Хеш:": ["Хеш:", "хеш:", "Hash:", "hash:"],
    "Достоверность:": ["Достоверность:", "достоверность:", "Confidence:", "confidence:"],
    "Последний аудит:": ["Последний аудит:", "последний аудит:", "Last audit:", "last audit:"],
    "Проверок на религионизмы:": ["Проверок на религионизмы:", "проверок на религионизмы:", "Religionism checks:"],
    "Последняя проверка:": ["Последняя проверка:", "последняя проверка:", "Last check:", "last check:"],
    "Иврит:": ["Иврит:", "иврит:", "Hebrew:", "hebrew:"],
    "Транслитерация:": ["Транслитерация:", "транслитерация:", "Transliteration:"],
    "Корень:": ["Корень:", "корень:", "Root:", "root:", "Шореш:"],
    "Этимология:": ["Этимология:", "этимология:", "Etymology:"],
    "Источник:": ["Источник:", "источник:", "Source:", "source:", "Макор:"],
    "Метод:": ["Метод:", "метод:", "Method:", "method:", "Шита:"],
    "Тип искажения:": ["Тип искажения:", "тип искажения:", "Distortion type:"],
    "Примечание:": ["Примечание:", "примечание:", "Note:", "note:", "Заметки:", "Заметка:", "hеара:"],
    "Назначение:": ["Назначение:", "назначение:", "Purpose:", "purpose:"],
    "Категория:": ["Категория:", "категория:", "Category:", "category:"],
    "Инструменты:": ["Инструменты:", "инструменты:", "Tools:", "tools:"],
    "Тип:": ["Тип:", "тип:", "Type:", "type:"],
    "Статус разработки:": ["Статус разработки:", "статус разработки:", "Dev status:"],
    "Имя файла:": ["Имя файла:", "Filename:"],
}


def get_category(file_path: str) -> str:
    parts = Path(file_path).parts
    if len(parts) >= 2:
        if parts[0] == "instructions":
            if len(parts) >= 3 and parts[1] in CATEGORY_FIELDS:
                return parts[1]
            return "instructions"
        if parts[0] in CATEGORY_FIELDS:
            return parts[0]
    return "other"


def get_allowed_fields(file_path: str) -> list:
    fields = list(CORE_FIELDS_ORDER)
    category = get_category(file_path)
    if category in CATEGORY_FIELDS:
        fields.extend(CATEGORY_FIELDS[category])
    return fields


def extract_metadata_block(content: str) -> tuple:
    if '**Метаданные файла**' not in content:
        return -1, -1, ""
    start = content.find('**Метаданные файла**')
    rest = content[start:]
    end_match = re.search(r'\n---|\n# |\n## ', rest[30:])
    end = start + 30 + end_match.start() if end_match else len(content)
    return start, end, content[start:end]


def parse_fields(block: str) -> dict:
    fields = {}
    for match in re.finditer(r'[-*]\s*\*\*([^*]+)\*\*\s*(.+)', block):
        raw_name = match.group(1).strip()
        raw_value = match.group(2).strip().strip('`').strip()
        if raw_value.endswith('\\'):
            raw_value = raw_value[:-1]
        normalized = normalize_field_name(raw_name)
        if normalized:
            fields[normalized] = raw_value
    return fields


def normalize_field_name(raw: str) -> str:
    raw_clean = raw.strip()
    for standard, aliases in FIELD_ALIASES.items():
        if raw_clean in aliases or raw_clean.lower() in [a.lower() for a in aliases]:
            return standard
    clean = re.sub(r'[📜🔥🛡️⚔️📖🎯🧭💻👑❤️🏷️📊📋🔍🌐📁📝]', '', raw_clean).strip()
    return clean if clean else raw_clean


def compute_hash(content: str) -> str:
    body = content
    if '**Метаданные файла**' in content:
        start = content.find('**Метаданные файла**')
        rest = content[start:]
        end_match = re.search(r'\n---|\n# |\n## ', rest[30:])
        if end_match:
            body = content[:start] + rest[30 + end_match.start():]
    return hashlib.md5(body.encode('utf-8')).hexdigest()[:8]


def build_metadata_block(fields: dict, allowed_fields: list) -> str:
    lines = ["**Метаданные файла**"]
    for field in CORE_FIELDS_ORDER:
        if field in fields and fields[field]:
            lines.append(format_field(field, fields[field]))
    for field in allowed_fields:
        if field in CORE_FIELDS_ORDER:
            continue
        if field in fields and fields[field]:
            lines.append(format_field(field, fields[field]))
    for field, value in fields.items():
        if field in CORE_FIELDS_ORDER or field in allowed_fields:
            continue
        if value:
            lines.append(format_field(field, value))
    return "\n".join(lines)


def format_field(name: str, value: str) -> str:
    if name in ("Файл:", "Имя файла:"):
        return f"- **{name}** `{value}`"
    return f"- **{name}** {value}"


def unify_file(filepath: Path, file_path: str) -> tuple:
    content = read_file_safe(filepath)
    if not content:
        return False, "ошибка чтения"
    if '**Метаданные файла**' not in content:
        return False, "нет метаданных"

    block_start, block_end, _ = extract_metadata_block(content)
    if block_start == -1:
        return False, "блок не найден"

    allowed_fields = get_allowed_fields(file_path)
    fields = parse_fields(content[block_start:block_end])
    category = get_category(file_path)

    # Заполняем недостающие обязательные поля
    for field in CORE_FIELDS_ORDER:
        if field not in fields or not fields[field]:
            if field == "Файл:":
                fields[field] = file_path
            elif field in DEFAULTS:
                fields[field] = DEFAULTS[field]
            elif field == "Тема:":
                title_match = re.search(r'^#\s+[📜🔥🛡️⚔️📖🎯🧭💻👑❤️]\s*(.+?)$', content, re.MULTILINE)
                fields[field] = title_match.group(1).strip() if title_match else "Требует уточнения"
            elif field == "Дата создания:" and "Последнее обновление:" in fields:
                fields[field] = fields["Последнее обновление:"]
            elif field == "Последнее обновление:" and "Дата создания:" in fields:
                fields[field] = fields["Дата создания:"]
            elif field == "Хеш:":
                fields[field] = compute_hash(content)
            elif field == "Последний аудит:":
                fields[field] = datetime.now().strftime("%Y-%m-%d")
            elif field == "Связанные файлы:":
                related = re.findall(r'`((?:terminology|researches|instructions)/.*?\.md)`', content)
                if related:
                    fields[field] = ", ".join(f"`{r}`" for r in related[:5])
            elif field == "Язык:" and category == "terminology":
                fields[field] = "иврит"

    new_block = build_metadata_block(fields, allowed_fields)
    new_content = content[:block_start] + new_block + content[block_end:]
    changed = new_content != content
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    return changed, "OK"


def add_metadata(filepath: Path, file_path: str) -> bool:
    content = read_file_safe(filepath)
    if not content:
        return False

    today = datetime.now().strftime("%Y-%m-%d")
    title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    topic = title_match.group(1).strip() if title_match else "Требует уточнения"
    topic = re.sub(r'[📜🔥🛡️⚔️📖🎯🧭💻👑❤️]\s*', '', topic)

    category = get_category(file_path)

    fields = {
        "Файл:": file_path,
        "Версия:": "1.0",
        "Дата создания:": today,
        "Последнее обновление:": today,
        "Причина обновления:": "Первичное создание",
        "Статус:": "Активный",
        "Тема:": topic,
        "Аудит:": "bdikah ⏳ | mivdak ⏳ | tikun ⏳ | factcheck ⏳",
        "Язык:": "иврит" if category == "terminology" else "русский",
        "Хеш:": compute_hash(content),
        "Достоверность:": "средняя",
        "Последний аудит:": today,
    }

    allowed_fields = get_allowed_fields(file_path)
    new_block = build_metadata_block(fields, allowed_fields)

    first_header = re.search(r'^#\s+.+$', content, re.MULTILINE)
    if first_header:
        insert_pos = first_header.end()
        new_content = content[:insert_pos] + "\n\n" + new_block + "\n" + content[insert_pos:]
    else:
        new_content = new_block + "\n\n" + content

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True


def main():
    fix_mode = "--fix" in sys.argv
    add_mode = "--add" in sys.argv
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print_header("ПРЕДПРОСМОТР УНИФИКАЦИИ МЕТАДАННЫХ", "🔍")
    elif add_mode:
        print_header("ДОБАВЛЕНИЕ МЕТАДАННЫХ", "➕")
    elif fix_mode:
        print_header("УНИФИКАЦИЯ МЕТАДАННЫХ", "🔧")
    else:
        print_header("ПРОВЕРКА МЕТАДАННЫХ", "📋")

    all_files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            all_files.extend(sorted(dir_path.rglob("*.md")))

    total = len(all_files)
    print(f"Найдено файлов: {total}")

    no_meta_files = []
    for filepath in all_files:
        content = read_file_safe(filepath)
        if content and '**Метаданные файла**' not in content:
            no_meta_files.append(filepath)

    stats = {"updated": 0, "no_metadata": len(no_meta_files), "ok": 0, "added": 0, "errors": []}

    if add_mode:
        if not ask_yes_no(f"Добавить метаданные в {len(no_meta_files)} файлов?"):
            print("👋 Отменено.")
            return 0
        for i, filepath in enumerate(no_meta_files, 1):
            rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
            if add_metadata(filepath, rel_path):
                stats["added"] += 1
            progress_bar(i, len(no_meta_files), extra=f"добавлено: {stats['added']}")
        finish_progress()
        print_success(f"Метаданные добавлены в {stats['added']} файлов")
        return 0

    for i, filepath in enumerate(all_files, 1):
        rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
        content = read_file_safe(filepath)

        if not content or '**Метаданные файла**' not in content:
            progress_bar(i, total, extra=f"OK: {stats['ok']} | обновлено: {stats['updated']} | без: {stats['no_metadata']}")
            continue

        if fix_mode and not dry_run:
            changed, msg = unify_file(filepath, rel_path)
            if changed:
                stats["updated"] += 1
            elif msg == "OK":
                stats["ok"] += 1
            else:
                stats["errors"].append((rel_path, msg))
        else:
            block_start, block_end, _ = extract_metadata_block(content)
            if block_start >= 0:
                fields = parse_fields(content[block_start:block_end])
                missing = [f for f in CORE_FIELDS_ORDER if f not in fields or not fields[f]]
                if missing:
                    stats["updated"] += 1
                else:
                    stats["ok"] += 1

        progress_bar(i, total, extra=f"OK: {stats['ok']} | обновлено: {stats['updated']} | без: {stats['no_metadata']}")

    finish_progress()

    print(f"\n📊 Результаты:")
    print(f"   Уже в порядке: {stats['ok']}")
    print(f"   Обновлено: {stats['updated']}")
    print(f"   Без метаданных: {stats['no_metadata']}")

    if stats["errors"]:
        print_warning(f"   Ошибок: {len(stats['errors'])}")

    if stats["no_metadata"] > 0:
        print_hint(f"Добавить метаданные в {stats['no_metadata']} файлов: python tools/generators/unify-metadata.py --add")
    if not fix_mode and stats["updated"] > 0:
        print_hint("Для унификации: python tools/generators/unify-metadata.py --fix")

    return 0


if __name__ == "__main__":
    sys.exit(main())

