# tools/check-links.py — проверка битых ссылок в md-файлах
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, progress_bar, finish_progress, print_header, print_success, print_error, print_warning, print_hint, REPO_ROOT

IGNORE_DIRS = {'.git', 'tools', 'drafts', 'ideas', '__pycache__', 'reports', 'neural'}


def find_all_md_files():
    files = {}
    for md_file in REPO_ROOT.rglob('*.md'):
        if '.git' in str(md_file):
            continue
        rel_path = str(md_file.relative_to(REPO_ROOT))
        parts = Path(rel_path).parts
        if parts[0] in IGNORE_DIRS:
            continue
        files[rel_path] = md_file
    return files


def extract_links(content: str) -> list:
    links = []
    for match in re.findall(r'\]\(([^\)]+\.md)\)', content):
        if not match.startswith("http"):
            links.append(match)
    return links


def main():
    print_header("ПРОВЕРКА ССЫЛОК", "🔗")

    files = find_all_md_files()
    total = len(files)
    print(f"Найдено файлов: {total}")

    broken = []
    encoding_issues = []

    for i, (rel_path, full_path) in enumerate(files.items(), 1):
        try:
            content = read_file_safe(full_path)
        except Exception as e:
            encoding_issues.append((rel_path, str(e)))
            continue

        for link in extract_links(content):
            if not (REPO_ROOT / link).exists():
                broken.append((rel_path, link))

        progress_bar(i, total, extra=f"битых: {len(broken)}")

    finish_progress()

    if encoding_issues:
        print_warning(f"Проблемы с кодировкой: {len(encoding_issues)}")
        for file_path, error in encoding_issues[:5]:
            print(f"   • {file_path} — {error}")

    if broken:
        print_error(f"БИТЫХ ССЫЛОК: {len(broken)}")
        for file_path, link in broken[:15]:
            print(f"   • {file_path} → {link}")
        if len(broken) > 15:
            print(f"   ... и ещё {len(broken) - 15}")
        return 1
    else:
        print_success("Все ссылки корректны")

    return 0


if __name__ == "__main__":
    sys.exit(main())

