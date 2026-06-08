# tools/lib/utils.py — общие утилиты для всех скриптов (с Rich)
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

console = Console()
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
    """Упрощённый прогресс-бар через Rich (без контекстного менеджера)."""
    if not hasattr(progress_bar, '_progress'):
        progress_bar._progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[dim]{task.fields[extra]}[/dim]"),
            console=console,
        )
        progress_bar._task = progress_bar._progress.add_task("", total=total, extra="")
        progress_bar._progress.start()

    extra_str = extra if extra else ""
    progress_bar._progress.update(progress_bar._task, completed=current, total=total,
                                   description=f"[{current}/{total}]", extra=extra_str)

def progress_bar_simple(current, total, extra=""):
    """Простой текстовый прогресс-бар (без Rich, для curses)."""
    pct = current / total if total > 0 else 0
    bar_len = 30
    filled = int(bar_len * pct)
    bar = "█" * filled + "░" * (bar_len - filled)
    extra_str = f" | {extra}" if extra else ""
    print(f"  [{bar}] {pct:.0%} ({current}/{total}){extra_str}", end="\r", flush=True)

def finish_progress():
    """Завершает прогресс-бар."""
    if hasattr(progress_bar, '_progress'):
        progress_bar._progress.stop()
        del progress_bar._progress
        del progress_bar._task


def print_header(title, emoji="📋"):
    """Выводит красивый заголовок."""
    console.print()
    console.print(Panel.fit(f"{emoji} {title}", border_style="bold cyan"))


def print_success(msg):
    """Выводит сообщение об успехе."""
    console.print(f"[bold green]✅ {msg}[/bold green]")


def print_error(msg):
    """Выводит сообщение об ошибке."""
    console.print(f"[bold red]❌ {msg}[/bold red]")


def print_warning(msg):
    """Выводит предупреждение."""
    console.print(f"[bold yellow]⚠️ {msg}[/bold yellow]")


def print_hint(msg):
    """Выводит подсказку."""
    console.print(f"[dim]💡 {msg}[/dim]")


def ask_yes_no(question):
    """Задаёт вопрос y/n."""
    answer = console.input(f"[bold yellow]{question} (y/n): [/bold yellow]").strip().lower()
    return answer in ('y', 'yes', 'д', 'да')

