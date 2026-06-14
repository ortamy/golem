#!/usr/bin/env python3
# tools/checkers/check-file-headers.py — проверка и автофикс заголовков файлов с путём

import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

SCAN_DIRS = ["tools", "ed", "web"]
CODE_EXTENSIONS = {".py", ".js", ".css", ".html", ".sh", ".ps1", ".yml", ".yaml"}
EXCLUDE_DIRS = {".venv", "node_modules", "__pycache__", "cache", ".git", "backup"}

HEADER_PATTERNS = {
    ".py": (r'^#!/usr/bin/env python3\n#\s*(\S+)\s*—\s*(.+)$', "# {path} — {desc}"),
    ".js": (r'^//\s*(\S+)\s*—\s*(.+)$', "// {path} — {desc}"),
    ".css": (r'^/\*\s*(\S+)\s*—\s*(.+?)\s*\*/$', "/* {path} — {desc} */"),
    ".html": (r'^<!--\s*(\S+)\s*—\s*(.+?)\s*-->$', "<!-- {path} — {desc} -->"),
    ".sh": (r'^#!/bin/bash\n#\s*(\S+)\s*—\s*(.+)$', "# {path} — {desc}"),
    ".ps1": (r'^#\s*(\S+)\s*—\s*(.+)$', "# {path} — {desc}"),
    ".yml": (r'^#\s*(\S+)\s*—\s*(.+)$', "# {path} — {desc}"),
    ".yaml": (r'^#\s*(\S+)\s*—\s*(.+)$', "# {path} — {desc}"),
}


def extract_header(filepath, ext):
    """Извлекает путь и описание из заголовка файла."""
    if ext not in HEADER_PATTERNS:
        return None, None, None
    
    pattern, _ = HEADER_PATTERNS[ext]
    
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None, None, None
    
    # Для .py и .sh — первые две строки
    if ext in (".py", ".sh"):
        lines = content.split("\n")[:2]
        text = "\n".join(lines).strip()
    else:
        lines = content.split("\n")[:1]
        text = lines[0].strip() if lines else ""
    
    match = re.match(pattern, text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip(), match.group(2).strip(), text
    
    return None, None, None


def get_actual_path(filepath):
    """Возвращает актуальный путь к файлу относительно корня."""
    return str(filepath.relative_to(ROOT)).replace("\\", "/")


def guess_description(filepath):
    """Пытается угадать описание файла по имени и местоположению."""
    name = filepath.stem
    parent = filepath.parent.name
    
    # Убираем префиксы
    for prefix in ["check-", "generate-", "report-", "auto-", "sync-", "backup-"]:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    
    # Заменяем дефисы на пробелы
    desc = name.replace("-", " ").replace("_", " ")
    
    return desc


def check_file(filepath):
    """Проверяет один файл на соответствие заголовка."""
    ext = filepath.suffix
    if ext not in HEADER_PATTERNS:
        return None
    
    header_path, header_desc, header_text = extract_header(filepath, ext)
    actual_path = get_actual_path(filepath)
    
    result = {
        "path": actual_path,
        "has_header": header_path is not None,
        "header_path": header_path,
        "header_desc": header_desc,
        "actual_path": actual_path,
    }
    
    if not header_path:
        result["issue"] = "missing"
        result["fix"] = "add"
    elif header_path != actual_path:
        result["issue"] = "wrong_path"
        result["fix"] = "update"
    else:
        result["issue"] = None
        result["fix"] = None
    
    return result


def fix_file(filepath, result):
    """Исправляет заголовок файла."""
    ext = filepath.suffix
    if ext not in HEADER_PATTERNS:
        return False
    
    _, template = HEADER_PATTERNS[ext]
    actual_path = result["actual_path"]
    desc = result.get("header_desc") or guess_description(filepath)
    
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    
    new_header = template.format(path=actual_path, desc=desc)
    
    # Убираем старый shebang и заголовок
    if ext == ".py":
        # Убираем shebang + старый заголовок (первые 2 строки)
        lines = content.split("\n")
        if lines[0].startswith("#!/usr/bin/env python3"):
            lines = lines[2:] if len(lines) > 1 and lines[1].startswith("# ") else lines[1:]
        elif lines[0].startswith("# "):
            lines = lines[1:]
        new_content = new_header + "\n" + "\n".join(lines)
    elif ext == ".sh":
        lines = content.split("\n")
        if lines[0].startswith("#!/bin/bash"):
            lines = lines[2:] if len(lines) > 1 and lines[1].startswith("# ") else lines[1:]
        elif lines[0].startswith("# "):
            lines = lines[1:]
        new_content = new_header + "\n" + "\n".join(lines)
    else:
        # Для остальных — первая строка
        lines = content.split("\n")
        if lines[0].startswith(("//", "/*", "<!--", "#")):
            lines = lines[1:]
        new_content = new_header + "\n" + "\n".join(lines)
    
    try:
        filepath.write_text(new_content, encoding="utf-8")
        return True
    except Exception:
        return False


def main():
    fix_mode = "--fix" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    print("🔍 Проверка заголовков файлов...\n")
    
    stats = {
        "total": 0,
        "ok": 0,
        "missing": 0,
        "wrong_path": 0,
        "fixed": 0,
        "errors": 0,
    }
    
    issues = []
    
    for scan_dir in SCAN_DIRS:
        dir_path = ROOT / scan_dir
        if not dir_path.exists():
            continue
        
        for ext in CODE_EXTENSIONS:
            for filepath in dir_path.rglob(f"*{ext}"):
                if any(exc in filepath.parts for exc in EXCLUDE_DIRS):
                    continue
                
                stats["total"] += 1
                result = check_file(filepath)
                
                if result is None:
                    continue
                
                if result["issue"] is None:
                    stats["ok"] += 1
                elif result["issue"] == "missing":
                    stats["missing"] += 1
                    issues.append((filepath, result))
                elif result["issue"] == "wrong_path":
                    stats["wrong_path"] += 1
                    issues.append((filepath, result))
    
    # Вывод результатов
    if issues:
        print(f"📋 Найдено проблем: {len(issues)}\n")
        
        if stats["missing"] > 0:
            print(f"❌ Без заголовка ({stats['missing']}):")
            for fp, r in issues:
                if r["issue"] == "missing":
                    print(f"   • {r['path']}")
            print()
        
        if stats["wrong_path"] > 0:
            print(f"⚠️ Неверный путь ({stats['wrong_path']}):")
            for fp, r in issues:
                if r["issue"] == "wrong_path":
                    print(f"   • Файл: {r['actual_path']}")
                    print(f"     В заголовке: {r['header_path']}")
                    print(f"     Описание: {r['header_desc']}")
            print()
    
    # Фикс
    if fix_mode and issues:
        print(f"🔧 Исправление...\n")
        for fp, r in issues:
            if fix_file(fp, r):
                stats["fixed"] += 1
                print(f"   ✅ {r['actual_path']}")
            else:
                stats["errors"] += 1
                print(f"   ❌ {r['actual_path']}")
        print()
    
    # Итог
    print(f"📊 Статистика:")
    print(f"   Всего файлов: {stats['total']}")
    print(f"   ✅ Корректных: {stats['ok']}")
    print(f"   ❌ Без заголовка: {stats['missing']}")
    print(f"   ⚠️ Неверный путь: {stats['wrong_path']}")
    
    if fix_mode:
        print(f"   🔧 Исправлено: {stats['fixed']}")
        if stats['errors']:
            print(f"   ❌ Ошибок: {stats['errors']}")
    else:
        if issues:
            print(f"\n💡 Для исправления: python tools/checkers/check-file-headers.py --fix")


if __name__ == "__main__":
    main()