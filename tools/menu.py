#!/usr/bin/env python3
# menu.py — единое CLI-меню для всех инструментов

import os
import sys
import subprocess
from pathlib import Path

TOOLS_DIR = Path(__file__).parent
REPO_ROOT = TOOLS_DIR.parent

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🛠️  ГОЛЕМ — ИНСТРУМЕНТЫ                  ║
║                      Единое CLI-меню                        ║
╚══════════════════════════════════════════════════════════════╝
""")

def print_menu():
    print("📋 ПРОВЕРКИ")
    print("  1. check-naming.py      — проверка именования файлов")
    print("  2. validate-metadata.py — проверка метаданных")
    print("  3. check-links.py       — проверка битых ссылок")
    print("  4. find-duplicates.py   — поиск дубликатов")
    print("  5. find-orphans.py      — поиск файлов-сирот")
    print("")
    print("🔧 ОБНОВЛЕНИЕ И СОЗДАНИЕ")
    print("  6. add-metadata.py      — добавление метаданных")
    print("  7. update-versions.py   — обновление версий")
    print("  8. sync-structure.py    — синхронизация structure.md")
    print("  9. generate-glossary.py — генерация глоссария")
    print(" 10. generate-nav.py      — генерация навигации")
    print(" 11. stats-report.py      — статистика репозитория")
    print("")
    print("💾 БЭКАП И ЭКСПОРТ")
    print(" 12. export-repo.sh       — экспорт всех md в один файл")
    print(" 13. backup.sh            — создать бэкап")
    print("")
    print("⚡ МАССОВЫЕ ОПЕРАЦИИ")
    print(" 14. Все проверки         — запустить 1-5")
    print(" 15. Всё обновление       — запустить 6-11")
    print(" 16. Полный аудит         — запустить 1-5, 12-13")
    print("")
    print(" 0. Выход")
    print("")

def run_script(script_name, *args):
    """Запускает python или bash скрипт"""
    script_path = TOOLS_DIR / script_name
    
    if not script_path.exists():
        print(f"❌ Скрипт не найден: {script_name}")
        return
    
    cmd = []
    if script_name.endswith('.py'):
        cmd = [sys.executable, str(script_path)] + list(args)
    elif script_name.endswith('.sh'):
        cmd = ['bash', str(script_path)] + list(args)
    
    print(f"\n▶️  Запуск: {script_name}\n")
    subprocess.run(cmd)
    print("\n✅ Завершено. Нажмите Enter для продолжения...")
    input()

def run_checks():
    """Запускает все проверки (1-5)"""
    run_script('check-naming.py')
    run_script('validate-metadata.py')
    run_script('check-links.py')
    run_script('find-duplicates.py')
    run_script('find-orphans.py')

def run_updates():
    """Запускает все обновления (6-11)"""
    print("⚠️  Внимание: add-metadata.py и update-versions.py изменяют файлы")
    confirm = input("Продолжить? (y/N): ")
    if confirm.lower() != 'y':
        print("Отменено")
        return
    
    run_script('add-metadata.py')
    run_script('update-versions.py', '--type', 'minor')
    run_script('sync-structure.py')
    run_script('generate-glossary.py')
    run_script('generate-nav.py')
    run_script('stats-report.py')

def run_full_audit():
    """Полный аудит: проверки + бэкап + экспорт"""
    run_checks()
    run_script('export-repo.sh')
    run_script('backup.sh')

def main():
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("👉 Выберите действие: ").strip()
        
        if choice == '0':
            print("До свидания!")
            break
        elif choice == '1':
            run_script('check-naming.py')
        elif choice == '2':
            run_script('validate-metadata.py')
        elif choice == '3':
            run_script('check-links.py')
        elif choice == '4':
            run_script('find-duplicates.py')
        elif choice == '5':
            run_script('find-orphans.py')
        elif choice == '6':
            run_script('add-metadata.py')
        elif choice == '7':
            print("1. Minor (1.0 → 1.1)")
            print("2. Major (1.0 → 2.0)")
            print("3. Только показать (--dry-run)")
            sub = input("Выберите тип: ")
            if sub == '1':
                run_script('update-versions.py', '--type', 'minor')
            elif sub == '2':
                run_script('update-versions.py', '--type', 'major')
            elif sub == '3':
                run_script('update-versions.py', '--dry-run')
            else:
                print("Неверный выбор")
        elif choice == '8':
            run_script('sync-structure.py')
        elif choice == '9':
            run_script('generate-glossary.py')
        elif choice == '10':
            run_script('generate-nav.py')
        elif choice == '11':
            run_script('stats-report.py')
        elif choice == '12':
            run_script('export-repo.sh')
        elif choice == '13':
            run_script('backup.sh')
        elif choice == '14':
            run_checks()
        elif choice == '15':
            run_updates()
        elif choice == '16':
            run_full_audit()
        else:
            print("❌ Неверный выбор")
            input("Нажмите Enter...")

if __name__ == "__main__":
    main()
