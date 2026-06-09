#!/usr/bin/env python3
# golem.py — единый скрипт для управления проектом (минимализм v4.3)

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
VERSION = "4.3"

current_lang = "ru"
LANGUAGES = {}
config = {}

SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
LABEL_WIDTH = 45

# Цвета (инициализируются после initscr)
ORANGE = None
SELECTED = None
DIM = None
WHITE = None


def init_colors():
    global ORANGE, SELECTED, DIM, WHITE
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, 208, -1)      # Оранжевый на дефолтном фоне
        curses.init_pair(2, 255, 208)     # Белый на оранжевом (выделение)
        curses.init_pair(3, 240, -1)      # Серый
        curses.init_pair(4, 255, -1)      # Белый
        ORANGE = curses.color_pair(1)
        SELECTED = curses.color_pair(2)
        DIM = curses.color_pair(3)
        WHITE = curses.color_pair(4)
    else:
        ORANGE = curses.A_NORMAL
        SELECTED = curses.A_REVERSE
        DIM = curses.A_DIM
        WHITE = curses.A_NORMAL


def scan_scripts():
    paths = {}
    for subdir in ["checkers", "generators", "reports", "automation"]:
        dir_path = TOOLS_DIR / subdir
        if dir_path.exists():
            for script in sorted(dir_path.glob("*.py")):
                name = script.stem.replace("-", "_").replace(".", "_")
                paths[name] = script
    backup_dir = TOOLS_DIR / "backup"
    if backup_dir.exists():
        for script in sorted(backup_dir.glob("*.sh")):
            name = script.stem.replace("-", "_").replace(".", "_")
            paths[name] = script
    return paths


PATHS = scan_scripts()


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
            "title": "ГОЛЕМ", "actions": "ДЕЙСТВИЯ", "tools": "ИНСТРУМЕНТЫ", "exit": "ВЫХОД",
            "run_all_checks": "Запустить все проверки", "run_all_fixes": "Запустить все исправления",
            "full_audit": "Полный аудит", "checkers": "Чекеры", "generators": "Генераторы",
            "reports": "Отчёты", "automation": "Автоматизация", "backup": "Бэкап",
            "back": "← НАЗАД", "running": "Выполняется: {}",
            "up_down": "↑↓ выбор   Enter вход   Esc назад   q выход",
            "goodbye": "До свидания.", "not_found": "не найден",
            "press_enter": "Нажмите любую клавишу...",
            "error_occurred": "Ошибка", "skipped": "пропущен",
        },
        "en": {
            "title": "GOLEM", "actions": "ACTIONS", "tools": "TOOLS", "exit": "EXIT",
            "run_all_checks": "Run all checks", "run_all_fixes": "Run all fixes",
            "full_audit": "Full audit", "checkers": "Checkers", "generators": "Generators",
            "reports": "Reports", "automation": "Automation", "backup": "Backup",
            "back": "← BACK", "running": "Running: {}",
            "up_down": "↑↓ select   Enter enter   Esc back   q quit",
            "goodbye": "Goodbye.", "not_found": "not found",
            "press_enter": "Press any key...",
            "error_occurred": "Error", "skipped": "skipped",
        },
        "he": {
            "title": "GOLEM", "actions": "PEULOT", "tools": "KELIM", "exit": "YETZIA",
            "run_all_checks": "Haratz bdikot", "run_all_fixes": "Haratz tikunim",
            "full_audit": "Bikoret", "checkers": "Bodkim", "generators": "Meholelim",
            "reports": "Duchot", "automation": "Automazia", "backup": "Gibuoy",
            "back": "← CHAZOR", "running": "Mevatze: {}",
            "up_down": "↑↓ bchira   Enter knisa   Esc chazor   q yetzia",
            "goodbye": "Lehitraot.", "not_found": "lo nimtza",
            "press_enter": "Lachatz al makash...",
            "error_occurred": "Shgia", "skipped": "dulug",
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
        h, w = stdscr.getmaxyx()
        stdscr.bkgd(' ', WHITE)
        stdscr.addstr(h // 2, max(0, (w - len(msg)) // 2), msg, DIM)
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
        stdscr.bkgd(' ', WHITE)
        msg = t('running').format(description or script_path.stem)
        stdscr.addstr(h // 2, max(0, (w - len(msg)) // 2), msg, ORANGE | curses.A_BOLD)
        stdscr.refresh()
        curses.napms(400)
        curses.endwin()
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        subprocess.run(cmd, cwd=str(REPO_ROOT))
        _wait_key()
        curses.initscr()
        init_colors()
        stdscr.clear()
        stdscr.refresh()
    except Exception as e:
        log(f"run: {script_path.name}: {e}")
        print(f"\n{t('error_occurred')}: {e}")
        _wait_key()
        curses.initscr()
        init_colors()
        stdscr.clear()
        stdscr.refresh()


def _run_sh(stdscr, script_path):
    if not script_path.exists():
        _flash(stdscr, f"[X] {script_path.name} — {t('skipped')}")
        return
    try:
        h, w = stdscr.getmaxyx()
        stdscr.bkgd(' ', WHITE)
        msg = t('running').format(script_path.stem)
        stdscr.addstr(h // 2, max(0, (w - len(msg)) // 2), msg, ORANGE | curses.A_BOLD)
        stdscr.refresh()
        curses.napms(400)
        curses.endwin()
        subprocess.run(['bash', str(script_path)], cwd=str(TOOLS_DIR))
        _wait_key()
        curses.initscr()
        init_colors()
        stdscr.clear()
        stdscr.refresh()
    except Exception as e:
        log(f"bash: {script_path.name}: {e}")
        print(f"\n{t('error_occurred')}: {e}")
        _wait_key()
        curses.initscr()
        init_colors()
        stdscr.clear()
        stdscr.refresh()


def draw_menu(stdscr, title_key, items, selected):
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.bkgd(' ', WHITE)

    title = t('title')
    stdscr.addstr(2, 4, title, ORANGE | curses.A_BOLD)
    stdscr.addstr(2, 4 + len(title) + 2, f"v{VERSION}", DIM)

    stdscr.addstr(4, 4, "─" * (w - 8), DIM)

    start_y = 6
    for i, item in enumerate(items):
        y = start_y + i
        if y >= h - 3:
            break
        if i == selected:
            stdscr.addstr(y, 4, " " * (w - 8), SELECTED)
            stdscr.addstr(y, 6, f"› {item}", SELECTED | curses.A_BOLD)
        else:
            stdscr.addstr(y, 6, f"  {item}", WHITE)

    hint = t('up_down')
    stdscr.addstr(h - 2, 4, hint, DIM)
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
    items = []
    actions = []
    folder = TOOLS_DIR / menu_type
    if folder.exists():
        for script in sorted(folder.glob("*.py")):
            name = script.stem.replace("-", " ").replace("_", " ").title()
            items.append(name)
            actions.append(lambda s=script: _run_py(stdscr, s, description=s.stem))
    items.append(t('back'))
    actions.append(None)
    return items, actions


# Исправлено: передача stdscr в замыкание
def _build_menu_actions(menu_type, stdscr):
    items = []
    actions = []
    folder = TOOLS_DIR / menu_type
    if folder.exists():
        for script in sorted(folder.glob("*.py")):
            name = script.stem.replace("-", " ").replace("_", " ").title()
            items.append(name)
            actions.append(lambda s=script: _run_py(stdscr, s, description=s.stem))
    items.append(t('back'))
    actions.append(None)
    return items, actions


def menu_checkers(stdscr):
    items, actions = _build_menu_actions("checkers", stdscr)
    menu_loop(stdscr, 'checkers', items, actions)


def menu_generators(stdscr):
    items, actions = _build_menu_actions("generators", stdscr)
    menu_loop(stdscr, 'generators', items, actions)


def menu_reports(stdscr):
    items, actions = _build_menu_actions("reports", stdscr)
    menu_loop(stdscr, 'reports', items, actions)


def menu_automation(stdscr):
    items, actions = _build_menu_actions("automation", stdscr)
    menu_loop(stdscr, 'automation', items, actions)


def menu_backup(stdscr):
    items = ["Экспорт репозитория", "Создать бэкап", t('back')]
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
            print(f"{label}  {t('not_found')}")
            results.append((description, "skip", 0, 0))
            continue

        cmd = [sys.executable, str(script_path)]
        proc = subprocess.Popen(cmd, cwd=str(REPO_ROOT), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        si = 0
        while proc.poll() is None:
            sys.stdout.write(f"\r{label} {SPINNER[si % len(SPINNER)]}")
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
            print(f"{label} ✓ {total_files} файлов")
            results.append((description, "ok", total_files, 0))
        elif issues > 0:
            print(f"{label} ✗ {issues} проблем")
            results.append((description, "issues", 0, issues))
        else:
            print(f"{label} ✓ {total_files} файлов")
            results.append((description, "ok", total_files, 0))

    ok = sum(1 for _, s, _, _ in results if s == "ok")
    bad = sum(1 for _, s, _, _ in results if s == "issues")
    skp = sum(1 for _, s, _, _ in results if s == "skip")

    print(f"\n{'─' * 50}")
    print(f"РЕЗУЛЬТАТЫ")
    print(f"{'─' * 50}")
    for name, status, files, issues in results:
        if status == "ok":    print(f"  ✓ {name}")
        elif status == "issues": print(f"  ✗ {name} — {issues} проблем")
        elif status == "skip":   print(f"  - {name} — {t('not_found')}")
    print(f"\n  Пройдено: {ok}  Проблем: {bad}  Пропущено: {skp}")
    print(f"{'─' * 50}")

    _wait_key()
    curses.initscr()
    init_colors()
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
    global current_lang
    init_colors()

    items = [t('actions'), t('tools'), t('exit')]
    menus = [menu_actions, menu_tools, None]
    sel = 0
    n = len(items)

    while True:
        try:
            h, w = stdscr.getmaxyx()
            stdscr.clear()
            stdscr.bkgd(' ', WHITE)

            # Заголовок
            title = t('title')
            stdscr.addstr(2, 4, title, ORANGE | curses.A_BOLD)
            stdscr.addstr(2, 4 + len(title) + 2, f"v{VERSION}", DIM)

            # Языки справа
            if current_lang == "ru":
                stdscr.addstr(2, w - 24, "[RU] EN HE", ORANGE | curses.A_BOLD)
            elif current_lang == "en":
                stdscr.addstr(2, w - 24, "RU [EN] HE", ORANGE | curses.A_BOLD)
            else:
                stdscr.addstr(2, w - 24, "RU EN [HE]", ORANGE | curses.A_BOLD)

            stdscr.addstr(4, 4, "─" * (w - 8), DIM)

            start_y = 6
            for i, item in enumerate(items):
                y = start_y + i
                if y >= h - 3:
                    break
                if i == sel:
                    stdscr.addstr(y, 4, " " * (w - 8), SELECTED)
                    stdscr.addstr(y, 6, f"› {item}", SELECTED | curses.A_BOLD)
                else:
                    stdscr.addstr(y, 6, f"  {item}", WHITE)

            hint = t('up_down')
            stdscr.addstr(h - 2, 4, hint, DIM)
            stdscr.refresh()

            key = stdscr.getch()

            # Языки: 1/2/3
            if key == ord('1'):
                current_lang = "ru"
                config["language"] = "ru"
                save_config()
                items = [t('actions'), t('tools'), t('exit')]
                continue
            elif key == ord('2'):
                current_lang = "en"
                config["language"] = "en"
                save_config()
                items = [t('actions'), t('tools'), t('exit')]
                continue
            elif key == ord('3'):
                current_lang = "he"
                config["language"] = "he"
                save_config()
                items = [t('actions'), t('tools'), t('exit')]
                continue

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
    current_lang = config.get("language", "ru")

    try:
        curses.wrapper(main_menu)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log(f"critical: {e}\n{traceback.format_exc()}")
        print(f"\n{t('error_occurred')}: {e}")
    finally:
        print(f"\n{t('goodbye')}\n")


if __name__ == "__main__":
    main()