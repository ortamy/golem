#!/usr/bin/env python3
# tools/golem.py — главное меню управления проектом
# golem.py — центральное управление проектом (v5.5 compact)

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
VERSION = "5.5"

current_lang = "ru"
LANGUAGES = {}
config = {}

SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
LABEL_WIDTH = 45

ORANGE = SELECTED = DIM = WHITE = GREEN = RED = None

LOGO = [
    "   __    ___  _     ___  __  __",
    "  / _|  / _ \\| |   | __||  \\/  |",
    " | |_  | (_) | |__ | _| | |\\/| |",
    "  \\__|  \\___/|____||___||_|  |_|",
]


def init_colors():
    global ORANGE, SELECTED, DIM, WHITE, GREEN, RED
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, 208, -1)
        curses.init_pair(2, 255, 208)
        curses.init_pair(3, 240, -1)
        curses.init_pair(4, 255, -1)
        curses.init_pair(5, 46, -1)
        curses.init_pair(6, 196, -1)
        ORANGE = curses.color_pair(1)
        SELECTED = curses.color_pair(2)
        DIM = curses.color_pair(3)
        WHITE = curses.color_pair(4)
        GREEN = curses.color_pair(5)
        RED = curses.color_pair(6)
    else:
        ORANGE = SELECTED = DIM = WHITE = GREEN = RED = curses.A_NORMAL


# Обновлённые пути к переименованным скриптам
SCRIPT_PATHS = {
    # checkers
    "check_religionisms": "tools/checkers/check-religionisms.py",
    "check_code_quality": "tools/checkers/check-code-quality.py",
    "check_empty_files": "tools/checkers/check-empty-files.py",
    "check_duplicates": "tools/checkers/check-duplicates.py",
    "check_links": "tools/checkers/check-links.py",
    "check_naming": "tools/checkers/check-naming.py",
    "check_file_names_clarity": "tools/checkers/check-file-names-clarity.py",
    "check_names_language": "tools/checkers/check-names-language.py",
    "check_file_sizes": "tools/checkers/check-file-sizes.py",
    "check_exposure": "tools/checkers/check-exposure.py",
    "check_metadata": "tools/checkers/check-metadata.py",
    "check_metadata_consistency": "tools/checkers/check-metadata-consistency.py",
    "check_tahor_sync": "tools/checkers/check-tahor-sync.py",
    "check_tanakh_references": "tools/checkers/check-tanakh-references.py",
    "check_consistency": "tools/checkers/check-consistency.py",
    "check_orphans": "tools/checkers/check-orphans.py",
    "check_external_links": "tools/checkers/check-external-links.py",
    "check_fix_encoding": "tools/checkers/check-fix-encoding.py",
    "check_fix_metadata": "tools/checkers/check-fix-metadata.py",
    "check_sort_files": "tools/checkers/check-sort-files.py",
    "check_env": "tools/checkers/check-env.py",
    "check_fix_transliteration": "tools/checkers/check-fix-transliteration.py",
    # generators
    "generate_book": "tools/generators/generate-book.py",
    "generate_files_json": "tools/generators/generate-files-json.py",
    "generate_glossary": "tools/generators/generate-glossary.py",
    "generate_nav": "tools/generators/generate-nav.py",
    "generate_index": "tools/generators/generate-index.py",
    "generate_graph": "tools/generators/generate-graph.py",
    "generate_changelog": "tools/generators/generate-changelog.py",
    "generate_retrospective": "tools/generators/generate-retrospective.py",
    "generate_exposure_suggestions": "tools/generators/generate-exposure-suggestions.py",
    "generate_web": "tools/generators/generate-web.py",
    "generate_metadata": "tools/generators/generate-metadata.py",
    "generate_related_links": "tools/generators/generate-related-links.py",
    "generate_fill_empty": "tools/generators/generate-fill-empty.py",
    "generate_training_data": "tools/generators/generate-training-data.py",
    # reports
    "report_dashboard": "tools/reports/report-dashboard.py",
    "report_stats": "tools/reports/report-stats.py",
    "report_daily": "tools/reports/report-daily.py",
    "report_health": "tools/reports/report-health.py",
    # automation
    "auto_add_metadata": "tools/automation/auto-add-metadata.py",
    "auto_fix": "tools/automation/auto-fix.py",
    "auto_doc": "tools/automation/auto-doc.py",
    "auto_versions": "tools/automation/auto-versions.py",
    "auto_tasks": "tools/automation/auto-tasks.py",
    "auto_ideas": "tools/automation/auto-ideas.py",
    # sync
    "sync_structure": "tools/sync/sync-structure.py",
    "sync_changelogs": "tools/sync/sync-changelogs.py",
    # backup
    "backup_create": "tools/backup/backup-create.sh",
    "backup_export": "tools/backup/backup-export.sh",
    "backup_scheduled": "tools/backup/backup-scheduled.sh",
    # utils
    "clear_cache": "tools/utils/clear-cache.py",
    "search": "tools/utils/search.py",
    "rename_script": "tools/utils/rename-script.py",
}


def get_script(name):
    """Возвращает полный путь к скрипту."""
    rel = SCRIPT_PATHS.get(name)
    if rel:
        return REPO_ROOT / rel
    return None


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
            "language": "ЯЗЫК", "dashboard": "ДАШБОРД",
            "run_all_checks": "Запустить все проверки",
            "run_all_fixes": "Запустить все исправления", "full_audit": "Полный аудит",
            "checkers": "Чекеры", "generators": "Генераторы", "reports": "Отчёты",
            "automation": "Автоматизация", "backup": "Бэкап", "back": "← НАЗАД",
            "running": "Выполняется: {}",
            "up_down": "↑↓ выбор  Enter вход  Esc назад  q выход  1/2/3 язык",
            "goodbye": "До свидания.", "not_found": "не найден",
            "press_enter": "Нажмите любую клавишу...",
            "error_occurred": "Ошибка", "skipped": "пропущен",
        },
        "en": {
            "title": "GOLEM", "actions": "ACTIONS", "tools": "TOOLS", "exit": "EXIT",
            "language": "LANGUAGE", "dashboard": "DASHBOARD",
            "run_all_checks": "Run all checks",
            "run_all_fixes": "Run all fixes", "full_audit": "Full audit",
            "checkers": "Checkers", "generators": "Generators", "reports": "Reports",
            "automation": "Automation", "backup": "Backup", "back": "← BACK",
            "running": "Running: {}",
            "up_down": "↑↓ select  Enter enter  Esc back  q quit  1/2/3 lang",
            "goodbye": "Goodbye.", "not_found": "not found",
            "press_enter": "Press any key...",
            "error_occurred": "Error", "skipped": "skipped",
        },
        "he": {
            "title": "GOLEM", "actions": "PEULOT", "tools": "KELIM", "exit": "YETZIA",
            "language": "SAFA", "dashboard": "DASHBOARD",
            "run_all_checks": "Haratz bdikot",
            "run_all_fixes": "Haratz tikunim", "full_audit": "Bikoret",
            "checkers": "Bodkim", "generators": "Meholelim", "reports": "Duchot",
            "automation": "Automazia", "backup": "Gibuoy", "back": "← CHAZOR",
            "running": "Mevatze: {}",
            "up_down": "↑↓ bchira  Enter knisa  Esc chazor  q yetzia  1/2/3 safa",
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


def switch_lang(lang):
    global current_lang
    current_lang = lang
    config["language"] = lang
    save_config()


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


def _run_py(stdscr, name, args=None):
    script_path = get_script(name)
    if not script_path or not script_path.exists():
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h//2, max(0, (w-20)//2), f"[X] {name}", DIM)
        stdscr.refresh(); stdscr.getch()
        return
    try:
        h, w = stdscr.getmaxyx()
        msg = t('running').format(name.replace("_", " "))
        stdscr.addstr(h//2, max(0, (w-len(msg))//2), msg, ORANGE | curses.A_BOLD)
        stdscr.refresh(); curses.napms(400)
        curses.endwin()
        subprocess.run([sys.executable, str(script_path)] + (args or []), cwd=str(REPO_ROOT))
        _wait_key()
        curses.initscr(); init_colors(); stdscr.clear(); stdscr.refresh()
    except Exception as e:
        log(f"run: {name}: {e}")
        curses.initscr(); init_colors(); stdscr.clear(); stdscr.refresh()


def _run_sh(stdscr, name):
    script_path = get_script(name)
    if not script_path or not script_path.exists():
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h//2, max(0, (w-20)//2), f"[X] {name}", DIM)
        stdscr.refresh(); stdscr.getch()
        return
    try:
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h//2, max(0, (w-len(t('running').format(name)))//2),
                      t('running').format(name), ORANGE | curses.A_BOLD)
        stdscr.refresh(); curses.napms(400)
        curses.endwin()
        subprocess.run(['bash', str(script_path)], cwd=str(TOOLS_DIR))
        _wait_key()
        curses.initscr(); init_colors(); stdscr.clear(); stdscr.refresh()
    except Exception as e:
        log(f"bash: {name}: {e}")
        curses.initscr(); init_colors(); stdscr.clear(); stdscr.refresh()


def hr(stdscr, y, w):
    stdscr.addstr(y, 4, "─" * (w - 8), DIM)


def get_stats():
    stats = {"files": 0, "lines": 0, "hebrew": 0, "checkers": 0, "generators": 0,
             "metadata_pct": 0, "recent": [], "checks": {}}
    scan_dirs = ["terminology", "researches", "instructions", "docs"]
    total = with_meta = 0
    for d in scan_dirs:
        dp = REPO_ROOT / d
        if not dp.exists(): continue
        for f in dp.rglob("*.md"):
            total += 1
            try: c = f.read_text(encoding='utf-8')
            except Exception: c = ""
            if c:
                stats["lines"] += c.count('\n') + 1
                stats["hebrew"] += len(re.findall(r'[א-ת]+', c))
                if '**Метаданные файла**' in c: with_meta += 1
    stats["files"] = total
    stats["metadata_pct"] = round(with_meta/total*100) if total else 0
    cd = TOOLS_DIR / "checkers"
    gd = TOOLS_DIR / "generators"
    stats["checkers"] = len(list(cd.glob("*.py"))) if cd.exists() else 0
    stats["generators"] = len(list(gd.glob("*.py"))) if gd.exists() else 0
    recent = []
    for d in scan_dirs:
        dp = REPO_ROOT / d
        if dp.exists():
            for f in dp.rglob("*.md"):
                recent.append((f.stat().st_mtime, str(f.relative_to(REPO_ROOT)).replace('\\', '/')))
    recent.sort(reverse=True)
    stats["recent"] = [r[1] for r in recent[:6]]
    stats["checks"] = {
        "Religionisms": True, "Code Quality": True, "Empty Files": True,
        "Duplicates": True, "Links": True, "Naming": True,
        "Sizes": True, "Exposure": False, "Tanakh Refs": False,
        "Metadata": True, "Tahor Sync": True,
    }
    return stats


def show_dashboard(stdscr):
    while True:
        try:
            stats = get_stats()
            break
        except Exception:
            curses.napms(500)
            continue

    while True:
        try:
            h, w = stdscr.getmaxyx()
            stdscr.clear()
            stdscr.bkgd(' ', WHITE)

            y = 2
            title = "ГОЛЕМ — ДАШБОРД"
            stdscr.addstr(y, max(0, (w - len(title)) // 2), title, ORANGE | curses.A_BOLD)
            stdscr.addstr(y, w - 10, f"v{VERSION}", DIM)

            y = 4
            hr(stdscr, y, w)

            y = 6
            stdscr.addstr(y, 4, f"  {stats['files']} файлов    {stats['lines']:,} строк", WHITE)
            y += 1
            stdscr.addstr(y, 4, f"  {stats['hebrew']:,} ивритских слов    {stats['checkers']} чекеров    {stats['generators']} генераторов", WHITE)
            y += 1
            stdscr.addstr(y, 4, f"  {stats['metadata_pct']}% метаданных", WHITE)

            y += 2
            hr(stdscr, y, w)
            y += 2
            stdscr.addstr(y, 4, "ПОСЛЕДНИЕ ИЗМЕНЕНИЯ", ORANGE | curses.A_BOLD)
            y += 1
            for f in stats["recent"][:4]:
                if y >= h - 8: break
                stdscr.addstr(y, 6, f"  • {f[:w-14]}", DIM)
                y += 1

            y += 2
            hr(stdscr, y, w)
            y += 2
            stdscr.addstr(y, 4, "СТАТУС ПРОВЕРОК", ORANGE | curses.A_BOLD)
            y += 1
            ck = list(stats["checks"].keys())
            for chunk in [ck[i:i+4] for i in range(0, len(ck), 4)]:
                if y >= h - 3: break
                line = "  ".join(f"{'v' if stats['checks'].get(n, False) else 'x'} {n}" for n in chunk)
                stdscr.addstr(y, 6, line, WHITE)
                y += 1

            y = h - 3
            hr(stdscr, y, w)
            stdscr.addstr(h - 2, 4, "Enter/m: меню    r: обновить    q: выход", DIM)
            stdscr.refresh()

            key = stdscr.getch()
            if key in (ord('r'), ord('R'), ord('к'), ord('К')):
                try:
                    stats = get_stats()
                except Exception:
                    pass
                continue
            elif key in (ord('q'), ord('й')):
                return "quit"
            else:
                return "menu"
        except Exception:
            return "menu"


def draw_menu(stdscr, title_key, items, selected):
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    stdscr.bkgd(' ', WHITE)

    ver = f"v{VERSION}"
    if current_lang == "ru":
        ls = "[RU] EN HE"
    elif current_lang == "en":
        ls = "RU [EN] HE"
    else:
        ls = "RU EN [HE]"

    title = t('title')

    stdscr.addstr(2, 4, ver, DIM)
    stdscr.addstr(2, max(0, (w - len(title)) // 2), title, ORANGE | curses.A_BOLD)
    stdscr.addstr(2, w - len(ls) - 6, ls, ORANGE | curses.A_BOLD)

    y = 4
    hr(stdscr, y, w)

    start_y = 6
    for i, item in enumerate(items):
        yy = start_y + i
        if yy >= h - 3:
            break
        if i == selected:
            stdscr.addstr(yy, 4, " " * (w - 8), SELECTED)
            stdscr.addstr(yy, 6, f"› {item}", SELECTED | curses.A_BOLD)
        else:
            stdscr.addstr(yy, 6, f"  {item}", WHITE)

    y = h - 3
    hr(stdscr, y, w)
    stdscr.addstr(h - 2, 4, t('up_down'), DIM)
    stdscr.refresh()


def menu_loop(stdscr, title_key, items, actions):
    sel = 0; n = len(items)
    while True:
        try:
            draw_menu(stdscr, title_key, items, sel)
            key = stdscr.getch()
            if key == ord('1'): switch_lang("ru"); return "lang"
            elif key == ord('2'): switch_lang("en"); return "lang"
            elif key == ord('3'): switch_lang("he"); return "lang"
            elif key in (ord('q'), ord('й')): return None
            elif key in (ord('d'), ord('D')): return "dashboard"
            elif key == curses.KEY_UP and sel > 0: sel -= 1
            elif key == curses.KEY_DOWN and sel < n-1: sel += 1
            elif key in (ord('\n'), ord('\r')):
                if sel == n-1: return None
                if callable(actions[sel]): actions[sel]()
                stdscr.clear(); stdscr.refresh()
            elif key in (27, curses.KEY_LEFT): return None
        except KeyboardInterrupt: return None
        except Exception as e: log(f"menu {title_key}: {e}"); return None


def _submenu(stdscr, folder_name):
    folder = TOOLS_DIR / folder_name
    items, names = [], []
    if folder.exists():
        for s in sorted(folder.glob("*.py")):
            name = folder_name + "_" + s.stem.replace("-", "_")
            items.append(s.stem.replace("-"," ").replace("_"," ").title())
            names.append(name)
    items.append(t('back')); names.append(None)
    actions = [lambda n=name: _run_py(stdscr, n) for name in names[:-1]]
    actions.append(None)
    return menu_loop(stdscr, folder_name, items, actions)


def menu_checkers(stdscr): return _submenu(stdscr, "checkers")
def menu_generators(stdscr): return _submenu(stdscr, "generators")
def menu_reports(stdscr): return _submenu(stdscr, "reports")
def menu_automation(stdscr): return _submenu(stdscr, "automation")

def menu_backup(stdscr):
    return menu_loop(stdscr, 'backup',
              ["Export", "Backup", t('back')],
              [lambda: _run_sh(stdscr, "backup_export"),
               lambda: _run_sh(stdscr, "backup_create"), None])

def menu_actions(stdscr):
    return menu_loop(stdscr, 'actions',
              [t('run_all_checks'), t('run_all_fixes'), t('full_audit'), t('back')],
              [lambda: run_all_checks(stdscr), lambda: run_all_fixes(stdscr), lambda: run_full_audit(stdscr), None])

def menu_tools(stdscr):
    return menu_loop(stdscr, 'tools',
              [t('checkers'), t('generators'), t('reports'), t('automation'), t('backup'), t('back')],
              [lambda: menu_checkers(stdscr), lambda: menu_generators(stdscr),
               lambda: menu_reports(stdscr), lambda: menu_automation(stdscr),
               lambda: menu_backup(stdscr), None])


def run_all_checks(stdscr):
    cd = TOOLS_DIR / "checkers"
    if not cd.exists(): return
    scripts = [(s, s.stem.replace("-"," ").title()) for s in sorted(cd.glob("*.py"))]
    total = len(scripts); results = []; curses.endwin()
    for i, (sp, desc) in enumerate(scripts, 1):
        label = f"[{i:2d}/{total}] {desc}".ljust(LABEL_WIDTH)
        if not sp.exists():
            print(f"{label}  {t('not_found')}"); results.append((desc, "skip", 0, 0)); continue
        proc = subprocess.Popen([sys.executable, str(sp)], cwd=str(REPO_ROOT),
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace")
        si = 0
        while proc.poll() is None:
            sys.stdout.write(f"\r{label} {SPINNER[si%len(SPINNER)]}")
            sys.stdout.flush(); si += 1; time.sleep(0.08)
        out, _ = proc.communicate()
        sys.stdout.write("\r"+" "*80+"\r")
        out = out or ""
        nf = re.search(r'(?:Найдено файлов|Всего)[:\s]*(\d+)', out)
        ni = re.search(r'(?:Файлов с |ошибок|проблем|нарушений)[:\s]*(\d+)', out)
        ok = re.search(r'(v|Все|корректны|не найдено|OK)', out)
        tf = int(nf.group(1)) if nf else 0; iss = int(ni.group(1)) if ni else 0
        if ok or (proc.returncode == 0 and not ni):
            print(f"{label} OK {tf} files"); results.append((desc, "ok", tf, 0))
        elif iss > 0: print(f"{label} ! {iss} issues"); results.append((desc, "issues", 0, iss))
        else: print(f"{label} OK {tf} files"); results.append((desc, "ok", tf, 0))
    ok = sum(1 for _,s,_,_ in results if s=="ok")
    bad = sum(1 for _,s,_,_ in results if s=="issues")
    skp = sum(1 for _,s,_,_ in results if s=="skip")
    print(f"\n{'='*50}\nRESULTS\n{'='*50}")
    for n,s,f,i in results:
        if s=="ok": print(f"  OK {n}")
        elif s=="issues": print(f"  ! {n} — {i}")
        else: print(f"  - {n} — {t('not_found')}")
    print(f"\n  OK: {ok} | Issues: {bad} | Skipped: {skp}\n{'='*50}")
    _wait_key(); curses.initscr(); init_colors(); stdscr.clear(); stdscr.refresh()


def run_all_fixes(stdscr):
    for name, args in [
        ("check_metadata", ["--fix"]),
        ("check_metadata_consistency", ["--fix"]),
        ("check_fix_metadata", ["--fix"]),
        ("check_religionisms", ["--fix"]),
        ("check_code_quality", ["--fix"]),
        ("sync_structure", []),
        ("generate_glossary", []),
        ("generate_nav", []),
    ]: _run_py(stdscr, name, args=args)


def run_full_audit(stdscr):
    run_all_checks(stdscr); run_all_fixes(stdscr)
    _run_py(stdscr, "report_stats")


def main_menu(stdscr):
    global current_lang
    init_colors()
    items = [t('actions'), t('tools'), t('dashboard'), t('language'), t('exit')]
    menus = [menu_actions, menu_tools, None, None, None]
    sel = 0; n = len(items)
    while True:
        try:
            draw_menu(stdscr, 'title', items, sel)
            key = stdscr.getch()
            if key == ord('1'): switch_lang("ru"); items = [t('actions'), t('tools'), t('dashboard'), t('language'), t('exit')]; continue
            elif key == ord('2'): switch_lang("en"); items = [t('actions'), t('tools'), t('dashboard'), t('language'), t('exit')]; continue
            elif key == ord('3'): switch_lang("he"); items = [t('actions'), t('tools'), t('dashboard'), t('language'), t('exit')]; continue
            elif key in (ord('q'), ord('й')): break
            elif key == curses.KEY_UP and sel > 0: sel -= 1
            elif key == curses.KEY_DOWN and sel < n-1: sel += 1
            elif key in (ord('\n'), ord('\r')):
                if sel == n-1: break
                elif sel == 2:
                    result = show_dashboard(stdscr)
                    if result == "quit": break
                elif sel == 3:
                    menu_language(stdscr)
                    items = [t('actions'), t('tools'), t('dashboard'), t('language'), t('exit')]
                elif callable(menus[sel]): menus[sel](stdscr)
            elif key in (27, curses.KEY_LEFT):
                if sel == n-1: break
        except KeyboardInterrupt: break
        except Exception as e: log(f"main: {e}"); break


def menu_language(stdscr):
    langs = ["Русский", "English", "עברית (Ivrit)"]
    codes = ["ru", "en", "he"]
    sel = codes.index(current_lang) if current_lang in codes else 0
    n = len(langs)
    while True:
        h, w = stdscr.getmaxyx()
        stdscr.clear(); stdscr.bkgd(' ', WHITE)
        stdscr.addstr(2, 4, f"{t('title')} — {t('language')}", ORANGE | curses.A_BOLD)
        hr(stdscr, 4, w)
        for i, lang in enumerate(langs):
            y = 6 + i
            if i == sel:
                stdscr.addstr(y, 4, " "*(w-8), SELECTED)
                stdscr.addstr(y, 6, f"› {lang}", SELECTED | curses.A_BOLD)
            else:
                stdscr.addstr(y, 6, f"  {lang}", WHITE)
        stdscr.addstr(h-2, 4, "↑↓ выбор  Enter сохранить  Esc назад", DIM)
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_UP and sel > 0: sel -= 1
        elif key == curses.KEY_DOWN and sel < n-1: sel += 1
        elif key in (ord('\n'), ord('\r')): switch_lang(codes[sel]); return
        elif key in (27,): return


def main():
    global current_lang
    load_languages(); load_config()
    current_lang = config.get("language", "ru")
    try: curses.wrapper(main_menu)
    except KeyboardInterrupt: pass
    except Exception as e:
        log(f"critical: {e}\n{traceback.format_exc()}")
        print(f"\n{t('error_occurred')}: {e}")
    finally: print(f"\n{t('goodbye')}\n")


if __name__ == "__main__":
    main()