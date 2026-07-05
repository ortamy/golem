#!/usr/bin/env python3
"""
tools/generate-all.py — Единый генератор сайта Golem.

Запускает полную перегенерацию:
  1. Конвертация .md → .html (generate_site.py)
  2. Генерация files.json (generate-files-json.py)
  3. Опционально: сборка CSS/JS (npm run build)

Использование:
  python tools/generate-all.py              # полная генерация
  python tools/generate-all.py --no-npm     # без npm сборки
  python tools/generate-all.py --check      # только проверка (dry run)
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Принудительно устанавливаем UTF-8 для stdout (Windows cp1251 fix)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = {
    "html": REPO_ROOT / "tools" / "generate_site.py",
    "files_json": REPO_ROOT / "tools" / "generators" / "generate-files-json.py",
}
NPM_DIR = REPO_ROOT / "products" / "website" / "build"


def safe_print(text: str):
    """Печать с защитой от UnicodeEncodeError в Windows консоли."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Заменяем не ASCII символы на безопасные
        cleaned = text.encode("ascii", errors="replace").decode("ascii")
        print(cleaned)


def print_header(text: str):
    safe_print("")
    safe_print("=" * 60)
    safe_print(f"  {text}")
    safe_print("=" * 60)


def print_step(step: int, total: int, text: str):
    safe_print(f"\n  [{step}/{total}] {text}...")


def run_script(script_path: Path, label: str) -> bool:
    """Запускает Python-скрипт и возвращает True при успехе."""
    if not script_path.exists():
        print(f"  ⚠️  Скрипт не найден: {script_path}")
        return False

    print(f"  → {script_path.name}")
    start = time.time()
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
    )
    elapsed = time.time() - start

    if result.returncode == 0:
        # Выводим последние строки вывода (статистику)
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                print(f"     {line.strip()}")
        print(f"     ✓ Завершено за {elapsed:.1f}с")
        return True
    else:
        print(f"     ✗ Ошибка (код {result.returncode})")
        if result.stderr.strip():
            for line in result.stderr.strip().split("\n")[-5:]:
                print(f"     {line.strip()}")
        return False


def run_npm_build() -> bool:
    """Запускает npm run build в products/website/build/."""
    if not (NPM_DIR / "package.json").exists():
        print(f"  ⚠️  package.json не найден в {NPM_DIR}")
        return False

    print(f"  → npm run build (в {NPM_DIR.relative_to(REPO_ROOT)})")
    start = time.time()
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=NPM_DIR,
        capture_output=True,
        text=True,
    )
    elapsed = time.time() - start

    if result.returncode == 0:
        for line in result.stdout.strip().split("\n")[-3:]:
            if line.strip():
                print(f"     {line.strip()}")
        print(f"     ✓ Завершено за {elapsed:.1f}с")
        return True
    else:
        print(f"     ✗ Ошибка (код {result.returncode})")
        if result.stderr.strip():
            for line in result.stderr.strip().split("\n")[-5:]:
                print(f"     {line.strip()}")
        return False


def count_files(directory: Path, pattern: str) -> int:
    """Считает файлы по glob-паттерну."""
    return len(list(directory.rglob(pattern)))


def report():
    """Выводит итоговый отчёт о состоянии сайта."""
    content_dir = REPO_ROOT / "products" / "website" / "content"
    files_json = REPO_ROOT / "products" / "website" / "files.json"

    print_header("📊 ИТОГОВЫЙ ОТЧЁТ")

    html_count = count_files(content_dir, "*.html")
    md_count = count_files(REPO_ROOT / "content", "*.md")

    print(f"  📄 HTML-страниц:        {html_count}")
    print(f"  📝 Markdown-файлов:     {md_count}")

    if files_json.exists():
        import json
        try:
            with open(files_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"  📋 files.json записей:  {len(data)}")
            # Категории
            cats = {}
            for entry in data:
                cat = entry.get("category", "Без категории")
                cats[cat] = cats.get(cat, 0) + 1
            print(f"  🏷️  Категорий:           {len(cats)}")
            for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
                print(f"     {cat}: {count}")
        except Exception as e:
            print(f"  ⚠️  Ошибка чтения files.json: {e}")
    else:
        print(f"  ⚠️  files.json отсутствует")

    print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Единый генератор сайта Golem"
    )
    parser.add_argument(
        "--no-npm",
        action="store_true",
        help="Пропустить npm сборку CSS/JS",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Только проверка (dry run) — показать, что будет сделано",
    )
    args = parser.parse_args()

    print_header("🛠  GOLEM — ПОЛНАЯ ПЕРЕГЕНЕРАЦИЯ САЙТА")
    print(f"  Корень проекта: {REPO_ROOT}")
    print(f"  Python:         {sys.executable}")
    print(f"  Режим:          {'проверка (dry run)' if args.check else 'полная генерация'}")

    steps = 3 if args.no_npm else 4
    ok = True

    # Шаг 1: HTML
    print_step(1, steps, "Генерация HTML из Markdown")
    if args.check:
        md_count = count_files(REPO_ROOT / "content", "*.md")
        print(f"     Будет обработано: ~{md_count} .md файлов")
    else:
        if not run_script(SCRIPTS["html"], "HTML"):
            ok = False

    # Шаг 2: files.json
    print_step(2, steps, "Генерация files.json")
    if args.check:
        print(f"     Будет создан: {SCRIPTS['files_json'].relative_to(REPO_ROOT)}")
    else:
        if not run_script(SCRIPTS["files_json"], "files.json"):
            ok = False

    # Шаг 3: npm build (опционально)
    if not args.no_npm:
        print_step(3, steps, "Сборка CSS/JS (npm run build)")
        if args.check:
            print(f"     Будет выполнено в: {NPM_DIR.relative_to(REPO_ROOT)}")
        else:
            if not run_npm_build():
                ok = False
        report_step = 4
    else:
        report_step = 3

    # Шаг 4: Отчёт
    print_step(report_step, steps, "Формирование отчёта")
    if not args.check:
        report()

    # Итог
    print_header("✅ ГОТОВО" if ok else "❌ ОШИБКИ")
    if ok:
        print("  Все шаги выполнены успешно.")
        print(f"  Откройте сайт: products/website/index.html")
    else:
        print("  Некоторые шаги завершились с ошибками.")
        print("  Проверьте вывод выше для деталей.")
        sys.exit(1)


if __name__ == "__main__":
    main()