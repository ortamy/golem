#!/usr/bin/env python3
"""
Checker: проверяет активные md-файлы в content/researches/ (исключая archive/)
на соответствие шаблону TEMPLATE-RESEARCH.md.

Правила:
- Стрелки → НЕ ошибка (это формат глоссария: русское → ИВРИТ — описание)
- Троеточия ... считаются в не-заголовочном/не-цитатном контексте (> 2 = незавершённость)
- Метаданные: оба формата **Поле:** и **Поле**:
- Секции: ВВЕДЕНИЕ, РАЗОБЛАЧЕНИЕ, СВОДКА (с любыми эмодзи/иконками)

Usage:
  python check-active-researches.py
"""

import os
import re
import sys

RESEARCHES_DIR = 'content/researches'
EXCLUDE_DIRS = {'archive', 'node_modules', '.git', '__pycache__'}

REQUIRED_SECTIONS = ["ВВЕДЕНИЕ", "РАЗОБЛАЧЕНИЕ", "СВОДКА"]
REQUIRED_META_KEYS = ["Файл", "Версия", "Статус", "Тема"]


def check_file(filepath):
    """Проверяет один md-файл и возвращает список проблем."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f'ERROR({e})']

    issues = []

    # ===== 1. Метаданные =====
    # Формат 1: **Поле:** значение
    meta1 = set(re.findall(r'-\s+\*\*([^*:]+):\*\*', content))
    # Формат 2: **Поле**: значение
    meta2 = set(re.findall(r'-\s+\*\*([^*]+?)\*\*:', content))
    all_meta_fields = meta1 | meta2
    
    # Проверяем обязательные поля
    missing = []
    for key in REQUIRED_META_KEYS:
        found = False
        for f in all_meta_fields:
            if f.strip() == key:
                found = True
                break
        if not found:
            missing.append(key)
    
    if missing:
        issues.append(f'MISSING_METADATA({",".join(missing)})')
    if len(all_meta_fields) < 4:
        issues.append(f'FEW_METADATA({len(all_meta_fields)} fields)')

    # ===== 2. Обязательные секции =====
    missing_sec = []
    for sec in REQUIRED_SECTIONS:
        # Ищем ## с любыми символами до названия секции
        if not re.search(rf'##\s.*{re.escape(sec)}', content):
            missing_sec.append(sec)
    if missing_sec:
        issues.append(f'MISSING_SECTIONS({",".join(missing_sec)})')

    # ===== 3. Троеточия (незавершённость) =====
    # Считаем только в тексте, не в заголовках, не в метаданных, не в цитатах
    ellipsis_total = 0
    for line in content.split('\n'):
        s = line.strip()
        if s.startswith('#') or s.startswith('>') or s.startswith('- **') or s.startswith('**'):
            continue
        ellipsis_total += len(re.findall(r'\.\.\.', s))
    
    if ellipsis_total > 2:
        issues.append(f'NOT_FINISHED({ellipsis_total} ellipses in text)')

    # ===== 4. Иконки (только проверка существования) =====
    for m in re.finditer(r'!\[icon\]\(icons/32/([^)]+)\)', content):
        icon_path = os.path.join('web', 'icons', '32', m.group(1))
        if not os.path.exists(icon_path):
            issues.append(f'ICON_MISSING(icons/32/{m.group(1)})')

    return issues


def find_md_files(root_dir):
    md_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith('.')]
        for fn in filenames:
            if fn.endswith('.md'):
                rel = os.path.relpath(os.path.join(dirpath, fn), root_dir)
                md_files.append(rel)
    return sorted(md_files)


def main():
    if not os.path.isdir(RESEARCHES_DIR):
        print(f"Not found: {RESEARCHES_DIR}")
        sys.exit(1)

    files = find_md_files(RESEARCHES_DIR)
    problems = []
    ok_files = []

    for rel in files:
        issues = check_file(os.path.join(RESEARCHES_DIR, rel))
        if issues:
            problems.append((rel, issues))
        else:
            ok_files.append(rel)

    # Stats
    cat_counts = {}
    for _, issues in problems:
        for i in issues:
            cat = i.split('(')[0]
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

    print()
    print("=" * 70)
    print("  RESEARCH FILES CHECK (active, non-archive)")
    print("=" * 70)
    print(f"  Files: {len(files)}  |  OK: {len(ok_files)}  |  Issues: {len(problems)}")
    print()
    print("  CATEGORIES:")
    for cat, n in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {n}")
    print()
    print("  DETAIL:")
    for rel, issues in problems:
        print(f"    [ ] {rel}")
        for i in issues:
            print(f"        - {i}")
    print()
    if ok_files:
        print("  OK FILES:")
        for f in ok_files:
            print(f"    [V] {f}")
    print()
    print("=" * 70)
    print(f"  Total: {sum(len(i) for _, i in problems)}")
    print("=" * 70)


if __name__ == '__main__':
    main()