#!/usr/bin/env python3
# golem.py — единый скрипт для управления проектом (древовидное меню) v4.1

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
VERSION = "4.1"

current_lang = "ru"
LANGUAGES = {}
config = {}

# =============================================================================
# АВТО-СКАНИРОВАНИЕ СКРИПТОВ
# =============================================================================

def scan_scripts():
    """Автоматически находит все скрипты в подпапках tools/."""
    paths = {}
    for subdir in ["checkers", "generators", "reports", "automation"]:
        dir_path = TOOLS_DIR / subdir
        if dir_path.exists():
            for script in sorted(dir_path.glob("*.py")):
                name = script.stem.replace("-", "_").replace(".", "_")
                paths[name] = script
    # Bash-скрипты
    backup_dir = TOOLS_DIR / "backup"
    if backup_dir.exists():
        for script in sorted(backup_dir.glob("*.sh")):
            name = script.stem.replace("-", "_").replace(".", "_")
            paths[name] = script
    return paths

PATHS = scan_scripts()

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
            "back": "← Назад", "running": "Выполняется: {}",
            "up_down": "↑↓ выбор | Enter вход | Esc/← назад | q выход", "goodbye": "До свидания!",
            "not_found": "не найден", "press_enter": "Нажмите любую клавишу...",
            "error_occurred": "Произошла ошибка", "skipped": "пропущен",
        },
        "en": {
            "title": "GOLEM v{}", "actions": "ACTIONS", "tools": "TOOLS", "exit": "EXIT",
            "run_all_checks": "Run all checks", "run_all_fixes": "Run all fixes",
            "full_audit": "Full audit", "checkers": "Checkers", "generators": "Generators",
            "reports": "Reports", "automation": "Automation", "backup": "Backup & Export",
            "back": "← Back", "running": "Running: {}",
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


def _build_menu(menu_type):
    """Строит меню из скриптов в указанной папке."""
    items = []
    actions = []
    folder = TOOLS_DIR / menu_type
    if folder.exists():
        for script in sorted(folder.glob("*.py")):
            name = script.stem.replace("-", " ").replace("_", " ").title()
            items.append(name)
            actions.append(lambda s=script: _run_py(None, s, description=s.stem))
    items.append(t('back'))
    actions.append(None)
    return items, actions


def menu_checkers(stdscr):
    items, actions = _build_menu("checkers")
    # Перемещаем clear_cache в конец перед back
    menu_loop(stdscr, 'checkers', items, actions)


def menu_generators(stdscr):
    items, actions = _build_menu("generators")
    menu_loop(stdscr, 'generators', items, actions)


def menu_reports(stdscr):
    items, actions = _build_menu("reports")
    menu_loop(stdscr, 'reports', items, actions)


def menu_automation(stdscr):
    items, actions = _build_menu("automation")
    menu_loop(stdscr, 'automation', items, actions)


def menu_backup(stdscr):
    items = [t('export_repo'), t('backup_repo'), t('back')]
    actions = [
        lambda: _run_sh(stdscr, PATHS.get("export_repo", TOOLS_DIR / "backup" / "export-repo.sh")),
        lambda: _run_sh(stdscr, PATHS.get("backup_repo", TOOLS_DIR / "backup" / "backup.sh")),
        None,
    ]
    menu_loop(stdscr, 'backup', items, actions)


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


def run_all_checks(stdscr):
    checkers_dir = TOOLS_DIR / "checkers"
    if not checkers_dir.exists():
        return

    scripts = [(s, s.stem.replace("-", " ").title()) for s in sorted(checkers_dir.glob("*.py"))]
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
        (PATHS.get("validate_metadata", TOOLS_DIR / "checkers" / "validate-metadata.py"), ['--fix']),
        (PATHS.get("fix_metadata_fields", TOOLS_DIR / "checkers" / "fix-metadata-fields.py"), ['--fix']),
        (PATHS.get("check_religionisms", TOOLS_DIR / "checkers" / "check-religionisms.py"), ['--fix']),
        (PATHS.get("check_code_quality", TOOLS_DIR / "checkers" / "check-code-quality.py"), ['--fix']),
        (PATHS.get("sync_structure", TOOLS_DIR / "generators" / "sync-structure.py"), []),
        (PATHS.get("generate_glossary", TOOLS_DIR / "generators" / "generate-glossary.py"), []),
        (PATHS.get("generate_nav", TOOLS_DIR / "generators" / "generate-nav.py"), []),
    ]
    for script, args in scripts:
        _run_py(stdscr, script, args=args)


def run_full_audit(stdscr):
    run_all_checks(stdscr)
    run_all_fixes(stdscr)
    _run_py(stdscr, PATHS.get("stats_report", TOOLS_DIR / "reports" / "stats-report.py"))


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