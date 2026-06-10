#!/usr/bin/env python3
# tools/checkers/check-links.py — быстрая проверка битых ссылок в md-файлах
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import (
    progress_bar, finish_progress,
    print_header, print_success, print_error, print_warning, print_hint,
    ask_yes_no, REPO_ROOT
)

IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__', 'reports', 'neural'}

_file_cache = {}
_existing_paths = None


def find_all_md_files():
    """Быстро находит все md-файлы."""
    global _existing_paths
    files = {}
    paths = set()
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        rel = str(md_file.relative_to(REPO_ROOT)).replace('\\', '/')
        if rel.split('/')[0] in IGNORE_DIRS:
            continue
        files[rel] = md_file
        paths.add(rel)
    _existing_paths = paths
    return files


def read_fast(filepath: Path) -> str | None:
    """Быстрое чтение файла с кешем."""
    rel = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
    mtime = filepath.stat().st_mtime

    if rel in _file_cache and _file_cache[rel][0] == mtime:
        return _file_cache[rel][1]

    try:
        content = filepath.read_text(encoding='utf-8')
    except:
        try:
            content = filepath.read_text(encoding='utf-8', errors='replace')
        except:
            return None

    _file_cache[rel] = (mtime, content)
    return content


def extract_links(content: str) -> list:
    """Извлекает все ссылки на md-файлы — один проход."""
    links = []

    for m in re.finditer(r'`([^`]+\.md)`', content):
        link = m.group(1)
        if '/' in link and not link.startswith('http'):
            links.append(link)

    for m in re.finditer(r'\]\(([^\)]+\.md)(?:#[^\)]*)?\)', content):
        link = m.group(1)
        if not link.startswith('http'):
            links.append(link)

    return links


def normalize_link(link: str, current_file: str) -> str:
    """Нормализует относительную ссылку до пути от корня."""
    if link.startswith('/'):
        return link[1:]
    if link.startswith('../'):
        parts = current_file.split('/')
        ups = link.count('../')
        if ups >= len(parts):
            return link.replace('../', '')
        base = '/'.join(parts[:-ups-1])
        rest = link.replace('../', '').replace('./', '')
        return (base + '/' + rest).strip('/') if base else rest
    if link.startswith('./'):
        base = '/'.join(current_file.split('/')[:-1])
        return (base + '/' + link[2:]).strip('/')
    base = '/'.join(current_file.split('/')[:-1])
    return (base + '/' + link).strip('/')


def find_similar(target: str, candidates: set) -> list:
    """Находит похожие существующие файлы."""
    target_stem = Path(target).stem.lower()
    target_parent = str(Path(target).parent)

    for c in candidates:
        if Path(c).stem.lower() == target_stem:
            return [c]

    same_folder = [c for c in candidates if str(Path(c).parent) == target_parent]
    if same_folder:
        return same_folder[:2]

    similar = [c for c in candidates if target_stem in c.lower()][:2]
    return similar if similar else []


def fix_link(filepath: Path, old_link: str, new_link: str) -> bool:
    """Заменяет битую ссылку на правильную."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except:
        return False

    if old_link not in content:
        return False

    new_content = content.replace(old_link, new_link)
    if new_content == content:
        return False

    try:
        filepath.write_text(new_content, encoding='utf-8')
        rel = str(filepath.relative_to(REPO_ROOT)).replace('\\', '/')
        if rel in _file_cache:
            _file_cache[rel] = (filepath.stat().st_mtime, new_content)
        return True
    except:
        return False


def main():
    global _existing_paths
    fix_mode = "--fix" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    print_header("ПРОВЕРКА ССЫЛОК", "🔗")

    files = find_all_md_files()
    total = len(files)
    print(f"🔍 Файлов: {total}")

    broken = []
    suggestions = {}
    by_folder = defaultdict(int)
    total_fixed = 0

    for i, (rel_path, full_path) in enumerate(files.items(), 1):
        content = read_fast(full_path)
        if not content:
            continue

        links = extract_links(content)
        if not links:
            progress_bar(i, total, extra=f"битых: {len(broken)}")
            continue

        for link in links:
            normalized = normalize_link(link, rel_path)
            if normalized not in _existing_paths:
                broken.append((rel_path, link, normalized))
                by_folder[rel_path.split('/')[0]] += 1
                if normalized not in suggestions:
                    similar = find_similar(normalized, _existing_paths)
                    if similar:
                        suggestions[normalized] = similar

        progress_bar(i, total, extra=f"битых: {len(broken)}")

    finish_progress()

    if not broken:
        print_success("🎉 Все ссылки корректны")
        return 0

    print_error(f"\n🔗 БИТЫХ ССЫЛОК: {len(broken)}")
    print(f"💡 Предложений по исправлению: {len(suggestions)}")

    print("\n📊 По папкам:")
    for folder, count in sorted(by_folder.items()):
        print(f"  {folder}: {count}")

    print(f"\n📋 Битые ссылки:")
    for file_path, link, normalized in (broken if verbose else broken[:20]):
        sugg = ""
        if normalized in suggestions:
            sugg = f"  → {', '.join(suggestions[normalized][:2])}"
        print(f"  {file_path} → {link}{sugg}")
    if len(broken) > 20 and not verbose:
        print(f"  ... и ещё {len(broken) - 20}")

    if fix_mode:
        fixable = [(fp, l, n) for fp, l, n in broken if n in suggestions and suggestions[n]]
        if not fixable:
            print_warning("Нет ссылок для автоматического исправления")
            return 1

        if not ask_yes_no(f"\n🔧 Исправить {len(fixable)} битых ссылок?"):
            return 1

        for i, (file_path, link, normalized) in enumerate(fixable, 1):
            filepath = files[file_path]
            new_link = suggestions[normalized][0]
            if fix_link(filepath, link, new_link):
                total_fixed += 1
            progress_bar(i, len(fixable), extra=f"исправлено: {total_fixed}")

        finish_progress()
        print_success(f"✅ Исправлено ссылок: {total_fixed}")
    else:
        print_hint("\n--fix — автоматически исправить ссылки")

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())