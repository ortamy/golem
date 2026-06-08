#!/usr/bin/env python3
# golem.py — единый скрипт для управления проектом (древовидное меню) v4.0

import os
import sys
import subprocess
import json
import traceback
import re
import time
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
VERSION = "4.0"

current_lang = "ru"
LANGUAGES = {}
config = {}

D = TOOLS_DIR
PATHS = {
    "check_naming":             D / "checkers" / "check-naming.py",
    "validate_metadata":        D / "checkers" / "validate-metadata.py",
    "fix_metadata_fields":      D / "checkers" / "fix-metadata-fields.py",
    "check_links":              D / "checkers" / "check-links.py",
    "validate_external_links":  D / "checkers" / "validate-external-links.py",
    "find_duplicates":          D / "checkers" / "find-duplicates.py",
    "find_orphans":             D / "checkers" / "find-orphans.py",
    "check_empty_files":        D / "checkers" / "check-empty-files.py",
    "consistency":              D / "checkers" / "consistency-checker.py",
    "check_religionisms":       D / "checkers" / "check-religionisms.py",
    "check_tahor_sync":         D / "checkers" / "check-tahor-sync.py",
    "check_code_quality":       D / "checkers" / "check-code-quality.py",
    "clear_cache":              D / "checkers" / "clear-cache.py",
    "generate_glossary":        D / "generators" / "generate-glossary.py",
    "generate_nav":             D / "generators" / "generate-nav.py",
    "sync_structure":           D / "generators" / "sync-structure.py",
    "generate_retrospective":   D / "generators" / "generate-retrospective.py",
    "generate_changelog":       D / "generators" / "generate-changelog.py",
    "generate_index":           D / "generators" / "generate-index.py",
    "unify_metadata":           D / "generators" / "unify-metadata.py",
    "stats_report":             D / "reports" / "stats-report.py",
    "check_file_sizes":         D / "reports" / "check-file-sizes.py",
    "daily_report":             D / "reports" / "daily-report.py",
    "check_health":             D / "reports" / "check-health.py",
    "add_metadata":             D / "automation" / "add-metadata.py",
    "auto_fix":                 D / "automation" / "auto-fix.py",
    "task_manager":             D / "automation" / "task-manager.py",
    "idea_manager":             D / "automation" / "idea-manager.py",
    "update_versions":          D / "automation" / "update-versions.py",
    "export_repo":              D / "backup" / "export-repo.sh",
    "backup_repo":              D / "backup" / "backup.sh",
}

SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
LABEL_WIDTH = 45

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {msg}\n")
    except Exception:
        pass

def load_languages():
    global LANGUAGES
    LANGUAGES = {
        "ru": {
            "title": "ГОЛЕМ v{}", "actions": "ДЕЙСТВИЯ", "tools": "ИНСТРУМЕНТЫ", "exit": "ВЫХОД",
            "run_all_checks": "Запустить все проверки", "run_all_fixes": "Запустить все исправления",
            "full_audit": "Полный аудит", "checkers": "Чекеры", "generators": "Генераторы",
            "reports": "Отчёты", "automation": "Автоматизация", "backup": "Бэкап и экспорт",
            "check_file_naming": "Проверка имён файлов", "check_metadata": "Проверка метаданных",
            "fix_metadata_fields": "Исправить поля метаданных", "check_links": "Проверка внутренних ссылок",
            "validate_external_links": "Проверка внешних ссылок", "find_duplicates": "Поиск дубликатов",
            "find_orphans": "Поиск файлов-сирот", "check_empty_files": "Поиск пустых/незаполненных",
            "check_consistency": "Проверка согласованности", "check_religionisms": "Проверить религионимы",
            "check_tahor_sync": "Сверка tahor/ ↔ forbidden-words", "check_code_quality": "Проверить качество кода",
            "clear_cache": "Очистить кэш", "generate_glossary": "Генерация глоссария",
            "generate_navigation": "Генерация навигации", "sync_structure": "Синхронизация структуры",
            "generate_retrospective": "Ретроспектива", "generate_changelog": "Генерация CHANGELOG",
            "generate_index": "Индексы папок", "unify_metadata": "Унификация метаданных",
            "stats": "Статистика репозитория", "check_file_sizes": "Анализ размеров файлов",
            "daily_report": "Ежедневный отчёт", "check_health": "Здоровье проекта",
            "add_metadata": "Добавить метаданные", "auto_fix": "Автофикс задач",
            "task_manager": "Менеджер задач", "idea_manager": "Управление идеями",
            "update_versions": "Обновить версии", "export_repo": "Экспорт репозитория",
            "backup_repo": "Создать бэкап", "back": "← Назад", "running": "Выполняется: {}",
            "up_down": "↑↓ выбор | Enter вход | Esc/← назад | q выход", "goodbye": "До свидания!",
            "not_found": "не найден", "press_enter": "Нажмите любую клавишу...",
            "error_occurred": "Произошла ошибка", "skipped": "пропущен",
        },
        "en": {
            "title": "GOLEM v{}", "actions": "ACTIONS", "tools": "TOOLS", "exit": "EXIT",
            "run_all_checks": "Run all checks", "run_all_fixes": "Run all fixes",
            "full_audit": "Full audit", "checkers": "Checkers", "generators": "Generators",
            "reports": "Reports", "automation": "Automation", "backup": "Backup & Export",
            "check_file_naming": "Check file naming", "check_metadata": "Check metadata",
            "fix_metadata_fields": "Fix metadata fields", "check_links": "Check internal links",
            "validate_external_links": "Validate external links", "find_duplicates": "Find duplicates",
            "find_orphans": "Find orphans", "check_empty_files": "Find empty/unfilled",
            "check_consistency": "Check consistency", "check_religionisms": "Check religionisms",
            "check_tahor_sync": "Sync tahor/ ↔ forbidden-words", "check_code_quality": "Check code quality",
            "clear_cache": "Clear cache", "generate_glossary": "Generate glossary",
            "generate_navigation": "Generate navigation", "sync_structure": "Sync structure",
            "generate_retrospective": "Retrospective", "generate_changelog": "Generate CHANGELOG",
            "generate_index": "Folder index", "unify_metadata": "Unify metadata",
            "stats": "Repository statistics", "check_file_sizes": "File size analysis",
            "daily_report": "Daily report", "check_health": "Project health",
            "add_metadata": "Add metadata", "auto_fix": "Auto fix tasks",
            "task_manager": "Task manager", "idea_manager": "Idea manager",
            "update_versions": "Update versions", "export_repo": "Export repository",
            "backup_repo": "Backup repository", "back": "← Back", "running": "Running: {}",
            "up_down": "↑↓ select | Enter enter | Esc/← back | q quit", "goodbye": "Goodbye!",
            "not_found": "not found", "press_enter": "Press any key...",
            "error_occurred": "An error occurred", "skipped": "skipped",
        },
    }

def load_config():
    global config
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        if CONFIG_FILE.exists():
            config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return
    except Exception:
        pass
    config = {"language": "ru"}

def save_config():
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log(f"config: {e}")

def t(key):
    return LANGUAGES.get(current_lang, LANGUAGES["ru"]).get(key, key)

def _flash(stdscr, msg):
    try:
        stdscr.addstr(msg + "\n")
        stdscr.refresh()
        stdscr.getch()
    except Exception:
        print(msg)

def _wait_key():
    print(f"\n{t('press_enter')}")
    try:
        if os.name == 'nt':
            import msvcrt
            msvcrt.getch()
        else:
            sys.stdin.read(1)
    except Exception:
        input()

def _run_py(stdscr, script_path, args=None, description=None):
    if not script_path.exists():
        _flash(stdscr, f"[X] {script_path.name} — {t('skipped')}")
        return
    try:
        h, w = stdscr.getmaxyx()
        msg = t('running').format(description or script_path.stem)
        stdscr.addstr(h // 2, max(0, (w - len(msg)) // 2), msg, curses.A_BOLD)
        stdscr.refresh()
        curses.napms(400)
        curses.endwin()
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        subprocess.run(cmd, cwd=str(REPO_ROOT))
        _wait_key()
        curses.initscr()
        stdscr.clear()
        stdscr.refresh()
    except Exception as e:
        log(f"run: {script_path.name}: {e}")
        print(f"\n{t('error_occurred')}: {e}")
        _wait_key()
        curses.initscr()
        stdscr.clear()
        stdscr.refresh()

def _run_sh(stdscr, script_path):
    if not script_path.exists():
        _flash(stdscr, f"[X] {script_path.name} — {t('skipped')}")
        return
    try:
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h // 2, max(0, (w - len(t('running').format(script_path.stem))) // 2),
                      t('running').format(script_path.stem), curses.A_BOLD)
        stdscr.refresh()
        curses.napms(400)
        curses.endwin()
        subprocess.run(['bash', str(script_path)], cwd=str(TOOLS_DIR))
        _wait_key()
        curses.initscr()
        stdscr.clear()
        stdscr.refresh()
    except Exception as e:
        log(f"bash: {script_path.name}: {e}")
        print(f"\n{t('error_occurred')}: {e}")
        _wait_key()
        curses.initscr()
        stdscr.clear()
        stdscr.refresh()

def draw_menu(stdscr, title_key, items, selected):
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    title = f"{t('title').format(VERSION)} — {t(title_key)}"
    stdscr.addstr(0, max(0, (w - len(title)) // 2), title, curses.A_BOLD | curses.A_UNDERLINE)
    for i, item in enumerate(items):
        y = 3 + i
        if y >= h - 2:
            break
        attr = curses.A_REVERSE if i == selected else curses.A_NORMAL
        stdscr.addstr(y, 4, ("> " if i == selected else "  ") + item, attr)
    hint = t('up_down')
    stdscr.addstr(h - 2, max(0, (w - len(hint)) // 2), hint, curses.A_DIM)
    stdscr.refresh()

def menu_loop(stdscr, title_key, items, actions):
    sel = 0
    n = len(items)
    while True:
        try:
            draw_menu(stdscr, title_key, items, sel)
            key = stdscr.getch()
            if key in (ord('q'), ord('й')): return
            elif key == curses.KEY_UP and sel > 0: sel -= 1
            elif key == curses.KEY_DOWN and sel < n - 1: sel += 1
            elif key in (ord('\n'), ord('\r')):
                if sel == n - 1: return
                if callable(actions[sel]): actions[sel]()
                stdscr.clear(); stdscr.refresh()
            elif key in (27, curses.KEY_LEFT): return
        except KeyboardInterrupt: return
        except Exception as e: log(f"menu {title_key}: {e}"); return

def menu_actions(stdscr):
    menu_loop(stdscr, 'actions',
              [t('run_all_checks'), t('run_all_fixes'), t('full_audit'), t('back')],
              [lambda: run_all_checks(stdscr), lambda: run_all_fixes(stdscr),
               lambda: run_full_audit(stdscr), None])

def menu_tools(stdscr):
    menu_loop(stdscr, 'tools',
              [t('checkers'), t('generators'), t('reports'), t('automation'), t('backup'), t('back')],
              [lambda: menu_checkers(stdscr), lambda: menu_generators(stdscr),
               lambda: menu_reports(stdscr), lambda: menu_automation(stdscr),
               lambda: menu_backup(stdscr), None])

def menu_checkers(stdscr):
    menu_loop(stdscr, 'checkers',
              [t('check_file_naming'), t('check_metadata'), t('fix_metadata_fields'),
               t('check_links'), t('validate_external_links'), t('find_duplicates'),
               t('find_orphans'), t('check_empty_files'), t('check_consistency'),
               t('check_religionisms'), t('check_tahor_sync'), t('check_code_quality'),
               t('clear_cache'), t('back')],
              [lambda: _run_py(stdscr, PATHS["check_naming"]),
               lambda: _run_py(stdscr, PATHS["validate_metadata"]),
               lambda: _run_py(stdscr, PATHS["fix_metadata_fields"]),
               lambda: _run_py(stdscr, PATHS["check_links"]),
               lambda: _run_py(stdscr, PATHS["validate_external_links"]),
               lambda: _run_py(stdscr, PATHS["find_duplicates"]),
               lambda: _run_py(stdscr, PATHS["find_orphans"]),
               lambda: _run_py(stdscr, PATHS["check_empty_files"]),
               lambda: _run_py(stdscr, PATHS["consistency"]),
               lambda: _run_py(stdscr, PATHS["check_religionisms"]),
               lambda: _run_py(stdscr, PATHS["check_tahor_sync"]),
               lambda: _run_py(stdscr, PATHS["check_code_quality"]),
               lambda: _run_py(stdscr, PATHS["clear_cache"]), None])

def menu_generators(stdscr):
    menu_loop(stdscr, 'generators',
              [t('generate_glossary'), t('generate_navigation'), t('sync_structure'),
               t('unify_metadata'), t('generate_retrospective'), t('generate_changelog'),
               t('generate_index'), t('back')],
              [lambda: _run_py(stdscr, PATHS["generate_glossary"]),
               lambda: _run_py(stdscr, PATHS["generate_nav"]),
               lambda: _run_py(stdscr, PATHS["sync_structure"]),
               lambda: _run_py(stdscr, PATHS["unify_metadata"], ['--dry-run']),
               lambda: _run_py(stdscr, PATHS["generate_retrospective"]),
               lambda: _run_py(stdscr, PATHS["generate_changelog"], ['--dry-run']),
               lambda: _run_py(stdscr, PATHS["generate_index"]), None])

def menu_reports(stdscr):
    menu_loop(stdscr, 'reports',
              [t('stats'), t('check_file_sizes'), t('daily_report'), t('check_health'), t('back')],
              [lambda: _run_py(stdscr, PATHS["stats_report"]),
               lambda: _run_py(stdscr, PATHS["check_file_sizes"]),
               lambda: _run_py(stdscr, PATHS["daily_report"]),
               lambda: _run_py(stdscr, PATHS["check_health"]), None])

def menu_automation(stdscr):
    menu_loop(stdscr, 'automation',
              [t('add_metadata'), t('auto_fix'), t('task_manager'), t('idea_manager'),
               t('update_versions'), t('back')],
              [lambda: _run_py(stdscr, PATHS["add_metadata"]),
               lambda: _run_py(stdscr, PATHS["auto_fix"]),
               lambda: _run_py(stdscr, PATHS["task_manager"]),
               lambda: _run_py(stdscr, PATHS["idea_manager"]),
               lambda: _run_py(stdscr, PATHS["update_versions"], ['--dry-run']), None])

def menu_backup(stdscr):
    menu_loop(stdscr, 'backup',
              [t('export_repo'), t('backup_repo'), t('back')],
              [lambda: _run_sh(stdscr, PATHS["export_repo"]),
               lambda: _run_sh(stdscr, PATHS["backup_repo"]), None])

def run_all_checks(stdscr):
    scripts = [
        (PATHS["check_naming"], t('check_file_naming')),
        (PATHS["validate_metadata"], t('check_metadata')),
        (PATHS["fix_metadata_fields"], t('fix_metadata_fields')),
        (PATHS["check_links"], t('check_links')),
        (PATHS["find_duplicates"], t('find_duplicates')),
        (PATHS["find_orphans"], t('find_orphans')),
        (PATHS["check_empty_files"], t('check_empty_files')),
        (PATHS["consistency"], t('check_consistency')),
        (PATHS["check_religionisms"], t('check_religionisms')),
        (PATHS["check_tahor_sync"], t('check_tahor_sync')),
        (PATHS["check_code_quality"], t('check_code_quality')),
    ]
    total = len(scripts)
    results = []
    curses.endwin()

    for i, (script_path, description) in enumerate(scripts, 1):
        label = f"[{i:2d}/{total}] {description}".ljust(LABEL_WIDTH)

        if not script_path.exists():
            print(f"{label} ⏭️ {t('not_found')}")
            results.append((description, "skip", 0, 0))
            continue

        cmd = [sys.executable, str(script_path)]
        proc = subprocess.Popen(cmd, cwd=str(REPO_ROOT), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        si = 0
        while proc.poll() is None:
            sys.stdout.write(f"\r{label} {SPINNER[si % len(SPINNER)]} Выполняется...")
            sys.stdout.flush()
            si += 1
            time.sleep(0.08)
        proc.wait()
        sys.stdout.write("\r" + " " * 80 + "\r")

        output = proc.stdout.read() if proc.stdout else ""
        found_files = re.search(r'(?:Найдено файлов|Всего)[:\s]*(\d+)', output)
        found_issues = re.search(r'(?:Файлов с |ошибок|проблем|нарушений)[:\s]*(\d+)', output)
        ok_msg = re.search(r'(✅|Все|корректны|не найдено)', output)

        total_files = int(found_files.group(1)) if found_files else 0
        issues = int(found_issues.group(1)) if found_issues else 0

        if ok_msg or (proc.returncode == 0 and not found_issues):
            print(f"{label} ✅ {total_files} файлов")
            results.append((description, "ok", total_files, 0))
        elif issues > 0:
            print(f"{label} ❌ {issues} проблем")
            results.append((description, "issues", 0, issues))
        else:
            print(f"{label} ✅ {total_files} файлов")
            results.append((description, "ok", total_files, 0))

    ok = sum(1 for _, s, _, _ in results if s == "ok")
    bad = sum(1 for _, s, _, _ in results if s == "issues")
    skp = sum(1 for _, s, _, _ in results if s == "skip")

    print(f"\n{'═' * 50}\nРЕЗУЛЬТАТЫ\n{'═' * 50}")
    for name, status, files, issues in results:
        if status == "ok":    print(f"  ✅ {name}")
        elif status == "issues": print(f"  ❌ {name} — {issues} проблем")
        elif status == "skip":   print(f"  ⏭️ {name} — {t('not_found')}")
    print(f"\n  Пройдено: {ok} | Проблем: {bad} | Пропущено: {skp}\n{'═' * 50}")

    _wait_key()
    curses.initscr()
    stdscr.clear()
    stdscr.refresh()

def run_all_fixes(stdscr):
    scripts = [
        (PATHS["validate_metadata"], ['--fix']),
        (PATHS["fix_metadata_fields"], ['--fix']),
        (PATHS["check_religionisms"], ['--fix']),
        (PATHS["check_code_quality"], ['--fix']),
        (PATHS["sync_structure"], []),
        (PATHS["generate_glossary"], []),
        (PATHS["generate_nav"], []),
    ]
    for script, args in scripts:
        _run_py(stdscr, script, args=args)

def run_full_audit(stdscr):
    run_all_checks(stdscr)
    run_all_fixes(stdscr)
    _run_py(stdscr, PATHS["stats_report"])

def main_menu(stdscr):
    items = [t('actions'), t('tools'), t('exit')]
    menus = [menu_actions, menu_tools, None]
    sel = 0
    n = len(items)
    while True:
        try:
            draw_menu(stdscr, 'title', items, sel)
            key = stdscr.getch()
            if key in (ord('q'), ord('й')): break
            elif key == curses.KEY_UP and sel > 0: sel -= 1
            elif key == curses.KEY_DOWN and sel < n - 1: sel += 1
            elif key in (ord('\n'), ord('\r')):
                if sel == n - 1: break
                if callable(menus[sel]): menus[sel](stdscr)
            elif key in (27, curses.KEY_LEFT):
                if sel == n - 1: break
        except KeyboardInterrupt: break
        except Exception as e: log(f"main: {e}"); break

def main():
    global current_lang
    load_languages()
    load_config()
    saved = config.get("language", "ru")
    print("\nВыберите язык / Select language:\n  1. Русский\n  2. English")
    print(f"  Enter — сохранённый ({saved})")
    choice = input("> ").strip()
    lang_map = {"1": "ru", "2": "en"}
    current_lang = lang_map.get(choice, saved)
    if choice in lang_map:
        config["language"] = current_lang
        save_config()
    try:
        curses.wrapper(main_menu)
    except KeyboardInterrupt: pass
    except Exception as e:
        log(f"critical: {e}\n{traceback.format_exc()}")
        print(f"\n\033[91m{t('error_occurred')}: {e}\033[0m")
    finally:
        print(f"\n\033[92m{t('goodbye')}\033[0m\n")

if __name__ == "__main__":
    main()