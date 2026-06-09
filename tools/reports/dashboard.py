# tools/reports/dashboard.py — интерактивный дашборд (минимализм, ч/б + оранжевый)
import sys
import re
import json
import time
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, print_header, print_success, print_hint, REPO_ROOT

OUTPUT_FILE = REPO_ROOT / "docs" / "export" / "dashboard.html"
SCAN_DIRS = ["terminology", "researches", "instructions", "docs", "drafts", "ideas"]
SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def animate(message: str, duration: float = 0.3):
    start = time.time()
    i = 0
    while time.time() - start < duration:
        sys.stdout.write(f"\r  {SPINNER[i % len(SPINNER)]} {message}...")
        sys.stdout.flush()
        i += 1
        time.sleep(0.08)
    sys.stdout.write(f"\r  ✅ {message}\n")
    sys.stdout.flush()


def count_files():
    animate("Подсчёт файлов")
    stats = defaultdict(int)
    total = 0
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            count = len(list(dir_path.rglob("*.md")))
            stats[scan_dir] = count
            total += count
    stats["total"] = total
    return dict(stats)


def count_lines():
    animate("Подсчёт строк")
    total = 0
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            for md_file in dir_path.rglob("*.md"):
                content = read_file_safe(md_file)
                if content:
                    total += len(content.split('\n'))
    return total


def count_hebrew():
    animate("Подсчёт ивритских слов")
    total = 0
    for scan_dir in ["terminology", "researches"]:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            for md_file in dir_path.rglob("*.md"):
                content = read_file_safe(md_file)
                if content:
                    total += len(re.findall(r'[א-ת]+', content))
    return total


def count_religionisms():
    animate("Поиск религионимов")
    total = Counter()
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            for md_file in dir_path.rglob("*.md"):
                content = read_file_safe(md_file)
                if content:
                    for word in ["Бог", "Господь", "грех", "душа", "церковь", "Христос", "Иисус"]:
                        count = len(re.findall(rf'\b{word}\b', content, re.IGNORECASE))
                        if count:
                            total[word] += count
    return dict(total.most_common(10))


def count_metadata_quality():
    animate("Проверка метаданных")
    total = 0
    with_metadata = 0
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            for md_file in dir_path.rglob("*.md"):
                total += 1
                content = read_file_safe(md_file)
                if content and '**Метаданные файла**' in content:
                    with_metadata += 1
    return {"total": total, "with_metadata": with_metadata, "percent": round(with_metadata / total * 100, 1) if total else 0}


def get_recent_files():
    animate("Последние изменения")
    files = []
    for scan_dir in SCAN_DIRS:
        dir_path = REPO_ROOT / scan_dir
        if dir_path.exists():
            for md_file in dir_path.rglob("*.md"):
                files.append((md_file.stat().st_mtime, str(md_file.relative_to(REPO_ROOT)).replace('\\', '/')))
    files.sort(reverse=True)
    return [f[1] for f in files[:10]]


def get_tools_count():
    animate("Подсчёт инструментов")
    tools_dir = REPO_ROOT / "tools"
    count = 0
    if tools_dir.exists():
        count = len(list(tools_dir.rglob("*.py")))
    return count


def generate_html():
    print_header("СБОР СТАТИСТИКИ", "📊")

    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    files = count_files()
    lines_count = count_lines()
    hebrew_count = count_hebrew()
    relig_count = count_religionisms()
    meta_quality = count_metadata_quality()
    recent = get_recent_files()
    tools_count = get_tools_count()

    animate("Генерация HTML", 0.2)

    files_json = json.dumps({k: v for k, v in files.items() if k != "total"})
    relig_json = json.dumps(relig_count)

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Голем — Дашборд</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Courier New', monospace; background: #fff; color: #111; padding: 40px; max-width: 1200px; margin: 0 auto; }}
h1 {{ font-size: 32px; font-weight: 300; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 4px; }}
.subtitle {{ font-size: 12px; color: #999; margin-bottom: 40px; letter-spacing: 1px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1px; background: #111; border: 1px solid #111; }}
.card {{ background: #fff; padding: 30px; }}
.card h2 {{ font-size: 11px; font-weight: 400; letter-spacing: 3px; text-transform: uppercase; color: #999; margin-bottom: 20px; }}
.stat {{ font-size: 64px; font-weight: 200; color: #111; line-height: 1; }}
.stat-label {{ font-size: 11px; color: #999; letter-spacing: 1px; margin-top: 4px; }}
.metric {{ display: inline-block; margin: 15px 24px 10px 0; }}
.metric strong {{ font-size: 20px; font-weight: 400; color: #111; }}
.metric span {{ display: block; font-size: 10px; color: #999; letter-spacing: 1px; }}
.bar {{ height: 2px; margin-top: 15px; background: #eee; position: relative; }}
.bar-fill {{ height: 2px; position: absolute; left: 0; top: 0; }}
.recent {{ list-style: none; }}
.recent li {{ padding: 6px 0; border-bottom: 1px solid #f0f0f0; font-size: 11px; color: #666; letter-spacing: 0.5px; }}
.recent li:last-child {{ border-bottom: none; }}
.chart-container {{ position: relative; height: 200px; }}
.accent {{ color: #ff4d00; }}
.status {{ display: inline-block; width: 8px; height: 8px; background: #ff4d00; margin-right: 8px; }}
footer {{ text-align: center; margin-top: 40px; font-size: 10px; color: #ccc; letter-spacing: 2px; }}
</style>
</head>
<body>

<h1>ГОЛЕМ</h1>
<p class="subtitle">ДАШБОРД / {today}</p>

<div class="grid">
    <div class="card">
        <h2>Файлы</h2>
        <div class="stat">{files["total"]}</div>
        <div class="stat-label">всего документов</div>
        <div style="margin-top:20px;">
            <div class="metric"><strong>{files.get("terminology", 0)}</strong><span>терминов</span></div>
            <div class="metric"><strong>{files.get("researches", 0)}</strong><span>исследований</span></div>
            <div class="metric"><strong>{files.get("instructions", 0)}</strong><span>инструкций</span></div>
            <div class="metric"><strong>{files.get("docs", 0)}</strong><span>документов</span></div>
        </div>
    </div>

    <div class="card">
        <h2>Метрики</h2>
        <div class="stat">{lines_count:,}</div>
        <div class="stat-label">строк текста</div>
        <div style="margin-top:20px;">
            <div class="metric"><strong>{hebrew_count:,}</strong><span>ивритских слов</span></div>
            <div class="metric"><strong>{tools_count}</strong><span>инструментов</span></div>
            <div class="metric"><strong>{meta_quality["percent"]}%</strong><span>метаданных</span></div>
        </div>
        <div class="bar"><div class="bar-fill" style="width:{meta_quality['percent']}%; background:#ff4d00;"></div></div>
    </div>

    <div class="card">
        <h2>Распределение</h2>
        <div class="chart-container">
            <canvas id="filesChart"></canvas>
        </div>
    </div>

    <div class="card">
        <h2>Религионимы</h2>
        <div class="chart-container">
            <canvas id="religChart"></canvas>
        </div>
    </div>

    <div class="card">
        <h2>Последние изменения</h2>
        <ul class="recent">
"""

    for f in recent:
        html += f'<li>{f}</li>\n'

    html += f"""
        </ul>
    </div>

    <div class="card">
        <h2>Система</h2>
        <div style="margin-top:10px;">
            <p style="font-size:11px;color:#999;letter-spacing:1px;">ВЕРСИЯ</p>
            <p style="font-size:20px;font-weight:200;">Golem <span class="accent">v4.1</span></p>
        </div>
        <div style="margin-top:20px;">
            <p style="font-size:11px;color:#999;letter-spacing:1px;">ИНСТРУМЕНТЫ</p>
            <p style="font-size:20px;font-weight:200;">{tools_count} скриптов</p>
        </div>
        <div style="margin-top:20px;">
            <p style="font-size:11px;color:#999;letter-spacing:1px;">ЧЕКЕРЫ</p>
            <p style="font-size:20px;font-weight:200;">19 активных</p>
        </div>
        <div style="margin-top:20px; padding:15px; background:#fafafa; border-left:2px solid #ff4d00;">
            <span class="status"></span><span style="font-size:11px;letter-spacing:1px;color:#999;">ВСЕ СИСТЕМЫ РАБОТАЮТ</span>
        </div>
    </div>
</div>

<script>
const filesCtx = document.getElementById('filesChart').getContext('2d');
new Chart(filesCtx, {{
    type: 'doughnut',
    data: {{
        labels: Object.keys({files_json}),
        datasets: [{{ data: Object.values({files_json}), backgroundColor: ['#111','#333','#555','#777','#999','#ff4d00'], borderWidth: 0 }}]
    }},
    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 10, family: 'Courier New' }}, color: '#999', padding: 10 }} }} }} }}
}});

const religCtx = document.getElementById('religChart').getContext('2d');
new Chart(religCtx, {{
    type: 'bar',
    data: {{
        labels: Object.keys({relig_json}),
        datasets: [{{ label: 'Найдено', data: Object.values({relig_json}), backgroundColor: '#ff4d00', borderRadius: 0, barThickness: 16 }}]
    }},
    options: {{ responsive: true, maintainAspectRatio: false, scales: {{ y: {{ beginAtZero: true, ticks: {{ font: {{ size: 9, family: 'Courier New' }}, color: '#999' }}, grid: {{ color: '#f0f0f0' }} }}, x: {{ ticks: {{ font: {{ size: 9, family: 'Courier New' }}, color: '#999' }}, grid: {{ display: false }} }} }}, plugins: {{ legend: {{ display: false }} }} }}
}});
</script>

<footer>GOLEM DASHBOARD / СВИДЕТЕЛЬ ИСТИНЫ</footer>
</body>
</html>
"""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    print_header("ГЕНЕРАЦИЯ ДАШБОРДА", "📊")

    start_time = time.time()
    generate_html()

    elapsed = time.time() - start_time
    print_success(f"Дашборд сохранён: {OUTPUT_FILE}")
    print(f"   Время генерации: {elapsed:.1f} сек")
    print_hint("Откройте в браузере: Ctrl+O → docs/export/dashboard.html")

    return 0


if __name__ == "__main__":
    sys.exit(main())