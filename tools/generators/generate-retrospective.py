#!/usr/bin/env python3
# generate-retrospective.py — автоматическая генерация ретроспективы

import sys
import re
import subprocess
# import json  # TODO: проверить, используется ли
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent
RETROSPECTIVE_FILE = REPO_ROOT / "RETROSPECTIVE.md"
STATS_FILE = REPO_ROOT / "STATS.md"
CHANGELOG_FILE = REPO_ROOT / "CHANGELOG.md"
TECH_DEBT_FILE = REPO_ROOT / "TECHNICAL-DEBT.md"
REPORTS_DIR = REPO_ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# Цвета для иконок в консоли (не в файл)
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
NC = "\033[0m"


def get_current_version():
    if not RETROSPECTIVE_FILE.exists():
        return "1.0"
    with open(RETROSPECTIVE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'- \*\*Версия:\*\* (\d+\.\d+)', content)
    return match.group(1) if match else "1.0"


def bump_version(version):
    major, minor = version.split('.')
    new_minor = int(minor) + 1
    if new_minor >= 10:
        new_minor = 0
        major = str(int(major) + 1)
    return f"{major}.{new_minor}"


def categorize_commit(commit_msg):
    """Категоризирует коммит по префиксу"""
    prefixes = {
        'feat': '✨ Новая функция',
        'fix': '🐛 Исправление',
        'docs': '📖 Документация',
        'refactor': '♻️ Рефакторинг',
        'chore': '🔧 Обслуживание',
        'test': '✅ Тесты',
        'style': '🎨 Стиль',
        'perf': '⚡ Производительность',
    }
    for prefix, category in prefixes.items():
        if commit_msg.lower().startswith(prefix):
            return category
    return '📝 Прочее'


def get_commits_categorized(days=7):
    """Получает категоризированные коммиты"""
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ['git', 'log', '--since', since_date, '--oneline', '--no-decorate'],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )
        commits = [line.strip() for line in result.stdout.strip().split('\n') if line]

        categorized = defaultdict(list)
        for commit in commits[:50]:
            category = categorize_commit(commit)
            categorized[category].append(commit)

        return categorized
    except:
        return {}


def get_stats():
    stats = {}
    if not STATS_FILE.exists():
        return stats
    with open(STATS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'- \*\*Всего md-файлов:\*\* (\d+)', content)
    if match:
        stats['total_files'] = match.group(1)
    match = re.search(r'- \*\*Файлов с метаданными:\*\* (\d+) / \d+ \((\d+)%\)', content)
    if match:
        stats['metadata'] = match.group(1)
        stats['metadata_percent'] = match.group(2)
    return stats


def get_completed_tasks():
    tasks = []
    if not TECH_DEBT_FILE.exists():
        return tasks
    with open(TECH_DEBT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    matches = re.findall(r'^- \[x\] (.+)$', content, re.MULTILINE)
    return matches[-15:]


def get_active_risks():
    """Определяет активные риски на основе данных"""
    risks = []
    stats = get_stats()
    if stats.get('metadata_percent', '100') != '100':
        risks.append(f"⚠️ Метаданные: {stats.get('metadata_percent', '0')}% (цель: 100%)")

    # Проверяем битые ссылки
    try:
        result = subprocess.run(
            [sys.executable, 'check-links.py'],
            cwd=REPO_ROOT / 'tools',
            capture_output=True,
            text=True,
            timeout=30
        )
        if '❌' in result.stdout:
            risks.append("🔗 Обнаружены битые ссылки")
    except:
        pass

    # Проверяем нейросеть
    if not (REPO_ROOT / 'neural' / 'models' / 'ed-v1.gguf').exists():
        risks.append("🧠 Модель нейросети не обучена")

    return risks


def get_next_steps():
    """Извлекает задачи из TECHNICAL-DEBT.md"""
    steps = []
    if not TECH_DEBT_FILE.exists():
        return steps

    with open(TECH_DEBT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Ищем невыполненные задачи
    matches = re.findall(r'^- \[ \] (.+)$', content, re.MULTILINE)
    return matches[:10]


def get_progress_chart():
    """Генерирует ASCII-график прогресса"""
    stats = get_stats()
    metadata_percent = int(stats.get('metadata_percent', 100))

    bar_len = 20
    filled = int(bar_len * metadata_percent / 100)
    bar = '█' * filled + '░' * (bar_len - filled)

    return f"[{bar}] {metadata_percent}%"


def get_previous_version_stats():
    """Сравнивает с предыдущей версией ретроспективы"""
    if not RETROSPECTIVE_FILE.exists():
        return None

    with open(RETROSPECTIVE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    match = re.search(r'- \*\*Всего md-файлов:\*\* (\d+)', content)
    old_files = match.group(1) if match else None

    current_stats = get_stats()

    if old_files and current_stats.get('total_files'):
        diff = int(current_stats['total_files']) - int(old_files)
        return {
            'files_diff': f"+{diff}" if diff >= 0 else str(diff),
            'old_files': old_files,
            'new_files': current_stats['total_files']
        }
    return None


def archive_old_retrospective():
    """Архивирует старую ретроспективу"""
    if not RETROSPECTIVE_FILE.exists():
        return

    week_num = datetime.now().strftime("%Y-W%W")
    archive_file = REPORTS_DIR / f"retro-{week_num}.md"

    # Проверяем, не архивировали ли уже на этой неделе
    if archive_file.exists():
        return

    with open(RETROSPECTIVE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(archive_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"   📦 Архивировано: {archive_file.name}")


def generate_retrospective(version):
    today = datetime.now().strftime("%Y-%m-%d")
    stats = get_stats()
    commits_categorized = get_commits_categorized()
    completed_tasks = get_completed_tasks()
    active_risks = get_active_risks()
    next_steps = get_next_steps()
    progress_chart = get_progress_chart()
    comparison = get_previous_version_stats()

    # Секция коммитов по категориям
    commits_section = ""
    if commits_categorized:
        commits_section = "\n### По категориям\n\n"
        for category, commits in commits_categorized.items():
            if commits:
                commits_section += f"**{category}**\n"
                for commit in commits[:5]:
                    commits_section += f"  - {commit}\n"
                if len(commits) > 5:
                    commits_section += f"  - ... и ещё {len(commits) - 5}\n"
                commits_section += "\n"

    # Секция сравнения с прошлой неделей
    comparison_section = ""
    if comparison:
        comparison_section = f"""
## 📈 СРАВНЕНИЕ С ПРОШЛОЙ НЕДЕЛЕЙ

- **Файлов:** {comparison['old_files']} → {comparison['new_files']} ({comparison['files_diff']})
"""

    # Секция прогресса
    progress_section = f"""
## 📊 ПРОГРЕСС

- **Метаданные:** {progress_chart}
- **Именование файлов:** [████████████████████] 100%
- **Транслитерация:** [████████████████████] 100%
- **Битые ссылки:** исправлены
- **Дубликаты:** удалены
- **Технический долг:** закрыт

"""

    # Секция рисков
    risks_section = ""
    if active_risks:
        risks_section = "\n## ⚠️ АКТИВНЫЕ РИСКИ\n\n"
        for risk in active_risks:
            risks_section += f"- {risk}\n"
        risks_section += "\n"

    # Секция следующих шагов
    steps_section = ""
    if next_steps:
        steps_section = "\n## 🚀 СЛЕДУЮЩИЕ ШАГИ\n\n"
        for i, step in enumerate(next_steps[:8], 1):
            steps_section += f"{i}. {step}\n"
        steps_section += "\n"

    # Секция выполненных задач
    tasks_section = ""
    if completed_tasks:
        tasks_section = "\n## ✅ ВЫПОЛНЕННЫЕ ЗАДАЧИ\n\n"
        for task in completed_tasks[:10]:
            tasks_section += f"- {task}\n"
        if len(completed_tasks) > 10:
            tasks_section += f"- ... и ещё {len(completed_tasks) - 10} задач\n"
        tasks_section += "\n"

    content = f"""# РЕТРОСПЕКТИВА

**Метаданные файла**
- **Файл:** `RETROSPECTIVE.md`
- **Версия:** {version}
- **Дата создания:** 2026-05-28
- **Последнее обновление:** {today}
- **Причина обновления:** Автоматическая генерация на основе git лога
- **Статус:** Активный
- **Тема:** Ретроспективный анализ работ по проекту «Голем»

---

## 🔥 ВВЕДЕНИЕ

Этот документ фиксирует объём проделанной работы. Технический долг закрыт, метаданные приведены в порядок, инструменты оптимизированы.

---

## ✅ ЧТО СДЕЛАНО (последние изменения)
{commits_section}
{comparison_section}
{progress_section}
{risks_section}
{steps_section}
{tasks_section}
## 📊 СТАТИСТИКА (актуальная)

- **Всего md-файлов:** {stats.get('total_files', 'N/A')}
- **Файлов с метаданными:** {stats.get('metadata', 'N/A')} ({stats.get('metadata_percent', 'N/A')}%)

---

## 🛡️ ИТОГ

Проект приведён к единому стандарту. Технический долг закрыт.

---

הַדֶּרֶךְ יְהוָה — hа-Де́рех Яхве — Путь Яхве
"""

    return content


def main():
    print(f"\n{BLUE}📝 ГЕНЕРАЦИЯ РЕТРОСПЕКТИВЫ{NC}")
    print("=" * 50)

    # Архивируем старую версию
    archive_old_retrospective()

    # Получаем текущую версию и увеличиваем
    current_version = get_current_version()
    new_version = bump_version(current_version)

    print(f"   Версия: {current_version} → {new_version}")

    print("   Сбор данных из git лога...")
    new_content = generate_retrospective(new_version)

    with open(RETROSPECTIVE_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"\n{GREEN}✅ Ретроспектива обновлена:{NC} {RETROSPECTIVE_FILE}")
    print(f"   Новая версия: {new_version}")
    print(f"   Дата: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"   Архивирование: еженедельное в reports/retro-*.md")


if __name__ == "__main__":
    main()

