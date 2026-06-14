#!/usr/bin/env python3
# tools/generators/generate-files-json.py — генерация files.json для веб-интерфейса
# generate-files-json.py — генерирует files.json для статического веб-интерфейса

import json
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import REPO_ROOT

WEB_DIR = REPO_ROOT / "web"
SCAN_DIRS = [
    ("content/terminology", "Терминология"),
    ("content/tanakh", "ТаНаХ"),
    ("content/bashah", "БаШаХ"),
    ("content/researches", "Исследования"),
    ("content/teachings", "Учения"),
    ("content/learn-hebrew", "Изучение иврита"),
]
IGNORE_FILES = {"README.md", "STRUCTURE.md", "GLOSSARY.md", "CHANGELOG.md"}

SUBCATEGORY_LABELS = {
    'archive': 'Архив',
    'books': 'Книги',
    'chronology': 'Хронология',
    'companies': 'Компании',
    'concepts': 'Понятия',
    'economy': 'Экономика',
    'events': 'События',
    'history': 'История',
    'language': 'Язык',
    'manuscripts': 'Рукописи',
    'media': 'Медиа',
    'medicine': 'Медицина',
    'names': 'Имена',
    'persons': 'Личности',
    'practices': 'Практики',
    'psychology': 'Психология',
    'roman-law': 'Римское право',
    'science': 'Наука',
    'simvolika': 'Символика',
    'slavery': 'Рабство',
    'sociology': 'Общество',
    'sport': 'Спорт',
    'systems': 'Системы',
    'tanakh': 'ТаНаХ',
}


def extract_title(content):
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    if match:
        title = match.group(1)
        title = re.sub(r'[\U0001F000-\U0001FFFF\u2600-\u27BF\uFE00-\uFEFF\u200D\uFE0F]', '', title)
        return title.strip()[:80]
    return ''


def extract_topic(content):
    for line in content.split("\n"):
        if "**Тема:**" in line:
            return line.split("**Тема:**")[1].strip()[:100]
    return ""


def extract_related(content):
    related = []
    capture = False
    for line in content.split("\n"):
        if "**Связанные файлы:**" in line:
            capture = True
            continue
        if capture:
            if line.strip().startswith("---") or line.strip() == "":
                if related:
                    break
                continue
            for match in line.split("`")[1::2]:
                if match and match not in related:
                    related.append(match)
    return related


def walk_dir(dir_path, base_folder, label):
    files = []
    for entry in sorted(dir_path.rglob("*.md")):
        if entry.name in IGNORE_FILES:
            continue
        rel = entry.relative_to(REPO_ROOT).as_posix()
        content = entry.read_text(encoding="utf-8", errors="ignore")
        parts = rel.split("/")
        subcategory = ""
        if len(parts) > 3:
            subcategory = SUBCATEGORY_LABELS.get(parts[2], parts[2])
        files.append({
            "path": rel,
            "title": extract_title(content) or entry.stem.replace("-", " "),
            "topic": extract_topic(content),
            "category": label,
            "subcategory": subcategory,
            "related": extract_related(content),
        })
    return files


def generate():
    all_files = []
    for folder, label in SCAN_DIRS:
        dir_path = REPO_ROOT / folder
        if dir_path.exists():
            all_files.extend(walk_dir(dir_path, folder, label))

    WEB_DIR.mkdir(parents=True, exist_ok=True)
    out_path = WEB_DIR / "files.json"
    out_path.write_text(json.dumps(all_files, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {out_path} — {len(all_files)} файлов")


if __name__ == "__main__":
    generate()