# tools/lib/utils.py — общие утилиты для всех скриптов
import sys
import time
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
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def progress_bar(current, total, label="", extra=""):
    """Рисует прогресс-бар в одной строке.
    Использование:
        progress_bar(i, total, "сканирование", f"найдено: {count}")
    """
    pct = current / total if total > 0 else 0
    bar_len = 30
    filled = int(bar_len * pct)
    bar = "█" * filled + "░" * (bar_len - filled)
    info = f"{label} " if label else ""
    extra_info = f" | {extra}" if extra else ""
    print(f"\r  [{bar}] {pct:.0%} ({current}/{total}){extra_info}", end="", flush=True)


def finish_progress():
    """Завершает строку прогресс-бара."""
    print()


def print_header(title, emoji="📋"):
    """Выводит заголовок скрипта."""
    print(f"\n{emoji} {title}")
    print("=" * 50)


def print_success(msg):
    """Выводит сообщение об успехе."""
    print(f"\n✅ {msg}")


def print_error(msg):
    """Выводит сообщение об ошибке."""
    print(f"\n❌ {msg}")


def print_warning(msg):
    """Выводит предупреждение."""
    print(f"\n⚠️ {msg}")


def print_hint(msg):
    """Выводит подсказку."""
    print(f"\n💡 {msg}")


def ask_yes_no(question):
    """Задаёт вопрос y/n и возвращает True/False."""
    answer = input(f"{question} (y/n): ").strip().lower()
    return answer in ('y', 'yes', 'д', 'да')


class ScriptTemplate:
    """Шаблон для быстрого создания скриптов."""

    def __init__(self, name, emoji="🔍", fix_mode=False):
        self.name = name
        self.emoji = emoji
        self.fix_mode = fix_mode or "--fix" in sys.argv

    def run(self):
        """Запускает скрипт с общим обрамлением."""
        if self.fix_mode:
            print_header(f"ИСПРАВЛЕНИЕ: {self.name}", "🔧")
        else:
            print_header(self.name, self.emoji)

        try:
            result = self.main()
            if result:
                print_success("Готово")
            if not self.fix_mode:
                print_hint(f"Для исправления: python {sys.argv[0]} --fix")
        except KeyboardInterrupt:
            print_warning("Прервано пользователем")
        except Exception as e:
            print_error(f"Ошибка: {e}")

    def main(self):
        """Переопредели в наследнике."""
        raise NotImplementedError