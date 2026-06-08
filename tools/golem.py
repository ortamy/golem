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
CONFIG_FILE = REPO_ROOT / "golem-config.json"
LOG_FILE = REPO_ROOT / "golem.log"
VERSION = "3.1"

current_lang = "ru"
LANGUAGES = {}


def log_error(error_msg):
    """Логирует ошибку с временной меткой."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {error_msg}\n")
    except Exception:
        pass


def load_languages():
    """Загружает все переводы интерфейса."""
    global LANGUAGES
    LANGUAGES = {
        "ru": {
            "title": "ГОЛЕМ v{}",
            "actions": "ДЕЙСТВИЯ",
            "management": "УПРАВЛЕНИЕ",
            "tools": "ИНСТРУМЕНТЫ",
            "settings": "НАСТРОЙКИ",
            "exit": "ВЫХОД",
            "run_all_checks": "Запустить все проверки",
            "run_all_fixes": "Запустить все исправления",
            "generate_reports": "Сгенерировать отчёты",
            "full_audit": "Полный аудит (все проверки + исправления)",
            "task_manager": "Менеджер задач",
            "idea_manager": "Управление идеями",
            "auto_fix": "Автофикс задач",
            "project_status": "Статус проекта",
            "export_repo": "Экспорт репозитория",
            "backup_repo": "Создать бэкап",
            "update_versions": "Обновить версии",
            "checkers": "Чекеры",
            "check_file_naming": "check-naming.py — проверка имён файлов",
            "check_metadata": "validate-metadata.py — проверка метаданных",
            "check_links": "check-links.py — проверка ссылок",
            "find_duplicates": "find-duplicates.py — поиск дубликатов",
            "find_orphans": "find-orphans.py — поиск файлов-сирот",
            "check_consistency": "consistency-checker.py — проверка согласованности",
            "stats": "stats-report.py — статистика репозитория",
            "generate_glossary": "generate-glossary.py — генерация глоссария",
            "generate_navigation": "generate-nav.py — генерация навигации",
            "sync_structure": "sync-structure.py — синхронизация структуры",
            "generate_retrospective": "generate-retrospective.py — ретроспектива",
            "generate_changelog": "generate-changelog.py — генерация CHANGELOG",
            "check_env": "check-env.py — проверка окружения",
            "generate_index": "generate-index.py — индексы папок",
            "daily_report": "daily-report.py — ежедневный отчёт",
            "check_health": "check-health.py — здоровье проекта",
            "select_language": "Выберите язык",
            "language_ru": "Русский",
            "language_en": "English",
            "language_he": "עברית",
            "save": "Сохранить",
            "back": "Назад",
            "up_down": "↑↓ — выбор | Enter — вход | Esc/← — назад | q — выход",
            "goodbye": "До свидания!",
            "not_found": "не найден",
            "press_enter": "Нажмите Enter для продолжения...",
            "error_occurred": "Произошла ошибка",
            "check_log": "Проверьте golem.log",
            "language_changed": "Язык изменён. Перезапустите меню.",
            "skipped": "пропущен (нет файла)",
        },
        "en": {
            "title": "GOLEM v{}",
            "actions": "ACTIONS",
            "management": "MANAGEMENT",
            "tools": "TOOLS",
            "settings": "SETTINGS",
            "exit": "EXIT",
            "run_all_checks": "Run all checks",
            "run_all_fixes": "Run all fixes",
            "generate_reports": "Generate reports",
            "full_audit": "Full audit (all checks + fixes)",
            "task_manager": "Task manager",
            "idea_manager": "Idea manager",
            "auto_fix": "Auto fix tasks",
            "project_status": "Project status",
            "export_repo": "Export repository",
            "backup_repo": "Backup repository",
            "update_versions": "Update versions",
            "checkers": "Checkers",
            "check_file_naming": "check-naming.py — check file naming",
            "check_metadata": "validate-metadata.py — check metadata",
            "check_links": "check-links.py — check links",
            "find_duplicates": "find-duplicates.py — find duplicates",
            "find_orphans": "find-orphans.py — find orphans",
            "check_consistency": "consistency-checker.py — check consistency",
            "stats": "stats-report.py — repository statistics",
            "generate_glossary": "generate-glossary.py — generate glossary",
            "generate_navigation": "generate-nav.py — generate navigation",
            "sync_structure": "sync-structure.py — sync structure",
            "generate_retrospective": "generate-retrospective.py — retrospective",
            "generate_changelog": "generate-changelog.py — generate CHANGELOG",
            "check_env": "check-env.py — environment check",
            "generate_index": "generate-index.py — folder index",
            "daily_report": "daily-report.py — daily report",
            "check_health": "check-health.py — project health",
            "select_language": "Select language",
            "language_ru": "Russian",
            "language_en": "English",
            "language_he": "Hebrew",
            "save": "Save",
            "back": "Back",
            "up_down": "↑↓ — select | Enter — enter | Esc/← — back | q — quit",
            "goodbye": "Goodbye!",
            "not_found": "not found",
            "press_enter": "Press Enter to continue...",
            "error_occurred": "An error occurred",
            "check_log": "Check golem.log",
            "language_changed": "Language changed. Please restart menu.",
            "skipped": "skipped (file missing)",
        },
        "he": {
            "title": "ГОЛЕМ v{}",
            "actions": "פעולות",
            "management": "ניהול",
            "tools": "כלים",
            "settings": "הגדרות",
            "exit": "יציאה",
            "run_all_checks": "הרץ את כל הבדיקות",
            "run_all_fixes": "הרץ את כל התיקונים",
            "generate_reports": "צור דוחות",
            "full_audit": "ביקורת מלאה",
            "task_manager": "מנהל משימות",
            "idea_manager": "מנהל רעיונות",
            "auto_fix": "תיקון אוטומטי",
            "project_status": "סטטוס הפרויקט",
            "export_repo": "ייצא מאגר",
            "backup_repo": "גיבוי",
            "update_versions": "עדכן גרסאות",
            "checkers": "בודקים",
            "check_file_naming": "בדיקת שמות קבצים",
            "check_metadata": "בדיקת מטא-נתונים",
            "check_links": "בדיקת קישורים",
            "find_duplicates": "חיפוש כפילויות",
            "find_orphans": "חיפוש קבצים יתומים",
            "check_consistency": "בדיקת עקביות",
            "stats": "סטטיסטיקה",
            "generate_glossary": "יצירת מילון מונחים",
            "generate_navigation": "יצירת ניווט",
            "sync_structure": "סנכרון מבנה",
            "generate_retrospective": "רטרוספקטיבה",
            "generate_changelog": "יצירת CHANGELOG",
            "check_env": "בדיקת סביבה",
            "generate_index": "יצירת אינדקס",
            "daily_report": "דוח יומי",
            "check_health": "בדיקת תקינות",
            "select_language": "בחר שפה",
            "language_ru": "רוסית",
            "language_en": "אנגלית",
            "language_he": "עברית",
            "save": "שמור",
            "back": "חזור",
            "up_down": "חיצים לבחירה | Enter — כניסה | Esc/← — חזור | q — יציאה",
            "goodbye": "להתראות!",
            "not_found": "לא נמצא",
            "press_enter": "לחץ Enter להמשך...",
            "error_occurred": "אירעה שגיאה",
            "check_log": "בדוק את golem.log",
            "language_changed": "השפה שונתה. אנא הפעל מחדש את התפריט.",
            "skipped": "דולג (קובץ חסר)",
        }
    }


def load_config():
    """Загружает конфигурацию из JSON-файла."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        log_error(f"Ошибка загрузки конфига: {e}")
    return {"language": "ru"}


def save_config(config):
    """Сохраняет конфигурацию в JSON-файл."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log_error(f"Ошибка сохранения конфига: {e}")
        return False


def t(key):
    """Возвращает перевод ключа для текущего языка."""
    return LANGUAGES.get(current_lang, LANGUAGES["ru"]).get(key, key)


def run_script(stdscr, script_name, description, args=None):
    """Запускает Python-скрипт с выводом в терминал."""
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
        print(f"\n{description}")
        print("=" * 50)

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


def run_bash_script(stdscr, script_name, description):
    """Запускает Bash-скрипт с выводом в терминал."""
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
        print(f"\n{description}")
        print("=" * 50)
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
    """Отрисовывает меню. Возвращает максимальную Y-координату контента."""
    height, width = stdscr.getmaxyx()
    stdscr.clear()

    title = f"{t('title').format(VERSION)} — {t(title_key)}"
    x_title = max(0, (width - len(title)) // 2)
    stdscr.addstr(0, x_title, title, curses.A_BOLD | curses.A_UNDERLINE)

    start_y = 3
    max_y = start_y
    for i, item in enumerate(items):
        y = start_y + i
        if y >= height - 2:
            break
        attr = curses.A_REVERSE if i == selected else curses.A_NORMAL
        prefix = "> " if i == selected else "  "
        stdscr.addstr(y, 4, prefix + item, attr)
        max_y = y

    hint = t('up_down')
    x_hint = max(0, (width - len(hint)) // 2)
    stdscr.addstr(height - 2, x_hint, hint, curses.A_DIM)

    stdscr.refresh()
    return max_y


def menu_loop(stdscr, title_key, items, actions):
    """Универсальный цикл меню. Принимает список пунктов и список функций-действий."""
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
                if selected == n - 1:  # Последний пункт — «Назад»
                    return
                action = actions[selected]
                if callable(action):
                    action()
                stdscr.clear()
                stdscr.refresh()
            elif key in (27, curses.KEY_LEFT):  # Esc или стрелка влево
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
        t('generate_reports'),
        t('full_audit'),
        t('back'),
    ]
    actions = [
        lambda: run_all_checks(stdscr),
        lambda: run_all_fixes(stdscr),
        lambda: run_script(stdscr, 'stats-report.py', t('stats')),
        lambda: run_full_audit(stdscr),
        None,
    ]
    menu_loop(stdscr, 'actions', items, actions)


def menu_management(stdscr):
    items = [
        t('task_manager'),
        t('idea_manager'),
        t('auto_fix'),
        t('project_status'),
        t('back'),
    ]
    actions = [
        lambda: run_script(stdscr, 'task-manager.py', t('task_manager')),
        lambda: run_script(stdscr, 'idea-manager.py', t('idea_manager')),
        lambda: run_script(stdscr, 'auto-fix.py', t('auto_fix')),
        lambda: run_script(stdscr, 'stats-report.py', t('project_status'), ['--summary']),
        None,
    ]
    menu_loop(stdscr, 'management', items, actions)


def menu_tools(stdscr):
    items = [
        t('checkers'),
        t('export_repo'),
        t('backup_repo'),
        t('update_versions'),
        t('generate_retrospective'),
        t('generate_changelog'),
        t('check_env'),
        t('generate_index'),
        t('daily_report'),
        t('check_health'),
        t('back'),
    ]
    actions = [
        lambda: menu_checkers(stdscr),
        lambda: run_bash_script(stdscr, 'export-repo.sh', t('export_repo')),
        lambda: run_bash_script(stdscr, 'backup.sh', t('backup_repo')),
        lambda: run_script(stdscr, 'update-versions.py', t('update_versions'), ['--dry-run']),
        lambda: run_script(stdscr, 'generate-retrospective.py', t('generate_retrospective')),
        lambda: run_script(stdscr, 'generate-changelog.py', t('generate_changelog'), ['--dry-run']),
        lambda: run_script(stdscr, 'check-env.py', t('check_env')),
        lambda: run_script(stdscr, 'generate-index.py', t('generate_index')),
        lambda: run_script(stdscr, 'daily-report.py', t('daily_report')),
        lambda: run_script(stdscr, 'check-health.py', t('check_health')),
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
        lambda: run_script(stdscr, 'check-naming.py', t('check_file_naming')),
        lambda: run_script(stdscr, 'validate-metadata.py', t('check_metadata')),
        lambda: run_script(stdscr, 'check-links.py', t('check_links')),
        lambda: run_script(stdscr, 'find-duplicates.py', t('find_duplicates')),
        lambda: run_script(stdscr, 'find-orphans.py', t('find_orphans')),
        lambda: run_script(stdscr, 'consistency-checker.py', t('check_consistency')),
        lambda: run_script(stdscr, 'stats-report.py', t('stats')),
        lambda: run_script(stdscr, 'generate-glossary.py', t('generate_glossary')),
        lambda: run_script(stdscr, 'generate-nav.py', t('generate_navigation')),
        lambda: run_script(stdscr, 'sync-structure.py', t('sync_structure')),
        None,
    ]
    menu_loop(stdscr, 'checkers', items, actions)


def menu_settings(stdscr):
    global current_lang
    items = [
        t('language_ru'),
        t('language_en'),
        t('language_he'),
        t('save'),
        t('back'),
    ]
    temp_lang = current_lang
    selected = 0
    height, width = stdscr.getmaxyx()

    while True:
        try:
            stdscr.clear()
            title = f"{t('title').format(VERSION)} — {t('settings')}"
            x_title = max(0, (width - len(title)) // 2)
            stdscr.addstr(0, x_title, title, curses.A_BOLD | curses.A_UNDERLINE)

            start_y = 3
            for i, item in enumerate(items):
                y = start_y + i
                if y >= height - 2:
                    break

                # Отмечаем выбранный язык [X]
                display = item
                if i == 0 and temp_lang == "ru":
                    display = "[X] " + item
                elif i == 1 and temp_lang == "en":
                    display = "[X] " + item
                elif i == 2 and temp_lang == "he":
                    display = "[X] " + item

                attr = curses.A_REVERSE if i == selected else curses.A_NORMAL
                prefix = "> " if i == selected else "  "
                stdscr.addstr(y, 4, prefix + display, attr)

            hint = t('up_down')
            x_hint = max(0, (width - len(hint)) // 2)
            stdscr.addstr(height - 2, x_hint, hint, curses.A_DIM)
            stdscr.refresh()

            key = stdscr.getch()

            if key in (ord('q'), ord('й'), ord('ע')):
                return
            elif key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(items) - 1:
                selected += 1
            elif key in (ord('\n'), ord('\r')):
                if selected == 0:
                    temp_lang = "ru"
                elif selected == 1:
                    temp_lang = "en"
                elif selected == 2:
                    temp_lang = "he"
                elif selected == 3:  # Сохранить
                    if temp_lang != current_lang:
                        config["language"] = temp_lang
                        if save_config(config):
                            current_lang = temp_lang
                            try:
                                stdscr.clear()
                                msg = t('language_changed')
                                stdscr.addstr(height // 2, max(0, (width - len(msg)) // 2), msg)
                                stdscr.refresh()
                                stdscr.getch()
                            except Exception:
                                pass
                        return
                elif selected == 4:  # Назад
                    return
            elif key in (27, curses.KEY_LEFT):
                return
        except KeyboardInterrupt:
            return
        except Exception as e:
            log_error(f"Ошибка в menu_settings: {e}")
            return


def run_all_checks(stdscr):
    """Запускает все проверки подряд."""
    scripts = [
        ('check-naming.py', t('check_file_naming')),
        ('validate-metadata.py', t('check_metadata')),
        ('check-links.py', t('check_links')),
        ('find-duplicates.py', t('find_duplicates')),
        ('find-orphans.py', t('find_orphans')),
        ('consistency-checker.py', t('check_consistency')),
    ]
    for script_name, description in scripts:
        run_script(stdscr, script_name, description)


def run_all_fixes(stdscr):
    """Запускает все исправления подряд."""
    scripts = [
        ('validate-metadata.py', t('check_metadata'), ['--fix']),
        ('sync-structure.py', t('sync_structure')),
        ('generate-glossary.py', t('generate_glossary')),
        ('generate-nav.py', t('generate_navigation')),
    ]
    for script_name, description, *args in scripts:
        run_script(stdscr, script_name, description, args[0] if args else None)


def run_full_audit(stdscr):
    """Полный аудит: все проверки + все исправления."""
    run_all_checks(stdscr)
    run_all_fixes(stdscr)
    run_script(stdscr, 'stats-report.py', t('stats'))


def main_menu(stdscr):
    """Главное меню."""
    items = [
        t('actions'),
        t('management'),
        t('tools'),
        t('settings'),
        t('exit'),
    ]
    menus = [menu_actions, menu_management, menu_tools, menu_settings, None]

    selected = 0
    n = len(items)
    height, width = stdscr.getmaxyx()

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
                if selected == n - 1:  # Выход
                    break
                menu_func = menus[selected]
                if callable(menu_func):
                    menu_func(stdscr)
            elif key in (27, curses.KEY_LEFT):  # Esc или стрелка влево
                if selected == n - 1:
                    break
        except KeyboardInterrupt:
            break
        except Exception as e:
            log_error(f"Ошибка в главном меню: {e}")
            break


def main():
    """Точка входа."""
    global current_lang

    load_languages()

    config = load_config()
    current_lang = config.get("language", "ru")

    # Передаём config в menu_settings через замыкание — используем глобальную переменную
    # (уже работает через global current_lang)

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