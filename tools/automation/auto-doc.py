# tools/automation/auto-doc.py — doc
import sys
import shutil
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, print_header, print_success, print_error, print_warning, print_hint, ask_yes_no, REPO_ROOT

DOCS_DIR = REPO_ROOT / "docs"
BACKUP_DIR = REPO_ROOT / "docs_backup"

FILES_TO_MOVE = [
    "BACKLOG.md",
    "CHANGELOG.md",
    "COMPLETED-TASKS.md",
    "CONTRIBUTORS.md",
    "DECISIONS.md",
    "GLOSSARY.md",
    "RETROSPECTIVE.md",
    "ROADMAP.md",
    "STATS.md",
    "STRUCTURE.md",
    "TECHNICAL-DEBT.md",
]


def find_all_md_files():
    files = []
    for md_file in REPO_ROOT.rglob("*.md"):
        if ".git" in str(md_file) or "__pycache__" in str(md_file) or "docs_backup" in str(md_file):
            continue
        files.append(md_file)
    return files


def update_links_in_file(filepath, moved_files):
    content = read_file_safe(filepath)
    if not content:
        return 0

    original = content

    for old_name in moved_files:
        old_name_no_ext = old_name.replace(".md", "")

        patterns = [
            (rf'\[([^\]]*)\]\({re.escape(old_name)}\)', rf'[\1](docs/{old_name})'),
            (rf'\[([^\]]*)\]\({re.escape(old_name_no_ext)}\)', rf'[\1](docs/{old_name})'),
            (rf'\[([^\]]*)\]\(\.\/{re.escape(old_name)}\)', rf'[\1](docs/{old_name})'),
            (rf'`{re.escape(old_name)}`', rf'`docs/{old_name}`'),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return 1

    return 0


def main():
    print_header("ПЕРЕНОС ДОКУМЕНТАЦИИ В docs/", "📁")

    if DOCS_DIR.exists():
        existing = [f.name for f in DOCS_DIR.iterdir() if f.name in FILES_TO_MOVE]
        if existing:
            print_warning(f"В docs/ уже есть: {', '.join(existing)}")
            if not ask_yes_no("Перезаписать?"):
                print("👋 Отменено.")
                return 1

    files_to_move = []
    missing_files = []

    for filename in FILES_TO_MOVE:
        src = REPO_ROOT / filename
        if src.exists():
            files_to_move.append(filename)
        else:
            missing_files.append(filename)

    if not files_to_move:
        print_success("Нечего переносить — всё уже в docs/")
        return 0

    print(f"\nФайлов для переноса: {len(files_to_move)}")
    for f in files_to_move:
        print(f"  • {f}")

    if missing_files:
        print(f"\nУже отсутствуют: {len(missing_files)}")
        for f in missing_files:
            print(f"  • {f}")

    if not ask_yes_no("\nПеренести и обновить все ссылки?"):
        print("👋 Отменено.")
        return 0

    # Бэкап
    print("\n📦 Бэкап...")
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    for filename in files_to_move:
        src = REPO_ROOT / filename
        shutil.copy2(src, BACKUP_DIR / filename)
    print(f"✅ Бэкап: {BACKUP_DIR}")

    # Перенос
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    print("\n📁 Перенос...")
    for filename in files_to_move:
        src = REPO_ROOT / filename
        dst = DOCS_DIR / filename
        shutil.move(str(src), str(dst))
        print(f"  ✓ {filename} → docs/{filename}")

    # Обновление ссылок
    print("\n🔗 Обновление ссылок...")
    all_md_files = find_all_md_files()
    updated = 0
    for md_file in all_md_files:
        updated += update_links_in_file(md_file, files_to_move)

    print(f"✅ Обновлено файлов: {updated}")

    # .gitignore
    gitignore = REPO_ROOT / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if "docs_backup" not in content:
            with open(gitignore, "a", encoding="utf-8") as f:
                f.write("\ndocs_backup/\n")
            print("✅ Обновлён .gitignore")

    print("\n" + "=" * 50)
    print_success(f"Готово! {len(files_to_move)} файлов → docs/")
    print_hint("Проверьте: git status")
    print_hint("Отмена: восстановите из docs_backup/")

    return 0


if __name__ == "__main__":
    sys.exit(main())

