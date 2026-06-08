# tools/lib/utils.py — общие утилиты для всех скриптов
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def read_file_safe(filepath: Path) -> str:
    """Читает файл с автоопределением кодировки."""
    encodings = ['utf-8', 'utf-16', 'cp1251', 'latin-1']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception:
        return None


def progress_bar(current, total, label="", extra=""):
    """Прогресс-бар в одной строке."""
    pct = current / total if total > 0 else 0
    bar_len = 30
    filled = int(bar_len * pct)
    bar = "█" * filled + "░" * (bar_len - filled)
    info = f"  [{bar}] {pct:.0%} ({current}/{total})"
    if extra:
        info += f" | {extra}"
    print(info, end="\r", flush=True)


def finish_progress():
    """Завершает строку прогресс-бара."""
    print()


def print_header(title, emoji="📋"):
    """Выводит заголовок."""
    print(f"\n{emoji} {title}")
    print("=" * 50)


def print_success(msg):
    """Выводит успех."""
    print(f"\n✅ {msg}")


def print_error(msg):
    """Выводит ошибку."""
    print(f"\n❌ {msg}")


def print_warning(msg):
    """Выводит предупреждение."""
    print(f"\n⚠️ {msg}")


def print_hint(msg):
    """Выводит подсказку."""
    print(f"\n💡 {msg}")


def ask_yes_no(question):
    """Задаёт вопрос y/n."""
    answer = input(f"{question} (y/n): ").strip().lower()
    return answer in ('y', 'yes', 'д', 'да')