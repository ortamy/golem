#!/usr/bin/env python3
# tools/checkers/check-env.py — проверка окружения для проекта «Голем»
import sys
import os
import subprocess
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

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
            print(f"{GREEN}✅ {result.stdout.strip()}{NC}")
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
    return True  # Не критично


def check_node():
    """Проверяет наличие Node.js"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{GREEN}✅ Node.js {result.stdout.strip()}{NC}")
            return True
    except:
        pass
    print(f"{YELLOW}⚠️ Node.js не найден (нужен для web/server.js){NC}")
    return True  # Не критично


def check_curses():
    """Проверяет наличие curses"""
    try:
        import curses
        print(f"{GREEN}✅ curses доступен{NC}")
        return True
    except ImportError:
        if sys.platform == 'win32':
            print(f"{YELLOW}⚠️ windows-curses не установлен (нужен для golem.py){NC}")
        else:
            print(f"{GREEN}✅ curses (системный){NC}")
        return True


def check_rich():
    """Проверяет наличие rich"""
    try:
        import rich
        print(f"{GREEN}✅ rich установлен{NC}")
        return True
    except ImportError:
        print(f"{YELLOW}⚠️ rich не установлен (pip install rich){NC}")
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
            print(f"{RED}❌ Мало места: {free_gb:.1f} GB{NC}")
            return False
    except:
        print(f"{YELLOW}⚠️ Не удалось проверить место на диске{NC}")
        return True


def check_write_permissions():
    """Проверяет права на запись в ключевых папках"""
    folders = ['tools', 'web', 'reports']
    all_ok = True
    for folder in folders:
        folder_path = REPO_ROOT / folder
        if folder_path.exists():
            if os.access(folder_path, os.W_OK):
                print(f"{GREEN}✅ Запись в {folder}/{NC}")
            else:
                print(f"{RED}❌ Нет прав на запись в {folder}/{NC}")
                all_ok = False
        else:
            print(f"{YELLOW}⚠️ Папка {folder}/ не существует{NC}")
    return all_ok


def check_web_files():
    """Проверяет наличие файлов веб-интерфейса"""
    web_dir = REPO_ROOT / "web"
    if not web_dir.exists():
        print(f"{YELLOW}⚠️ Папка web/ не найдена{NC}")
        return False
    required = ["index.html", "app.js", "style.css", "server.js"]
    all_ok = True
    for f in required:
        if (web_dir / f).exists():
            print(f"{GREEN}✅ web/{f}{NC}")
        else:
            print(f"{RED}❌ web/{f} отсутствует{NC}")
            all_ok = False
    return all_ok


def check_files_json():
    """Проверяет наличие files.json"""
    json_path = REPO_ROOT / "web" / "files.json"
    if json_path.exists():
        size_kb = json_path.stat().st_size / 1024
        print(f"{GREEN}✅ web/files.json ({size_kb:.0f} KB){NC}")
        return True
    else:
        print(f"{YELLOW}⚠️ web/files.json отсутствует{NC}")
        return False


def check_dependencies():
    """Проверяет установку необходимых пакетов"""
    packages = {
        'requests': 'pip install requests',
        'yaml': 'pip install pyyaml',
        'markdown_it': 'pip install markdown-it-py',
    }
    all_ok = True
    for package, install_cmd in packages.items():
        try:
            __import__(package)
            print(f"{GREEN}✅ {package} установлен{NC}")
        except ImportError:
            print(f"{YELLOW}⚠️ {package} не установлен ({install_cmd}){NC}")
            all_ok = False
    return all_ok


def main():
    json_mode = "--json" in sys.argv

    if not json_mode:
        print(f"\n{BOLD}{BLUE}🔧 ПРОВЕРКА ОКРУЖЕНИЯ — GOLEM{NC}")
        print("=" * 50)
        print(f"Репозиторий: {REPO_ROOT}")
        print("")

    checks = {
        "python": ("Python", check_python),
        "git": ("Git", check_git),
        "bash": ("Bash", check_bash),
        "node": ("Node.js", check_node),
        "curses": ("Curses", check_curses),
        "rich": ("Rich", check_rich),
        "disk": ("Диск", check_disk_space),
        "permissions": ("Права записи", check_write_permissions),
        "web_files": ("Веб-файлы", check_web_files),
        "files_json": ("files.json", check_files_json),
        "packages": ("Пакеты Python", check_dependencies),
    }

    results = {}

    for key, (label, func) in checks.items():
        if not json_mode:
            print(f"{label}:")
        results[key] = func()
        if not json_mode:
            print("")

    if json_mode:
        print(json.dumps(results, ensure_ascii=False))
        return 0 if all(results.values()) else 1

    print("=" * 50)

    if all(results.values()):
        print(f"{GREEN}✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ. ОКРУЖЕНИЕ ГОТОВО.{NC}")
        return 0
    else:
        failed = [label for key, (label, _) in checks.items() if not results[key]]
        print(f"{RED}❌ ПРОВАЛЕНО ПРОВЕРОК: {len(failed)}{NC}")

        print(f"\n{YELLOW}📋 ЧТО НУЖНО СДЕЛАТЬ:{NC}")
        if not results["python"]:
            print("   • Установить Python 3.6+ с python.org")
        if not results["git"]:
            print("   • Установить git с git-scm.com")
        if not results["node"]:
            print("   • Установить Node.js с nodejs.org")
        if not results["rich"]:
            print("   • pip install rich")
        if not results["packages"]:
            print("   • pip install -r requirements.txt")
        if not results["curses"] and sys.platform == 'win32':
            print("   • pip install windows-curses")
        if not results["files_json"]:
            print("   • python tools/generators/generate-files-json.py")
        if not results["web_files"]:
            print("   • Проверить наличие файлов в web/")
        if not results["permissions"]:
            print("   • Проверить права доступа к папкам")
        if not results["disk"]:
            print("   • Освободить место на диске")

        return 1


if __name__ == "__main__":
    sys.exit(main())