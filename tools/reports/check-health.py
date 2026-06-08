#!/usr/bin/env python3
# check-health.py — проверка здоровья проекта

import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TOOLS_DIR = REPO_ROOT / "tools"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
NC = "\033[0m"
BOLD = "\033[1m"


def show_progress(current, total, label=""):
    percent = int(current / total * 100)
    bar_len = 40
    filled = int(bar_len * current / total)
    bar = '█' * filled + '░' * (bar_len - filled)
    sys.stdout.write(f'\r[{bar}] {percent}% ({current}/{total}) {label}')
    sys.stdout.flush()


def finish_progress():
    sys.stdout.write('\n')
    sys.stdout.flush()


def run_checker(script_name):
    """Запускает чекер и возвращает результат"""
    script_path = TOOLS_DIR / script_name
    if not script_path.exists():
        return "skip", f"скрипт не найден"

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=TOOLS_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return "ok", ""
        else:
            # Показываем только первую строку ошибки
            error_lines = result.stderr.strip().split('\n')
            first_error = error_lines[0][:80] if error_lines else "ошибка"
            return "fail", first_error
    except subprocess.TimeoutExpired:
        return "fail", "таймаут"
    except Exception as e:
        return "fail", str(e)[:80]


def main():
    print(f"\n{BOLD}{BLUE}🏥 ПРОВЕРКА ЗДОРОВЬЯ ПРОЕКТА{NC}")
    print("=" * 50)

    checkers = [
        ('check-naming.py', 'Проверка имён'),
        ('validate-metadata.py', 'Проверка метаданных'),
        ('check-links.py', 'Проверка ссылок'),
        ('find-duplicates.py', 'Поиск дубликатов'),
        ('find-orphans.py', 'Поиск сирот'),
        ('consistency-checker.py', 'Проверка согласованности'),
    ]

    results = {}

    print("Запуск проверок...\n")
    for i, (checker, name) in enumerate(checkers, 1):
        show_progress(i, len(checkers), name)
        status, error = run_checker(checker)
        results[checker] = (status, error, name)

    finish_progress()
    print("\n\n" + "=" * 50)
    print("\n📊 РЕЗУЛЬТАТЫ ПРОВЕРОК:\n")

    all_ok = True
    for checker, (status, error, name) in results.items():
        if status == "ok":
            print(f"   {GREEN}✅{NC} {name}")
        elif status == "skip":
            print(f"   {YELLOW}⚠️{NC} {name} - {error}")
            all_ok = False
        else:
            print(f"   {RED}❌{NC} {name} - {error}")
            all_ok = False

    print("\n" + "=" * 50)

    if all_ok:
        print(f"\n{GREEN}✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ. ПРОЕКТ ЗДОРОВ.{NC}")
        return 0
    else:
        print(f"\n{RED}❌ НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ. ТРЕБУЕТСЯ ВНИМАНИЕ.{NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

