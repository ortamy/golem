#!/usr/bin/env python3
"""Проверка целостности документации docs/ (пути, ссылки, навигация).

Проверки:
  header_path  [error]  «Файл:» в шапке ≠ фактический путь файла;
  links        [error]  битые Markdown-ссылки внутри docs/ (регистрозависимо);
  nav          [error]  INDEX.md / README-обложки / STATS.md ≠ эталон генератора;
  dup_h1       [warn]   дубли первых заголовков по корпусу;
  empty_links  [warn]   пустые элементы в «Связанные файлы»;
  status       [warn]   неизвестное значение «Статус:».

Использование:
  python tools/check-docs.py check            # проверка (0 = чисто, 1 = есть error)
  python tools/check-docs.py check --fix      # автоисправление путей в шапках и регистра ссылок
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
HAND_WRITTEN_README = {"00-START", "07-MECHANICS"}

_ALLOWED_STATUS = {"Активный", "Исторический", "Заготовка", "Концепция"}
_META_FILE = re.compile(r"^-\s*\*{0,2}(Файл|File)\*{0,2}\s*[:：]\s*(.+)$")
_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_FENCE = re.compile(r"^```")
_EMPTY_REL = ", ``,"


def load_generator():
    """Импортирует tools/generate-docs-index.py как модуль."""
    path = ROOT / "tools" / "generate-docs-index.py"
    spec = importlib.util.spec_from_file_location("generate_docs_index", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def walk_md(folder: Path) -> list[Path]:
    return sorted(folder.glob("*.md"), key=lambda p: p.name.upper())


def normalize_rel(path: Path) -> str:
    """Относительный путь от docs/ в posix-форме."""
    return path.relative_to(DOCS).as_posix()


def norm_declared(value: str) -> str:
    """Нормализует объявленный путь: убирает разметку и docs/-префикс."""
    value = value.strip().replace("\\", "/")
    for _ in range(6):
        cleaned = value.strip().strip("`* _>").replace("**", "")
        if cleaned == value:
            break
        value = cleaned
    value = re.sub(r"^\.?/?docs/", "", value)
    return value.strip()


def header_declared(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    for line in lines[:60]:
        m = _META_FILE.match(line)
        if m:
            return m.group(2).strip()
    return None


def lines_of(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []


def case_sensitive_exists(base: Path, rel: str) -> tuple[Path | None, bool]:
    """Проверяет rel внутри base с учётом регистра имён.

    Возвращает (реальный_путь|None, регистр_совпал). Если путь существует, но
    регистр имени отличается — возвращает путь с фактическим именем и False.
    """
    current = base
    case_ok = True
    for part in Path(rel).parts:
        if part in ("", ".", ".."):
            if part == "..":
                current = current.parent
            continue
        try:
            names = os.listdir(current)
        except OSError:
            return None, case_ok
        if part in names:
            current = current / part
            continue
        lowered = {n.lower(): n for n in names}
        match = lowered.get(part.lower())
        if match is None:
            return None, case_ok
        case_ok = False
        current = current / match
    return current, case_ok


def resolve_link(source: Path, target: str) -> tuple[Path | None, str | None]:
    """Разрешает цель ссылки в путь внутри docs/.

    Возвращает (реальный_путь|None, причина_ошибки|None).
    """
    target = target.strip().strip("<>")
    target = target.split("#", 1)[0].strip()
    if not target or not target.lower().endswith(".md"):
        return None, None
    if re.match(r"^(https?|mailto|tel|data|javascript):", target, re.I):
        return None, None
    if target.startswith("/"):
        return None, None
    if target.startswith("docs/"):
        base, rel = DOCS, target[len("docs/"):]
    else:
        base = source.parent
        rel = target
    resolved = (base / rel).resolve()
    if DOCS not in resolved.parents and resolved != DOCS:
        return None, None  # ссылка наружу docs/ — не проверяем
    real, case_ok = case_sensitive_exists(base, rel)
    if real is None:
        return None, f"не найден: {target}"
    if not case_ok:
        return None, f"регистр имени: {target} (фактически {real.name})"
    if real.resolve() != resolved:
        return None, f"регистр пути: {target}"
    if not real.is_file():
        return None, f"не файл: {target}"
    return real, None


def check_headers(files: list[Path], fix: bool) -> tuple[int, list[str]]:
    errors: list[str] = []
    for path in files:
        declared = header_declared(path)
        if declared is None:
            continue
        norm = norm_declared(declared)
        actual = normalize_rel(path)
        if norm == actual:
            continue
        errors.append(f"{normalize_rel(path)}: шапка «Файл: {declared}» ≠ фактический путь «docs/{actual}»")
        if not fix:
            continue
        new_value = f"docs/{actual}"
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        out: list[str] = []
        replaced = False
        for ln in lines:
            if not replaced and _META_FILE.match(ln):
                ending = "\r\n" if ln.endswith("\r\n") else "\n" if ln.endswith("\n") else ""
                out.append(f"- **Файл:** `{new_value}`{ending}")
                replaced = True
            else:
                out.append(ln)
        if replaced:
            path.write_text("".join(out), encoding="utf-8")
    return 1 if errors else 0, errors


def check_links(files: list[Path], fix: bool) -> tuple[int, list[str]]:
    errors: list[str] = []
    for path in files:
        in_fence = False
        for idx, line in enumerate(lines_of(path), start=1):
            if _FENCE.match(line.strip()):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for m in _LINK.finditer(line):
                target = m.group(1).strip()
                real, reason = resolve_link(path, target)
                if reason is None:
                    continue
                if fix and reason.startswith("регистр имени"):
                    # пробуем починить: заменяем регистр конечного имени на фактический
                    parts = target.split("/")
                    base = path.parent if not target.startswith("docs/") else DOCS
                    rel_prefix = target[len("docs/"):] if target.startswith("docs/") else target
                    dir_part, name_part = rel_prefix.rsplit("/", 1) if "/" in rel_prefix else ("", rel_prefix)
                    dir_path = (base / dir_part) if dir_part else base
                    try:
                        names = os.listdir(dir_path)
                    except OSError:
                        names = []
                    actual_name = next((n for n in names if n.lower() == name_part.lower()), None)
                    if actual_name is not None and actual_name != name_part:
                        new_target = (dir_part + "/" if dir_part else "") + actual_name
                        if target.startswith("docs/"):
                            new_target = "docs/" + new_target
                        fixed_line = line.replace(m.group(1), new_target)
                        if fixed_line != line:
                            raw = path.read_text(encoding="utf-8").splitlines(keepends=True)
                            if idx - 1 < len(raw):
                                orig = raw[idx - 1]
                                ending = "\r\n" if orig.endswith("\r\n") else "\n" if orig.endswith("\n") else ""
                                raw[idx - 1] = fixed_line + ending
                                path.write_text("".join(raw), encoding="utf-8")
                            continue
                errors.append(f"{normalize_rel(path)}:{idx}: битая ссылка ({reason})")
    return 1 if errors else 0, errors


def check_nav(gen, index_path: Path, stats_path: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    if not index_path.exists():
        errors.append("INDEX.md отсутствует")
    elif index_path.read_text(encoding="utf-8") != gen.render_index():
        errors.append("INDEX.md расходится с генератором (запусти python tools/generate-docs-index.py)")
    folders = gen.doc_folders()
    for folder in folders:
        readme = folder / "README.md"
        if not readme.exists():
            errors.append(f"{folder.name}/README.md отсутствует (генератор создаёт обложку раздела)")
            continue
        if folder.name in HAND_WRITTEN_README:
            continue
        expected = gen.render_folder_readme(folder)
        if expected is None:
            continue
        if readme.read_text(encoding="utf-8") != expected:
            errors.append(f"{folder.name}/README.md расходится с генератором")
    if not stats_path.exists():
        errors.append("02-MANAGEMENT/STATS.md отсутствует")
    elif stats_path.read_text(encoding="utf-8") != gen.render_stats():
        errors.append("02-MANAGEMENT/STATS.md расходится с генератором")
    return 1 if errors else 0, errors


def check_warnings(files: list[Path], gen) -> list[str]:
    warns: list[str] = []
    h1_index: dict[str, list[str]] = {}
    for path in files:
        lines = lines_of(path)
        meta = gen.metadata(path)
        if meta["status"] and meta["status"].split("(")[0].strip() not in _ALLOWED_STATUS:
            warns.append(f"{normalize_rel(path)}: неизвестный статус «{meta['status']}»")
        for idx, line in enumerate(lines, start=1):
            if _EMPTY_REL in line:
                warns.append(f"{normalize_rel(path)}:{idx}: пустые элементы в «Связанные файлы»")
        h1 = meta["h1"]
        if h1:
            h1_index.setdefault(h1, []).append(normalize_rel(path))
    for h1, paths in sorted(h1_index.items()):
        if len(paths) > 1:
            warns.append(f"дубль заголовка «{h1}»: {', '.join(paths)}")
    return warns


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Проверка целостности документации docs/")
    parser.add_argument("cmd", choices=["check"], help="команда")
    parser.add_argument("--docs", type=Path, default=None, help="корень docs/ (по умолчанию рядом со скриптом)")
    parser.add_argument("--fix", action="store_true", help="автоисправление путей шапок и регистра ссылок")
    args = parser.parse_args()

    global DOCS
    if args.docs is not None:
        DOCS = args.docs.resolve()
    index_path = DOCS / "INDEX.md"
    stats_path = DOCS / "02-MANAGEMENT" / "STATS.md"

    gen = load_generator()
    # генератор оперирует собственным DOCS — синхронизируем при нестандартном --docs
    if args.docs is not None:
        gen.DOCS = DOCS
        gen.INDEX_PATH = index_path
        gen.STATS_PATH = stats_path

    all_files: list[Path] = []
    for folder in gen.doc_folders():
        all_files.extend(walk_md(folder))

    code_h, errs_h = check_headers(all_files, args.fix)
    code_l, errs_l = check_links(all_files, args.fix)
    code_n, errs_n = check_nav(gen, index_path, stats_path)
    warns = check_warnings(all_files, gen)

    print("— Проверка документации docs/ —")
    for label, code, errs in (("Шапки/пути", code_h, errs_h),
                              ("Ссылки", code_l, errs_l),
                              ("Навигация", code_n, errs_n)):
        print(f"[{'ERROR' if code else 'ok'}] {label}: {len(errs)}")
        for e in errs[:40]:
            print(f"    {e}")
        if len(errs) > 40:
            print(f"    … и ещё {len(errs) - 40}")
    print(f"[warn] прочее: {len(warns)}")
    for w in warns[:30]:
        print(f"    {w}")
    if len(warns) > 30:
        print(f"    … и ещё {len(warns) - 30}")

    total_errors = code_h + code_l + code_n
    print("— Итог: " + ("есть ошибки" if total_errors else "чисто") + " —")
    sys.exit(1 if total_errors else 0)


if __name__ == "__main__":
    main()
