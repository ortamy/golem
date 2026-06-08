#!/usr/bin/env python3
# golem.py — единый скрипт для управления проектом (древовидное меню)

import os
import sys
import subprocess
import json
import traceback
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    try:
        import curses
    except ImportError:
        print("Ошибка: не установлен windows-curses")
        print("Установите: pip install windows-curses")
        sys.exit(1)
else:
    import curses

REPO_ROOT = Path(__file__).parent.parent
TOOLS_DIR = Path(__file__).parent
CACHE_DIR = TOOLS_DIR / "cache"
CONFIG_FILE = CACHE_DIR / "golem-config.json"
LOG_FILE = REPO_ROOT / "golem.log"
VERSION = "3.3"

current_lang = "ru"
LANGUAGES = {}
config = {}


def log_error(error_msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {error_msg}\n")
    except Exception:
        pass


def load_languages():
    global LANGUAGES
    LANGUAGES = {
        "ru": {
            "title": "ГОЛЕМ v{}",
            "actions": "ДЕЙСТВИЯ",
            "tools": "ИНСТРУМЕНТЫ",
            "exit": "ВЫХОД",
            "run_all_checks": "Запустить все проверки",
            "run_all_fixes": "Запустить все исправления",
            "full_audit": "Полный аудит (проверки + исправления)",
            "check_code_quality": "Проверить качество кода",
            "check_religionisms": "Проверить религионимы",
            "export_repo": "Экспорт репозитория",
            "backup_repo": "Создать бэкап",
            "update_versions": "Обновить версии",
            "checkers": "Чекеры",
            "check_file_naming": "Проверка имён файлов",
            "check_metadata": "Проверка метаданных",
            "check_links": "Проверка ссылок",
            "find_duplicates": "Поиск дубликатов",
            "find_orphans": "Поиск файлов-сирот",
            "check_consistency": "Проверка согласованности",
            "stats": "Статистика репозитория",
            "generate_glossary": "Генерация глоссария",
            "generate_navigation": "Генерация навигации",
            "sync_structure": "Синхронизация структуры",
            "generate_retrospective": "Ретроспектива",
            "generate_changelog": "Генерация CHANGELOG",
            "back": "Назад",
            "up_down": "Стрелки - выбор | Enter - вход | Esc - назад | q - выход",
            "goodbye": "До свидания!",
            "not_found": "не найден",
            "press_enter": "Нажмите Enter для продолжения...",
            "error_occurred": "Произошла ошибка",
            "check_log": "Проверьте golem.log",
            "skipped": "пропущен (нет файла)",
        },
        "en": {
            "title": "GOLEM v{}",
            "actions": "ACTIONS",
            "tools": "TOOLS",
            "exit": "EXIT",
            "run_all_checks": "Run all checks",
            "run_all_fixes": "Run all fixes",
            "full_audit": "Full audit (checks + fixes)",
            "check_code_quality": "Check code quality",
            "check_religionisms": "Check religionisms",
            "export_repo": "Export repository",
            "backup_repo": "Backup repository",
            "update_versions": "Update versions",
            "checkers": "Checkers",
            "check_file_naming": "Check file naming",
            "check_metadata": "Check metadata",
            "check_links": "Check links",
            "find_duplicates": "Find duplicates",
            "find_orphans": "Find orphans",
            "check_consistency": "Check consistency",
            "stats": "Repository statistics",
            "generate_glossary": "Generate glossary",
            "generate_navigation": "Generate navigation",
            "sync_structure": "Sync structure",
            "generate_retrospective": "Retrospective",
            "generate_changelog": "Generate CHANGELOG",
            "back": "Back",
            "up_down": "Arrows - select | Enter - enter | Esc - back | q - quit",
            "goodbye": "Goodbye!",
            "not_found": "not found",
            "press_enter": "Press Enter to continue...",
            "error_occurred": "An error occurred",
            "check_log": "Check golem.log",
            "skipped": "skipped (file missing)",
        },
        "he": {
            "title": "ГОЛЕМ v{}",
            "actions": "ПЕУЛОТ",
            "tools": "КЛИМ",
            "exit": "ЕЦИА",
            "run_all_checks": "hарэц эт коль hа-бдикот",
            "run_all_fixes": "hарэц эт коль hа-тикуним",
            "full_audit": "Бикорет малеа",
            "check_code_quality": "Бдикат эйхут коде",
            "check_religionisms": "Бдикат милим асурот",
            "export_repo": "Йеца маагар",
            "backup_repo": "Гибуй",
            "update_versions": "Адкен гирсаот",
            "checkers": "Бодким",
            "check_file_naming": "Бдикат шмот кебацим",
            "check_metadata": "Бдикат мета-нетуним",
            "check_links": "Бдикат кишурим",
            "find_duplicates": "Хипус кфилуёт",
            "find_orphans": "Хипус кебацим йетомим",
            "check_consistency": "Бдикат аквиют",
            "stats": "Статистика",
            "generate_glossary": "Йецират милон мунахим",
            "generate_navigation": "Йецират нивут",
            "sync_structure": "Синхрон мивне",
            "generate_retrospective": "Ретроспектива",
            "generate_changelog": "Йецират CHANGELOG",
            "back": "Хазор",
            "up_down": "Хицим - бхира | Enter - книса | Esc - хазор | q - ециа",
            "goodbye": "Леhитраот!",
            "not_found": "ло нимца",
            "press_enter": "Лахац Enter леhамшех...",
            "error_occurred": "Итра шагия",
            "check_log": "Бедок эт golem.log",
            "skipped": "дулаг (кебец хасер)",
        }
    }


def load_config():
    global config
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                return
    except Exception:
        pass
    config = {"language": "ru"}


def save_config():
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_error(f"Ошибка сохранения конфига: {e}")


def t(key):
    return LANGUAGES.get(current_lang, LANGUAGES["ru"]).get(key, key)


def run_script(stdscr, script_name, args=None):
    script_path = TOOLS_DIR / script_name
    if not script_path.exists():
        msg = f"[X] {script_name} — {t('skipped')}"
        try:
            stdscr.addstr(msg + "\n")
            stdscr.refresh()
            stdscr.getch()
        except Exception:
            print(msg)
        return

    try:
        curses.endwin()
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        subprocess.run(cmd, cwd=str(REPO_ROOT))
        input(f"\n{t('press_enter')}")
    except Exception as e:
        log_error(f"Ошибка запуска {script_name}: {e}")
        print(f"\n{t('error_occurred')}: {e}")
        input(f"\n{t('press_enter')}")
    finally:
        stdscr.clear()
        stdscr.refresh()


def run_bash_script(stdscr, script_name):
    script_path = TOOLS_DIR / script_name
    if not script_path.exists():
        msg = f"[X] {script_name} — {t('skipped')}"
        try:
            stdscr.addstr(msg + "\n")
            stdscr.refresh()
            stdscr.getch()
        except Exception:
            print(msg)
        return

    try:
        curses.endwin()
        subprocess.run(['bash', str(script_path)], cwd=str(TOOLS_DIR))
        input(f"\n{t('press_enter')}")
    except Exception as e:
        log_error(f"Ошибка запуска {script_name}: {e}")
        print(f"\n{t('error_occurred')}: {e}")
        input(f"\n{t('press_enter')}")
    finally:
        stdscr.clear()
        stdscr.refresh()


def draw_menu(stdscr, title_key, items, selected):
    height, width = stdscr.getmaxyx()
    stdscr.clear()

    title = f"{t('title').format(VERSION)} — {t(title_key)}"
    x_title = max(0, (width - len(title)) // 2)
    stdscr.addstr(0, x_title, title, curses.A_BOLD | curses.A_UNDERLINE)

    start_y = 3
    for i, item in enumerate(items):
        y = start_y + i
        if y >= height - 2:
            break
        attr = curses.A_REVERSE if i == selected else curses.A_NORMAL
        prefix = "> " if i == selected else "  "
        stdscr.addstr(y, 4, prefix + item, attr)

    hint = t('up_down')
    x_hint = max(0, (width - len(hint)) // 2)
    stdscr.addstr(height - 2, x_hint, hint, curses.A_DIM)
    stdscr.refresh()


def menu_loop(stdscr, title_key, items, actions):
    selected = 0
    n = len(items)

    while True:
        try:
            draw_menu(stdscr, title_key, items, selected)
            key = stdscr.getch()

            if key in (ord('q'), ord('й'), ord('ע')):
                return
            elif key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < n - 1:
                selected += 1
            elif key in (ord('\n'), ord('\r')):
                if selected == n - 1:
                    return
                action = actions[selected]
                if callable(action):
                    action()
                stdscr.clear()
                stdscr.refresh()
            elif key in (27, curses.KEY_LEFT):
                return
        except KeyboardInterrupt:
            return
        except Exception as e:
            log_error(f"Ошибка в меню '{title_key}': {e}")
            return


def menu_actions(stdscr):
    items = [
        t('run_all_checks'),
        t('run_all_fixes'),
        t('full_audit'),
        t('check_code_quality'),
        t('check_religionisms'),
        t('back'),
    ]
    actions = [
        lambda: run_all_checks(stdscr),
        lambda: run_all_fixes(stdscr),
        lambda: run_full_audit(stdscr),
        lambda: run_script(stdscr, 'check-code-quality.py'),
        lambda: run_script(stdscr, 'check-religionisms.py'),
        None,
    ]
    menu_loop(stdscr, 'actions', items, actions)


def menu_tools(stdscr):
    items = [
        t('checkers'),
        t('export_repo'),
        t('backup_repo'),
        t('update_versions'),
        t('generate_retrospective'),
        t('generate_changelog'),
        t('back'),
    ]
    actions = [
        lambda: menu_checkers(stdscr),
        lambda: run_bash_script(stdscr, 'export-repo.sh'),
        lambda: run_bash_script(stdscr, 'backup.sh'),
        lambda: run_script(stdscr, 'update-versions.py', ['--dry-run']),
        lambda: run_script(stdscr, 'generate-retrospective.py'),
        lambda: run_script(stdscr, 'generate-changelog.py', ['--dry-run']),
        None,
    ]
    menu_loop(stdscr, 'tools', items, actions)


def menu_checkers(stdscr):
    items = [
        t('check_file_naming'),
        t('check_metadata'),
        t('check_links'),
        t('find_duplicates'),
        t('find_orphans'),
        t('check_consistency'),
        t('stats'),
        t('generate_glossary'),
        t('generate_navigation'),
        t('sync_structure'),
        t('back'),
    ]
    actions = [
        lambda: run_script(stdscr, 'check-naming.py'),
        lambda: run_script(stdscr, 'validate-metadata.py'),
        lambda: run_script(stdscr, 'check-links.py'),
        lambda: run_script(stdscr, 'find-duplicates.py'),
        lambda: run_script(stdscr, 'find-orphans.py'),
        lambda: run_script(stdscr, 'consistency-checker.py'),
        lambda: run_script(stdscr, 'stats-report.py'),
        lambda: run_script(stdscr, 'generate-glossary.py'),
        lambda: run_script(stdscr, 'generate-nav.py'),
        lambda: run_script(stdscr, 'sync-structure.py'),
        None,
    ]
    menu_loop(stdscr, 'checkers', items, actions)


def run_all_checks(stdscr):
    scripts = [
        'check-naming.py', 'validate-metadata.py', 'check-links.py',
        'find-duplicates.py', 'find-orphans.py', 'consistency-checker.py',
        'check-religionisms.py', 'check-code-quality.py',
    ]
    for script_name in scripts:
        run_script(stdscr, script_name)


def run_all_fixes(stdscr):
    scripts = [
        ('validate-metadata.py', ['--fix']),
        ('check-religionisms.py', ['--fix']),
        ('check-code-quality.py', ['--fix']),
        ('sync-structure.py', []),
        ('generate-glossary.py', []),
        ('generate-nav.py', []),
    ]
    for script_name, args in scripts:
        run_script(stdscr, script_name, args)


def run_full_audit(stdscr):
    run_all_checks(stdscr)
    run_all_fixes(stdscr)
    run_script(stdscr, 'stats-report.py')


def main_menu(stdscr):
    items = [t('actions'), t('tools'), t('exit')]
    menus = [menu_actions, menu_tools, None]

    selected = 0
    n = len(items)

    while True:
        try:
            draw_menu(stdscr, 'title', items, selected)
            key = stdscr.getch()

            if key in (ord('q'), ord('й'), ord('ע')):
                break
            elif key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < n - 1:
                selected += 1
            elif key in (ord('\n'), ord('\r')):
                if selected == n - 1:
                    break
                menu_func = menus[selected]
                if callable(menu_func):
                    menu_func(stdscr)
            elif key in (27, curses.KEY_LEFT):
                if selected == n - 1:
                    break
        except KeyboardInterrupt:
            break
        except Exception as e:
            log_error(f"Ошибка в главном меню: {e}")
            break


def main():
    global current_lang

    load_languages()
    load_config()
    saved_lang = config.get("language", "ru")

    print("\nВыберите язык / Select language / вхар сафа:")
    print("  1. Русский")
    print("  2. English")
    print(f"  3. Иврит (по умолчанию: {saved_lang})")
    print("  Enter — использовать сохранённый")

    choice = input("> ").strip()
    lang_map = {"1": "ru", "2": "en", "3": "he"}
    current_lang = lang_map.get(choice, saved_lang)

    if choice in lang_map:
        config["language"] = current_lang
        save_config()

    try:
        curses.wrapper(main_menu)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log_error(f"Критическая ошибка: {e}\n{traceback.format_exc()}")
        print(f"\n\033[91m{t('error_occurred')}: {e}\033[0m")
        print(t('check_log'))
    finally:
        print(f"\n\033[92m{t('goodbye')}\033[0m\n")


if __name__ == "__main__":
    main()