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
VERSION = "3.6"

current_lang = "ru"
LANGUAGES = {}
config = {}

# =============================================================================
# СТРУКТУРА ПУТЕЙ
# =============================================================================
D = TOOLS_DIR
PATHS = {
    # Чекеры
    "check_naming":             D / "checkers" / "check-naming.py",
    "validate_metadata":        D / "checkers" / "validate-metadata.py",
    "check_links":              D / "checkers" / "check-links.py",
    "find_duplicates":          D / "checkers" / "find-duplicates.py",
    "find_orphans":             D / "checkers" / "find-orphans.py",
    "consistency":              D / "checkers" / "consistency-checker.py",
    "check_religionisms":       D / "checkers" / "check-religionisms.py",
    "check_code_quality":       D / "checkers" / "check-code-quality.py",
    "check_metadata_consistency": D / "checkers" / "check-metadata-consistency.py",
    "check_empty_files":        D / "checkers" / "check-empty-files.py",
    "check_tahor_sync":         D / "checkers" / "check-tahor-sync.py",
    "validate_external_links":  D / "checkers" / "validate-external-links.py",
    "clear_cache":              D / "checkers" / "clear-cache.py",

    # Генераторы
    "generate_glossary":        D / "generators" / "generate-glossary.py",
    "generate_nav":             D / "generators" / "generate-nav.py",
    "sync_structure":           D / "generators" / "sync-structure.py",
    "generate_retrospective":   D / "generators" / "generate-retrospective.py",
    "generate_changelog":       D / "generators" / "generate-changelog.py",
    "generate_index":           D / "generators" / "generate-index.py",

    # Отчёты
    "stats_report":             D / "reports" / "stats-report.py",
    "daily_report":             D / "reports" / "daily-report.py",
    "check_health":             D / "reports" / "check-health.py",
    "check_file_sizes":         D / "reports" / "check-file-sizes.py",

    # Автоматизация
    "add_metadata":             D / "automation" / "add-metadata.py",
    "auto_fix":                 D / "automation" / "auto-fix.py",
    "task_manager":             D / "automation" / "task-manager.py",
    "idea_manager":             D / "automation" / "idea-manager.py",
    "update_versions":          D / "automation" / "update-versions.py",

    # Бэкап
    "export_repo":              D / "backup" / "export-repo.sh",
    "backup_repo":              D / "backup" / "backup.sh",
}


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

            "checkers": "Чекеры",
            "generators": "Генераторы",
            "reports": "Отчёты",
            "automation": "Автоматизация",
            "backup": "Бэкап и экспорт",

            # Чекеры
            "check_file_naming": "Проверка имён файлов",
            "check_metadata": "Проверка метаданных",
            "check_links": "Проверка внутренних ссылок",
            "find_duplicates": "Поиск дубликатов",
            "find_orphans": "Поиск файлов-сирот",
            "check_consistency": "Проверка согласованности",
            "check_religionisms": "Проверить религионимы",
            "check_code_quality": "Проверить качество кода",
            "check_metadata_consistency": "Сверка путей в метаданных",
            "check_empty_files": "Поиск пустых/незаполненных",
            "check_tahor_sync": "Сверка tahor/ ↔ forbidden-words",
            "validate_external_links": "Проверка внешних ссылок",
            "clear_cache": "Очистить кэш",

            # Генераторы
            "generate_glossary": "Генерация глоссария",
            "generate_navigation": "Генерация навигации",
            "sync_structure": "Синхронизация структуры",
            "generate_retrospective": "Ретроспектива",
            "generate_changelog": "Генерация CHANGELOG",
            "generate_index": "Индексы папок",

            # Отчёты
            "stats": "Статистика репозитория",
            "daily_report": "Ежедневный отчёт",
            "check_health": "Здоровье проекта",
            "check_file_sizes": "Анализ размеров файлов",

            # Автоматизация
            "add_metadata": "Добавить метаданные",
            "auto_fix": "Автофикс задач",
            "task_manager": "Менеджер задач",
            "idea_manager": "Управление идеями",
            "update_versions": "Обновить версии",

            # Бэкап
            "export_repo": "Экспорт репозитория",
            "backup_repo": "Создать бэкап",

            # Общие
            "back": "← Назад",
            "running": "Выполняется: {}",
            "up_down": "↑↓ выбор | Enter вход | Esc/← назад | q выход",
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

            "checkers": "Checkers",
            "generators": "Generators",
            "reports": "Reports",
            "automation": "Automation",
            "backup": "Backup & Export",

            "check_file_naming": "Check file naming",
            "check_metadata": "Check metadata",
            "check_links": "Check internal links",
            "find_duplicates": "Find duplicates",
            "find_orphans": "Find orphans",
            "check_consistency": "Check consistency",
            "check_religionisms": "Check religionisms",
            "check_code_quality": "Check code quality",
            "check_metadata_consistency": "Check metadata paths",
            "check_empty_files": "Find empty/unfilled",
            "check_tahor_sync": "Sync tahor/ ↔ forbidden-words",
            "validate_external_links": "Validate external links",
            "clear_cache": "Clear cache",

            "generate_glossary": "Generate glossary",
            "generate_navigation": "Generate navigation",
            "sync_structure": "Sync structure",
            "generate_retrospective": "Retrospective",
            "generate_changelog": "Generate CHANGELOG",
            "generate_index": "Folder index",

            "stats": "Repository statistics",
            "daily_report": "Daily report",
            "check_health": "Project health",
            "check_file_sizes": "File size analysis",

            "add_metadata": "Add metadata",
            "auto_fix": "Auto fix tasks",
            "task_manager": "Task manager",
            "idea_manager": "Idea manager",
            "update_versions": "Update versions",

            "export_repo": "Export repository",
            "backup_repo": "Backup repository",

            "back": "← Back",
            "running": "Running: {}",
            "up_down": "↑↓ select | Enter enter | Esc/← back | q quit",
            "goodbye": "Goodbye!",
            "not_found": "not found",
            "press_enter": "Press Enter to continue...",
            "error_occurred": "An error occurred",
            "check_log": "Check golem.log",
            "skipped": "skipped (file missing)",
        },
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


def run_script(stdscr, script_path, args=None, description=None):
    if not script_path.exists():
        msg = f"[X] {script_path.name} — {t('skipped')}"
        _flash_message(stdscr, msg)
        return

    try:
        height, width = stdscr.getmaxyx()
        msg = t('running').format(description or script_path.stem)
        stdscr.addstr(height // 2, max(0, (width - len(msg)) // 2), msg, curses.A_BOLD)
        stdscr.refresh()
        curses.napms(400)

        curses.endwin()
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        subprocess.run(cmd, cwd=str(REPO_ROOT))
        input(f"\n{t('press_enter')}")
    except Exception as e:
        log_error(f"Ошибка запуска {script_path.name}: {e}")
        print(f"\n{t('error_occurred')}: {e}")
        input(f"\n{t('press_enter')}")
    finally:
        stdscr.clear()
        stdscr.refresh()


def run_bash_script(stdscr, script_path):
    if not script_path.exists():
        msg = f"[X] {script_path.name} — {t('skipped')}"
        _flash_message(stdscr, msg)
        return

    try:
        height, width = stdscr.getmaxyx()
        msg = t('running').format(script_path.stem)
        stdscr.addstr(height // 2, max(0, (width - len(msg)) // 2), msg, curses.A_BOLD)
        stdscr.refresh()
        curses.napms(400)

        curses.endwin()
        subprocess.run(['bash', str(script_path)], cwd=str(TOOLS_DIR))
        input(f"\n{t('press_enter')}")
    except Exception as e:
        log_error(f"Ошибка запуска {script_path.name}: {e}")
        print(f"\n{t('error_occurred')}: {e}")
        input(f"\n{t('press_enter')}")
    finally:
        stdscr.clear()
        stdscr.refresh()


def _flash_message(stdscr, msg):
    try:
        stdscr.addstr(msg + "\n")
        stdscr.refresh()
        stdscr.getch()
    except Exception:
        print(msg)


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

            if key in (ord('q'), ord('й')):
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


# =============================================================================
# МЕНЮ
# =============================================================================

def menu_actions(stdscr):
    items = [
        t('run_all_checks'),
        t('run_all_fixes'),
        t('full_audit'),
        t('back'),
    ]
    actions = [
        lambda: run_all_checks(stdscr),
        lambda: run_all_fixes(stdscr),
        lambda: run_full_audit(stdscr),
        None,
    ]
    menu_loop(stdscr, 'actions', items, actions)


def menu_tools(stdscr):
    items = [
        t('checkers'),
        t('generators'),
        t('reports'),
        t('automation'),
        t('backup'),
        t('back'),
    ]
    actions = [
        lambda: menu_checkers(stdscr),
        lambda: menu_generators(stdscr),
        lambda: menu_reports(stdscr),
        lambda: menu_automation(stdscr),
        lambda: menu_backup(stdscr),
        None,
    ]
    menu_loop(stdscr, 'tools', items, actions)


def menu_checkers(stdscr):
    items = [
        t('check_file_naming'),
        t('check_metadata'),
        t('check_metadata_consistency'),
        t('check_links'),
        t('validate_external_links'),
        t('find_duplicates'),
        t('find_orphans'),
        t('check_empty_files'),
        t('check_consistency'),
        t('check_religionisms'),
        t('check_tahor_sync'),
        t('check_code_quality'),
        t('clear_cache'),
        t('back'),
    ]
    actions = [
        lambda: run_script(stdscr, PATHS["check_naming"], description=t('check_file_naming')),
        lambda: run_script(stdscr, PATHS["validate_metadata"], description=t('check_metadata')),
        lambda: run_script(stdscr, PATHS["check_metadata_consistency"], description=t('check_metadata_consistency')),
        lambda: run_script(stdscr, PATHS["check_links"], description=t('check_links')),
        lambda: run_script(stdscr, PATHS["validate_external_links"], description=t('validate_external_links')),
        lambda: run_script(stdscr, PATHS["find_duplicates"], description=t('find_duplicates')),
        lambda: run_script(stdscr, PATHS["find_orphans"], description=t('find_orphans')),
        lambda: run_script(stdscr, PATHS["check_empty_files"], description=t('check_empty_files')),
        lambda: run_script(stdscr, PATHS["consistency"], description=t('check_consistency')),
        lambda: run_script(stdscr, PATHS["check_religionisms"], description=t('check_religionisms')),
        lambda: run_script(stdscr, PATHS["check_tahor_sync"], description=t('check_tahor_sync')),
        lambda: run_script(stdscr, PATHS["check_code_quality"], description=t('check_code_quality')),
        lambda: run_script(stdscr, PATHS["clear_cache"], description=t('clear_cache')),
        None,
    ]
    menu_loop(stdscr, 'checkers', items, actions)


def menu_generators(stdscr):
    items = [
        t('generate_glossary'),
        t('generate_navigation'),
        t('sync_structure'),
        t('generate_retrospective'),
        t('generate_changelog'),
        t('generate_index'),
        t('back'),
    ]
    actions = [
        lambda: run_script(stdscr, PATHS["generate_glossary"], description=t('generate_glossary')),
        lambda: run_script(stdscr, PATHS["generate_nav"], description=t('generate_navigation')),
        lambda: run_script(stdscr, PATHS["sync_structure"], description=t('sync_structure')),
        lambda: run_script(stdscr, PATHS["generate_retrospective"], description=t('generate_retrospective')),
        lambda: run_script(stdscr, PATHS["generate_changelog"], ['--dry-run'], description=t('generate_changelog')),
        lambda: run_script(stdscr, PATHS["generate_index"], description=t('generate_index')),
        None,
    ]
    menu_loop(stdscr, 'generators', items, actions)


def menu_reports(stdscr):
    items = [
        t('stats'),
        t('check_file_sizes'),
        t('daily_report'),
        t('check_health'),
        t('back'),
    ]
    actions = [
        lambda: run_script(stdscr, PATHS["stats_report"], description=t('stats')),
        lambda: run_script(stdscr, PATHS["check_file_sizes"], description=t('check_file_sizes')),
        lambda: run_script(stdscr, PATHS["daily_report"], description=t('daily_report')),
        lambda: run_script(stdscr, PATHS["check_health"], description=t('check_health')),
        None,
    ]
    menu_loop(stdscr, 'reports', items, actions)


def menu_automation(stdscr):
    items = [
        t('add_metadata'),
        t('auto_fix'),
        t('task_manager'),
        t('idea_manager'),
        t('update_versions'),
        t('back'),
    ]
    actions = [
        lambda: run_script(stdscr, PATHS["add_metadata"], description=t('add_metadata')),
        lambda: run_script(stdscr, PATHS["auto_fix"], description=t('auto_fix')),
        lambda: run_script(stdscr, PATHS["task_manager"], description=t('task_manager')),
        lambda: run_script(stdscr, PATHS["idea_manager"], description=t('idea_manager')),
        lambda: run_script(stdscr, PATHS["update_versions"], ['--dry-run'], description=t('update_versions')),
        None,
    ]
    menu_loop(stdscr, 'automation', items, actions)


def menu_backup(stdscr):
    items = [
        t('export_repo'),
        t('backup_repo'),
        t('back'),
    ]
    actions = [
        lambda: run_bash_script(stdscr, PATHS["export_repo"]),
        lambda: run_bash_script(stdscr, PATHS["backup_repo"]),
        None,
    ]
    menu_loop(stdscr, 'backup', items, actions)


# =============================================================================
# КОМБО-ДЕЙСТВИЯ
# =============================================================================

def run_all_checks(stdscr):
    scripts = [
        PATHS["check_naming"],
        PATHS["validate_metadata"],
        PATHS["check_metadata_consistency"],
        PATHS["check_links"],
        PATHS["find_duplicates"],
        PATHS["find_orphans"],
        PATHS["check_empty_files"],
        PATHS["consistency"],
        PATHS["check_religionisms"],
        PATHS["check_tahor_sync"],
        PATHS["check_code_quality"],
    ]
    for script in scripts:
        run_script(stdscr, script, description=script.stem)


def run_all_fixes(stdscr):
    scripts = [
        (PATHS["validate_metadata"], ['--fix']),
        (PATHS["check_metadata_consistency"], ['--fix']),
        (PATHS["check_religionisms"], ['--fix']),
        (PATHS["check_code_quality"], ['--fix']),
        (PATHS["sync_structure"], []),
        (PATHS["generate_glossary"], []),
        (PATHS["generate_nav"], []),
    ]
    for script, args in scripts:
        run_script(stdscr, script, args=args, description=script.stem)


def run_full_audit(stdscr):
    run_all_checks(stdscr)
    run_all_fixes(stdscr)
    run_script(stdscr, PATHS["stats_report"], description="stats")


# =============================================================================
# ГЛАВНОЕ МЕНЮ
# =============================================================================

def main_menu(stdscr):
    items = [t('actions'), t('tools'), t('exit')]
    menus = [menu_actions, menu_tools, None]

    selected = 0
    n = len(items)

    while True:
        try:
            draw_menu(stdscr, 'title', items, selected)
            key = stdscr.getch()

            if key in (ord('q'), ord('й')):
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

    print("\nВыберите язык / Select language:")
    print("  1. Русский")
    print("  2. English")
    print(f"  Enter — сохранённый ({saved_lang})")

    choice = input("> ").strip()
    lang_map = {"1": "ru", "2": "en"}
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