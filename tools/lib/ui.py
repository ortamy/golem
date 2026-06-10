# tools/lib/ui.py — дизайн-система Golem (ч/б + оранжевый акцент)

# import sys  # TODO: проверить, используется ли
import time
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import (
    Progress, SpinnerColumn, BarColumn, TextColumn,
    TaskProgressColumn, TimeRemainingColumn
)
from rich.panel import Panel
from rich.table import Table
# from rich.text import Text  # TODO: проверить, используется ли
# from rich.layout import Layout  # TODO: проверить, используется ли
from rich.columns import Columns
from rich import box
# from rich.style import Style  # TODO: проверить, используется ли
from rich.theme import Theme

# =============================================================================
# ТЕМА
# =============================================================================

GOLEM_THEME = Theme({
    "primary": "#ff4d00",        # Оранжевый акцент
    "primary_bold": "bold #ff4d00",
    "text": "#ffffff",           # Белый текст
    "dim": "#888888",            # Серый
    "success": "#00ff88",        # Зелёный (OK)
    "error": "#ff4444",          # Красный (ошибка)
    "warning": "#ffaa00",        # Жёлтый (предупреждение)
    "border": "#333333",         # Границы
    "bg": "#000000",             # Фон
})

console = Console(theme=GOLEM_THEME)

REPO_ROOT = Path(__file__).parent.parent.parent
TERMINAL_WIDTH = min(shutil.get_terminal_size().columns, 120)


# =============================================================================
# БАЗОВЫЕ ЭЛЕМЕНТЫ
# =============================================================================

def header(title: str, version: str = ""):
    """Заголовок страницы."""
    text = f"[primary_bold]{title}[/primary_bold]"
    if version:
        text += f" [dim]v{version}[/dim]"
    console.print()
    console.print(Panel(text, border_style="primary", box=box.HEAVY, padding=(1, 4)))
    console.print()


def section(title: str):
    """Раздел с заголовком."""
    console.print(f"\n[primary_bold]▸ {title}[/primary_bold]")
    console.print(f"[dim]{'─' * (TERMINAL_WIDTH - 4)}[/dim]")


def success(msg: str):
    """Успех."""
    console.print(f"  [success]✓[/success] {msg}")


def error(msg: str):
    """Ошибка."""
    console.print(f"  [error]✗[/error] {msg}")


def warning(msg: str):
    """Предупреждение."""
    console.print(f"  [warning]![/warning] {msg}")


def info(msg: str):
    """Информация."""
    console.print(f"  [dim]•[/dim] {msg}")


def hint(msg: str):
    """Подсказка."""
    console.print(f"\n[dim]💡 {msg}[/dim]")


def divider():
    """Разделитель."""
    console.print(f"[dim]{'=' * (TERMINAL_WIDTH - 4)}[/dim]")


def blank():
    """Пустая строка."""
    console.print()


# =============================================================================
# ПРОГРЕСС-БАР
# =============================================================================

def progress_bar(total: int, description: str = "Обработка"):
    """Создаёт контекстный менеджер прогресс-бара."""
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[primary]{description}[/primary]"),
        BarColumn(bar_width=40, style="dim", complete_style="primary"),
        TaskProgressColumn(),
        TextColumn("[dim]{task.fields[extra]}[/dim]"),
        console=console,
        expand=False,
    )


def simple_progress(current: int, total: int, label: str = "", extra: str = ""):
    """Простой прогресс-бар одной строкой (без контекстного менеджера)."""
    if not hasattr(simple_progress, '_progress'):
        simple_progress._progress = Progress(
            TextColumn("[primary]{task.description}[/primary]"),
            BarColumn(bar_width=30, style="dim", complete_style="primary"),
            TaskProgressColumn(),
            TextColumn("[dim]{task.fields[extra]}[/dim]"),
            console=console,
            expand=False,
        )
        simple_progress._task = simple_progress._progress.add_task(
            label, total=total, extra=extra
        )
        simple_progress._progress.start()

    simple_progress._progress.update(
        simple_progress._task,
        completed=current,
        total=total,
        description=f"[{current}/{total}] {label}",
        extra=extra
    )


def finish_progress():
    """Завершает простой прогресс-бар."""
    if hasattr(simple_progress, '_progress'):
        simple_progress._progress.stop()
        del simple_progress._progress
        del simple_progress._task


# =============================================================================
# СПИННЕР (анимация загрузки)
# =============================================================================

def spinner(message: str = "Загрузка", duration: float = 0.5):
    """Показывает спиннер с сообщением."""
    with console.status(f"[primary]{message}...[/primary]", spinner="dots"):
        time.sleep(duration)


# =============================================================================
# ТАБЛИЦЫ
# =============================================================================

def table(title: str, columns: list, rows: list):
    """Создаёт таблицу в стиле Golem."""
    t = Table(title=f"[primary_bold]{title}[/primary_bold]",
              border_style="dim",
              box=box.SIMPLE,
              expand=False)
    for col in columns:
        t.add_column(col, style="text")
    for row in rows:
        t.add_row(*[str(c) for c in row])
    console.print(t)


# =============================================================================
# СТАТУС-БАР
# =============================================================================

def status_line(items: dict):
    """Выводит строку статуса: {name: ok/error, ...}."""
    parts = []
    for name, ok in items.items():
        icon = "[success]✓[/success]" if ok else "[error]✗[/error]"
        parts.append(f"{icon} {name}")
    console.print("  " + "  ".join(parts))


# =============================================================================
# МЕНЮ
# =============================================================================

def menu(title: str, items: list) -> int:
    """Выводит меню и возвращает номер выбранного пункта (1-based)."""
    console.print(f"\n[primary_bold]{title}[/primary_bold]")
    console.print(f"[dim]{'─' * (TERMINAL_WIDTH - 4)}[/dim]")
    for i, item in enumerate(items, 1):
        console.print(f"  [primary]{i}.[/primary] {item}")
    console.print(f"  [dim]0. Выход[/dim]")
    console.print(f"[dim]{'─' * (TERMINAL_WIDTH - 4)}[/dim]")

    while True:
        try:
            choice = input("  > ").strip()
            if choice == '0':
                return 0
            idx = int(choice)
            if 1 <= idx <= len(items):
                return idx
        except ValueError:
            pass
        console.print("  [error]Неверный выбор[/error]")


# =============================================================================
# КАРТОЧКИ
# =============================================================================

def cards(items: list, columns: int = 3):
    """Выводит карточки в колонки."""
    card_texts = []
    for title, value, subtitle in items:
        card = f"[primary_bold]{value}[/primary_bold]\n[dim]{subtitle}[/dim]"
        card_texts.append(card)

    col_list = [Panel(c, border_style="dim", box=box.SQUARE, padding=(1, 3)) for c in card_texts]
    console.print(Columns(col_list, equal=True))


# =============================================================================
# ФАЙЛОВЫЙ СПИСОК
# =============================================================================

def file_list(files: list, max_items: int = 10):
    """Выводит список файлов."""
    for i, filepath in enumerate(files[:max_items], 1):
        console.print(f"  [dim]{i}.[/dim] {filepath}")


# =============================================================================
# ВВОД
# =============================================================================

def ask_yes_no(question: str) -> bool:
    """Задаёт вопрос да/нет."""
    answer = input(f"  [primary]?[/primary] {question} (y/n): ").strip().lower()
    return answer in ('y', 'yes', 'д', 'да')


def ask_input(prompt: str) -> str:
    """Запрашивает ввод."""
    return input(f"  [primary]>[/primary] {prompt}: ").strip()


# =============================================================================
# ЭКСПОРТ
# =============================================================================

__all__ = [
    'console', 'REPO_ROOT', 'TERMINAL_WIDTH',
    'header', 'section', 'success', 'error', 'warning', 'info', 'hint',
    'divider', 'blank',
    'progress_bar', 'simple_progress', 'finish_progress',
    'spinner',
    'table', 'status_line', 'menu', 'cards', 'file_list',
    'ask_yes_no', 'ask_input',
]

