#!/usr/bin/env python3
# check-env.py — проверка окружения

import sys
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
NC = "\033[0m"
BOLD = "\033[1m"


def check_python():
    """Проверяет версию Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 6:
        print(f"{GREEN}✅ Python {version.major}.{version.minor}.{version.micro}{NC}")
        return True
    else:
        print(f"{RED}❌ Python {version.major}.{version.minor} (требуется 3.6+){NC}")
        return False


def check_git():
    """Проверяет наличие git"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"{GREEN}✅ {version}{NC}")
            return True
    except:
        pass
    print(f"{RED}❌ git не найден{NC}")
    return False


def check_bash():
    """Проверяет наличие bash"""
    try:
        result = subprocess.run(['bash', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0][:50]
            print(f"{GREEN}✅ {version}{NC}")
            return True
    except:
        pass
    print(f"{YELLOW}⚠️ bash не найден (может понадобиться для .sh скриптов){NC}")
    return False


def check_curses():
    """Проверяет наличие curses"""
    try:
        import curses
        print(f"{GREEN}✅ curses доступен{NC}")
        return True
    except ImportError:
        if sys.platform == 'win32':
            print(f"{YELLOW}⚠️ windows-curses не установлен (нужен для golem.py){NC}")
            print(f"   Установите: pip install windows-curses")
        else:
            print(f"{RED}❌ curses не найден{NC}")
        return False


def check_disk_space():
    """Проверяет свободное место на диске"""
    try:
        import shutil
        usage = shutil.disk_usage(REPO_ROOT)
        free_gb = usage.free / (1024**3)
        if free_gb > 1:
            print(f"{GREEN}✅ Свободно: {free_gb:.1f} GB{NC}")
            return True
        else:
            print(f"{RED}❌ Мало места: {free_gb:.1f} GB (нужно минимум 1 GB){NC}")
            return False
    except:
        print(f"{YELLOW}⚠️ Не удалось проверить место на диске{NC}")
        return True


def check_write_permissions():
    """Проверяет права на запись в ключевых папках"""
    folders = ['tools', 'neural/models', 'reports']
    all_ok = True
    for folder in folders:
        folder_path = REPO_ROOT / folder
        if folder_path.exists():
            if os.access(folder_path, os.W_OK):
                print(f"{GREEN}✅ Запись в {folder}{NC}")
            else:
                print(f"{RED}❌ Нет прав на запись в {folder}{NC}")
                all_ok = False
        else:
            print(f"{YELLOW}⚠️ Папка {folder} не существует{NC}")
    return all_ok


def check_dependencies():
    """Проверяет установку необходимых пакетов"""
    packages = ['requests', 'pyyaml']
    all_ok = True
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"{GREEN}✅ {package} установлен{NC}")
        except ImportError:
            print(f"{RED}❌ {package} не установлен (pip install {package}){NC}")
            all_ok = False
    return all_ok


def main():
    print(f"\n{BOLD}{BLUE}🔧 ПРОВЕРКА ОКРУЖЕНИЯ{NC}")
    print("=" * 50)
    print(f"Репозиторий: {REPO_ROOT}")
    print("")

    results = []

    print("Python:")
    results.append(check_python())

    print("\nGit:")
    results.append(check_git())

    print("\nBash:")
    results.append(check_bash())

    print("\nCurses:")
    results.append(check_curses())

    print("\nДиск:")
    results.append(check_disk_space())

    print("\nПрава на запись:")
    results.append(check_write_permissions())

    print("\nПакеты Python:")
    results.append(check_dependencies())

    print("\n" + "=" * 50)

    if all(results):
        print(f"{GREEN}✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ. ОКРУЖЕНИЕ ГОТОВО.{NC}")
        return 0
    else:
        print(f"{RED}❌ НЕ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ. ТРЕБУЕТСЯ ДОРАБОТКА.{NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

