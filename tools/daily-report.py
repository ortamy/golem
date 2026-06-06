#!/usr/bin/env python3
# daily-report.py — ежедневный отчёт о состоянии проекта

import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from progress import show_progress, finish_progress

REPO_ROOT = Path(__file__).parent.parent
REPORTS_DIR = REPO_ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def get_git_changes(days=1):
    """Получает изменения за последние N дней"""
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ['git', 'log', '--since', since_date, '--oneline', '--no-decorate'],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        commits = [line.strip() for line in result.stdout.strip().split('\n') if line]
        return commits
    except:
        return []


def get_new_files(days=1):
    """Находит новые файлы за последние N дней"""
    since_date = datetime.now() - timedelta(days=days)
    new_files = []
    
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
        if mtime > since_date:
            new_files.append(md_file.relative_to(REPO_ROOT))
    
    return new_files


def get_stats():
    """Получает статистику из STATS.md"""
    stats_file = REPO_ROOT / "STATS.md"
    if not stats_file.exists():
        return {}
    
    with open(stats_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    import re
    stats = {}
    
    match = re.search(r'- \*\*Всего md-файлов:\*\* (\d+)', content)
    if match:
        stats['total_files'] = match.group(1)
    
    match = re.search(r'- \*\*Файлов с метаданными:\*\* (\d+) / \d+ \((\d+)%\)', content)
    if match:
        stats['metadata'] = f"{match.group(1)} ({match.group(2)}%)"
    
    return stats


def generate_report():
    """Генерирует ежедневный отчёт"""
    today = datetime.now().strftime("%Y-%m-%d")
    commits = get_git_changes(1)
    new_files = get_new_files(1)
    stats = get_stats()
    
    report = f"""# ЕЖЕДНЕВНЫЙ ОТЧЁТ

**Дата:** {today}
**Время:** {datetime.now().strftime("%H:%M:%S")}

---

## 📊 СТАТИСТИКА ПРОЕКТА

- **Всего файлов:** {stats.get('total_files', 'N/A')}
- **Метаданные:** {stats.get('metadata', 'N/A')}

---

## 📝 ИЗМЕНЕНИЯ ЗА ПОСЛЕДНИЕ 24 ЧАСА

**Коммитов:** {len(commits)}

"""
    if commits:
        for commit in commits[:10]:
            report += f"- {commit}\n"
        if len(commits) > 10:
            report += f"- ... и ещё {len(commits) - 10} коммитов\n"
    else:
        report += "- Нет коммитов\n"
    
    report += f"\n**Новых файлов:** {len(new_files)}\n\n"
    if new_files:
        for f in new_files[:15]:
            report += f"- {f}\n"
        if len(new_files) > 15:
            report += f"- ... и ещё {len(new_files) - 15} файлов\n"
    
    report += """
---

## 🔧 РЕКОМЕНДАЦИИ

"""
    if len(commits) == 0:
        report += "- ⚠️ Нет активности в репозитории. Рекомендуется сделать коммит.\n"
    
    report += f"""
---
*Отчёт сгенерирован автоматически*
"""
    
    return report


def main():
    print("\n📊 ГЕНЕРАЦИЯ ЕЖЕДНЕВНОГО ОТЧЁТА")
    print("=" * 50)
    
    report = generate_report()
    
    # Сохраняем отчёт
    today = datetime.now().strftime("%Y%m%d")
    report_file = REPORTS_DIR / f"daily-report-{today}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Отчёт сохранён: {report_file}")
    
    # Показываем краткую сводку
    print("\n📊 КРАТКАЯ СВОДКА:")
    print("-" * 30)
    
    import re
    commits_match = re.search(r'\*\*Коммитов:\*\* (\d+)', report)
    if commits_match:
        print(f"   Коммитов: {commits_match.group(1)}")
    
    files_match = re.search(r'\*\*Новых файлов:\*\* (\d+)', report)
    if files_match:
        print(f"   Новых файлов: {files_match.group(1)}")
    
    print(f"\n📄 Полный отчёт: {report_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())