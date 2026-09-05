#!/usr/bin/env python3
"""Генерирует навигацию документации docs/ из фактического состояния ФС.

Выход:
  docs/INDEX.md                    — индекс всех разделов и файлов;
  docs/<раздел>/README.md          — обложка раздела (только где README отсутствует);
  docs/02-MANAGEMENT/STATS.md      — авто-статистика корпуса.

Идемпотентен: повторный запуск не меняет файлы.
Функции render_* импортируются tools/check-docs.py для сверки «файл = эталон».
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX_PATH = DOCS / "INDEX.md"
STATS_PATH = DOCS / "02-MANAGEMENT" / "STATS.md"
SNAPSHOT = "2026-09-05"

# Короткие подписи разделов для оглавления. Если раздела нет в словаре —
# используется имя папки как есть.
TITLES = {
    "00-START": "вход в проект",
    "01-ARCHITECTURE": "архитектура",
    "02-MANAGEMENT": "управление проектом",
    "03-AI": "AI-агенты и модели",
    "04-STANDARD": "стандарты и терминология",
    "05-DICTIONARIES": "словари языковых подмен",
    "06-METHODOLOGY": "методология и разоблачение подмен",
    "07-MECHANICS": "механика 22 букв палео-иврита",
    "08-AUDITS": "аудиты, чекеры и отчёты качества",
    "09-GUIDES": "технические руководства",
    "10-DESIGN": "дизайн-система и иконки",
    "11-PRODUCTS": "документация продуктов",
    "12-TEMPLATES": "шаблоны документов",
    "13-REPORTS": "отчёты",
    "14-APPS": "документы приложений",
    "99-HISTORICAL": "архив (исторические документы)",
}

PURPOSE_KEYS = ("Назначение", "Назначение документа", "Тема", "Описание", "Цель")
STATUS_VALUES = {"Активный", "Исторический", "Заготовка", "Концепция"}

_META_VALUE = re.compile(r"^-\s*\*{0,2}([^*:：]+?)\*{0,2}\s*[:：]\s*(.+)$")
_H1 = re.compile(r"^#\s+(.+)$")
_STRIP = re.compile(r"[*`_>]")
_EMOJI = re.compile(r"^[\W_]+")


def plural(n: int, one: str, few: str, many: str) -> str:
    n10, n100 = n % 10, n % 100
    if n10 == 1 and n100 != 11:
        return one
    if 2 <= n10 <= 4 and not 12 <= n100 <= 14:
        return few
    return many


def folder_title(name: str) -> str:
    return TITLES.get(name, name)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def metadata(path: Path) -> dict:
    """Достаёт из шапки файла поля: файл, статус, версию и назначение."""
    meta: dict = {"file": "", "status": "", "version": "", "purpose": "", "h1": ""}
    try:
        lines = read_text(path).splitlines()
    except (OSError, UnicodeDecodeError):
        return meta
    for line in lines[:60]:
        if not meta["h1"]:
            m = _H1.match(line)
            if m:
                meta["h1"] = _STRIP.sub("", m.group(1)).strip()
        m = _META_VALUE.match(line)
        if not m:
            continue
        key = m.group(1).strip()
        value = _STRIP.sub("", m.group(2)).strip()
        if not value or value in {"ожидает", "—"}:
            continue
        if key in ("Файл", "File"):
            meta["file"] = value
        elif key == "Статус" and not meta["status"]:
            meta["status"] = value
        elif key == "Версия" and not meta["version"]:
            meta["version"] = value
        elif key in PURPOSE_KEYS and not meta["purpose"]:
            meta["purpose"] = value
    return meta


def annotation(path: Path) -> str:
    """Одна строка-аннотация файла: назначение из метаданных или первый H1."""
    meta = metadata(path)
    text = meta["purpose"] or meta["h1"]
    text = re.sub(r"\s+", " ", text).strip()
    text = _EMOJI.sub("", text).strip()
    stem = path.stem
    if text[: len(stem)].upper() == stem.upper():
        text = text[len(stem):].lstrip(" :–—-.").strip()
    return text[:140].rstrip()


def markdown_files(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.md"), key=lambda p: p.name.upper())


def doc_folders() -> list[Path]:
    return sorted(
        (p for p in DOCS.iterdir() if p.is_dir() and p.name[:2].isdigit()),
        key=lambda p: p.name,
    )


def status_suffix(path: Path) -> str:
    status = metadata(path)["status"]
    base = status.split("(")[0].strip() if status else ""
    if base == "Исторический":
        return " ⚠️ исторический"
    if base in STATUS_VALUES and base not in ("Активный",):
        return f" ({base.lower()})"
    return ""


def render_index() -> str:
    folders = doc_folders()
    lines = [
        "# 📑 ИНДЕКС ДОКУМЕНТАЦИИ «ГОЛЕМ»",
        "",
        f"> Файл генерируется автоматически: `python tools/generate-docs-index.py`. Ручные правки будут перезаписаны.",
        "",
        f"**Структура:** {len(folders)} {plural(len(folders), 'раздел', 'раздела', 'разделов')} (00–99). Имена файлов — ВЕРХНИЙ РЕГИСТР, расширение `.md`.",
        "",
        "---",
        "",
        "## 📂 СТРУКТУРА",
        "",
    ]
    for folder in folders:
        lines.append(f"### {folder.name} — {folder_title(folder.name)}")
        lines.append("")
        files = markdown_files(folder)
        if not files:
            lines.append("_(пусто)_")
            lines.append("")
            continue
        for f in files:
            lines.append(f"- **{f.name}** — {annotation(f)}{status_suffix(f)}")
        lines.append("")
    lines += [
        "---",
        "",
        "> Индекс генерируется из фактического состояния `docs/`. Расхождение файла с генератором",
        "> ловится `tools/check-docs.py` (проверка «дрейф навигации»).",
        "",
    ]
    return "\n".join(lines)


def render_folder_readme(folder: Path) -> str | None:
    """Обложка раздела; None, если README.md уже существует."""
    target = folder / "README.md"
    if target.exists():
        return None
    lines = [
        f"# {folder.name} — {folder_title(folder.name)}",
        "",
        f"> Обложка раздела генерируется автоматически: `python tools/generate-docs-index.py`.",
        "",
        "## Файлы",
        "",
    ]
    for f in markdown_files(folder):
        lines.append(f"- **{f.name}** — {annotation(f)}{status_suffix(f)}")
    return "\n".join(lines) + "\n"


def render_stats() -> str:
    folders = doc_folders()
    out = [
        "# 📊 СТАТИСТИКА ДОКУМЕНТАЦИИ",
        "",
        "**Метаданные файла**",
        "- **Файл:** `docs/02-MANAGEMENT/STATS.md`",
        f"- **Версия:** авто (снимок от {SNAPSHOT})",
        "- **Причина:** файл генерируется автоматически: `python tools/generate-docs-index.py`. Ручные правки будут перезаписаны.",
        "- **Статус:** Активный",
        "",
        "## Сводка",
        "",
    ]
    all_files: list[Path] = []
    total_lines = 0
    for folder in folders:
        files = [p for p in markdown_files(folder) if p.resolve() != STATS_PATH.resolve()]
        all_files.extend(files)
        folder_lines = sum(len(read_text(p).splitlines()) for p in files)
        total_lines += folder_lines
        out.append(
            f"- **{folder.name}** — {len(files)} {plural(len(files), 'файл', 'файла', 'файлов')}, "
            f"{folder_lines} {plural(folder_lines, 'строка', 'строки', 'строк')}"
        )
    out.append("")
    out.append(
        f"**Всего:** {len(all_files)} {plural(len(all_files), 'файл', 'файла', 'файлов')}, "
        f"{total_lines} {plural(total_lines, 'строка', 'строки', 'строк')}."
    )
    out.append("")
    statuses: dict[str, int] = {}
    for p in all_files:
        status = metadata(p)["status"] or "— (не указан)"
        statuses[status] = statuses.get(status, 0) + 1
    out.append("## Статусы документов")
    out.append("")
    for status, count in sorted(statuses.items(), key=lambda kv: -kv[1]):
        out.append(f"- {status}: {count}")
    out.append("")
    out.append("---")
    out.append("")
    out.append("> Срез вычисляется из фактического состояния `docs/` и не заменяет содержательные отчёты.")
    out.append("")
    return "\n".join(out)


def generate() -> dict[str, Path]:
    written: dict[str, Path] = {}
    # сначала обложки разделов (чтобы INDEX видел их), затем INDEX и статистика
    for folder in doc_folders():
        text = render_folder_readme(folder)
        if text is None:
            continue
        target = folder / "README.md"
        target.write_text(text, encoding="utf-8")
        written[folder.name] = target
    INDEX_PATH.write_text(render_index(), encoding="utf-8")
    written["index"] = INDEX_PATH
    STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATS_PATH.write_text(render_stats(), encoding="utf-8")
    written["stats"] = STATS_PATH
    return written


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Генератор навигации документации docs/")
    parser.add_argument("--docs", type=Path, default=None, help="корень docs/ (по умолчанию рядом со скриптом)")
    parser.add_argument("--print-index", action="store_true", help="вывести INDEX.md в stdout, ничего не писать")
    parser.add_argument("--print-stats", action="store_true", help="вывести STATS.md в stdout, ничего не писать")
    args = parser.parse_args()

    global DOCS, INDEX_PATH, STATS_PATH
    if args.docs is not None:
        DOCS = args.docs.resolve()
        INDEX_PATH = DOCS / "INDEX.md"
        STATS_PATH = DOCS / "02-MANAGEMENT" / "STATS.md"

    if args.print_index:
        print(render_index())
        return
    if args.print_stats:
        print(render_stats())
        return

    written = generate()
    for key, path in written.items():
        print(f"✅ {key}: {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
