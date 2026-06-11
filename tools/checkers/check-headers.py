#!/usr/bin/env python3
# tools/checkers/check-headers.py — проверка формата заголовков H1

import re
import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT = ROOT / "content"
CSV_OUT = ROOT / "tools" / "cache" / "headers-violations.csv"


def has_hebrew(text):
    return bool(re.search(r'[\u0590-\u05FF]', text))


def extract_hebrew_from_content(content):
    """Извлечь первое ивритское слово из текста (не из заголовка)."""
    lines = content.split("\n")
    for line in lines:
        if line.startswith("#"):
            continue
        # Ищем иврит в скобках: (נֶפֶשׁ)
        match = re.search(r'\(([\u0590-\u05FF]{2,}(?:\s+[\u0590-\u05FF]+)*)\)', line)
        if match:
            return match.group(1).strip()
        # Ищем отдельное ивритское слово
        match = re.search(r'[\u0590-\u05FF]{2,}', line)
        if match:
            return match.group(0).strip()
    return ""


def extract_hebrew_from_filename(filepath):
    """Попытаться извлечь иврит из имени файла."""
    name = filepath.stem
    return ""


def check_file(filepath):
    content = filepath.read_text(encoding="utf-8", errors="ignore")
    lines = content.split("\n")
    
    # Найти первый H1
    h1 = ""
    h1_line = 0
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            h1 = line[2:].strip()
            h1_line = i
            break
    
    if not h1:
        return None, "нет H1", "", h1_line
    
    # Проверить формат
    has_emoji = bool(re.match(r'^[🌀🔥💡🛡️⚔️🧠🏛️📜✡️🔤🌱📐❓🎯📊🕸️🕌🔍🧩⏳❤️💻👥🔄🗺️📋✅🚫📖💱🇬🇧🇬🇷🏷️🌹🕋🙏✂️👑💰🌬️🕊️🛣️🇪🇬🗼🇷🇺⛪🔥📜]', h1))
    has_hebrew_in_title = has_hebrew(h1)
    
    if has_hebrew_in_title and "—" in h1:
        return None, "OK", h1, h1_line
    
    # Проблема: нет иврита в заголовке
    hebrew_word = extract_hebrew_from_content(content)
    
    return {
        "path": str(filepath.relative_to(ROOT)).replace("\\", "/"),
        "current_h1": h1,
        "h1_line": h1_line + 1,
        "suggested_hebrew": hebrew_word,
        "issue": "no_hebrew" if not has_hebrew_in_title else "no_dash_format",
    }, "нарушение", h1, h1_line


def progress_bar(current, total, start_time, width=40):
    """Кастомный прогресс-бар без rich."""
    pct = current / total if total > 0 else 0
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    
    elapsed = time.time() - start_time
    if current > 0:
        eta = (elapsed / current) * (total - current)
        eta_str = f"{eta:.0f}с" if eta < 60 else f"{eta/60:.1f}м"
    else:
        eta_str = "..."
    
    sys.stdout.write(f"\r  [{bar}] {pct*100:.1f}%  {current}/{total}  осталось: {eta_str}  ")
    sys.stdout.flush()


def scan():
    violations = []
    total = 0
    start_time = time.time()
    
    # Собрать все файлы
    all_files = []
    for md_file in sorted(CONTENT.rglob("*.md")):
        if md_file.name in ["README.md", "STRUCTURE.md", "GLOSSARY.md", "CHANGELOG.md"]:
            continue
        all_files.append(md_file)
    
    total = len(all_files)
    print(f"\n📊 Проверка заголовков H1...")
    print(f"   Файлов: {total}\n")
    
    for i, md_file in enumerate(all_files, 1):
        progress_bar(i, total, start_time)
        
        result, status, h1, line = check_file(md_file)
        if status == "нарушение":
            violations.append(result)
    
    sys.stdout.write("\r" + " " * 80 + "\r")
    
    ok_count = total - len(violations)
    pct = (ok_count / total * 100) if total > 0 else 0
    
    print(f"📊 Проверено: {total} файлов за {time.time() - start_time:.1f}с")
    print(f"❌ Нарушений: {len(violations)}")
    print(f"✅ Правильных: {ok_count} ({pct:.1f}%)")
    
    if violations:
        CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
        with open(CSV_OUT, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["path", "current_h1", "h1_line", "suggested_hebrew", "issue"])
            writer.writeheader()
            for v in violations:
                writer.writerow(v)
        
        print(f"\n📄 CSV создан: {CSV_OUT}")
        print(f"   Колонки: path, current_h1, h1_line, suggested_hebrew, issue")
        print(f"\n   issue=no_hebrew: в заголовке нет иврита")
        print(f"   issue=no_dash_format: есть иврит но нет разделителя «—»")
        
        # Показать первые 10
        print(f"\n🔍 Первые 10 нарушений:")
        for v in violations[:10]:
            print(f"  {v['path']}")
            print(f"    Текущий: {v['current_h1'][:80]}")
            if v['suggested_hebrew']:
                print(f"    Иврит: {v['suggested_hebrew']}")
            print()
    else:
        print("\n✅ Все заголовки в правильном формате.")


if __name__ == "__main__":
    scan()