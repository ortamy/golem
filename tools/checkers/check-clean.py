#!/usr/bin/env python3
"""
Checker-cleaner эмодзи в заголовках md-файлов.
Режимы:
  check — найти и показать все эмодзи в первых строках-заголовках
  clean — удалить эмодзи из первых строк-заголовков
"""

import os
import re
import argparse
from collections import defaultdict

# Упрощённый паттерн для эмодзи — основные диапазоны без конфликтных
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F9FF"  # основная масса эмодзи
    "\U0001FA00-\U0001FAFF"  # расширенные
    "\U00002600-\U000027BF"  # символы и значки
    "\U0001F1E0-\U0001F1FF"  # флаги
    "\U0000FE00-\U0000FE0F"  # вариационные селекторы
    "\U0000200D"             # zero width joiner
    "\U0000200C"             # zero width non-joiner
    "\U00002714"             # ✔
    "\U00002705"             # ✅
    "\U0000274C"             # ❌
    "\U00002757"             # ❗
    "\U00002753"             # ❓
    "\U00002049"             # ⁉
    "\U0000203C"             # ‼
    "\U0001F500-\U0001F53D"  # символы
    "\U0001F4A0-\U0001F4F9"  # предметы
    "\U0001F3E0-\U0001F3F0"  # здания
    "\U0001F400-\U0001F43F"  # животные
    "\U0001F330-\U0001F37F"  # растения
    "\U0001F000-\U0001F02F"  # маджонг
    "\U00002B50"             # ⭐
    "\U00002B55"             # ⭕
    "\U0001F600-\U0001F64F"  # смайлики
    "\U0001F680-\U0001F6FF"  # транспорт
    "\U0001F700-\U0001F77F"  # алхимия
    "\U0001F780-\U0001F7FF"  # геометрические
    "\U0001F800-\U0001F8FF"  # стрелки
    "\U0001F900-\U0001F9FF"  # доп символы
    "\U00002300-\U000023FF"  # технические
    "\U000025AA-\U000025AB"  # квадраты
    "\U000025B6"             # ▶
    "\U000025C0"             # ◀
    "\U000025FB-\U000025FE"  # квадраты
    "\U00002614-\U00002615"  # зонтик
    "\U00002648-\U00002653"  # зодиак
    "\U0000267B"             # ♻
    "\U0000267F"             # ♿
    "\U00002693"             # ⚓
    "\U000026A0-\U000026A1"  # ⚠ ⚡
    "\U000026AA-\U000026AB"  # ⚪ ⚫
    "\U000026BD-\U000026BE"  # ⚽ ⚾
    "\U000026C4-\U000026C5"  # ⛄ ⛅
    "\U000026CE"             # ⛎
    "\U000026D4"             # ⛔
    "\U000026EA"             # ⛪
    "\U000026F2-\U000026F3"  # ⛲ ⛳
    "\U000026F5"             # ⛵
    "\U000026FA"             # ⛺
    "\U000026FD"             # ⛽
    "\U00002702"             # ✂
    "\U00002708-\U0000270F"  # ✈-✏
    "\U00002712"             # ✒
    "\U00002714"             # ✔
    "\U00002716"             # ✖
    "\U0000271D"             # ✝
    "\U00002721"             # ✡
    "\U00002733-\U00002734"  # ✳ ✴
    "\U00002744"             # ❄
    "\U00002747"             # ❇
    "\U0000274E"             # ❎
    "\U00002763-\U00002764"  # ❣ ❤
    "\U00002795-\U00002797"  # ➕-➗
    "\U000027A1"             # ➡
    "\U000027B0"             # ➰
    "\U000027BF"             # ➿
    "\U00002934-\U00002935"  # ⤴ ⤵
    "\U00002B05-\U00002B07"  # ⬅-⬇
    "\U00002B1B-\U00002B1C"  # ⬛ ⬜
    "\U00003030"             # 〰
    "\U0000303D"             # 〽
    "\U00003297"             # ㊗
    "\U00003299"             # ㊙
    "]+",
    re.UNICODE
)

# Паттерн для извлечения отдельных эмодзи (для отчёта)
EMOJI_EXTRACT = re.compile(
    "(["
    "\U0001F300-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E0-\U0001F1FF"
    "\U0000FE00-\U0000FE0F"
    "\U0000200D"
    "\U0000200C"
    "\U00002714"
    "\U00002705"
    "\U0000274C"
    "\U00002757"
    "\U00002753"
    "\U00002049"
    "\U0000203C"
    "\U00002B50"
    "\U00002B55"
    "])",
    re.UNICODE
)


def extract_emojis(text):
    """Извлекает все эмодзи из текста."""
    return EMOJI_EXTRACT.findall(text)


def clean_heading(text):
    """Убирает эмодзи из строки заголовка."""
    cleaned = EMOJI_PATTERN.sub('', text).strip()
    cleaned = re.sub(r'  +', ' ', cleaned)

    if cleaned.startswith('#') and not cleaned.startswith('# '):
        cleaned = '# ' + cleaned[1:].strip()

    return cleaned


def process_file_check(filepath):
    """Проверяет файл на эмодзи в первом заголовке."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            return None

        first_line = lines[0]

        if not first_line.startswith('# '):
            return None

        emojis = extract_emojis(first_line)
        if not emojis:
            return None

        return {
            'filepath': filepath,
            'original': first_line.strip(),
            'cleaned': clean_heading(first_line),
            'emojis': emojis
        }

    except Exception as e:
        return {'filepath': filepath, 'error': str(e)}


def process_file_clean(filepath, dry_run=False):
    """Убирает эмодзи из первого заголовка."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            return None

        first_line = lines[0]

        if not first_line.startswith('# '):
            return None

        emojis = extract_emojis(first_line)
        if not emojis:
            return None

        cleaned = clean_heading(first_line)

        if cleaned == first_line.strip():
            return None

        if dry_run:
            return {
                'filepath': filepath,
                'original': first_line.strip(),
                'cleaned': cleaned,
                'emojis': emojis
            }

        lines[0] = cleaned + '\n'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return {
            'filepath': filepath,
            'original': first_line.strip(),
            'cleaned': cleaned,
            'emojis': emojis
        }

    except Exception as e:
        return {'filepath': filepath, 'error': str(e)}


def find_md_files(root_dir, exclude_dirs=None):
    """Находит все md-файлы."""
    if exclude_dirs is None:
        exclude_dirs = {'node_modules', '.git', '__pycache__', '.venv', 'venv'}

    md_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for filename in filenames:
            if filename.endswith('.md'):
                md_files.append(os.path.join(dirpath, filename))

    return md_files


def print_report(results, mode, dry_run=False):
    """Универсальный отчёт."""
    total = len(results)
    errors = [r for r in results if 'error' in r]
    valid = [r for r in results if 'error' not in r]

    if mode == 'check':
        title = "ПРОВЕРКА ЭМОДЗИ В ЗАГОЛОВКАХ"
    else:
        title = "DRY RUN (без изменений)" if dry_run else "ОЧИСТКА ЗАГОЛОВКОВ"

    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print(f"  Всего файлов:          {total}")
    print(f"  Заголовков с эмодзи:   {len(valid)}")
    print(f"  Ошибок:                {len(errors)}")

    if errors:
        print(f"\n  Ошибки:")
        for r in errors:
            print(f"     {r['filepath']}: {r['error']}")

    if valid:
        emoji_stats = defaultdict(list)
        for r in valid:
            for e in r['emojis']:
                emoji_stats[e].append(r['filepath'])

        print(f"\n  ЭМОДЗИ ПО ТИПАМ:")
        for emoji, files in sorted(emoji_stats.items(), key=lambda x: -len(x[1])):
            print(f"     {emoji} — {len(files)} раз(а)")

        print(f"\n  ФАЙЛЫ:")
        for i, r in enumerate(valid, 1):
            print(f"\n  {i}. {r['filepath']}")
            print(f"     Было:  {r['original']}")
            print(f"     Стало: {r['cleaned']}")

    print("\n" + "=" * 70)

    if mode == 'check':
        print("  Для удаления: python check-clean.py clean")
    elif dry_run:
        print("  Это dry run. Файлы НЕ изменены.")
        print("  Для удаления: python check-clean.py clean")
    else:
        print("  Заголовки очищены.")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Checker-cleaner эмодзи в заголовках md-файлов'
    )
    parser.add_argument(
        'mode',
        nargs='?',
        default='check',
        choices=['check', 'clean'],
        help='Режим: check или clean'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Путь к директории'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Только показать изменения'
    )
    parser.add_argument(
        '--exclude',
        nargs='*',
        default=None,
        help='Дополнительные директории для исключения'
    )

    args = parser.parse_args()

    exclude = {'node_modules', '.git', '__pycache__', '.venv', 'venv', 'web'}
    if args.exclude:
        exclude.update(args.exclude)

    md_files = find_md_files(args.path, exclude)

    if args.mode == 'check':
        results = []
        for f in md_files:
            r = process_file_check(f)
            if r:
                results.append(r)
        print_report(results, 'check')

    else:
        results = []
        for f in md_files:
            r = process_file_clean(f, args.dry_run)
            if r:
                results.append(r)
        print_report(results, 'clean', args.dry_run)


if __name__ == '__main__':
    main()