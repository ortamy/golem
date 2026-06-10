# tools/lib/utils.py — общие утилиты для всех скриптов (с Rich)
# import sys  # TODO: проверить, используется ли
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich import print as rprint

console = Console()
REPO_ROOT = Path(__file__).parent.parent.parent


def read_file_safe(filepath: Path) -> str | None:
    """Читает файл с автоопределением кодировки. Возвращает None при ошибке."""
    if not filepath.exists():
        return None

    # Пропускаем бинарные файлы
    binary_extensions = {'.pyc', '.pyd', '.exe', '.dll', '.so', '.bin', '.zip', '.tar', '.gz', '.png', '.jpg', '.svg', '.ico'}
    if filepath.suffix.lower() in binary_extensions:
        return None

    # Проверяем размер — если > 10 МБ, пропускаем
    try:
        if filepath.stat().st_size > 10 * 1024 * 1024:
            return None
    except OSError:
        return None

    encodings = ['utf-8', 'utf-16', 'cp1251', 'latin-1']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
        except KeyboardInterrupt:
            raise
        except Exception:
            continue

    # Последняя попытка — с заменой ошибок
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except KeyboardInterrupt:
        raise
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
    progress_bar._progress.update(
        progress_bar._task,
        completed=current,
        total=total,
        description=f"[{current}/{total}]",
        extra=extra_str
    )


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
    try:
        answer = console.input(f"[bold yellow]{question} (y/n): [/bold yellow]").strip().lower()
        return answer in ('y', 'yes', 'д', 'да')
    except (KeyboardInterrupt, EOFError):
        print()
        return False

