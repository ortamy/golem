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

REPO_ROOT = Path(__file__).parent
TOOLS_DIR = REPO_ROOT
CONFIG_FILE = REPO_ROOT / "golem-config.json"
LOG_FILE = REPO_ROOT / "golem.log"
VERSION = "3.0"

# Глобальные переменные
current_lang = "ru"
LANGUAGES = None


def log_error(error_msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {error_msg}\n")


def load_languages():
    global LANGUAGES
    LANGUAGES = {
        "ru": {
            "title": "GOLEM v{}",
            "actions": "ДЕЙСТВИЯ",
            "management": "УПРАВЛЕНИЕ",
            "tools": "ИНСТРУМЕНТЫ",
            "settings": "НАСТРОЙКИ",
            "exit": "ВЫХОД",
            "run_all_checks": "Запустить все проверки",
            "run_all_fixes": "Запустить все исправления",
            "generate_reports": "Сгенерировать отчёты",
            "full_audit": "Полный аудит",
            "task_manager": "Менеджер задач",
            "idea_manager": "Управление идеями",
            "auto_fix": "Автофикс задач",
            "project_status": "Статус проекта",
            "export_repo": "Экспорт репозитория",
            "backup_repo": "Создать бэкап",
            "update_versions": "Обновить версии",
            "checkers": "Чекеры",
            "check_file_naming": "check-naming.py - проверка имён",
            "check_metadata": "validate-metadata.py - проверка метаданных",
            "check_links": "check-links.py - проверка ссылок",
            "find_duplicates": "find-duplicates.py - поиск дубликатов",
            "find_orphans": "find-orphans.py - поиск сирот",
            "check_consistency": "consistency-checker.py - проверка согласованности",
            "stats": "stats-report.py - статистика",
            "generate_glossary": "generate-glossary.py - генерация глоссария",
            "generate_navigation": "generate-nav.py - генерация навигации",
            "sync_structure": "sync-structure.py - синхронизация структуры",
            "generate_retrospective": "generate-retrospective.py - ретроспектива",
            "check_env": "check-env.py - проверка окружения",
            "generate_index": "generate-index.py - индексы папок",
            "daily_report": "daily-report.py - ежедневный отчёт",
            "check_health": "check-health.py - здоровье проекта",
            "select_language": "Выберите язык",
            "language_ru": "Русский",
            "language_en": "English",
            "language_he": "עברית",
            "save": "Сохранить",
            "back": "Назад",
            "up_down": "Стрелки для выбора | Enter - вход | Esc/← - назад | q - выход",
            "goodbye": "До свидания!",
            "not_found": "не найден",
            "press_enter": "Нажмите Enter для продолжения...",
            "error_occurred": "Произошла ошибка",
            "check_log": "Проверьте golem.log",
            "language_changed": "Язык изменён. Перезапустите меню.",
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
            "full_audit": "Full audit",
            "task_manager": "Task manager",
            "idea_manager": "Idea manager",
            "auto_fix": "Auto fix tasks",
            "project_status": "Project status",
            "export_repo": "Export repository",
            "backup_repo": "Backup repository",
            "update_versions": "Update versions",
            "checkers": "Checkers",
            "check_file_naming": "check-naming.py - check naming",
            "check_metadata": "validate-metadata.py - check metadata",
            "check_links": "check-links.py - check links",
            "find_duplicates": "find-duplicates.py - find duplicates",
            "find_orphans": "find-orphans.py - find orphans",
            "check_consistency": "consistency-checker.py - check consistency",
            "stats": "stats-report.py - statistics",
            "generate_glossary": "generate-glossary.py - generate glossary",
            "generate_navigation": "generate-nav.py - generate navigation",
            "sync_structure": "sync-structure.py - sync structure",
            "generate_retrospective": "generate-retrospective.py - retrospective",
            "check_env": "check-env.py - environment check",
            "generate_index": "generate-index.py - folder index",
            "daily_report": "daily-report.py - daily report",
            "check_health": "check-health.py - project health",
            "select_language": "Select language",
            "language_ru": "Russian",
            "language_en": "English",
            "language_he": "Hebrew",
            "save": "Save",
            "back": "Back",
            "up_down": "Arrows to select | Enter - enter | Esc/← - back | q - quit",
            "goodbye": "Goodbye!",
            "not_found": "not found",
            "press_enter": "Press Enter to continue...",
            "error_occurred": "An error occurred",
            "check_log": "Check golem.log",
            "language_changed": "Language changed. Please restart menu.",
        },
        "he": {
            "title": "GOLEM v{}",
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
            "up_down": "חיצים לבחירה | Enter - כניסה | Esc/← - חזור | q - יציאה",
            "goodbye": "להתראות!",
            "not_found": "לא נמצא",
            "press_enter": "לחץ Enter להמשך...",
            "error_occurred": "אירעה שגיאה",
            "check_log": "בדוק את golem.log",
            "language_changed": "השפה שונתה. אנא הפעל מחדש את התפריט.",
        }
    }


def load_config():
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        log_error(f"Ошибка загрузки конфига: {e}")
    return {"language": "ru"}


def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log_error(f"Ошибка сохранения конфига: {e}")
        return False


def get_text(key):
    global LANGUAGES, current_lang
    return LANGUAGES[current_lang].get(key, key)


def run_script_and_show(stdscr, script_name, description, args=None):
    script_path = TOOLS_DIR / script_name
    if not script_path.exists():
        try:
            stdscr.addstr(f"[X] {script_name} {get_text('not_found')}\n")
            stdscr.refresh()
            stdscr.getch()
        except:
            print(f"[X] {script_name} {get_text('not_found')}")
        return

    try:
        curses.endwin()
        print(f"\n{description}")
        print("=" * 50)
        
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        subprocess.run(cmd, cwd=TOOLS_DIR)
        
        input(f"\n{get_text('press_enter')}")
    except Exception as e:
        log_error(f"Ошибка запуска {script_name}: {e}")
        print(f"\n{get_text('error_occurred')}: {e}")
        input(f"\n{get_text('press_enter')}")
    finally:
        stdscr.clear()
        stdscr.refresh()


def run_with_error_handling(stdscr, func, *args):
    try:
        return func(*args)
    except Exception as e:
        log_error(f"Ошибка в меню: {e}\n{traceback.format_exc()}")
        try:
            stdscr.clear()
            stdscr.addstr(0, 0, f"{get_text('error_occurred')}: {str(e)[:50]}")
            stdscr.addstr(2, 0, get_text('check_log'))
            stdscr.refresh()
            stdscr.getch()
        except:
            print(f"{get_text('error_occurred')}: {e}")
        return


def menu_actions(stdscr):
    items = [
        get_text('run_all_checks'),
        get_text('run_all_fixes'),
        get_text('generate_reports'),
        get_text('full_audit'),
        get_text('back'),
    ]
    actions = [
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'check-naming.py', get_text('check_file_naming')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'validate-metadata.py', get_text('check_metadata'), ['--fix']),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'stats-report.py', get_text('stats')),
        lambda: run_with_error_handling(stdscr, run_everything, stdscr),
        lambda: None,
    ]
    
    selected = 0
    height, width = stdscr.getmaxyx()
    curses.curs_set(0)
    
    while True:
        try:
            stdscr.clear()
            title = f"{get_text('title').format(VERSION)} - {get_text('actions')}"
            stdscr.addstr(0, max(0, (width - len(title)) // 2), title, curses.A_BOLD | curses.A_UNDERLINE)
            
            start_y = 3
            for i, item in enumerate(items):
                y = start_y + i
                if y >= height - 2:
                    break
                if i == selected:
                    stdscr.addstr(y, 4, "> " + item, curses.A_REVERSE)
                else:
                    stdscr.addstr(y, 4, "  " + item, curses.A_NORMAL)
            
            hint = get_text('up_down')
            stdscr.addstr(height - 2, max(0, (width - len(hint)) // 2), hint, curses.A_DIM)
            stdscr.refresh()
            
            key = stdscr.getch()
            
            if key in [ord('q'), ord('й'), ord('ע')]:
                return
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(items) - 1:
                selected += 1
            elif key in [ord('\n'), ord('\r')]:
                if selected == len(items) - 1:
                    return
                actions[selected]()
                stdscr.clear()
                stdscr.refresh()
            elif key == 27 or key == curses.KEY_LEFT:
                return
        except KeyboardInterrupt:
            return
        except Exception as e:
            log_error(f"Ошибка в menu_actions: {e}")
            return


def menu_management(stdscr):
    items = [
        get_text('task_manager'),
        get_text('idea_manager'),
        get_text('auto_fix'),
        get_text('project_status'),
        get_text('back'),
    ]
    actions = [
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'task-manager.py', get_text('task_manager')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'idea-manager.py', get_text('idea_manager')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'auto-fix.py', get_text('auto_fix')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'stats-report.py', get_text('project_status'), ['--summary']),
        lambda: None,
    ]
    
    selected = 0
    height, width = stdscr.getmaxyx()
    curses.curs_set(0)
    
    while True:
        try:
            stdscr.clear()
            title = f"{get_text('title').format(VERSION)} - {get_text('management')}"
            stdscr.addstr(0, max(0, (width - len(title)) // 2), title, curses.A_BOLD | curses.A_UNDERLINE)
            
            start_y = 3
            for i, item in enumerate(items):
                y = start_y + i
                if y >= height - 2:
                    break
                if i == selected:
                    stdscr.addstr(y, 4, "> " + item, curses.A_REVERSE)
                else:
                    stdscr.addstr(y, 4, "  " + item, curses.A_NORMAL)
            
            hint = get_text('up_down')
            stdscr.addstr(height - 2, max(0, (width - len(hint)) // 2), hint, curses.A_DIM)
            stdscr.refresh()
            
            key = stdscr.getch()
            
            if key in [ord('q'), ord('й'), ord('ע')]:
                return
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(items) - 1:
                selected += 1
            elif key in [ord('\n'), ord('\r')]:
                if selected == len(items) - 1:
                    return
                actions[selected]()
                stdscr.clear()
                stdscr.refresh()
            elif key == 27 or key == curses.KEY_LEFT:
                return
        except KeyboardInterrupt:
            return
        except Exception as e:
            log_error(f"Ошибка в menu_management: {e}")
            return


def menu_tools(stdscr):
    items = [
        get_text('checkers'),
        get_text('export_repo'),
        get_text('backup_repo'),
        get_text('update_versions'),
        get_text('generate_retrospective'),
        get_text('check_env'),
        get_text('generate_index'),
        get_text('daily_report'),
        get_text('check_health'),
        get_text('back'),
    ]
    actions = [
        lambda: run_with_error_handling(stdscr, menu_checkers, stdscr),
        lambda: run_with_error_handling(stdscr, export_repo, stdscr),
        lambda: run_with_error_handling(stdscr, backup_repo, stdscr),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'update-versions.py', get_text('update_versions'), ['--dry-run']),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'generate-retrospective.py', get_text('generate_retrospective')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'check-env.py', get_text('check_env')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'generate-index.py', get_text('generate_index')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'daily-report.py', get_text('daily_report')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'check-health.py', get_text('check_health')),
        lambda: None,
    ]
    
    selected = 0
    height, width = stdscr.getmaxyx()
    curses.curs_set(0)
    
    while True:
        try:
            stdscr.clear()
            title = f"{get_text('title').format(VERSION)} - {get_text('tools')}"
            stdscr.addstr(0, max(0, (width - len(title)) // 2), title, curses.A_BOLD | curses.A_UNDERLINE)
            
            start_y = 3
            for i, item in enumerate(items):
                y = start_y + i
                if y >= height - 2:
                    break
                if i == selected:
                    stdscr.addstr(y, 4, "> " + item, curses.A_REVERSE)
                else:
                    stdscr.addstr(y, 4, "  " + item, curses.A_NORMAL)
            
            hint = get_text('up_down')
            stdscr.addstr(height - 2, max(0, (width - len(hint)) // 2), hint, curses.A_DIM)
            stdscr.refresh()
            
            key = stdscr.getch()
            
            if key in [ord('q'), ord('й'), ord('ע')]:
                return
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(items) - 1:
                selected += 1
            elif key in [ord('\n'), ord('\r')]:
                if selected == len(items) - 1:
                    return
                actions[selected]()
                stdscr.clear()
                stdscr.refresh()
            elif key == 27 or key == curses.KEY_LEFT:
                return
        except KeyboardInterrupt:
            return
        except Exception as e:
            log_error(f"Ошибка в menu_tools: {e}")
            return


def menu_checkers(stdscr):
    items = [
        get_text('check_file_naming'),
        get_text('check_metadata'),
        get_text('check_links'),
        get_text('find_duplicates'),
        get_text('find_orphans'),
        get_text('check_consistency'),
        get_text('stats'),
        get_text('generate_glossary'),
        get_text('generate_navigation'),
        get_text('sync_structure'),
        get_text('back'),
    ]
    actions = [
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'check-naming.py', get_text('check_file_naming')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'validate-metadata.py', get_text('check_metadata')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'check-links.py', get_text('check_links')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'find-duplicates.py', get_text('find_duplicates')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'find-orphans.py', get_text('find_orphans')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'consistency-checker.py', get_text('check_consistency')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'stats-report.py', get_text('stats')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'generate-glossary.py', get_text('generate_glossary')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'generate-nav.py', get_text('generate_navigation')),
        lambda: run_with_error_handling(stdscr, run_script_and_show, stdscr, 'sync-structure.py', get_text('sync_structure')),
        lambda: None,
    ]
    
    selected = 0
    height, width = stdscr.getmaxyx()
    curses.curs_set(0)
    
    while True:
        try:
            stdscr.clear()
            title = f"{get_text('title').format(VERSION)} - {get_text('checkers')}"
            stdscr.addstr(0, max(0, (width - len(title)) // 2), title, curses.A_BOLD | curses.A_UNDERLINE)
            
            start_y = 3
            for i, item in enumerate(items):
                y = start_y + i
                if y >= height - 2:
                    break
                if i == selected:
                    stdscr.addstr(y, 4, "> " + item, curses.A_REVERSE)
                else:
                    stdscr.addstr(y, 4, "  " + item, curses.A_NORMAL)
            
            hint = get_text('up_down')
            stdscr.addstr(height - 2, max(0, (width - len(hint)) // 2), hint, curses.A_DIM)
            stdscr.refresh()
            
            key = stdscr.getch()
            
            if key in [ord('q'), ord('й'), ord('ע')]:
                return
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(items) - 1:
                selected += 1
            elif key in [ord('\n'), ord('\r')]:
                if selected == len(items) - 1:
                    return
                actions[selected]()
                stdscr.clear()
                stdscr.refresh()
            elif key == 27 or key == curses.KEY_LEFT:
                return
        except KeyboardInterrupt:
            return
        except Exception as e:
            log_error(f"Ошибка в menu_checkers: {e}")
            return


def menu_settings(stdscr):
    global current_lang
    items = [get_text('language_ru'), get_text('language_en'), get_text('language_he'), get_text('save'), get_text('back')]
    
    selected = 0
    height, width = stdscr.getmaxyx()
    temp_lang = current_lang
    
    curses.curs_set(0)
    
    while True:
        try:
            stdscr.clear()
            title = f"{get_text('title').format(VERSION)} - {get_text('settings')}"
            stdscr.addstr(0, max(0, (width - len(title)) // 2), title, curses.A_BOLD | curses.A_UNDERLINE)
            
            start_y = 3
            for i, item in enumerate(items):
                y = start_y + i
                if y >= height - 2:
                    break
                
                display = item
                if i == 0 and temp_lang == "ru":
                    display = "[X] " + item
                elif i == 1 and temp_lang == "en":
                    display = "[X] " + item
                elif i == 2 and temp_lang == "he":
                    display = "[X] " + item
                
                if i == selected:
                    stdscr.addstr(y, 4, "> " + display, curses.A_REVERSE)
                else:
                    stdscr.addstr(y, 4, "  " + display, curses.A_NORMAL)
            
            hint = get_text('up_down')
            stdscr.addstr(height - 2, max(0, (width - len(hint)) // 2), hint, curses.A_DIM)
            stdscr.refresh()
            
            key = stdscr.getch()
            
            if key in [ord('q'), ord('й'), ord('ע')]:
                return
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(items) - 1:
                selected += 1
            elif key in [ord('\n'), ord('\r')]:
                if selected == 0:
                    temp_lang = "ru"
                elif selected == 1:
                    temp_lang = "en"
                elif selected == 2:
                    temp_lang = "he"
                elif selected == 3:
                    if temp_lang != current_lang:
                        config["language"] = temp_lang
                        if save_config(config):
                            current_lang = temp_lang
                            try:
                                stdscr.clear()
                                msg = get_text('language_changed')
                                stdscr.addstr(height // 2, max(0, (width - len(msg)) // 2), msg)
                                stdscr.refresh()
                                stdscr.getch()
                            except:
                                pass
                        return
                elif selected == 4:
                    return
            elif key == 27 or key == curses.KEY_LEFT:
                return
        except KeyboardInterrupt:
            return
        except Exception as e:
            log_error(f"Ошибка в menu_settings: {e}")
            return


def run_everything(stdscr):
    run_script_and_show(stdscr, 'check-naming.py', get_text('check_file_naming'))
    run_script_and_show(stdscr, 'validate-metadata.py', get_text('check_metadata'), ['--fix'])
    run_script_and_show(stdscr, 'check-links.py', get_text('check_links'))
    run_script_and_show(stdscr, 'find-duplicates.py', get_text('find_duplicates'))
    run_script_and_show(stdscr, 'find-orphans.py', get_text('find_orphans'))
    run_script_and_show(stdscr, 'consistency-checker.py', get_text('check_consistency'))
    run_script_and_show(stdscr, 'stats-report.py', get_text('stats'))
    run_script_and_show(stdscr, 'generate-glossary.py', get_text('generate_glossary'))
    run_script_and_show(stdscr, 'generate-nav.py', get_text('generate_navigation'))
    run_script_and_show(stdscr, 'sync-structure.py', get_text('sync_structure'))


def export_repo(stdscr):
    script_path = TOOLS_DIR / 'export-repo.sh'
    if not script_path.exists():
        try:
            stdscr.addstr(f"[X] export-repo.sh {get_text('not_found')}\n")
            stdscr.refresh()
            stdscr.getch()
        except:
            print(f"[X] export-repo.sh {get_text('not_found')}")
        return
    
    try:
        curses.endwin()
        subprocess.run(['bash', str(script_path)], cwd=TOOLS_DIR)
        input(f"\n{get_text('press_enter')}")
    except Exception as e:
        log_error(f"Ошибка экспорта: {e}")
        print(f"\n{get_text('error_occurred')}: {e}")
        input(f"\n{get_text('press_enter')}")
    finally:
        stdscr.clear()
        stdscr.refresh()


def backup_repo(stdscr):
    script_path = TOOLS_DIR / 'backup.sh'
    if not script_path.exists():
        try:
            stdscr.addstr(f"[X] backup.sh {get_text('not_found')}\n")
            stdscr.refresh()
            stdscr.getch()
        except:
            print(f"[X] backup.sh {get_text('not_found')}")
        return
    
    try:
        curses.endwin()
        subprocess.run(['bash', str(script_path)], cwd=TOOLS_DIR)
        input(f"\n{get_text('press_enter')}")
    except Exception as e:
        log_error(f"Ошибка бэкапа: {e}")
        print(f"\n{get_text('error_occurred')}: {e}")
        input(f"\n{get_text('press_enter')}")
    finally:
        stdscr.clear()
        stdscr.refresh()


def main_menu(stdscr):
    items = [get_text('actions'), get_text('management'), get_text('tools'), get_text('settings'), get_text('exit')]
    menus = [menu_actions, menu_management, menu_tools, menu_settings, None]
    
    selected = 0
    height, width = stdscr.getmaxyx()
    curses.curs_set(0)
    
    while True:
        try:
            stdscr.clear()
            title = get_text('title').format(VERSION)
            stdscr.addstr(0, max(0, (width - len(title)) // 2), title, curses.A_BOLD | curses.A_UNDERLINE)
            
            start_y = 3
            for i, item in enumerate(items):
                y = start_y + i
                if y >= height - 2:
                    break
                if i == selected:
                    stdscr.addstr(y, 4, "> " + item, curses.A_REVERSE)
                else:
                    stdscr.addstr(y, 4, "  " + item, curses.A_NORMAL)
            
            hint = get_text('up_down')
            stdscr.addstr(height - 2, max(0, (width - len(hint)) // 2), hint, curses.A_DIM)
            stdscr.refresh()
            
            key = stdscr.getch()
            
            if key in [ord('q'), ord('й'), ord('ע')]:
                break
            if key == curses.KEY_UP and selected > 0:
                selected -= 1
            elif key == curses.KEY_DOWN and selected < len(items) - 1:
                selected += 1
            elif key in [ord('\n'), ord('\r')]:
                if selected == len(items) - 1:
                    break
                menus[selected](stdscr)
            elif key == 27 or key == curses.KEY_LEFT:
                if selected == len(items) - 1:
                    break
        except KeyboardInterrupt:
            break
        except Exception as e:
            log_error(f"Ошибка в main_menu: {e}")
            break


def main():
    global current_lang
    
    load_languages()
    config_data = load_config()
    current_lang = config_data.get("language", "ru")
    
    try:
        curses.wrapper(main_menu)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log_error(f"Критическая ошибка: {e}\n{traceback.format_exc()}")
        print(f"\n\033[91m{get_text('error_occurred')}: {e}\033[0m")
        print(get_text('check_log'))
    finally:
        print(f"\n\033[92m{get_text('goodbye')}\033[0m\n")


if __name__ == "__main__":
    main()