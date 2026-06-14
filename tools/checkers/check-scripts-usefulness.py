#!/usr/bin/env python3
# tools/checkers/check-scripts-usefulness.py — аудит полезности скриптов (v1.0)

import sys
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = ROOT / "tools"

# Папки которые проверяем
SCAN_DIRS = ["checkers", "generators", "reports", "automation", "sync", "utils"]

def analyze_script(filepath):
    """Анализирует Python-скрипт на полезность."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"error": "не читается"}
    
    result = {
        "path": str(filepath.relative_to(ROOT)).replace("\\", "/"),
        "lines": len(content.split("\n")),
        "has_shebang": content.startswith("#!/usr/bin/env python3"),
        "has_docstring": '"""' in content or "'''" in content,
        "has_main": 'if __name__' in content,
        "has_argparse": 'argparse' in content,
        "has_progress": 'progress_bar' in content,
        "has_fix": '--fix' in content,
        "has_dry_run": '--dry-run' in content,
        "has_verbose": '--verbose' in content,
        "has_rebuild": '--rebuild' in content,
        "imports": [],
        "uses_cache": 'cache' in content.lower() or 'CACHE' in content,
        "uses_db": 'sqlite' in content.lower() or '.db' in content,
        "uses_network": 'urllib' in content or 'requests' in content or 'fetch' in content,
        "scans_files": '.rglob(' in content or 'glob(' in content or 'listdir' in content,
        "multithreaded": 'ThreadPool' in content or 'concurrent' in content,
        "score": 0,
    }
    
    # Извлекаем импорты
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    result["imports"].append(node.module)
    except SyntaxError:
        pass
    
    # Считаем баллы полезности
    score = 0
    if result["has_shebang"]: score += 5
    if result["has_main"]: score += 10
    if result["has_argparse"]: score += 10
    if result["has_fix"]: score += 15  # автофикс — очень полезно
    if result["has_dry_run"]: score += 10
    if result["has_verbose"]: score += 5
    if result["has_rebuild"]: score += 5
    if result["has_progress"]: score += 5
    if result["scans_files"]: score += 10
    if result["multithreaded"]: score += 10
    if result["uses_cache"]: score += 5
    if result["lines"] > 50: score += 5
    if result["lines"] > 100: score += 5
    if result["lines"] > 300: score += 10
    if result["has_docstring"]: score += 3
    
    # Минусы
    if result["uses_network"]: score -= 5  # зависимость от интернета
    if result["lines"] < 10: score -= 10   # слишком короткий — вероятно недоделан
    
    result["score"] = max(0, score)
    
    # Оценка
    if score >= 50: result["verdict"] = "✅ Критичный"
    elif score >= 30: result["verdict"] = "👍 Полезный"
    elif score >= 15: result["verdict"] = "⚠️ Под вопросом"
    else: result["verdict"] = "❌ Бесполезный"
    
    return result


def main():
    print("🔍 Аудит полезности скриптов...\n")
    
    results = []
    
    for scan_dir in SCAN_DIRS:
        dir_path = TOOLS_DIR / scan_dir
        if not dir_path.exists():
            continue
        
        print(f"📁 {scan_dir}/")
        for py_file in sorted(dir_path.glob("*.py")):
            result = analyze_script(py_file)
            results.append(result)
            
            icon = result["verdict"][0]
            print(f"  {icon} {py_file.name:40} {result['score']:3} баллов  {result['verdict']}")
        print()
    
    # Статистика
    critical = [r for r in results if r["verdict"].startswith("✅")]
    useful = [r for r in results if r["verdict"].startswith("👍")]
    questionable = [r for r in results if r["verdict"].startswith("⚠️")]
    useless = [r for r in results if r["verdict"].startswith("❌")]
    
    print("=" * 60)
    print(f"📊 Итого:")
    print(f"   ✅ Критичных: {len(critical)}")
    print(f"   👍 Полезных: {len(useful)}")
    print(f"   ⚠️ Под вопросом: {len(questionable)}")
    print(f"   ❌ Бесполезных: {len(useless)}")
    print(f"   📝 Всего: {len(results)}")
    
    if useless:
        print(f"\n💀 Кандидаты на удаление:")
        for r in useless:
            print(f"   • {r['path']} — {r['score']} баллов")
    
    if questionable:
        print(f"\n⚠️ Требуют доработки:")
        for r in questionable:
            print(f"   • {r['path']} — {r['score']} баллов")
    
    print(f"\n🔧 Для критичных скриптов:")
    print(f"   • Имеют --fix: {sum(1 for r in critical if r['has_fix'])}/{len(critical)}")
    print(f"   • Имеют --dry-run: {sum(1 for r in critical if r['has_dry_run'])}/{len(critical)}")
    print(f"   • Многопоточные: {sum(1 for r in critical if r['multithreaded'])}/{len(critical)}")


if __name__ == "__main__":
    main()