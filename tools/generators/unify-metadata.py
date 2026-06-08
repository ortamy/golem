# tools/generators/unify-metadata.py — адаптивная унификация метаданных
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_warning, print_hint, ask_yes_no, REPO_ROOT

SCAN_DIRS = ["terminology", "researches", "instructions", "davar", "ideas", "drafts", "docs"]

# Обязательные поля для всех категорий (строгий порядок)
CORE_FIELDS_ORDER = [
    "Файл:",
    "Версия:",
    "Дата создания:",
    "Последнее обновление:",
    "Причина обновления:",
    "Статус:",
    "Тема:",
]

# Дополнительные поля по категориям (после обязательных, порядок сохраняется)
CATEGORY_FIELDS = {
    "terminology": [
        "Иврит:",
        "Транслитерация:",
        "Корень:",
        "Этимология:",
    ],
    "researches": [
        "Источник:",
        "Метод:",
        "Тип искажения:",
        "Примечание:",
    ],
    "instructions": [
        "Назначение:",
        "Примечание:",
    ],
    "methodology": [
        "Метод:",
        "Инструменты:",
    ],
    "tahor": [
        "Категория:",
        "Примечание:",
    ],
    "exposure": [
        "Тип:",
        "Примечание:",
    ],
    "davar": [
        "Статус разработки:",
        "Примечание:",
    ],
    "docs": [
        "Назначение:",
    ],
}

# Значения по умолчанию
DEFAULTS = {
    "Версия:": "1.0",
    "Статус:": "Активный",
    "Причина обновления:": "Первичное создание",
}

# Варианты названий полей для распознавания
FIELD_ALIASES = {
    "Файл:": ["Файл:", "файл:", "File:", "file:"],
    "Версия:": ["Версия:", "версия:", "Version:", "version:", "Гирса:"],
    "Дата создания:": ["Дата создания:", "дата создания:", "Created:", "created:", "Таарих:"],
    "Последнее обновление:": ["Последнее обновление:", "последнее обновление:", "Last updated:", "last updated:", "Обновление:", "Итхадшут:", "hитхадшут:", "Хидшут:"],
    "Причина обновления:": ["Причина обновления:", "причина обновления:", "Reason:", "reason:", "Сиба:"],
    "Статус:": ["Статус:", "статус:", "Status:", "status:", "Маамад:", "Сманут:"],
    "Тема:": ["Тема:", "тема:", "Topic:", "topic:", "Носе:", "Носэ:"],
    "Иврит:": ["Иврит:", "иврит:", "Hebrew:", "hebrew:", "Ивритское написание:"],
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
    "Имя файла:": ["Имя файла:", "Filename:"],  # для docs/
}


def get_category(file_path: str) -> str:
    """Определяет категорию файла по пути."""
    parts = Path(file_path).parts

    if len(parts) >= 2:
        if parts[0] == "instructions":
            if len(parts) >= 3:
                sub = parts[1]
                if sub in CATEGORY_FIELDS:
                    return sub
            return "instructions"
        if parts[0] in CATEGORY_FIELDS:
            return parts[0]

    return "other"


def get_allowed_fields(file_path: str) -> list:
    """Возвращает список разрешённых полей для файла."""
    category = get_category(file_path)
    fields = list(CORE_FIELDS_ORDER)

    if category in CATEGORY_FIELDS:
        fields.extend(CATEGORY_FIELDS[category])

    return fields


def extract_metadata_block(content: str) -> tuple:
    """Извлекает блок метаданных. Возвращает (начало, конец, текст)."""
    if '**Метаданные файла**' not in content:
        return -1, -1, ""

    start = content.find('**Метаданные файла**')
    rest = content[start:]

    # Ищем конец блока
    end_match = re.search(r'\n---|\n# |\n## ', rest[30:])
    if end_match:
        end = start + 30 + end_match.start()
    else:
        end = len(content)

    return start, end, content[start:end]


def parse_fields(block: str) -> dict:
    """Извлекает все поля из блока метаданных в словарь {поле: значение}."""
    fields = {}

    # Ищем все строки вида - **Поле:** значение
    pattern = re.compile(r'[-*]\s*\*\*([^*]+)\*\*\s*(.+)')
    for match in pattern.finditer(block):
        raw_name = match.group(1).strip()
        raw_value = match.group(2).strip()

        # Убираем обратные кавычки и лишние пробелы
        value = raw_value.strip('`').strip()
        if value.endswith('\\'):
            value = value[:-1]

        # Нормализуем имя поля
        normalized = normalize_field_name(raw_name)
        if normalized:
            fields[normalized] = value

    return fields


def normalize_field_name(raw: str) -> str:
    """Приводит название поля к стандартному виду."""
    raw_clean = raw.strip()

    for standard, aliases in FIELD_ALIASES.items():
        if raw_clean in aliases or raw_clean.lower() in [a.lower() for a in aliases]:
            return standard

    # Если не найдено — возвращаем как есть (пользовательское поле)
    # Но чистим от мусора
    clean = re.sub(r'[📜🔥🛡️⚔️📖🎯🧭💻👑❤️🏷️📊📋🔍🌐📁📝]', '', raw_clean).strip()
    return clean if clean else raw_clean


def build_metadata_block(fields: dict, allowed_fields: list) -> str:
    """Строит блок метаданных из словаря полей."""
    lines = ["**Метаданные файла**"]

    # Сначала обязательные поля в правильном порядке
    for field in CORE_FIELDS_ORDER:
        if field in fields and fields[field]:
            value = fields[field]
            lines.append(format_field(field, value))

    # Потом дополнительные поля из категории
    for field in allowed_fields:
        if field in CORE_FIELDS_ORDER:
            continue
        if field in fields and fields[field]:
            value = fields[field]
            lines.append(format_field(field, value))

    # Потом пользовательские поля (которых нет в списках)
    for field, value in fields.items():
        if field in CORE_FIELDS_ORDER:
            continue
        if field in allowed_fields:
            continue
        if value:
            lines.append(format_field(field, value))

    return "\n".join(lines)


def format_field(name: str, value: str) -> str:
    """Форматирует одно поле метаданных."""
    if name in ("Файл:", "Имя файла:"):
        return f"- **{name}** `{value}`"
    return f"- **{name}** {value}"


def unify_file(filepath: Path, file_path: str) -> tuple:
    """Унифицирует метаданные одного файла. Возвращает (изменён, сообщение)."""
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

    # Строим новый блок
    new_block = build_metadata_block(fields, allowed_fields)

    # Собираем новый контент
    new_content = content[:block_start] + new_block + content[block_end:]

    changed = new_content != content
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return changed, "OK"


def main():
    fix_mode = "--fix" in sys.argv
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print_header("ПРЕДПРОСМОТР УНИФИКАЦИИ МЕТАДАННЫХ", "🔍")
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

    stats = {"updated": 0, "no_metadata": 0, "ok": 0, "errors": []}

    for i, filepath in enumerate(all_files, 1):
        rel_path = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')

        if '**Метаданные файла**' not in (read_file_safe(filepath) or ""):
            stats["no_metadata"] += 1
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
            # Проверка без изменений
            fields = parse_fields((read_file_safe(filepath) or "")[extract_metadata_block(read_file_safe(filepath) or "")[0]:extract_metadata_block(read_file_safe(filepath) or "")[1]])
            allowed = get_allowed_fields(rel_path)
            missing = [f for f in CORE_FIELDS_ORDER if f not in fields or not fields[f]]
            extra = [f for f in fields if f not in allowed and f not in CORE_FIELDS_ORDER]

            if missing:
                stats["updated"] += 1  # нуждается в обновлении
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
        for path, msg in stats["errors"][:5]:
            print(f"     • {path}: {msg}")

    if not fix_mode and stats["updated"] > 0:
        print_hint("Для унификации: python tools/generators/unify-metadata.py --fix")
        print_hint("Для предпросмотра: python tools/generators/unify-metadata.py --dry-run")

    return 0


if __name__ == "__main__":
    sys.exit(main())

