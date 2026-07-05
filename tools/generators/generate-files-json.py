#!/usr/bin/env python3
# tools/generators/generate-files-json.py — генерация files.json для веб-интерфейса

import json
import sys
import re
from pathlib import Path

# Принудительно устанавливаем UTF-8 для stdout (Windows cp1251 fix)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).parent.parent.parent
WEB_DIR = REPO_ROOT / "products" / "website"
SCAN_DIRS = [
    ("content/terminology", "Терминология"),
    ("content/tanakh", "ТаНаХ"),
    ("content/bashah", "БаШаХ"),
    ("content/researches", "Исследования"),
    ("content/teachings", "Учения"),
    ("content/hebrew", "Изучение иврита"),
    ("content/paleo-hebrew", "Палео-иврит")
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
    'laws': 'Законы',
    'sports': 'Спорт',
    'technology': 'Технологии',
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
    'symbols': 'Символика',
    'slavery': 'Рабство',
    'sociology': 'Общество',
    'sport': 'Спорт',
    'systems': 'Системы',
    'tanakh': 'ТаНаХ',
    'adam': 'Адам',
    'anatomy': 'Анатомия',
    'brit-nissuin': 'Брит-нисуин',
    'creation': 'Творение',
    'elohim': 'Элоhим',
    'geography': 'География',
    'hitgalut': 'Хитгалут',
    'kehillah': 'Кеhилла',
    'kelim': 'Келим',
    'makom': 'Маком',
    'mikra': 'Микра',
    'moadim': 'Моадим',
    'ruach': 'Руах',
    'shedim': 'Шедим',
    'tamid': 'Тамид',
    # Подкатегории ruach
    'behemot': 'Беhемот',
    'chayot': 'Хайот',
    'cholim': 'Холим',
    'leshonot': 'Лешонот',
    'levushim': 'Левушим',
    'makot': 'Мако́т',
    'matachot': 'Матахот',
    'mavet': 'Мавет',
    'meshalim': 'Мешалим',
    'misparim': 'Миспарим',
    'seor': 'Сеор',
    'taharah': 'Таhара',
    'techiah': 'Техия',
    # Подкатегории shedim
    'avonot': 'Авонóт',
    'choshech': 'Хошех',
    'kerav': 'Керав',
    'nefilah': 'Нефила',
    'rodefim': 'Родефим',
    'ruchot-raot': 'Рухот раот',
    'shemot-shedim': 'Шемот шедим',
    'sheol': 'Шеол',
}

ICON_RULES = {
    "content/terminology": "scroll.png",
    "content/researches": "book.png",
    "content/teachings": "heart.png",
    "content/practices": "shield.png",
    "content/hebrew": "lamp.png",
    "content/exposed": "sword.png",
    "content/tanakh/books": "scrolls.png",
    "content/tanakh/persons": "default.png",
    "content/tanakh/events": "default.png",
    "content/bashah/books": "scrolls.png",
    "content/bashah/letters": "scales.png",
    "content/bashah/persons": "default.png",
    "content/bashah/events": "default.png",
    "content/bashah/teachings": "heart.png",
    "content/bashah/terminology": "scroll.png",
    "content/bashah/concepts": "anchor.png",
    "content/bashah/practices": "shield.png",
    "content/bashah/chronology": "hourglass.png",
    "content/bashah/manuscripts": "default.png",
    "content/bashah/geography": "default.png",
    "content/bashah/nevua": "torch.png",
    "content/tzel/adam": "vase.png",
    "content/tzel/brit-nissuin": "ring.png",
    "content/tzel/elohim": "default.png",
    "content/tzel/hitgalut": "alert.png",
    "content/tzel/kehillah": "default.png",
    "content/tzel/kelim": "hammer-and-chisel.png",
    "content/tzel/makom": "default.png",
    "content/tzel/mikra": "default.png",
    "content/tzel/moadim": "track.png",
    "content/tzel/ruach": "default.png",
    "content/tzel/shedim": "default.png",
    "content/tzel/tamid": "default.png",
}


def resolve_icon(rel_path):
    sorted_rules = sorted(ICON_RULES.items(), key=lambda x: -len(x[0]))
    for prefix, icon in sorted_rules:
        if rel_path.startswith(prefix):
            return icon
    return "default.png"


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
            "icon": resolve_icon(rel),
        })
    return files


def safe_print(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        cleaned = text.encode("ascii", errors="replace").decode("ascii")
        print(cleaned)


def generate():
    all_files = []
    for folder, label in SCAN_DIRS:
        dir_path = REPO_ROOT / folder
        if dir_path.exists():
            all_files.extend(walk_dir(dir_path, folder, label))

    WEB_DIR.mkdir(parents=True, exist_ok=True)
    out_path = WEB_DIR / "files.json"
    out_path.write_text(json.dumps(all_files, ensure_ascii=False, indent=2), encoding="utf-8")
    safe_print(f"[OK] {out_path} — {len(all_files)} файлов")

    icon_count = {}
    for f in all_files:
        icon = f.get("icon", "default.png")
        icon_count[icon] = icon_count.get(icon, 0) + 1
    safe_print(f"\n[STATS] Статистика иконок:")
    for icon, count in sorted(icon_count.items(), key=lambda x: -x[1]):
        safe_print(f"  {icon}: {count}")
    default_count = icon_count.get("default.png", 0)
    safe_print(f"\n[OK] Файлов с иконками: {len(all_files) - default_count}")
    safe_print(f"[OK] default.png: {default_count}")


if __name__ == "__main__":
    generate()